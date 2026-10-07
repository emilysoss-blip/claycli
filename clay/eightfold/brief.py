ACTIONS = {
    "signal": "Route to the new-talent-leader ABM play: first-90-days outreach to the leader plus their TA and people analytics team.",
    "fit": "Keep in the tiered ABM audience; no outreach trigger yet.",
}


def handler(context):
    g = lambda k: "" if context.get_input(k) is None else str(context.get_input(k)).strip()
    tier = g("fit_tier")
    signal_led = bool(context.get_input("signal_led"))
    leader = g("talent_leader")
    if signal_led and g("recent_leader_summary"):
        brief = "%s meets %s. Talent leadership change in the last 18 months: %s. Evidence: %s. Current senior talent leader: %s (%s). Suggested action: %s" % (
            g("account_name"), g("score_reasons"), g("recent_leader_summary"), g("recent_leader_url") or "none",
            leader or "unknown", g("talent_leader_title") or "title unknown", ACTIONS["signal"])
    else:
        brief = "%s meets %s. Fit-led account; no verified recent trigger. Suggested action: %s" % (
            g("account_name"), g("score_reasons"), ACTIONS["fit"])
    campaign_ready = tier in ("Tier 1", "Tier 2") and bool(leader) and g("evidence_url").startswith("http")
    return {"why_now": brief, "campaign_ready": campaign_ready,
            "salesforce_owner": "not connected (Salesforce writeback disabled for POC)"}
