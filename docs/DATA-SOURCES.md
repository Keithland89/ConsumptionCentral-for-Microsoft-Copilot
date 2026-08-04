# Data sources

Everything CreditLens reads, where it comes from, and what it looks like.

Each section gives the click-path, the role required, the file it produces and its columns. Where
Microsoft or GitHub has published a schema, it is cited. Where they have not, the columns are the
ones observed in a real export and are marked as such — check yours matches before you trust it.

**Verification status is marked throughout.** A plausible-but-wrong click path wastes more of your
time than an honest "check the portal", so anything unconfirmed says so.

---

## 1. Cowork / Work IQ credits — Viva Insights Consumption Dashboard

The main source. Person × week credit consumption for the usage-based-billing Copilot services.

### Where

| | |
|---|---|
| **Portal** | <https://analysis.insights.viva.office.com> |
| **Path** | Viva Insights web app → **Consumption Dashboard** → export |
| **Role** | Global Administrator, **or** Viva Insights Analyst with global partition access |
| **Licence** | 50+ assigned Viva Insights licences, or 1+ Copilot licence including the Viva Insights service plan |

> ⚠️ **Partially verified.** The Consumption Dashboard is confirmed as a named component of the Viva
> Insights web app ([manage-settings-copilot-dashboard][s1a], updated 2026-08-03), but Microsoft has
> not yet published a dedicated page for *its* export. The exact left-nav label and export button
> wording should be confirmed in your own portal. The closely-related Copilot Dashboard export is
> documented at [export-copilot-metrics][s1b].

### Identified vs de-identified

This matters, and it changes which files you get.

| Variant | Person column | Extra files |
|---|---|---|
| **Identified** | Real `UserPrincipalName` + `EntraId` | — |
| **De-identified** | Anonymised `PersonId` | `PeopleMetaData.csv`, `PersonPolicyMap.csv` |

De-identified is the **default**. An administrator must explicitly enable identifiable export, per
user or tenant-wide, through Viva Feature Access Management.

> *"Personal identifiers are removed and replaced with anonymized IDs, unless your administrator has
> enabled identifiable export for you."* — [export-copilot-metrics][s1b], updated 2026-08-03

> ⚠️ **Could not verify** the exact VFAM policy name that enables it. Check Feature Access Management
> in the Viva Insights admin settings, or ask Microsoft support quoting the sentence above.
>
> ⚠️ **Inferred, not confirmed:** that `PeopleMetaData.csv` and `PersonPolicyMap.csv` come only with
> the de-identified export. It is the logical reading — in the identified export the identity is
> inline, so a separate map is redundant — and it matches the exports we have seen. **CreditLens
> handles both cases automatically either way**, so you do not need to resolve this before starting.

**Identifiable export is a public preview that processes personal data.** Read the "Previews" section
of the Data Protection Addendum, and check whether per-person reporting needs works-council consent
in your jurisdiction, before you turn it on.

### Grain and history

| Export | Grain | Covers | Freshness |
|---|---|---|---|
| **Weekly** | Week (Sun–Sat, completed weeks only) | Last 6 months | Up to 6 days old |
| **Daily** | Day | Last 28 days | Up to 3 days old |

Use **weekly** for CreditLens. Every Cowork page is built on weekly grain, the forecast fits its
trend across whatever weeks you load, and 6 months beats 28 days for that.

There is **no scheduled export and no API** — each run is a point-in-time ZIP download. That is the
single best reason to move to the [Fabric path](../2.%20Fabric/), which accumulates history beyond
the 6-month window.

### Files and columns

The ZIP is named like `ConsumptionDashboard-Weekly-Identified_Aug04_2026_1859Hours.zip`.

**`PersonServiceCreditsMetrics.csv`** — one row per person × service × policy × week.

| Column | Identified | De-identified | Notes |
|---|---|---|---|
| `UserPrincipalName` | ✅ | — | Real UPN |
| `EntraId` | ✅ | — | Entra object ID |
| `PersonId` | — | ✅ | Anonymised, stable across exports |
| `PeopleHistoricalId` | — | ✅ | Joins to `PeopleMetaData.csv` |
| `ServiceId` | ✅ | ✅ | |
| `ServiceName` | ✅ | ✅ | `Cowork` or `Work IQ API` |
| `SpendingPolicyId` | ✅ | ✅ | All-zero GUID = usage outside any policy |
| `MetricDate` | ✅ | ✅ | Week start |
| `Session count` | ✅ | ✅ | |
| `Spending policy limit` | ✅ | ✅ | The policy's monthly pool |
| `Total Copilot Credits used` | ✅ | ✅ | |
| `User limit` | ✅ | ✅ | Per-person cap, if the policy sets one |

