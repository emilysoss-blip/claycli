# Airport Intelligence Table

An account foundation and Clay build spec for 50 airports, keyed on airport domain.

## What is here

```
data/airports.csv            50 rows, 25 columns - the account list
data/buying_centers.csv      87 rows - who actually signs, normalized out of the airport row
data/clay_match_quality.csv  47 rows - observed Clay match quality per enrichment domain
data/signals.csv             17 rows - aviation signal dictionary
clay/column_plan.md          the stage-by-stage build spec
clay/claygent_prompt.md      the research agent prompt + validation plan
build/*.py                   regenerates every CSV; edit these, not the CSVs
```

Regenerate everything:

```bash
python3 build/seed_airports.py && python3 build/seed_buying_centers.py \
  && python3 build/seed_clay_match.py && python3 build/seed_signals.py
```

## The list

50 airports: 31 North America, 10 Europe, 4 Asia-Pacific, 3 Latin America, 2 Middle East.
Tiered 19 / 21 / 10 (Tier 1 = 60M+ passengers **or** 3+ independent buying centers).

Coverage is deliberately weighted to North America, where airport procurement is most public.
The list is a starting point, not a fixed universe — `build/seed_airports.py` is a plain list
of tuples, so swapping rows in or out is a one-line edit.

## Separating the authority from the terminal operators

This was the main ask, and it is where the structure earns its keep. The airport is the
account; the buying center is who signs. They are not the same, and at 9 of the 50 airports
they are not even the same company.

87 buying centers across 50 airports:

| Role | Count | Owns the budget for |
|---|---|---|
| Airport-wide authority | 50 | Airport-wide network and OT, common-use systems, AODB, airport-wide cyber, capital delivery |
| Parent authority (multi-asset) | 20 | Enterprise IT and security standards, group procurement, vendor master agreements |
| Terminal operator | 15 | In-terminal IT, baggage, passenger processing, terminal ops and cyber |
| Handling / subsidiary operator | 2 | Ground handling, cargo, ramp and resource-management systems |

27 of the 50 airports have more than one. The most split:

- **JFK — 6.** PANYNJ owns the airport-wide estate and the redevelopment program. JFKIAT
  (T4), New Terminal One (T1) and JFK Millennium Partners (T6) each buy their own passenger
  systems, baggage and terminal IT. Three separate paths, plus the authority, plus the parent.
- **HND — 4.** Structurally the hardest row. MLIT owns the airside, Japan Airport Terminal Co.
  runs the domestic terminals, TIAT runs the international terminal. There is no single
  airport-wide IT owner to sell to.
- **LGA — 3.** Terminal B is a full private concession (LaGuardia Gateway Partners) with its own
  CEO and procurement. Terminal C is Delta's. The authority keeps AirTrain, roadways and
  central systems.
- **EWR — 3.** Terminal A is PANYNJ-built but **operated by Munich Airport NJ LLC**, a
  Flughafen München subsidiary. The Terminal A buyer is a German airport operator.
- **DXB — 3.** Dubai Airports is a comparatively thin asset owner; Emirates and dnata hold much
  of the passenger and baggage estate.

Two routing rules fall out of this:

1. **Dedupe at the parent.** PANYNJ is one buying center behind JFK, LGA and EWR. MWAA is one
   behind IAD and DCA. Treating those as five accounts means five reps mailing the same CIO.
2. **Authority coverage never implies terminal coverage.** An authority-level contract does not
   reach a concessionaire's terminal.

## What Clay actually returned

Every one of the 47 unique enrichment domains was run through Clay live. Results in
`clay_match_quality.csv`. Two findings changed the build:

**Domain-keyed enrichment fails on 14 of 50 rows.** 35 domains matched cleanly, 4 resolved to
the wrong company, 8 returned nothing. The 4 wrong ones are the hazard, because they succeed
silently: `panynj.gov` returns two stale stubs of 58 and 17 employees (one description
references a 2011 anniversary), and it backs the JFK, LGA and EWR rows. `austintexas.gov`
returns the City of Austin, the public library and the water utility before the airport.
Fix: pin `linkedin_company_url` per row before enriching anything.

**`employee_count` is not airport size — on 31 of 47 domains.** Contradictory (BWI: 67
employees, size band "10,001+"), wrong scope (`portseattle.org` returns 2,096 for the whole
Port including the seaport), or structurally undercounted, because an authority employs a
small fraction of the people on its site. Zurich's own page says it: ~1,700 direct staff,
~27,000 across 280 partner firms. Use department-level headcount and passenger volume instead.

Clay also corrected two of my own rows: Munich Airport's US subsidiary operates EWR Terminal A
(I had EWR down as having no private operator), and LAWA only resolves on `lawa.org`, not
`flylax.com`.

## Data confidence

| Field group | Confidence | Note |
|---|---|---|
| Domains, names, IATA/ICAO, geography | High | |
| Operator model, authority, parent, terminal operators | High | The structural core; hand-built and cross-checked against Clay. |
| Associations, publications, procurement systems | Medium-high | Association membership is stable; verify procurement portal URLs at first use. |
| `annual_passengers_m_2024_est` | **Medium — seed only** | Rounded estimates for tiering. Re-verify before quoting externally. |
| Clay `employee_count` | **Low on 31 of 47 domains** | See above. |
| Newsroom, procurement and initiative URLs | Not populated | Deliberately left to Claygent rather than guessed. |

URL-discovery columns are empty by design. Fabricating plausible-looking deep links would have
made the table look more finished and been worse — Claygent resolves them at run time.

## Not done

- **Stage 2 enrichment values are not in this repo.** Enrichment was dispatched to Clay against
  10 Tier 1 accounts and accepted, but `get-task-context` returned `Internal error` on every
  read-back in this session. Values are in the Clay workspace under task
  `mcp-task_0tm35ji7wdtQyooSwrr`.
- **The Claygent column has not been run.** The prompt is written and the validation plan is
  specified; running 50 rows costs credits and should follow the 5-row validation.
- **No contacts sourced.** `buying_centers.csv` carries target titles per role, which is the
  input to contact search, not its output.

---

## Also in this repo

[`docs/vim-poc.md`](vim-poc.md) — the **Vim Enterprise GTM Engine** POC: three connected
builds (account universe and CRM cleanup, buying committees and signals, dynamic ad
audiences), with a sample-data account universe, a stage-by-stage Clay spec in
`clay/vim/`, and a browsable view at `vim-enterprise-gtm-engine.html`.
