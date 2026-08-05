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
