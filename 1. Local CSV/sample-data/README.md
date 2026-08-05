# Sample data

A synthetic dataset so you can see CreditLens working before you go and collect your own exports.

**None of this is real.** It is generated data for a fictional insurance company — invented people,
invented departments, invented usage. It carries no tenant's information and nothing here should be
read as a benchmark.

## What's here

| File | Rows | Represents |
|---|---|---|
| `PersonServiceCreditsMetrics.csv` | 1,500 | Cowork credits, person × week, **de-identified shape** |
| `SpendingPolicyMetadata.csv` | 42 | Spending policies with plan and user limits |
| `PersonPolicyMap.csv` | 1,020 | Person → policy map |
| `PeopleMetaData.csv` | 1,020 | Organisation and licence flag per person |
| `entra_org.csv` | 1,020 | Department, cost centre, job family, manager |
| `StudioTenantDaily.csv` | 31 | Copilot Studio, tenant × environment × day |
| `StudioPerAgent.csv` | 448 | Studio agent totals |
| `StudioPerUser.csv` | 29 | Studio user totals |
| `GitHubAiUsage.csv` | 3,000 | GitHub AI credit usage, person × day |
| `GitHubUserMap.csv` | 219 | GitHub seats with plan and included credits |

The Cowork and GitHub files are trimmed from a larger set to keep the repo small, so totals here are
lower than a full year of a real tenant. Shapes, column names and relationships are faithful.

## Using it

> **The `.pbit` is not built yet.** See [docs/BUILD.md](../../docs/BUILD.md) — it is a short manual
> step, because Power BI Desktop has no command-line template export. Until then, open the PBIP
> project directly.

Set the **`DataFolder`** parameter to this folder. That is the only one that has to change — the
files are found by name, so nothing needs renaming and nothing needs a path of its own.

Leave the commercial parameters at their defaults for a first look. The cost pages will then be
arithmetic on list prices rather than your agreement, which is fine for seeing the shape of it.

## A note on the two export shapes

This sample is the **de-identified** shape: `PersonId` and `PeopleHistoricalId`, with the person map
files alongside. That is the shape most tenants get by default.

If your tenant has identifiable export enabled you will get the **identified** shape instead — real
`UserPrincipalName` and `EntraId` inline, and *no* `PersonPolicyMap.csv` or `PeopleMetaData.csv`.
The template handles both automatically; see
[the data sources doc](../../docs/DATA-SOURCES.md#identified-vs-de-identified).

Worth knowing: on the identified path the seat roster is derived from the metrics file, so it can
only see people who consumed something. Seat counts become usage-based rather than
entitlement-based. The sample data uses the de-identified shape partly so that the fuller behaviour
is what you see first.
