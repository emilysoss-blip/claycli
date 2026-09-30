# -*- coding: utf-8 -*-
"""Seed sample Account Agent output: why now, and what to do (POC Build 2 payload).

This is the file to put on screen. Every row is an Account Agent reasoning over
three inputs the CRM cannot combine on its own:

  1. resolved account structure from Build 1 (hierarchy, EHR, tier)
  2. external signals from the dictionary in vim_signals.csv
  3. internal CRM history - deal stage, owner, last activity

and emitting a why-now, a named entry seat, and one action. The asks-a-human
column is deliberate: two of the eleven rows do not get an action, because the
honest output of an agent that found nothing is nothing.

Field order in ROWS:
 0  account
 1  signals_detected      "; " separated, each must exist in vim_signals.csv
 2  crm_context           what HubSpot already knew
 3  why_now
 4  recommended_action    "" means the agent is explicitly recommending no action
 5  entry_seat            person_name from vim_buying_committees.csv, "" if none
 6  channel
 7  confidence            High | Medium | Low
 8  what_would_change_it  the disconfirming check
"""
import csv, json, os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data")
ACCOUNTS = json.load(open(os.path.join(OUT, "vim_accounts.json"), encoding="utf-8"))
SIGNALS = json.load(open(os.path.join(OUT, "vim_signals.json"), encoding="utf-8"))
SEATS = json.load(open(os.path.join(OUT, "vim_buying_committees.json"), encoding="utf-8"))

