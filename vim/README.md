# Vim | Native-First Clay CLI POC

Build files for the Vim provider-prospecting workflow described in
"Vim | Native-First Clay CLI Workflow Build Guide" (Google Doc).

```
data/seed_accounts.csv     10 example logos (5 payer, 5 provider ICP models), guide headers
build/seed_accounts.py     regenerates the CSV; edit this, not the CSV
build/score.py             final code node: reconcile + score + why-now (self-test: python3 build/score.py)
clay/nodes/*.json          exact node specs sent to `clay workflows nodes create`
clay/nodes/*.py            code-node handlers (normalize, evidence)
clay/manifest/             workflow / trigger / graph responses and action schemas
```

## Live workflow (draft, not published, never run)

**[Vim | Provider Account Intelligence POC](https://app.clay.com/workspaces/91642/terracotta/tc-workflows/wf_0tm72qo2fw4Z5DAGxGn)**:
workspace Clay Demos (GTM), `wf_0tm72qo2fw4Z5DAGxGn`. The CSV trigger `62409ead-6f01-4ba0-b459-276dbad485cb`
is linked to `data/seed_accounts.csv`. `clay workflows graph validate` passes.

| # | Node | Type | Source | Credits/row |
|---|---|---|---|---|
| 1 | Normalize + identity check | code | rules | 0 |
| 2 | Clay: enrich company | tool | Clay `cpj-enrich-company-v2` (by Clay company ID) | 0.5 |
| 3 | HG Insights: website tech stack (EHR/portal) | tool | `hg-insights-get-company-website-tech-stack` | 2 |
| 4 | HG Insights: corporate structure (parent) | tool | `hg-insights-find-company-corporate-structure-v3` | 4 |
| 5 | PredictLeads: company news (M&A, expansion) | tool | `predict-leads-get-events-for-company-v3` | 0.5 |
| 6 | Clay: digital/IT/VBC job openings (90d) | tool | `cpj-find-lists-of-jobs` | 0.5 |
| 7 | Extract EHR / parent / M&A evidence | code | vendor dictionaries, 365-day M&A window | 0 |
| 8 | Needs healthcare fallback? | conditional (rules) | matched provider with EHR / parent / location gap | 0 |
| 9 | Claygent: healthcare gap research | agent (`gpt-5.4-nano`) | fallback branch only, evidence URL required | model cost |
| 10 | Reconcile + score + why-now | code | `build/score.py` | 0 |

About 7.5 catalog credits per row before Claygent, so roughly 75 for the 10 seeds plus up to
5 Claygent runs (providers only; payers skip it). These are catalog base prices, not a measured cost.

Not built yet, deliberately: people search and work email (guide §8), Signals (§9), weekly
discovery (§10), and HubSpot writeback (§11). They come after the 10-row test passes.
No structured action in this workspace returns clinic/location count, so every matched provider
goes to the Claygent for footprint. Swap in a structured source if Vim has one.

## Seed accounts

Company identity is from Clay company search. The provider ICP is modeled on the five
provider logos, not on individual physician practices.

| Segment | Accounts |
|---|---|
| Payer | UnitedHealthcare, Aetna (CVS Health), Cigna Healthcare, Humana, Elevance Health |
| Provider (ICP model) | VillageMD, Oak Street Health, One Medical, DaVita, LifeStance Health |

NPI, EHR, patient portal and location count are blank on purpose. The workflow's native
enrichment fills them, and blank means unknown, not no.

## Identity problems these seeds already show

- **Shared domains.** `elevancehealth.com` resolves to Elevance Health *and* the legacy
  "Anthem, Inc." entity. `lifestance.com` resolves to LifeStance Health *and* two small
  practice pages. Each row is pinned to one Clay company ID and LinkedIn URL. Key on those,
  not on the domain.
- **Shared parent.** Aetna and Oak Street Health are both CVS Health. Keep them as separate
  accounts. Record the parent only; never merge them.
- **LinkedIn headcount is not footprint.** VillageMD shows about 1.6k LinkedIn employees but
  describes 20,000+ staff at 700 locations. Score on locations and providers, not headcount.

## Scoring status

`score.py` is the guide's example scorecard (org type 25 / supported EHR 30 / specialty 20 /
footprint 15 / geography 10), labeled `provider-v0-placeholder`. `SUPPORTED_EHRS` is
**empty** until Vim confirms which EHRs it supports. Until then every account lands in
Review, which is the intended behavior. Payers need their own scorecard, which isn't built yet.
