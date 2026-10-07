def handler(context):
    suppressed = bool(context.get_input("suppressed"))
    if suppressed:
        tier, reason = "Excluded", "Existing customer or do-not-contact; skipped before paid enrichment"
    else:
        tier, reason = "Review", "No usable domain; identity must be resolved before enrichment"
    return {
        "source_row_id": context.get_input("source_row_id") or "",
        "account_name": context.get_input("account_name") or "",
        "fit_tier": tier,
        "score_reasons": reason,
        "score_version": "eightfold-fit-v0.1-calibration",
    }
