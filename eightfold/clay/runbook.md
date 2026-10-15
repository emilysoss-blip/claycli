# Eightfold demand-gen POC: CLI runbook

The build guide's sequence with [`guide_corrections.md`](./guide_corrections.md) applied and
wired to the files in this repo. Placeholders in `<angle brackets>` come from real command
output. Never paste them unchanged. Record every ID in the manifest at the bottom as it
comes back.

**Status:** partly executed on 2026-10-15 with Clay CLI 1.9.0. The workflow is built and
tested on 10 accounts, and is not published; see [`cli_build.md`](./cli_build.md) for IDs,
results and findings. Signals, Audiences fields and Salesforce writeback are not built yet.

Order of operations, and why it is this order:

1. Identity before enrichment. 8 of the 30 parents cannot be enriched safely by domain alone
   (`enrichment_identifier` is a LinkedIn URL on those rows).
2. Native before AI. Claygent only touches a field after a native source has been tried and
   recorded as failed.
3. Rules before routing. Tier and talent-leader qualification are code (`tiering.py`,
   `leaders.py`), so a reviewer can trace any outcome to one line.
4. Salesforce writes disconnected until the 10- and 50-row samples pass review.

---

## 0. Setup and inventory

```bash
# in Claude Code
/plugin marketplace add clay-run/agent-plugins
/plugin install clay@clay-plugins
# then run the bundled clay:setup skill; it installs the CLI and signs in

clay --version
clay whoami                                   # confirm workspace id + name before creating anything
clay workflows actions list > ./eightfold-actions-catalog.json
clay routines list
clay audiences fields list --entity-type companies > ./eightfold-company-fields.json
clay audiences fields list --entity-type people    > ./eightfold-people-fields.json
clay signals list                             # existing watches; do not duplicate one
```

Find the actions this build needs. Verify each one by field, not by integration. A connector
existing does not mean its fields are usable.

```bash
jq '.data[] | select(((.displayName // .name // "") + " " + (.description // "") + " " + (.packageDisplayName // ""))
   | test("company|domain|headcount|jobs|hiring|technolog|parent|email|intent|Salesforce|Marketo"; "i"))
   | {displayName, packageDisplayName, packageId, actionKey, creditCost, availableAppAccounts}' \
   ./eightfold-actions-catalog.json

clay workflows actions schema <packageId> <actionKey>   # read outputParameters: these are your $.result.<field> paths
```

**HR-tech coverage check.** Before you select a technographic action, confirm its schema
covers HR systems (Workday, SuccessFactors, Oracle HCM, Taleo, iCIMS, Greenhouse).
Technographic coverage is usually thinnest exactly here. This build's Tech Stack enrichment
returned nothing readable (read-back failed), so the question is still open.

## 1. Seed and identity

Swap the stand-in cohort for the agreed Salesforce export, but keep the identity method.

```bash
python3 eightfold/build/seed_accounts.py      # accounts.csv (parent grain) + divisions.csv (hiring-entity grain)
python3 eightfold/build/seed_clay_match.py    # per-domain match quality
```

Upload rule, from `clay_match_quality.csv`:

| match_class | Upload identifier | Domains in this cohort |
|---|---|---|
| `clean` | domain | 23 |
| `clean_with_stale_pages` | domain, then suppress stale entities | 5 |
| `shared_domain` | **LinkedIn URL per hiring entity** | 9 |
| `parent_missing_by_domain` / `no_usable_match` | **LinkedIn URL**: the domain never returns the parent | commonspirit.org, kaiserpermanente.org |
| `wrong_company` / `stale_parent` / `satellite_only` | **drop the domain** | marshmclennan.com, ge.com, mercer.com |

`accounts.csv` already carries the right value in `enrichment_identifier`. Upload that column,
not `account_domain`.

## 2. Workflow and CSV trigger

```bash
clay workflows create --name "Eightfold | Demand Gen Account Intelligence POC"
clay workflows triggers create <workflowId> --input '{"triggerType":"csv_upload"}'
clay workflows graph get <workflowId>         # trigger id is in .triggers[].id, not the create response's resourceId
clay workflows triggers csv upload <triggerId> --file ./eightfold-accounts-test10.csv
#   check csvFile.headers for duplicates: a duplicate header silently overwrites the earlier column
```

Headers become string fields at `$.<header>`. Cast `clay_employee_count` explicitly.

