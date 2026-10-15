# -*- coding: utf-8 -*-
"""
Qualify the talent-leadership signal (build guide sections 8 and 9) with rules, not AI.

Input: every person Clay's people search returned for "senior talent leader who started in
the last 18 months" across the cohort (data/raw/clay_talent_leaders_batch*.json).
Output: data/talent_leaders.csv with each person's persona, level, scope, geography and a
qualified yes/no plus the reason (local only, gitignored), and data/talent_leaders_public.csv,
the same rows without name, profile URL or location (committed).

Why a gate is needed at all: the search uses is_similar_to on titles, which is the right way
to cast the net but returns an Executive Assistant to the CHRO, a CPO Group Analyst, a
marketing AVP, and TA leads in Hyderabad alongside the CHROs. A rep should see the CHROs.

Every rule is a regex or a lookup, so a disputed classification can be traced to one line.
"""
import csv, json, os, re
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AS_OF = date(2026, 10, 15)
WINDOW_MONTHS = 18

# ----------------------------------------------------------------------------- persona
PERSONA_RULES = [
    ("off_persona",          r"\bmarketing\b|\bbusiness solutions\b"),
    ("hr_technology",        r"talent acquisition technology|hr technology|hris|people technology"),
    ("hr_business_partner",  r"business partner|hrbp|assistant to the"),
    ("talent_intelligence",  r"talent intelligence|people analytics|workforce analytics|talent strategy"),
    ("economic_buyer",       r"\bchro\b|chief (human resources|people|talent|hr) officer|chief talent officer"
                             r"|\(chief people officer\)|vp,? global talent|svp,? human resources"
                             r"|human resources \(chief people"),
    ("people_org_operations", r"head of business management|business management"),
    ("ta_owner",             r"talent acquisition|recruiting|recruitment|sourcing|early talent"),
    ("hr_generalist",        r"human resources|\bhr\b"),
]

# ----------------------------------------------------------------------------- level
SUPPORT = r"\bassistant\b|\banalyst\b|\bcoordinator\b|\bintern\b|\bspecialist\b"
LEVEL_RULES = [
    ("support",  SUPPORT),
    ("exec",     r"\bchief\b|\bchro\b|\bcpo\b(?!.*analyst)|executive vice president|\bevp\b"
                 r"|senior vice president|\bsvp\b"),
    ("vp",       r"\bvice president\b|\bvp\b|\bavp\b|executive director"),
    ("head",     r"\bhead of\b"),
    ("director", r"\bdirector\b"),
    ("manager",  r"\bmanager\b|\blead\b|\bleader\b"),
]

# Title says "manager" or "lead" despite a VP/SVP band: common in insurance and banking, where
# SVP is a pay band. Kept at its banded level but flagged so a human can judge.
BANDED = re.compile(r"(svp|senior vice president|\bvp\b|vice president).*(manager|lead\b)", re.I)

# ----------------------------------------------------------------------------- scope
REGIONAL = re.compile(
    r"\b(emea|apac|europe|uk\b|india|malaysia|ksa|international|americas excluding us|west region"
    r"|nese|north carolina division|capital division)\b", re.I)

US_HINTS = re.compile(
    r"united states|new york|boston|philadelphia|nashville|seattle|atlanta|houston|phoenix"
    r"|minneapolis|chandler|baltimore|charlotte|tampa|kansas city|league city|castro valley|chicago"
    r"|gresham|valley stream|paramus|maple grove|chattanooga|indianapolis|columbus", re.I)

# Division attribution by name in the title (titles misspell, so aliases are explicit).
DIVISION_ALIASES = {
    "UnitedHealthcare": ["unitedhealthcare", "unitedheathcare"],
    "Carelon": ["carelon"],
    "Optum": ["optum health", "optum"],
    "Cigna Healthcare": ["cigna healthcare"],
}


def first_match(rules, text):
    for name, pat in rules:
        if re.search(pat, text, re.I):
            return name
    return "unclassified"


def months_since(yyyymm):
    y, m = (int(x) for x in yyyymm.split("-")[:2])
    return (AS_OF.year - y) * 12 + (AS_OF.month - m)


def classify(p):
    t = p["title"]
    persona = first_match(PERSONA_RULES, t)
    # "Assistant to the CHRO" / "Partner to the CHRO" describe whom the person supports, not their level.
    level = first_match(LEVEL_RULES, re.sub(r"\bto the (chro|cpo|ceo)\b", "", t, flags=re.I))
    regional = bool(REGIONAL.search(t))
    us = bool(US_HINTS.search(p["location"] or ""))
    age = months_since(p["start"]) if p.get("start") else None

    reasons = []
    if persona in ("off_persona", "unclassified"):
        reasons.append("not a talent or HR persona")
    if persona in ("hr_business_partner", "people_org_operations", "hr_generalist"):
        reasons.append(f"{persona.replace('_', ' ')}: influencer, not a trigger")
    if level in ("support", "manager", "unclassified"):
        reasons.append(f"level '{level}' below trigger grade")
    if level == "director" and persona not in ("hr_technology",):
        reasons.append("director outside HR technology")
    if regional:
        reasons.append("regional scope")
    # Geography gates the person only below the executive line. An enterprise-scope CHRO or
    # Chief Talent Officer of a US account buys for the whole company wherever they live.
    exec_buyer = level == "exec" and persona == "economic_buyer" and not regional
    if not us and not exec_buyer:
        reasons.append("outside POC geography (US)")
    if age is None or age > WINDOW_MONTHS:
        reasons.append("start date outside 18-month window")

    return {
        "persona_group": persona,
        "level": level,
        "title_banded": "yes" if BANDED.search(t) else "no",
        "scope": "regional" if regional else "enterprise_or_division",
        "us_based": "yes" if us else "no (enterprise exec kept)" if exec_buyer else "no",
        "months_in_role": age,
        "qualified": "no" if reasons else "yes",
        "disqualify_reasons": "; ".join(reasons),
    }


