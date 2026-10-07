import re


def _clean_domain(raw):
    d = (raw or "").strip().lower()
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0]
    if d.startswith("www."):
        d = d[4:]
    return d


def _tri(raw):
    v = (raw or "").strip().lower()
    if v in ("true", "yes", "y", "1"):
        return "yes"
    if v in ("false", "no", "n", "0"):
        return "no"
    return "unknown"


def handler(context):
    domain = _clean_domain(context.get_input("account_domain"))
    return {
        "source_row_id": (context.get_input("source_row_id") or "").strip(),
        "account_name": (context.get_input("account_name") or "").strip(),
        "account_domain": domain,
        "has_domain": bool(domain) and "." in domain,
        "vertical": (context.get_input("vertical") or "").strip() or "unknown",
        "country": (context.get_input("country") or "").strip().upper() or "unknown",
        "is_customer": _tri(context.get_input("is_customer")),
        "do_not_contact": _tri(context.get_input("do_not_contact")),
        "suppressed": _tri(context.get_input("is_customer")) == "yes"
        or _tri(context.get_input("do_not_contact")) == "yes",
    }
