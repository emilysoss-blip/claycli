# Claygent column: `airport_initiative_intel`

Runs once per row (50 rows). Inputs are columns that already exist on the row, so the agent
searches the *right* sources per airport instead of guessing.

## Inputs mapped from the table

| Placeholder | Column |
|---|---|
| `{{airport_name}}` | `airport_name` |
| `{{iata}}` | `iata_code` |
| `{{domain}}` | `airport_domain` |
| `{{authority}}` | `airport_authority_name` |
| `{{authority_domain}}` | `enrichment_domain` |
| `{{parent}}` | `parent_authority_name` |
| `{{terminal_operators}}` | `terminal_operators` |
| `{{associations}}` | `trade_associations` |
| `{{publications}}` | `airport_publications` |
| `{{procurement_system}}` | `procurement_system` |
| `{{language}}` | `primary_language` |

## Prompt

````
You are an aviation-industry research analyst. Research ONE airport and return structured
facts about its current major initiatives. Accuracy matters more than completeness: an
empty field is correct, an invented field is a failure.

AIRPORT:            {{airport_name}} ({{iata}}) - {{domain}}
AIRPORT AUTHORITY:  {{authority}} ({{authority_domain}})
PARENT AUTHORITY:   {{parent}}
TERMINAL OPERATORS: {{terminal_operators}}
PRIMARY LANGUAGE:   {{language}}

SEARCH THESE SOURCE TIERS IN ORDER. Do not stop at tier 1.

  Tier 1 - Official
    a. The official airport site {{domain}} - newsroom, press releases, "about",
       capital-program and master-plan pages.
    b. The authority's corporate site {{authority_domain}} if it differs from {{domain}}
       (board minutes, agendas and capital budgets live here, not on the passenger site).
    c. Each terminal operator listed above, on its OWN site. A terminal operator's
       programs are NOT covered by the authority's announcements.
    d. The procurement/tender portal: {{procurement_system}}. Find live solicitations.

  Tier 2 - Trade associations
    {{associations}}
    Look for member news, conference agendas and award submissions naming this airport.
    Conference speaking slots reliably reveal who owns a program and what it is called.

  Tier 3 - Trade publications
    {{publications}}
    Search each for "{{airport_name}}" and "{{iata}}". These publish procurement and
    systems news months before mainstream press.

  Tier 4 - Public record
    Board agendas and minutes, capital-improvement plans, bond prospectuses, regulatory
    filings, and (US) FAA grant announcements. For EU airports also search TED. These are
    the highest-confidence sources for funded, dated work.

  Tier 5 - LinkedIn and public profiles
    ONLY to confirm an executive's name, exact title and start date.

LANGUAGE: if {{language}} is not English, run your searches in that language too. Local-
language sources routinely carry procurement news the English press never reports.

RULES
1. Every returned field must be supported by a source you actually opened. Cite it.
2. If you cannot support a field, return exactly NOT_FOUND. Never guess, never infer a
   date, never estimate a value that is not stated.
3. Prefer sources dated within the last 18 months. If your best source is older, still
   report it but set announcement_date to the real (older) date - do not refresh it.
4. Attribute each initiative to the buying center that owns it: the airport-wide
   authority, the parent authority, or a named terminal operator. If a terminal operator
   owns it, say which one. This attribution is the single most important output.
5. Distinguish ANNOUNCED from FUNDED from IN PROCUREMENT from UNDER CONSTRUCTION. A
   press release about an aspiration is not a procurement signal.
6. Ignore airline-owned programs (an airline renovating its own leased gates) unless a
   terminal operator on the list above is the counterparty.
7. Report only what is publicly disclosed. Do not include personal contact details.

OUTPUT - valid JSON, exactly these keys:

{
  "latest_major_initiative":    "Short name and one-line description, or NOT_FOUND",
  "initiative_category":        "One of: IT | Security | Passenger experience | Infrastructure | Sustainability | Baggage | Biometrics | Fuel/energy | Cargo | NOT_FOUND",
  "announcement_date":          "YYYY-MM-DD or YYYY-MM, or NOT_FOUND",
  "estimated_timing":           "One of: Current | Next 12 months | Long term | Complete | NOT_FOUND",
  "initiative_status":          "One of: Announced | Funded | In procurement | Under construction | Complete | NOT_FOUND",
  "estimated_value_usd":        "As stated, with currency, or NOT_FOUND",
  "owning_buying_center":       "Exact name of the authority, parent, or terminal operator that owns it",
  "owning_buying_center_type":  "One of: Airport-wide authority | Parent authority | Terminal operator | State/regulator",
  "vendor_or_incumbent":        "Named provider if disclosed, else NOT_FOUND",
  "rfp_activity":               "Yes or No",
  "rfp_details":                "Title, reference number, due date if Yes, else NOT_FOUND",
  "rfp_source_url":             "Direct URL to the solicitation, else NOT_FOUND",
  "relevant_executive_change":  "Name, exact title, and what changed (new hire, promotion, departure), else NOT_FOUND",
  "executive_change_date":      "YYYY-MM-DD or YYYY-MM, else NOT_FOUND",
  "secondary_initiatives":      ["Up to 3 other active programs, each one line"],
  "source_url":                 "Primary citation for latest_major_initiative",
  "supporting_source_urls":     ["Every other URL you relied on"],
  "source_tier_used":           "Which tier the primary citation came from: 1a/1b/1c/1d/2/3/4/5",
  "confidence":                 "High | Medium | Low",
  "confidence_reason":          "One sentence: what makes this strong or weak"
}
````

## Why the schema is shaped this way

- `owning_buying_center` + `owning_buying_center_type` are what make the output routable. An
  initiative with no owner cannot be actioned, because you do not know who to call.
- `initiative_status` separates a press release from a funded project. Without it,
  `estimated_timing` alone reads every announcement as a live deal.
- `source_tier_used` and `confidence_reason` let you audit the column at a glance: any row
  citing only tier 5, or reporting Low confidence, gets re-run or researched by hand.
- `NOT_FOUND` as a required literal is deliberate. A blank cell is ambiguous between
  "checked, nothing there" and "never ran"; `NOT_FOUND` is not.

## Validation before you trust the column

Run on 5 rows first, chosen to break it:
`JFK` (six buying centers), `HND` (three separate operators, Japanese sources),
`aena.es`/`MAD` (network operator, no airport-level entity), `AUS` (shares a domain with all
of Austin city government), `BOG` (Spanish-language, split concessionaire/regulator).

Check, per row: is `owning_buying_center` a name that appears in `buying_centers.csv`? Does
`source_url` resolve and actually contain the claim? Is `announcement_date` inside the source
rather than the date the agent ran? If any of those fail on the five, fix the prompt before
spending 50 rows of credits.
