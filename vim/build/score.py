# -*- coding: utf-8 -*-
"""Deterministic Vim reconciliation + fit scoring. This file IS the workflow's final code node
(`handler`), and runs locally for the self-test: python3 build/score.py

Criteria are PLACEHOLDERS (SCORE_VERSION) until Daryl and Raveed confirm the ICP and the
supported-EHR list. Tri-state checks: True / False / None (unknown). Unknown never counts as a
negative finding; it routes the account to Review. The Clay code runtime has no datetime
module, so this uses time only.
"""
import json, time

SCORE_VERSION = "provider-v0-placeholder"

# Placeholder ICP, modeled on VillageMD / Oak Street / One Medical / DaVita / LifeStance.
TARGET_ORG_TYPES = {"multi-site provider group", "primary care network", "specialty provider network"}
TARGET_SPECIALTIES = ("primary care", "multi-specialty", "behavioral health", "mental health", "nephrology")
SUPPORTED_EHRS = set()           # EMPTY until Vim confirms. Epic/athena are NOT assumed.
MIN_LOCATIONS = 50
TARGET_COUNTRIES = {"US"}

WEIGHTS = {"org_type": 25, "supported_ehr": 30, "specialty": 20, "footprint": 15, "geography": 10}
REQUIRED = ("org_type", "supported_ehr", "specialty")


def _tri(value, test):
    return None if value in (None, "", []) else bool(test(value))


