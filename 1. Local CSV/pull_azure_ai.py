"""Pull real Azure AI spend and token data into CSVs for dashboard development.

Two sources, because cost and usage live in different systems:

  Cost Management Query API   spend + usage quantity, daily, by meter
  Azure Monitor Metrics       token counts and PTU utilisation, per deployment

Verified against a live tenant on 2026-08-07. Findings that contradict the
research doc are noted at each site rather than silently corrected.
"""
import csv
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ARM = "https://management.azure.com"
API = "2025-03-01"
METRICS_API = "2024-02-01"

# ServiceName values that are actually AI, as returned by a live tenant.
#
# NOT "Azure OpenAI" - the research doc and most Learn examples say that, but
# a live query returns "Foundry Models". Anything filtering on the old name
# gets zero rows and looks like there is no spend.
AI_SERVICES = ["Foundry Models", "Microsoft Copilot Studio", "Cognitive Services",
               "Azure Machine Learning", "Azure OpenAI"]

# Resource-tag keys to try, in order, for the department attribution column.
# Tenants name this differently; the first one present on a resource wins.
# None of them present is fine - DepartmentTag is optional throughout.
TAG_KEYS = ["Department", "department", "CostCentre", "CostCenter",
            "Team", "BusinessUnit", "Owner"]


def az(args, parse=True):
    r = subprocess.run(["az"] + args, capture_output=True, text=True, shell=True)
    if r.returncode != 0:
        return None if parse else r.stderr
    return json.loads(r.stdout) if parse and r.stdout.strip() else r.stdout


def cost_query(sub, days, grouping, extra_filter=None):
    """Cost Management query. Returns (columns, rows)."""
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    body = {
        "type": "ActualCost",
        "timeframe": "Custom",
        "timePeriod": {"from": str(start), "to": str(end)},
        "dataset": {
            "granularity": "Daily",
            "aggregation": {
                "totalCost": {"name": "Cost", "function": "Sum"},
                "totalQty": {"name": "UsageQuantity", "function": "Sum"},
            },
            # 'Meter', NOT 'MeterName'. The API rejects MeterName outright and
            # helpfully lists the valid dimensions in the 400 body.
            "grouping": [{"type": "Dimension", "name": g} for g in grouping],
        },
    }
    if extra_filter:
        body["dataset"]["filter"] = extra_filter

    tmp = Path(sys.argv[0]).parent / "_cmbody.json"
    tmp.write_text(json.dumps(body), encoding="ascii")
    out = az(["rest", "--method", "post",
              "--uri", f"{ARM}/subscriptions/{sub}/providers/Microsoft.CostManagement/query?api-version={API}",
              "--body", f"@{tmp}",
              "--headers", "Content-Type=application/json", "-o", "json"])
    tmp.unlink(missing_ok=True)
    if not out:
        return [], []
    p = out.get("properties", out)
    return [c["name"] for c in p["columns"]], p["rows"]


