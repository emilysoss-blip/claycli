# -*- coding: utf-8 -*-
"""
Seed the Eightfold demand-gen POC cohort: one row per PARENT account, plus one row per HIRING
ENTITY (division, member hospital, regional arm) in a separate identity map.

Why two grains. Eightfold sells to large enterprises where one corporate domain covers many
hiring entities, and the talent leader and the requisition volume often sit at the division.
Collapsing UnitedHealth Group, UnitedHealthcare and Optum into one row loses the Optum VP of
Talent Acquisition; collapsing them by domain is worse, because they do not share one.

This is a STAND-IN for the Salesforce export the build guide asks for (section 3). The
CRM columns (salesforce_account_id, is_customer, is_open_opportunity, do_not_contact, owner_id,
current_tier, lifecycle_stage) are deliberately left blank or 'unknown': nothing in this repo
knows which of these companies Eightfold already sells to, and guessing would poison the
white-space logic. Replace the cohort with the real export and keep the identity map.

Every employee count, LinkedIn URL and match flag below was returned by Clay on 2026-10-15
(raw captures in data/raw/). Verticals follow the eight-account sample in the guide's appendix:
healthcare, insurance and financial services, semiconductors and advanced manufacturing.
"""
import csv, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBSERVED = "2026-10-15"
LI = "https://www.linkedin.com/company/"

# ------------------------------------------------------------------------------- parents
# (account_key, name, vertical, primary_domain, linkedin_slug, clay_employees, structural_note)
PARENTS = [
# ---- Healthcare (9)
("unitedhealth-group","UnitedHealth Group","Healthcare","unitedhealthgroup.com","unitedhealth-group",92856,
 "Two operating businesses on their own domains (UnitedHealthcare, Optum). Talent leaders found at both division and corporate level."),
("cvs-health","CVS Health","Healthcare","cvshealth.com","cvshealth",142370,
 "Aetna has its own domain; CVS Pharmacy and Caremark share cvshealth.com and do not resolve as separate entities."),
("elevance-health","Elevance Health","Healthcare","elevancehealth.com","elevance-health",44188,
 "Renamed from Anthem, Inc.; the defunct Anthem, Inc. page still sits on elevancehealth.com. Carelon has its own CHRO."),
("cigna-group","The Cigna Group","Healthcare","thecignagroup.com","the-cigna-group",50136,
 "Three domains: parent, Cigna Healthcare, Evernorth."),
("hca-healthcare","HCA Healthcare","Healthcare","hcahealthcare.com","hca",155698,
 "Physician Services division shares the parent domain."),
("johns-hopkins","Johns Hopkins (University + Medicine)","Healthcare","hopkinsmedicine.org","johns-hopkins-medicine",39514,
 "Two institutions, two domains, 34+ Clay entities between them. University and health system hire separately."),
("commonspirit-health","CommonSpirit Health","Healthcare","commonspirit.org","commonspirithealth",48637,
 "Parent does NOT resolve on commonspirit.org (10+ member hospitals do). Pinned LinkedIn resolves to domain commonspirit.careers."),
("kaiser-permanente","Kaiser Permanente","Healthcare","kaiserpermanente.org","kaiser-permanente",139271,
 "kaiserpermanente.org returns two placeholder pages tagged 'Blockchain Services'. Pinned LinkedIn resolves to kp.org."),
("mayo-clinic","Mayo Clinic","Healthcare","mayoclinic.org","mayo-clinic",49199,
 "Clean single entity."),
# ---- Insurance and financial services (9)
("state-farm","State Farm","Insurance & Financial Services","statefarm.com","state_farm",111988,
 "'State Farm Agent' page (11,996) sits on the carrier domain; agents are independent contractors, not State Farm employees."),
("lockton","Lockton","Insurance & Financial Services","lockton.com","lockton-companies",15209,
 "Clean single entity. Has a Head of Talent Intelligence (appendix sample)."),
("marsh","Marsh (formerly Marsh McLennan)","Insurance & Financial Services","marsh.com","marshglobal",65841,
 "Parent renamed Marsh (NYSE: MRSH). marshmclennan.com resolves to the wrong company; the Mercer LinkedIn page now reads 'Marsh People Solutions' (96)."),
("progressive","Progressive","Insurance & Financial Services","progressive.com","progressive-insurance",37894,
 "Clean single entity."),
("travelers","Travelers","Insurance & Financial Services","travelers.com","travelers",37678,
 "Clean single entity."),
("nationwide","Nationwide","Insurance & Financial Services","nationwide.com","nationwide",31628,
 "Clean single entity."),
("jpmorganchase","JPMorganChase","Insurance & Financial Services","jpmorganchase.com","jpmorganchase",238400,
 "Chase is the consumer brand of the same employer, on chase.com."),
("bank-of-america","Bank of America","Insurance & Financial Services","bankofamerica.com","bank-of-america",227047,
 "Private Bank shares the parent domain."),
("truist","Truist","Insurance & Financial Services","truist.com","truistfinancialcorporation",29574,
 "Inactive SunTrust page (11,541) still sits on truist.com."),
# ---- Semiconductors and advanced manufacturing (12)
("kla","KLA","Semiconductors & Advanced Manufacturing","kla.com","klacorp",17265,
 "Clean match, but annual_revenue band reads '1M-5M'. Domain did not resolve in people search; LinkedIn did."),
("lam-research","Lam Research","Semiconductors & Advanced Manufacturing","lamresearch.com","lam-research",18409,
 "Clean single entity."),
("applied-materials","Applied Materials","Semiconductors & Advanced Manufacturing","appliedmaterials.com","applied-materials",33320,
 "Clean single entity."),
("micron","Micron Technology","Semiconductors & Advanced Manufacturing","micron.com","micron-technology",44321,
 "Clean single entity."),
("texas-instruments","Texas Instruments","Semiconductors & Advanced Manufacturing","ti.com","texas-instruments",31289,
 "TI India (814) is a separate entity on the same domain."),
("analog-devices","Analog Devices","Semiconductors & Advanced Manufacturing","analog.com","analog-devices",27904,
 "Clean single entity."),
("flex","Flex","Semiconductors & Advanced Manufacturing","flex.com","flexintl",56696,
 "Clean single entity."),
("jabil","Jabil","Semiconductors & Advanced Manufacturing","jabil.com","jabil",64662,
 "Clean single entity."),
("honeywell","Honeywell Technologies","Semiconductors & Advanced Manufacturing","honeywell.com","honeywell",129754,
 "Post-separation automation company: page says 50,000+ employees, employee_count says 129,754. New CHRO (Jul 2026) and Chief Talent Officer (Apr 2026)."),
("ge-aerospace","GE Aerospace","Semiconductors & Advanced Manufacturing","geaerospace.com","geaerospace",115922,
 "One of three GE successors. Legacy ge.com still returns a 95,424-employee 'GE' page; do not enrich on ge.com."),
("ge-vernova","GE Vernova","Semiconductors & Advanced Manufacturing","gevernova.com","gevernova",70995,
 "Four inactive legacy pages (GE Power, GE Renewable Energy, GE Grid Solutions, Alstom Power) still resolve on gevernova.com."),
("ge-healthcare","GE HealthCare","Semiconductors & Advanced Manufacturing","gehealthcare.com","gehealthcare",60146,
 "Medtech, classified by Clay as Hospitals and Health Care. Vertical assignment needs Eightfold's call."),
]

