# -*- coding: utf-8 -*-
"""Seed the sample Vim enterprise account universe (POC Build 1).

SAMPLE DATA. Every organization below is fictional. The structures are real
patterns from healthcare GTM — provider-sponsored plans, employed physician
groups on a different EHR than their parent, MA subsidiaries with their own
contracting team, site-level records created by a web form — but no row
describes an actual company, and no number should be quoted externally.

The point of the file is the *shape* of the resolved table, so that the POC
can be pointed at Vim's real HubSpot export by swapping this seed for the
export and keeping every downstream column.

Field order in ROWS (25 columns, matching the shape of the airport table):
 0  crm_record_id        HubSpot-style numeric id
 1  crm_name             the name AS IT SITS IN THE CRM - deliberately messy
 2  domain               "" where the CRM has none
 3  org_type
 4  hierarchy_level      Ultimate parent | Subsidiary | Site | Standalone | Unresolved
 5  parent_org_name      immediate parent, "" if none
 6  ultimate_parent_name top of the tree, "" if unresolved
 7  ehr_primary
 8  ehr_confidence       High | Medium | Low | n/a
 9  providers_est        0 for payers
10  lives_covered_m      0 for pure providers
11  sites_est
12  hq_state
13  region
14  vbc_model
15  counterparties       payer relationships for providers, provider relationships for payers
16  dedupe_status        canonical | duplicate | merge_candidate | unresolved
17  duplicate_of         crm_record_id this collapses into, "" if canonical
18  dedupe_reason
19  icp_score            0-100
20  crm_owner
21  lifecycle_stage
22  open_deal            Yes | No
23  resolution_note      what the hierarchy resolution did to this row
24  icp_reason
"""
import csv, json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data")

HS = "Health system"
EPG = "Employed physician group"
IPG = "Independent provider group"
PSP = "Provider-sponsored health plan"
RP = "Regional payer"
NP = "National payer"
MA = "Medicare Advantage plan"
VBC = "Value-based care enabler"
ACO = "ACO / IPA"
DH = "Digital health vendor"
SVC = "Payer services"
UNK = "Unknown"

NA = "Not applicable (payer)"

