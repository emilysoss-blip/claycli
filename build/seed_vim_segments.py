# -*- coding: utf-8 -*-
"""Seed the dynamic ad segments (POC Build 3).

Membership is COMPUTED from vim_accounts.csv and vim_buying_committees.csv rather
than typed in, so the counts and the match rates cannot drift away from the rules
that produced them - which is the whole argument of this build. Change the ICP
threshold in Build 1 and these numbers move on the next run, exactly as the live
segment would.

The one thing a static snapshot genuinely cannot produce is a weekly delta, so
joined_7d and left_7d below are illustrative and labelled as such. Everything
else is derived.

Destination decides the match key: LinkedIn matches on the member's profile, Meta
on a hashed email, so the same segment has two different addressable sizes.

Two numbers per segment, and they mean different things:

  addressable_people  people who HAVE the match key this destination needs.
                      Derived - count it from the data.
  est_reachable       people the platform would actually put an impression in
                      front of. Derived, but on a flat assumed match rate
                      (PLATFORM_MATCH below), because the true rate depends on
                      what the platform holds and cannot be known from here.

Do not quote est_reachable to the customer as a measured figure. It is there so
the before/after comparison has a denominator, not as a promise.
"""
import csv, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data")
ACCOUNTS = json.load(open(os.path.join(OUT, "vim_accounts.json"), encoding="utf-8"))
SEATS = json.load(open(os.path.join(OUT, "vim_buying_committees.json"), encoding="utf-8"))
AGENT = json.load(open(os.path.join(OUT, "vim_account_agent.json"), encoding="utf-8"))

CANON = [a for a in ACCOUNTS if a["dedupe_status"] == "canonical"]
BY_NAME = {a["crm_name"]: a for a in CANON}

PAYER = {"Regional payer", "National payer", "Medicare Advantage plan",
         "Provider-sponsored health plan", "Payer services"}
PROVIDER = {"Health system", "Employed physician group", "Independent provider group",
            "ACO / IPA", "Value-based care enabler"}

agent_by_acct = {r["account"]: r for r in AGENT}

# Illustrative, not measured. Typical order of magnitude for a well-formed B2B
# audience: LinkedIn resolves most named profiles, hashed-email matching on Meta
# is materially worse. Replace both with the customer's observed rates after the
# first sync, which is the first thing Build 3 produces that Build 3 can be judged on.
PLATFORM_MATCH = {"LinkedIn": 65, "Meta": 45}


def has_signal(acct, needle):
    r = agent_by_acct.get(acct)
    return bool(r) and needle in r["signals_detected"]


# (segment, destination, match_key, account predicate, seat predicate, entry_rule, exit_rule,
#  refresh, joined_7d, left_7d, purpose)
SEGMENTS = [
    ("T1 payer - VBC and network owners", "LinkedIn", "LinkedIn profile",
     lambda a: a["icp_tier"] == "Tier 1" and a["org_type"] in PAYER,
     lambda s: s["function"] in {"Value-based care", "Network & contracting", "Product"},
     "Account reaches Tier 1 AND org_type is a payer AND the seat's function is VBC, network "
     "contracting or product.",
     "Account drops below Tier 1, the person changes company, or the seat's function changes.",
     "Nightly", 4, 1,
     "The payer-side committee. Different message to the provider side, so it cannot share an audience."),

    ("T1 health system - IT and clinical transformation", "LinkedIn", "LinkedIn profile",
     lambda a: a["icp_tier"] == "Tier 1" and a["org_type"] in PROVIDER,
     lambda s: s["function"] in {"CIO / IT", "Clinical transformation", "Population health"},
     "Account reaches Tier 1 AND org_type is a provider organization AND the seat owns IT, "
     "clinical transformation or population health.",
     "Account drops below Tier 1, the person changes company, or the seat's function changes.",
     "Nightly", 6, 2,
     "The provider-side committee. Air cover for the seats that decide workflow and adoption."),

    ("Epic estates - interoperability owners", "LinkedIn", "LinkedIn profile",
     lambda a: a["ehr_primary"].startswith("Epic") and a["icp_tier"] in {"Tier 1", "Tier 2"},
     lambda s: s["function"] in {"CIO / IT", "Clinical transformation"},
     "ehr_primary begins with Epic AND account is Tier 1 or 2 AND the seat owns IT or clinical "
     "transformation.",
     "EHR enrichment stops returning Epic, or the account drops below Tier 2.",
     "Weekly (EHR re-enrichment cadence)", 2, 0,
     "Epic-specific creative. The 'why not just do it in Epic' objection is answered in the ad, "
     "not in the third meeting."),

    ("EHR migration in flight", "LinkedIn", "LinkedIn profile",
     lambda a: has_signal(a["crm_name"], "EHR migration announced"),
     lambda s: True,
     "The EHR-migration signal fires on the account. Every committee seat enters, not just IT - "
     "a migration is a whole-committee event.",
     "Signal ages past 12 months with no confirmed go-live date, or the migration completes.",
     "Weekly", 5, 0,
     "The highest-intent segment and the smallest. Highest bid, narrowest creative."),

    ("Open opportunity - full committee ABM", "LinkedIn", "LinkedIn profile",
     lambda a: a["open_deal"] == "Yes" and a["icp_tier"] == "Tier 1",
     lambda s: True,
     "Account has an open deal AND is Tier 1. Every seat enters, including the ones with no CRM "
     "contact record.",
     "Deal closes won or lost, or the account drops below Tier 1.",
     "Nightly (follows HubSpot deal stage)", 3, 4,
     "Air cover over live deals. The 81% of seats with no CRM contact are the point - today they "
     "see nothing."),

    ("Engaged but stalled - re-engagement", "Meta", "Hashed email",
     lambda a: has_signal(a["crm_name"], "Stalled after engagement"),
     lambda s: s["email_status"] == "Verified",
     "The stalled-after-engagement signal fires AND the seat has a verified email, because Meta "
     "matches on the email rather than the profile.",
     "Any new engagement from the account, or a booked meeting.",
     "Weekly", 2, 3,
     "Cheapest audience in the set. Meta rather than LinkedIn because the intent is recall, not reach."),
]

