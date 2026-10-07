SCORE_VERSION = "eightfold-fit-v0.1-calibration"
TARGET_VERTICALS = ["healthcare", "insurance", "financial services", "semiconductors", "manufacturing", "retail"]
TARGET_GEOS = ["US"]
SUPPORTED_HCM = ["workday", "successfactors", "oracle", "taleo", "ukg"]


def _s(context, key):
    v = context.get_input(key)
    return "" if v is None else str(v).strip()


def _n(context, key, default=-1):
    v = context.get_input(key)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _promote(native, fallback, source, uncertainty):
    # Native structured values always win; a fallback value needs a source URL and usable confidence.
    if native:
        return native, "native"
    if fallback and source.startswith("http") and uncertainty in ("Low", "Medium"):
        return fallback, "claygent"
    return "", "unknown"


def handler(context):
    unc = _s(context, "fb_uncertainty")
    leader, leader_src = _promote(_s(context, "talent_leader_name"), _s(context, "fb_leader_name"), _s(context, "fb_leader_source_url"), unc)
    title = _s(context, "talent_leader_title") if leader_src == "native" else (_s(context, "fb_leader_title") if leader_src == "claygent" else "")
    start, start_src = _promote(_s(context, "talent_leader_start_date"), _s(context, "fb_leader_start_date"), _s(context, "fb_leader_source_url"), unc)
    hcm, hcm_src = _promote(_s(context, "hcm_systems"), _s(context, "fb_hcm_systems"), _s(context, "fb_hcm_source_url"), unc)
    evidence_url = _s(context, "talent_leader_url") if leader_src == "native" else (_s(context, "fb_leader_source_url") if leader_src == "claygent" else "")

    vertical = _s(context, "vertical")
    country = _s(context, "country")
    headcount = _n(context, "headcount")
    open_roles = _n(context, "open_roles_30d")

    score, reasons, missing = 0, [], []
    # Target industry (25)
    if vertical.lower() in TARGET_VERTICALS:
        score += 25
        reasons.append("target vertical: %s" % vertical)
    elif not vertical or vertical == "unknown":
        missing.append("vertical")
    # Headcount band (20)
    if headcount >= 10000:
        score += 20
        reasons.append("%d employees" % headcount)
    elif headcount >= 5000:
        score += 10
        reasons.append("%d employees (below enterprise band)" % headcount)
    elif headcount < 0:
        missing.append("headcount")
    # Open requisition volume (25)
    if open_roles >= 50:
        score += 25
        reasons.append("%d open roles in 30 days" % open_roles)
    elif open_roles >= 10:
        score += 15
        reasons.append("%d open roles in 30 days" % open_roles)
    elif open_roles >= 1:
        score += 5
        reasons.append("%d open roles in 30 days" % open_roles)
    elif open_roles < 0:
        missing.append("open_roles")
    # Supported or displaceable HCM confirmed (20)
    if hcm and any(k in hcm.lower() for k in SUPPORTED_HCM):
        score += 20
        reasons.append("HCM confirmed (%s)" % hcm_src)
    elif hcm:
        score += 10
        reasons.append("ATS/HR tech found, core HCM not confirmed")
    else:
        missing.append("hcm")
    # Target geography (10)
    if country in TARGET_GEOS:
        score += 10
        reasons.append("geo %s" % country)

    if missing and ("headcount" in missing or "vertical" in missing):
        tier = "Review"
    elif "hcm" in missing and score + 20 >= 80 and score < 80:
        tier = "Review"  # the unknown field alone decides the tier, so do not guess it
    elif score >= 80:
        tier = "Tier 1"
    elif score >= 60:
        tier = "Tier 2"
    else:
        tier = "Tier 3"

    months = _n(context, "talent_leader_months_in_role")
    recent = bool(context.get_input("recent_leader_change"))
    signal = "New talent leader within 18 months" if recent else "No verified recent trigger"
    return {
        "source_row_id": _s(context, "source_row_id"),
        "account_name": _s(context, "account_name"),
        "account_domain": _s(context, "account_domain"),
        "fit_score": score,
        "fit_tier": tier,
        "intent_score": "not connected (6sense not wired)",
        "engagement_score": "not connected (Marketo not wired)",
        "signal": signal,
        "signal_led": recent,
        "talent_leader": leader,
        "talent_leader_title": title,
        "talent_leader_start_date": start,
        "talent_leader_months_in_role": months if leader_src == "native" else -1,
        "talent_leader_source": leader_src,
        "evidence_url": evidence_url,
        "hcm_systems": hcm,
        "hcm_source": hcm_src,
        "missing_required_fields": ", ".join(missing),
        "score_reasons": "; ".join(reasons),
        "score_version": SCORE_VERSION,
    }
