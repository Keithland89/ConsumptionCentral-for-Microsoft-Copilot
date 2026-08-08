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

## Department breakdowns

**Add them to your Viva query.** Under *"Select spending policy and employee attributes"*, tick
Department, Job title, Manager — whatever you want to slice by. They flow through automatically.

That's easier and more reliable than supplying a separate file, because the attributes always match
the people in the data.

<details>
<summary>If you can't change the query</summary>

Set `EntraCsvPath` to a directory export from the Microsoft Entra admin centre
(Users → Download users). It's a fallback: Viva's own attributes are always used first when present.

**[More on org data →](../docs/ORG-DATA.md)**

</details>

---

## Adding the other products

Optional. Fill in the matching paths if you have them:

| Product | Parameter |
|---|---|
| Copilot Studio | `StudioTenantCsvPath`, `StudioAgentCsvPath`, `StudioUserCsvPath` |
| GitHub Copilot | `GitHubUsageCsvPath`, `GitHubUserMapCsvPath` |
| Azure AI Foundry | `AzureAiSpendCsvPath`, `AzureAiTokensCsvPath` |

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