def main():
    divisions = json.load(open(os.path.join(BASE, "data", "divisions.json"), encoding="utf-8"))
    by_domain = {d["entity_domain"]: d["account_key"] for d in divisions if d["include_in_cohort"] == "yes"}
    by_li = {d["entity_linkedin_url"].rstrip("/"): d["account_key"] for d in divisions}
    entity_names = {(d["account_key"], d["entity_name"]) for d in divisions if d["include_in_cohort"] == "yes"}

    raw = os.path.join(BASE, "data", "raw")
    batches = sorted(f for f in os.listdir(raw) if f.startswith("clay_talent_leaders_batch"))
    if not batches:
        # The raw people captures are kept out of the public repo (.gitignore). Without them the
        # committed talent_leaders_public.* files are the record; nothing to rebuild.
        print("no raw talent-leader captures; keeping data/talent_leaders_public.*")
        return

    people, seen_urls, seen_keys = [], set(), {}
    for fname in batches:
        cap = json.load(open(os.path.join(BASE, "data", "raw", fname), encoding="utf-8"))
        for p in cap["contacts"]:
            ident = (p.get("search_domain") or p.get("search_identifier") or "").rstrip("/")
            acct = by_domain.get(ident) or by_li.get(ident) or ""
            attribution = "search identifier"
            if not acct:
                # Clay occasionally returns a person with no companyIdentifier. Fall back to the
                # employer name, and say so on the row rather than guessing silently.
                hit = [d for d in divisions if d["entity_name"].lower().startswith(p["company"].lower())]
                acct = hit[0]["account_key"] if len(hit) == 1 else ""
                attribution = "employer name (identifier missing in Clay response)" if acct else "unattributed"
            # Division: named in the title, else the employer name when it is a known entity.
            division = ""
            low = p["title"].lower()
            for name, aliases in DIVISION_ALIASES.items():
                if any(a in low for a in aliases) and (acct, name) in entity_names:
                    division = name; break
            if not division and (acct, p["company"]) in entity_names:
                division = p["company"]

            url = p["linkedin"].rstrip("/")
            key = (re.sub(r"[^a-z]", "", p["name"].lower()), p["company"], p["title"], p["start"])
            dup = ""
            if url in seen_urls:
                dup = "exact duplicate (same LinkedIn URL)"
            elif key in seen_keys:
                dup = f"probable duplicate of {seen_keys[key]} (same name, employer, title and start, different URL)"
            seen_urls.add(url); seen_keys.setdefault(key, url)

            row = {"account_key": acct, "division": division or p["company"], "name": p["name"],
                   "title": p["title"], "employer_in_clay": p["company"], "start": p["start"],
                   "location": p["location"], "linkedin_url": p["linkedin"],
                   **classify(p), "duplicate": dup, "account_attribution": attribution, "source_task": cap["task_id"],
                   "observed_at": cap["captured"]}
            if dup:
                row["qualified"] = "no"
                row["disqualify_reasons"] = (row["disqualify_reasons"] + "; " if row["disqualify_reasons"] else "") + dup
            people.append(row)

    path = os.path.join(BASE, "data", "talent_leaders.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(people[0].keys())); w.writeheader(); w.writerows(people)
    json.dump(people, open(path.replace(".csv", ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    # Public copy: no name, profile URL or location. Titles, employers and start months stay,
    # because they are what the rules act on and what a reviewer needs to audit them.
    public = []
    for p in people:
        r = {k: v for k, v in p.items() if k not in ("name", "linkedin_url", "location", "duplicate")}
        r["duplicate"] = "yes" if p["duplicate"] else ""
        r["disqualify_reasons"] = re.sub(r"probable duplicate of \S+ \([^)]*\)", "probable duplicate profile",
                                         p["disqualify_reasons"])
        public.append(r)
    pub = os.path.join(BASE, "data", "talent_leaders_public.csv")
    with open(pub, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(public[0].keys())); w.writeheader(); w.writerows(public)
    json.dump(public, open(pub.replace(".csv", ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    q = [p for p in people if p["qualified"] == "yes"]
    print(f"{len(people)} returned | {len(q)} qualified across {len({p['account_key'] for p in q})} accounts")
    for p in q:
        print(f"  {p['account_key']:<20} {p['name']:<22} {p['persona_group']:<20} {p['start']}  {p['title']}")


if __name__ == "__main__":
    main()
