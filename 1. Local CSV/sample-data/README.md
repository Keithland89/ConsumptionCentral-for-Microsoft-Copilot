# Sample data

A synthetic dataset so you can see Consumption Central working before you go and collect your own
exports. Set **`DataFolder`** to this folder and everything loads.

**None of this is real.** It is generated data for a fictional insurance company — invented people,
invented departments, invented usage. It carries no tenant's information and nothing here should be
read as a benchmark.

## What's here

All four products, over the same thirteen weeks — **3 May to 31 July 2026** — so the combined page
compares like with like.

| File | Rows | Represents |
|---|---|---|
| `PersonServiceCreditsMetrics.csv` | 1,500 | Cowork credits, person × week, **de-identified shape** |
| `SpendingPolicyMetadata.csv` | 42 | Spending policies with plan and user limits |
| `PersonPolicyMap.csv` | 1,020 | Person → policy map |
| `PeopleMetaData.csv` | 1,020 | Organisation and licence flag per person |
| `entra_org.csv` | 1,020 | Department, cost centre, job family, manager |
| `StudioTenantDaily.csv` | 810 | Copilot Studio, environment × day |
| `StudioPerAgent.csv` | 40 | Studio agent totals |
| `StudioPerUser.csv` | 240 | Studio user totals, reconciling to the tenant file |
| `GitHubAiUsage.csv` | 11,916 | GitHub AI credit usage, person × day |
| `GitHubUserMap.csv` | 219 | GitHub seats with plan and included credits |
| `AzureAiSpendDaily.csv` | 1,473 | Azure AI Foundry spend by meter and resource |
| `AzureAiTokensDaily.csv` | 1,530 | Foundry token counts and PTU utilisation |

## What the demo shows

The data is shaped to exercise the parts of the report that matter, rather than to look tidy:

- **GitHub crosses its allowance.** May sits at 0.63× the credit pool and costs nothing. June lands
  almost exactly on it. July runs to 1.34× and bills about $4,000. That is what the overage measures,
  the cost pages and the September allowance change are all there to show.
- **Studio consumes both prepaid and pay-as-you-go**, so the cost split has two bars rather than one.
- **Provisioned Azure capacity sits near 30%**, which is the finding the Foundry page exists to
  surface — capacity paid for and not used.
- **Foundry spend is tagged with real departments**, so Group By reaches it like every other product.
- **A few people are licensed and completely inactive**, which is what the optimisation pages look for.

## Using it

Set the **`DataFolder`** parameter to this folder. That is the only one that has to change — files are
found by name, so nothing needs renaming and nothing needs a path of its own. That now includes the
two Azure files: drop them in with the rest and the Foundry page fills in.

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
