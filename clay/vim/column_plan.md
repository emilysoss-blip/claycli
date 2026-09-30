# Vim Enterprise GTM Engine — Clay build spec

Three builds, one table lineage. Build 1 produces the account universe; Build 2 only
ever runs against rows Build 1 has already qualified; Build 3 reads the same rows and
pushes them outward. Nothing in Build 2 or 3 re-derives an account — if a definition
needs to change, it changes in Build 1 and everything downstream moves on the next run.

That is the whole architectural claim: **one continuously updated source of truth instead
of three ad-hoc tables.**

All data currently in `data/vim_*.csv` is **sample data** — see `docs/vim-poc.md`. The
column plan below is written against the real HubSpot export.

---

## Build 1 — Enterprise Account Intelligence + CRM Cleanup

The hero build. Six stages. Stage 3 is a gate, not a step: nothing downstream is
trustworthy until it passes, and it is the stage that can silently corrupt everything.

### Stage 1 — Pull the HubSpot company universe into an Audience

| | |
|---|---|
| Source | HubSpot Companies object, full sync (not a saved view) |
| Key | `crm_record_id` |
| Columns in | `crm_name`, `domain`, `crm_owner`, `lifecycle_stage`, open-deal flag, `last_activity_date` |
| Credits | None |
| Failure mode | Syncing a saved view instead of the object. Duplicates and junk records are exactly what is being measured, so filtering them at import destroys the result. |

Pull **everything**, including records with no domain. The unresolvable tail is a
finding, not noise to be dropped.

### Stage 2 — Normalize the name, resolve the company

| | |
|---|---|
| Columns out | `normalized_name`, `clay_company_id`, `linkedin_company_url` |
| Credits | 1 company search per record |
| Failure mode | Treating the normalized string as the identity. |

Normalization is deterministic and cheap — lowercase, strip parentheticals and legal
suffixes, expand the CRM's abbreviations (`Hlth` → `Health`, `Pln` → `Plan`, `Ntwk` →
`Network`), drop trailing region qualifiers (`— OH`, `— Houston`). It is implemented in
`build/seed_vim_accounts.py:normalize()` and is worth reading, because it is also worth
distrusting: in the sample set it collapses 8 of 11 duplicates and **misses 3**. One copy
pluralizes "Physician", and no amount of string work fixes that.

So resolve to a **Clay Company ID** and dedupe on the ID. Name normalization narrows the
candidate set; the ID decides.

### Stage 3 — Dedupe (the gate)

| | |
|---|---|
| Columns out | `dedupe_status`, `duplicate_of`, `matched_on`, `dedupe_reason` |
| Credits | None (operates on stage 2 output) |
| Failure mode | Deduping on the domain. |

Four outcomes, and all four have to exist or the pass is lying:

| Status | Rule | What happens to it |
|---|---|---|
| `canonical` | Highest-engagement record for a Company ID | Survives, carries the enrichment |
| `duplicate` | Same Company ID as a canonical record | Collapsed, activity merged into the canonical |
| `merge_candidate` | Same domain, one hierarchy level too deep — a service line, a clinic site | Merged as an activity, not kept as a company |
| `unresolved` | No domain and no Company ID | **Held for a human.** Never auto-merged |

**Do not dedupe on the domain.** In the sample set, `harborviewhp.org` carries both
Harborview Health Partners and Harborview ACO LLC — a separate legal entity, with its own
VBC leadership, that holds the REACH contract. A domain-based dedupe deletes the row that
decides whether VBC tooling gets bought. Same domain is a *candidate*, never a verdict.

The two `unresolved` rows are the honest output. `meridian mutual (do not use)` matches a
canonical record on normalized name and record owner and nothing else; `Unknown — web
form 4/12` matches nothing at all. Guessing a parent for either is how bad hierarchy data
gets created, and bad hierarchy data is worse than none because it routes confidently.

### Stage 4 — Resolve the hierarchy

