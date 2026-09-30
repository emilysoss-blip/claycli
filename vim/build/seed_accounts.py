# -*- coding: utf-8 -*-
"""Vim POC seed: 10 example logos, normalized to the build guide's headers.

Company fields come from Clay company search (Clay Demos (GTM) workspace, 2026-09-30).
Clinical fields (NPI, EHR, portal, locations) are left blank on purpose: the workflow's
native enrichment fills them. Blank means unknown, not no.
"""
import csv, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADERS = [
    "source_row_id", "segment", "icp_model_account", "clay_company_id", "company_name",
    "company_domain", "company_linkedin_url", "parent_name_hint", "parent_hint_source",
    "organization_npi", "address", "city", "state", "country", "specialty",
    "employee_count_linkedin", "identity_note", "hubspot_company_id", "owner_id",
    "lifecycle_stage", "do_not_contact",
]

# (segment, icp_model, clay_id, name, domain, linkedin, parent_hint, parent_source,
#  city, state, specialty, employees, identity_note)
ROWS = [
("payer", "false", "33626243", "UnitedHealthcare", "uhc.com",
 "https://www.linkedin.com/company/unitedhealthcare", "UnitedHealth Group", "clay_description",
 "Minnetonka", "MN", "", "16951", ""),
("payer", "false", "31619759", "Aetna, a CVS Health Company", "aetna.com",
 "https://www.linkedin.com/company/aetna", "CVS Health", "clay_description",
 "Hartford", "CT", "", "41131", "Parent CVS Health also owns Oak Street Health: keep both as separate accounts"),
("payer", "false", "20433793", "Cigna Healthcare", "cigna.com",
 "https://www.linkedin.com/company/cignahealthcare", "", "",
 "Bloomfield", "CT", "", "29381", "Evernorth is a separate LinkedIn entity; not merged"),
("payer", "false", "30291322", "Humana", "humana.com",
 "https://www.linkedin.com/company/humana", "", "",
 "Louisville", "KY", "", "49156", ""),
("payer", "false", "2469366", "Elevance Health", "elevancehealth.com",
 "https://www.linkedin.com/company/elevance-health", "", "",
 "Indianapolis", "IN", "", "44163", "Shared domain: legacy 'Anthem, Inc.' entity 18532299 also resolves to elevancehealth.com; pinned to 2469366"),
("provider", "true", "15946144", "VillageMD", "villagemd.com",
 "https://www.linkedin.com/company/villagemd", "", "",
 "Chicago", "IL", "primary care; multi-specialty; urgent care", "1649", "LinkedIn headcount understates footprint (description: 20,000+ staff, 700 locations)"),
("provider", "true", "26420863", "Oak Street Health", "oakstreethealth.com",
 "https://www.linkedin.com/company/oak-street-health", "CVS Health", "clay_description",
 "Chicago", "IL", "primary care (Medicare, value-based)", "5278", "Parent CVS Health shared with Aetna"),
("provider", "true", "34520624", "One Medical", "onemedical.com",
 "https://www.linkedin.com/company/one-medical-group", "", "",
 "San Francisco", "CA", "primary care", "3339", "Audience record name is legacy '1Life Healthcare'"),
("provider", "true", "14405981", "DaVita Kidney Care", "davita.com",
 "https://www.linkedin.com/company/davita", "", "",
 "Denver", "CO", "nephrology; dialysis", "40410", ""),
("provider", "true", "25325124", "LifeStance Health", "lifestance.com",
 "https://www.linkedin.com/company/lifestance-health", "", "",
 "Scottsdale", "AZ", "behavioral health", "5636", "Shared domain: 2 small practice entities (1600448, 3327234) also on lifestance.com; pinned to 25325124"),
]

def main():
    out = os.path.join(BASE, "data", "seed_accounts.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADERS)
        for i, (seg, icp, cid, name, dom, li, ph, phs, city, st, spec, emp, note) in enumerate(ROWS, 1):
            w.writerow([f"vim-{i:03d}", seg, icp, cid, name, dom, li, ph, phs,
                        "", "", city, st, "US", spec, emp, note, "", "", "", "false"])
    print(f"wrote {out} ({len(ROWS)} rows)")

if __name__ == "__main__":
    main()
