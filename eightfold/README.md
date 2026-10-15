# Eightfold: demand-gen signal engine (POC build)

This is the Eightfold version of the airport intelligence table, built from the *Native-First
Clay CLI Workflow Build Guide*. It tiers an account book with rules, finds new talent leaders,
and writes why-now briefs that cite their evidence. It keeps the parent company and the
division that actually hires as separate records.

It runs on a **stand-in cohort of 30 US enterprise parents**, not Eightfold's Salesforce
export, which is not in this repo. The cohort covers the three verticals in the guide's
appendix: healthcare, insurance and financial services, and semiconductors and advanced
manufacturing. Every count below comes from live Clay calls made on 2026-10-15 through the
Clay MCP against workspace 91642 (Clay Demos GTM). Raw captures are in `data/raw/`.

## What is here

```
data/accounts.csv            30 parents (guide section 3 schema; CRM fields blank, never inferred)
data/divisions.csv           69 hiring entities: 51 in scope, 18 suppressed (stale, wrong-company, non-employee)
data/clay_match_quality.csv  42 domains: what Clay returns when you enrich by each one
data/tiered_accounts.csv     deterministic tiering, tri-state checks, score_version on every row
data/talent_leaders_public.csv  68 people Clay returned (no names); 13 pass the rules gate, every rejection has a reason
data/why_now_public.csv      one templated brief per account; signal-led and fit-led reported separately
data/signals.csv             each Eightfold ask -> the native Clay signal type that answers it
data/raw/                    every Clay company response this build used, with task IDs (people captures stay local)
build/*.py                   regenerates all of the above; edit these, not the CSVs
build/test_engine.py         the unit checks guide section 7 asks for, plus the leader gate (22 tests)
clay/runbook.md              the CLI build, step by step, with the corrections applied
clay/cli_build.md            what was built in Clay: workflow and node IDs, 10-account test, findings
clay/nodes/                  code-node source, generated from build/tiering.py by build/node_code.py
clay/guide_corrections.md    four commands in the guide that would break the build, with plugin-doc citations
clay/claygent_fallback.md    eligibility gate, prompt, output schema, reconciliation rules
```

Regenerate everything:

```bash
cd eightfold
python3 build/seed_accounts.py && python3 build/seed_clay_match.py && python3 build/tiering.py \
  && python3 build/leaders.py && python3 build/why_now.py && python3 build/seed_signals.py \
  && python3 build/make_page.py && python3 build/test_engine.py
```

The browsable view is `../eightfold-demand-gen-engine.html`.

## Named data stays local

This repo is public, so the people-level data is gitignored. That covers names, LinkedIn
URLs and locations in `data/raw/clay_talent_leaders_*.json`, `data/talent_leaders.*` and
`data/why_now.*`. Committed instead:

- `data/talent_leaders_public.csv`: every row the gate saw, with title, employer, start month,
  persona, level and the qualification reason, but no name, URL or location.
- `data/why_now_public.csv`: the same briefs, naming the role rather than the person.
- `eightfold-demand-gen-engine.html`: built from the public files.

With the raw captures present locally, `python3 build/make_page.py --private` writes the
named version to `eightfold-demand-gen-engine.private.html`, which is also gitignored. On a
fresh clone, `leaders.py` skips and the public files are the record.

## Results

### 1. Identity: 8 of 30 parents cannot be enriched by domain

Eightfold sells to companies where one domain covers many hiring entities, and the talent
leader often sits in the division. The guide says not to collapse them. Here is what that
looks like in Clay's data.

| Domain | What Clay returns | Fix |
|---|---|---|
| `jhu.edu` | 26+ entities: university, schools, centres, a misspelled stub | LinkedIn URL per entity |
| `hopkinsmedicine.org` | 8+ entities: health system, hospitals, School of Medicine, health plan | LinkedIn URL per entity |
| `commonspirit.org` | 10+ member hospitals, **never the parent**; 8 of 10 tagged `10,001+` on 114-1,090 employees | `linkedin.com/company/commonspirithealth` resolves (48,637, `commonspirit.careers`) |
| `kaiserpermanente.org` | two placeholder pages tagged "Blockchain Services", no headcount | `linkedin.com/company/kaiser-permanente` resolves (139,271, `kp.org`) |
| `marshmclennan.com` | "Celedinas Insurance Group", 31 employees. Wrong, silently | parent renamed to Marsh, on `marsh.com` |
| `mercer.com` | regional pages only; the Mercer LinkedIn page itself now reads "Marsh People Solutions" (96) | treat Mercer as a Marsh division; confirm in Salesforce |
| `ge.com` | legacy page (95,424) whose own text says content moved to GE Aerospace and GE Vernova | never enrich on it |
| `gevernova.com` | the parent, plus four inactive legacy pages | suppress the four |

