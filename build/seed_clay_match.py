# -*- coding: utf-8 -*-
"""
Observed Clay company-match quality per enrichment domain.

Recorded from live Clay `search-companies` runs on 2026-09-28 against all 47 unique
enrichment domains. This is NOT a projection - every row is what Clay actually returned.

Why this table exists: airports break domain-keyed company enrichment. A single airport
domain can resolve to a stale page, a marketing sub-brand, a real-estate subsidiary, or the
whole city government. If you enrich on the domain alone, a meaningful share of rows silently
attach to the wrong company. Pinning linkedin_company_url per row is the fix.
"""
import csv, json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (enrichment_domain, quality, matched_name, linkedin_slug, clay_employee_count, issue, action)
OK, SAT, NONE = "clean_match", "satellite_only", "no_match"
M = [
 ("dfwairport.com",OK,"Dallas Fort Worth International Airport (DFW)","dfwairport",3422,"","Use as-is"),
 ("portseattle.org",OK,"Port of Seattle","port-of-seattle",2096,"Count is PORT-WIDE (seaport+airport), not the aviation division","Filter people by Aviation division; do not use headcount as airport size"),
 ("flydenver.com",OK,"Denver International Airport - City & County of Denver Dept of Aviation","city-&-county-of-denver---department-of-aviation",1218,"","Use as-is"),
 ("flysfo.com",OK,"San Francisco International Airport","flysfo",1359,"","Use as-is"),
 ("atl.com",OK,"Hartsfield-Jackson Atlanta International Airport","atlairport",696,"Second stale record on same domain ('Department of Aviation', 162, industry=Accounting)","Pin LinkedIn URL to atlairport"),
 ("lawa.org",OK,"Los Angeles World Airports","los-angeles-world-airports",1097,"Only resolves on lawa.org - flylax.com returns nothing","Enrich on lawa.org, keep flylax.com as the row key"),
 ("san.org",OK,"San Diego County Regional Airport Authority","sdcraa",439,"","Use as-is"),
 ("mwaa.com",OK,"Metropolitan Washington Airports Authority","mwaahq",1173,"One record serves BOTH the IAD and DCA rows","Dedupe contacts across IAD/DCA"),
 ("flychicago.com",OK,"Chicago Department of Aviation (CDA) - O'Hare & Midway","chicago-department-of-aviation",532,"One record serves ORD and MDW","Disambiguate by IATA, not domain"),
 ("massport.com",OK,"Massachusetts Port Authority","massachusetts-port-authority",774,"Port-wide (airports+seaport+cruise)","Filter people by aviation"),
 ("flynashville.com",OK,"Metropolitan Nashville Airport Authority","mnaa",306,"","Use as-is"),
 ("metroairport.com",OK,"Wayne County Airport Authority","wayne-county-airport-authority",459,"","Use as-is"),
 ("tampaairport.com",OK,"Tampa International Airport (TPA)","tampa-international-airport",439,"Duplicate HCAA record (405) is explicitly retired ('We've consolidated')","Pin LinkedIn URL to tampa-international-airport"),
 ("slcairport.com",OK,"Salt Lake City International Airport","slc-international-airport",192,"","Use as-is"),
 ("harryreidairport.com",OK,"Harry Reid International Airport","lasairport",425,"Second record 'Las Vegas Air Service Development' is a route-marketing page","Pin LinkedIn URL to lasairport"),
 ("fly2houston.com",OK,"Houston Airport System","houston-airports",498,"One record serves IAH, HOU and EFD","Disambiguate by IATA, not domain"),
 ("skyharbor.com",OK,"Phoenix Sky Harbor International Airport","phoenix-sky-harbor-international-airport",336,"Size band says 10,001+ but employee_count says 336","Trust neither as authority headcount; use dept budget/org chart"),
 ("phl.org",OK,"Philadelphia International Airport (PHL)","phlairport",306,"","Use as-is"),
 ("cltairport.com",OK,"Charlotte Douglas International Airport","charlotte-douglas-international-airport",502,"","Use as-is"),
 ("bwiairport.com",OK,"BWI Thurgood Marshall Airport","bwi_airport",67,"employee_count 67 vs size band 10,001+ - almost certainly wrong","Do not use headcount; MAA staff sit under MDOT"),
 ("metroairports.org",OK,"Metropolitan Airports Commission","metroairportsmn",511,"Only resolves on metroairports.org, not mspairport.com","Enrich on metroairports.org"),
 ("yvr.ca",OK,"Vancouver Airport Authority","vancouver-airport-authority",798,"","Use as-is"),
 ("admtl.com",OK,"ADM Aeroports de Montreal","adm-aeroports-de-montreal",730,"","Use as-is"),
 ("heathrow.com",OK,"Heathrow","heathrow-airport",6033,"Legal entity in CRM is 'FGP TOPCO'; Ardian investment dated 2025-07-08","Keep legal-entity alias for CRM matching"),
 ("gatwickairport.com",OK,"London Gatwick","gatwick-airport",1922,"","Use as-is"),
 ("aena.es",OK,"Aena","aena",5412,"ONE record covers 46 Spanish airports - no MAD-specific entity exists","Treat as network account; MAD is not separately addressable"),
 ("fraport.com",OK,"Fraport AG","fraport-ag",3331,"Group count only (29 airports, 4 continents); FRA site staff far higher","Use for group-level buyer; not FRA headcount"),
 ("flughafen-zuerich.ch",OK,"Zurich Airport Ltd","zurich-airport-ltd",1272,"~1,700 direct staff vs 27,000 across 280 partner firms on site","Authority staff only"),
 ("daa.ie",OK,"daa","dublin-airport-authority-daa-",2407,"Covers Dublin+Cork+ARI retail+daa International","Filter to Dublin Airport"),
 ("dubaiairports.ae",OK,"Dubai Airports","dubaiairports",10432,"Count looks inflated for an asset-owner that outsources heavily","Verify before using as department-size proxy"),
 ("dohahamadairport.com",OK,"Hamad International Airport","hamad-international-airport",2979,"Operator is MATAR under Qatar Airways Group","Also enrich qatarairways.com as the true parent"),
 ("changiairport.com",OK,"Changi Airport Group","changiairportgroup",2674,"","Use as-is"),
 ("airport.kr",OK,"Incheon International Airport Corporation","incheon-international-airport-corporation",584,"","Use as-is"),
 ("gru.com.br",OK,"GRU Airport - Aeroporto Internacional de Sao Paulo","gru-airport---aeroporto-internacional-de-s-o-paulo",2039,"","Use as-is"),
 ("aicm.com.mx",OK,"Aeropuerto Internacional de la Ciudad de Mexico","aeropuerto-internacional-de-la-ciudad-de-méxico",582,"","Use as-is"),
 ("austintexas.gov",SAT,"City of Austin / Austin Public Library / Austin Water","city-of-austin",8992,"Domain returns the whole city: City of Austin (8,992), Austin Public Library (280), Austin Water (534). The real AUS page (226) exists but is NOT the top match","MUST pin LinkedIn URL to austin-bergstrom-international-airport"),
 ("schiphol.nl",SAT,"Aviation Solutions - by Schiphol Group / Schiphol Real Estate","aviation-solutions-by-schiphol-group",18,"Royal Schiphol Group's MAIN page was never returned - only an 18-person product unit and a 71-person real-estate arm","Pin LinkedIn URL to Royal Schiphol Group manually"),
 ("munich-airport.com",SAT,"Munich Airport International / Munich Airport NJ LLC","munich-airport-international-gmbh",245,"Flughafen Muenchen GmbH's MAIN page was never returned. NOTE: the NJ subsidiary operates EWR Terminal A - a separate buying center","Pin FMG LinkedIn URL; treat Munich Airport NJ as its own EWR row"),
 ("panynj.gov",SAT,"John F. Kennedy International Airport / Port Of New York Authority","john-f.-kennedy-international-airport",58,"Both records are stale stubs (58 and 17 employees; one description references a 2011 anniversary). The real PANYNJ page was never returned","MUST pin PANYNJ LinkedIn URL - affects JFK, LGA and EWR rows"),
 ("adp.fr",NONE,"","",0,"No company record returned","Resolve Groupe ADP LinkedIn URL via Claygent, then pin"),
 ("istairport.com",NONE,"","",0,"No company record returned","Resolve iGA LinkedIn URL via Claygent, then pin"),
 ("eldorado.aero",NONE,"","",0,"No company record returned","Resolve Opain S.A. LinkedIn URL via Claygent, then pin"),
 ("sydneyairport.com.au",NONE,"","",0,"No company record returned (delisted 2022, disclosure dropped)","Resolve via Claygent; lean on Sydney Aviation Alliance/IFM reporting"),
 ("tokyo-airport-bldg.co.jp",NONE,"","",0,"No company record returned","Resolve Japan Airport Terminal Co. + TIAT separately, then pin"),
 ("orlandoairports.net",NONE,"","",0,"No company record returned","Resolve GOAA LinkedIn URL via Claygent, then pin"),
 ("miami-airport.com",NONE,"","",0,"No company record returned","Resolve MDAD LinkedIn URL via Claygent, then pin"),
 ("gtaa.com",NONE,"","",0,"No company record returned on gtaa.com or torontopearson.com","Resolve GTAA LinkedIn URL via Claygent, then pin"),
]

