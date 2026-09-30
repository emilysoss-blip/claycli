import re

def handler(context):
    g = lambda k: (context.get_input(k) or "").strip()
    dom = g("company_domain").lower()
    dom = re.sub(r"^https?://", "", dom)
    dom = re.sub(r"^www\.", "", dom).split("/")[0]
    li = g("company_linkedin_url").lower().rstrip("/")
    li = re.sub(r"^https?://(www\.)?", "https://www.", li) if li else ""
    clay_id = g("clay_company_id")
    # Identity: matched only when the row is pinned to one Clay company AND one LinkedIn page.
    # Shared domains (elevancehealth.com, lifestance.com) make domain-only identity ambiguous.
    if clay_id and li:
        status = "matched"
    elif dom:
        status = "ambiguous"
    else:
        status = "unmatched"
    return {
        "account_key": clay_id or dom,
        "company_domain": dom,
        "company_linkedin_url": li,
        "identity_status": status,
        "segment": g("segment").lower() or "unknown",
        "country": g("country").upper(),
    }
