# Clay playbook: industrial contacts, trade-show lists, and the rail / people-mover expansion

Prospect profile: sells into mining, mills, and oil & gas today. Wants to (1) reach plant, mine
and operations managers who are thin on LinkedIn, (2) turn trade-show lists into reachable
prospects before and after events, and (3) open rail, airport people-mover and monorail accounts.

Everything below was tested live against the Clay workspace on 2026-11-11. Results are quoted
from those runs, not estimated.

---

## 1. Niche industrial contacts (plant, mine, operations managers)

### What was tested

One people search across 8 producers (Freeport-McMoRan, Newmont, Nucor, Cleveland-Cliffs,
Peabody, Vale, Rio Tinto, US Steel), titles similar to *Plant Manager / Mine Manager / Mill
Manager / Operations Manager / Site Manager*, US + Canada, capped at 3 per company.

| Result | Count |
|---|---|
| Site-level operators returned | 20 |
| Of which clearly plant/mine/mill-level (not HQ) | 15 |
| Work emails requested on a sample | 8 |
| Work emails found | **8 of 8** |

Representative rows: Plant Manager at Nucor Wire Products (Maryville, MO); Mine Operations
Manager, Peñasquito (Newmont); Rolling Mill Manager and Melt Shop Manager (Nucor); General
Manager, Copper Cliff Mine Complex (Vale); Plant Manager (Peabody, Washington, IN); Operations
Manager HBI (Cleveland-Cliffs, Dearborn).

### Why "they aren't on LinkedIn" is only half true

LinkedIn-derived search did find site managers at every major producer. The gap is at the
**site** level, not the company level: a 300-facility steelmaker has far more plant managers
than show up with a clean title. Two things close the gap.

**a. Search by site, not by HQ.** Clay people search filters on `location_city` /
`location_state` and on `job_title contains`. Run one query per plant town (Maryville MO,
Labrador City NL, Dearborn MI, Washington IN) rather than one per company. Titles at the site
level are irregular ("Melt Shop Manager", "Mill Superintendent", "Site Support Manager"), so
use `is_similar_to` with 6 to 8 variants, not an exact title list.

**b. Build the facility list first, then find the person.** For people who truly are not on
LinkedIn, the account is the *facility*, and the facility is in public record:

| Source | What it gives | How it enters Clay |
|---|---|---|
| MSHA Mine Data Retrieval System (US) | Every active mine, operator, controller, address, mine ID | CSV import → one row per mine |
| EPA ECHO / state air permits | Every mill and plant with a permit, operator name, address | CSV import |
| Company "Operations" / "Locations" pages | Plant names, often plant manager quotes in press releases | Claygent column per company |
| Trade press (Mining.com, Steel Market Update, Oil & Gas Journal) | Named plant managers in quotes | Claygent search per facility |

Then a Claygent column per facility row: *"Find the current plant/mine manager at
{{facility_name}}, {{city}}, operated by {{operator}}. Search the operator's newsroom, local
press, MSHA/permit filings, and conference speaker lists. Return name, title, source URL.
Return empty if not found; do not guess."* Finish with the **Work Email** waterfall and the
**Mobile Phone** waterfall (both exist as workspace functions). Mobile matters here: site
managers answer phones, not InMail.

### Minimal table build

1. `facilities` table: import MSHA + permit CSVs; columns `facility_name`, `operator`,
   `operator_domain`, `city`, `state`, `commodity/product`, `facility_type`.
2. Enrich company on `operator_domain` (headcount, revenue, parent via **Get Company Hierarchy**).
3. Find People at Company, scoped by `location_state` + title variants → writes contacts.
4. Claygent fallback on rows where step 3 returned nothing.
5. Work Email → Mobile Phone waterfall → push to CRM (**Add Contact to Salesforce** exists).

---

## 2. Enriching trade-show lists

### What was tested

The workspace already has a function built for exactly this: **"Full Name & Company Inputs
Only - Event Templates"**. It takes only `Full Name` and `Company` (Title and Email optional)
and returns company domain, title, work email, and LinkedIn URL. It was run on two names
pulled from the search above with Title and Email left blank.