ROWS = [
    ("Sierra Health Network",
     "EHR migration announced (Cerner or MEDITECH to Epic); Hiring interoperability or integration engineers; Account engagement spike",
     "Open opportunity, Ravid, stage unchanged for 41 days. Two contacts on the record, both in IT. "
     "Three visits to the integration docs page in the last week, all from the CIO's office.",
     "A funded platform migration with a board deadline, four open integration requisitions, and "
     "docs traffic from the buyer's own team in the same week. Integration requirements for the "
     "target state are being written right now - after they are frozen, this becomes a change request.",
     "Get into the EHR Transformation Program review, not the IT evaluation. Offer a target-state "
     "referral-data design against the migration plan, dated to their go-live.",
     "Gideon Barclay", "Exec intro via CIO, then programme review", "High",
     "If the migration is still 'evaluating vendors' rather than scheduled, this drops to Medium and "
     "the requirements window has not opened yet."),

    ("Lakeshore Integrated Health",
     "Health system acquires a provider group or hospital; Referral leakage or network integrity programme launched; New VP or Chief of Population Health / VBC",
     "Open opportunity, Ravid. Ridgeline Community Health sat in HubSpot as an unrelated parent "
     "account with its own owner until the hierarchy pass reparented it.",
     "They closed an acquisition that added 720 providers on MEDITECH to an Epic system, then posted "
     "a referral-management role naming leakage explicitly. The integration office exists, is funded, "
     "and has a deadline. This is the cleanest why-now in the universe.",
     "One conversation covering both entities. Lead with the merged referral process, which is "
     "running on spreadsheets, and show the hierarchy resolution as the artefact - their own CRM "
     "does not know these two are one company.",
     "Margarethe Solberg", "Champion-led, warm via the integration office", "High",
     "If the acquisition has announced but not closed state review, the integration budget is not "
     "released yet and the timeline slips a quarter or two."),

    ("Meridian Mutual Health Plan",
     "Payer enters a new state or files new MA counties; Prior-authorization automation initiative (CMS-0057); Provider directory accuracy or No Surprises Act exposure",
     "Open opportunity, Daryl, largest open deal in the book. Six committee seats, one in HubSpot.",
     "New MA county filings mean an adequate network has to be built to a regulatory date, while a "
     "CMS-0057 programme is already staffed against the same provider data. Two deadlines, one "
     "data problem, and a directory finding on the record that gives it an executive sponsor.",
     "Reframe from an IT purchase to network adequacy. Bring Network Management in as co-buyer - "
     "the budget is larger there than in IT, and the deadline is theirs.",
     "Katherine Vasquez", "Multithread: CIO plus SVP Network Management", "High",
     "If the county filings were withdrawn, the deadline disappears and this is an ordinary "
     "prior-auth conversation."),

    ("Pinnacle Provider Network",
     "New value-based or full-risk contract with a payer; Payer-provider partnership or joint venture announced; Hiring interoperability or integration engineers",
     "Open opportunity, Ravid. Largest account in the universe. Contracts with four other Tier 1 "
     "accounts in this same table.",
     "New risk arrangements with two systems already in the universe, and six open integration "
     "requisitions. The build-versus-buy decision is live, and the VP of Product would rather build.",
     "Answer build-versus-buy in the first meeting, in writing, or Product becomes the blocker. "
     "The proof point is the relationship graph: four Tier 1 systems here are already their "
     "counterparties.",
     "Rosalind Mbeki", "VBC-led, with Product in the room from the start", "Medium",
     "If the integration requisitions are agency reposts rather than new headcount, build-versus-buy "
     "is not actually open and there is no urgency."),

    ("Cascade Valley Health",
     "Epic Community Connect expansion to affiliates; New CIO or CDIO appointed; Account engagement spike",
     "Open opportunity, Ravid. The physicians network sits in HubSpot as its own record on a "
     "different domain; only the hierarchy pass links it to the parent.",
     "A new Chief Digital & Information Officer in month four, inheriting a Cerner system and an "
     "acquired athenahealth group, and a Community Connect rollout that pushes one instance across "
     "organizations that do not share an owner. New CIOs are measured on visible convergence wins.",
     "Lead with the two-EHR gap between the parent and the acquired group. That is a problem the new "
     "CIO was hired to solve and that Community Connect does not fix on its own.",
     "Deandra Whitfield", "New-CIO first-90-days angle", "High",
     "If the CDIO is an internal promotion rather than an outside hire, the vendor reset does not "
     "happen and the existing roadmap holds."),

    ("Sunbelt Care Partners",
     "New value-based or full-risk contract with a payer; Referral leakage or network integrity programme launched",
     "Open opportunity, Daryl. Short evaluation cycles on record from the last two deals.",
     "Full risk on 220k delegated lives across 1,900 providers they do not employ. Leakage is a "
     "direct P&L line, and a network-performance programme is already staffed against it.",
     "Go straight at unit economics with the CMO: cost per leaked referral against 220k delegated "
     "lives. Expect the analytics director to benchmark against building it in-house.",
     "Dr. Luis Ontiveros", "CMO-led, economics first", "High",
     "If the new risk contract is a renewal rather than an expansion, the economics have not changed "
     "and this is a renewal-cycle conversation instead."),

    ("Harborview Health Partners",
     "ACO REACH / MSSP participation change; Digital front door / patient access programme; Account engagement spike",
     "Open opportunity, Ravid. Previous cycle lost to 'we'll do it in Epic'. That objection is "
     "still on the record and unanswered.",
     "They moved up a risk track, which puts downside exposure on the Chief Population Health "
     "Officer. Her budget moves faster than IT's, and the ACO is a separate legal entity with its "
     "own leadership - a path around the Epic objection rather than through it.",
     "Route through Harborview ACO LLC and the population-health budget. Answer the Epic question "
     "in writing before the applications director asks it, because he will.",
     "Dr. Miriam Castellanos", "Population-health budget, ACO entity as the vehicle", "Medium",
     "If the REACH change is a within-model track change rather than a new risk position, the "
     "economics did not move and the Epic objection stands."),

    ("Cascade Valley Health Plan",
     "Provider directory accuracy or No Surprises Act exposure; Prior-authorization automation initiative (CMS-0057)",
     "Open opportunity, Daryl. Sibling of the provider parent, which is also an open opportunity "
     "with a different owner.",
     "A directory finding plus a prior-auth programme on the same provider file. The unusual part is "
     "structural: the payer and the provider network share an ultimate parent, so the same executive "
     "owns both sides of the referral.",
     "Sell the family, not the entity. One conversation with the system parent covering both the "
     "plan and the provider arm - and coordinate with the provider-side owner before either call.",
     "Owen Kirkbride", "Coordinated with the provider-side account owner", "Medium",
     "If the directory finding was an industry-wide CMS sweep naming dozens of plans, it is not "
     "specific to them and the sponsor does not exist."),

    ("Meridian Advantage",
     "ACO REACH / MSSP participation change; Payer enters a new state or files new MA counties",
     "Open opportunity, Daryl. Parent is the largest open deal in the book, under the same owner.",
     "Delegated-risk contracts with Gulf Coast and Great Lakes - both in this universe - and Stars "
     "performance depends on care gaps closing, which depends on referrals landing. Separate P&L "
     "from the parent, so it can buy on its own timeline.",
     "Sequence behind the parent rather than beside it. Use the parent conversation to earn the "
     "introduction, then run a separate cycle on the Stars economics.",
     "Yvette Cardoso", "Sequenced after the parent deal", "Medium",
     "If the parent deal stalls, this one is better run independently - the separate P&L is what "
     "makes that possible."),

    ("Northmark Health System",
     "Account engagement spike; Stalled after engagement",
     "Open opportunity, Daryl, no activity in 63 days. Two contacts, both marketing-sourced. "
     "Engagement in the last fortnight came from a resident, not from the committee.",
     "Nothing external changed. The only movement is engagement from someone with no role in the "
     "decision, which the agent weights down rather than up.",
     "",
     "", "No action this cycle", "Low",
     "This becomes real on any of: a new VBC or population-health hire, a risk contract with "
     "Meridian or Pinnacle, or engagement from the CIO or CMIO seat. All three are monitored."),

    ("Summit Ridge Health",
     "Stalled after engagement",
     "Open opportunity, Daryl, last activity 38 days ago. Four committee seats, none in HubSpot.",
     "Just over the Tier 1 line on structure - Epic, 2,450 providers, a captive plan taking full "
     "MA risk - but no external signal has fired. Good account, wrong week.",
     "",
     "", "Nurture only; hold for a signal", "Low",
     "A full-risk contract expansion at the captive plan, or a VBC hire, would move this to the top "
     "of the queue. Until then, forcing a touch spends the account."),
]

