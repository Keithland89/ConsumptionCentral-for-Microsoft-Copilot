# Contributing

Thank you for your interest in CreditLens.

## Contributor License Agreement

Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you
have the right to, and actually do, grant us the rights to use your contribution. For details, visit
<https://cla.opensource.microsoft.com>.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a
CLA and decorate the PR appropriately. Follow the instructions provided by the bot; you only need to
do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions.

---

## What's most useful

**Corrections to the click-paths.** Several of the exports CreditLens reads are in preview and their
portals move. If a path in [docs/DATA-SOURCES.md](docs/DATA-SOURCES.md) no longer matches what you
see, that is a genuinely valuable issue — please include what you saw instead.

**Answers to the open questions.** Three things are marked unverified in the docs, and a definitive
answer to any of them would improve the template for everyone:

1. Does the **Viva Insights Power BI connector** expose Consumption Dashboard credit data, or only
   Analyst Workbench queries? See [3. Viva Direct](3.%20Viva%20Direct/).
2. What is the exact **VFAM control** that enables identifiable export?
3. Where exactly do the **Copilot Studio CSVs** download from in PPAC?

**New export shapes.** If your export has columns ours does not, open an issue with the header row
(no data rows, please). The loaders alias-match on purpose so new shapes can usually be absorbed
without breaking anyone.

---

## Working on the model

The report is a **PBIP project** — TMDL for the model, JSON for the report — so changes are
reviewable in a diff.

Two rules, both learned the hard way:

**Edit with Power BI Desktop closed.** Desktop holds an in-memory copy and writes it back over your
changes on save. Close it, edit, validate, then open.

**Save the model in Desktop before closing it.** Model edits made through an external tool only
reach the TMDL files when Desktop saves. Force-closing discards them.

### Before opening a PR

If you have changed model or report files, please confirm:

- [ ] The project opens in Power BI Desktop without error
- [ ] A full refresh completes against the sample data
- [ ] Every page renders — a visual can silently vanish without any file being invalid
- [ ] No new hardcoded numbers, dates, or interpretations in any card, title or measure

That last point matters more than it sounds. CreditLens is a **template**: every customer's data is
different, so a headline that says "usage grew 19.8% over the last 13 weeks" is a lie for the next
reader unless both numbers are computed. If you add narrative, derive it.

### Testing against both export shapes

The Viva consumption export comes in two shapes and both must keep working. If you touch anything in
the loading path, test with:

- the **de-identified** sample under `1. Local CSV/sample-data/`
- an **identified** export, or a hand-made file with `UserPrincipalName` and `EntraId` instead of
  `PersonId` and `PeopleHistoricalId`, and *without* the two person-map files

A useful check: on a small file, count the rows. A join that fans out doubles your credits, and on a
large file doubled credits look entirely plausible.