| | |
|---|---|
| Columns out | `hierarchy_level`, `parent_org_name`, `parent_domain`, `ultimate_parent_name` |
| Credits | Company enrichment per canonical record + Claygent where the parent is not in the graph |
| Failure mode | Trusting the CRM's parent field. |

Levels: `Ultimate parent` · `Subsidiary` · `Site` · `Standalone` · `Unresolved`.

Four structures this has to get right, all of them present in the sample set and none of
them inferable from a domain:

1. **Different domain, same parent.** Northmark Medical Group (`northmarkmedicalgroup.com`)
   under Northmark Health System (`northmarkhealth.org`). Survives dedupe correctly and is
   still not a separate sale — same Epic instance, same signing authority.
2. **Same domain, different entity.** Harborview ACO LLC. Kept, not merged.
3. **Payer and provider under one parent.** Cascade Valley Health owns both a Cerner
   provider estate and Cascade Valley Health Plan. The same executive is on both sides of
   the referral, which changes who you sell to and what you sell.
4. **A parent the CRM cannot know about.** Ridgeline Community Health sits in HubSpot as an
   unrelated parent account with its own owner. It was acquired. Nothing in the CRM will
   ever say so — only the M&A signal in Build 2 reparents it, which is why Build 2 feeds
   back into Build 1 rather than just consuming it.

Reparent on **close**, not on announcement. Announced deals fail state review and closing
runs 12–18 months.

### Stage 5 — Healthcare enrichment

| | |
|---|---|
| Credits | The expensive stage. Rows × data points, canonical records only |
| Failure mode | Running it before stage 3 finishes |

Run this **after** the gate, never beside it. Enriching 44 records instead of 32 pays for
duplicates; enriching before the hierarchy resolves attaches subsidiary data to a parent.

| Column | Source | Confidence to expect |
|---|---|---|
| `org_type` | Claygent + classification against the ICP taxonomy | High |
| `ehr_primary`, `ehr_secondary` | Tech-stack enrichment, Claygent on the newsroom | High for Epic and Cerner, **Low for alliances** |
| `ehr_confidence` | Derived — agreement across sources | — |
| `providers_est` | Claygent on the provider directory and CMS NPI data | Medium-high |
| `lives_covered_m` | CMS enrolment files (payers), plan filings | High for MA, medium commercial |
| `sites_est` | Provider directory | Medium |
| `hq_state`, `region` | Company enrichment | High |
| `vbc_model` | Claygent on contracts, CMS participant lists | Medium |
| `counterparties` | Claygent on both sides' newsrooms, cross-checked within the universe | Medium |

**`employee_count` is not organization size in healthcare**, for the same reason it was
not airport size in the sibling project: a system employs a small fraction of the
clinicians who practise on its site, and an alliance employs almost none of them. Use
`providers_est` and `lives_covered_m`. Do not let `employee_count` into the ICP score.

`ehr_primary` on a multi-EHR alliance is the field most likely to be wrong and most likely
to be believed. Keystone Health Alliance is 165 sites with no single instance; the right
value is `Mixed` with `ehr_confidence = Low`, not a guess at the most common one.

### Stage 6 — ICP score and tier

| | |
|---|---|
| Columns out | `icp_score`, `icp_tier`, `icp_reason` |
| Credits | None |
| Failure mode | A score with no stated reason |

Bands: **Tier 1** ≥ 85 · **Tier 2** 70–84 · **Tier 3** 50–69 · **Out of ICP** < 50 ·
**Unscored** where the hierarchy is unresolved.

Inputs, in the order they matter: risk position (`vbc_model`) → scale
(`providers_est` / `lives_covered_m`) → stack (`ehr_primary`, `ehr_confidence`) →
structure (does it sign for itself?) → counterparty overlap inside the universe.

Every score carries an `icp_reason` in one sentence. A tier nobody can explain gets
overridden by whoever is loudest in the pipeline review, and then the engine is decoration.

