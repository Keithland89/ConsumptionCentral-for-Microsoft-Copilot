# 3. Viva Direct

Connect straight to Viva Insights through the certified connector — no files, no notebooks, native
scheduled refresh.

**`Consumption Central - Viva Direct.pbit`** is in this folder. Open it, paste two identifiers, done.

---

## Bring whichever products you have

> ### **Only two boxes are required. One product is enough.**
>
> This path is built for Cowork, so `VivaPartitionId` and `VivaQueryId` are the two you must fill.
> **Everything else in the parameter prompt is optional — leave it blank.**
>
> Copilot Studio and GitHub Copilot are bonus pages. Add them if you have them; skip them if you
> don't. Their pages come up empty and nothing else changes.

The prompt is long. Ignore most of it:

| Fill in | Leave blank |
|---|---|
| `VivaPartitionId` | everything starting `Studio…` |
| `VivaQueryId` | everything starting `GitHub…` |
| | `EntraCsvPath`, `VivaExportName`, and all the rate parameters |

*The rates default to the published $0.01 per credit — correct for most agreements.*

---

## The short version

1. Viva Insights → **Analysis** → build a query with the Copilot credit metrics → **Auto-refresh on**
2. **Analysis results** → your query → the **Link** icon → copy the two identifiers
3. Open `Consumption Central - Viva Direct.pbit`, paste them into the two Viva boxes, leave the rest blank

The rest of this page is the detail behind those three steps.

---

## Status: working

Verified end to end on a live tenant: the connector returned real UPNs and credit figures matching
the CSV export of the same query, exactly.

**Use a custom query.** Viva Insights → **Analysis** → create an analysis with the Copilot credit
metrics → turn on **Auto-refresh**. Then **Analysis results** → your query → the **Link** icon for
the two identifiers.

| | Custom query *(recommended)* | Consumption Dashboard export |
|---|---|---|
| Auto-refresh | ✅ | ❌ |
| Real UPNs under identification | ✅ | ✅ |
| Org attributes | ✅ *analyst chooses* | ❌ |
| `VivaExportName` | **leave blank** | must be set — see below |
| Policy names | in-query column | separate table, read automatically |