COLS = ["priority_rank", "account", "account_crm_id", "icp_tier", "icp_score", "signals_detected",
        "signal_count", "crm_context", "why_now", "recommended_action", "entry_seat",
        "entry_seat_title", "entry_seat_role", "channel", "recommended_owner", "confidence",
        "what_would_change_it"]

acct_by_name = {a["crm_name"]: a for a in ACCOUNTS if a["dedupe_status"] == "canonical"}
signal_names = {s["signal"] for s in SIGNALS}
seat_by_name = {s["person_name"]: s for s in SEATS}

records = []
for rank, (account, sigs, crm_ctx, why, action, seat, channel, conf, change) in enumerate(ROWS, 1):
    a = acct_by_name[account]
    detected = [s.strip() for s in sigs.split(";") if s.strip()]
    for s in detected:
        assert s in signal_names, f"{account} cites a signal not in the dictionary: {s}"
    seat_rec = seat_by_name.get(seat) if seat else None
    if seat:
        assert seat_rec, f"{account} names an entry seat not in the committee file: {seat}"
        assert seat_rec["account"] == account, f"{seat} is not on the {account} committee"
    records.append({
        "priority_rank": rank,
        "account": account,
        "account_crm_id": a["crm_record_id"],
        "icp_tier": a["icp_tier"],
        "icp_score": a["icp_score"],
        "signals_detected": "; ".join(detected),
        "signal_count": len(detected),
        "crm_context": crm_ctx,
        "why_now": why,
        "recommended_action": action,
        "entry_seat": seat,
        "entry_seat_title": seat_rec["title"] if seat_rec else "",
        "entry_seat_role": seat_rec["role_in_deal"] if seat_rec else "",
        "channel": channel,
        "recommended_owner": a["crm_owner"],
        "confidence": conf,
        "what_would_change_it": change,
    })

# Every Tier 1 account gets a verdict, including the ones the agent declines to act on.
tier1 = {a["crm_name"] for a in ACCOUNTS
         if a["dedupe_status"] == "canonical" and a["icp_tier"] == "Tier 1"}
missing = sorted(tier1 - {r["account"] for r in records})
assert not missing, f"Tier 1 accounts with no agent verdict: {missing}"
for r in records:
    # An action needs a named seat to take it to; no action needs no seat.
    assert bool(r["recommended_action"]) == bool(r["entry_seat"]), \
        f"{r['account']}: action and entry seat must agree"
    assert r["what_would_change_it"], f"{r['account']} has no disconfirming check"

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "vim_account_agent.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(records)
json.dump(records, open(os.path.join(OUT, "vim_account_agent.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

acted = [r for r in records if r["recommended_action"]]
print(f"vim_account_agent: {len(records)} Tier 1 verdicts, {len(acted)} with a recommended action")
print("  confidence: " + ", ".join(f"{k} {v}" for k, v in Counter(r["confidence"] for r in records).items()))
print(f"  {len(records) - len(acted)} accounts explicitly recommended no action this cycle")
