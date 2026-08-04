# 2. Fabric / Lakehouse deployment *(recommended)*

Land the exports in a Fabric Lakehouse, read them through the SQL analytics endpoint, refresh on a
schedule.

**Why bother?** One reason above all others: **the Viva Insights consumption export only reaches back
6 months, and there is no API.** Every week you don't capture is gone permanently. This path
accumulates history in a Delta table that outlives the export window — so a year from now you have a
year of trend, not the same rolling six months.

You also get: scheduled refresh, sub-second pages on large tenants, and a single governed copy of the
data rather than CSVs on someone's laptop.

**You need** Fabric capacity, Premium, or PPU. If you only have Power BI Pro, use
**[1. Local CSV](../1.%20Local%20CSV/)**.

---

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

**GitHub is the one source that can run unattended.** Use `Ingest_GitHub_API.ipynb` and you never
download a GitHub file again — it reads the dedicated AI-credit endpoints, which carry 24 months of
history against the web report's 31 days. Needs a classic PAT with `read:enterprise` or
`manage_billing:copilot`, stored in Key Vault.

Use the CSV version instead only if you specifically need `total_monthly_quota` or the `aic_*`
columns, which are not in the API schema.

Each notebook is **idempotent and append-safe**: it merges on the natural key, so re-running last
week's file does not double-count. That property is what makes accumulating history safe.

### 4. Drop in your first exports

Upload each export into its `landing/` subfolder and run the matching notebook.
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
| Viva consumption | ❌ Manual | **Weekly** | No API, no scheduled export; 6-month window, so don't drift |
| Copilot Studio | ❌ Manual | Monthly | CSV download only; ~3 months available |
| Entra org | ⚠️ Scriptable | Quarterly, or after a reorg | Graph PowerShell works; slow-moving anyway |

**Set up the GitHub notebook on a schedule and forget it.** The other three are the recurring chore,
and Viva is the one that actually matters — miss six months and that history is gone permanently.

If you want to automate the *landing* step for the manual sources, a Power Automate flow that watches
a mailbox or SharePoint library and writes to OneLake works well — the
[ValueLens repo](https://github.com/microsoft/ValueLens-for-Microsoft-Copilot) has working examples
of exactly that pattern under `2. Fabric/flows/` that you can adapt.

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

## Table contracts

The template expects these tables. If you build your own pipeline, match this and the template works
unchanged.

**`viva_credits_weekly`** — one row per person × service × policy × week
`person_id`, `user_principal_name`, `entra_id`, `service_id`, `service_name`, `spending_policy_id`,
`metric_date`, `session_count`, `spending_policy_limit`, `credits_used`, `user_limit`

**`viva_spending_policy`**
`spending_policy_id`, `name`, `plan_limit`, `user_limit`, `included_services`

**`studio_tenant_daily`**
`billing_plan_id`, `billing_plan_name`, `environment_id`, `environment_name`, `capacity_type`,
`entitled_quantity`, `prepaid_consumed`, `payg_consumed`, `usage_date`

**`studio_agent`**
`agent_name`, `agent_id`, `product`, `billable_feature`, `billed_credit`, `non_billed_credit`,
`channel`, `knowledge_sources`, `tool_used`, `llm_model`, `scenario_name`, `environment_id`,
`environment_name`

**`studio_user`**
`user_id`, `user_email`, `agent_id`, `agent_name`, `billable_credit_used`, `credits_used`,
`m365_copilot_licensed`

**`github_ai_usage`**
`usage_date`, `username`, `product`, `sku`, `model`, `quantity`, `unit_type`,
`applied_cost_per_quantity`, `gross_amount`, `discount_amount`, `net_amount`, `total_monthly_quota`,
`organization`, `repository`, `cost_center_name`

**`github_user_map`**
`username`, `user_principal_name`, `display_name`, `plan`, `included_credits`

**`org_attributes`**
`user_principal_name`, `display_name`, `department`, `job_title`, `job_family`, `city`, `country`,
`cost_center`, `manager`, `business_unit`

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