# ---------------------------------------------------------------------- hiring entities
# role: parent | operating division | member hospital | regional entity | shared research org |
#       legacy-inactive | non-employee network | wrong-company match | stale stub
# include: yes = a real hiring entity to prospect; no = must be suppressed so it never takes a contact
# (account_key, entity_name, domain, linkedin_slug, clay_employees, size_band, role, include, note)
ENTITIES = [
("unitedhealth-group","UnitedHealth Group","unitedhealthgroup.com","unitedhealth-group",92856,"10,001+","parent","yes",""),
("unitedhealth-group","UnitedHealthcare","uhc.com","unitedhealthcare",16974,"10,001+","operating division","yes","Own domain. Division CPO sits under UHG in people data (UHC Operations)."),
("unitedhealth-group","Optum","optum.com","optum",114911,"10,001+","operating division","yes","Larger than the parent page by Clay headcount. Own VP Talent Acquisition."),
("unitedhealth-group","Landmark Health","optum.com","landmark-health",790,"1,001-5,000","legacy-inactive","no","'Now part of Optum Home & Community'. Page no longer active."),
("unitedhealth-group","naviHealth","optum.com","navihealth-inc-",984,"1,001-5,000","legacy-inactive","no","'Now part of Optum Home & Community'. Page no longer active."),
("unitedhealth-group","Optum Philippines","optum.com","optum-philippines",667,"1,001-5,000","regional entity","no","Non-US capability center; outside POC geography."),
("unitedhealth-group","Optum Workers' Comp and Auto No-Fault","optum.com","workcompauto.optum",618,"1,001-5,000","operating division","yes","Shares optum.com."),
("cvs-health","CVS Health","cvshealth.com","cvshealth",142370,"10,001+","parent","yes","VP Head of TA started Mar 2026."),
("cvs-health","Aetna, a CVS Health Company","aetna.com","aetna",41157,"10,001+","operating division","yes","Industry misclassified as 'Wellness and Fitness Services'."),
("elevance-health","Elevance Health","elevancehealth.com","elevance-health",44188,"10,001+","parent","yes","EVP CHRO started Aug 2025."),
("elevance-health","Anthem, Inc.","elevancehealth.com","antheminc",19436,"1","stale stub","no","'Anthem, Inc. is now Elevance Health'. Size band '1' against 19,436 employees."),
("elevance-health","Anthem Blue Cross and Blue Shield","anthem.com","anthembcbs",10447,"10,001+","operating division","yes",""),
("elevance-health","Carelon","carelon.com","carelon",3197,"10,001+","operating division","yes","Has its own CHRO (started Dec 2025)."),
("elevance-health","AIM Specialty Health","carelon.com","aim-specialty-health",537,"1,001-5,000","legacy-inactive","no","'AIM is now Carelon Medical Benefits Management'."),
("cigna-group","The Cigna Group","thecignagroup.com","the-cigna-group",50136,"10,001+","parent","yes",""),
("cigna-group","Cigna Healthcare","cigna.com","cignahealthcare",29395,"10,001+","operating division","yes","annual_revenue band '75M-200M' is wrong for this entity."),
("cigna-group","Evernorth Health Services","evernorth.com","evernorth",7647,"10,001+","operating division","yes","Recent TA leads returned are all in Hyderabad."),
("hca-healthcare","HCA Healthcare","hcahealthcare.com","hca",155698,"10,001+","parent","yes","Director of TA Technology started Feb 2026 (HR-tech persona)."),
("hca-healthcare","HCA Healthcare Physician Services","hcahealthcare.com","hca-physician-services",2733,"10,001+","operating division","yes","Shares parent domain."),
("johns-hopkins","Johns Hopkins Medicine","hopkinsmedicine.org","johns-hopkins-medicine",39514,"10,001+","parent","yes","Governing structure for the health system + School of Medicine."),
("johns-hopkins","The Johns Hopkins University","jhu.edu","johns-hopkins-university",18367,"10,001+","parent","yes","Separate employer from the health system. VP and CHRO started Jun 2025."),
("johns-hopkins","Johns Hopkins Hospital","hopkinsmedicine.org","johns-hopkins-hospital",14399,"10,001+","member hospital","yes",""),
("johns-hopkins","Johns Hopkins Health Plans","hopkinsmedicine.org","johns-hopkins-health-plans",1352,"1,001-5,000","operating division","yes",""),
("johns-hopkins","John Hopkins University (misspelled stub)","jhu.edu","john-hopkins-university",677,"2-10","stale stub","no","Misspelled name; size band '2-10' against 677 employees."),
("commonspirit-health","CommonSpirit Health","commonspirit.careers","commonspirithealth",48637,"10,001+","parent","yes","Only reachable by LinkedIn URL. Domain-keyed enrichment never finds it."),
("commonspirit-health","Dignity Health California","commonspirit.org","dignity-health-california",293,"10,001+","member hospital","yes","29 hospitals; Clay employee_count 293."),
("commonspirit-health","CommonSpirit Health Mountain Region","commonspirit.org","commonspirit-health-mountain-region",1090,"10,001+","member hospital","yes","Regional system, 20 hospitals."),
("commonspirit-health","St. Luke's Health","commonspirit.org","st-luke's-health",2790,"5,001-10,000","member hospital","yes",""),
("commonspirit-health","CHI Memorial","commonspirit.org","chi-memorial",1012,"1,001-5,000","member hospital","yes",""),
("kaiser-permanente","Kaiser Permanente","kp.org","kaiser-permanente",139271,"10,001+","parent","yes","Only reachable by LinkedIn URL."),
("kaiser-permanente","Kaiser Permanente-US","kaiserpermanente.org","kaiser-permanente-us",None,"10,001+","stale stub","no","Placeholder page: type Partnership, industry 'Blockchain Services', no headcount."),
("kaiser-permanente","Kaiser Permanente-LA","kaiserpermanente.org","kaiser-permanente-la",None,"10,001+","stale stub","no","Placeholder page: type Partnership, industry 'Blockchain Services', no headcount."),
("mayo-clinic","Mayo Clinic","mayoclinic.org","mayo-clinic",49199,"10,001+","parent","yes",""),
("state-farm","State Farm","statefarm.com","state_farm",111988,"10,001+","parent","yes",""),
("state-farm","State Farm Agent","statefarm.com","state-farm-agent",11996,"5,001-10,000","non-employee network","no","Independent agents. A contact here is not a State Farm employee and must never be routed as one."),
("lockton","Lockton","lockton.com","lockton-companies",15209,"10,001+","parent","yes",""),
("marsh","Marsh","marsh.com","marshglobal",65841,"10,001+","parent","yes","Current parent page."),
("marsh","Marsh McLennan (closed page)","marsh.com","marshmclennan",17314,"10,001+","legacy-inactive","no","'This LinkedIn page is closed.' Still carries 17,314 employees."),
("marsh","Mercer (now 'Marsh People Solutions')","mercer.com","mercer",96,"","operating division","yes","Pinned LinkedIn resolves to 'Marsh People Solutions', 96 employees. Mercer's own regional pages sit on mercer.com and marsh.com."),
("marsh","Celedinas Insurance Group","marshmclennan.com","celedinas-insurance-group",31,"10,001+","wrong-company match","no","What marshmclennan.com resolves to. Silent wrong match."),
("progressive","Progressive Insurance","progressive.com","progressive-insurance",37894,"10,001+","parent","yes",""),
("travelers","Travelers","travelers.com","travelers",37678,"10,001+","parent","yes",""),
("nationwide","Nationwide","nationwide.com","nationwide",31628,"10,001+","parent","yes",""),
("jpmorganchase","JPMorganChase","jpmorganchase.com","jpmorganchase",238400,"10,001+","parent","yes",""),
("jpmorganchase","Chase","chase.com","chase",35456,"10,001+","operating division","yes","Consumer brand of the same employer."),
("bank-of-america","Bank of America","bankofamerica.com","bank-of-america",227047,"10,001+","parent","yes",""),
("bank-of-america","Bank of America Private Bank","bankofamerica.com","bank-of-america-private-bank",3731,"1,001-5,000","operating division","yes","Shares parent domain."),
("truist","Truist","truist.com","truistfinancialcorporation",29574,"10,001+","parent","yes",""),
("truist","SunTrust","truist.com","suntrustnowtruist",11541,"10,001+","legacy-inactive","no","'No longer active' since the BB&T/SunTrust merger."),
("kla","KLA","kla.com","klacorp",17265,"10,001+","parent","yes",""),
("lam-research","Lam Research","lamresearch.com","lam-research",18409,"10,001+","parent","yes",""),
("applied-materials","Applied Materials","appliedmaterials.com","applied-materials",33320,"10,001+","parent","yes",""),
("micron","Micron Technology","micron.com","micron-technology",44321,"10,001+","parent","yes",""),
("texas-instruments","Texas Instruments","ti.com","texas-instruments",31289,"10,001+","parent","yes",""),
("texas-instruments","Texas Instruments India","ti.com","texas-instruments-india",814,"1,001-5,000","regional entity","no","Outside POC geography."),
("analog-devices","Analog Devices","analog.com","analog-devices",27904,"10,001+","parent","yes",""),
("flex","Flex","flex.com","flexintl",56696,"10,001+","parent","yes",""),
("jabil","Jabil","jabil.com","jabil",64662,"10,001+","parent","yes",""),
("honeywell","Honeywell Technologies","honeywell.com","honeywell",129754,"10,001+","parent","yes","Headcount conflict: page text 50,000+, employee_count 129,754."),
("ge-aerospace","GE Aerospace","geaerospace.com","geaerospace",115922,"10,001+","parent","yes",""),
("ge-aerospace","GE Research","geaerospace.com","geresearch",884,"1,001-5,000","shared research org","yes","Serves GE Aerospace and GE Vernova; sits on the Aerospace domain."),
("ge-aerospace","GE (legacy parent page)","ge.com","ge",95424,"10,001+","legacy-inactive","no","Content moved to GE Aerospace and GE Vernova. Still carries 95,424 employees."),
("ge-vernova","GE Vernova","gevernova.com","gevernova",70995,"10,001+","parent","yes",""),
("ge-vernova","GE Digital","ge.com","ge-digital",1762,"1,001-5,000","operating division","yes","Energy software (GE Vernova) still on legacy ge.com."),
("ge-vernova","GE Power","gevernova.com","gepower",16996,"10,001+","legacy-inactive","no","Folded into GE Vernova Apr 2024."),
("ge-vernova","GE Renewable Energy","gevernova.com","gerenewableenergy",4759,"10,001+","legacy-inactive","no","Folded into GE Vernova Apr 2024."),
("ge-vernova","GE Grid Solutions","gevernova.com","gegridsolutions",4736,"10,001+","legacy-inactive","no","Folded into GE Vernova Apr 2024."),
("ge-vernova","Alstom Power","gevernova.com","alstom-power",6507,"10,001+","legacy-inactive","no","No longer active."),
("ge-healthcare","GE HealthCare","gehealthcare.com","gehealthcare",60146,"10,001+","parent","yes",""),
]