ROWS = [
    # ---- Northmark Health System: 4 CRM records, 2 sellable orgs, 1 parent ----
    (7011824, "Northmark Health System", "northmarkhealth.org", HS, "Ultimate parent", "",
     "Northmark Health System", "Epic", "High", 4200, 0.0, 38, "IL", "Midwest",
     "Shared savings + full-risk MA", "Meridian Mutual Health Plan; Pinnacle Provider Network",
     "canonical", "", "", 92, "Daryl", "Opportunity", "Yes",
     "Top of the tree. The Epic enterprise agreement and all IT contracting sit here, not at the hospitals.",
     "Epic at 4,200 providers with a full-risk MA book, and one signing authority for the whole system."),
    (7011825, "NORTHMARK HEALTH SYS", "northmarkhealth.org", HS, "Ultimate parent", "",
     "Northmark Health System", "Epic", "High", 4200, 0.0, 38, "IL", "Midwest",
     "Shared savings + full-risk MA", "Meridian Mutual Health Plan; Pinnacle Provider Network",
     "duplicate", "7011824", "Same domain and same Clay Company ID; name normalizes to the canonical record.",
     92, "Ravid", "Lead", "No",
     "Collapses into 7011824. Two owners on one company is how the same CIO gets mailed twice.",
     "Scored on the canonical record."),
    (7011901, "Northmark Medical Group", "northmarkmedicalgroup.com", EPG, "Subsidiary",
     "Northmark Health System", "Northmark Health System", "Epic", "High", 1150, 0.0, 62, "IL", "Midwest",
     "Shared savings", "Meridian Mutual Health Plan", "canonical", "", "", 74, "Daryl", "Lead", "No",
     "Distinct domain, so it survives dedupe - but it is not a separate sale. Same Epic instance, same parent budget.",
     "Real provider volume, no independent signing authority. Sell through the parent."),
    (7012044, "Northmark Heart & Vascular Inst.", "northmarkhealth.org", "Service line / site", "Site",
     "Northmark Medical Group", "Northmark Health System", "Epic", "High", 180, 0.0, 6, "IL", "Midwest",
     "Shared savings", "", "merge_candidate", "7011901",
     "Service line on the parent domain, created by a conference-badge import. Not an account.",
     31, "Unassigned", "Lead", "No",
     "Merged into 7011901 as an activity, not kept as a company.",
     "Below any threshold that matters; a service line does not buy network infrastructure."),

    # ---- Cascade Valley Health: payer and provider under one parent, two EHRs ----
    (7013310, "Cascade Valley Health", "cascadevalleyhealth.org", HS, "Ultimate parent", "",
     "Cascade Valley Health", "Oracle Health (Cerner)", "High", 2800, 0.0, 21, "WA", "West",
     "Shared savings", "Cascade Valley Health Plan; Pinnacle Provider Network",
     "canonical", "", "", 88, "Ravid", "Opportunity", "Yes",
     "Parent of both a Cerner provider estate and its own health plan.",
     "Owns both sides of the referral, which is the clearest place to show network integrity."),
    (7013402, "Cascade Valley Physicians Network", "cvphysicians.com", EPG, "Subsidiary",
     "Cascade Valley Health", "Cascade Valley Health", "athenahealth", "Medium", 640, 0.0, 44, "WA", "West",
     "Shared savings", "Cascade Valley Health Plan", "canonical", "", "", 81, "Ravid", "Lead", "No",
     "Acquired group, still on athenahealth while the parent is Cerner. Two EHRs under one logo.",
     "The EHR split is the wedge: neither instance sees the other's referrals."),
    (7013455, "Cascade Valley Health Plan", "cvhealthplan.com", PSP, "Subsidiary",
     "Cascade Valley Health", "Cascade Valley Health", NA, "n/a", 0, 0.41, 3, "WA", "West",
     "Full-risk MA", "Cascade Valley Health; Blue Ridge Health Collective",
     "canonical", "", "", 90, "Daryl", "Opportunity", "Yes",
     "Payer subsidiary of a provider parent. Separate contracting, same ultimate budget owner.",
     "Full-risk MA lives plus a captive provider network - both halves of the ICP in one family."),

    # ---- Meridian Mutual: regional payer, MA subsidiary, and an unresolvable stub ----
    (7014120, "Meridian Mutual Health Plan", "meridianmutual.com", RP, "Ultimate parent", "",
     "Meridian Mutual Health Plan", NA, "n/a", 0, 2.10, 11, "OH", "Midwest",
     "MA-heavy + commercial", "Northmark Health System; Lakeshore Integrated Health; Keystone Health Alliance",
     "canonical", "", "", 95, "Daryl", "Opportunity", "Yes",
     "Top of the tree. Enterprise network strategy and vendor master agreements sit here.",
     "2.1M lives, MA-heavy, and contracts with three other Tier 1 accounts in this same table."),
    (7014121, "Meridian Mutual Hlth Pln - OH", "meridianmutual.com", RP, "Ultimate parent", "",
     "Meridian Mutual Health Plan", NA, "n/a", 0, 2.10, 11, "OH", "Midwest",
     "MA-heavy + commercial", "", "duplicate", "7014120",
     "Abbreviated state-suffixed copy on the same domain. Same Company ID.",
     95, "Ravid", "Lead", "No", "Collapses into 7014120.", "Scored on the canonical record."),
    (7014188, "Meridian Advantage", "meridianadvantage.com", MA, "Subsidiary",
     "Meridian Mutual Health Plan", "Meridian Mutual Health Plan", NA, "n/a", 0, 0.68, 4, "OH", "Midwest",
     "Full-risk MA", "Gulf Coast Physician Alliance; Great Lakes Care Alliance",
     "canonical", "", "", 87, "Daryl", "Opportunity", "Yes",
     "Separate legal entity with its own provider contracting team. A real second seat, not a duplicate.",
     "Delegated-risk MA book with its own contracting leadership - buys on its own timeline."),
    (7014210, "meridian mutual (do not use)", "", UNK, "Unresolved", "", "",
     UNK, "Low", 0, 0.0, 0, "OH", "Midwest", "", "", "unresolved", "7014120",
     "No domain and no Company ID. Matched to 7014120 on normalized name plus owner, flagged for a human.",
     0, "Ravid", "Other", "No",
     "The honest outcome: name-only match, held for review rather than merged automatically.",
     "Cannot be scored without a domain."),

    # ---- Lakeshore: the M&A case the CRM cannot know about ----
    (7015001, "Lakeshore Integrated Health", "lakeshoreintegrated.org", HS, "Ultimate parent", "",
     "Lakeshore Integrated Health", "Epic", "High", 3350, 0.0, 27, "MI", "Midwest",
     "Shared savings + MSSP", "Meridian Mutual Health Plan; Prairie States Health Plan",
     "canonical", "", "", 90, "Ravid", "Opportunity", "Yes",
     "Acquirer. Gained 720 providers and a MEDITECH estate this year.",
     "Epic parent absorbing a MEDITECH system - a live integration problem with a budget behind it."),
    (7015219, "Ridgeline Community Health", "ridgelinecommunity.org", HS, "Subsidiary",
     "Lakeshore Integrated Health", "Lakeshore Integrated Health", "MEDITECH", "Medium", 720, 0.0, 9,
     "MI", "Midwest", "MSSP", "Prairie States Health Plan", "canonical", "", "", 79, "Daryl", "Lead", "No",
     "Reparented by the M&A signal, not by anything in HubSpot - the CRM still had it as an unrelated parent.",
     "Still a real buyer for integration work, but the economics now sit one level up."),
    (7015277, "Ridgeline Med Group", "ridgelinecommunity.org", EPG, "Site",
     "Ridgeline Community Health", "Lakeshore Integrated Health", "MEDITECH", "Medium", 210, 0.0, 14,
     "MI", "Midwest", "MSSP", "", "merge_candidate", "7015219",
     "Same domain as its parent record, one hierarchy level too deep to be its own account.",
     29, "Unassigned", "Lead", "No", "Merged into 7015219.",
     "A sub-unit of a subsidiary. Two levels below where anyone signs."),

    # ---- Pinnacle: national payer ----
    (7016300, "Pinnacle Provider Network", "pinnacleprovider.com", NP, "Ultimate parent", "",
     "Pinnacle Provider Network", NA, "n/a", 0, 6.40, 19, "CT", "Northeast",
     "MA + commercial + exchange",
     "Northmark Health System; Cascade Valley Health; Harborview Health Partners; Sierra Health Network",
     "canonical", "", "", 97, "Ravid", "Opportunity", "Yes",
     "Largest node in the table. Contracts with four other Tier 1 accounts here.",
     "6.4M lives and the widest provider overlap in the universe - the highest-leverage single account."),
    (7016344, "Pinnacle Health Solutions", "pinnaclehealthsolutions.com", SVC, "Subsidiary",
     "Pinnacle Provider Network", "Pinnacle Provider Network", NA, "n/a", 0, 0.0, 6, "CT", "Northeast",
     "n/a", "Pinnacle Provider Network", "canonical", "", "", 72, "Ravid", "Lead", "No",
     "Services arm. Buys tooling on behalf of the plan, so it is a channel into 7016300 rather than a target.",
     "No lives of its own; scored as an influence path, not a book of business."),
    (7016390, "Pinnacle Provider Ntwk.", "pinnacleprovider.com", NP, "Ultimate parent", "",
     "Pinnacle Provider Network", NA, "n/a", 0, 6.40, 19, "CT", "Northeast",
     "MA + commercial + exchange", "", "duplicate", "7016300",
     "Abbreviated duplicate on the same domain, created by a list import.",
     97, "Daryl", "Lead", "No", "Collapses into 7016300.", "Scored on the canonical record."),

    # ---- Sunbelt: VBC enabler ----
    (7017410, "Sunbelt Care Partners", "sunbeltcare.com", VBC, "Ultimate parent", "",
     "Sunbelt Care Partners", "athenahealth", "High", 1900, 0.22, 140, "TX", "South",
     "Full-risk", "Meridian Advantage; Pinnacle Provider Network",
     "canonical", "", "", 93, "Daryl", "Opportunity", "Yes",
     "Affiliated-network model: 1,900 providers it does not employ, delegated risk on 220k lives.",
     "Full-risk enabler with delegated lives - referral leakage is a direct cost line, not a KPI."),
    (7017455, "Sunbelt Primary Care - Houston", "sunbeltcare.com", "Clinic site", "Site",
     "Sunbelt Care Partners", "Sunbelt Care Partners", "athenahealth", "High", 34, 0.0, 6, "TX", "South",
     "Full-risk", "", "merge_candidate", "7017410",
     "One market's clinics on the parent domain. A location, not a company.",
     24, "Unassigned", "Lead", "No", "Merged into 7017410.", "A site record."),

    # ---- Gulf Coast ----
    (7018220, "Gulf Coast Physician Alliance", "gulfcoastalliance.org", ACO, "Ultimate parent", "",
     "Gulf Coast Physician Alliance", "eClinicalWorks", "Medium", 1450, 0.15, 96, "FL", "Southeast",
     "Shared savings + ACO REACH", "Meridian Advantage; Pinnacle Provider Network",
     "canonical", "", "", 84, "Daryl", "Opportunity", "Yes",
     "Independent alliance - no health-system parent above it, so it signs for itself.",
     "Tier 2 by a point. ACO REACH participation is the thing that would move it up."),
    (7018290, "Gulf Coast Physician Alliance (ACO)", "gulfcoastalliance.org", ACO, "Ultimate parent", "",
     "Gulf Coast Physician Alliance", "eClinicalWorks", "Medium", 1450, 0.15, 96, "FL", "Southeast",
     "Shared savings + ACO REACH", "", "duplicate", "7018220",
     "Parenthetical-suffix duplicate. Same domain, same Company ID.",
     84, "Ravid", "Lead", "No", "Collapses into 7018220.", "Scored on the canonical record."),

    # ---- Harborview: the ACO is a seat, not a duplicate ----
    (7019100, "Harborview Health Partners", "harborviewhp.org", HS, "Ultimate parent", "",
     "Harborview Health Partners", "Epic", "High", 5100, 0.0, 44, "MA", "Northeast",
     "Shared savings + downside risk", "Pinnacle Provider Network; Meridian Mutual Health Plan",
     "canonical", "", "", 94, "Ravid", "Opportunity", "Yes",
     "Largest provider estate in the table.",
     "5,100 providers on Epic with downside risk already taken. Buys for outcomes, not for reporting."),
    (7019166, "Harborview Physician Organization", "harborviewpo.org", EPG, "Subsidiary",
     "Harborview Health Partners", "Harborview Health Partners", "Epic", "High", 2300, 0.0, 88,
     "MA", "Northeast", "Shared savings", "Pinnacle Provider Network", "canonical", "", "", 80,
     "Ravid", "Lead", "No",
     "Own domain, own CMIO, same Epic instance. Kept as a subsidiary, not merged.",
     "Where clinical workflow decisions actually get made, even though the money is upstairs."),
    (7019188, "Harborview ACO LLC", "harborviewhp.org", ACO, "Subsidiary",
     "Harborview Health Partners", "Harborview Health Partners", "Epic", "High", 0, 0.09, 1,
     "MA", "Northeast", "ACO REACH", "Pinnacle Provider Network", "canonical", "", "", 76,
     "Daryl", "Lead", "No",
     "Same domain as the parent but a separate legal entity with its own VBC leadership. NOT a duplicate - "
     "this is the row a naive domain-based dedupe destroys.",
     "Holds the risk contract. Small on headcount, decisive on whether VBC tooling gets bought."),

    # ---- mid-market and out-of-ICP texture ----
    (7020010, "Desert Sky Medical Group", "desertskymed.com", IPG, "Standalone", "",
     "Desert Sky Medical Group", "NextGen", "Medium", 380, 0.0, 29, "AZ", "Mountain West",
     "FFS + shared savings", "Pinnacle Provider Network", "canonical", "", "", 61,
     "Daryl", "Lead", "No", "No parent found, and none exists. A genuine standalone.",
     "Tier 3: real providers, no risk contract, so no burning reason to buy this year."),
    (7020044, "Desert Sky Med Grp", "desertskymed.com", IPG, "Standalone", "",
     "Desert Sky Medical Group", "NextGen", "Medium", 380, 0.0, 29, "AZ", "Mountain West",
     "FFS + shared savings", "", "duplicate", "7020010",
     "Abbreviated duplicate on the same domain.", 61, "Ravid", "Lead", "No",
     "Collapses into 7020010.", "Scored on the canonical record."),
    (7021200, "Keystone Health Alliance", "keystonehealthalliance.org", ACO, "Ultimate parent", "",
     "Keystone Health Alliance", "Mixed (Epic / NextGen / eCW)", "Low", 2200, 0.0, 165, "PA", "Northeast",
     "Shared savings", "Meridian Mutual Health Plan", "canonical", "", "", 83, "Ravid", "Opportunity", "Yes",
     "Alliance of independent practices. 165 sites, no single EHR, no single IT owner.",
     "The mixed-EHR case: high provider count, low confidence on stack, so discovery matters more than scoring."),
    (7021255, "Keystone Care Network", "keystonecarenetwork.org", ACO, "Subsidiary",
     "Keystone Health Alliance", "Keystone Health Alliance", "Mixed (Epic / NextGen / eCW)", "Low",
     900, 0.06, 71, "PA", "Northeast", "MSSP", "Meridian Mutual Health Plan",
     "canonical", "", "", 70, "Daryl", "Lead", "No",
     "The risk-bearing entity inside the alliance.",
     "Tier 2 floor. Holds the MSSP contract but has to ask the alliance for budget."),
    (7022400, "Evergreen Digital Health", "evergreendigitalhealth.com", DH, "Standalone", "",
     "Evergreen Digital Health", "Not applicable (vendor)", "n/a", 0, 0.0, 2, "CA", "West",
     "n/a", "", "canonical", "", "", 34, "Ravid", "Lead", "No",
     "Resolved cleanly and still does not belong in pipeline.",
     "Out of ICP: a vendor, not a buyer of provider-network data. Partner motion, not a deal."),
    (7023100, "Rio Grande Family Care", "riograndefamilycare.com", IPG, "Standalone", "",
     "Rio Grande Family Care", "eClinicalWorks", "Medium", 46, 0.0, 4, "NM", "Mountain West",
     "FFS only", "", "canonical", "", "", 22, "Unassigned", "Lead", "No",
     "Correctly resolved, correctly excluded.",
     "Out of ICP: 46 providers, no risk contract. Suppress from paid audiences too."),
    (7023240, "Allegheny Valley Physicians", "avphysicians.com", IPG, "Standalone", "",
     "Allegheny Valley Physicians", "NextGen", "Medium", 210, 0.0, 18, "PA", "Northeast",
     "FFS + shared savings", "Meridian Mutual Health Plan", "canonical", "", "", 55,
     "Daryl", "Lead", "No", "Standalone.", "Tier 3. Keep in nurture, out of the sales committee build."),
    (7023388, "Blue Ridge Health Collective", "brhealthcollective.org", ACO, "Ultimate parent", "",
     "Blue Ridge Health Collective", "athenahealth", "Medium", 690, 0.04, 52, "NC", "Southeast",
     "Shared savings", "Cascade Valley Health Plan", "canonical", "", "", 68,
     "Ravid", "Lead", "No", "Standalone collective.",
     "Tier 3 on size, but it contracts with a Tier 1 plan - a referral path worth keeping visible."),
    (7023455, "Prairie States Health Plan", "prairiestateshp.com", RP, "Ultimate parent", "",
     "Prairie States Health Plan", NA, "n/a", 0, 0.55, 5, "IA", "Midwest",
     "MA + Medicaid", "Lakeshore Integrated Health; Ridgeline Community Health",
     "canonical", "", "", 79, "Daryl", "Opportunity", "Yes",
     "Regional plan, no parent above it.",
     "Tier 2: 550k lives, and it is the plan on both sides of the Lakeshore/Ridgeline merger."),
    (7023456, "Prairie States Hlth Pln", "prairiestateshp.com", RP, "Ultimate parent", "",
     "Prairie States Health Plan", NA, "n/a", 0, 0.55, 5, "IA", "Midwest",
     "MA + Medicaid", "", "duplicate", "7023455",
     "Abbreviated duplicate on the same domain.", 79, "Ravid", "Lead", "No",
     "Collapses into 7023455.", "Scored on the canonical record."),
    (7023501, "Coastal Carolina Health System", "coastalcarolinahealth.org", HS, "Ultimate parent", "",
     "Coastal Carolina Health System", "Oracle Health (Cerner)", "High", 1320, 0.0, 14, "SC", "Southeast",
     "Shared savings", "Pinnacle Provider Network", "canonical", "", "", 77, "Ravid", "Lead", "No",
     "Parent of one employed group.",
     "Tier 2: Cerner shop with a live consolidation story but no risk contract yet."),
    (7023577, "Coastal Carolina Medical Partners", "coastalcarolinahealth.org", EPG, "Subsidiary",
     "Coastal Carolina Health System", "Coastal Carolina Health System", "Oracle Health (Cerner)", "High",
     610, 0.0, 33, "SC", "Southeast", "Shared savings", "Pinnacle Provider Network",
     "canonical", "", "", 64, "Ravid", "Lead", "No",
     "Same domain as the parent, but a distinct employed group with its own leadership. Kept, flagged for review.",
     "Tier 3 alone; only interesting as part of the parent's footprint."),
    (7023610, "Summit Ridge Health", "summitridgehealth.org", HS, "Ultimate parent", "",
     "Summit Ridge Health", "Epic", "High", 2450, 0.0, 19, "CO", "Mountain West",
     "Full-risk MA + shared savings", "Summit Ridge Health Plan; Pinnacle Provider Network",
     "canonical", "", "", 85, "Daryl", "Opportunity", "Yes",
     "Parent of its own health plan.",
     "Just into Tier 1: Epic, 2,450 providers, and a captive plan taking full MA risk."),
    (7023688, "Summit Ridge Health Plan", "summitridgehp.com", PSP, "Subsidiary",
     "Summit Ridge Health", "Summit Ridge Health", NA, "n/a", 0, 0.19, 2, "CO", "Mountain West",
     "Full-risk MA", "Summit Ridge Health; Desert Sky Medical Group",
     "canonical", "", "", 82, "Daryl", "Lead", "No",
     "Payer subsidiary. Contracts with Desert Sky, which is also in this table.",
     "Tier 2: small book, but full risk and a named provider network to keep inside."),
    (7023740, "Great Lakes Care Alliance", "greatlakescare.org", ACO, "Standalone", "",
     "Great Lakes Care Alliance", "Mixed (Epic / athenahealth)", "Low", 1080, 0.09, 74, "WI", "Midwest",
     "MSSP", "Meridian Advantage", "canonical", "", "", 72, "Ravid", "Lead", "No",
     "Standalone alliance.", "Tier 2: MSSP contract with a Tier 1 MA plan, mixed stack."),
    (7023800, "Tidewater Physician Group", "tidewaterpg.com", IPG, "Standalone", "",
     "Tidewater Physician Group", "Epic (Community Connect)", "Medium", 430, 0.0, 26, "VA", "South",
     "Shared savings", "Pinnacle Provider Network", "canonical", "", "", 63, "Daryl", "Lead", "No",
     "Independent, but running on a host system's Epic instance via Community Connect - so its IT decisions "
     "are partly someone else's.", "Tier 3. The Community Connect dependency is the detail to qualify on."),
    (7023844, "Tidewater Physicians Grp.", "tidewaterpg.com", IPG, "Standalone", "",
     "Tidewater Physician Group", "Epic (Community Connect)", "Medium", 430, 0.0, 26, "VA", "South",
     "Shared savings", "", "duplicate", "7023800",
     "Pluralized copy - \"Physicians\" vs \"Physician\" - so name normalization does NOT collapse it. "
     "Only the shared domain and Company ID do.", 63, "Ravid", "Lead", "No",
     "Collapses into 7023800, but only because the match runs on the Company ID rather than the string.",
     "Scored on the canonical record."),
    (7023900, "Sierra Health Network", "sierrahealthnetwork.org", HS, "Ultimate parent", "",
     "Sierra Health Network", "Oracle Health (Cerner)", "High", 3900, 0.0, 31, "CA", "West",
     "Shared savings + full-risk MA", "Pinnacle Provider Network; Cascade Valley Health Plan",
     "canonical", "", "", 89, "Ravid", "Opportunity", "Yes",
     "Parent of a medical foundation on a separate domain.",
     "Tier 1: 3,900 providers, full-risk MA, and an active Cerner-to-Epic evaluation."),
    (7023955, "Sierra Medical Foundation", "sierramedfoundation.org", EPG, "Subsidiary",
     "Sierra Health Network", "Sierra Health Network", "Oracle Health (Cerner)", "High", 1600, 0.0, 58,
     "CA", "West", "Shared savings", "Pinnacle Provider Network", "canonical", "", "", 75,
     "Ravid", "Lead", "No",
     "California foundation model - legally separate from the system, practically part of it. "
     "Different domain, so only the hierarchy pass catches it.",
     "Tier 2: the foundation employs the physicians, so clinical adoption runs through here."),
    (7024010, "Unknown - web form 4/12", "", UNK, "Unresolved", "", "",
     UNK, "n/a", 0, 0.0, 0, "", "", "", "", "unresolved", "",
     "No company name, no domain, no Company ID. Nothing to resolve against.",
     0, "Unassigned", "Other", "No",
     "Left unresolved on purpose. Guessing a parent here is how bad hierarchy data gets created.",
     "Cannot be scored."),
]