Across 42 domains: 23 clean, 5 clean apart from stale pages, 9 shared between real hiring
entities, and 5 unusable as-is. Pinning the LinkedIn URL fixed both parents that domain
search never found. `accounts.csv` carries the identifier to use in `enrichment_identifier`.

Size bands contradict headcount often enough to matter: KLA's revenue band is `1M-5M`, Cigna
Healthcare's is `75M-200M`, and Honeywell's page says 50,000+ employees while
`employee_count` says 129,754. Tiering uses `employee_count` with these flagged.

### 2. Talent-leadership signal: 68 returned, 13 qualify, at 9 of 30 accounts

People search: CHRO / CPO / Head of TA / Head of Talent Intelligence / People Analytics who
started in the last 18 months. `leaders.py` then applies rules. Rejection reasons (a person
can have several):

| Reason | People |
|---|---|
| manager / lead level | 33 |
| outside the US (below executive level) | 33 |
| regional scope in the title | 14 |
| assistant, analyst or coordinator | 4 |
| HR generalist, HRBP or HR operations: an influencer, not a trigger | 6 |
| not an HR persona (e.g. a marketing AVP) | 3 |
| probable duplicate profile (same person, two LinkedIn URLs) | 1 |

Qualified, strongest persona first:

| Account | Entity | Title | Started |
|---|---|---|---|
| Honeywell Technologies | parent | SVP, Chief Human Resources Officer | 2026-07 |
| Honeywell Technologies | parent | Chief Talent Officer, VP Global Talent | 2026-04 |
| GE HealthCare | parent | Chief Talent Officer (based in Greece; enterprise exec kept) | 2026-04 |
| Elevance Health | **Carelon** | CHRO Carelon | 2025-12 |
| UnitedHealth Group | **UnitedHealthcare** | SVP HR (Chief People Officer), UHC Operations | 2025-09 |
| Elevance Health | parent | EVP, Chief Human Resources Officer | 2025-08 |
| Johns Hopkins | **University** | VP and Chief Human Resources Officer | 2025-06 |
| Lockton | parent | Head of Talent Intelligence | 2026-01 |
| JPMorganChase | Asset & Wealth Mgmt | Head of People Analytics Advisory | 2026-01 |
| CVS Health | parent | VP, Head of Talent Acquisition | 2026-03 |
| Lockton | parent | SVP - Senior TA Manager (flagged: banded title) | 2026-06 |
| UnitedHealth Group | **Optum** | VP Talent Acquisition | 2025-12 |
| HCA Healthcare | parent | Director, TA Technology (HR-tech persona) | 2026-02 |

Three of the 13 sit in a division, not on the parent page: Carelon, UnitedHealthcare and
Optum. Johns Hopkins' CHRO belongs to the University, a separate employer from Johns Hopkins
Medicine. A parent-only build would route all four to the wrong owner.

Under the proposed policy (task only within 90 days of start), **one account creates a task
today: Honeywell**. Its new CHRO started in July, three months after a new Chief Talent
Officer and after the company's separation. The other 8 signal-led accounts get a brief but
no task. The 21 without a qualified leader read "Fit-led account; no verified recent
trigger." and nothing more.

Against the guide's appendix sample:
- CVS Health's VP, Head of Talent Acquisition now has a start date (2026-03). The appendix
  had it as unconfirmed.
- CVS Health's HR business partner to the CHRO is an influencer under the gate, not a trigger.
- Flex's Director of TA (Executive & Commercial) is below trigger grade unless Eightfold wants
  TA directors in. That is one line in `leaders.py`.
- Johns Hopkins had none in the appendix's window. The LinkedIn-pinned search on the
  University page returned its CHRO, 16 months in role.

### 3. Tiering: all 30 land in Review, which is correct

