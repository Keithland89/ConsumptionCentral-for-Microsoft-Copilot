# 2. Fabric

**Set it up once, then it refreshes itself.** Data lands in a Lakehouse; the report reads it on a
schedule.

Needs Fabric capacity, Premium, or PPU. Only have Power BI Pro?
Use **[1. Local CSV](../1.%20Local%20CSV/)**.

---

## Why bother

The Viva Insights export only reaches back **6 months**. Every week you don't capture is gone.

This path accumulates history in a table that outlives the export window — a year from now you have
a year of trend, not the same rolling six months.

---

## You only need one product

Load Cowork alone and its pages work. Studio only, or GitHub only — same. **Skip the notebooks for
products you don't have.**

---

## Setup

### 1. Create a Lakehouse

Fabric portal → your workspace → **New** → **Lakehouse**.

### 2. Import the notebooks

**[notebooks/](notebooks/)** — one per product. Import the ones you need, set the workspace and
Lakehouse at the top of each, run.

| Notebook | Reads | Writes |
|---|---|---|
| `Ingest_Viva_Consumption` | Viva Insights export | `viva_credits_weekly`, `viva_spending_policy` |
| `Ingest_Studio` | Power Platform exports | `studio_*` |
| `Ingest_GitHub_API` | GitHub REST API | `github_*` |
| `Ingest_Org` | Entra export | `org_attributes` |
| `Ingest_CommercialTerms` | Azure Cost Management | `commercial_terms` |

**[Where each export comes from →](../docs/DATA-SOURCES.md)**

### 3. Get the SQL connection string

Lakehouse → **Settings** → **SQL analytics endpoint** → copy it.

### 4. Open the template

Open **`Consumption Central - Fabric.pbit`** and paste in:

| | |
|---|---|
| **`FabricSQLEndpoint`** | The string you just copied |
| **`LakehouseName`** | Your Lakehouse name |

Everything else has a default.

### 5. Publish and schedule

Publish to your workspace, then set a refresh schedule. **Tuesday morning** works well — after
Viva's weekend refresh.

---

## Try it with sample data first

**[seed_sample_data.py](seed_sample_data.py)** loads the synthetic dataset straight into your
Lakehouse — no exports, no waiting.

```
pip install pandas deltalake requests
az login --tenant <your-tenant>
python seed_sample_data.py --workspace <guid> --lakehouse <guid>
```

Both GUIDs are in the Fabric portal URL with the Lakehouse open. It only touches the Consumption
Central tables.

---

## The Viva half can run itself

Viva Insights ships a **Dataflow Gen2** connector that writes query results straight into a
Lakehouse on a schedule — no download, no notebook.

Set the query to auto-refresh in Viva, schedule the Dataflow for Tuesday morning, and that half of
the pipeline looks after itself.

**[Microsoft's guide →](https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/export-query-data-microsoft-fabric)**

---

## Reference

| | |
|---|---|
| [Table contracts](docs/DATA-DICTIONARY.md) | Every table and column the model expects |
| [Automating the landing step](flows/) | Power Automate, if you'd rather not use notebooks |
