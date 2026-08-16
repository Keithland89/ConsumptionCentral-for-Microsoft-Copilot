# 3. Viva Direct

**No files at all.** Connect straight to Viva Insights and let it refresh itself.

---

## Two things to paste

In Viva Insights:

1. **Analysis** → build a query with the Copilot credit metrics → turn on **Auto-refresh**
2. **Analysis results** → your query → the **link icon**
3. Copy the two identifiers

Open **`Consumption Central - Viva Direct.pbit`**, paste them in, click **Load**.

| | |
|---|---|
| **`VivaPartitionId`** | Partition identifier |
| **`VivaQueryId`** | Query identifier |

**Leave everything else blank.** The prompt lists more boxes than you need — the rest are for
Copilot Studio, GitHub and Azure AI, which are optional.

---

## Either Viva source works

The connector reads **two different shapes**, and one parameter tells them apart:

| Your source | `VivaExportName` |
|---|---|
| **Custom query** — you built it in Analysis | **leave blank** |
| **Consumption Dashboard export** | **set it** to the export name |

A custom query returns a single table, so no table name is sent. A Consumption Dashboard export is
multi-table and named, so the name has to go with the request — omit it and the service returns a
bare `500` rather than saying a name was needed.

This can't be detected automatically: `VivaInsights.Data` hands back a *lazy* table, so probing it
reports success whether or not the table can actually be read.

**[Full connector reference →](../docs/VIVA-CONNECTOR.md)**

---

## Department breakdowns

**Add them to your Viva query.** Under *"Select spending policy and employee attributes"*, tick
Department, Job title, Manager — whatever you want to slice by. They flow through automatically.

That's easier and more reliable than supplying a separate file, because the attributes always match
the people in the data.

<details>
<summary>If you can't change the query</summary>

Drop a directory export from the Microsoft Entra admin centre (Users → Download users) into your
`DataFolder`. It's a fallback: Viva's own attributes are always used first when present.

**[More on org data →](../docs/ORG-DATA.md)**

</details>

---

## Adding the other products

Optional. Set **`DataFolder`** to a folder holding whatever exports you have and drop the files in —
they're found by name, so nothing needs renaming and anything you don't have is skipped.

| Product | Files it looks for |
|---|---|
| Copilot Studio | `StudioTenantDaily`, `StudioPerAgent`, `StudioPerUser` |
| GitHub Copilot | `GitHubAiUsage`, `GitHubUserMap` |
| Azure AI Foundry | `AzureAiSpendDaily`, `AzureAiTokensDaily` |
| Org attributes | `entra` / `orgdata` / `users` — only if you can't add them to the Viva query |

Leave `DataFolder` alone if all you have is Cowork. The connector covers it and those pages simply
stay empty, which is a supported state.

> Foundry exports often land somewhere else entirely, so `AzureAiSpendCsvPath` and
> `AzureAiTokensCsvPath` remain as an explicit escape hatch — set either one and it wins over the
> folder.

**[Where to get each one →](../docs/DATA-SOURCES.md)**

---

## If the refresh fails

**`(500) Internal Server Error`** almost always means `VivaExportName` is set when it shouldn't be.
A custom query needs it **blank**.

Set it only if you're using a Consumption Dashboard export instead of a custom query.

**[Connector detail and what was tested →](../docs/VIVA-CONNECTOR.md)**

---

## Worth knowing

Microsoft ships its own Power BI template from the same dialog. It covers Cowork consumption with
first-party support.

This is a different proposition: four products in one report, with cost, optimisation and forecast
across all of them. Download both and see which you'd rather have.
