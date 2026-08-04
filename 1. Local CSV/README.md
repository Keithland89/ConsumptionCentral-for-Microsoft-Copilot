# 1. Local CSV deployment

The simplest path. Download the exports, unzip them into one folder, point the template at it.

**About ten minutes.** Power BI Pro is enough — no Fabric, no Premium, no gateway.

Use this to find out whether the numbers are worth automating. Move to
**[2. Fabric](../2.%20Fabric/)** when you want them refreshed without anyone remembering to download
anything.

---

## Before you start

You need at least the **Cowork export**. Everything else is optional — the pages for a product you
have no data for simply come up empty, and the rest still works.

| | Role needed | Takes |
|---|---|---|
| Cowork / Work IQ credits | Global Admin *or* Viva Insights Analyst | 2 min |
| Copilot Studio credits | Power Platform Admin | 2 min |
| GitHub Copilot AI usage | Enterprise owner or billing manager | 2 min + email wait |
| Entra org attributes | Any user | 3 min |

Full click-paths, roles and caveats: **[docs/DATA-SOURCES.md](../docs/DATA-SOURCES.md)**.

---

## Step 1 — Make a data folder

Anywhere you like. A OneDrive- or SharePoint-synced folder is a good choice — the template reads a
normal file path, so a synced folder gives you a shared location without any extra plumbing.

```
C:\CreditLens\Data\
```

## Step 2 — Get the exports

### Cowork / Work IQ — required

1. Go to <https://analysis.insights.viva.office.com>
2. Open the **Consumption Dashboard**
3. Export, choosing **by week** (6 months of history, versus 28 days for daily)
4. Unzip into your data folder

You get `PersonServiceCreditsMetrics.csv` and `SpendingPolicyMetadata.csv`, and — if your tenant
exports de-identified — also `PeopleMetaData.csv` and `PersonPolicyMap.csv`.

**Both variants work.** CreditLens detects which one you have and adapts. See
[Identified vs de-identified](../docs/DATA-SOURCES.md#identified-vs-de-identified) for what changes.

### Copilot Studio — optional

Power Platform admin center → **Licensing** → **Copilot Studio**. Export the tenant, per-agent and
per-user views into the same folder as `StudioTenantDaily.csv`, `StudioPerAgent.csv` and
`StudioPerUser.csv`.

> The export button is not documented by Microsoft — look for **Download** or **Export** on each tab.
> If there isn't one, skip it; the Studio pages stay empty and nothing else is affected.

### GitHub Copilot — optional

1. GitHub → your enterprise → **Billing &amp; Licensing** → Usage → **AI usage**
2. **Get usage report**, pick a range of up to **31 days**, **Email me the report**
3. Save the CSV as `GitHubAiUsage.csv`

You also need a seat list as `GitHubUserMap.csv`, with columns:

```
username,userPrincipalName,displayName,plan,included_credits
```

`plan` must be `Copilot Business` or `Copilot Enterprise` — the seat-cost measure keys on it.
`userPrincipalName` is what links a GitHub account to the Entra org file, so department breakdowns
depend on it being right.

### Entra org attributes — optional but recommended

Entra admin center → **Users** → **All users** → **Download users**. Save as `entra_org.csv`.

Without it, everything works but you lose department, cost-centre and business-unit breakdowns —
which is most of the chargeback story. `manager`, `costCenter`, `jobFamily` and `businessUnit` need
Graph rather than the classic download; see
[the Entra section](../docs/DATA-SOURCES.md#4-org-attributes--microsoft-entra-optional) for a
ready-to-run PowerShell snippet.

## Step 3 — Open the template

Double-click **`CreditLens - Local CSV.pbit`**. Power BI Desktop prompts for parameters before it
loads anything.

**Paths** — point each at your file. Only the first is required.

| Parameter | Your file |
|---|---|
| `VivaMetricsCsvPath` | `PersonServiceCreditsMetrics.csv` |
| `VivaPolicyCsvPath` | `SpendingPolicyMetadata.csv` |
| `PersonMapCsvPath` | `PersonPolicyMap.csv` — de-identified exports only |
| `VivaPeopleCsvPath` | `PeopleMetaData.csv` — de-identified exports only |
| `EntraCsvPath` | `entra_org.csv` |
| `StudioTenantCsvPath` | `StudioTenantDaily.csv` |
| `StudioAgentCsvPath` | `StudioPerAgent.csv` |
| `StudioUserCsvPath` | `StudioPerUser.csv` |
| `GitHubUsageCsvPath` | `GitHubAiUsage.csv` |
| `GitHubUserMapCsvPath` | `GitHubUserMap.csv` |

> **On the two de-identified-only paths.** Leave them pointing at a file that doesn't exist and the
> template still loads — it falls back to deriving the roster from the metrics file. See
> [the limitation](#the-derived-roster-limitation) below.

**Commercial terms** — the exports carry consumption, not pricing. Until you set these, the cost
pages are arithmetic on a guess. See the
[table in the root README](../README.md#-commercial-terms-you-must-set).

Click **Load**. First refresh takes a minute or two.

## Step 4 — Set the billing period

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

**"We couldn't find the file"** — a path is wrong, or points at a folder rather than a file. Each
parameter wants a full path including the filename.

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

## What's in this folder

```
CreditLens - Local CSV.pbit    the template
sample-data/                   a small synthetic dataset, if you want to see it working first
README.md                      this file
```
