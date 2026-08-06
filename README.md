<div align="center">

# 💳 CreditLens

### *for Microsoft Copilot* — one Power BI template for **Copilot credit consumption and cost** across Cowork/Work IQ, Copilot Studio and GitHub Copilot.

[![Built by Microsoft](https://img.shields.io/badge/BUILT_BY-MICROSOFT-4F73B8?style=for-the-badge&labelColor=1C2632)](https://github.com/microsoft/CreditLens-for-Microsoft-Copilot)
[![Power BI Template](https://img.shields.io/badge/POWER_BI-TEMPLATE-F2C811?style=for-the-badge&logo=powerbi&logoColor=1C2632&labelColor=1C2632)](#-pick-a-deployment-path)
[![Deploy](https://img.shields.io/badge/DEPLOY-CSV_%2B_FABRIC_%2B_VIVA_DIRECT-09B39D?style=for-the-badge&labelColor=1C2632)](#-pick-a-deployment-path)

**Credits consumed · what they cost · where to trim · what next year looks like**

**[Deployment paths ↓](#-pick-a-deployment-path)** · **[What it measures ↓](#-what-it-measures)** · **[Data sources ↓](#-data-sources)** · **[Pages ↓](#-dashboard-pages)**

![CreditLens — all fourteen pages](Images/CreditLens-Preview.gif)

<sub>All fourteen pages, shown with the synthetic sample dataset.</sub>

</div>

<details>
<summary>⚠️ <strong>Usage &amp; compliance disclaimer</strong></summary>

This template helps you understand your own Copilot credit consumption and cost. Microsoft has
**no visibility** into the data you load, nor control over how the template is used. You are solely
responsible for ensuring your use complies with all applicable laws and regulations, including data
privacy and employment law. **Microsoft disclaims all liability** arising from use of this template.

Several of the underlying exports are **in preview** at the time of writing, and the identifiable
(named-user) variant of the Viva Insights consumption export processes personal data. Review the
"Previews" section of the Microsoft Products and Services Data Protection Addendum before enabling
it, and consult your works council or privacy office where per-person reporting requires it.

Not supported through Microsoft support channels — please open an issue in this repo.

</details>

---

## 🚀 Pick a deployment path

The dashboard ships as **three folders**. They produce the same 14 pages and the same measures — they
differ only in *how the data gets in and how it refreshes*.

| Path | Pick this when… | What you need |
|---|---|---|
| **[1. Local CSV](1.%20Local%20CSV/)** · *simplest* | You want to see it working today, or you report monthly by hand. | Download the exports, unzip, point five parameters at the folder. Power BI Pro only. |
| **[2. Fabric](2.%20Fabric/)** · *recommended* | You want scheduled refresh and history that outlives the export window. | Fabric capacity (or Premium/PPU). Notebooks land the exports in a Lakehouse; the template reads the SQL analytics endpoint. |
| **[3. Viva Direct](3.%20Viva%20Direct/)** · *experimental* | You want Cowork data with no file handling at all. | The certified Viva Insights connector. **Read the folder README first — this path is not yet confirmed to carry credit data.** |

**Not sure?** Start with **Local CSV**. It takes about ten minutes and tells you whether the numbers
are worth automating. Move to **Fabric** once you want them weekly without anyone remembering to
download anything.

> Each path folder has its own README with the exact steps. This page is the map.

---

## 📊 What it measures

Three products, one narrative each: **Consumption → Cost → Optimization → Forecast**, plus a combined
view and a glossary.

| | Cowork / Work IQ | Copilot Studio | GitHub Copilot |
|---|---|---|---|
| **Billing model** | Credits, prepaid packs or pay-as-you-go | Credits, prepaid or pay-as-you-go | Seats + pooled AI credits |
| **Export grain** | Person × week | Tenant × day; agent and user totals | Person × day |
| **What drives cost** | Credits over the spending-policy limit | Credits over prepaid capacity | Seats, plus credits over the pooled allowance |

Because the three exports arrive at different grains and cover different windows, the combined page
normalises everything to a **monthly run rate** rather than adding raw totals together. The page says
so on its face.

---

## 🔌 Data sources

Each path README carries the full click-path, the role required, and the gotchas. In summary:

| Source | Where it comes from | Grain | History | Automatable? |
|---|---|---|---|---|
| **Cowork / Work IQ credits** | Viva Insights web app → Consumption Dashboard → export | Person × week | 6 months (weekly) / 28 days (daily) | ⚠️ Connector, not REST |
| **Spending policies** | Same export | Policy | Current | ❌ |
| **Copilot Studio** | Power Platform admin center → Licensing → Copilot Studio | Tenant × day; agent and user totals | ~3 months | ❌ CSV only |
| **GitHub Copilot** | GitHub REST API, *or* Billing &amp; Licensing → AI usage report | Person × day | **24 months via API**; 31 days per web report | ✅ **Yes** |
| **Org attributes** *(optional)* | Microsoft Entra admin center → Users → Download users | Person | Current | ⚠️ Graph PowerShell |

**Only GitHub can be pulled on a schedule.** It has dedicated AI-credit API endpoints carrying two
years of history. The other three are download-only — which is the main reason the
[Fabric path](2.%20Fabric/) exists: it accumulates history that the exports themselves cannot reach
back to.

**The org file is optional but worth it.** Without it every page still works, but you lose the
department, cost-centre and business-unit breakdowns — which is most of the chargeback story.

See **[docs/DATA-SOURCES.md](docs/DATA-SOURCES.md)** for the full schema of every file, including
which columns are required and what happens when one is missing.

---

## 📚 Dashboard pages

| # | Page | Answers |
|---|---|---|
| 0 | Overall: Combined | What are all three products costing us a month? |
| 1 | Cowork: Consumption | Who is using credits, and how much? |
| 2 | Cowork: Cost | What does it cost — prepaid, pay-as-you-go, blended? |
| 3 | Cowork: Optimization | Where is money being left on the table? |
| 4 | Cowork: Forecast | What do the next twelve months look like? |
| 5 | Studio: Consumption | Which agents and people consume credits? |
| 6 | Studio: Cost | Prepaid vs pay-as-you-go, by environment |
| 7 | Studio: Optimization | Which agents are worth attention? |
| 8 | Studio: Forecast | Twelve months at the current run rate |
| 9 | GHCP: Consumption | Which developers, which models? |
| 10 | GHCP: Cost | Seats vs credits beyond the allowance |
| 11 | GHCP: Optimization | Unused seats, model-tier mix |
| 12 | GHCP: Forecast | Twelve months, including the allowance step-down |
| 13 | Glossary | What every term and measure means |

Every headline, card and summary is **computed from your data**. Nothing is hardcoded — the report
reads its own numbers, its own date ranges and its own history length, so it tells the truth about
whatever you load into it.

---

## ⚙️ Commercial terms you must set

The exports carry **consumption, not pricing**. Before the cost pages mean anything, set these under
**Transform data → Manage parameters**:

There are **seven**, and only the first is required.

| # | Parameter | Default | What it is |
|---|---|---|---|
| 1 | `DataFolder` | — | **The one thing you must set.** A folder holding whatever exports you have. Files are found by name, subfolders included, so nothing needs renaming and anything absent is skipped. |
| 2 | `CreditRate` | 0.01 | Pay-as-you-go cost per credit. Microsoft and GitHub both publish $0.01, so one number covers all three products. |
| 3 | `PrepaidCreditRate` | 0.008 | Cost per credit drawn from prepaid capacity. Only matters if you hold some. |
| 4 | `PrepaidCreditBalance` | 0 | Prepaid Cowork credits this period, from M365 admin center → Copilot → Cost management. |
| 5 | `GitHubBusinessSeatPrice` | 19 | List price. Change if discounted — seats are usually the larger half of the GitHub bill. |
| 6 | `GitHubEnterpriseSeatPrice` | 39 | List price. |
| 7 | `BillingPeriodWeeks` | 4 | Trailing weeks that make one billing period. |

**If your agreement prices products differently**, leave `CreditRate` alone and edit the per-product
columns in the **Settings** query — it keeps a separate column for Cowork, Studio and GitHub, so a
one-line change there beats three parameters nobody understood.

**GitHub's allowance change** also lives in the Settings query rather than a parameter, because it is
a GitHub product fact rather than a customer term: the allowance falls from 3,000/7,000 to
1,900/3,900 on 1 September 2026, and the forecast page models that step-down. If no change is pending
for you, set the date to one already past and the two values to your current entitlement — the report
detects that nothing is changing and says so instead of forecasting a cliff.

> **The template prompt opens with every box empty.** Power BI clears parameter values on template
> export and there is no supported way around it. Every default is written into the parameter's own
> description, so hovering the **ⓘ** beside each box tells you what to type.
>
> **[docs/COMMERCIAL-TERMS.md](docs/COMMERCIAL-TERMS.md)** covers where each figure comes from, and
> which of them can be looked up automatically — the credit list rate is available from a public
> Azure API, and your actual negotiated rate from Azure Cost Management.

---

## 🗂 What's in this repo

```
1. Local CSV/        the simplest path — CSVs on disk or a synced folder
2. Fabric/           notebooks + Lakehouse + scheduled refresh
3. Viva Direct/      the certified Viva Insights connector (experimental)
docs/                data sources, measures, build steps, testing
Images/              screenshots
```

## ✅ Status

This is a **first scaffold**. Before it goes public:

| | |
|---|---|
| Model — 27 tables, 284 measures, 14 pages | ✅ Built and validated |
| Both Viva export shapes (identified / de-identified) | ✅ Tested against real files |
| Commercial terms parameterised | ✅ Verified by flexing rates |
| No hardcoded figures in any card or headline | ✅ Audited |
| Documentation, cited | ✅ |
| `.pbit` files | ⏳ [docs/BUILD.md](docs/BUILD.md) |
| Viva connector path | ❓ [test procedure](3.%20Viva%20Direct/TEST-PROCEDURE.md) |
| GitHub API ingester | ⏳ Written, needs a live enterprise to confirm |

**→ [docs/TESTING.md](docs/TESTING.md)** has the steps for everything still open.

---

## 🤝 Contributing

Issues and pull requests are welcome. This project follows the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

Most contributions require you to agree to a Contributor License Agreement (CLA). Visit
<https://cla.opensource.microsoft.com> for details.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorised use of
Microsoft trademarks or logos is subject to and must follow
[Microsoft's Trademark &amp; Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of third-party trademarks or logos is subject to those third parties' policies.
