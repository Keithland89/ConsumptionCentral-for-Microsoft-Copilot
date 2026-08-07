# 1. Local CSV deployment

The simplest path. Download the exports, unzip them into one folder, point the template at it.

**About ten minutes.** Power BI Pro is enough — no Fabric, no Premium, no gateway.

Use this to find out whether the numbers are worth automating. Move to
**[2. Fabric](../2.%20Fabric/)** when you want them refreshed without anyone remembering to download
anything.

---

## Before you start

**Bring whichever products you have. One is enough.**

Consumption Central covers three: Cowork/Work IQ, Copilot Studio and GitHub Copilot. **None of them is
required.** Load one and its four pages work; the other ten come up empty and nothing breaks. Load
all three and you get the combined view.

| I have… | I get |
|---|---|
| Cowork only | Cowork consumption, cost, optimisation, forecast |
| Studio only | The same four, for Studio |
| GitHub only | The same four, for GitHub |
| Any two, or all three | Those, plus the combined overview |

*Verified by loading each combination and checking every product's figures are unchanged by the
others' absence.*

**Org attributes are optional too.** Without them, Group By falls back to usage intensity — every
credit and cost figure is still correct, you just cannot break it down by department.

| Export | Role needed | Takes |
|---|---|---|
| Cowork / Work IQ credits | Global Admin *or* Viva Insights Analyst | 2 min |
| Copilot Studio credits | Power Platform Admin | 2 min |
| GitHub Copilot AI usage | Enterprise owner or billing manager | 2 min + email wait |
| Org attributes | Any user | 3 min |

Full click-paths, roles and caveats: **[docs/DATA-SOURCES.md](../docs/DATA-SOURCES.md)**.

---

## Step 1 — Make a data folder

Anywhere you like. A OneDrive- or SharePoint-synced folder is a good choice — the template reads a
normal file path, so a synced folder gives you a shared location without any extra plumbing.

```
C:\CreditLens\Data\
```

## Step 2 — Get whichever exports you have

**Skip any product you don't use.** Each section stands alone.

### Cowork / Work IQ

**Best route — a custom query.** It auto-refreshes, and it can carry org attributes so you may not
need a separate directory export at all.

1. <https://analysis.insights.cloud.microsoft> → **Analysis** → create an analysis
2. Choose the **Copilot credit** metrics, add any org attributes you want, turn on **Auto-refresh**
3. **Analysis results** → your query → download as CSV
4. Unzip into your data folder

**Or the Consumption Dashboard export**, if you'd rather not build a query: open the
**Consumption Dashboard**, export **by week** (6 months of history, versus 28 days for daily), unzip
into the same folder.