Every account passes the three criteria that are known: target vertical, 10,000+
employees and US headquarters, for 55 of 100. The two that decide the tier, open
requisition volume and a supported or displaceable HCM, are **unknown** on every row. The
native enrichment that would fill them was dispatched (below), but no values could be read
back. So every account is in Review, with `fit_best_case` at 100 and
`missing_required_fields = open_reqs;hcm`. Unknown is not treated as a no.
`test_engine.py` checks that a confirmed unsupported HCM scores 80 (Tier 1), while an
unknown one goes to Review.

The criteria in `tiering.CRITERIA` are a **calibration set**: industry 25, headcount 20,
open reqs 25, HCM 20, geography 10, Tier 1 at 80. They are not Eightfold's ICP. Eightfold's
demand gen team still needs to agree them. Intent (6sense) and engagement (Marketo) are carried through
as separate fields and never enter fit. Neither is connected yet.

### 4. Headcount growth (3 months)

Read through native search filters, because enrichment read-back failed. The result is a
band, not a ratio.

- **Up 3%+:** Applied Materials, Optum, GE Vernova, GE Aerospace, Micron, Lockton, Lam
  Research, Evernorth, Analog Devices, JPMorganChase
- **Down 3%+:** Marsh
- **Everyone else:** `flat_or_unreported`. That is not the same as flat.

Both filters also returned 25 regional, inactive or stub pages (e.g. "UnitedHealth Group us", 36 employees)
that inherit the parent's `10,001+` band. Only entities in `divisions.csv` count.

## Corrections to the build guide

Details and citations: [`clay/guide_corrections.md`](./clay/guide_corrections.md).

1. Enrich-node results are at **`$.result.<field>`**. The guide's `$.toolResult.result` path
   resolves to nothing, silently.
2. Signal `--input` uses **`segmentIds`**. The guide's `{"audiences": [...]}` matches neither
   the input shape nor the read-back shape.
3. `runs test --trigger <csvTrigger> --limit 10` runs **every row**. The bounded path is
   `clay workflows triggers csv run <triggerId> --limit 10`.
4. An unwired CSV trigger accepts `csv run`, then fails every row.

The guide asks for #1 and #2 to be copied into the Vim guide as corrections. Don't.

## Data confidence

| Field group | Confidence | Note |
|---|---|---|
| Parent / division structure, roles, suppression | High | Every entity was returned by Clay on 2026-10-15; roles are hand-assigned from page text |
| Domain match class | High for what was seen | Counts are lower bounds where paging stopped (`count_is_lower_bound`) |
| `clay_employee_count` | Medium | Contradicted by its own size band on several rows; see `divisions.csv` notes |
| Talent leaders: name, title, start month, LinkedIn URL | Medium-high | From Clay people data; start dates are month-precision; validate employment before outreach |
| Headcount growth band | Medium | Derived from filter membership, not a stored ratio |
| Open reqs, HCM | **None** | Dispatched, not read back |
| CRM state (customer, opportunity, owner, suppression) | **None** | Not in this repo; never inferred |

Search results also carried Audiences fields from the Clay Demos workspace (other demos'
tiers and scores). None of it is used, and none of it is Eightfold's data. It also shows the
decay problem the JobChange watch exists for: stale company names on records, and one
qualified TA leader's record carrying an email at a previous employer.

## Not done

- **Salesforce export.** The cohort is a stand-in. The 10-row test set in
  `clay/runbook.md` needs a known customer, an open opportunity and a suppressed account from
  the real export.
- **Enrichment values.** Open Jobs, Tech Stack and Headcount Growth were dispatched on 11
  parents and accepted. `get-task-context` returned `Internal error` on all six read attempts.
  This is the same failure the airport build hit. The values should be in the Clay workspace
  under the task IDs in `data/raw/clay_enrichment_dispatch.json`.
- **The rest of the CLI build.** The workflow now exists in Clay and passed a 10-account test
  (`clay/cli_build.md`, results in `data/cli_test10_results.csv`). It is not published, and
  no signal, segment or Audiences field has been created yet.
- **Contacts.** No emails were looked up or stored. Person enrichment and email validation
  come after the qualified list is reviewed (guide section 8).
- **Claygent.** Specified, not run. Nothing in this build used AI to fill a field.