**`SpendingPolicyMetadata.csv`** — one row per policy.

| Column | Notes |
|---|---|
| `SpendingPolicyId` | |
| `Name` | Blank on the all-zero GUID row; CreditLens renders that as "(Unassigned)" |
| `PlanLimit` | Total monthly credit budget for the whole policy |
| `UserLimit` | Optional per-user cap within it |
| `IncludedServices` | e.g. `Cowork;WorkIQ` |

> ⚠️ **No official column-level schema published.** The above is from real exports. If your file
> differs, CreditLens matches column names case-insensitively and ignoring spaces, dashes and
> underscores, so minor naming changes are absorbed automatically. A genuinely new column is ignored.

### Spending policies

Configured in **M365 admin center → Copilot → Cost Management → Configuration**.

- **PlanLimit** — the monthly credit budget for everyone on the policy. Exhaust it and the whole
  policy loses access for the rest of the billing month, unless additional usage is allowed.
- **UserLimit** — an optional per-person cap, so one heavy user cannot drain the shared pool.

Roles: **Global** or **Billing Administrator** to set billing methods; **AI** or **License
Administrator** to create policies and limits but *not* change the billing method.
([usage-based-billing-manage-copilot-credits][s1c], updated 2026-07-30)

### What "Cowork" is

Cowork is the agentic service inside Microsoft 365 Copilot that carries out multi-step tasks —
sending mail, scheduling, drafting, deep research, scheduled automations.
([cowork][s1d], updated 2026-07-27)

As of August 2026 the two services under usage-based billing are **Cowork** and **Work IQ API**
([usage-based-billing-overview][s1e], updated 2026-07-30). Microsoft has said more will follow, so
treat `ServiceName` as an open list — CreditLens groups by whatever values it finds.

---

## 2. Copilot Studio credits

### Where

| | |
|---|---|
| **Portal** | <https://admin.powerplatform.microsoft.com> |
| **Path** | **Licensing** → **Products** → **Copilot Studio** → Summary / Environments / Agents tabs |
| **Role** | Power Platform Administrator, or Environment Admin |

([manage-copilot-studio-messages-capacity][s2a], updated 2026-08-04)

> ⚠️ **Export path not documented by Microsoft.** Microsoft documents the *page* — daily consumption
> trend up to 3 months, per-environment breakdowns, per-agent billed vs non-billable credits — but
> not a CSV export from it.
>
> **What is confirmed:** PPAC is a **CSV download** surface for this data. There is no API for the
> per-agent and per-user grain that CreditLens uses, so this source is manual on every path,
> including Fabric. Look for a **Download** or **Export** control on each tab.
>
> If you cannot find one, skip it — the Studio pages stay empty and the other two products are
> unaffected.

### Files and columns

**`StudioTenantDaily.csv`** — tenant × environment × day.

`BillingPlan Id`, `BillingPlan Name`, `Environment Id`, `Environment Name`, `Capacity Type`,
`Entitled Quantity`, `Prepaid Consumed Quantity`, `Pay as you go Consumed Quantity`, `Usage Date`

**`StudioPerAgent.csv`** — agent totals. **No date column.**

`Agent Name`, `Agent Id`, `Product`, `AI Feature/Billable Feature`, `Billed credit`,
`Non-billed credit`, `Channel`, `Knowledge Sources`, `Tool Used`, `LLM Model`, `Scenario Name`,
`Environment Id`, `Environment Name`

**`StudioPerUser.csv`** — user × agent totals. **No date column.**

`User Id`, `User Email`, `Agent Id`, `Agent Name`, `Billable credit used`, `Credits used`,
`M365 Copilot Licensed`

> **On the missing dates:** the per-agent and per-user files appear to be period aggregates for the
> current month-to-date, consistent with PPAC's documented "current month-to-date, the last two full
> months" behaviour. CreditLens therefore treats them as period totals and does **not** plot them on
> a time axis — only the tenant daily file drives Studio trends. This is why the Studio forecast
> extends a daily run rate rather than fitting a growth curve: there is not enough dated history to
> fit one honestly.

---

## 3. GitHub Copilot AI credits

Fully documented by GitHub — this is the most reliable of the three.

### Where

| | |
|---|---|
| **Portal** | `https://github.com/enterprises/<slug>/settings/billing` |
| **Path** | Enterprise → **Billing &amp; Licensing** → Usage → **AI usage** → **Get usage report** |
| **Role** | Enterprise owner or billing manager (org owners can download but not view per-user in the UI) |

Choose a date range of **up to 31 days**, click **Email me the report**, and GitHub mails a download
link to your primary account email. The link is valid for **24 hours**.
([view-product-license-use][s3a])