**A model wired for it exists** at `ConsumptionCentral-VivaDirect` — see [Already wired](#already-wired).

> **If you use the Consumption Dashboard export, `VivaExportName` must be set.**
>
> That export is a **multi-table** query result and the connector fails with a bare
> `(500): Internal Server Error` when the table name is missing — it does not say a table name is
> needed. The Learn article lists Glint, Copilot business impact and Skills landscape as the
> multi-table queries and does not mention this one, so there is nothing to warn you.
>
> | Export | `VivaExportName` |
> |---|---|
> | Identified | `IdentifiableAiConsumptionWeeklyExport` |
> | De-identified | `AiConsumptionWeeklyExport` |
>
> Verify yours: **Download Power BI template** from the same dialog, open it, and read a table name
> in Power Query. Whatever precedes `Data_` is your export name.
>
> A custom query returns a single table, so none of this applies — leave the parameter blank.

---

## Worth knowing before you invest in this

Microsoft ships **its own Power BI template** from that same dialog. Download it first.

It will cover Cowork consumption from the Consumption Dashboard, and it will do that with
first-party support. Consumption Central is a different proposition: three products in one report — Cowork,
Copilot Studio and GitHub Copilot — with cost, optimisation and forecast pages over all of them.

If you only need Cowork, use Microsoft's. If you are trying to see the whole Copilot bill in one
place, that is what this is for.

---

## Getting the identifiers

1. <https://analysis.insights.cloud.microsoft> → **Consumption Dashboard**
2. The **download** icon, top right
3. Choose **Export by week** *(weekly is what Consumption Central is built on)*
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

A Consumption Central variant with the connector in place exists at `ConsumptionCentral-VivaDirect`.

### What it asks you for

**Two identifiers. That's it.** The prompt lists 21 boxes; 19 of them are optional.

| Parameter | | |
|---|---|---|
| `VivaPartitionId` | **required** | Partition identifier, from **Analysis results → Link** |
| `VivaQueryId` | **required** | Query identifier, from the same place |
| *everything else* | *leave blank* | Studio, GitHub, org file, rates — all optional |

<details>
<summary>The optional ones, if you want them</summary>

| Parameter | When |
|---|---|
| `StudioTenantCsvPath`, `StudioAgentCsvPath`, `StudioUserCsvPath` | you have Copilot Studio and want its 4 pages |
| `GitHubUsageCsvPath`, `GitHubUserMapCsvPath` | you have GitHub Copilot and want its 4 pages |
| `EntraCsvPath` | **fallback only** — Viva's own org attributes are used first; supply this only if your query carries none. See [docs/ORG-DATA.md](../docs/ORG-DATA.md) |
| `VivaExportName` | you're using a Consumption Dashboard export, not a custom query — see below |
| the rate parameters | your agreement differs from the published $0.01 per credit |

</details>

### Use a custom query

**Viva Insights → Analysis → create an analysis → Copilot credit metrics → Auto-refresh on.**

A custom query beats the Consumption Dashboard export on every axis that matters here:

| | Custom query | Consumption Dashboard |
|---|---|---|
| Auto-refresh | ✅ | ❌ |
| Real UPNs under identification | ✅ | ✅ |
| Org attributes | ✅ *analyst chooses* | ❌ |
| Table name needed | ❌ **none** | ✅ and getting it wrong gives a bare 500 |
| Policy names | in-query column | separate table |

**Verified live on both.** A custom query returns one table with
`UserPrincipalName, EntraId, ServiceId, ServiceName, SpendingPolicyId, MetricDate, Session count,
Spending policy limit, Total Copilot Credits used, User limit, PeopleHistoricalId` — no table name
required. Six candidate table names were tried; only *no name* and `MetricOutput` worked.

**So leave `VivaExportName` blank.** Set it only for a Consumption Dashboard export, to
`IdentifiableAiConsumptionWeeklyExport` or `AiConsumptionWeeklyExport`. That export is multi-table
and its tables are named after it, which is why the name is needed there and nowhere else.

Four CSV parameters used to sit here and all were wrong to have:

- `VivaMetricsCsvPath` had **zero references**. Dead weight in the prompt.
- `VivaPeopleCsvPath`, `VivaPolicyCsvPath` and `PersonMapCsvPath` fed a file-based seat roster that
  **silently outranked the connector**. Point them at another tenant's export — or at the sample data
  in this repo — and you get a roster of people with no usage joined to usage by people not on the
  roster. Every page then reads zero credits against a full set of seat limits, which looks like a
  broken measure rather than a mismatched file.

### Where org data comes from

**Viva first. The Entra file is a fallback.**

Viva publishes org attributes on a **people table**, keyed by `PeopleHistoricalId`, which the model
joins to the usage rows for you. Whatever it carries is used automatically. `EntraCsvPath` is read
**only** when Viva carries nothing usable, and ignored entirely when it does.

So try it blank first. Load the report, open **Group By**, and see what's offered.

**Measured against two live exports:**

| Export | `PeopleMetaData` columns |
|---|---|
| De-identified | `PeopleHistoricalId`, `IsCopilotLicensed`, `Domain`, **`Organization`**, **`PopulationType`**, `StandardTimeZone`, `TimeZone` |
| Custom query *(as built)* | `PeopleHistoricalId`, `IsCopilotLicensed` — nothing else |

> ### If Group By is empty, add org attributes to your Viva query
>
> **This is usually the fix, not the Entra file.** A custom query returns only what the analyst
> selected under *"Select spending policy and employee attributes to include in the query"*. Add
> Department / Job title / Manager / Function there and re-run — they arrive on the people table and
> the model picks them up automatically. No file, no parameter.

A column that is present but blank for everybody is treated as absent — it would otherwise offer a
Group By entry that yields a single empty bucket. In a live test `Organization` was blank while
`Domain` and `PopulationType` were populated, so only the latter two were offered.
`IsCopilotLicensed` and the two time zone columns are dropped as non-organisational.

<details>
<summary>Connector table names — what answers and what doesn't</summary>

**Verified live against a custom query.** The names are not the ones the CSV export uses:

| `TableName` | Result |
|---|---|
| *(omitted)* | ✅ the metrics — `UserPrincipalName`, `EntraId`, `ServiceId`, `ServiceName`, `SpendingPolicyId`, `MetricDate`, session/credit columns, `PeopleHistoricalId` |
| **`PeopleHistorical`** | ✅ **the org attributes** — `PeopleHistoricalId`, `IsCopilotLicensed`, `Domain`, `Organization`, `PopulationType`, `StandardTimeZone`, `TimeZone` |
| **`HR`** | ✅ same table, same columns |
| `PeopleMetaData` | ❌ — *this is the name the CSV export uses, and it does not work* |
| `Data_PeopleMetaData`, `Data_People`, `OrganizationalData` | ❌ |

The model tries `PeopleHistorical`, then `HR`, then `PeopleMetaData`, and falls through to the Entra
file if none answer.

**The join is `PeopleHistoricalId`**, which the metrics rows also carry — that is what connects a
person's org attributes to their credit usage.

</details>

### Org filtering covers all three products

Once org data is present, the **Group By** slicer filters Cowork, Copilot Studio *and* GitHub
Copilot together — the relationships already exist and were verified live:

| | Joined on |
|---|---|
| Cowork | `CoworkBilling` / `CreditsWeekly` → `Org` via UPN |
| Copilot Studio | `Credit Consumption (User)` → `Org` via `User_Email` |
| GitHub Copilot | `GitHub User` → `Org` via UPN, then → `GitHub Usage` |

Studio's **per-agent** and **tenant** pages don't filter by org — they have no person column, so
there is nothing to join. That is inherent to those exports, not a gap in the model.

Full detail: **[docs/ORG-DATA.md](../docs/ORG-DATA.md)**.

> **If Group By is empty, check the UPNs match.** A directory export for a different tenant matches
> nobody and fills the department table with people who have no credits. That is a mismatched file,
> not a broken report, and it is the most common cause of one looking broken.

### The connector call

```m
VivaInsights.Data(
    VivaPartitionId,
    null,                    // Query Name - blank
    VivaQueryId,
    [
        SchemaType = "Pivoted",
        APIType    = "Row-level data",
        TableName  = VivaExportPrefix & "Data_UserAIConsumptionActivity"
    ]
)
```

The signature was originally read out of Power BI Desktop's connector registry and is confirmed
against Microsoft's own generated template, which issues exactly this call.

Everything downstream is unchanged. The column normalisation that copes with both export shapes
copes with the connector too — including the connector's lack of a `PersonId` column, which the
loader synthesises from the UPN.

**Policy names come from the connector**, via the plans table above. This corrects an earlier note in
these docs claiming they had no connector equivalent. Pricing is unaffected either way — the limits
travel inline on the metrics rows.

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
`ConsumptionCentral-VivaDirect` is putting both GUIDs where they belong.

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

Consumption Central shows per-person consumption deliberately — that is what a chargeback report is for — but
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
