# Vim | Native-First Clay CLI POC

Build files for the Vim provider-prospecting workflow described in
"Vim | Native-First Clay CLI Workflow Build Guide" (Google Doc).

```
data/seed_accounts.csv     10 example logos (5 payer, 5 provider ICP models), guide headers
build/seed_accounts.py     regenerates the CSV; edit this, not the CSV
build/score.py             deterministic fit scoring + tiering for the code node (self-test: python3 build/score.py)
build/build_workflow.sh    phase-1 CLI build: inventory, draft workflow, CSV trigger, CSV link (no credits)
```

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
