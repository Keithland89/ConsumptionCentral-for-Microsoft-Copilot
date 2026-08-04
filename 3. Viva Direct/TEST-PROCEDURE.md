# Testing the Viva Insights connector — ten minutes

The one open question on this path: **does the certified Viva Insights connector expose Consumption
Dashboard credit data, or only Analyst Workbench collaboration queries?**

This page makes that test decisive. Follow it, record the outcome in the table at the bottom, and
open an issue either way — a firm answer helps everyone.

---

## What you need

- **Viva Insights Analyst** role
- Power BI Desktop, December 2022 or newer
- A query in Viva Insights whose results you believe contain credit consumption

---

## Step 1 — Get the identifiers

1. Open the Viva Insights web app → **Analysis results**
2. Find the query whose results you want
3. Click the **Link** icon next to it
4. Copy both:
   - **Partition Identifier**
   - **Query Identifiers**

> If the Link icon is absent, the query has not finished, or its results are not exposed to the
> connector. That is itself a finding — note it.

## Step 2 — Connect

Power BI Desktop → **Get Data** → **Online Services** → **Viva Insights** → **Connect** → **Continue**

| Field | Value |
|---|---|
| Partition Identifier | *(from step 1)* |
| Query Name | **leave blank** |
| Query Identifiers | *(from step 1)* |
| **Advanced** → Schema type | **Pivoted** — Unpivoted is no longer supported |
| **Advanced** → Data granularity | **Row-level data** — Aggregated is no longer supported |
| **Advanced** → Table name | only for multi-table queries |
| Data Connectivity mode | **Import** — DirectQuery is no longer supported |

Get any of the three Advanced settings wrong and the connector may load something that looks
plausible but is not row-level. Check them before clicking Load.

## Step 3 — Read the column list

**Do not click Load yet.** The Navigator preview is enough to answer the question.

### ✅ It works — you see something like

| Column | Or |
|---|---|
| `PersonId` | `UserPrincipalName` |
| `ServiceName` | values `Cowork`, `Work IQ API` |
| `SpendingPolicyId` | |
| `MetricDate` | |
| `Total Copilot Credits used` | any credits column |
| `Spending policy limit` | `User limit` |

Any two or three of those together means the connector carries consumption data. **That is the good
outcome** — this becomes the best of the three paths: no files, no notebooks, native scheduled
refresh.

### ❌ It does not — you see only

`Meeting_hours`, `Email_hours`, `After_hours_collaboration`, `Internal_network_size`,
`Focus_hours`, `Chats_sent`, `Collaboration_hours`…

Collaboration metrics with **no credits, no spending policy, no service name** means the connector
covers Analyst Workbench queries only and this path is a dead end for CreditLens. Use
**[2. Fabric](../2.%20Fabric/)** for automation, or **[1. Local CSV](../1.%20Local%20CSV/)** to get
going today.

### 🤔 Ambiguous

Credit-ish columns but not the ones above — capture the **full column list** and put it in the issue.
A different-but-usable shape is worth adapting the template for.

---

## Step 4 — If it worked, check the grain

Load it and run this in a blank query to confirm it is row-level rather than pre-aggregated:

```
EVALUATE
ROW(
    "rows",        COUNTROWS( 'YourVivaTable' ),
    "people",      DISTINCTCOUNT( 'YourVivaTable'[PersonId] ),
    "dates",       DISTINCTCOUNT( 'YourVivaTable'[MetricDate] ),
    "earliest",    MIN( 'YourVivaTable'[MetricDate] ),
    "latest",      MAX( 'YourVivaTable'[MetricDate] ),
    "credits",     SUM( 'YourVivaTable'[Total Copilot Credits used] )
)
```

Two things to check:

**Is it row-level?** `rows` should be roughly `people × dates`. If `rows` equals `people`, or equals
`dates`, you have an aggregate and the Advanced settings did not take.

**Does it go back further than the download?** The file export gives 6 months weekly. If the
connector reaches further, that is a significant advantage — it would remove the main reason to run
the Fabric path at all.

**Cross-check against a file export** covering the same window. The totals should match. If they do
not, say so in the issue — a silent discrepancy between two Microsoft surfaces is worth knowing
about.

---

## Step 5 — Record it

| | |
|---|---|
| Date tested | |
| Tenant type | production / demo |
| Identifiable export enabled? | yes / no |
| Link icon present? | yes / no |
| **Credit columns present?** | **yes / no** |
| Columns seen | *(paste the list)* |
| Row-level confirmed? | yes / no |
| History depth | *(earliest → latest)* |
| Matches file export? | yes / no / not checked |

Please [open an issue](../../issues) with this table filled in, whichever way it went. A confirmed
"no" is as useful as a "yes" — it stops the next person spending an afternoon on it.

---

## If it works, what happens next

We build a proper `.pbit` for this path with the connector wired in, and the folder gets a real
README instead of a caveat.

The model needs no changes: the loader already normalises whatever person key it is given, so
connector output would be wired in exactly like the CSV path. It is the connection, not the model,
that is in question.

---

## One thing to be aware of either way

The connector **does not enforce Viva Insights privacy rules**, including minimum group size. It
returns raw row-level data.

> *"The connector doesn't enforce privacy rules, including Minimum group size."*
> — [Viva Insights Power BI connector](https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/power-bi-connector),
> checked 2026-04-25

CreditLens shows per-person consumption deliberately — that is what a chargeback report is for — but
check whether per-person reporting needs works-council consultation or similar where you operate
before publishing it.