# Domain match status per parent, from data/raw/*.json. See seed_clay_match.py for the per-domain table.
#   clean                     primary domain returns the parent and nothing misleading
#   clean_with_stale_pages    returns the parent, plus defunct or non-employee pages on the same domain
#   shared_domain             one domain, many real hiring entities; domain alone cannot pick one
#   parent_missing_by_domain  domain returns members or junk but never the parent; pin LinkedIn
MATCH_STATUS = {
 "unitedhealth-group":"clean","cvs-health":"clean","elevance-health":"clean_with_stale_pages",
 "cigna-group":"clean","hca-healthcare":"shared_domain","johns-hopkins":"shared_domain",
 "commonspirit-health":"parent_missing_by_domain","kaiser-permanente":"parent_missing_by_domain",
 "mayo-clinic":"clean","state-farm":"clean_with_stale_pages","lockton":"clean",
 "marsh":"shared_domain","progressive":"clean","travelers":"clean","nationwide":"clean",
 "jpmorganchase":"clean","bank-of-america":"shared_domain","truist":"clean_with_stale_pages",
 "kla":"clean","lam-research":"clean","applied-materials":"clean","micron":"clean",
 "texas-instruments":"shared_domain","analog-devices":"clean","flex":"clean","jabil":"clean",
 "honeywell":"clean","ge-aerospace":"shared_domain","ge-vernova":"clean_with_stale_pages",
 "ge-healthcare":"clean",
}

