# Building the templates

The `.pbit` files are produced from the working PBIP project. This is a short manual step — Power BI
Desktop has no command-line template export, so it cannot be scripted.

## Source project

```
CreditLens-GHCP\CreditLens - Cowork WorkIQ Studio GHCP.pbip
```

27 tables, 284 measures, 14 pages.

## Producing `CreditLens - Local CSV.pbit`

1. Open the `.pbip` in Power BI Desktop and let it refresh.
2. **Reset the seven parameters to shipping defaults** — *Transform data → Manage parameters*. A
   `.pbit` stores parameter *defaults*, so whatever is set here is what every customer sees first.
   This is the step to be careful about: if `DataFolder` still points at your OneDrive, or the rates
   are a customer's real ones, that ships inside the file.

   | Parameter | Ship as |
   |---|---|
   | `DataFolder` | `C:\CreditLens\Data` — a neutral placeholder |
   | `CreditRate` | `0.01` |
   | `PrepaidCreditRate` | `0.008` |
   | `PrepaidCreditBalance` | `0` |
   | `GitHubBusinessSeatPrice` | `19` |
   | `GitHubEnterpriseSeatPrice` | `39` |
   | `BillingPeriodWeeks` | `4` |

3. Check the **Settings** query still holds `#date(2026, 9, 1)`, `1900`, `3900` for the GitHub
   allowance change — those are constants there, not parameters, so they are easy to forget.
4. **File → Export → Power BI template**.
5. Description:
   > Copilot credit consumption and cost across Cowork/Work IQ, Copilot Studio and GitHub Copilot.
   > Point DataFolder at a folder holding your exports — the files are found by name, so nothing
   > needs renaming and anything you do not have is skipped. See the README for where each export
   > comes from.
6. Save as `1. Local CSV\CreditLens - Local CSV.pbit`.

## Producing `CreditLens - Fabric.pbit`

Same model, different source. From the same project:

1. Swap each table's partition from the folder-discovery pattern to
   `Sql.Database(FabricSQLEndpoint, LakehouseName)` against the table contract in
   [`2. Fabric/README.md`](2.%20Fabric/README.md#table-contracts).
2. Replace `DataFolder` (and the `DataFiles` / `GetDataFile` helpers it feeds) with two text
   parameters: `FabricSQLEndpoint` and `LakehouseName`.
3. Leave the five commercial parameters as they are — they are source-independent.
4. Export as above to `2. Fabric\CreditLens - Fabric.pbit`.

**Keep these as two separate templates.** A single template that branches on a `SourceMode` parameter
is tempting and does not work reliably: Power Query registers every data source in an `if/then/else`
at *parse* time rather than runtime, so the firewall sees the CSV and SQL sources as being combined
in one partition and throws
`Formula.Firewall: ... privacy levels which cannot be used together`. Two files, no branch.

## Before you ship either one

- [ ] Open the exported `.pbit` fresh — it should prompt for parameters before touching any data
- [ ] Point it at `sample-data\` and confirm all 14 pages render
- [ ] Check no parameter default contains a real customer path, endpoint or rate
- [ ] Confirm the model has no cached data: templates carry structure only, never rows

## Checks worth running first

The validators used while building this live in the session workspace. They catch, in about a second
each, several classes of problem that otherwise cost a two-and-a-half-minute failed Desktop load:

| Script | Catches |
|---|---|
| `check_m_syntax.py` | Unbalanced brackets, `let`/`in` mismatch, bare `try`, unquoted identifiers like `[@upn]` |
| `check_tmdl_indent.py` | TMDL indentation damage — a `///` block at the wrong depth stops the whole model loading |
| `validate_model.py` | Duplicate measures, DAX reserved words used as VAR names, dangling references |
| `validate_schema.py` | Malformed `visual.json` |
| `validate_layout.py` | Overlapping or off-canvas visuals |
| `validate_narrative.py` | Narrative measures referencing something that no longer exists |
| `audit_template_safety.py` | Hardcoded figures, dates or interpretations in any card or title |

That last one matters most for a template. Run it before every release: a headline that says "usage
grew 19.8% over the last 13 weeks" is simply false for the next customer unless both numbers are
computed from their data.
