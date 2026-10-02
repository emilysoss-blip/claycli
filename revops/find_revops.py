#!/usr/bin/env python3
"""Find every RevOps manager / head / leader at the accounts in a Clay Audience segment.

Uses only the Clay CLI (`npm i -g @clay-run/cli`, then `clay login`):

  1. `clay audiences records`  - read the accounts in the segment (for the coverage report)
  2. `clay searches query-mode` - one people search scoped to the segment with
                                  clay.filter_to_companies(@audience_segment(...))
  3. classify each person by level and write two CSVs

The segment is a live filter (Salesforce owner = you), so re-running picks up
accounts added to or removed from your book. People search costs no credits;
it only counts against the workspace search-result quota.

  python3 revops/find_revops.py
  python3 revops/find_revops.py --audience-id audseg_xxx --out-dir revops
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys

# "Emily Soss accounts": sfdc_owner_id contains 005a700000HVPht (61 accounts).
DEFAULT_AUDIENCE_ID = "audseg_0tkp7k67sq7xSYd9Wgr"

TITLE_INCLUDE = ("revenue operations", "revops", "rev ops", "revenue ops")
# Second pass, only for accounts with no RevOps title: the function usually lives here instead.
# CRM / Salesforce titles are left out: they are mostly developers and resellers.
ADJACENT_INCLUDE = (
    "sales operations", "sales ops", "gtm operations", "go-to-market operations",
    "go to market operations", "commercial operations", "business operations",
    "sales strategy and operations", "gtm systems",
)
# Drops individual contributors and roles that only mention RevOps in passing.
TITLE_EXCLUDE = (
    "analyst", "analista", "specialist", "coordinator", "associate", "intern",
    "assistant", "administrator", "representative", "consultant",
    "people business partner",
)

LEVELS = [
    ("Leader", r"\b(chief|cro|svp|evp|vp|vice president|head|director)\b"),
    ("Manager", r"\b(manager|supervisor|lead|architect|principal)\b"),
]


def clay(*args):
    env = dict(os.environ, NODE_USE_ENV_PROXY="1", NODE_NO_WARNINGS="1")
    proc = subprocess.run(["clay", *args], capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        sys.exit(f"clay {' '.join(args[:3])} failed (exit {proc.returncode}): {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def quoted(values):
    return ", ".join(f'"{v}"' for v in values)


def build_query(companies, titles):
    return (
        f"select from people where clay.filter_to_companies({companies}) "
        f"and experiences.any(is_current = true and job_title contains ({quoted(titles)}) "
        f"and not job_title contains ({quoted(TITLE_EXCLUDE)}))"
    )


def fetch_accounts(audience_id):
    ids = clay("audiences", "records", "search-ids", "--entity-type", "companies",
               "--audience-id", audience_id, "--limit", "2000")["data"]
    accounts = []
    for i in range(0, len(ids), 100):
        batch = ",".join(map(str, ids[i:i + 100]))
        for rec in clay("audiences", "records", "get", "--entity-type", "companies", "--ids", batch)["data"]:
            f = rec["fields"]
            accounts.append({"record_id": rec["recordId"], "name": f.get("org_name") or "",
                             "domain": f.get("domain") or "", "linkedin_url": f.get("linkedin_url") or ""})
    return accounts


def fetch_people(query):
    search_id = clay("searches", "query-mode", "create", "--query", query)["searchId"]
    people = []
    while True:
        page = clay("searches", "query-mode", "run", search_id, "--limit", "500")
        people.extend(page["data"])
        if not page["hasMore"]:
            return search_id, people


def norm(name):
    name = re.sub(r"\(.*?\)|\|.*", "", name.lower())
    name = re.sub(r"\b(inc|llc|ltd|corp|corporation|global|ai|systems|technologies)\b", "", name)
    return re.sub(r"[^a-z0-9]", "", name)


def keys(text):
    """Normalized name variants: whole name plus each part split on parens / pipes."""
    parts = [text] + re.split(r"[()|]", text)
    return {k for k in (norm(re.sub(r"\bformerly\b", "", x)) for x in parts) if len(k) >= 3}


def match_account(company, accounts):
    company_keys = keys(company)
    for acct in accounts:
        acct_keys = keys(acct["name"])
        if acct["domain"]:
            acct_keys.add(norm(acct["domain"].split(".")[0]))
        for a in company_keys:
            for b in acct_keys:
                if a == b or a.startswith(b) or b.startswith(a):
                    return acct
    return None


def to_rows(people, accounts, match_type):
    rows = []
    for p in people:
        exp = next((e for e in p["matched_experiences"] if not e.get("end_date")), p["matched_experiences"][0])
        acct = match_account(exp.get("company") or "", accounts)
        rows.append({
            "account": acct["name"] if acct else exp.get("company") or "",
            "account_domain": acct["domain"] if acct else "",
            "match_type": match_type,
            "name": p.get("name") or "",
            "title": exp.get("title") or "",
            "level": level_of(exp.get("title") or ""),
            "location": (p.get("location") or {}).get("name") or "",
            "linkedin_url": p.get("linkedin_url") or "",
            "start_date": exp.get("start_date") or "",
        })
    return rows


def level_of(title):
    t = title.lower()
    for label, pattern in LEVELS:
        if re.search(pattern, t):
            return label
    return "Unclear"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audience-id", default=DEFAULT_AUDIENCE_ID)
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--no-adjacent", action="store_true",
                    help="skip the Sales/GTM/Business Ops pass for accounts with no RevOps title")
    args = ap.parse_args()

    accounts = fetch_accounts(args.audience_id)
    segment = f'@audience_segment("{args.audience_id}")'
    search_id, people = fetch_people(build_query(segment, TITLE_INCLUDE))
    rows = to_rows(people, accounts, "revops")

    # Pass 2: accounts with no RevOps title get an adjacent-ops search, keyed on
    # the account's domain or LinkedIn URL (accounts with neither are skipped).
    covered = {r["account"] for r in rows}
    uncovered = [a for a in accounts if a["name"] not in covered]
    idents = sorted({a["domain"] or a["linkedin_url"] for a in uncovered} - {""})
    adjacent_search_id = None
    if idents and not args.no_adjacent:
        adjacent_search_id, more = fetch_people(build_query(f"({quoted(idents)})", ADJACENT_INCLUDE))
        rows += [r for r in to_rows(more, accounts, "adjacent")
                 if r["account"] not in covered and r["level"] != "Unclear"]

    seen, unique = set(), []
    for r in rows:
        # Clay can hold two profiles for one person, so match on who they are too.
        key = (r["account"], r["name"], r["title"])
        if key not in seen and (not r["linkedin_url"] or r["linkedin_url"] not in seen):
            seen.update({key, r["linkedin_url"]})
            unique.append(r)
    rows = unique
    order = {"Leader": 0, "Manager": 1, "Unclear": 2}
    rows.sort(key=lambda r: (r["account"].lower(), r["match_type"] != "revops", order[r["level"]], r["name"]))

    os.makedirs(args.out_dir, exist_ok=True)
    contacts_path = os.path.join(args.out_dir, "revops_contacts.csv")
    with open(contacts_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["account"])
        w.writeheader()
        w.writerows(rows)

    hits = {}
    for r in rows:
        hits.setdefault(r["account"], []).append(r)
    coverage_path = os.path.join(args.out_dir, "account_coverage.csv")
    with open(coverage_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["account", "domain", "revops_found", "leaders", "managers", "unclear_level", "adjacent_found"])
        for a in sorted(accounts, key=lambda a: a["name"].lower()):
            rs = [r for r in hits.get(a["name"], []) if r["match_type"] == "revops"]
            w.writerow([a["name"], a["domain"], len(rs),
                        sum(r["level"] == "Leader" for r in rs),
                        sum(r["level"] == "Manager" for r in rs),
                        sum(r["level"] == "Unclear" for r in rs),
                        sum(r["match_type"] == "adjacent" for r in hits.get(a["name"], []))])

    revops = [r for r in rows if r["match_type"] == "revops"]
    print(json.dumps({
        "audience_id": args.audience_id,
        "search_id": search_id,
        "adjacent_search_id": adjacent_search_id,
        "accounts": len(accounts),
        "accounts_with_revops": len({r["account"] for r in revops}),
        "accounts_with_adjacent_only": len({r["account"] for r in rows if r["match_type"] == "adjacent"}),
        "accounts_with_nobody": sum(1 for a in accounts if a["name"] not in hits),
        "revops_people": len(revops),
        "revops_by_level": {k: sum(r["level"] == k for r in revops) for k in order},
        "adjacent_people": len(rows) - len(revops),
        "contacts_csv": contacts_path,
        "coverage_csv": coverage_path,
    }, indent=2))


if __name__ == "__main__":
    main()