def li(slug):
    return LI + slug if slug else ""

def main():
    ent_by_acct = {}
    for e in ENTITIES:
        ent_by_acct.setdefault(e[0], []).append(e)

    accounts = []
    for i, (key, name, vert, dom, slug, emp, note) in enumerate(PARENTS, 1):
        ents = ent_by_acct.get(key, [])
        status = MATCH_STATUS[key]
        accounts.append({
            "source_row_id": f"seed-{i:03d}",
            "account_key": key,
            "account_name": name,
            "vertical": vert,
            "country": "United States",
            "account_domain": dom,
            "account_linkedin_url": li(slug),
            # Enrich on the LinkedIn URL wherever the domain cannot be trusted to return the parent.
            "enrichment_identifier": li(slug) if status in ("parent_missing_by_domain", "shared_domain") else dom,
            "clay_employee_count": emp,
            "hiring_entities_in_scope": sum(1 for e in ents if e[7] == "yes"),
            "entities_suppressed": sum(1 for e in ents if e[7] == "no"),
            "domain_match_status": status,
            "identity_note": note,
            # CRM fields: blank until the Salesforce export lands. Never inferred.
            "salesforce_account_id": "",
            "owner_id": "",
            "is_customer": "unknown",
            "is_open_opportunity": "unknown",
            "do_not_contact": "unknown",
            "current_tier": "",
            "lifecycle_stage": "",
            "field_source": "Clay search-companies (seed cohort, not Salesforce)",
            "observed_at": OBSERVED,
        })

    divisions = []
    for (key, ename, dom, slug, emp, band, role, inc, note) in ENTITIES:
        parent_dom = next(p[3] for p in PARENTS if p[0] == key)
        divisions.append({
            "account_key": key,
            "entity_name": ename,
            "entity_domain": dom,
            "shares_parent_domain": "yes" if dom == parent_dom else "no",
            "entity_linkedin_url": li(slug),
            "clay_employee_count": "" if emp is None else emp,
            "clay_size_band": band,
            "role": role,
            "include_in_cohort": inc,
            "note": note,
            "observed_at": OBSERVED,
        })

    out = os.path.join(BASE, "data")
    for fname, rows in (("accounts", accounts), ("divisions", divisions)):
        with open(os.path.join(out, fname + ".csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        json.dump(rows, open(os.path.join(out, fname + ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"accounts: {len(accounts)} | entities: {len(divisions)} "
          f"({sum(d['include_in_cohort']=='yes' for d in divisions)} in scope, "
          f"{sum(d['include_in_cohort']=='no' for d in divisions)} suppressed)")

if __name__ == "__main__":
    main()
