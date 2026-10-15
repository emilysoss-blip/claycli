# -*- coding: utf-8 -*-
"""
Deterministic why-now briefs (build guide section 9). A template, not a generator.

One brief per account. If the account has a qualified talent-leadership event, the brief
names it, dates it and links the evidence. If it has none, it says so in exactly those words
rather than reaching for urgency the data does not support.

Event policy (proposed pilot values; Eightfold's demand gen lead to calibrate against their cadence):
  - an event counts for the brief within the 18-month qualification window
  - it creates a TASK only within 90 days (3 calendar months at month granularity)
  - one task per account per 7 days, none while one is open; dedupe on
    account + event type + evidence URL + event date
"""
import csv, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_WINDOW_MONTHS = 3

TEMPLATE = ("{account} meets {fit_reasons}. {event_type} occurred on {event_date}: {event_summary}. "
            "Evidence: {event_url}. Relevant persona: {persona_group}. "
            "Suggested action: {approved_action_for_event_type}.")
NO_SIGNAL = "Fit-led account; no verified recent trigger."

# Proposed actions per (event type, persona). Every one needs Eightfold's approval before use;
# the label says so on the row so nobody mistakes a proposal for policy.
ACTIONS = {
    ("NewHire", "economic_buyer"):      "PROPOSED - executive first-90-days sequence plus CHRO roundtable invite",
    ("NewHire", "ta_owner"):            "PROPOSED - TA leader sequence on requisition volume and recruiter capacity",
    ("NewHire", "talent_intelligence"): "PROPOSED - talent intelligence briefing; strongest category match",
    ("NewHire", "hr_technology"):       "PROPOSED - HR tech architecture conversation (TalentForge build-your-own path)",
}

# Guide section 8: the economic buyer first; Talent Intelligence is the closest category match.
PERSONA_RANK = {"economic_buyer": 0, "talent_intelligence": 1, "ta_owner": 2, "hr_technology": 3}

PERSONA_LABEL = {
    "economic_buyer": "CHRO / CPO (economic buyer)",
    "ta_owner": "Head of Talent Acquisition (operational owner)",
    "talent_intelligence": "Talent Intelligence / People Analytics",
    "hr_technology": "HR / TA Technology",
}


def fit_reasons(t):
    met = [k.replace("check_", "") for k, v in t.items() if k.startswith("check_") and v == "yes"]
    unknown = [k.replace("check_", "") for k, v in t.items() if k.startswith("check_") and v == "unknown"]
    s = "fit on " + ", ".join(met) + f" ({t['fit_score']}/{t['fit_best_case']} possible)"
    if unknown:
        s += "; " + ", ".join(unknown) + " not yet verified"
    return s


def main():
    tiers = {t["account_key"]: t for t in json.load(open(os.path.join(BASE, "data", "tiered_accounts.json"), encoding="utf-8"))}
    full = os.path.join(BASE, "data", "talent_leaders.json")
    have_people = os.path.exists(full)
    src = full if have_people else os.path.join(BASE, "data", "talent_leaders_public.json")
    leaders = json.load(open(src, encoding="utf-8"))
    qualified = [p for p in leaders if p["qualified"] == "yes"]

    rows, public_rows, seen = [], [], set()
    for key, t in tiers.items():
        # Lead with the strongest persona, then an unbanded title, then the most recent start.
        events = sorted([p for p in qualified if p["account_key"] == key],
                        key=lambda p: (PERSONA_RANK[p["persona_group"]], p["title_banded"] == "yes",
                                       -int(p["start"].replace("-", ""))))
        ident = lambda e: e.get("linkedin_url") or e["title"]
        events = [e for e in events if (key, "NewHire", ident(e), e["start"]) not in seen]
        for e in events:
            seen.add((key, "NewHire", ident(e), e["start"]))
        e = events[0] if events else None
        for public, out in ((False, rows), (True, public_rows)):
            if public is False and not have_people:
                continue
            if e:
                who = "A new" if public else f"{e['name']} started as"
                summary = f"{who} {e['title']}" + (" started" if public else "")
                if e["division"] != e["employer_in_clay"] and e["division"].lower() not in e["title"].lower():
                    summary += f" ({e['division']})"
                brief = TEMPLATE.format(
                    account=t["account_name"], fit_reasons=fit_reasons(t),
                    event_type="NewHire (talent leader joined)", event_date=e["start"], event_summary=summary,
                    event_url="LinkedIn profile, held in local data" if public else e["linkedin_url"],
                    persona_group=PERSONA_LABEL[e["persona_group"]],
                    approved_action_for_event_type=ACTIONS[("NewHire", e["persona_group"])])
                task = "yes" if e["months_in_role"] <= TASK_WINDOW_MONTHS else "no"
            else:
                brief, task = NO_SIGNAL, "no"
            row = {
                "account_key": key, "account_name": t["account_name"], "fit_tier": t["fit_tier"],
                "motion": "signal-led" if e else "fit-led", "qualified_events": len(events),
                "latest_event_date": e["start"] if e else "",
                "latest_event_title": e["title"] if e else "",
                "create_task_now": task, "why_now": brief,
                "other_qualified_leaders": "; ".join(
                    f"{x['title'] if public else x['name']} ({x['start']})" for x in events[1:]),
                "salesforce_owner": "unknown (pending Salesforce export)",
                "recent_touches": "unknown (pending Marketo/Salesforce)",
                "suppression_status": "unknown (pending Salesforce export)",
            }
            if not public:
                row["latest_event_person"] = e["name"] if e else ""
            out.append(row)

    order = lambda r: (r["motion"] != "signal-led", -int(r["latest_event_date"].replace("-", "") or 0))
    for name, out in (("why_now", rows), ("why_now_public", public_rows)):
        if not out:
            continue
        out.sort(key=order)
        path = os.path.join(BASE, "data", name + ".csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
        json.dump(out, open(path.replace(".csv", ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    sig = [r for r in public_rows if r["motion"] == "signal-led"]
    print(f"{len(sig)} signal-led, {len(public_rows) - len(sig)} fit-led; "
          f"tasks now: {sum(r['create_task_now'] == 'yes' for r in public_rows)}"
          + ("" if have_people else " (public data only)"))
    for r in sig:
        print(" ", r["why_now"])


if __name__ == "__main__":
    main()