airports = json.load(open(os.path.join(BASE,"data","airports.json"), encoding="utf-8"))
rows_for = {}
for a in airports:
    rows_for.setdefault(a["enrichment_domain"], []).append(a["iata_code"])

out = []
for dom,q,name,slug,cnt,issue,action in M:
    out.append({
        "enrichment_domain": dom,
        "airports_affected": ", ".join(sorted(rows_for.get(dom, []))) or "(unmapped)",
        "match_quality": q,
        "clay_matched_name": name,
        "linkedin_company_url": f"https://www.linkedin.com/company/{slug}" if slug else "",
        "clay_employee_count": cnt or "",
        "headcount_trustworthy": "No" if (q != OK or issue) else "Yes",
        "issue": issue,
        "required_action": action,
    })

FIELDS = ["enrichment_domain","airports_affected","match_quality","clay_matched_name",
          "linkedin_company_url","clay_employee_count","headcount_trustworthy","issue","required_action"]
with open(os.path.join(BASE,"data","clay_match_quality.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(out)
json.dump(out, open(os.path.join(BASE,"data","clay_match_quality.json"),"w",encoding="utf-8"),
          indent=2, ensure_ascii=False)

covered = {r["enrichment_domain"] for r in out}
expected = set(rows_for)
print("domains audited:", len(out), "| unique enrichment domains in table:", len(expected))
print("missing from audit:", expected - covered or "none")
from collections import Counter
c = Counter(r["match_quality"] for r in out)
for k in (OK,SAT,NONE): print(f"  {k}: {c[k]}")
bad = [r for r in out if r["match_quality"]!=OK]
aff = sorted({i for r in bad for i in r["airports_affected"].split(", ") if i})
print(f"\nairport rows that CANNOT be enriched by domain alone: {len(aff)}")
print(" ", ", ".join(aff))
print("\nrows where Clay headcount should not be trusted:",
      sum(1 for r in out if r["headcount_trustworthy"]=="No"), "of", len(out))