Node sequence (group as **Identity**, **Research**, **Qualification**):

```
csv_upload
 └─ Identity:      normalize → identity check (match_class gate) → CRM reuse / cache gate
 └─ Research:      native company enrichment → hiring (JobPost / Open Jobs) → HR technographics
                   → "Needs enrichment fallback?" (rules) ─┬─ yes → field-level Claygent
                                                          └─ no ──────────────┐
 └─ Qualification: evidence reconciliation → tiering (code node = tiering.evaluate) → POC output
```

Wire `csv_upload` to the first node **before** any run. An unwired trigger accepts `csv run`
and then fails every row with "Workflow has no initial node."

### Tool-node template

```json
{
  "nodeType": "tool",
  "name": "Native company enrichment",
  "incomingEdges": [{"sourceNode": "<previousNodeId>"}],
  "tools": [{
    "toolType": "clay_action",
    "actionKey": "<catalogActionKey>",
    "actionPackageId": "<catalogPackageId>",
    "inputMappingConfig": {
      "<exactSchemaInputName>": {"type": "reference", "expression": "{{enrichment_identifier}}"}
    }
  }]
}
```

```bash
clay workflows nodes create <workflowId> --input ./eightfold-native-company-node.json
clay workflows nodes get <workflowId> <nodeId>     # confirm the mapping persisted; invented inputSchema keys are dropped on save
```

**Downstream references to an enrich node use `$.result.<outputPath>`.** Not
`$.toolResult.result`. See corrections #1.

## 3. Fallback gate and Claygent

Rules conditional `Needs enrichment fallback?`: route a row to Claygent only when **all** of
these hold:

- `identity_status` is resolved
- a required fit field (`hcm`, `open_reqs`) is empty or conflicted after native sources
- `native_sources_tried` lists every structured source for that field
- the field could move the tier: `fit_best_case >= tier2_min` from `tiering.py`

Prompt and output schema: [`claygent_fallback.md`](./claygent_fallback.md). Log the share of
rows that needed AI and how much usable coverage it added. That number answers the
build-vs-buy question.

## 4. Tiering

A Python code node holding `evaluate()` and `CRITERIA` from `eightfold/build/tiering.py`,
pasted verbatim. Keep the same `score_version`, test locally first, and never re-implement
it in a prompt.

```bash
python3 eightfold/build/tiering.py && python3 eightfold/build/test_engine.py
```

Output fields: `fit_score`, `fit_best_case`, `fit_tier`, `missing_required_fields`,
`score_reasons`, `intent_score`, `engagement_score`, `score_version`, `scored_at`, plus a
tri-state `check_*` per criterion. Intent (6sense) and engagement (Marketo) are carried
through as-is and never enter `fit_score`.

## 5. Buying committee

Tier 1, plus some Tier 2 for comparison. Three persona groups, five contacts per account,
deduped by LinkedIn URL **and** by name + employer + title + start (this build returned the
same GE Aerospace TA lead under two URLs).

```bash
clay searches query-mode reference | jq -r '.reference' > ./eightfold-search-reference.md
grep -n '^##' ./eightfold-search-reference.md    # read Grammar / Operators / Where Semantics by offset
clay searches query-mode create --query '<query built from the reference>'
clay searches query-mode run <searchId> --limit 10   # forward-only; each call is the NEXT page
```

The query used in this build (MCP form, same DSL):

```
select from people where experiences.any(is_current = true
  and job_title is_similar_to ("Chief People Officer", "Chief Human Resources Officer",
      "Head of Talent Acquisition", "Head of Talent Intelligence", "VP Talent Acquisition",
      "Head of People Analytics")
  and start_date >= today() - interval 18 months)
limit 3 by clay_company_id
```

Pass every result through `leaders.py` before it is routed. Then use the managed person and
work-email routines (`clay routines list` / `get`) before building a custom waterfall.

## 6. Signals

```bash
clay signals list                              # duplicate check: compare signal.type and input
clay signals create --help                     # the authority on --input shape per type
clay audiences list --entity-type companies    # resolve segment IDS, never names ("ALL" is a sentinel)
clay signals create --type NewHire --name "Eightfold | New talent leadership at ICP accounts" \
  --input '<shape from --help, using segmentIds from the audiences list>'
clay signals get <td_id> | jq '.input, .filter, .schedule'   # created Paused; confirm before resume
clay signals resume <td_id>                    # starts spending
```

