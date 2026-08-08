# Viva Insights connector — what we found

Reference for the **[3. Viva Direct](../3.%20Viva%20Direct/)** path. You don't need this to connect;
it's here for when something doesn't behave.

All verified against a live tenant in August 2026.

---

## Custom query vs Consumption Dashboard export

| | Custom query | Consumption Dashboard |
|---|---|---|
| Auto-refresh | ✅ | ❌ |
| Real UPNs under identification | ✅ | ✅ |
| Org attributes | ✅ analyst chooses | limited |
| `VivaExportName` needed | ❌ **leave blank** | ✅ required |
| Policy names | in-query column | separate table |

**Use a custom query** unless you have a reason not to.

---

## Table names that answer

The connector exposes more than one table, and the names are not guessable.

| `TableName` | Returns |
|---|---|
| *(omitted)* | The metrics — UPN, EntraId, service, policy, date, credits, `PeopleHistoricalId` |
| **`PeopleHistorical`** | Org attributes — `PeopleHistoricalId`, `IsCopilotLicensed`, `Domain`, `Organization`, `PopulationType`, time zones |
| **`HR`** | Same table, same columns |
| `PeopleMetaData` | ❌ **fails** — despite being the name the CSV export uses |
| `Data_PeopleMetaData`, `Data_People`, `OrganizationalData` | ❌ |

The model tries `PeopleHistorical`, then `HR`, then `PeopleMetaData`, and falls back to the Entra
file if none answer.

**The join key is `PeopleHistoricalId`**, which the metrics rows also carry.

---

## The 500 error

A Consumption Dashboard export is **multi-table**. Omit `TableName` and the connector returns a bare
`(500) Internal Server Error` — it does not say a table name is needed.

| Export | `VivaExportName` |
|---|---|
| Identified | `IdentifiableAiConsumptionWeeklyExport` |
| De-identified | `AiConsumptionWeeklyExport` |

To check yours: **Download Power BI template** from the same dialog, open it, and read a table name
in Power Query. Whatever precedes `Data_` is your export name.

**A custom query returns a single table, so none of this applies — leave the parameter blank.**

---

## Org attribute precedence

All three paths follow the same order:

| | Source | Keyed by |
|---|---|---|
| 1 | Org columns on the metrics rows | UPN |
| 2 | Viva's people table | `PeopleHistoricalId` → UPN |
| 3 | An Entra directory export | UPN |

Viva wins when present. A column that exists but is blank for everyone counts as absent — otherwise
it offers a Group By entry that yields one empty bucket.

`IsCopilotLicensed` and the time zone columns are dropped as non-organisational.

---

## Org filtering coverage

Once org data is present, the **Group By** slicer filters Cowork, Copilot Studio and GitHub Copilot
together. Verified by simulating a slicer selection and checking each table responds.

Studio's **per-agent** and **tenant** pages don't filter by org — they carry no person column, so
there's nothing to join on. That's inherent to those exports.

Azure AI Foundry is the same: Cost Management is resource-grained. Where a resource carries a
department tag it can be attributed; otherwise the Foundry page says what share cannot be.
