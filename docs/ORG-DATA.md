# Org data

Department, job title, cost centre, country, manager — the attributes the **Group By** control offers
beyond usage intensity.

**None of the three consumption sources carry them.** Viva gives you an identity (UPN and Entra ID),
Copilot Studio gives you an email, GitHub gives you a handle. Every organisational attribute comes
from your directory, and you supply it.

That is not a gap in the template. Your directory holds richer and more current org data than any
consumption export would, and it is the same directory all three products can be joined back to.

---

## What it unlocks

Without org data the report is complete and correct — every credit, cost, trend and forecast figure
is right. Group By simply falls back to **usage intensity** (percentile cohorts derived from
consumption itself).

With it, every one of those figures can be cut by department, cost centre, country, manager or
business unit — **across all three products at once**, which is the point of the report.

```
org_attributes ──┬── user_principal_name ──── Cowork / Work IQ credits
                 ├── user_principal_name ──── Copilot Studio  (via user_email)
                 └── user_principal_name ──── GitHub Copilot  (via the handle map)
```

---

## Three ways to get it

All three produce the same shape. Pick by how you deploy.

| | Tool | Auth | Good for |
|---|---|---|---|
| **A** | [`Get-EntraOrgData-SP-AppReg.ps1`][ps-appreg] | App registration | **Scheduled**, unattended — Task Scheduler, Azure Automation, GitHub Actions |
| **B** | [`Get-EntraOrgData-SP.ps1`][ps-interactive] | Browser sign-in | One-off, or validating the pipeline before automating |
| **C** | [`Copilot_Org_Data_Direct_Ingester.ipynb`][vl-notebook] | App registration | **Fabric** — calls Graph from inside the Lakehouse, no file anywhere |

> These live in **[AI-in-One-Dashboard][ai1]** and **[ValueLens][vl]**. They are linked rather than
> copied, so you get their fixes rather than a fork that quietly ages. Both are Keith's or
> Microsoft's own; neither is CreditLens-specific.

### A and B — PowerShell to CSV

Both call `GET /v1.0/users` with `$expand=manager` and write a CSV. Point `DataFolder` (Local CSV) or
`EntraCsvPath` (Viva Direct) at it.

Run **[`provisioning/ProvisionPreReqs.ps1`][prov]** once per tenant first — it sets up the app
registration and grants `User.Read.All`.

Schedule A weekly. Org data changes slowly; a stale department is a smaller problem than a missing
one, but a quarter-old org chart will misattribute anyone who moved.

### C — Fabric, no file

Writes a Delta table directly, so nothing lands on anyone's laptop. It also builds a **flattened
manager hierarchy** — `Level0_Name`…`LevelN_Name`, `OrgLevel`, `HierarchyPath`, `IsManager`,
`DirectReports` — which CreditLens does not use today but is there if you want to extend it.

It writes to `copilot_org_data`. CreditLens reads `org_attributes`. Either rename the output table or
add a one-line view:

```sql
CREATE VIEW org_attributes AS SELECT * FROM copilot_org_data;
```

The column *names* need no mapping — see below.

---

## Columns

CreditLens matches on a **normalised** name: case, spaces, underscores and hyphens are ignored. So
`user_principal_name`, `userPrincipalName` and `User Principal Name` are the same column.

| CreditLens | Also accepts |
|---|---|
| `UserPrincipalName` | `upn`, `email`, `mail`, `PersonId`, `PersonId_Normalized` |
| `DisplayName` | `name`, `fullName`, `preferredName` |
| `Department` | `dept`, `Organization`, `organisation` |
| `JobTitle` | `title`, `role` |
| `JobFamily` | `function`, `functionType`, `jobFunction` |
| `City` | `officeLocation`, `location` |
| `Country` | `countryOrRegion`, `region` |
| `CostCenter` | `costCentre` |
| `Manager` | `managerName`, `supervisor`, `managerId`, `managerUPN` |
| `BusinessUnit` | `division`, `segment`, `companyName` |

**Anything absent is created empty** rather than failing the load, so a directory export missing
`costCenter` costs you that one breakdown and nothing else.

All three sources above land 8 of the 10 — everything except `JobFamily` and `CostCenter`, which
Entra does not hold as standard attributes. Add them yourself if you have them.

> `Organization` maps to `Department`, and `companyName` to `BusinessUnit`. Both are deliberate:
> Entra's `department` is what people mean by department, and `companyName` is the closest thing it
> has to a business unit.

---

## The join, and why it is usually the problem

**Matching is on UPN, lowercased and trimmed on both sides.**

If a department breakdown comes back empty or full of people with no credits, it is almost always the
join rather than the model:

| Symptom | Cause |
|---|---|
| Group By empty, credits fine | No org file supplied, or the path is wrong |
| Departments listed, all zero credits | Org file is for a **different tenant** — no UPN matches |
| Some people missing | Guest accounts, service accounts, or people who left since the export |
| **De-identified Viva export** | Hashed person IDs cannot match a real UPN. Org grouping is not possible — use an identified export if you need it |

**Copilot Studio** joins on `user_email`, which must be the same UPN. **GitHub Copilot** joins
through the handle map, since the GitHub billing export carries a handle and no email — see
[the GitHub notes](DATA-SOURCES.md#github-copilot).

---

## How often

| | |
|---|---|
| **Weekly** | Matches the Viva export cadence. A reasonable default. |
| **Monthly** | Fine for a stable org. |
| **Quarterly or less** | People who moved get attributed to their old department. Chargeback arguments follow. |

[ps-appreg]: https://github.com/microsoft/AI-in-One-Dashboard/blob/main/Classic%20Editions/2.%20SharePoint/File/scripts/appreg/Get-EntraOrgData-SP-AppReg.ps1
[ps-interactive]: https://github.com/microsoft/AI-in-One-Dashboard/tree/main/Classic%20Editions/2.%20SharePoint/File/scripts/interactive
[prov]: https://github.com/microsoft/AI-in-One-Dashboard/tree/main/Classic%20Editions/2.%20SharePoint/File/scripts/provisioning
[ai1]: https://github.com/microsoft/AI-in-One-Dashboard
[vl]: https://github.com/Keithland89/ValueLens-for-Microsoft-Copilot
[vl-notebook]: https://github.com/Keithland89/ValueLens-for-Microsoft-Copilot/blob/main/2.%20Fabric/notebooks/Copilot_Org_Data_Direct_Ingester.ipynb
