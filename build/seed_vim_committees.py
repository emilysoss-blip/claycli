# -*- coding: utf-8 -*-
"""Seed the sample enterprise buying committees (POC Build 2, first half).

SAMPLE DATA. People are invented. Titles and committee shapes are not - they are
the seats that actually decide provider-network and interoperability purchases at
a health system, a payer, and a risk-bearing enabler, which are three different
committees with three different economic buyers.

Only Tier 1 accounts from vim_accounts.csv get a committee. That constraint is the
build: Clay sources the committee for the accounts Build 1 has already qualified,
rather than everyone at every company in the CRM.

Field order in ROWS:
 0  account            must match an ultimate_parent_name/crm_name in vim_accounts.csv
 1  person_name
 2  title
 3  function           CIO / IT - Value-based care - Population health - Digital health
                       Clinical transformation - Partnerships - Product - Network & contracting
 4  seniority          C-level | SVP/EVP | VP | Director | Manager
 5  role_in_deal       Economic buyer | Technical buyer | Champion | Influencer | Gatekeeper
 6  in_crm             Yes if a HubSpot contact already exists on this person
 7  email_status       Verified | Catch-all | Not found
 8  linkedin_present   Yes | No   (drives the Build 3 ad-audience match rate)
 9  why_this_seat
"""
import csv, json, os
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data")
ACCOUNTS = json.load(open(os.path.join(OUT, "vim_accounts.json"), encoding="utf-8"))

IT, VBC, POP, DIG = "CIO / IT", "Value-based care", "Population health", "Digital health"
CLIN, PART, PROD, NET = "Clinical transformation", "Partnerships", "Product", "Network & contracting"
EB, TB, CH, IN, GK = "Economic buyer", "Technical buyer", "Champion", "Influencer", "Gatekeeper"

