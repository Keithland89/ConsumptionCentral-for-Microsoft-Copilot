# 2. Fabric / Lakehouse deployment *(recommended)*

Land the exports in a Fabric Lakehouse, read them through the SQL analytics endpoint, refresh on a
schedule.

**Why bother?** The Viva Insights consumption export only reaches back **6 months**. Every week you
don't capture is gone permanently. This path accumulates history in a Delta table that outlives the
export window — a year from now you have a year of trend, not the same rolling six months.

You also get scheduled refresh, sub-second pages on large tenants, and one governed copy of the data
rather than CSVs on someone's laptop.

**You need** Fabric capacity, Premium, or PPU. If you only have Power BI Pro, use
**[1. Local CSV](../1.%20Local%20CSV/)**.

---

## Bring whichever products you have

> ### **Every table is optional. One product is enough.**
>
> Load Cowork only and its four pages work. Studio only, or GitHub only — same. A missing table is a
> supported state, not an error: those pages come up empty and nothing else is affected.

*Verified by deleting tables from a live Lakehouse and refreshing — each product's figures were
unchanged by the others' absence.*

---

## The short version

1. Create a Lakehouse
2. Land whatever data you have — **one product is enough**
3. Open `CreditLens - Fabric.pbit`, paste two values, done

**The Viva half can run itself.** Viva Insights ships a **Dataflow Gen2** connector that writes query
results straight into a Lakehouse on a schedule — no download, no notebook. See
[Automating the Viva load](#automating-the-viva-load).

The rest of this page is the detail behind those three steps.

---

## What's in this folder

```
notebooks/                 six — Viva, Studio, GitHub (API), GitHub (CSV), Org, commercial terms
flows/                     automating the landing step with Power Automate
docs/DATA-DICTIONARY.md    every table and column, with merge keys and caveats
seed_sample_data.py        load the sample dataset into a Lakehouse, for a quick try
README.md                  this file
CreditLens - Fabric.pbit   the template
```

[vivafabric]: https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/export-query-data-microsoft-fabric

The model has been built and tested end to end against a live Lakehouse — all nine tables, plus two
partial-product subsets. See [Table contracts](#table-contracts) for the figures.

## How it fits together

```
Viva Insights  ─┐  (manual download)
Power Platform ─┼─▶  Files/landing/*.csv  ─▶  ingester notebooks  ─▶  Delta tables
Entra          ─┘         (OneLake)                    ▲                   │
                                                       │                   │
GitHub  ────────────── REST API, scheduled ────────────┘                   ▼
                                                        SQL analytics endpoint
                                                                  │
                                                                  ▼
                                                    CreditLens - Fabric.pbit
```

The exports still have to be *fetched* — with one exception. **GitHub can be pulled straight from its
API on a schedule.** Viva, Studio and Entra have no usable API for this data, so those three land as
files. Once a file lands, everything downstream is automatic and history accrues.

---

## Quick start

### 1. Create a Lakehouse

Fabric portal → your workspace → **New** → **Lakehouse**. Call it something like `creditlens`.

### 2. Create the landing folder

In the Lakehouse **Files** area, create `landing/`.

### 3. Import the notebooks

Upload everything from [`notebooks/`](notebooks/) into the workspace and attach them to the Lakehouse.

| Notebook | Reads | Writes |
|---|---|---|
| `Ingest_Viva_Consumption.ipynb` | `landing/viva/*.csv` | `viva_credits_weekly`, `viva_spending_policy` |
| `Ingest_Studio.ipynb` | `landing/studio/*.csv` | `studio_tenant_daily`, `studio_agent`, `studio_user` |
| `Ingest_GitHub_API.ipynb` | **GitHub REST API** — no file | `github_ai_usage`, `github_user_map` |
| `Ingest_GitHub.ipynb` | `landing/github/*.csv` | same tables, from the emailed CSV |
| `Ingest_Org.ipynb` | `landing/org/*.csv` | `org_attributes` |
| *(or)* [ValueLens Graph ingester][vlorg] | **Microsoft Graph** — no file | `copilot_org_data` → see [docs/ORG-DATA.md](../docs/ORG-DATA.md) |

[vlorg]: https://github.com/Keithland89/ValueLens-for-Microsoft-Copilot/blob/main/2.%20Fabric/notebooks/Copilot_Org_Data_Direct_Ingester.ipynb
| `Ingest_CommercialTerms.ipynb` | **Azure Cost Management API** — no file | `commercial_terms` *(optional)* |

**GitHub is the one source that can run unattended.** Use `Ingest_GitHub_API.ipynb` and you never
download a GitHub file again — it reads the dedicated AI-credit endpoints, which carry 24 months of
history against the web report's 31 days. Needs a classic PAT with `read:enterprise` or
`manage_billing:copilot`, stored in Key Vault.

Use the CSV version instead only if you need `total_monthly_quota`, the `aic_*` columns, or
`repository` — none of which the AI-credit API returns.

Each notebook is **idempotent and append-safe**: it merges on the natural key, so re-running last
week's file does not double-count. That property is what makes accumulating history safe.

Two of the Studio exports carry **no date** — they are month-to-date aggregates — so the Studio
ingester stamps each load with a `snapshot_month` and merges on that. Run it monthly and you build
per-agent history from a source that has none. **The report reads the latest snapshot only**, since
each one is already a month-to-date total and summing them would multiply every agent's credits by
the number of months loaded. See
[docs/DATA-DICTIONARY.md](docs/DATA-DICTIONARY.md#studio_agent) for what that means when reading the
numbers.

`Ingest_CommercialTerms.ipynb` is the odd one out: it ingests no consumption data. It asks Azure
Cost Management what you were actually charged per credit and writes it to a one-row table that
overrides the template's parameters. Optional, and it needs **Cost Management Reader** — if that
grant is refused, skip it and set the rate in the template by hand.

### 4. Drop in your first exports

Upload each export into its `landing/` subfolder and run the matching notebook.

> **Only run the notebooks for products you actually have.** Skipping one is fine — its pages come up
> empty and everything else works. Don't wait until you have all three.

> **Or try it with sample data first.** [`seed_sample_data.py`](seed_sample_data.py) writes all nine
> tables straight into your Lakehouse from the synthetic dataset in
> [`1. Local CSV/sample-data/`](../1.%20Local%20CSV/sample-data/) — no exports, no notebooks, no
> waiting for a billing cycle:
>
> ```
> pip install pandas deltalake requests
> az login --tenant <your-tenant>
> python seed_sample_data.py --workspace <guid> --lakehouse <guid>
> ```
>
> Both GUIDs are in the Fabric portal URL with the Lakehouse open. It overwrites only the nine
> CreditLens tables and refuses to touch anything else, which matters because Lakehouses are usually
> shared. Testing convenience only — for real data use the notebooks, which merge rather than
> overwrite and so accumulate history.
Click-paths for getting the exports: **[docs/DATA-SOURCES.md](../docs/DATA-SOURCES.md)**.

### 5. Get the SQL connection string

1. Open the Lakehouse, and in the top-right switch from **Lakehouse** to **SQL analytics endpoint**
2. **Settings** (gear) → **SQL endpoint**
3. Copy **SQL connection string** — it looks like
   `<guid>.datawarehouse.fabric.microsoft.com`

*(Verified: [how-to-connect](https://learn.microsoft.com/en-us/fabric/data-warehouse/how-to-connect),
updated 2026-06-26.)*

### 6. Open the template

Double-click **`CreditLens - Fabric.pbit`** and supply:

| Parameter | Value |
|---|---|
| `FabricSQLEndpoint` | the string from step 5 |
| `LakehouseName` | your Lakehouse name, e.g. `creditlens` |

Then the commercial terms — see the
[table in the root README](../README.md#-commercial-terms-you-must-set).

> **Or don't.** On this path the commercial terms are optional. Publish a one-row
> [`commercial_terms`](docs/DATA-DICTIONARY.md#commercial_terms) table and it overrides every one of
> them, so the rate in the report is the rate on your invoice rather than a number somebody typed
> once and nobody revisited. Any column you leave out falls back to the parameter.

Power BI will ask you to sign in with an **Organizational Account**. That is expected: the endpoint
is Entra-authenticated and templates never carry credentials.

### 7. Publish and schedule

Publish to your workspace, then **Semantic model → Settings → Scheduled refresh**. Weekly, a day or
so after you expect to upload the Viva export, is a sensible cadence.

**No gateway needed.** The SQL analytics endpoint is a cloud source the Service reaches directly.

---

## Keeping it fed

Three of the four sources need someone to download a file. One does not.

| Source | Automatable? | Cadence | Why |
|---|---|---|---|
| **GitHub AI usage** | ✅ **Fully** | Nightly or monthly | Dedicated API endpoints, 24 months of history |
| Viva consumption | ⚠️ Manual *or* [Dataflow Gen2](#automating-the-viva-load) | **Weekly** | 6-month window, so don't drift |
| Copilot Studio | ❌ Manual | Monthly | CSV download only; ~3 months available |
| Entra org | ⚠️ Scriptable | Quarterly, or after a reorg | Graph PowerShell works; slow-moving anyway |

**Set up the GitHub notebook on a schedule and forget it.** The other three are the recurring chore,
and Viva is the one that actually matters — miss five months and that history is gone permanently.

**You can automate the landing step** for the manual sources with a Power Automate flow that watches
a mailbox or SharePoint library and writes to OneLake — see [`flows/`](flows/). Entra becomes fully
hands-off that way too. Viva and Studio still need someone to press export, but the flow removes the
"save it in the right place" step, which is where things actually go wrong.

---

## Works beyond Fabric

The template uses `Sql.Database()`, which speaks to anything exposing these tables over TDS:

- Fabric Lakehouse or Warehouse
- Databricks SQL Warehouse
- Synapse SQL pool
- Azure SQL

The notebooks are PySpark and run unchanged on Databricks or Synapse Spark. Only the connection
parameters change.

---

## Automating the Viva load

The Viva half of this pipeline does not have to be a manual download. Viva Insights ships a
**Dataflow Gen2** connector that writes query results directly into a Lakehouse table on a schedule:
[export-query-data-microsoft-fabric][vivafabric].

> **Use a custom query, not the Consumption Dashboard export.** The Learn article tells you to get
> the identifiers from **Analysis results** — which is where custom queries live. That is the
> intended route, and it is better in three ways:
>
> - **It auto-refreshes.** Turn on Auto-refresh on the query and the source keeps itself current.
> - **It returns a single table**, so `Table name` stays blank. The Consumption Dashboard export is
>   multi-table and needs the right name or the connector fails with a bare 500.
> - **The analyst chooses the columns**, including org attributes — which can remove the need for a
>   separate directory export entirely.
>
> Both work. The custom query is simply less to get wrong.

1. **Fabric** → your workspace → **New → Dataflow Gen2** → **Get data** → **Online Services** →
   **Viva Insights**
2. **Analysis results** → your query → the **Link** icon → copy the **Partition identifier** and
   **Query identifier**. **Query Name blank.**
3. Advanced: Schema type **Pivoted**, Data granularity **Row-level data**, **Table name**:

   | Source | Table name |
   |---|---|
   | **Custom query** | **leave blank** |
   | Consumption Dashboard, identified | `IdentifiableAiConsumptionWeeklyExportData_UserAIConsumptionActivity` |
   | Consumption Dashboard, de-identified | `AiConsumptionWeeklyExportData_UserAIConsumptionActivity` |

   Leave it blank on a multi-table export and the connector fails with a bare
   `(500): Internal Server Error`. It does not tell you a table name is needed.
4. Set the **data destination** to your Lakehouse, writing `viva_credits_weekly`. Match the columns
   in [docs/DATA-DICTIONARY.md](docs/DATA-DICTIONARY.md#viva_credits_weekly) and the template reads
   it with no change.
5. **Both** refreshes must be on, or the report goes stale while appearing to refresh:
   - **Auto-refresh** on the query, in Viva Insights → Analysis results
   - **Scheduled refresh** on the Dataflow — Microsoft suggests **Tuesday ~8am PST**, after Viva's
     weekend refresh

> **Org attributes, free.** If the custom query includes department, job family or similar, write
> them to `org_attributes` from the same Dataflow. They will always match the people in the metrics,
> which a separate directory export cannot guarantee. See
> [docs/ORG-DATA.md](../docs/ORG-DATA.md#where-org-data-comes-from).

> **A Consumption Dashboard export also publishes policy names** as a second table,
> `<export>Data_AIConsumptionPlans`. Add a second connection for it and write `viva_spending_policy`,
> and policies stop showing as GUIDs. A custom query has no equivalent — include a policy name column
> in the query itself instead.

**Dataflow Gen2 consumes Fabric Capacity Units**, unlike running a notebook over a file you dropped
in. On a small tenant the notebook route may well be cheaper. Both are supported — the notebooks are
not deprecated by this.

Studio, GitHub CSV and Org have no equivalent. GitHub has a real API, so
[`Ingest_GitHub_API.ipynb`](notebooks/Ingest_GitHub_API.ipynb) already runs unattended.

---

## Table contracts

Nine tables, all optional. See [`docs/DATA-DICTIONARY.md`](docs/DATA-DICTIONARY.md) for columns.

**Verified against a live Lakehouse.** All nine loaded, the report refreshed, and the figures matched
the source row for row. Two subsets were then tested by deleting tables and refreshing again:

| Tables present | Result |
|---|---|
| All nine | Cowork £5,134.64 · Studio 2,013 billed credits · GitHub $6,212.50 |
| GitHub + Org only | Refreshes. GitHub figures unchanged. Cowork/Studio pages empty. |
| Cowork + Studio + terms | Refreshes. Cowork and Studio figures **identical** to the full run. |

> **A note on removing a table while Desktop is open.** Power Query caches the connection's table
> list for the session, so a refresh straight after a table disappears still tries to read it and
> fails with `Invalid object name`. Restart Desktop and it is fine. Scheduled refreshes in the
> Service evaluate fresh each time and are unaffected.

Full column-by-column detail, including merge keys and the gotchas that matter when reading the
numbers, is in **[docs/DATA-DICTIONARY.md](docs/DATA-DICTIONARY.md)**.

| Table | Grain | Load |
|---|---|---|
| `viva_credits_weekly` | person × service × policy × week | merge |
| `viva_spending_policy` | policy | replace |
| `studio_tenant_daily` | environment × plan × capacity × day | merge |
| `studio_agent` | snapshot month × agent × feature × channel × environment | merge |
| `studio_user` | snapshot month × user × agent | merge |
| `github_ai_usage` | person × day × sku × model | merge |
| `github_user_map` | person | replace |
| `org_attributes` | person | replace |
| `commercial_terms` | one row | replace *(optional)* |

If you build your own pipeline, match the dictionary and the template works unchanged.

---

## Troubleshooting

**"Cannot connect"** — check the endpoint string has no `https://` prefix and no database suffix.
It is a bare hostname ending `.datawarehouse.fabric.microsoft.com`.

**Signs in, then no tables** — you have connected to `master`. Set `LakehouseName` explicitly rather
than leaving it blank.

**Refresh works in Desktop, fails in the Service** — usually privacy levels. Set each source to
**Organizational** in the semantic model's data source credentials.

**Tables exist but are empty** — the notebook ran against an empty landing folder. Check the file
actually uploaded, and that it is in the right subfolder.

**Numbers changed after a re-run** — the merge key didn't match, so rows were inserted rather than
updated. Check the export you re-ran covers the same weeks; the notebooks log row counts before and
after for exactly this reason.
