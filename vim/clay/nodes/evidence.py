import json, re, time

# Deterministic vendor dictionaries. An HG install record is evidence; a portal brand is only a clue.
EHR = {"epic": "Epic", "athenahealth": "athenahealth", "athenaone": "athenahealth", "athenaclinicals": "athenahealth",
       "eclinicalworks": "eClinicalWorks", "nextgen": "NextGen", "cerner": "Oracle Health (Cerner)",
       "oracle health": "Oracle Health (Cerner)", "allscripts": "Veradigm (Allscripts)", "veradigm": "Veradigm (Allscripts)",
       "greenway": "Greenway", "modernizing medicine": "ModMed", "modmed": "ModMed", "advancedmd": "AdvancedMD",
       "elation": "Elation", "meditech": "MEDITECH", "practice fusion": "Practice Fusion", "drchrono": "DrChrono",
       "tebra": "Tebra (Kareo)", "kareo": "Tebra (Kareo)", "netsmart": "Netsmart", "qualifacts": "Qualifacts",
       "valant": "Valant", "simplepractice": "SimplePractice", "canvas medical": "Canvas Medical"}
PORTAL = {"mychart": "MyChart (Epic)", "followmyhealth": "FollowMyHealth", "healow": "healow (eCW)",
          "athenapatient": "athenaPatient", "phreesia": "Phreesia", "luma health": "Luma Health", "klara": "Klara",
          "solutionreach": "Solutionreach", "relatient": "Relatient", "kyruus": "Kyruus"}
MA_CATEGORIES = {"acquires", "merges_with", "is_acquired_by", "sells_assets_to", "invests_into", "partners_with",
                 "expands_facilities", "opens_new_location", "expands_to_new_market"}


def _load(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return v
    return v


def _match(text, table):
    t = (text or "").lower()
    return sorted({label for k, label in table.items() if re.search(r"\b" + re.escape(k) + r"\b", t)})


def handler(context):
    g = lambda k: _load(context.get_input(k))
    installs = g("hg_installs") or []
    installs = installs if isinstance(installs, list) else []
    ehr_hits, portal_hits = [], []
    for i in installs:
        blob = " ".join(str(i.get(k, "")) for k in ("product_name", "vendor_name", "product_category_name"))
        for v in _match(blob, EHR):
            ehr_hits.append({"vendor": v, "product": i.get("product_name"), "first_verified": i.get("product_first_verified_date")})
        portal_hits += _match(blob, PORTAL)
    ehr_vendors = sorted({h["vendor"] for h in ehr_hits})
    if len(ehr_vendors) == 1:
        ehr_status = "confirmed_structured"
    elif len(ehr_vendors) > 1:
        ehr_status = "conflict"
    else:
        ehr_status = "unknown"

    companies = g("hg_companies") or []
    companies = companies if isinstance(companies, list) else []
    sel = next((c for c in companies if c.get("selected")), companies[0] if companies else {})
    parent = sel.get("global_hq_name") or sel.get("corporate_parent_name") or ""
    own = (context.get_input("company_name") or "").strip()
    parent_status = "self" if parent and parent.lower() == own.lower() else ("structured" if parent else "unknown")

    cutoff = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 365 * 86400))  # ISO dates compare as strings
    events = g("pl_events") or []
    events = events if isinstance(events, list) else []
    ma = []
    for e in events:
        if e.get("category") not in MA_CATEGORIES:
            continue
        d = e.get("found_at") or e.get("effective_date") or ""
        if d and d[:10] < cutoff:
            continue
        art = e.get("news_article_attributes") or {}
        ma.append({"category": e.get("category"), "date": d[:10], "summary": e.get("article_sentence") or art.get("title"),
                   "url": art.get("url"), "confidence": e.get("confidence")})
    ma.sort(key=lambda x: x["date"] or "", reverse=True)

    jobs = g("jobs") or []
    jobs = jobs if isinstance(jobs, list) else []

    # No structured action in this workspace returns clinic/location count, so it stays missing
    # until a structured source is added; that is what sends providers to the fallback.
    locs = context.get_input("location_count")
    missing = [k for k, v in (("ehr", ehr_status in ("unknown", "conflict")), ("parent", parent_status == "unknown"),
                              ("location_count", not locs)) if v]
    latest = ma[0] if ma else {}
    # Fallback research only for identity-matched providers with a decision-critical gap.
    needs_fallback = (context.get_input("segment") == "provider"
                      and context.get_input("identity_status") == "matched" and bool(missing))
    return {
        "ehr_vendor": ehr_vendors[0] if ehr_status == "confirmed_structured" else "",
        "ehr_candidates": ", ".join(ehr_vendors),
        "ehr_status": ehr_status,
        "ehr_evidence": json.dumps(ehr_hits[:5]),
        "portal_vendor_clue": ", ".join(sorted(set(portal_hits))),
        "parent_name": parent,
        "parent_status": parent_status,
        "ma_event_count": len(ma),
        "latest_event_type": latest.get("category") or "",
        "latest_event_date": latest.get("date") or "",
        "latest_event_summary": latest.get("summary") or "",
        "latest_event_url": latest.get("url") or "",
        "relevant_job_count": len(jobs),
        "missing_fields": ", ".join(missing),
        "needs_fallback": needs_fallback,
        "field_source": "hg_insights+predictleads+clay_jobs",
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
