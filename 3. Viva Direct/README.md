# 3. Viva Direct

Connect straight to the Consumption Dashboard through the certified Viva Insights connector — no
files, no notebooks, native scheduled refresh.

---

## Status: confirmed to exist, not yet confirmed to work

**The connection is real.** The Consumption Dashboard's own export dialog has a **Connect data**
button that hands you a **Partition identifier** and a **Query identifier**, under two tabs:

| Tab | For |
|---|---|
| **Power BI** | Also offers **Download Power BI template** — Microsoft's own starter template |
| **Microsoft Fabric** | Dataflow Gen2, documented at [export-query-data-microsoft-fabric][d1] |

So this is not a guess about whether Analyst Workbench queries happen to carry credit data. The
Consumption Dashboard publishes identifiers specifically for this purpose.

**What is not yet confirmed** is that a given tenant can actually use it. Our first attempt returned
**access forbidden**, which looks like a tenant-side permission rather than anything in the
connection — most likely the Viva Insights **Analyst** role, or connector access not yet granted.

Until someone completes the round trip, this folder ships a test procedure rather than a template.
**[TEST-PROCEDURE.md](TEST-PROCEDURE.md)** makes the test decisive in about ten minutes.

**A model wired for it already exists** — see [Already wired](#already-wired) below.

---

## Worth knowing before you invest in this

Microsoft ships **its own Power BI template** from that same dialog. Download it first.

It will cover Cowork consumption from the Consumption Dashboard, and it will do that with
first-party support. CreditLens is a different proposition: three products in one report — Cowork,
Copilot Studio and GitHub Copilot — with cost, optimisation and forecast pages over all of them.

If you only need Cowork, use Microsoft's. If you are trying to see the whole Copilot bill in one
place, that is what this is for.

---

## Getting the identifiers

1. <https://analysis.insights.cloud.microsoft> → **Consumption Dashboard**
2. The **download** icon, top right
3. Choose **Export by week** *(weekly is what CreditLens is built on)*
4. **Connect data** → **Power BI** tab
5. Copy **Partition identifier** and **Query identifier**

## Connecting

Power BI Desktop → **Get Data** → **Online Services** → **Viva Insights** → **Connect**

| Field | Value |
|---|---|
| Partition Identifier | from step 5 |
| Query Name | **leave blank** |
| Query Identifiers | from step 5 |
| **Advanced** → Schema type | **Pivoted** — Unpivoted is no longer supported |
| **Advanced** → Data granularity | **Row-level data** — Aggregated is no longer supported |
| **Advanced** → Table name | only for multi-table queries |
| Data Connectivity mode | **Import** — DirectQuery is no longer supported |
| Authentication | **Organizational account** |

Get any of the three Advanced settings wrong and you may load something that looks plausible but is
not row-level. Check them before clicking Load.

---

## Already wired

A CreditLens variant with the connector in place exists at `CreditLens-VivaDirect`. It adds two
parameters — `VivaPartitionId` and `VivaQueryId` — and swaps the metrics source from CSV to:

```m
VivaInsights.Data(
    VivaPartitionId,
    null,                    // Query Name - blank
    VivaQueryId,
    [SchemaType = "Pivoted", APIType = "Row-level data"]
)
```

Microsoft does not publish that function's signature. It was read out of Power BI Desktop's own
connector registry, which declares `VivaInsights.Data` with an options record at position 3 —
meaning arguments 0–2 are the three dialog fields in dialog order. The model loads, so the name and
arity are right; what remains untested is the round trip to real data.

Everything downstream is unchanged. The column normalisation that already copes with both export
shapes will cope with the connector too, provided it returns the same columns.

**One known gap.** Spending policy *names* have no connector equivalent — the dashboard exposes one
query result, and names live in `SpendingPolicyMetadata.csv`. Without that file, policies show as
GUIDs. Pricing is unaffected: the limits travel inline on the metrics rows.

---

## Troubleshooting the connection

### `(500): Internal Server Error` on refresh

```
Web.Contents failed to get contents from
'https://api.analysis.insights.svc.cloud.microsoft/v1.0/tenants/{tenant}
 /scopes/{partition}/reports/{query}/result' (500)
```

**Good news first: this is not an authentication failure.** Auth failures come back as `403
Forbidden`. A 500 means the service accepted your token *and* the request, then failed producing the
result — so the tenant permission (Analyst role) is in place.

The argument order is also fine. Your **query** identifier appears in the `reports/` position and
your **partition** identifier in `scopes/`, which is what the service expects — so the M in
`CreditLens-VivaDirect` is putting both GUIDs where they belong.

That leaves three candidates, all beyond the connector:

| Candidate | How to check |
|---|---|
| **The query has never produced a result.** A query can be defined without having been run, and `/result` has nothing to return. | Viva Insights → **Analysis results**. The query should show a completed run with a row count, not just "created". Run it once and retry. |
| **The Advanced settings do not suit this query.** `Row-level data` and `Pivoted` are the only supported values, but a query that was set up to return aggregated output may reject them server-side. | Re-check the download dialog. If it offers a choice, take the one that matches what you set. |
| **The partition identifier is not the one the dashboard issued.** Ours resolved to the tenant GUID, which *may* be right — or may be a paste of the wrong field. | Re-copy both from **Consumption Dashboard → download → Connect data → Power BI**, and confirm the partition really is a distinct value rather than your tenant ID. |

### The test that separates "our M" from "the service"

Two minutes, and it is worth doing before anything else:

1. New Power BI Desktop file
2. **Get Data → Online Services → Viva Insights**
3. Enter the **same two identifiers**, Advanced → `Pivoted` / `Row-level data`

- **Native connection also fails with 500** — the template is not the problem. The fix belongs in
  Viva Insights: run the query, or check what the dashboard is actually offering to export.
- **Native connection succeeds** — then our M differs from what the dialog generates. View the
  generated query (*Advanced Editor*), send it over, and we match it exactly.

Everything downstream of `VivaConnectorSource` is shared with the CSV path and already proven, so a
working connector call is the only missing piece.

---

## Scheduled refresh

Two things must both be true, or the report goes stale while appearing to refresh:

1. **Auto-refresh** enabled on the query in Viva Insights → Analysis results
2. **Scheduled refresh** configured on the semantic model in the Power BI Service

Viva Insights refreshes over the weekend, so schedule for **Tuesday morning** — Microsoft suggests
around 8am PST for the Fabric route, and the same reasoning applies here.

---

## A privacy note

The connector **does not enforce Viva Insights privacy rules**, including minimum group size. It
returns row-level data and it is on you to aggregate appropriately before publishing.

> *"The connector doesn't enforce privacy rules, including Minimum group size."* — [connector docs][d2]

CreditLens shows per-person consumption deliberately — that is what a chargeback report is for — but
check whether that needs works-council consultation where you operate.

---

## Known deprecations

| Was | Now |
|---|---|
| DirectQuery | **Import** only |
| Unpivoted schema | **Pivoted** only |
| Aggregated granularity | **Row-level data** only |

To convert an older connection: change Storage mode to Import in Model view, then set `APIType` to
`"Row-level data"` and `SchemaType` to `"Pivoted"` in the formula bar.

---

[d1]: https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/export-query-data-microsoft-fabric
[d2]: https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/power-bi-connector

**Sources:** [Export query data to Microsoft Fabric][d1] (2026-03-06) ·
[Viva Insights Power BI connector][d2] (2026-04-25) · portal steps checked 2026-08-04.
