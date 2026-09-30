# Vim Enterprise GTM Engine — POC

Three builds, packaged as **one connected enterprise workflow** rather than three
capabilities. The business story is what changes: not "account enrichment, contact
enrichment, ads", but *one continuously updated source of truth instead of ad-hoc Clay
tables, manual research, fragmented CRM data and CSV uploads.*

> **Sample data.** Every organization and person in `data/vim_*.csv` is invented. The
> structures are real healthcare GTM patterns — provider-sponsored plans, employed groups
> on a different EHR than their parent, MA subsidiaries with their own contracting team —
> and every headline count is computed from the seed files, so the page and the CSVs
> cannot disagree. But nothing here describes an actual company, and no figure should be
> quoted externally. Point stage 1 at Vim's HubSpot export and every column downstream
> stays exactly as specified.

## The slide

**VIM ENTERPRISE GTM ENGINE**

1. **Know the account.** HubSpot → dedupe → parent/subsidiary mapping → EHR + healthcare
   enrichment → ICP score.
2. **Know when and who.** Tier 1 accounts → buying committees → signals → Account Agent →
   recommended action.
3. **Activate everywhere.** Dynamic audiences → LinkedIn/Meta → continuously updated
   targeting.

*One continuously updated source of truth instead of ad-hoc Clay tables, manual research,
fragmented CRM data and CSV uploads.*

## What is here

```
vim-enterprise-gtm-engine.html   the browsable view - open this first
clay/vim/column_plan.md          stage-by-stage build spec for all three builds
clay/vim/account_agent_prompt.md the Account Agent prompt + 5-row validation plan
data/vim_accounts.csv            44 CRM records -> 32 organizations (Build 1)
data/vim_buying_committees.csv   55 seats across the 11 Tier 1 accounts (Build 2)
data/vim_signals.csv             18-signal healthcare dictionary (Build 2)
data/vim_account_agent.csv       11 why-now / recommended-action verdicts (Build 2)
data/vim_ad_segments.csv         6 dynamic segments (Build 3)
build/seed_vim_*.py              regenerates every CSV - edit these, not the CSVs
build/make_vim_page.py           regenerates the HTML view from the JSON
```

Regenerate everything, in order (later seeds read earlier ones):

```bash
python3 build/seed_vim_accounts.py && python3 build/seed_vim_committees.py \
  && python3 build/seed_vim_signals.py && python3 build/seed_vim_agent.py \
  && python3 build/seed_vim_segments.py && python3 build/make_vim_page.py
```

Each seed asserts its own integrity as it runs — no orphaned parents, no duplicate
collapsing into a non-canonical record, no Tier 1 account without an economic buyer, no
agent verdict citing a signal that is not in the dictionary, no recommended action without
a named seat, no empty segment. A seed that would produce an inconsistent table fails
instead.

---

## Build 1 — Enterprise Account Intelligence + CRM Cleanup

**The hero build.** It combines the two things Vim raised themselves: Daryl is already
thinking about deduping the CRM, and Ravid specifically wanted to test parent/subsidiary
identification. Those are not two projects.

Pull the HubSpot company universe into an Audience, resolve companies to Clay Company IDs,
dedupe, resolve parent/subsidiary and ultimate-parent relationships, then enrich every
account with the healthcare fields Vim actually cares about: EHR and tech stack
(Epic, Oracle Health/Cerner, athenahealth, MEDITECH, eClinicalWorks, NextGen, mixed),
organization type, parent health system, provider and network size, lives covered,
geography, payer/provider relationships, and the rest of the ICP criteria.

**Output:** a continuously maintained *Vim Enterprise Account Universe* answering, per row:
who should we sell to, which health system do they belong to, what EHR do they use, and how
valuable are they.

In the sample set: **44 CRM records resolve to 32 organizations inside 20 corporate
families, with 11 Tier 1.**

Three things worth putting on screen from this build, all of them in the view:

- **7 duplicates, 3 site-level merges, 2 unresolved.** The 12 collapsed records are the
  cleanup number, and it lands before a single enrichment credit is spent.
- **Dedupe on the Company ID, never the domain.** `harborviewhp.org` carries both Harborview
  Health Partners *and* Harborview ACO LLC — a separate legal entity, with its own VBC
  leadership, holding the ACO REACH contract. A domain dedupe deletes the row that decides
  whether VBC tooling gets bought. Meanwhile three Northmark records on three different
  domains are one company, which no domain rule catches either. Same shortcut, both failures.
- **The two unresolved rows stay unresolved.** One matches a canonical record on name and
  owner only; one has no name, no domain and no ID. They are held for a human. Bad hierarchy
  data is worse than none, because it routes confidently.

## Build 2 — Enterprise Buying Committee + Signals