SUFFIX = re.compile(
    r"\b(inc|inc\.|llc|llc\.|l\.l\.c\.|corp|corp\.|co|co\.|ltd|ltd\.|pc|p\.c\.|"
    r"pllc|lp|l\.p\.|the)\b", re.I)
ABBREV = {
    "hlth": "health", "pln": "plan", "sys": "system", "grp": "group", "med": "medical",
    "ntwk": "network", "hosp": "hospital", "inst": "institute", "phys": "physician",
    "svcs": "services", "mgmt": "management", "reg": "regional", "ctr": "center",
}


def normalize(name):
    """The normalization the dedupe pass actually runs. Deterministic, no model call."""
    s = name.lower()
    s = re.sub(r"\(.*?\)", " ", s)          # drop parentheticals: "(ACO)", "(do not use)"
    s = re.sub(r"[^a-z0-9&\s-]", " ", s)    # drop punctuation, keep & and -
    s = re.sub(r"\s+-\s+.*$", "", s)        # drop " - OH", " - Houston" style qualifiers
    s = SUFFIX.sub(" ", s)
    s = " ".join(ABBREV.get(w, w) for w in s.split())
    s = re.sub(r"[&]", "and", s)
    return " ".join(s.split())


def tier(score):
    if score >= 85:
        return "Tier 1"
    if score >= 70:
        return "Tier 2"
    if score >= 50:
        return "Tier 3"
    if score > 0:
        return "Out of ICP"
    return "Unscored"