### Columns

`date`, `product`, `sku`, `model`, `quantity`, `unit_type`, `applied_cost_per_quantity`,
`gross_amount`, `discount_amount`, `net_amount`, `username`, `organization`, `repository`,
`cost_center_name` ([billing-reports][s3b])

> ⚠️ Real exports also carry `total_monthly_quota`, `aic_quantity` and `aic_gross_amount`, which are
> **not** in the published reference. They are likely newer additions. CreditLens reads them where
> present and does not fail when they are absent.

### API — yes, and better than expected

There **are** dedicated AI-credit endpoints, separate from the general billing usage endpoint:

```
GET /enterprises/{enterprise}/settings/billing/ai_credit/usage
GET /enterprises/{enterprise}/settings/billing/premium_request/usage
```

Organisation equivalents exist at `/organizations/{org}/settings/billing/...`.

| | |
|---|---|
| **Filters** | `year`, `month`, `day`, `organization`, `user`, `model`, `product`, `cost_center_id` |
| **History** | **24 months** — far beyond the 31-day web report |
| **Returns per item** | `product`, `sku`, `model`, `unitType`, `pricePerUnit`, `grossQuantity`, `grossAmount`, `discountQuantity`, `discountAmount`, `netQuantity`, `netAmount` |
| **Auth** | **Classic PAT only** — fine-grained PATs are *not* supported |
| **Scope** | `read:enterprise` or `manage_billing:copilot`; enterprise admin or billing manager |
| **Rate limit** | 5,000 req/hr (PAT), 15,000 (GitHub App) |

**The one structural catch:** `user` is a *request filter*, not a field on each row. The response tells
you what a user consumed but does not name them. To build a per-developer view you enumerate seats
first, then loop:

```
GET /enterprises/{e}/copilot/billing/seats           → every licensed user
GET .../ai_credit/usage?user={login}&year=Y&month=M  → once per user, tag rows with {login}
```

At 500 developers that is 500 calls a day — comfortably inside the rate limit.

**Three columns the API cannot give you:** `total_monthly_quota`, `aic_quantity` and
`aic_gross_amount` are in the CSV but not in the API schema (they are undocumented in the CSV
reference too). `repository` is also absent from the AI-credit schema. If you need those, the web
download stays necessary.

> ⚠️ **Not the Copilot Metrics API.** `/copilot/metrics/reports/*` is a different family —
> engagement and productivity, not billing. It does expose `ai_credits_used`, but GitHub documents
> that as *"for consumption analysis, not invoicing totals"*. It carries no gross/discount/net
> amounts. Don't build a cost dashboard on it.

> ⚠️ **A different limitation is often misquoted.** The billing docs say the **detailed usage
> report** is *"available only through the GitHub web interface and cannot be obtained via the REST
> API `/usage` endpoint"*. That is about the general metered-billing report and the general
> `/usage` endpoint — **not** about the AI-credit endpoints above. The AI-credit endpoints are the
> programmatic route.

There is **no way to trigger the emailed report programmatically** — no endpoint, no webhook, no
scheduled blob export. Automation means the API route, not the CSV route.

**([billing/usage reference][s3d], [automate usage reporting][s3e], checked 2026-08-04)**

### Seats and the allowance

You also need a seat list, as `GitHubUserMap.csv`:

`username`, `userPrincipalName`, `displayName`, `plan`, `included_credits`

`plan` must read `Copilot Business` or `Copilot Enterprise` — the seat-price measure keys on it.
`userPrincipalName` is what joins a GitHub user to the Entra org file, so department breakdowns
depend on it.

**Included allowances** ([usage-based-billing-for-organizations-and-enterprises][s3c]):

| Plan | Promotional (1 Jun – 1 Sep 2026) | Standard (from 1 Sep 2026) |
|---|---|---|
| Copilot Business | 3,000 | **1,900** |
| Copilot Enterprise | 7,000 | **3,900** |

Four things worth knowing, all confirmed:

- 1 AI credit = **$0.01**
- Credits are **pooled across the enterprise**, not reserved per person. There is no such thing as an
  individual developer being over their limit — only the pool can be over.
- Included credits **do not roll over**; they reset at 00:00 UTC on the 1st.
- **Code completions and next-edit suggestions are never billed** and never appear in this export.
  A developer can be highly active and consume zero credits.

---

## 4. Org attributes — Microsoft Entra *(optional)*

Without this file every page still works, but you lose department, cost-centre and business-unit
breakdowns. That is most of the chargeback story, so it is worth the effort.

### Where

| | |
|---|---|
| **Portal** | <https://entra.microsoft.com> |
| **Path** | **Microsoft Entra ID** → **Users** → **All users** → **Download users** |
| **Role** | None special — standard users can download the list |