Take Build 1's Tier 1 rows and find the people who matter across CIO/IT, value-based care,
population health, digital health, clinical transformation, partnerships, product, and
network/contracting. Then layer in signals: executive hires, EHR changes, new VBC
initiatives, payer/provider partnerships, M&A, market expansion, relevant job openings,
and account engagement. An **Account Agent** combines CRM history with external signals and
outputs *why now* and a recommended action.

Ravid asked directly whether Account Agents could combine internal CRM history with external
signals such as hiring and LinkedIn activity. They can, and this is the column that does it.

This is the build that connects to what was learned in person: Vim wants to win more
enterprise organizations. Instead of the team manually researching huge healthcare systems,
Clay continuously says which enterprise accounts changed, who matters there, and why someone
should act now.

In the sample set: **55 seats across 11 accounts, 45 of them net-new to the CRM (82%).** Today
Vim cannot see four out of five of the people who decide.

Two design choices that make the difference between a signal engine people trust and one
they stop opening:

- **Every signal carries its false positive.** An interim CIO promoted from inside changes
  nothing. "Exploring options" is not a migration. A staffing agency reposting one
  requisition across four boards is one requisition. A CMS sweep naming forty plans says
  nothing about this one. All four look like buying signals in a dashboard.
- **The agent is allowed to return nothing.** Two of the 11 verdicts recommend no action —
  Northmark, where the only movement is engagement from a resident with no role in the
  decision, and Summit Ridge, a genuinely good account with no signal fired. Both still carry
  a `what_would_change_it` naming the monitored events. An agent that always finds a reason
  to act is a random number generator with good manners.

Ranking is on **a dated deadline that belongs to them**, never on signal count.

## Build 3 — Dynamic Enterprise Ad Audiences

Worth keeping because it is the cleanest before/after ROI demonstration in the set. Today
Ravid enriches people, exports CSVs, hands them to marketing or a freelancer, and they upload
to LinkedIn/Meta — a process he described as decoupled and manual. Seeing the dynamic version
was what prompted "opens a lot of capabilities for us."

Build dynamic segments off the same account universe: Tier 1 payer/provider accounts → target
buying committee → enrich identifiers → sync to LinkedIn/Meta. As people enter and leave the
segment, the audience updates.

In the sample set: **6 segments**, each with an entry rule **and an exit rule**. The exit rule
is the half a CSV upload does not have, and it is why the uploaded list decays from the day it
is built.

One number to be careful with in a pricing conversation. `addressable_people` is how many
people have the match key the destination needs — counted from the data, and quotable.
`est_reachable` applies a flat assumed platform match rate (LinkedIn 65%, Meta 45%) and is
**illustrative**; replace it with observed rates after the first sync. That first sync is the
first thing this build can honestly be judged on.

---

## What is deliberately not a primary POC

**AI outbound and copy generation.** Discussed on the call, but Daryl did not have an
immediate campaign that needed building. A build here demos well and proves nothing about the
enterprise motion.

**Inbound lead enrichment and routing.** A strong **Phase 2** workflow, and genuinely
valuable: new HubSpot lead → immediate enrichment → determine payer/provider/EHR/health-tech
segment → score → route → sync everything back to HubSpot. Daryl recognized the value and
also recognized that the current daily-sync setup caps how much of it is reachable today. It
becomes the natural first Phase 2 build once the sync cadence is addressed.

## If one thing goes in front of the CIO

**Build 1 into Build 2, as a single live run.** Take a messy Vim enterprise account, identify
its entire health-system hierarchy, enrich its EHR and healthcare context, find the buying
committee, detect the relevant signals, and produce the recommended next action.

Lakeshore is the row to use. Ridgeline Community Health sits in HubSpot as an unrelated parent
account with its own owner; it was acquired. No amount of CRM hygiene discovers that — the
M&A signal in Build 2 reparents it, and then Build 1's hierarchy is right on the next run and
Build 3's audiences follow the night after. That feedback loop is why this is one engine and
not three tables, and it is the demo where Enterprise stops needing an explanation.

These were the three POC areas the call landed on, and Daryl said that would be "huge". The
difference is the packaging: one connected enterprise workflow, which gives the $100K
conversation a materially bigger business story than three separate capabilities.

## Not done

- **Nothing has been run in Clay.** No credits spent, no live enrichment, no contact search.
  This is the spec plus a worked sample, not a populated table.
- **The account universe is invented.** The real Build 1 starts with Vim's HubSpot company
  export. Stage 1 is the only thing that changes; every column after it is specified.
- **No committee contacts are real.** `vim_buying_committees.csv` carries the titles and
  functions to search for, which is the *input* to contact sourcing, not its output.
- **The Account Agent prompt has not been run.** It is written and its 5-row validation plan
  is specified in `clay/vim/account_agent_prompt.md`; validate before running the full set.
- **Platform match rates are assumed.** See Build 3 above. The first sync replaces them.