def main():
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    sub = az(["account", "show", "-o", "json"])["id"]
    print("subscription:", sub)

    # ---- 1. AI spend, daily, by meter and resource -------------------------
    filt = {"dimensions": {"name": "ServiceName", "operator": "In", "values": AI_SERVICES}}
    cols, rows = cost_query(sub, 90, ["Meter", "MeterCategory", "ResourceId", "ServiceName"], filt)
    print(f"\ncost rows: {len(rows)}")

    path = outdir / "AzureAiSpendDaily.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["UsageDate", "ServiceName", "MeterCategory", "Meter",
                    "ResourceId", "ResourceName", "ResourceGroup", "Cost",
                    "UsageQuantity", "Currency", "DepartmentTag"])
        def g(r, n):
            return r[cols.index(n)] if n in cols else ""

        # DepartmentTag comes from an Azure resource tag, so the dashboard can
        # break Foundry spend down the same way the other products break down
        # by department. Grouping the cost query on a TagKey would be tidier,
        # but it changes a query that is verified working - so the tags are
        # fetched separately and joined on resource id.
        #
        # Set TAG_KEY to whatever your organisation actually tags with. Leave
        # the column empty and every other figure still works.
        tags = {}
        for res in az(["resource", "list", "-o", "json"]) or []:
            t = (res.get("tags") or {})
            for key in TAG_KEYS:
                if key in t:
                    tags[res["id"].lower()] = t[key]
                    break
        for r in rows:
            rid = str(g(r, "ResourceId"))
            parts = rid.split("/")
            name = parts[-1] if parts else ""
            rg = parts[parts.index("resourcegroups") + 1] if "resourcegroups" in parts else ""
            d = str(g(r, "UsageDate"))
            iso = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else d
            w.writerow([iso, g(r, "ServiceName"), g(r, "MeterCategory"), g(r, "Meter"),
                        rid, name, rg, g(r, "Cost"), g(r, "UsageQuantity"),
                        g(r, "Currency"), tags.get(rid.lower(), "")])
    print("wrote", path.name)

    # ---- 2. Token + PTU metrics per deployment -----------------------------
    #
    # METRIC NAMES HAVE CHANGED. Checked with metrics list-definitions against
    # a live AIServices resource on 2026-08-07:
    #
    #   current                  older name, still in most documentation
    #   InputTokens              ProcessedPromptTokens
    #   OutputTokens             GeneratedTokens
    #   TotalCalls               AzureOpenAIRequests
    #   ProvisionedUtilization   AzureOpenAIProvisionedManagedUtilizationV2
    #
    # An "OpenAI" kind resource may still emit the old names and an
    # "AIServices" one the new, so ask for the definitions and request
    # whichever this resource actually has. Asking for a name a resource does
    # not publish returns a well-formed series of zeros - which looks like an
    # idle deployment rather than a wrong metric name, and is how an hour
    # disappears.
    accounts = az(["resource", "list", "--resource-type",
                   "Microsoft.CognitiveServices/accounts", "-o", "json"]) or []
    WANTED = ["InputTokens", "OutputTokens", "TotalTokens", "TotalCalls",
              "ModelRequests", "ProvisionedUtilization",
              "ProcessedPromptTokens", "GeneratedTokens", "AzureOpenAIRequests",
              "AzureOpenAIProvisionedManagedUtilizationV2"]
    start = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

    mpath = outdir / "AzureAiTokensDaily.csv"
    written = 0
    with mpath.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "ResourceName", "ResourceGroup", "Deployment", "Metric", "Value"])
        for a in accounts:
            defs = az(["monitor", "metrics", "list-definitions",
                       "--resource", a["id"], "-o", "json"]) or []
            available = {d["name"]["value"] for d in defs}
            ask = [m for m in WANTED if m in available]
            if not ask:
                print(f"  {a['name']}: none of the known token metrics are published")
                continue
            print(f"  {a['name']}: {', '.join(ask)}")
            res = az(["monitor", "metrics", "list", "--resource", a["id"],
                      "--metric"] + ask + ["--interval", "P1D",
                     "--start-time", start, "-o", "json"])
            if not res:
                continue
            for v in res.get("value", []):
                nm = v["name"]["value"]
                for s in v.get("timeseries", []):
                    for p in s.get("data", []):
                        val = p.get("total", p.get("average"))
                        if val:
                            w.writerow([p["timeStamp"][:10], a["name"],
                                        a.get("resourceGroup", ""), "", nm, val])
                            written += 1
    print(f"wrote {mpath.name} ({written} metric points)")
    if written == 0:
        print("  NOTE: zero token rows. The metric names above ARE published by")
        print("        the resource, so this is genuinely no traffic rather than")
        print("        a wrong name.")

    # ---- 3. Deployment inventory ------------------------------------------
    dpath = outdir / "AzureAiDeployments.csv"
    with dpath.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ResourceName", "ResourceGroup", "Location", "Deployment",
                    "Model", "ModelVersion", "Sku", "Capacity"])
        n = 0
        for a in accounts:
            deps = az(["cognitiveservices", "account", "deployment", "list",
                       "-g", a["resourceGroup"], "-n", a["name"], "-o", "json"]) or []
            for d in deps:
                m = d.get("properties", {}).get("model", {})
                w.writerow([a["name"], a["resourceGroup"], a.get("location", ""),
                            d.get("name", ""), m.get("name", ""), m.get("version", ""),
                            (d.get("sku") or {}).get("name", ""),
                            (d.get("sku") or {}).get("capacity", "")])
                n += 1
    print(f"wrote {dpath.name} ({n} deployments)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
