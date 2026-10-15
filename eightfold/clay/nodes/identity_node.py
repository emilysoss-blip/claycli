# Identity gate input. Domains that resolve to the wrong company, a stale parent, or only
# satellites are unresolved unless the row carries a pinned LinkedIn company URL.
UNSAFE = ("wrong_company", "no_usable_match", "stale_parent", "satellite_only")


def handler(context):
    status = (context.get_input("domain_match_status") or "").strip()
    ident = (context.get_input("enrichment_identifier") or "").strip()
    pinned = ident.startswith("https://www.linkedin.com/company/")
    if not ident:
        ok, why = False, "no identifier"
    elif status in UNSAFE and not pinned:
        ok, why = False, "domain is " + status + " and no LinkedIn URL is pinned"
    else:
        ok, why = True, ("pinned LinkedIn URL" if pinned else "domain (" + (status or "unclassified") + ")")
    return {
        "identity_resolved": ok,
        "identifier_type": "company_linkedin_url" if pinned else "company_domain",
        "identity_reason": why,
    }
