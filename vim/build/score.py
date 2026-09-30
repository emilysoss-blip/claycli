# -*- coding: utf-8 -*-
"""Deterministic Vim fit scoring. Paste `score()` into the workflow's code node.

Criteria are PLACEHOLDERS (score_version below) until Daryl and Raveed confirm the ICP and
the supported-EHR list. Tri-state inputs: True / False / None (unknown). Unknown never
counts as a negative finding; it routes the account to Review instead.
"""
from datetime import datetime, timezone

SCORE_VERSION = "provider-v0-placeholder"

# Placeholder ICP, modeled on VillageMD / Oak Street / One Medical / DaVita / LifeStance.
TARGET_ORG_TYPES = {"multi-site provider group", "primary care network", "specialty provider network"}
TARGET_SPECIALTIES = {"primary care", "multi-specialty", "behavioral health", "nephrology"}
SUPPORTED_EHRS = set()           # EMPTY until Vim confirms. Epic/athena are NOT assumed.
MIN_LOCATIONS = 50
TARGET_COUNTRIES = {"US"}

WEIGHTS = {"org_type": 25, "supported_ehr": 30, "specialty": 20, "footprint": 15, "geography": 10}
REQUIRED = ("org_type", "supported_ehr", "specialty")


def _tri(value, test):
    """None stays None (unknown); otherwise apply test."""
    return None if value in (None, "", []) else bool(test(value))


def score(row):
    specialties = {s.strip().lower() for s in (row.get("specialty") or "").split(";") if s.strip()}
    ehr = (row.get("ehr_vendor") or "").strip().lower()
    locs = row.get("location_count")
    checks = {
        "org_type": _tri(row.get("org_type"), lambda v: v.lower() in TARGET_ORG_TYPES),
        # EHR is only decidable once Vim publishes its supported list.
        "supported_ehr": None if not ehr or not SUPPORTED_EHRS else ehr in SUPPORTED_EHRS,
        "specialty": _tri(specialties, lambda v: bool(v & TARGET_SPECIALTIES)),
        "footprint": _tri(locs, lambda v: int(v) >= MIN_LOCATIONS),
        "geography": _tri(row.get("country"), lambda v: v.upper() in TARGET_COUNTRIES),
    }
    fit = sum(WEIGHTS[k] for k, v in checks.items() if v is True)
    missing = [k for k in REQUIRED if checks[k] is None]
    reasons = [f"{k}:{'yes' if v else 'no' if v is False else 'unknown'}" for k, v in checks.items()]

    if row.get("excluded") is True or checks["supported_ehr"] is False:
        tier = "Excluded"
    elif row.get("identity_status") != "matched" or missing:
        tier = "Review"
    elif fit >= 80:
        tier = "Tier 1"
    elif fit >= 60:
        tier = "Tier 2"
    else:
        tier = "Tier 3"

    return {
        "fit_score": fit, "fit_tier": tier, "missing_required_fields": missing,
        "score_reasons": reasons, "score_version": SCORE_VERSION,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def _self_test():
    global SUPPORTED_EHRS
    saved, SUPPORTED_EHRS = SUPPORTED_EHRS, {"athenahealth", "epic"}  # test-only list
    base = dict(identity_status="matched", org_type="primary care network",
                specialty="primary care", location_count="230", country="US")
    try:
        assert score({**base, "ehr_vendor": "athenahealth"})["fit_tier"] == "Tier 1"
        assert score({**base, "ehr_vendor": "legacyehr"})["fit_tier"] == "Excluded"
        r = score({**base, "ehr_vendor": ""})
        assert r["fit_tier"] == "Review" and r["missing_required_fields"] == ["supported_ehr"]
        # shared-domain entity that failed identity pinning stays in Review even if it scores
        assert score({**base, "ehr_vendor": "epic", "identity_status": "ambiguous"})["fit_tier"] == "Review"
        assert score({**base, "ehr_vendor": "epic", "location_count": "12"})["fit_tier"] == "Tier 1"  # 85
        assert score({**base, "ehr_vendor": "epic", "location_count": "12", "country": "CA"})["fit_tier"] == "Tier 2"  # 75
        assert score({**base, "ehr_vendor": "epic", "excluded": True})["fit_tier"] == "Excluded"
    finally:
        SUPPORTED_EHRS = saved
    # with the real (empty) EHR list, nothing can reach a tier yet
    assert score({**base, "ehr_vendor": "epic"})["fit_tier"] == "Review"
    print("score.py self-test: 8 checks passed")


if __name__ == "__main__":
    _self_test()