Both work, and both are found by name — nothing needs renaming. Identified and de-identified exports
both work too; the template detects which you have. See
[Identified vs de-identified](../docs/DATA-SOURCES.md#identified-vs-de-identified).

### Copilot Studio

Power Platform admin center → **Licensing** → **Copilot Studio**. Export the tenant, per-agent and
per-user views into the same folder as `StudioTenantDaily.csv`, `StudioPerAgent.csv` and
`StudioPerUser.csv`.

> The export button is not documented by Microsoft — look for **Download** or **Export** on each tab.
> If there isn't one, skip it. The Studio pages stay empty and nothing else is affected.

### GitHub Copilot

1. GitHub → your enterprise → **Billing &amp; Licensing** → Usage → **AI usage**
2. **Get usage report**, pick a range of up to **31 days**, **Email me the report**
3. Save the CSV as `GitHubAiUsage.csv`

You also need a seat list as `GitHubUserMap.csv`:

```
username,userPrincipalName,displayName,plan,included_credits
```

`plan` must read `Copilot Business` or `Copilot Enterprise` — the seat-cost measure keys on it.
`userPrincipalName` is what links a GitHub account to your directory, so department breakdowns depend
on it.

### Org attributes

**You may already have these.** If your Viva custom query includes department or similar, Consumption Central
uses them and you can skip this entirely.

Otherwise: Entra admin center → **Users** → **All users** → **Download users**, saved as
`entra_org.csv`. For `manager`, `costCenter`, `jobFamily` and `businessUnit` you need Graph rather
than the classic download — **[docs/ORG-DATA.md](../docs/ORG-DATA.md)** has ready-to-run scripts and
how to schedule them.

Without any org data, Group By falls back to usage intensity. Every credit and cost figure is still
correct.

## Step 3 — Open the template

Double-click **`Consumption Central - Local CSV.pbit`**. Power BI prompts for parameters before loading
anything.

**Only the first one matters to get started. Leave the rest alone.**

| Parameter | What to put |
|---|---|
| **`DataFolder`** | The folder from step 1. That's it. |

<details>
<summary>The other six — commercial terms, all with sensible defaults</summary>

| Parameter | Default | Change it when |
|---|---|---|
| `CreditRate` | `0.01` | your agreement prices credits differently |
| `PrepaidCreditRate` | `0.008` | you hold prepaid capacity |
| `PrepaidCreditBalance` | `0` | you hold prepaid capacity |
| `GitHubBusinessSeatPrice` | `19` | your GitHub seats are discounted |
| `GitHubEnterpriseSeatPrice` | `39` | your GitHub seats are discounted |
| `BillingPeriodWeeks` | `4` | your billing month isn't four weeks |

Every one has an ⓘ tooltip in the prompt explaining where to find the real value.
Full detail: **[docs/COMMERCIAL-TERMS.md](../docs/COMMERCIAL-TERMS.md)**.

</details>

**You do not point at individual files.** The template searches the folder — subfolders included —
and matches each export by name, so `PersonServiceCreditsMetrics.csv`,
`Person Service Credits Metrics.csv` and `person_service_credits_metrics.csv` all work equally well.

Where two copies of the same export exist, the one nearest the top of your folder wins, and among
equals the most recent — so re-exporting over the top does the right thing, and an old copy in a
subfolder cannot silently take over.

Click **Load**. First refresh takes a minute or two.

## Step 4 — Check the numbers mean something

The exports carry **consumption, not pricing**. Until you have set the rates, the cost pages are
arithmetic on a list price. The **Rates in use** card on the Cost page shows what the report is
currently assuming — worth a glance before anyone acts on a number.

`BillingPeriodWeeks` (default **4**) defines what "current period" means on the Cowork pages. If your
billing month is a calendar month rather than four weeks, this is approximate — the Viva export is
weekly, so whole weeks are all it can offer.

---

## Refreshing

Re-export, overwrite the files in the folder, hit **Refresh** in Power BI Desktop.

The Cowork export gives 6 months of weekly history each time, so you keep a rolling 6-month window.
**History older than that is lost** — the export cannot reach further back, and neither can this
path. If you want to accumulate history indefinitely, that is exactly what
**[2. Fabric](../2.%20Fabric/)** is for.

---

## The derived roster limitation

When `PersonPolicyMap.csv` and `PeopleMetaData.csv` are absent — normal for an identified export —
the seat roster is derived from the metrics file instead.

**That roster can only see people who consumed something.** A seat holder with zero usage in the
window has no row in the metrics file, so they are not counted. Seat counts and allowance totals
become **usage-based rather than entitlement-based**.

In practice this means:

- "Seats with no credit use" will under-report — it can only see people who used *some* credits
- Total allowance is the sum over consuming users, not over everyone entitled

If you need the full entitled roster, take a de-identified export as well and point
`PersonMapCsvPath` and `VivaPeopleCsvPath` at its files. The model will use them in preference.

---

## Troubleshooting

**"We couldn't find the folder"** — `DataFolder` is wrong, or points at a file rather than a folder.
It wants the folder your exports are in, not one of the files.

**A file is there but its page is still empty** — the name may not be recognised. The matcher strips
spaces, dashes and underscores and looks for a fragment: `personservicecredits`, `spendingpolicy`,
`personpolicymap`, `peoplemetadata`, `entra` / `orgdata` / `users`, `studiotenantdaily`,
`studioperagent`, `studioperuser`, `githubaiusage`, `githubusermap`. Rename the file to contain the
relevant fragment and refresh.

**Cowork pages are empty** — check `PersonServiceCreditsMetrics.csv` opens and has more than a header
row. If your export is daily rather than weekly you will get very few weeks; re-export by week.

**Department breakdowns show blank or "(Unassigned)"** — the org file's `userPrincipalName` values
don't match the consumption export's. Compare a few rows by eye. Casing and domain suffix must match.

**GitHub pages empty but the file is there** — check `plan` reads exactly `Copilot Business` or
`Copilot Enterprise`.

**Everything loads but costs are zero** — the rate parameters are still at their defaults and your
pack balance is 0. Set the commercial terms.

**Formula.Firewall error** — File → Options → Current file → Privacy → *Always combine data according
to your Privacy Level settings*, and set each source to **Organizational**. Do not use *Ignore the
Privacy Levels*: it works in Desktop and then fails on scheduled refresh in the Service.

---

## Two Viva export routes

**A custom query is the better one.** In Viva Insights - Analysis - create an analysis, choose the
Copilot credit metrics, and set it to auto-refresh. It gives you:

- **auto-refresh**, so the export keeps itself current
- **real UPNs and EntraId**, even with identification enabled
- **org attributes of your choosing**, carried alongside the credits - which means no separate
  directory export is needed at all

The Consumption Dashboard export still works and needs no change. Its files are named differently
and both sets of names are recognised, so nothing has to be renamed either way:

| | Custom query | Consumption Dashboard |
|---|---|---|
| Metrics | PersonM365CreditsMetrics.csv | PersonServiceCreditsMetrics.csv |
| Policies | M365SpendingPolicyMetaData.csv | SpendingPolicyMetadata.csv |
| People | PeopleMetaData.csv | PeopleMetaData.csv |

Unzip whichever you have into your data folder. See
[docs/ORG-DATA.md](../docs/ORG-DATA.md#where-org-data-comes-from) for how org attributes are picked up.

---

## What's in this folder

```
Consumption Central - Local CSV.pbit    the template
sample-data/                   a small synthetic dataset, if you want to see it working first
README.md                      this file
```