COLS = [
    "crm_record_id", "crm_name", "normalized_name", "domain", "org_type", "hierarchy_level",
    "parent_org_name", "ultimate_parent_name", "ehr_primary", "ehr_confidence", "providers_est",
    "lives_covered_m", "sites_est", "hq_state", "region", "vbc_model", "counterparties",
    "dedupe_status", "duplicate_of", "matched_on", "dedupe_reason", "icp_score", "icp_tier", "crm_owner",
    "lifecycle_stage", "open_deal", "resolution_note", "icp_reason",
]

records = []
for r in ROWS:
    (crm_id, crm_name, domain, org_type, level, parent, ultimate, ehr, ehr_conf, providers,
     lives, sites, state, region, vbc, counter, status, dup_of, dup_reason, score, owner,
     stage, deal, res_note, icp_reason) = r
    records.append({
        "crm_record_id": crm_id,
        "crm_name": crm_name,
        "normalized_name": normalize(crm_name),
        "domain": domain,
        "org_type": org_type,
        "hierarchy_level": level,
        "parent_org_name": parent,
        "ultimate_parent_name": ultimate,
        "ehr_primary": ehr,
        "ehr_confidence": ehr_conf,
        "providers_est": providers,
        "lives_covered_m": lives,
        "sites_est": sites,
        "hq_state": state,
        "region": region,
        "vbc_model": vbc,
        "counterparties": counter,
        "dedupe_status": status,
        "duplicate_of": dup_of,
        "dedupe_reason": dup_reason,
        "icp_score": score,
        "icp_tier": tier(score) if status in ("canonical",) else
                    ("Unscored" if status == "unresolved" else tier(score)),
        "crm_owner": owner,
        "lifecycle_stage": stage,
        "open_deal": deal,
        "resolution_note": res_note,
        "icp_reason": icp_reason,
    })