COLS = ["segment", "destination", "match_key", "accounts_in_segment", "accounts_with_committee",
        "people_in_segment", "addressable_people", "has_match_key_pct",
        "platform_match_assumption_pct", "est_reachable", "net_new_to_crm", "entry_rule",
        "exit_rule", "refresh", "joined_7d_illustrative", "left_7d_illustrative", "purpose",
        "account_list"]

records = []
for (name, dest, key, acct_pred, seat_pred, entry, exit_, refresh, joined, left, purpose) in SEGMENTS:
    accts = [a for a in CANON if acct_pred(a)]
    acct_names = {a["crm_name"] for a in accts}
    people = [s for s in SEATS if s["account"] in acct_names and seat_pred(s)]
    # LinkedIn matches on the profile; Meta needs a deliverable email address.
    if key == "LinkedIn profile":
        addressable = [p for p in people if p["linkedin_present"] == "Yes"]
    else:
        addressable = [p for p in people if p["email_status"] == "Verified"]
    rate = round(100 * len(addressable) / len(people)) if people else 0
    assumption = PLATFORM_MATCH[dest]
    records.append({
        "segment": name,
        "destination": dest,
        "match_key": key,
        "accounts_in_segment": len(accts),
        # Committees are only sourced for Tier 1, so a segment that reaches into Tier 2
        # has accounts with no seats yet. Surfacing the gap beats hiding it in a total.
        "accounts_with_committee": len({s["account"] for s in SEATS if s["account"] in acct_names}),
        "people_in_segment": len(people),
        "addressable_people": len(addressable),
        "has_match_key_pct": rate,
        "platform_match_assumption_pct": assumption,
        "est_reachable": round(len(addressable) * assumption / 100),
        "net_new_to_crm": sum(1 for p in people if p["in_crm"] == "No"),
        "entry_rule": entry,
        "exit_rule": exit_,
        "refresh": refresh,
        "joined_7d_illustrative": joined,
        "left_7d_illustrative": left,
        "purpose": purpose,
        "account_list": "; ".join(sorted(acct_names)),
    })

for r in records:
    assert r["people_in_segment"] > 0, f"{r['segment']} is empty - the rule matches nobody"
    assert r["addressable_people"] <= r["people_in_segment"]
    assert r["accounts_in_segment"] > 0, f"{r['segment']} matches no accounts"
assert len({r["segment"] for r in records}) == len(records), "duplicate segment name"

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "vim_ad_segments.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(records)
json.dump(records, open(os.path.join(OUT, "vim_ad_segments.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"vim_ad_segments: {len(records)} segments")
for r in records:
    print(f"  {r['segment'][:44].ljust(44)} {r['destination'][:8].ljust(8)} "
          f"{r['accounts_in_segment']:>2} accts ({r['accounts_with_committee']} w/ committee)  "
          f"{r['addressable_people']:>2}/{r['people_in_segment']:>2} keyed  "
          f"~{r['est_reachable']:>2} reachable @ {r['platform_match_assumption_pct']}%")