ROWS = [
    # ---- Northmark Health System - Epic, 4,200 providers ----
    ("Northmark Health System", "Priya Raghunathan", "SVP & Chief Information Officer", IT, "SVP/EVP", EB,
     "Yes", "Verified", "Yes",
     "Signs anything that touches the Epic estate. The enterprise agreement is hers."),
    ("Northmark Health System", "Marcus Delgado", "VP, Population Health", POP, "VP", CH,
     "No", "Verified", "Yes",
     "Owns the shared-savings result, so referral leakage is his number rather than an IT metric."),
    ("Northmark Health System", "Dr. Alice Yeung", "Chief Medical Information Officer", CLIN, "C-level", TB,
     "No", "Verified", "Yes",
     "Decides whether anything reaches the clinician's workflow. No CMIO sign-off, no adoption."),
    ("Northmark Health System", "Tobias Lindqvist", "Executive Director, Value-Based Care Contracting",
     VBC, "Director", IN, "No", "Catch-all", "Yes",
     "Holds the payer contracts that define what a referral out of network actually costs."),
    ("Northmark Health System", "Renee Abara", "Director, Digital Patient Access", DIG, "Director", IN,
     "Yes", "Verified", "Yes",
     "Runs scheduling and access. First to feel a broken referral, last to be asked."),

    # ---- Cascade Valley Health - Cerner parent over an athenahealth group ----
    ("Cascade Valley Health", "Deandra Whitfield", "Chief Digital & Information Officer", IT, "C-level", EB,
     "Yes", "Verified", "Yes", "Single owner of both the Cerner estate and the acquired athena instance."),
    ("Cascade Valley Health", "Hector Salinas", "VP, Clinical Integration", CLIN, "VP", CH,
     "No", "Verified", "Yes",
     "Chartered specifically to make the acquired group behave like the system. The two-EHR problem is his job."),
    ("Cascade Valley Health", "Wen Li Chen", "Director, Interoperability & Integration", IT, "Director", TB,
     "No", "Verified", "Yes", "Will ask the interface questions. Gets a technical veto in practice."),
    ("Cascade Valley Health", "Bridget Osei", "VP, Physician Network Development", PART, "VP", IN,
     "No", "Not found", "Yes",
     "Recruits and retains affiliated physicians - the population a network-integrity tool has to serve."),
    ("Cascade Valley Health", "Samir Bhatt", "Director, Population Health Analytics", POP, "Director", IN,
     "No", "Verified", "Yes", "Produces the leakage report today, by hand, quarterly."),

    # ---- Cascade Valley Health Plan - payer arm of a provider parent ----
    ("Cascade Valley Health Plan", "Nadia Petrov", "Chief Operating Officer", NET, "C-level", EB,
     "Yes", "Verified", "Yes", "Plan-side budget owner. Reports to the same system CEO as the provider arm."),
    ("Cascade Valley Health Plan", "Owen Kirkbride", "VP, Network Strategy & Contracting", NET, "VP", CH,
     "No", "Verified", "Yes",
     "Decides which providers are in and at what rate. Directory accuracy is his compliance exposure."),
    ("Cascade Valley Health Plan", "Talia Mercer", "Director, Payment Innovation", VBC, "Director", IN,
     "No", "Catch-all", "Yes", "Designs the full-risk MA arrangements the data has to support."),
    ("Cascade Valley Health Plan", "Jorge Almeida", "Manager, Provider Data Management", IT, "Manager", TB,
     "No", "Verified", "No",
     "Maintains the provider file. Knows exactly how wrong it is, and is never in the room."),
    ("Cascade Valley Health Plan", "Simone Duval", "Director, Member Digital Experience", DIG, "Director", IN,
     "No", "Verified", "Yes", "Owns the find-a-doctor experience, which is the directory in public."),

    # ---- Meridian Mutual Health Plan - 2.1M lives, MA-heavy ----
    ("Meridian Mutual Health Plan", "Gerald Okonkwo", "Chief Information Officer", IT, "C-level", EB,
     "Yes", "Verified", "Yes", "Enterprise vendor master agreements route through him."),
    ("Meridian Mutual Health Plan", "Katherine Vasquez", "SVP, Network Management", NET, "SVP/EVP", EB,
     "No", "Verified", "Yes",
     "The other economic buyer. Network spend is the largest line she controls; IT is a co-signer, not the owner."),
    ("Meridian Mutual Health Plan", "Ahmed Farouk", "VP, Value-Based Payment", VBC, "VP", CH,
     "No", "Verified", "Yes",
     "Accountable for moving lives into risk arrangements. Needs provider data he does not have."),
    ("Meridian Mutual Health Plan", "Lindsay Brauer", "Senior Director, Provider Data & Interoperability",
     IT, "Director", TB, "No", "Verified", "Yes",
     "Owns the provider directory and the CMS-0057 prior-auth API work. The technical gate."),
    ("Meridian Mutual Health Plan", "Rafael Moreno", "VP, Strategic Partnerships", PART, "VP", IN,
     "No", "Catch-all", "Yes", "Builds the health-system relationships a network product has to land inside."),
    ("Meridian Mutual Health Plan", "Iris Nakamura", "Director, Product", PROD, "Director", IN,
     "No", "Verified", "Yes", "Decides what ships to providers and on what roadmap."),

    # ---- Meridian Advantage - MA subsidiary with its own contracting ----
    ("Meridian Advantage", "Carl Dembinski", "President", NET, "C-level", EB,
     "No", "Verified", "Yes", "Separate P&L. Buys on his own timeline, not the parent's."),
    ("Meridian Advantage", "Yvette Cardoso", "VP, Provider Contracting", NET, "VP", CH,
     "No", "Verified", "Yes", "Delegated-risk contracts with Gulf Coast and Great Lakes sit with her."),
    ("Meridian Advantage", "Dr. Emeka Nwosu", "Director, Stars & Risk Adjustment", VBC, "Director", IN,
     "No", "Verified", "Yes", "Stars rating depends on care gaps closing, which depends on referrals landing."),
    ("Meridian Advantage", "Hana Sorensen", "Director, Clinical Programs", POP, "Director", IN,
     "No", "Not found", "Yes", "Runs the care-management programs that consume the network data."),

    # ---- Lakeshore Integrated Health - mid-integration ----
    ("Lakeshore Integrated Health", "Vincent Achebe", "Chief Information Officer", IT, "C-level", EB,
     "Yes", "Verified", "Yes", "Inherited a MEDITECH estate he has to converge onto Epic."),
    ("Lakeshore Integrated Health", "Margarethe Solberg", "VP, Integration Management Office", CLIN,
     "VP", CH, "No", "Verified", "Yes",
     "The seat that only exists because of the acquisition, with a funded mandate and a deadline. "
     "The single best entry point in this table."),
    ("Lakeshore Integrated Health", "Dr. Paul Ferreira", "Chief Medical Information Officer", CLIN,
     "C-level", TB, "No", "Verified", "Yes", "Clinical sign-off across two EHRs instead of one."),
    ("Lakeshore Integrated Health", "Shanice Boyd", "VP, Value-Based Care", VBC, "VP", IN,
     "No", "Catch-all", "Yes", "MSSP performance across a network that just grew by 720 providers."),
    ("Lakeshore Integrated Health", "Dmitri Kolarov", "Director, Referral Management", POP, "Director", CH,
     "No", "Verified", "No",
     "Running the merged referral process on spreadsheets right now. Loudest internal pain."),

    # ---- Pinnacle Provider Network - 6.4M lives ----
    ("Pinnacle Provider Network", "Eleanor Whitcomb", "EVP & Chief Information Officer", IT, "SVP/EVP", EB,
     "Yes", "Verified", "Yes", "Enterprise buyer at the largest account in the universe."),
    ("Pinnacle Provider Network", "Desmond Achterberg", "SVP, Provider Network Strategy", NET, "SVP/EVP", EB,
     "No", "Verified", "Yes", "Co-signer and the one with the business case."),
    ("Pinnacle Provider Network", "Rosalind Mbeki", "VP, Value-Based Solutions", VBC, "VP", CH,
     "No", "Verified", "Yes", "Sells risk arrangements to the four Tier 1 systems already in this table."),
    ("Pinnacle Provider Network", "Aaron Lieberman", "VP, Product", PROD, "VP", IN,
     "No", "Verified", "Yes", "Would rather build it. Has to be convinced early or he becomes the blocker."),
    ("Pinnacle Provider Network", "Fatima Zaidi", "Senior Director, Provider Data Governance", IT,
     "Director", TB, "No", "Verified", "Yes",
     "Owns directory accuracy and the No Surprises Act exposure that comes with it."),
    ("Pinnacle Provider Network", "Grant Molloy", "VP, Health System Partnerships", PART, "VP", IN,
     "No", "Catch-all", "Yes", "Holds the relationships at Northmark, Cascade Valley, Harborview and Sierra."),

    # ---- Sunbelt Care Partners - full-risk enabler ----
    ("Sunbelt Care Partners", "Anika Rasmussen", "Chief Technology Officer", IT, "C-level", EB,
     "Yes", "Verified", "Yes", "Buys and builds. Short evaluation cycles, high technical bar."),
    ("Sunbelt Care Partners", "Dr. Luis Ontiveros", "Chief Medical Officer", CLIN, "C-level", CH,
     "No", "Verified", "Yes", "Full risk on 220k lives makes leakage a P&L item he answers for."),
    ("Sunbelt Care Partners", "Bethany Kroll", "VP, Network Performance", NET, "VP", CH,
     "No", "Verified", "Yes", "Manages 1,900 affiliated providers Sunbelt does not employ."),
    ("Sunbelt Care Partners", "Emmanuel Sarpong", "Director, Data & Analytics", IT, "Director", TB,
     "No", "Verified", "No", "Will benchmark any vendor against what his team could ship in a quarter."),
    ("Sunbelt Care Partners", "Claire Bonnet", "VP, Payer Partnerships", PART, "VP", IN,
     "No", "Verified", "Yes", "Negotiates the delegated arrangements with Meridian Advantage and Pinnacle."),

    # ---- Harborview Health Partners - Epic-first, downside risk ----
    ("Harborview Health Partners", "Theodore Nwachukwu", "SVP & Chief Information Officer", IT, "SVP/EVP", EB,
     "Yes", "Verified", "Yes", "Signs. Also the most Epic-loyal buyer in the table."),
    ("Harborview Health Partners", "Dr. Miriam Castellanos", "Chief Population Health Officer", POP,
     "C-level", EB, "No", "Verified", "Yes",
     "Second economic buyer, and the one carrying downside risk. Her budget moves faster than IT's."),
    ("Harborview Health Partners", "Julian Amaechi", "VP, Clinical Transformation", CLIN, "VP", CH,
     "No", "Verified", "Yes", "Runs the change programme that adoption depends on."),
    ("Harborview Health Partners", "Kristin Halvorsen", "Director, Epic Applications", IT, "Director", GK,
     "No", "Verified", "Yes",
     "Will ask why this is not an Epic module. Treat as a gatekeeper and answer it in writing, early."),
    ("Harborview Health Partners", "Obinna Eze", "VP, ACO Operations", VBC, "VP", CH,
     "No", "Catch-all", "Yes", "Runs Harborview ACO LLC, the separate entity holding the REACH contract."),

    # ---- Summit Ridge Health - Epic plus a captive plan ----
    ("Summit Ridge Health", "Lorena Aguilar", "Chief Information Officer", IT, "C-level", EB,
     "No", "Verified", "Yes", "Buys for both the system and, in practice, the plan."),
    ("Summit Ridge Health", "Nathaniel Osborne", "VP, Value-Based Care", VBC, "VP", CH,
     "No", "Verified", "Yes", "Full-risk MA through the captive plan is his to make work."),
    ("Summit Ridge Health", "Adaeze Okafor", "Director, Care Management", POP, "Director", IN,
     "No", "Verified", "Yes", "Where the care-gap and referral work actually gets staffed."),
    ("Summit Ridge Health", "Felix Brunner", "Director, Digital Health", DIG, "Director", IN,
     "No", "Not found", "Yes", "Owns the patient-facing access layer."),

    # ---- Sierra Health Network - Cerner-to-Epic evaluation in flight ----
    ("Sierra Health Network", "Rosemary Tualagi", "Chief Information Officer", IT, "C-level", EB,
     "Yes", "Verified", "Yes", "Mid-evaluation on a platform migration. Every integration decision is open."),
    ("Sierra Health Network", "Gideon Barclay", "VP, EHR Transformation Program", CLIN, "VP", CH,
     "No", "Verified", "Yes",
     "Funded programme with a board-level deadline. Migration windows are when integration budget exists."),
    ("Sierra Health Network", "Dr. Camila Restrepo", "Chief Medical Information Officer", CLIN,
     "C-level", TB, "No", "Verified", "Yes", "Clinical authority over the target-state workflow."),
    ("Sierra Health Network", "Byron Haverford", "Executive Director, Managed Care Contracting", NET,
     "Director", IN, "No", "Catch-all", "Yes",
     "Holds the Pinnacle and Cascade Valley Health Plan contracts."),
    ("Sierra Health Network", "Priscilla Nkemdirim", "Director, Interoperability", IT, "Director", TB,
     "No", "Verified", "Yes", "Writes the integration requirements the migration will be built against."),
]

