# -*- coding: utf-8 -*-
"""
Normalize the airport list into BUYING CENTERS.

The airport row is the account. The buying center is who actually signs. These are not the
same thing and at 9 of the 50 airports they are not even the same company. This table is the
join that keeps a terminal-operator contact from being mis-filed as an authority contact.
"""
import csv, json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
airports = json.load(open(os.path.join(BASE,"data","airports.json"), encoding="utf-8"))

# What each role owns the budget for -> drives which offer and which titles to target.
SCOPE = {
 "Airport-wide authority":
   "Airport-wide network & OT, common-use passenger systems (CUPPS/CUSS), AODB/RMS, "
   "airport-wide cybersecurity, access control & perimeter, capital delivery programs, "
   "airfield systems, master-plan IT",
 "Parent authority (multi-asset)":
   "Enterprise IT standards, enterprise cybersecurity & identity, group procurement & vendor "
   "master agreements, shared data platform, capital program governance across multiple assets",
 "Terminal operator":
   "In-terminal IT & networks, baggage handling (BHS) and its controls, passenger processing "
   "(check-in, self-bag-drop, boarding, biometrics), terminal operations systems, retail/F&B "
   "systems, terminal-level cyber",
 "Handling / subsidiary operator":
   "Ground-handling and cargo systems, ramp and baggage operations technology, "
   "resource-management and crew/staff systems",
 "State / regulator (airside owner)":
   "Airfield and airside infrastructure, ATC-adjacent systems, national aviation security "
   "mandates, public tender issuance",
}

# Titles worth prospecting per role.
TITLES = {
 "Airport-wide authority":
   "CIO; Chief Information Officer; CISO; Director of IT; VP Technology; Chief Innovation Officer; "
   "Director of Airport Operations; COO; Chief Development Officer; VP Capital Programs; "
   "Director of Procurement; Chief Security Officer",
 "Parent authority (multi-asset)":
   "Group CIO; Group CISO; Chief Technology Officer; SVP Enterprise IT; Chief Procurement Officer; "
   "Director of Enterprise Architecture; Chief Digital Officer",
 "Terminal operator":
   "CEO (terminal company); CIO / Head of IT; Director of Terminal Operations; "
   "Head of Baggage Systems; Head of Passenger Experience; Director of Engineering; "
   "Procurement Manager; Head of Digital",
 "Handling / subsidiary operator":
   "COO; Head of IT; Director of Ground Operations; Head of Cargo Systems; Head of Innovation",
 "State / regulator (airside owner)":
   "Director General; Director of Aviation; Head of Airport Infrastructure Division; "
   "Chief Engineer; Tender/Contracts Officer",
}

rows = []
for a in airports:
    dom, iata = a["airport_domain"], a["iata_code"]

    # 1) the airport-wide authority (always exists)
    rows.append({
        "airport_domain": dom, "iata_code": iata, "airport_name": a["airport_name"],
        "buying_center_name": a["airport_authority_name"],
        "buying_center_domain": a["airport_authority_domain"] or dom,
        "role": "Airport-wide authority",
        "terminal_or_asset": "Airport-wide",
        "is_primary_buyer": "Yes",
        "owns_budget_for": SCOPE["Airport-wide authority"],
        "target_titles": TITLES["Airport-wide authority"],
        "notes": a["systems_owner_note"],
    })

    # 2) the parent, only when it is a genuinely distinct legal/technology layer
    pd_, pn = a["parent_authority_domain"], a["parent_authority_name"]
    if pn and pd_ and pd_ != (a["airport_authority_domain"] or dom):
        shared = [x["iata_code"] for x in airports
                  if x["parent_authority_domain"] == pd_ and x["iata_code"] != iata]
        rows.append({
            "airport_domain": dom, "iata_code": iata, "airport_name": a["airport_name"],
            "buying_center_name": pn, "buying_center_domain": pd_,
            "role": "Parent authority (multi-asset)",
            "terminal_or_asset": "Enterprise / multi-airport",
            "is_primary_buyer": "No",
            "owns_budget_for": SCOPE["Parent authority (multi-asset)"],
            "target_titles": TITLES["Parent authority (multi-asset)"],
            "notes": ("Shared parent with " + ", ".join(sorted(shared)) +
                      " on this list - DEDUPE contacts across those rows."
                      if shared else "Parent layer; verify whether IT is centralized here or at the airport."),
        })

    # 3) each terminal operator / handler, parsed from "Name (Terminal) | domain"
    for t in [x.strip() for x in a["terminal_operators"].split(";") if x.strip()]:
        name_part, _, tdom = t.partition("|")
        name_part, tdom = name_part.strip(), tdom.strip()
        asset = ""
        if "(" in name_part and name_part.endswith(")"):
            name_part, _, asset = name_part.partition("(")
            name_part, asset = name_part.strip(), asset.rstrip(")").strip()
        low = (name_part + " " + asset).lower()
        if "handling" in low or "dnata" in low or "aviation services" in low:
            role = "Handling / subsidiary operator"
        elif "ministry" in low or "mlit" in low:
            role = "State / regulator (airside owner)"
        else:
            role = "Terminal operator"
        rows.append({
            "airport_domain": dom, "iata_code": iata, "airport_name": a["airport_name"],
            "buying_center_name": name_part, "buying_center_domain": tdom,
            "role": role, "terminal_or_asset": asset or "Terminal",
            "is_primary_buyer": "No",
            "owns_budget_for": SCOPE[role], "target_titles": TITLES[role],
            "notes": "Buys independently of the airport-wide authority. Do not assume authority-level contracts cover this asset.",
        })

    # 4) airside owner where it is legally split from the terminal companies
    if a["parent_authority_domain"] == "mlit.go.jp":
        rows[-1]["notes"] += " Airside is separately owned by MLIT."

FIELDS = ["airport_domain","iata_code","airport_name","buying_center_name","buying_center_domain",
          "role","terminal_or_asset","is_primary_buyer","owns_budget_for","target_titles","notes"]
with open(os.path.join(BASE,"data","buying_centers.csv"),"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
json.dump(rows, open(os.path.join(BASE,"data","buying_centers.json"),"w",encoding="utf-8"),
          indent=2, ensure_ascii=False)

print("buying centers:", len(rows), "across", len({r['airport_domain'] for r in rows}), "airports")
from collections import Counter
for k,v in Counter(r["role"] for r in rows).most_common(): print(f"  {k}: {v}")
multi = Counter(r["airport_domain"] for r in rows)
print("\nairports with >1 buying center:", sum(1 for v in multi.values() if v>1))
print("most complex:")
for d,c in multi.most_common(6):
    print(f"  {d}: {c} buying centers")
