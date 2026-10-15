# Claygent fallback: field-level, gated

Claygent is the last step for one field on one row, not a research column over the cohort.
This follows build guide section 6.

## Eligibility (rules conditional `Needs enrichment fallback?`)

A row goes to Claygent only when every one of these is true:

| Condition | Field on the row |
|---|---|
| Identity resolved | `domain_match_status` is not `wrong_company` / `no_usable_match` unless a LinkedIn URL is pinned |
| A required fit field is still unknown or conflicted | `missing_required_fields` contains `hcm` or `open_reqs`, or a `conflict_status` is set |
| Every structured source for that field was tried | `native_sources_tried` lists them (Salesforce, native technographic action, Open Jobs) |
| Research could change the tier | `fit_best_case >= 60` (the Tier 2 floor in `tiering.CRITERIA`) |

Good candidates on this cohort: the HCM on any account (technographics was dispatched, but
read-back failed and coverage of HR systems is typically thin), the Mercer relationship to
Marsh, and the Honeywell headcount conflict (page text 50,000+ vs `employee_count` 129,754).

## Prompt

```
Organization: {{account_name}}, {{enrichment_identifier}}, {{country}}.
Hiring entity, if narrower than the parent: {{entity_name}}.
Missing fields: {{missing_fields}}.

Research only these fields. For each finding return value, source URL, short supporting
evidence, observation date and uncertainty.

- HCM / ATS: name the system only when a source states it is deployed (vendor case study,
  press release, job posting requiring admin experience in the system, the company's own
  careers-site footer naming the ATS). A careers-site vendor alone is a clue, not proof: return
  it as a clue with uncertainty "high".
- Parent / division: do not infer ownership from a similar name or a shared domain.
- Leadership change: do not infer one from a press mention without a date.

Return unknown if the evidence does not establish the answer. Never overwrite a verified
structured result.
```

## Output schema

```json
{
  "findings": [
    {
      "field": "hcm | open_reqs | parent | headcount",
      "value": "string or unknown",
      "evidence_type": "deployed | clue | stated | none",
      "source_url": "string",
      "supporting_evidence": "one sentence quoted or paraphrased from the source",
      "observed_at": "YYYY-MM-DD from the source, not the run date",
      "uncertainty": "low | medium | high"
    }
  ]
}
```

## Reconciliation (deterministic, after Claygent)

- Promote a value only if `evidence_type` is `deployed` or `stated` **and** `uncertainty` is
  not `high`.
- A `clue` never fills a required field. It goes on the row as evidence and the account
  stays in Review.
- When Claygent contradicts a native value, keep both. Set `conflict_status`, and leave the
  native value in the scored field until a human resolves it.
- Log for every row: `ai_called` (yes/no), `fields_promoted`, `credits`. The POC report
  quotes the ratio of promoted fields to rows sent.
