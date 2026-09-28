# Clay table build: Airport Intelligence

One table, **one row per airport**, primary key `airport_domain` (50 rows).
Two companion tables handle the things that do not fit one-row-per-airport.

| Table | Grain | Rows | Why it is separate |
|---|---|---|---|
| `airports.csv` | Airport | 50 | The account list. `airport_domain` is the key. |
| `buying_centers.csv` | Buying center | 87 | An airport can have up to 6 independent buyers. Flattening them onto the airport row would either lose them or duplicate the airport. |
| `clay_match_quality.csv` | Enrichment domain | 47 | Which domains Clay can actually resolve. Governs whether enrichment on a row is trustworthy. |
| `signals.csv` | Signal type | 17 | Shared signal dictionary, referenced by all rows. |

---

## Stage 1 - Foundation (built, no credits)

Written by `build/seed_airports.py`. 23 columns, all populated.

| Column | Notes |
|---|---|
| `airport_domain` | **Primary key.** Passenger-facing domain. |
| `airport_name`, `iata_code`, `icao_code` | `iata_code` is the real disambiguator — see caveat below. |
| `city`, `country`, `region` | |
| `annual_passengers_m_2024_est`, `passenger_volume_tier` | Seed estimates for tiering. Re-verify before quoting. |
| `operator_model` | 13 distinct models, from "municipal department" to "private BOT concession". Drives the whole sales path. |
| `airport_authority_name` / `_domain` | The airport-wide authority. |
| `parent_authority_name` / `_domain` | Blank where the authority *is* the top of the tree. |
| `terminal_operators` | `Name (Terminal) \| domain`, semicolon-separated. |
| `has_separate_terminal_operators`, `buying_center_count` | Derived. |
| `enrichment_domain`, `enrichment_domain_differs` | **The corporate domain to enrich on.** Differs from the key on 13 of 50 rows. |
| `systems_owner_note` | Free text: who actually owns airport IT here. The most useful column for a rep. |
| `trade_associations` | Per-country, not per-region. |
| `airport_publications` | 8 titles, region-specific. Feeds the Claygent prompt. |
| `procurement_system` | The named portal. Feeds Claygent tier 1d. |
| `primary_language` | 10 non-English rows need local-language search. |
| `account_tier` | Tier 1 if 60M+ pax **or** 3+ buying centers. 19 / 21 / 10. |

### Two caveats that will bite

**`airport_domain` is unique, but it is not one-domain-one-airport.** `flychicago.com` is ORD
*and* MDW; `fly2houston.com` is IAH, HOU *and* EFD. Join on `iata_code`, not domain, or ORD
work will land on Midway.

**`aena.es` has no airport-level entity at all.** Aena runs 46 Spanish airports from one
organization. The MAD row is really "Aena network, MAD as flagship" — there is no MAD CIO to
find. Treat it as a network account or drop it.

---

## Stage 2 - Marketplace enrichment

Run against `enrichment_domain`, **not** `airport_domain`.

| Column | Source | Notes |
|---|---|---|
| `linkedin_company_url` | Clay company match | **Pin this manually first.** See Stage 2a. |
| `employee_count` | Clay / LinkedIn | Unreliable here — see below. |
| `department_size_it`, `department_size_security` | Headcount by department | The number that actually matters. |
| `tech_stack` | BuiltWith + PredictLeads | Web-facing only; will not see AODB, BHS or CUPPS. |
| `open_roles_total`, `open_roles_cyber`, `open_roles_infrastructure`, `open_roles_passenger_systems`, `open_roles_baggage`, `open_roles_biometrics`, `open_roles_facilities` | Clay Open Jobs + keyword filter | Split by keyword; the aggregate count is not a signal. |
| `recent_news` | Clay Recent News | Broad. Claygent is the precise instrument. |
| `latest_funding`, `investors`, `ownership_change` | Clay funding data | Only meaningful for the 8 private/concession rows. |
| `job_changes_90d` | Clay job-change signal | The highest-value native signal on this list. |

### Stage 2a - Pin the LinkedIn URL before enriching anything

Non-negotiable. Live Clay runs against all 47 enrichment domains returned:

- **35 clean matches**
- **4 satellite-only** — the domain resolves, but to the wrong company
- **8 no match**

Which means **14 of 50 airport rows cannot be enriched by domain alone**:
`AMS, AUS, BOG, CDG, EWR, HND, IST, JFK, LGA, MCO, MIA, MUC, SYD, YYZ`.

The satellite matches are the dangerous ones, because they succeed:

| Domain | What Clay returns | What you wanted |
|---|---|---|
| `panynj.gov` | Two stale stubs (58 and 17 employees; one describes a 2011 anniversary) | Port Authority of NY & NJ — **affects JFK, LGA and EWR** |
| `schiphol.nl` | "Aviation Solutions" (18 people) and "Schiphol Real Estate" (71) | Royal Schiphol Group |
| `munich-airport.com` | "Munich Airport International" (245) and "Munich Airport NJ LLC" (119) | Flughafen München GmbH |
| `austintexas.gov` | City of Austin (8,992), Austin Public Library (280), Austin Water (534) | Austin-Bergstrom (226), which exists but is not the top match |

Enrich `panynj.gov` by domain and your three largest New York accounts attach to a dead page
with 58 employees. Nothing errors. Full detail and the fix per row in `clay_match_quality.csv`.

### Stage 2b - Do not use `employee_count` as airport size

**31 of 47 domains** returned a headcount that should not be trusted. Three distinct failures:

- **Internally contradictory.** BWI: `employee_count` 67, size band "10,001+". PHX: 336 vs "10,001+".
- **Wrong scope.** `portseattle.org` returns 2,096 for the whole Port (seaport, cruise, airport).
  `massport.com` 774 covers airports plus seaport plus cruise. `daa.ie` 2,407 spans Dublin,
  Cork, a global retail arm and a consultancy.
- **Structurally undercounted.** An airport authority employs a small fraction of the people on
  its site. Zurich's own page says it: ~1,700 direct staff, ~27,000 across 280 partner firms.
  Heathrow: 6,033 on the company page, 90,000+ working at the airport.

Use `department_size_it` and `department_size_security` instead, and treat
`annual_passengers_m` as the size proxy.

### Stage 2c - Enrichment dispatched in this build

Tech Stack, Open Jobs, Recent News, plus two custom research columns (*Airport Capital
Program*, *IT and Security Leadership*) were dispatched against 10 Tier 1 accounts: Heathrow,
Fraport, Dubai Airports, Changi, Aena, Gatwick, daa, LAWA, Incheon and Vancouver.

**The results are not in this repo.** Clay accepted the enrichment and reported it running,
but `get-task-context` returned `Internal error` on every read-back attempt in this session.
The values are in the Clay workspace under task `mcp-task_0tm35ji7wdtQyooSwrr` — read them
there, or re-run the enrichment from the UI.

---

## Stage 3 - Claygent research column

Full prompt, input mapping and validation plan in [`claygent_prompt.md`](./claygent_prompt.md).

Returns 21 structured fields per row. The two that matter most are
`owning_buying_center` and `owning_buying_center_type`: an initiative whose owner you cannot
name is not actionable, because you do not know who to call. `owning_buying_center` should
always be a value that appears in `buying_centers.csv` — that is the column's built-in check.

Validate on 5 deliberately hard rows (JFK, HND, MAD, AUS, BOG) before spending 50 rows of
credits.

---

## Stage 4 - Routing

Join `airports.csv` → `buying_centers.csv` on `airport_domain`, then prospect
`target_titles` at `buying_center_domain`. Two rules:

1. **Dedupe at the parent.** 20 rows carry a distinct parent authority. PANYNJ is one buying
   center behind three airports (JFK, LGA, EWR); MWAA is one behind two (IAD, DCA). Sequencing
   them as five accounts means five reps mailing the same CIO.
2. **Never assume authority coverage extends to a terminal.** 15 terminal operators on this
   list buy their own passenger systems, baggage and terminal IT. At JFK the authority owns the
   airport-wide estate while JFKIAT, New Terminal One and JFK Millennium Partners each buy
   their own. EWR Terminal A is operated by a Flughafen München subsidiary — the buyer there is
   a German airport operator, not the Port Authority.