# ---- how each collapsed record was actually matched -------------------------
# Worth surfacing: string normalization alone does not catch every duplicate.
# Tidewater's copy pluralizes "Physician", so only the shared domain and Clay
# Company ID collapse it. That is the argument for resolving on the ID, not the name.
_by_id = {r["crm_record_id"]: r for r in records}
for r in records:
    if not r["duplicate_of"]:
        r["matched_on"] = ""
        continue
    target = _by_id[int(r["duplicate_of"])]
    same_name = r["normalized_name"] == target["normalized_name"]
    same_domain = bool(r["domain"]) and r["domain"] == target["domain"]
    if r["dedupe_status"] == "unresolved":
        r["matched_on"] = "Name + record owner only - held for human review"
    elif r["dedupe_status"] == "merge_candidate":
        r["matched_on"] = "Hierarchy - site rolls into its parent record"
    elif same_name and same_domain:
        r["matched_on"] = "Normalized name + domain + Company ID"
    elif same_domain:
        r["matched_on"] = "Domain + Company ID (name normalization misses it)"
    else:
        r["matched_on"] = "Company ID"

# ---- integrity checks: the seed should not be able to lie about its own shape ----
ids = [r["crm_record_id"] for r in records]
assert len(ids) == len(set(ids)), "duplicate crm_record_id in the seed"
by_id = {r["crm_record_id"]: r for r in records}
for r in records:
    if r["duplicate_of"]:
        assert int(r["duplicate_of"]) in by_id, f"{r['crm_record_id']} points at a missing record"
        assert by_id[int(r["duplicate_of"])]["dedupe_status"] == "canonical", \
            f"{r['crm_record_id']} collapses into a non-canonical record"
canonical_names = {r["ultimate_parent_name"] for r in records if r["dedupe_status"] == "canonical"}
for r in records:
    if r["dedupe_status"] == "canonical" and r["parent_org_name"]:
        assert r["parent_org_name"] in {x["crm_name"] for x in records}, \
            f"{r['crm_name']} names a parent that is not a record: {r['parent_org_name']}"

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "vim_accounts.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(records)
json.dump(records, open(os.path.join(OUT, "vim_accounts.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

canon = [r for r in records if r["dedupe_status"] == "canonical"]
dupes = [r for r in records if r["dedupe_status"] == "duplicate"]
merges = [r for r in records if r["dedupe_status"] == "merge_candidate"]
unres = [r for r in records if r["dedupe_status"] == "unresolved"]
parents = sorted({r["ultimate_parent_name"] for r in canon if r["ultimate_parent_name"]})
t1 = [r for r in canon if r["icp_tier"] == "Tier 1"]

print(f"vim_accounts: {len(records)} CRM records -> {len(canon)} organizations")
print(f"  {len(dupes)} duplicates, {len(merges)} site-level merges, {len(unres)} unresolved")
print(f"  {len(parents)} ultimate parent groups, {len(t1)} Tier 1")