COLS = ["account", "account_crm_id", "account_org_type", "account_icp_score", "person_name", "title",
        "function", "seniority", "role_in_deal", "in_crm", "email_status", "linkedin_present",
        "why_this_seat"]

tier1 = {a["crm_name"]: a for a in ACCOUNTS
         if a["dedupe_status"] == "canonical" and a["icp_tier"] == "Tier 1"}

records = []
for (account, name, title, fn, sen, role, in_crm, email, li, why) in ROWS:
    assert account in tier1, f"{account} is not a Tier 1 canonical account in vim_accounts.csv"
    a = tier1[account]
    records.append({
        "account": account,
        "account_crm_id": a["crm_record_id"],
        "account_org_type": a["org_type"],
        "account_icp_score": a["icp_score"],
        "person_name": name,
        "title": title,
        "function": fn,
        "seniority": sen,
        "role_in_deal": role,
        "in_crm": in_crm,
        "email_status": email,
        "linkedin_present": li,
        "why_this_seat": why,
    })

# Every Tier 1 account must have a committee, and every committee needs an economic buyer.
by_acct = defaultdict(list)
for r in records:
    by_acct[r["account"]].append(r)
missing = sorted(set(tier1) - set(by_acct))
assert not missing, f"Tier 1 accounts with no committee: {missing}"
for acct, seats in by_acct.items():
    assert any(s["role_in_deal"] == "Economic buyer" for s in seats), f"{acct} has no economic buyer"
    # A committee needs someone who can stop it on technical grounds - a technical
    # buyer, or a gatekeeper like Harborview's Epic applications director.
    assert any(s["role_in_deal"] in ("Technical buyer", "Gatekeeper") for s in seats) \
        or len(seats) < 5, f"{acct} has no technical seat"

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "vim_buying_committees.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(records)
json.dump(records, open(os.path.join(OUT, "vim_buying_committees.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

new_to_crm = sum(1 for r in records if r["in_crm"] == "No")
verified = sum(1 for r in records if r["email_status"] == "Verified")
print(f"vim_buying_committees: {len(records)} seats across {len(by_acct)} Tier 1 accounts")
print(f"  {new_to_crm} of {len(records)} are net-new to the CRM ({round(100*new_to_crm/len(records))}%)")
print(f"  {verified} verified emails, {sum(1 for r in records if r['linkedin_present']=='Yes')} with LinkedIn")
print("  by function: " + ", ".join(f"{k} {v}" for k, v in Counter(r["function"] for r in records).most_common()))
