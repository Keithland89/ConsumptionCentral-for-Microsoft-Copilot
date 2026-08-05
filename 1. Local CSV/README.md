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

Double-click **`CreditLens - Local CSV.pbit`** *(see the note at the foot of this page — it needs
building first)*. Power BI Desktop prompts for parameters before it
loads anything. **There are seven, and only the first matters to get started.**

| Parameter | What to put |
|---|---|
| **`DataFolder`** | The folder from step 1. That's it — the files are found by name. |
| `CreditRate` | Leave at `0.01` unless your agreement differs |
| `PrepaidCreditRate` | Leave at `0.008` unless you hold prepaid capacity |
| `PrepaidCreditBalance` | Your prepaid Cowork credits, or `0` |
| `GitHubBusinessSeatPrice` | `19`, or your discounted price |
| `GitHubEnterpriseSeatPrice` | `39`, or your discounted price |
| `BillingPeriodWeeks` | `4` unless your billing month differs |

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

## What's in this folder

```
CreditLens - Local CSV.pbit    the template — NOT YET BUILT, see ../docs/BUILD.md
sample-data/                   a small synthetic dataset, if you want to see it working first
README.md                      this file
```

> **On the missing `.pbit`.** Power BI Desktop has no command-line template export, so producing it
> is a short manual step that has not been done yet. [docs/BUILD.md](../docs/BUILD.md) has the
> procedure. Until then, open the PBIP project directly — everything else on this page applies
> unchanged.