Two rows to check the scoring against: Evergreen Digital Health resolves perfectly and is
**out of ICP** — a vendor, not a buyer, so partner motion rather than pipeline. Rio Grande
Family Care is a clean record, 46 providers, no risk contract: also out, and also worth
suppressing from paid audiences in Build 3 so it does not consume budget.

**Output:** the Vim Enterprise Account Universe — who to sell to, which health system they
belong to, what EHR they run, and how valuable they are, maintained continuously rather
than rebuilt per campaign.

---

## Build 2 — Enterprise Buying Committee + Signals

Runs only against Build 1's Tier 1 rows. In the sample set that is 11 accounts out of 32
organizations out of 44 CRM records — a 4× reduction in what gets researched, which is
where the credit budget comes from.

### Stage 7 — Source the committee

| | |
|---|---|
| Key | `account_crm_id` from Build 1 |
| Credits | Contact search + enrichment per seat |
| Failure mode | Sourcing by seniority instead of by function |

Eight functions, and the committee differs by organization type rather than by size:

| Organization type | Economic buyer usually sits in | Also required |
|---|---|---|
| Health system | CIO / IT, or Population Health where downside risk is held | CMIO, clinical transformation, VBC |
| Payer | Network & contracting **and** IT, jointly | Provider data, payment innovation, product |
| VBC enabler | CTO or CMO | Network performance, analytics, payer partnerships |

Three rules that come out of the sample committees:

1. **Two economic buyers is normal on the payer side.** At Meridian Mutual, network spend
   is a larger line than IT's, so the SVP of Network Management co-signs. Pitching IT alone
   pitches the smaller budget.
2. **Source the gatekeeper on purpose.** Harborview's Director of Epic Applications will
   ask why this is not an Epic module. He is not a technical buyer and he can stop the deal;
   the answer belongs in writing, early, whether or not he is in the room.
3. **The best seat is often the newest one.** Lakeshore's VP of the Integration Management
   Office exists only because of an acquisition, with a funded mandate and a deadline. No
   title-seniority filter would rank that seat first.

Expect roughly 4 in 5 seats to be net-new to the CRM (45 of 55 in the sample). That ratio
is the clearest measure of what the build adds, so record it on the first run.

### Stage 8 — Signal detection

Dictionary: `data/vim_signals.csv`. 18 signals across hiring, technology, partnership, M&A,
regulatory, programme, engagement and risk, each with the detection method, the committee
function it routes to, a refresh cadence, and — the load-bearing column — the false
positive that makes it worthless if you fire on it blind.

| | |
|---|---|
| Credits | Job-change monitoring per committee contact, job-posting enrichment per account, Claygent per newsroom sweep |
| Refresh | Daily for engagement, weekly for hiring and partnership, monthly for tech stack, quarterly for regulatory lists |
| Failure mode | Scoring signal volume |

Three signals are Critical and reliably fire an action: a **new CIO** (re-opens every
vendor decision, and the only signal that resets a lost deal), a **new VBC or
population-health leader** (arrives with a mandate and a budget), and an **EHR migration
with a named go-live** (the only window when integration budget is uncontested).

The false-positive column is not garnish. An interim CIO promoted from inside changes
nothing. "Exploring options" is not a migration. A staffing agency reposting one
requisition across four boards is one requisition. A leakage phrase in a job description
that has been reposted for two years is not a programme. Every one of these looks like a
buying signal in a dashboard.

**Never score on signal count.** Three weak signals are not one strong one. In the sample
output the top-ranked account has three and the second-ranked has three, but the ranking is
driven by a dated deadline in each case, not by the tally.

### Stage 9 — The Account Agent

Prompt and validation plan: `clay/vim/account_agent_prompt.md`. Output:
`data/vim_account_agent.csv`.

