# Automating the landing step

Three of Consumption Central's four sources have **no REST API** — Viva consumption, Copilot Studio, and Entra org
attributes all have to be exported by hand. Only GitHub can be pulled directly, which
[`Ingest_GitHub_API.ipynb`](../notebooks/Ingest_GitHub_API.ipynb) does.

That leaves someone remembering to download files. For the Viva export in particular that matters
more than it sounds: it reaches back five months, so a forgotten quarter is permanently lost history.

**The fix is a Power Automate flow that lands the file for you** — watch a mailbox or a SharePoint
library, write straight to OneLake, let the ingester pick it up on its next run.

---

## Use the ValueLens flows

Two working flows already exist and need only their trigger filter and target folder changed:

**[ValueLens → Fabric + Copilot Studio → flows][vl]**

| Flow | Use when |
|---|---|
| `Copilot_Consumption_Email_to_OneLake.json` | The export arrives by **email** |
| `Copilot_Consumption_SharePoint_to_OneLake.json` | You prefer a governed **SharePoint** drop folder |

They write to OneLake with the ADLS Gen2 three-step pattern — `PUT ?resource=file` →
`PATCH ?action=append` → `PATCH ?action=flush` — against audience `https://storage.azure.com/`.

We link rather than fork them: a copy here would drift from the original, and there is no version of
that which ends well for whoever reads it in six months.

---

## What to change per source

Import the flow, then set the parameters. Only two differ per source.

| Source | `TargetFolder` | Email `SubjectFilter` |
|---|---|---|
| Viva consumption | `Files/landing/viva` | `Consumption Dashboard` |
| Copilot Studio | `Files/landing/studio` | `Copilot Usage Dashboard` |
| GitHub AI usage *(if not using the API)* | `Files/landing/github` | `usage report` |
| Entra org | `Files/landing/org` | whatever your export script sends |

The rest stay as documented in the ValueLens README: `OneLakeWorkspace`, `OneLakeLakehouse`,
`TenantId`, `ClientId`, `ClientSecret`.

**`TargetFolder` must match `LANDING` in the matching ingester notebook.** That is the one setting
that silently does nothing if you get it wrong — the flow reports success, the file lands somewhere
the notebook never looks, and the table stays empty.

---

## The one real prerequisite

The HTTP actions authenticate as a service principal, which must be able to **write** to the
workspace's OneLake:

1. Add the app registration (or workspace identity) as **Member or Contributor** on the Fabric
   workspace holding the Lakehouse
2. Put the secret in **Azure Key Vault** and reference it — do not ship a literal `ClientSecret`
3. The tenant setting **"Service principals can use Fabric APIs"** must be on

**Prefer not to use an app secret?** Swap the three `Http` actions for **OneLake / Azure Blob**
connector actions and authenticate interactively. The create/append/flush URIs are identical.

---

## Getting the export to arrive in the first place

A flow can only react to a file that shows up. How each source gets there:

| Source | Reality |
|---|---|
| **Viva consumption** | Manual download, then mail it to the watched mailbox or drop it in the library. **Or skip the flow entirely** — a [Dataflow Gen2](../README.md#the-viva-half-can-run-itself) writes query results straight to the Lakehouse on a schedule. |
| **Copilot Studio** | Same — PPAC is download-only. |
| **GitHub** | The report is *emailed to you*, so the email flow can catch it with no human step at all. Better still, skip it and use the API notebook. |
| **Entra org** | Schedule the Graph PowerShell snippet in [DATA-SOURCES.md](../../docs/DATA-SOURCES.md) and have it write to the SharePoint library. Fully automatable. |

So realistically: **GitHub and Entra can be fully hands-off. Viva and Studio still need someone to
press export** — the flow just removes the "save it in the right place" step and the mistakes that
come with it.

That is still worth having. The failure mode you are protecting against is not someone forgetting to
click download; it is someone downloading it and putting it somewhere the pipeline cannot see.

---

## Re-runs are safe

Every Consumption Central ingester merges on a natural key, so re-landing the same export updates rather than
duplicates. You can leave old files in the landing folder, or prune them — neither changes the
numbers.

The Studio ingester additionally records a `source_file` column, so if a bad export does land you can
find its rows and remove them.

---

## Reusing the pattern elsewhere

The `PUT → append → flush` mechanism works for **any** export-only Microsoft report. Only the trigger
filter and target folder change. ValueLens documents the generalised version at
[`2. Fabric/flows/README.md`][vlg].

---

[vl]: https://github.com/Keithland89/ValueLens-for-Microsoft-Copilot/tree/main/3.%20Fabric%20Extended/Fabric%20%2B%20Copilot%20Studio/flows
[vlg]: https://github.com/Keithland89/ValueLens-for-Microsoft-Copilot/tree/main/2.%20Fabric/flows

**Related:** [StudioLens][sl] reads the same PPAC exports for agent-level analytics, and its ingester
is where the real export filenames used by our Studio notebook were confirmed.

[sl]: https://github.com/Keithland89/StudioLens-for-Copilot-Studio
