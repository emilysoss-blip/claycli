# -*- coding: utf-8 -*-
"""
Per-domain Clay match quality for the cohort, derived from the raw search captures.

The question this answers: if you enrich this row by its domain, what do you actually get?
Counts are lower bounds wherever the capture paged out before the result set ended
(has_more = true); that is recorded per domain rather than smoothed over.
"""
import csv, json, os, re
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")

accounts = json.load(open(os.path.join(BASE, "data", "accounts.json"), encoding="utf-8"))
entities = json.load(open(os.path.join(BASE, "data", "divisions.json"), encoding="utf-8"))
dom_to_acct = {}
for e in entities:
    dom_to_acct.setdefault(e["entity_domain"], e["account_key"])
for a in accounts:
    dom_to_acct.setdefault(a["account_domain"], a["account_key"])

STALE = re.compile(r"inactive|no longer active|closed|defunct|stub|'now part of|is now", re.I)
CONTRA = re.compile(r"contradicts|size band|is wrong|wrong by", re.I)

seen = defaultdict(list)
for fname in ("clay_identity_healthcare.json", "clay_identity_fs_mfg.json"):
    cap = json.load(open(os.path.join(RAW, fname), encoding="utf-8"))
    for e in cap["entities"]:
        seen[e["domain"]].append(e)

# Aggregated rows in the capture stand for 12 small JHU centres; count them as 12.
AGGREGATED = {"jhu.edu": 11}

# Domains settled by the follow-up query (data/raw/clay_identity_followup.json) and the
# LinkedIn-pinned people search (data/raw/clay_talent_leaders_batch4_pinned.json).
OVERRIDES = {
 "kaiserpermanente.org": dict(returned=2, parent="no", stale=2, wrong=0, contradictions=0, lower_bound="no",
    match_class="no_usable_match",
    finding="Two placeholder pages (type Partnership, industry 'Blockchain Services', no headcount).",
    fix="Enrich on linkedin.com/company/kaiser-permanente, which resolves to Kaiser Permanente (kp.org, 139,271)."),
 "marshmclennan.com": dict(returned=1, parent="no", stale=0, wrong=1, contradictions=0, lower_bound="no",
    match_class="wrong_company",
    finding="Resolves to 'Celedinas Insurance Group', 31 employees, carrying Marsh McLennan boilerplate.",
    fix="Drop the domain. The parent is now Marsh on marsh.com (linkedin.com/company/marshglobal)."),
 "mercer.com": dict(returned=3, parent="no", stale=0, wrong=0, contradictions=0, lower_bound="no",
    match_class="satellite_only",
    finding="Regional pages only: Mercer UK (270), Mercer Latinoamerica (125), Mercer Sverige (23).",
    fix="The Mercer LinkedIn page itself now reads 'Marsh People Solutions' (96). Treat Mercer as a Marsh division and confirm in Salesforce whether it is a separate account."),
 "commonspirit.org": dict(returned=10, parent="no", stale=0, wrong=0, contradictions=8, lower_bound="yes",
    match_class="parent_missing_by_domain",
    finding="10+ member hospitals and regions, never the parent. 8 of the 10 carry size band '10,001+' on 114-1,090 employees (Dignity Health California: 29 hospitals, 293 employees).",
    fix="Enrich on linkedin.com/company/commonspirithealth, which resolves to CommonSpirit Health (48,637) on commonspirit.careers."),
}

FIX = {
 "clean": "Enrich by domain.",
 "clean_with_stale_pages": "Enrich by domain, then suppress the stale pages in divisions.csv so none of them takes a contact.",
 "shared_domain": "Enrich each hiring entity by its LinkedIn URL from divisions.csv; the domain alone cannot choose between them.",
}

rows = []
for dom in sorted(set(seen) | set(OVERRIDES)):
    acct = dom_to_acct.get(dom, "")
    if dom in OVERRIDES:
        o = OVERRIDES[dom]
        rows.append({"domain": dom, "account_key": acct, "entities_returned": o["returned"],
                     "count_is_lower_bound": o["lower_bound"], "parent_returned": o["parent"],
                     "stale_or_inactive_pages": o["stale"], "wrong_company_pages": o["wrong"],
                     "size_or_revenue_contradictions": o["contradictions"],
                     "match_class": o["match_class"], "finding": o["finding"], "fix": o["fix"]})
        continue
    ents = seen[dom]
    n = len(ents) + AGGREGATED.get(dom, 0)
    stale = sum(1 for e in ents if STALE.search(e["flag"] + " " + e["name"]))
    contra = sum(1 for e in ents if CONTRA.search(e["flag"]))
    live = n - stale
    if dom == "ge.com":
        cls, finding = "stale_parent", "Legacy GE page (95,424) whose own text says content moved to GE Aerospace and GE Vernova; plus GE Digital."
        fix = "Never enrich on ge.com. Route GE Digital to GE Vernova by LinkedIn URL."
    elif live <= 1:
        cls = "clean" if stale == 0 else "clean_with_stale_pages"
        finding = "; ".join(f"{e['name']} ({e['employees']:,})" if e["employees"] else e["name"] for e in ents)
        fix = FIX[cls]
    else:
        cls = "shared_domain"
        top = sorted([e for e in ents if e["employees"]], key=lambda e: -e["employees"])[:4]
        finding = f"{n} entities; largest: " + "; ".join(f"{e['name']} ({e['employees']:,})" for e in top)
        fix = FIX[cls]
    # Non-employee networks are not stale but must still be suppressed.
    if dom == "statefarm.com":
        cls, fix = "clean_with_stale_pages", "Enrich by domain; suppress 'State Farm Agent' (independent agents, not employees)."
    rows.append({"domain": dom, "account_key": acct, "entities_returned": n,
                 "count_is_lower_bound": "yes" if dom in ("jhu.edu", "hopkinsmedicine.org", "optum.com", "marsh.com") else "no",
                 "parent_returned": "yes", "stale_or_inactive_pages": stale, "wrong_company_pages": 0,
                 "size_or_revenue_contradictions": contra, "match_class": cls, "finding": finding, "fix": fix})

path = os.path.join(BASE, "data", "clay_match_quality.csv")
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(rows, open(path.replace(".csv", ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

from collections import Counter
print(f"{len(rows)} domains:", dict(Counter(r["match_class"] for r in rows)))