Three inputs the CRM cannot combine on its own — resolved structure from Build 1, external
signals from stage 8, internal history from HubSpot (stage, owner, last activity,
engagement by seat) — and one output per Tier 1 account: `why_now`, `recommended_action`,
`entry_seat`, `channel`, `confidence`, `what_would_change_it`.

Two constraints on the agent, both enforced in `build/seed_vim_agent.py`:

- **An action must name a seat.** A recommendation with no person to take it to is a
  sentiment, and the assertion fails the build if the two disagree.
- **Every row carries a disconfirming check.** `what_would_change_it` states what would
  make the verdict wrong. This is what makes the output arguable in a pipeline review
  rather than oracular.

And the agent must be allowed to return nothing. Two of the 11 sample rows recommend **no
action this cycle** — Northmark, where the only movement is engagement from a resident with
no role in the decision, and Summit Ridge, a genuinely good account with no signal. An
agent that always finds a reason to act is a random number generator with good manners.

**Output:** which enterprise accounts changed, who matters there, and why someone should
act now — continuously, instead of a rep manually researching a 5,000-provider system.

---

## Build 3 — Dynamic Enterprise Ad Audiences

The before/after. Today: enrich people → export CSV → hand to marketing → someone uploads
it to LinkedIn or Meta, and the list is stale the day after it is built. After: the segment
is a query over Build 1 and Build 2, and it syncs on its own.

### Stage 10 — Define segments as rules

Definitions: `data/vim_ad_segments.csv`. Six segments, each with an **entry rule, an exit
rule, and a destination.** The exit rule is the half that CSV uploads do not have, and it
is the reason the audience decays.

| | |
|---|---|
| Credits | Identifier enrichment per person (email for Meta, profile for LinkedIn) |
| Refresh | Nightly where the rule reads a CRM field, weekly where it reads an enrichment |
| Failure mode | One audience for the whole ICP |

The payer committee and the provider committee get different segments because they get
different messages — VBC and network contracting on one side, IT and clinical
transformation on the other. Merging them halves the creative and wastes both.

`Epic estates` deliberately reaches into Tier 2, where committees have not been sourced
yet: 7 accounts, 4 with a committee. The `accounts_with_committee` column exists to keep
that gap visible rather than buried in a total.

### Stage 11 — Sync, and measure the right number

| | |
|---|---|
| Destination | LinkedIn (profile match) · Meta (hashed email) |
| Failure mode | Quoting the wrong match number to the customer |

Two different numbers, and the distinction matters in a pricing conversation:

- **`addressable_people`** — people who have the match key the destination needs. Counted
  from the data, and quotable.
- **`est_reachable`** — people the platform will actually serve. Derived on a flat assumed
  match rate (LinkedIn 65%, Meta 45%) because the true rate depends on what the platform
  holds. **Illustrative. Replace with observed rates after the first sync**, which is the
  first thing this build can be judged on.

Suppression is part of the build, not an afterthought: out-of-ICP rows (Evergreen, Rio
Grande) and closed-lost accounts are excluded by the entry rules, so budget stops flowing
to them the night the tier changes.

**Output:** targeting that updates itself as people enter and leave the segment, with no
CSV in the loop.

---

## Credit order, and what to run first

1. Stages 1–3 on the full HubSpot export. Cheap, and produces the CRM-cleanup number on
   its own — no enrichment required to say "44 records are 32 companies".
2. Stage 4 on canonical records only.
3. **Validate stage 5 on 5 rows before running 32.** Pick the hard ones deliberately: a
   mixed-EHR alliance (Keystone), a payer with no EHR at all (Meridian Mutual), a same-domain
   sibling pair (Harborview and Harborview ACO), a cross-domain subsidiary (Sierra Medical
   Foundation), and an unresolved row (the web-form record) to confirm it stays unresolved.
4. Stage 6, then stages 7–9 on Tier 1 only.
5. Stages 10–11 last. Nothing should be synced to an ad platform off an unvalidated tier.
