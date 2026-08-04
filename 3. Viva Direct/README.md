# 3. Viva Direct *(experimental — read this before you start)*

Connect straight to Viva Insights through the certified Power BI connector, with no file handling
at all.

---

## ⚠️ Start here

**This path is not confirmed to work for credit consumption data.** Please read that sentence again
before you spend an afternoon on it.

Here is exactly what is and is not known:

**Verified.** Microsoft ships a certified first-party **Viva Insights** connector in Power BI Desktop
under *Get Data → Online Services*. It connects to **Analyst Workbench query results** using a
Partition Identifier and Query Identifiers. It supports scheduled refresh. This is all documented.
([power-bi-connector][c1], updated 2026-04-25)

**Not verified.** Whether the connector exposes the **Consumption Dashboard** credit data —
`PersonServiceCreditsMetrics` and friends — at all. The connector documentation describes Analyst
Workbench collaboration queries. It does not mention credit consumption. The consumption export may
well be download-only.

**Why we shipped the folder anyway.** You asked for it, the connector plainly exists, and if it does
carry credit data this is the best of the three paths — no files, no notebooks, native scheduled
refresh. It is worth ten minutes to find out. But we are not going to write confident instructions
for something we have not seen work.

**→ [TEST-PROCEDURE.md](TEST-PROCEDURE.md) makes the test decisive.** Ten minutes, and you will know
for certain which way it falls.

**If it turns out not to carry credit data**, use **[2. Fabric](../2.%20Fabric/)** for automation or
**[1. Local CSV](../1.%20Local%20CSV/)** to get going quickly. Please
[open an issue](../../issues) either way — a definitive answer helps everyone.

---

## How to find out in ten minutes

1. Run a query in Viva Insights that you believe contains credit consumption data.
2. Open Power BI Desktop → **Get Data** → **Online Services** → **Viva Insights** → **Connect**.
3. In Viva Insights, go to **Analysis results** and click the **Link** icon next to your query. That
   gives you the **Partition Identifier** and **Query Identifiers**.
4. Paste both into the connector dialog. Leave **Query Name** blank.
5. Under **Advanced**, set:
   - **Schema type** → **Pivoted** *(Unpivoted is no longer supported)*
   - **Data granularity** → **Row-level data** *(Aggregated is no longer supported)*
   - **Table name** → only needed for multi-table queries
6. **Data Connectivity mode** → **Import**. *(DirectQuery is no longer supported.)*
7. Load, and look at the columns you get.

**What you're looking for:** columns resembling `PersonId` or `UserPrincipalName`, `ServiceName`,
`SpendingPolicyId`, `MetricDate` and `Total Copilot Credits used`. If you see those, the path works
and we would very much like to hear about it. If you only get collaboration metrics — meeting hours,
email volume, focus time — then the connector does not carry consumption data and this path is a dead
end for CreditLens.

---

## Requirements

| | |
|---|---|
| **Role** | Viva Insights **Analyst** (assigned by a Global Administrator) |
| **Power BI** | Desktop December 2022 or newer |
| **Licence** | No Premium or Fabric capacity needed for the connector itself |

---

## Scheduled refresh

Two things must both be true, or the report goes stale while appearing to refresh:

1. **Auto-refresh** must be enabled on the source query in Viva Insights → Analysis results.
2. **Scheduled refresh** must be configured on the semantic model in the Power BI Service.

Miss the first and Power BI will faithfully re-read a result set that never changes.

---

## A privacy note worth reading

The connector **does not enforce Viva Insights privacy rules**, including minimum group size. It
returns row-level data and it is on you to apply appropriate aggregation before anyone sees it.

> *"The connector doesn't enforce privacy rules, including Minimum group size."*
> — [power-bi-connector][c1]

CreditLens shows per-person consumption by design — that is the point of a chargeback report — but
check whether per-person reporting requires works-council consultation or similar in your
jurisdiction before publishing it.

---

## If it works

Tell us, and we will build a proper `.pbit` for this path with the connector wired in. Right now
there is no template in this folder, because shipping one that connects to something we cannot
confirm exists would be worse than shipping nothing.

---

## Known deprecations

If you have an older Viva Insights connection anywhere, these are all now unsupported:

| Was | Now |
|---|---|
| DirectQuery | **Import** only |
| Unpivoted schema | **Pivoted** only |
| Aggregated granularity | **Row-level data** only |

To convert an existing one: change Storage mode to Import in Model view, then set `APIType` to
`"Row-level data"` and `SchemaType` to `"Pivoted"` in the formula bar.

---

[c1]: https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/power-bi-connector

**Source:** [Viva Insights Power BI connector][c1], checked 2026-04-25.