def _num(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def score(row):
    spec = (row.get("specialty") or "").lower()
    ehr = (row.get("ehr_vendor") or "").strip().lower()
    checks = {
        "org_type": _tri(row.get("org_type"), lambda v: v.lower() in TARGET_ORG_TYPES),
        "supported_ehr": None if not ehr or not SUPPORTED_EHRS else ehr in {e.lower() for e in SUPPORTED_EHRS},
        "specialty": _tri(spec, lambda v: any(t in v for t in TARGET_SPECIALTIES)),
        "footprint": _tri(_num(row.get("location_count")), lambda v: v >= MIN_LOCATIONS),
        "geography": _tri(row.get("country"), lambda v: v.upper() in TARGET_COUNTRIES),
    }
    fit = sum(WEIGHTS[k] for k, v in checks.items() if v is True)
    missing = [k for k in REQUIRED if checks[k] is None]
    reasons = [f"{k}:{'yes' if v else 'no' if v is False else 'unknown'}" for k, v in checks.items()]

    if row.get("segment") == "payer":
        tier = "Review"
        reasons.append("payer scorecard not defined yet")
    elif row.get("excluded") is True or checks["supported_ehr"] is False:
        tier = "Excluded"
    elif row.get("identity_status") != "matched" or missing:
        tier = "Review"
    elif fit >= 80:
        tier = "Tier 1"
    elif fit >= 60:
        tier = "Tier 2"
    else:
        tier = "Tier 3"
    return {"fit_score": fit, "fit_tier": tier, "missing_required_fields": ", ".join(missing),
            "score_reasons": "; ".join(reasons), "score_version": SCORE_VERSION,
            "scored_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def reconcile(structured, research, research_url):
    """Structured wins. Research is promoted only with a source URL. Disagreement is a conflict."""
    s, r = (structured or "").strip(), (research or "").strip()
    if s and r and s.lower() != r.lower():
        return s, "conflict"
    if s:
        return s, "structured"
    if r and (research_url or "").strip():
        return r, "research_with_evidence"
    return "", "unknown"


def handler(context):
    g = lambda k: context.get_input(k)
    ehr, ehr_src = reconcile(g("ehr_vendor"), g("cg_ehr_vendor"), g("cg_ehr_source_url"))
    parent, parent_src = reconcile(g("parent_name"), g("cg_parent_name"), g("cg_parent_source_url"))
    locs = g("cg_location_count") if (g("cg_location_source_url") or "").strip() else None
    org_type = g("cg_org_type") or ""
    row = {"segment": g("segment"), "identity_status": g("identity_status"), "country": g("country"),
           "specialty": g("specialty"), "org_type": org_type,
           "ehr_vendor": ehr if ehr_src != "conflict" else "", "location_count": locs}
    out = score(row)
    if ehr_src == "conflict":
        out["fit_tier"] = "Review"

    reasons = out["score_reasons"]
    if g("latest_event_type"):
        why = (f"{g('company_name')} meets: {reasons}. {g('latest_event_type')} on {g('latest_event_date')}: "
               f"{g('latest_event_summary')}. Evidence: {g('latest_event_url')}.")
    else:
        why = f"{g('company_name')}: fit-led account; no verified recent trigger. Fit: {reasons}."
    jobs = g("relevant_job_count") or 0
    if jobs:
        why += f" {jobs} digital/IT/VBC openings in the last 90 days."

    out.update({"ehr_vendor_final": ehr, "ehr_source": ehr_src, "parent_final": parent, "parent_source": parent_src,
                "location_count_final": _num(locs) if locs is not None else None, "org_type_final": org_type,
                "research_status": "needs_review" if "conflict" in (ehr_src, parent_src) else
                                   ("ai_fallback_used" if g("cg_uncertainty_notes") is not None else "structured_only"),
                "why_now": why})
    return out


class _Ctx:
    def __init__(self, d): self.d = d
    def get_input(self, k): return self.d.get(k)


def _self_test():
    global SUPPORTED_EHRS
    saved, SUPPORTED_EHRS = SUPPORTED_EHRS, {"athenahealth", "epic"}  # test-only list
    base = dict(identity_status="matched", org_type="primary care network", segment="provider",
                specialty="primary care", location_count="230", country="US")
    try:
        assert score({**base, "ehr_vendor": "athenahealth"})["fit_tier"] == "Tier 1"
        assert score({**base, "ehr_vendor": "legacyehr"})["fit_tier"] == "Excluded"
        r = score({**base, "ehr_vendor": ""})
        assert r["fit_tier"] == "Review" and r["missing_required_fields"] == "supported_ehr"
        assert score({**base, "ehr_vendor": "epic", "identity_status": "ambiguous"})["fit_tier"] == "Review"
        assert score({**base, "ehr_vendor": "epic", "location_count": "12"})["fit_tier"] == "Tier 1"  # 85
        assert score({**base, "ehr_vendor": "epic", "location_count": "12", "country": "CA"})["fit_tier"] == "Tier 2"  # 75
        assert score({**base, "ehr_vendor": "epic", "excluded": True})["fit_tier"] == "Excluded"
        assert score({**base, "ehr_vendor": "epic", "segment": "payer"})["fit_tier"] == "Review"
        # reconciliation
        assert reconcile("Epic", "athenahealth", "https://x") == ("Epic", "conflict")
        assert reconcile("", "Epic", "") == ("", "unknown")          # no evidence URL -> not promoted
        assert reconcile("", "Epic", "https://x") == ("Epic", "research_with_evidence")
        h = handler(_Ctx({"segment": "provider", "identity_status": "matched", "country": "US",
                          "specialty": "primary care", "company_name": "Oak Street Health", "ehr_vendor": "Epic",
                          "cg_ehr_vendor": "athenahealth", "cg_ehr_source_url": "https://x", "cg_org_type": "primary care network",
                          "cg_location_count": 230, "cg_location_source_url": "https://y", "cg_uncertainty_notes": ""}))
        assert h["fit_tier"] == "Review" and h["research_status"] == "needs_review" and h["location_count_final"] == 230
    finally:
        SUPPORTED_EHRS = saved
    assert score({**base, "ehr_vendor": "epic"})["fit_tier"] == "Review"
    print("score.py self-test: 13 checks passed")


if __name__ == "__main__":
    _self_test()