| Input (name + company only) | Domain | Title returned | Work email | LinkedIn |
|---|---|---|---|---|
| Peyton Nicholson, Nucor | nucor.com | Beam Mill Manager (fresher than the search result's "Rolling Mill Manager") | found | found |
| Stephanie Bleker, Vale | **valeinsurancepartners.com (wrong)** | General Manager Copper Cliff Mine Complex | found, correct vale.com address | found |

Both rows resolved the person, title, email and LinkedIn correctly. The Vale row shows the
one failure mode of name-plus-company input: a short or generic company name can resolve to
the wrong domain even when the person match is right. Mitigation: when the badge scan or
exhibitor list includes a website, pass it as the domain; otherwise add a check column that
compares the returned domain against the email domain and flags mismatches for review.

Also present in the workspace: **Cvent - Event Involvement** (takes a person, returns events
they are involved in), which is the "who is going" half of the pre-event play.

### The pre / post event workflow

**Before the event**

1. Import the exhibitor list or attendee list (name + company is enough; booth number and
   session if available).
2. Run *Event Templates* on every row → domain, title, email, LinkedIn.
3. Enrich company on the domain → industry, headcount, revenue, HQ. Filter to ICP
   (mining / metals / O&G / rail operators, 500+ employees).
4. Dedupe against the CRM. Flag **net-new** vs **existing customer** vs **open opp** so reps
   spend floor time on the first bucket.
5. Claygent column: *"What is {{company}} building or expanding in the next 12 months?
   Search press releases and trade press since {{today - 6 months}}."* Gives the rep a
   reason to walk up.
6. Sequence: 2 emails + 1 LinkedIn touch, 10 to 3 days before the show, "we'll be at booth X".

**After the event**

1. Import badge scans (usually name, company, sometimes a personal email).
2. Run *Event Templates* again to replace personal emails with verified work emails and add
   LinkedIn.
3. **Find People at Company** on each scanned company → the 2 to 3 people *above* the badge
   holder (plant manager → operations director → VP operations). The person at the booth is
   rarely the signer.
4. Score: scanned-at-booth + ICP fit + buying signal → route hot rows to the rep within 48 h.

### Shows that matter for this prospect

| Market | Show | Why |
|---|---|---|
| Mining | MINExpo (Las Vegas, every 4 years), SME Annual, CIM Connect | Operators attend, not just vendors |
| Metals / mills | AISTech | Mill managers present papers; speaker list is a target list |
| Oil & gas | OTC Houston, Gastech | Operations and asset managers |
| Rail | Railway Interchange, InnoTrans (Berlin), APTA TRANSform, Railway Age events | Class I + transit agency ops leaders |
| Airports / people movers | ACI-NA Annual, Passenger Terminal Expo, APM conference (ASCE) | Airport authority engineering + APM O&M contractors |

Speaker lists are free, public, and higher quality than attendee lists. Scrape them into
Clay the same way.

---

## 3. New markets: rail, airport people movers, monorail

### What was tested

Two company searches.

**Rail / transit by industry** (Rail Transportation, Urban Transit Services, Ground Passenger
Transportation, Railroad Equipment Manufacturing; US; 500+ employees). First page of 20
returned the right universe: Union Pacific, CSX, Norfolk Southern, Amtrak, BART, WMATA,
Chicago Transit Authority, Sound Transit, MTA, California High-Speed Rail Authority, TTX,
Genesee & Wyoming, plus suppliers Wabtec, Progress Rail, Harsco Rail, Stadler, MERMEC.
`hasMore` was true; the full list is several hundred rows.

**People movers / monorail by semantic description** ("automated people mover", "monorail
system operator", "airport APM", "cable-propelled people mover"). Returned the real players:
POMA, Leitner, Doppelmayr (cable APMs: Oakland Airport Connector, Mexicali, Toulouse), Keolis
(automated metro operator), Alstom via Bombardier Transportation (Innovia APM/monorail),
Hyundai Rotem, Daifuku Airport America, Alstef, plus LAX (LAWA, mid-build on its APM) and ATL
from the first query. Noise to filter out: warehouse-robot vendors (Vecna, Quicktron,
Botsync) and elevator subsidiaries (Schindler). A `not industry in ("Industrial Automation")`
clause and a headcount floor fix most of it.

Of the 40 companies returned, **37 were already in the workspace's Audiences**, many with
Salesforce account IDs and fit scores. Whoever runs this prospect's workspace will start
from zero, but it shows the universe is fully covered in Clay's company data.

### Who actually buys, by segment

| Segment | Account type | Buyer titles to target | Notes |
|---|---|---|---|
| Class I freight rail | UP, BNSF, CSX, NS, CPKC, CN | VP/Dir Mechanical, Dir Engineering (MoW), Shop Superintendent, Locomotive Shop Manager | Shops are the "plants". Search by shop city (North Little Rock, Roanoke, Waycross). |
| Short lines | Genesee & Wyoming (100+ railroads), Watco, OmniTRAX | GM of each railroad, Chief Mechanical Officer | G&W is one domain hiding 100 buying centers. Use **Get Company Hierarchy**. |
| Transit / commuter | MTA, BART, WMATA, CTA, Metrolinx, Sound Transit | Chief Mechanical Officer, Dir Rail Vehicle Maintenance, Dir Infrastructure, Procurement | Public agencies: titles are on org charts and board minutes. Claygent on the agency site works well. |
| Airport APM | Airport authority (LAWA, PANYNJ, MWAA, DFW, ATL) **and** the APM O&M contractor | Authority: Dir Landside/APM Systems, Chief Engineer. Contractor: Site Manager, O&M Manager | Two buying centers per system. Contractors are Alstom, Mitsubishi (Crystal Mover), Doppelmayr, Leitner-Poma, Bombardier legacy. |
| Monorail | Las Vegas Monorail (LVCVA), Disney, Hitachi Rail, Alstom, BYD SkyRail | Dir Maintenance, Systems Engineering Manager | Small universe; a 30-row hand list beats a search. |
| Rail OEM / MRO | Wabtec, Progress Rail, Stadler US, Siemens Mobility, Alstom NA, Hitachi Rail | Plant Manager (Erie, Sacramento, Salt Lake City, Hornell), Dir Supply Chain | These *are* industrial plants. Same play as section 1. |

### Table build for the expansion

1. **Accounts**: run the two searches above with `load more` until exhausted; add the hand
   list for monorail and APM O&M contractors. Expect ~300 rows.
2. Enrich: headcount, revenue, HQ, **Get Company Hierarchy** (critical for G&W, MTA's six
   agencies, Alstom's legacy brands).
3. **Signals** (Claygent per account): fleet procurement announced; new line / extension under
   construction; federal grant awarded (FTA, FRA, FAA AIP); O&M contract re-bid; new CMO or
   VP Mechanical hired in last 6 months.
4. **Contacts**: Find People at Company with the titles in the table, 3 to 5 per account,
   then Work Email + Mobile.
5. Score and route.

The airport half of this already exists in this repo: `data/airports.csv` (50 airports),
`data/buying_centers.csv` (87 buying centers, authority vs terminal operator), and
`clay/column_plan.md`. Reuse it; the people-mover buyers are the "airport-wide authority"
rows plus one new row per APM O&M contractor.

---

## What to show the prospect

1. Live: the industrial search above. Twenty site managers, eight emails requested, eight
   found. Then "now do it for your 300 target plants."
2. Live: paste 5 names + companies from their last show into *Event Templates*. Watch the
   domain, title, email and LinkedIn fill in.
3. Live: the rail search, then click into Genesee & Wyoming and show the hierarchy problem
   and how Clay resolves it.
4. Close with the facility-first approach for off-LinkedIn contacts. Nobody else pitches
   MSHA + Claygent + mobile waterfall; it is the piece that makes "not on LinkedIn" a solved
   problem instead of an excuse.

---

## Status of the live runs (2026-11-11)

| Run | Task ID | Result |
|---|---|---|
| Industrial site managers, 8 producers | `mcp-task_0tocivhExvgJzRwQU6M` | 20 contacts; Work Email 8/8 on sample |
| Rail / transit companies by industry | `mcp-task_0tocivcAJsxK9DcjfDT` | 20 of several hundred, correct universe |
| People mover / monorail semantic search | `mcp-task_0tociwl9a4tq4EmwZZU` | 20 returned, ~14 relevant, filter noise as noted |
| Event Templates on 2 name+company rows | `mcp-task_0tociwxzzpURF2hwS3M` | 2/2 persons, titles, emails, LinkedIn resolved; 1 wrong company domain (Vale) |
