# Support

## How to get help

This project uses **GitHub Issues** for bugs and feature requests. Please search the existing issues
before opening a new one — several of the exports this template reads are in preview and their
portals move, so the same question often comes up more than once.

| I want to… | Where |
|---|---|
| Report something broken | [Open an issue](../../issues) — include which path (Local CSV, Fabric, Viva Direct) and what you saw |
| Say a click-path is wrong | [Open an issue](../../issues) — tell us what the portal shows instead. These are genuinely useful. |
| Ask how something is calculated | [docs/MEASURES.md](docs/MEASURES.md) documents every measure and why it works that way |
| Work out what data I need | [docs/DATA-SOURCES.md](docs/DATA-SOURCES.md) has the click-paths and permissions |
| Understand department breakdowns | [docs/ORG-DATA.md](docs/ORG-DATA.md) |
| Suggest a change | See [CONTRIBUTING.md](CONTRIBUTING.md) |

### Before you open an issue

Two things make a report far quicker to act on:

- **Which deployment path** you used, and **which product's pages** are wrong. The four products
  load independently, so "the Studio pages are empty but GitHub is fine" narrows it immediately.
- **What the figure said versus what you expected.** A screenshot of the page is ideal. Please
  redact anything identifiable first — see below.

### Please don't attach real data

Issues here are public. Do not attach an unredacted export, a `.pbix` containing your tenant's
data, or screenshots showing real names, email addresses or spend. The synthetic sample set under
`1. Local CSV/sample-data/` reproduces most problems and is safe to share.

Security vulnerabilities go to MSRC, **not** to GitHub Issues — see [SECURITY.md](SECURITY.md).

## Microsoft support policy

This is a community-supported project released under the [MIT licence](LICENSE). It is **not**
covered by a Microsoft support agreement, and there is no SLA on issue response. Support is limited
to the resources listed above.
