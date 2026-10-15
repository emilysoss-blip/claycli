# -*- coding: utf-8 -*-
"""
Deterministic account tiering (build guide section 7). No AI score.

Three scores stay separate, and completeness stays separate again:
  fit_score         0-100 from the versioned criteria below
  intent_score      from 6sense, brought in as-is (None until connected)
  engagement_score  from Marketo, brought in as-is (None until connected)
A single blended number is exactly what the demand gen team already distrusts.

Every criterion is tri-state: True, False, or None (unknown). Unknown is never coerced to
False. An account missing a required field lands in Review with the field named, and its
best-case fit is reported next to its known fit so Review is sortable.

CRITERIA is a CALIBRATION SET, not Eightfold's ICP. Eightfold's demand gen team has to confirm target
industries, minimum headcount, the supported HCM list, geography and exclusions. Change the
dict, bump the version, re-run; score_version travels with every row.
"""
import csv, json, os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CRITERIA = {
    "version": "0.1-calibration",
    "weights": {"industry": 25, "headcount": 20, "open_reqs": 25, "hcm": 20, "geography": 10},
    "required": ["industry", "headcount", "open_reqs", "hcm", "geography"],
    "target_verticals": ["Healthcare", "Insurance & Financial Services",
                         "Semiconductors & Advanced Manufacturing"],
    "excluded_verticals": [],
    "min_employees": 10000,
    "min_open_reqs": 500,
    # Supported or displaceable HCM / ATS. Presence on a careers site is a clue, not proof.
    "hcm_supported": ["Workday", "SAP SuccessFactors", "Oracle HCM", "Taleo", "iCIMS",
                      "Greenhouse", "SmartRecruiters", "Avature", "Phenom"],
    "target_countries": ["United States"],
    "tier1_min": 80,
    "tier2_min": 60,
}


def _tri(value, test):
    """Apply test to value, preserving None as unknown."""
    return None if value is None else bool(test(value))


def evaluate(facts, c=CRITERIA):
    """facts: dict with vertical, employees, open_reqs, hcm (list|None), country,
    disqualifier (str|None). Returns the scored row, never raises on missing data."""
    checks = {
        "industry":  _tri(facts.get("vertical"), lambda v: v in c["target_verticals"]),
        "headcount": _tri(facts.get("employees"), lambda v: v >= c["min_employees"]),
        "open_reqs": _tri(facts.get("open_reqs"), lambda v: v >= c["min_open_reqs"]),
        "hcm":       _tri(facts.get("hcm"), lambda v: any(h in c["hcm_supported"] for h in v)),
        "geography": _tri(facts.get("country"), lambda v: v in c["target_countries"]),
    }
    w = c["weights"]
    fit = sum(w[k] for k, ok in checks.items() if ok is True)
    best_case = fit + sum(w[k] for k, ok in checks.items() if ok is None)
    missing = [k for k in c["required"] if checks[k] is None]

    reasons = []
    for k, ok in checks.items():
        tag = {True: "+", False: "-", None: "?"}[ok]
        reasons.append(f"{tag}{k}({w[k]})")

    if facts.get("disqualifier"):
        tier = "Excluded"
    elif facts.get("vertical") in c["excluded_verticals"]:
        tier = "Excluded"
    elif facts.get("identity_unresolved"):
        tier = "Review"
        missing = ["identity"] + missing
    elif missing:
        tier = "Review"
    elif fit >= c["tier1_min"]:
        tier = "Tier 1"
    elif fit >= c["tier2_min"]:
        tier = "Tier 2"
    else:
        tier = "Tier 3"

    return {
        "fit_score": fit,
        "fit_best_case": best_case,
        "fit_tier": tier,
        "missing_required_fields": ";".join(missing),
        "score_reasons": " ".join(reasons),
        "intent_score": facts.get("intent_score"),
        "engagement_score": facts.get("engagement_score"),
        "score_version": c["version"],
        "scored_at": facts.get("as_of", date.today().isoformat()),
        **{f"check_{k}": {True: "yes", False: "no", None: "unknown"}[v] for k, v in checks.items()},
    }


def facts_for(account, growth_band):
    """Build tiering facts from what this repo actually holds. Open reqs and HCM are None:
    the native enrichment was dispatched but could not be read back (see README)."""
    return {
        "vertical": account["vertical"],
        "employees": int(account["clay_employee_count"]) if account["clay_employee_count"] else None,
        "open_reqs": None,
        "hcm": None,
        "country": account["country"],
        "disqualifier": None,
        # A parent the domain cannot find is still resolved here, because the pinned LinkedIn
        # URL found it. Identity is unresolved only when neither path returns the parent.
        "identity_unresolved": False,
        "intent_score": None,
        "engagement_score": None,
        "as_of": account["observed_at"],
        "growth_band": growth_band,
    }


def main():
    accounts = json.load(open(os.path.join(BASE, "data", "accounts.json"), encoding="utf-8"))
    growth = json.load(open(os.path.join(BASE, "data", "raw", "clay_headcount_growth.json"), encoding="utf-8"))
    band_of = {}
    for q in growth["queries"]:
        for name in q["cohort_entities"]:
            band_of[name] = q["band"]
    divisions = json.load(open(os.path.join(BASE, "data", "divisions.json"), encoding="utf-8"))

    rows = []
    for a in accounts:
        ents = [d for d in divisions if d["account_key"] == a["account_key"] and d["include_in_cohort"] == "yes"]
        parent_names = {d["entity_name"] for d in ents if d["role"] == "parent"}
        bands = {d["entity_name"]: band_of[d["entity_name"]] for d in ents if d["entity_name"] in band_of}
        parent_band = next((b for n, b in bands.items() if n in parent_names), None)
        r = evaluate(facts_for(a, parent_band))
        rows.append({
            "account_key": a["account_key"], "account_name": a["account_name"], "vertical": a["vertical"],
            **r,
            "headcount_growth_3mo": parent_band or "flat_or_unreported",
            "division_growth": "; ".join(f"{n}: {b}" for n, b in bands.items() if n not in parent_names),
        })

    path = os.path.join(BASE, "data", "tiered_accounts.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(rows, open(path.replace(".csv", ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    from collections import Counter
    print("tiers:", dict(Counter(r["fit_tier"] for r in rows)),
          "| missing:", dict(Counter(r["missing_required_fields"] for r in rows)))


if __name__ == "__main__":
    main()
