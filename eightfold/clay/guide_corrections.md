# Build guide vs. Clay's plugin docs

The Eightfold build guide's CLI commands, checked against
[`clay-run/agent-plugins`](https://github.com/clay-run/agent-plugins) at commit `a813258`
(Oct 6 2026, the same day the guide says it was checked). Live `--help` output is still the
authority. The CLI could not be installed in this environment, so nothing below was executed.

Four items need changing before the guide is pasted into a coding agent. Two of them are the
"corrections" the guide asks to have carried back into the Vim guide. Neither should be.

## Must change

### 1. Enrich-node results are at `$.result.<field>`, not `$.toolResult.result.<field>`

The guide (section 5) says: *"Enrich nodes wrap their Clay action result in a toolResult
envelope, so the action's fields are at $.toolResult.result.<field>, never at $.result.<field>."*

The plugin docs say the opposite, in three places:

- `clay/skills/workflows/data-passing.md`, "Output structure of enrich (tool) nodes": *"the
  Clay action's returned fields are under `result`, and its success flag is `success`, both at
  the top level ... address the action's fields under `$.result.*`"*
- the same file's worked example: `{ "sourceNodeId": "wfn_enrich_company", "sourcePath": "$.result.name" }`
- `clay/skills/workflows/SKILL.md`, `actions test`: *"action fields live under `.result` (use
  those for `$.result.<field>` wiring)"*

Wired the guide's way, every downstream reference resolves to nothing. Nothing errors, because
`graph validate` checks structure, not paths. **Use `$.result.<field>`, take the field name from
`outputParameters` in `clay workflows actions schema`, and do not carry this "correction" into
the Vim guide.**

### 2. Signal targeting: `segmentIds` is the input key

The guide (section 9) says: *"Signal inputs take input.table or input.audiences, not a
segmentIds array"*, and gives `--input '{"audiences":["<companyAudienceId>"]}'`.

`clay/skills/signals/SKILL.md` separates the two shapes:

- **What `get` returns:** `input.table` (`{ id, viewId }`) or `input.audiences`
  (`{ segmentIds, entityType }`), with `entityType` spelled `ACCOUNT` / `CONTACT`.
- **What you send:** *"`--input`'s `segmentIds` are ids from `clay audiences list`"*, and
  *"an update changing `segmentIds` does not disturb `filters`"*.

So `segmentIds` is the input key. The guide's `{"audiences": [...]}` matches neither shape.
Run `clay signals create --help`, which the skill calls *"the authority on each one's `--input`
shape"*, and copy the shape from an existing signal of the same type
(`clay signals get td_... | jq '.signal.inputs'`). **Do not carry this "correction" into the
Vim guide either.**

### 3. `runs test --trigger <csvTrigger> --limit 10` does not test 10 rows

The guide (section 12) runs the 10 → 50 sample as
`clay workflows runs test <workflowId> --trigger <triggerId> --limit 10`.

`clay/skills/workflows/testing.md`: `runs test --trigger` *"starts one run per record it
returns"*. `--limit` is documented for **audience segment** triggers only, *"pass `--limit`
(max 10)"*. For a CSV trigger the bounded path is a different command
(`clay/skills/workflows/csv-triggers.md`):

```bash
clay workflows triggers csv run <triggerId> --limit 10   # first 10 rows only
```

`--limit` *"always takes rows from the top of the file and has no offset"*, so the 50-row
pass is a **new file** of rows 11-60 linked with `csv upload` and run without `--limit`.
`csv run` is *"not idempotent"*: a retried timeout doubles the runs and the spend. Also,
`--limit 50` against a segment trigger is out of range (max 10).

### 4. Every run fails if the trigger is unwired

The guide does say *"wire the trigger to the first node before testing"*. Here is how it
fails if that step is skipped. `csv-triggers.md`: an unwired CSV trigger still accepts
`csv run` and returns a `batch.key`, *"but every row's run then fails with 'Workflow has no
initial node.'"* Put `clay workflows graph get` and a wiring check before the first
`csv run`, not after.

## Confirmed as written

| Guide claim | Plugin source |
|---|---|
| `clay signals get` takes `td_…` only; `sig_…` returns not_found | `signals/SKILL.md`, record table |
| Only `Active` or `Paused` signals can be toggled | `signals/SKILL.md` |
| `Custom` signals are app-only; not creatable from the CLI | `signals/SKILL.md`, `### Custom` |
| `NewHire` = person joined; `JobPost` = open role | `signals/SKILL.md`, type table |
| `audience_signal` triggers bind to the `sig_…` id | `workflows/SKILL.md`, triggers |
| CSV upload links the file but does not start a run | `workflows/csv-triggers.md` |
| CSV values arrive as strings | `workflows/csv-triggers.md`, "one string column per CSV header" |
| `clay routines create workflow <id> --name` | `routines/SKILL.md` |
| `clay audiences fields create --entity-type … --name … --data-type …` | `audiences/SKILL.md` |
| `clay searches query-mode reference / create / run` | `searches/SKILL.md` |
| `nodes test … --source-run <runId>`; `runs steps <workflowId> <runId> --status failed` | `workflows/testing.md` |
| A published workflow and a paused signal are separate controls | `workflows/publishing.md`, `signals/SKILL.md` |

## Worth adding

- **A created signal starts Paused** and spends nothing until `clay signals resume`. The guide
  resumes right after `get`. Check coverage first: *"a record with a missing, stale, or
  invalid URL is silently not monitored"*. On this cohort that is concrete. `commonspirit.org`
  and `kaiserpermanente.org` never return the parent (see `data/clay_match_quality.csv`), so a
  domain-watched `NewHire` signal on those two would watch the wrong records.
- **Job change and promotion signals ship with a default `confidence >= 90` filter.** Passing
  `--filter` replaces it rather than adding to it.
- **Topic-intent providers are fixed at creation.** `update` can change `topicIds` but not
  add or drop a provider. That makes the 6sense-overlap question (guide section 9) a decision
  to settle before `create`.
- **A native `scheduled` trigger type exists** (`workflows/SKILL.md`, triggers:
  `scheduled = triggerType, scheduleConfig`). The weekly white-space job in section 10 can
  likely use it instead of an external cron. `clay workflows triggers create --help` gives
  the `scheduleConfig` shape.
