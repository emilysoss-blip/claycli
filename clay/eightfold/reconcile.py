
PERSONAS = [
    ("Economic buyer (CHRO / CPO)", ["chief human resources", "chief people", "chro", "chief talent",
                                    "svp, human resources", "svp human resources", "senior vice president, human resources",
                                    "evp, human resources", "executive vice president, human resources", "chief hr"]),
    ("Operational owner (Head / VP of TA)", ["head of talent acquisition", "vp talent acquisition", "vp, talent acquisition",
                                            "vice president, talent acquisition", "vice president talent acquisition",
                                            "vice president of talent acquisition", "global head of talent", "head of talent"]),
    ("Talent intelligence / people analytics", ["head of talent intelligence", "talent intelligence", "head of people analytics",
                                               "vp people analytics", "vice president, people analytics", "director of people analytics",
                                               "people analytics director"]),
]
SUPPORTED_HCM = ["workday", "successfactors", "oracle", "taleo", "ukg", "icims", "greenhouse", "cornerstone", "avature", "phenom"]
NON_HCM = ["financial", "planning", "integration", "procurement", "spend", "supply chain"]
RECENT_MONTHS = 18


def _today_ym(as_of):
    try:
        import time
        t = time.gmtime()
        return t.tm_year, t.tm_mon
    except Exception:
        return int(as_of[:4]), int(as_of[5:7])


def _months_since(ym, today):
    try:
        y, m = int(ym[:4]), int(ym[5:7])
    except (TypeError, ValueError):
        return -1
    return (today[0] - y) * 12 + (today[1] - m)


def _persona(title):
    t = (title or "").lower()
    for rank, (label, keys) in enumerate(PERSONAS):
        if any(k in t for k in keys):
            return rank, label
    return None, ""


def handler(context):
    today = _today_ym(context.get_input("as_of_month") or "2026-10")
    company = (context.get_input("matched_name") or "").lower()
    candidates = []
    for p in context.get_input("people") or []:
        cur = [e for e in (p.get("current_experience") or []) if e.get("is_current")]
        role = next((e for e in cur if company and company in (e.get("company") or "").lower()), cur[0] if cur else {})
        title = role.get("title") or p.get("title") or ""
        rank, label = _persona(title)
        if rank is None:
            continue
        start = role.get("start_date") or ""
        candidates.append((rank, -_months_since(start, today) if start else -9999, {
            "name": p.get("name") or "", "title": title, "url": p.get("url") or "",
            "start": start, "months": _months_since(start, today) if start else -1, "persona": label}))
    candidates.sort(key=lambda c: (c[0], c[1]))
    best = candidates[0][2] if candidates else None
    recent = [c[2] for c in candidates if 0 <= c[2]["months"] <= RECENT_MONTHS]

    installs = context.get_input("installs") or []
    hcm = []
    for i in installs:
        name = i.get("product_name") or ""
        low = name.lower()
        if any(k in low for k in SUPPORTED_HCM) and not any(x in low for x in NON_HCM) and name not in hcm:
            hcm.append(name)
    hcm_verified = max([i.get("product_last_verified_date") or "" for i in installs] or [""])

    open_roles = context.get_input("job_count")
    headcount = context.get_input("employee_count")
    growth = context.get_input("growth_12m")
    missing = []
    if not best:
        missing.append("talent_leader")
    elif not best["start"]:
        missing.append("talent_leader_start_date")
    if not hcm:
        missing.append("hcm")
    if open_roles is None:
        missing.append("open_roles")
    if headcount is None:
        missing.append("headcount")

    return {
        "talent_leader_name": best["name"] if best else "",
        "talent_leader_title": best["title"] if best else "",
        "talent_leader_url": best["url"] if best else "",
        "talent_leader_start_date": best["start"] if best else "",
        "talent_leader_months_in_role": best["months"] if best else -1,
        "persona_group": best["persona"] if best else "",
        "qualified_leaders_found": len(candidates),
        "recent_leader_change": bool(recent),
        "recent_leader_url": recent[0]["url"] if recent else "",
        "recent_leader_summary": "; ".join("%s, %s (since %s)" % (r["name"], r["title"], r["start"]) for r in recent[:3]),
        "hcm_systems": ", ".join(hcm),
        "hcm_known": bool(hcm),
        "hcm_source": ("HG Insights, last verified %s" % hcm_verified) if hcm else "",
        "open_roles_30d": int(open_roles) if open_roles is not None else -1,
        "headcount": int(headcount) if headcount is not None else -1,
        "headcount_growth_12m_pct": float(growth) if growth is not None else 0.0,
        "headcount_growth_known": growth is not None,
        "missing_fields": ", ".join(missing),
        "needs_fallback": ("talent_leader" in missing) or ("hcm" in missing) or ("talent_leader_start_date" in missing),
    }