Type mapping is in `data/signals.csv`. One rule from this build: a domain-watched signal
on `commonspirit.org` or `kaiserpermanente.org` would watch member hospitals or placeholder
pages, never the parent. Check identifier coverage on the segment before `resume`.

Bind a workflow to signal events with an `audience_signal` trigger on the **`sig_…`** id
(`signal.id`), not the `td_…` id.

## 7. Test 10 → 50 → cohort

```bash
clay workflows graph validate <workflowId>          # structure only, not data quality
clay workflows triggers csv run <triggerId> --limit 10
clay workflows runs list <workflowId>
clay workflows runs get <runId> --nodes
clay workflows runs get <runId> --wait 60
clay workflows runs steps <workflowId> <runId> --status failed
clay workflows nodes test <workflowId> <nodeId> --source-run <runId>   # cheapest way to debug one mapping

# 50: rows 11-60 in a NEW file (--limit has no offset), then run without --limit
clay workflows triggers csv upload <triggerId> --file ./eightfold-accounts-rows11-60.csv
clay workflows triggers csv run <triggerId>
```

`csv run` is not idempotent. After a timeout, inspect `runs list` before retrying, or the
batch doubles.

The 10-row test file should include, from this cohort:

| Row | Why it is in the test set |
|---|---|
| UnitedHealth Group | clean parent + divisions on separate domains (UHC, Optum) |
| HCA Healthcare | shared-domain parent + division pair |
| Johns Hopkins | 34+ entities across two domains |
| CommonSpirit Health | parent missing by domain; LinkedIn-only |
| Kaiser Permanente | domain returns placeholders; LinkedIn-only |
| Marsh | renamed parent; wrong-company match on the old domain |
| GE Vernova | four inactive legacy pages on the domain |
| Honeywell Technologies | headcount conflict (page text vs employee_count) |
| Lockton | Head of Talent Intelligence: the category-match trigger |
| State Farm | non-employee agent network on the carrier domain |

Plus a known customer, an open opportunity and a suppressed account from the real export.
This repo cannot supply those three, because it does not know Eightfold's CRM state.

## 8. Publish

```bash
clay workflows publish <workflowId> --name "Eightfold demand gen POC validated"
```

A published workflow and a paused signal are separate controls. Check both.

---

## Manifest

| Object | ID | Notes |
|---|---|---|
| Workspace | `91642` Clay Demos (GTM) | MCP connection used for this build |
| Workflow | `wf_0tmyo3dtqBTPxC5cfhA` | draft, validated, not published |
| CSV trigger | `c1f5fe62-0eee-4b73-8bc2-b69c734adc51` (node `wfn_0tmyo3kQhMa2bu3NTNt`) | live from creation |
| Identity group | `wfng_0tmyo9lNX9f9pyapv67` | |
| Research group | `wfng_0tmyo9nEJZWKywc9XW6` | |
| Qualification group | `wfng_0tmyo9o9msMw57sYKWb` | |
| NewHire signal | not created | deferred until Eightfold's account list is in; see cli_build.md |
| JobPost signal | `td_` / `sig_` | |
| Company segments | Tier 1 / Needs Review / Activation | |
| White-space workflow | | |
| White-space routine | | |

MCP task IDs from this build, for read-back from the Clay UI:

| Task | What |
|---|---|
| `mcp-task_0tmylr6NVb7s2aZo24N` | healthcare identity search + enrichment on 5 entities |
| `mcp-task_0tmylt75G9ot9XtEJZ5` | insurance / FS identity search + enrichment on 3 entities |
| `mcp-task_0tmyltdGWZhQXekrvWo` | semis / manufacturing identity search + enrichment on 3 entities |
| `mcp-task_0tmylv0kUPqU9xogsTR` / `mcp-task_0tmylvyxywZicSV2t5Z` / `mcp-task_0tmylwig6ikx2ZBxjJ3` | talent-leader searches by domain, three verticals |
| `mcp-task_0tmylxkrUcah3HbRiKK` | talent-leader search pinned by LinkedIn URL (10 accounts) |
| `mcp-task_0tmym4oNdoEKc5TZbbY` / `mcp-task_0tmym507S6msUvWFkBc` | headcount-growth band searches (+3% / -3%) |