([users-bulk-download][s4a], updated 2026-03-25)

### The catch: not every attribute is standard

| Attribute | Available? |
|---|---|
| `userPrincipalName`, `displayName`, `jobTitle`, `department`, `city`, `country` | ✅ In the standard bulk download |
| `manager` | Standard Entra property, but **not** in the classic download. Use Graph, or the preview download with *Employee org data* selected. |
| `costCenter`, `jobFamily`, `businessUnit` | ❌ **Not standard Entra properties.** Extension attributes, usually populated by an HR sync. Names vary per tenant. |

**CreditLens does not require any of them.** The org loader recognises a range of spellings, carries
through anything it does not recognise, and creates any expected-but-missing column as empty — so one
absent attribute cannot break the Group By control or any measure that groups by org.

### Getting manager as well

```powershell
Connect-MgGraph -Scopes "User.Read.All"

Get-MgUser -All -Property "userPrincipalName,displayName,department,jobTitle,city,country" -ExpandProperty Manager |
  Select-Object userPrincipalName, displayName, department, jobTitle, city, country,
    @{ N = 'manager'; E = { $_.Manager.AdditionalProperties.userPrincipalName } } |
  Export-Csv -Path "entra_org.csv" -NoTypeInformation -Encoding UTF8
```

For `costCenter` / `jobFamily` / `businessUnit` you need your tenant's own extension attribute names
— ask whoever owns the HR sync, then add them to `-Property` and `Select-Object`. They often live in
`onPremisesExtensionAttributes`.

---

## What happens when something is missing

CreditLens is built to degrade rather than break:

| Missing | Effect |
|---|---|
| Org file | Pages work; Group By offers fewer attributes; no department breakdown |
| One org column | That attribute disappears from Group By. Nothing else changes. |
| Studio files | Studio pages empty. Cowork and GitHub unaffected. |
| GitHub files | GitHub pages empty. Others unaffected. |
| `PeopleMetaData` / `PersonPolicyMap` | Roster is derived from the metrics file instead — see below |
| Cowork metrics file | Cowork pages empty. This is the one file worth having. |

**On the derived roster.** When the map files are absent — normal for an identified export — the seat
roster is built from the metrics file. That roster can only see people who **consumed something**. A
seat holder with no usage at all has no row in the metrics file and so will not be counted. Seat
counts and allowance totals are therefore **usage-based rather than entitlement-based** on that path.
If you need the full entitled roster, supply the map files from a de-identified export.

---

## Sources

[s1a]: https://learn.microsoft.com/en-us/viva/insights/advanced/admin/manage-settings-copilot-dashboard
[s1b]: https://learn.microsoft.com/en-us/viva/insights/org-team-insights/export-copilot-metrics
[s1c]: https://learn.microsoft.com/en-us/microsoft-365/copilot/usage-based-billing-manage-copilot-credits
[s1d]: https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/
[s1e]: https://learn.microsoft.com/en-us/microsoft-365/copilot/usage-based-billing-overview-copilot-credits
[s2a]: https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity
[s3a]: https://docs.github.com/en/billing/how-tos/products/view-productlicense-use
[s3b]: https://docs.github.com/en/billing/reference/billing-reports
[s3c]: https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises
[s3d]: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage
[s3e]: https://docs.github.com/en/enterprise-cloud@latest/billing/tutorials/automate-usage-reporting
[s4a]: https://learn.microsoft.com/en-us/entra/identity/users/users-bulk-download

| # | Source | Checked |
|---|---|---|
| s1a | [Manage Copilot Dashboard settings][s1a] | 2026-08-03 |
| s1b | [Export Copilot metrics][s1b] | 2026-08-03 |
| s1c | [Manage Copilot Credits][s1c] | 2026-07-30 |
| s1d | [Microsoft 365 Copilot Cowork][s1d] | 2026-07-27 |
| s1e | [Usage-based billing overview][s1e] | 2026-07-30 |
| s2a | [Manage Copilot Studio capacity][s2a] | 2026-08-04 |
| s3a | [View product and license use][s3a] | 2026-08-04 |
| s3b | [Billing reports reference][s3b] | 2026-08-04 |
| s3c | [Usage-based billing for orgs and enterprises][s3c] | 2026-08-04 |
| s3d | [REST billing usage endpoints][s3d] | 2026-08-04 |
| s3e | [Automate usage reporting][s3e] | 2026-08-04 |
| s4a | [Bulk download users][s4a] | 2026-03-25 |

Preview features move. If a click-path here does not match what you see, the portal is right and this
document is stale — please open an issue.
