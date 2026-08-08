# 1. Local CSV

**The quickest way to see it working.** Download your exports, put them in a folder, open the
template.

Works with Power BI Pro — no Fabric capacity needed.

---

## You only need one product

Cowork, Copilot Studio, GitHub Copilot, Azure AI Foundry — **bring whichever you have**. Missing
products just leave their pages empty.

---

## Three steps

### 1. Make a folder

Anywhere. `C:\Consumption Central\Data` is fine.

### 2. Put your exports in it

| Product | Where to get it |
|---|---|
| **Cowork / Work IQ** | Viva Insights → Analysis → build a query → download CSV |
| **Copilot Studio** | Power Platform admin centre → Licensing → Copilot Studio |
| **GitHub Copilot** | GitHub → Billing → AI usage report |
| **Azure AI Foundry** | Azure Cost Analysis → export, or the script in this repo |

File names don't have to match exactly — the template recognises the usual variations.

**[Full click-paths and permissions →](../docs/DATA-SOURCES.md)**

### 3. Open the template

Open **`Consumption Central - Local CSV.pbit`**, paste your folder path into `DataFolder`, click
**Load**.

That's it.

---

## Try it with sample data first

The **[sample-data](sample-data/)** folder holds a synthetic dataset covering all four products.
Point `DataFolder` at it and the whole report fills in — no exports needed, no real data involved.

Worth doing before you go hunting for your own files.

---

## What you'll be asked for

| | |
|---|---|
| **`DataFolder`** | Your folder path — the only one that matters |
| Everything else | Has a sensible default. Leave it |

<details>
<summary>The optional ones, if your pricing differs</summary>

| | Default | Change it when |
|---|---|---|
| `CreditRate` | $0.01 | Your agreement isn't list price |
| `PrepaidCreditRate` | $0.008 | You bought credits up front |
| `PrepaidCreditBalance` | 0 | You have a prepaid balance |
| `GitHubBusinessSeatPrice` | $19 | Your GitHub pricing differs |
| `GitHubEnterpriseSeatPrice` | $39 | As above |
| `BillingPeriodWeeks` | 4 | Your billing period isn't monthly |

**[Where to find your real rates →](../docs/COMMERCIAL-TERMS.md)**

</details>

---

## Department breakdowns

If your Viva query includes department or job title, they appear automatically.

If it doesn't, add them to the query in Viva Insights and re-run — that's easier than supplying a
separate file.

**[More on org data →](../docs/ORG-DATA.md)**

---

## When you outgrow this

Local CSV means someone downloads files each month. When that stops being fun,
**[2. Fabric](../2.%20Fabric/)** does the same thing on a schedule and keeps history beyond the
6-month export window.
