PERSONAS = [
    ("Economic buyer (CHRO / CPO)", ["chief human resources", "chief people", "chro", "chief talent", "chief hr",
                                    "svp, human resources", "svp human resources", "senior vice president, human resources",
                                    "evp, human resources", "executive vice president, human resources", "head of hr", "head of people"]),
    ("Talent intelligence / people analytics", ["talent intelligence", "people analytics", "workforce analytics", "workforce planning"]),
    ("HR technology (CIO / HRIT)", ["hr technology", "hris", "people technology", "hr systems", "hr digital"]),
    ("Operational owner (Head / VP of TA)", ["talent acquisition", "recruiting", "recruitment", "head of talent", "global head of talent"]),
]
SENIOR = ["chief", "chro", "svp", "evp", "senior vice president", "executive vice president", "vice president", "vp", "head", "director"]


def handler(context):
    p = context.get_input("profile") or {}
    title = p.get("latest_experience_title") or (p.get("matched_experience") or {}).get("job_title") or ""
    low = title.lower()
    persona = next((label for label, keys in PERSONAS if any(k in low for k in keys)), "")
    senior = any(s in low for s in SENIOR)
    return {
        "event_id": context.get_input("event_id") or "",
        "full_name": p.get("name") or "",
        "first_name": p.get("first_name") or (p.get("name") or "").split(" ")[0],
        "title": title,
        "start_date": p.get("latest_experience_start_date") or (p.get("matched_experience") or {}).get("start_date") or "",
        "company": p.get("latest_experience_company") or "",
        "domain": p.get("domain") or "",
        "profile_url": context.get_input("profile_url") or p.get("url") or "",
        "location": p.get("location_name") or "",
        "persona_group": persona,
        "qualifies": bool(persona) and senior and not bool(context.get_input("is_initial_check")),
    }
