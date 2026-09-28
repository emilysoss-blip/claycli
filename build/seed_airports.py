# -*- coding: utf-8 -*-
"""
Seed the airport intelligence table: one row per airport, airport domain = primary key.

Columns that carry a value here are STRUCTURAL facts (ownership/operator model, geography,
association membership, relevant trade press). Columns intentionally left EMPTY are the ones
Clay should own: marketplace enrichment (headcount, tech stack, LinkedIn, people) and
Claygent research (newsroom URL, procurement URL, live initiatives). See docs/README.md.

Passenger volumes are 2024 seed estimates in millions, rounded, for tiering only. They are
NOT authoritative and are re-verified by the Claygent column `pax_verified_*`.
"""
import csv, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- reference: associations
ASSOC = {
    "us":     "ACI-NA; AAAE; ACI World",
    "us_fl":  "ACI-NA; AAAE; ACI World; Florida Airports Council",
    "us_tx":  "ACI-NA; AAAE; ACI World; Texas Airports Council (TxDOT Aviation)",
    "us_ca":  "ACI-NA; AAAE; ACI World; California Airports Council",
    "ca":     "Canadian Airports Council; ACI-NA; ACI World",
    "eu":     "ACI EUROPE; ACI World",
    "uk":     "ACI EUROPE; ACI World; Airport Operators Association (AOA UK)",
    "de":     "ACI EUROPE; ACI World; ADV (Arbeitsgemeinschaft Deutscher Verkehrsflughaefen)",
    "fr":     "ACI EUROPE; ACI World; Union des Aeroports Francais (UAF)",
    "me":     "ACI Asia-Pacific & Middle East; ACI World",
    "apac":   "ACI Asia-Pacific & Middle East; ACI World",
    "latam":  "ACI Latin America-Caribbean (ACI-LAC); ACI World",
}

# ---------------------------------------------------------------- reference: publications
# 6-8 titles per region. These are the sources the Claygent agent is pointed at.
PUBS = {
    "na": ("Airport Improvement Magazine; Airport Experience News; Passenger Terminal Today; "
           "International Airport Review; Airport Technology; AviationPros; ACI-NA Centerlines; Aviation Week Network"),
    "eu": ("International Airport Review; Passenger Terminal Today; Airport Technology; "
           "Airport Industry Review; Airport Business (EMEA); Aviation Week Network; ACI EUROPE Media; Air Cargo News"),
    "me": ("Aviation Business Middle East; Arabian Aerospace; International Airport Review; "
           "Passenger Terminal Today; Airport Technology; Airport Industry Review; Aviation Week Network; Air Cargo News"),
    "apac": ("Asian Aviation; International Airport Review; Passenger Terminal Today; Airport Technology; "
             "Airport Industry Review; Aviation Week Network; Air Cargo News; ACI Asia-Pacific Media"),
    "latam": ("Aviacionline; A21 (MX); AEROIN (BR); International Airport Review; Passenger Terminal Today; "
              "Airport Technology; Aviation Week Network; ACI-LAC Media"),
}

# ---------------------------------------------------------------- the 50 accounts
# (domain, name, iata, icao, city, country, region, pax_m, operator_model,
#  authority_name, authority_domain, parent_name, parent_domain, terminal_operators, systems_owner_note,
#  assoc_key, pubs_key, procurement_system)
ROWS = [
# ---- United States (28) -------------------------------------------------------------------
("atl.com","Hartsfield-Jackson Atlanta International Airport","ATL","KATL","Atlanta, GA","United States","North America",108,
 "Municipal department","City of Atlanta Department of Aviation","atl.com","City of Atlanta","atlantaga.gov","",
 "Single-operator airport: authority runs all terminals; airline-leased gates only. IT/systems owned by Dept of Aviation Technology division under City of Atlanta CIO shared services.",
 "us","na","City of Atlanta procurement portal"),
("dfwairport.com","Dallas Fort Worth International Airport","DFW","KDFW","Dallas-Fort Worth, TX","United States","North America",88,
 "Independent joint-owner board","DFW International Airport Board","dfwairport.com","Cities of Dallas & Fort Worth (joint owners)","","",
 "Self-operated terminals A-E. Strong standalone IT organization with its own CIO and CISO; not dependent on city shared services.",
 "us_tx","na","DFW Business Diversity / Bonfire"),
("flydenver.com","Denver International Airport","DEN","KDEN","Denver, CO","United States","North America",82,
 "Municipal department","City and County of Denver Department of Aviation (Denver International Airport)","flydenver.com","City and County of Denver","denvergov.org","",
 "Authority-operated concourses A/B/C. Great Hall program is a named capital program with its own delivery org.",
 "us","na","Denver BidNet / City procurement"),
("flychicago.com","Chicago O'Hare International Airport","ORD","KORD","Chicago, IL","United States","North America",80,
 "Municipal department","Chicago Department of Aviation","flychicago.com","City of Chicago","chicago.gov","",
 "CDA operates ORD and MDW on one domain (flychicago.com) - domain maps to TWO airports, so IATA code is required to disambiguate rows.",
 "us","na","City of Chicago eProcurement"),
("flylax.com","Los Angeles International Airport","LAX","KLAX","Los Angeles, CA","United States","North America",77,
 "Municipal airport authority","Los Angeles World Airports (LAWA)","lawa.org","City of Los Angeles","lacity.gov","",
 "LAWA is the airport-wide authority and also operates ONT-adjacent assets historically; LAX terminals largely airline-leased (Delta T2/3, AA T4/5, United T7/8) with airline-led renovations.",
 "us_ca","na","LAWA Procurement Services / RAMP"),
("harryreidairport.com","Harry Reid International Airport","LAS","KLAS","Las Vegas, NV","United States","North America",58,
 "County department","Clark County Department of Aviation","harryreidairport.com","Clark County, Nevada","clarkcountynv.gov","",
 "County-run; IT under Department of Aviation but procurement flows through Clark County. Buyer often sits at county level.",
 "us","na","Clark County procurement"),
("cltairport.com","Charlotte Douglas International Airport","CLT","KCLT","Charlotte, NC","United States","North America",59,
 "Municipal department","City of Charlotte Aviation Department","cltairport.com","City of Charlotte","charlottenc.gov","",
 "Single-operator hub dominated by American Airlines. Destination CLT capital program.",
 "us","na","City of Charlotte procurement"),
("orlandoairports.net","Orlando International Airport","MCO","KMCO","Orlando, FL","United States","North America",57,
 "Independent public authority","Greater Orlando Aviation Authority (GOAA)","orlandoairports.net","","",
 "",
 "GOAA operates MCO and ORL. Terminal C is authority-built and authority-operated; strong in-house IT and a named biometric/passenger-processing program.",
 "us_fl","na","GOAA procurement / Bonfire"),
("miami-airport.com","Miami International Airport","MIA","KMIA","Miami, FL","United States","North America",56,
 "County department","Miami-Dade Aviation Department (MDAD)","miami-airport.com","Miami-Dade County","miamidade.gov","",
 "MDAD runs MIA plus four GA airports. Procurement and IT governance run through Miami-Dade County ITD as well as MDAD - dual-path buyer.",
 "us_fl","na","Miami-Dade County procurement"),
("portseattle.org","Seattle-Tacoma International Airport","SEA","KSEA","Seattle, WA","United States","North America",53,
 "Port authority","Port of Seattle Aviation Division","portseattle.org","Port of Seattle","portseattle.org","",
 "PORT is the parent: domain portseattle.org covers seaport + airport, so airport-specific people must be filtered by division. Airport also markets as seatacairport.com.",
 "us","na","Port of Seattle procurement"),
("skyharbor.com","Phoenix Sky Harbor International Airport","PHX","KPHX","Phoenix, AZ","United States","North America",52,
 "Municipal department","City of Phoenix Aviation Department","skyharbor.com","City of Phoenix","phoenix.gov","",
 "City department operating PHX, DVT, GEU. Terminal 3/4 modernization programs.",
 "us","na","City of Phoenix eProcurement"),
("jfkairport.com","John F. Kennedy International Airport","JFK","KJFK","New York, NY","United States","North America",63,
 "Landlord authority + private terminal operators","Port Authority of New York and New Jersey (Aviation Dept)","panynj.gov","Port Authority of New York and New Jersey","panynj.gov",
 "JFKIAT (Terminal 4) | jfkiat.com; New Terminal One consortium (Terminal 1) | anewterminalone.com; JFK Millennium Partners (Terminal 6) | jfkmillenniumpartners.com; American Airlines (Terminal 8) | aa.com; Delta Air Lines (Terminals 2/4 ops) | delta.com",
 "HIGHEST separation value on the list. PANYNJ owns airport-wide infrastructure, security and the $19B redevelopment; each terminal operator buys its OWN passenger systems, baggage and terminal IT. Three distinct buyer paths.",
 "us","na","PANYNJ procurement (Ariba)"),
("laguardiaairport.com","LaGuardia Airport","LGA","KLGA","New York, NY","United States","North America",33,
 "Landlord authority + private terminal operators","Port Authority of New York and New Jersey (Aviation Dept)","panynj.gov","Port Authority of New York and New Jersey","panynj.gov",
 "LaGuardia Gateway Partners (Terminal B) | laguardiab.com; Delta Air Lines (Terminal C) | delta.com",
 "Terminal B is a full private concession (LGP) with its own CEO, CIO-equivalent and procurement. Terminal C is Delta-run. Authority retains AirTrain/roadway/central systems.",
 "us","na","PANYNJ procurement (Ariba)"),
("newarkairport.com","Newark Liberty International Airport","EWR","KEWR","Newark, NJ","United States","North America",49,
 "Landlord authority","Port Authority of New York and New Jersey (Aviation Dept)","panynj.gov","Port Authority of New York and New Jersey","panynj.gov",
 "Munich Airport NJ LLC (Terminal A operations & commercial) | munich-airport.com; United Airlines (Terminals B/C anchor tenant) | united.com",
 "Terminal A is PANYNJ-delivered but OPERATED under contract by Munich Airport NJ LLC (a Flughafen Muenchen subsidiary) - so the Terminal A buyer is a German airport operator, not the Port Authority. Same parent authority as JFK and LGA: dedupe people outreach at the PANYNJ level.",
 "us","na","PANYNJ procurement (Ariba)"),
("flysfo.com","San Francisco International Airport","SFO","KSFO","San Francisco, CA","United States","North America",47,
 "Municipal airport commission","San Francisco International Airport (SFO), City and County of San Francisco","flysfo.com","City and County of San Francisco","sf.gov","",
 "Airport Commission governance. Mature in-house IT and a well-documented biometric/digital identity program; publishes its own tech roadmap.",
 "us_ca","na","SFO / SF City procurement"),
("fly2houston.com","George Bush Intercontinental Airport","IAH","KIAH","Houston, TX","United States","North America",46,
 "Municipal airport system","Houston Airport System (HAS)","fly2houston.com","City of Houston","houstontx.gov","",
 "HAS runs IAH, HOU and EFD on ONE domain - domain is not unique per airport, so IATA disambiguation is required. IAH Terminal B/D redevelopment program.",
 "us_tx","na","City of Houston / HAS procurement"),
("bostonlogan.com","Boston Logan International Airport","BOS","KBOS","Boston, MA","United States","North America",44,
 "Independent port authority","Massachusetts Port Authority (Massport) Aviation","massport.com","Massachusetts Port Authority","massport.com","",
 "Massport is the parent (seaport + airport + Worcester/Hanscom). Primary corporate domain is massport.com; bostonlogan.com is the passenger-facing brand - both must be kept on the row.",
 "us","na","Massport procurement / COMMBUYS"),
("mspairport.com","Minneapolis-Saint Paul International Airport","MSP","KMSP","Minneapolis, MN","United States","North America",35,
 "Independent public commission","Metropolitan Airports Commission (MAC)","metroairports.org","","",
 "",
 "MAC is a public corporation running MSP + six reliever airports. Corporate domain metroairports.org differs from passenger domain mspairport.com - people search must use the corporate domain.",
 "us","na","MAC procurement"),
("phl.org","Philadelphia International Airport","PHL","KPHL","Philadelphia, PA","United States","North America",31,
 "Municipal division","City of Philadelphia Division of Aviation","phl.org","City of Philadelphia","phila.gov","",
 "City division running PHL and PNE. Capital program with terminal and baggage modernization scope.",
 "us","na","City of Philadelphia eContract Philly"),
("metroairport.com","Detroit Metropolitan Wayne County Airport","DTW","KDTW","Detroit, MI","United States","North America",32,
 "Independent county authority","Wayne County Airport Authority (WCAA)","metroairport.com","","",
 "Delta Air Lines (McNamara Terminal anchor) | delta.com",
 "WCAA is legally independent of Wayne County government despite the name - do not route to county IT. Runs DTW and YIP.",
 "us","na","WCAA procurement"),
("flydulles.com","Washington Dulles International Airport","IAD","KIAD","Washington, DC","United States","North America",27,
 "Independent regional authority","Metropolitan Washington Airports Authority (MWAA)","mwaa.com","Metropolitan Washington Airports Authority","mwaa.com","",
 "MWAA is the parent for BOTH IAD and DCA and also operates the Dulles Toll Road / Silver Line delivery. Corporate domain mwaa.com - dedupe people against the DCA row.",
 "us","na","MWAA procurement"),
("flyreagan.com","Ronald Reagan Washington National Airport","DCA","KDCA","Washington, DC","United States","North America",25,
 "Independent regional authority","Metropolitan Washington Airports Authority (MWAA)","mwaa.com","Metropolitan Washington Airports Authority","mwaa.com","",
 "Same parent authority as IAD. Shared CIO/CISO and shared procurement - treat IAD + DCA as ONE buying center with two physical assets.",
 "us","na","MWAA procurement"),
("slcairport.com","Salt Lake City International Airport","SLC","KSLC","Salt Lake City, UT","United States","North America",28,
 "Municipal department","Salt Lake City Department of Airports","slcairport.com","Salt Lake City Corporation","slc.gov","",
 "Completed a full greenfield terminal rebuild (New SLC) - now in systems-optimization rather than build phase, which changes the offer.",
 "us","na","Salt Lake City procurement"),
("san.org","San Diego International Airport","SAN","KSAN","San Diego, CA","United States","North America",25,
 "Independent regional authority","San Diego County Regional Airport Authority","san.org","","",
 "",
 "Independent authority, not a city department. New Terminal 1 program is a large active capital delivery with its own program-management org.",
 "us_ca","na","San Diego Airport Authority / Bonfire"),
("tampaairport.com","Tampa International Airport","TPA","KTPA","Tampa, FL","United States","North America",26,
 "Independent county authority","Hillsborough County Aviation Authority (HCAA)","tampaairport.com","","",
 "",
 "HCAA runs TPA plus three GA airports. Independent of county government. Airside D and SkyCenter expansion programs.",
 "us_fl","na","HCAA procurement / Bonfire"),
("flynashville.com","Nashville International Airport","BNA","KBNA","Nashville, TN","United States","North America",23,
 "Independent metropolitan authority","Metropolitan Nashville Airport Authority (MNAA)","flynashville.com","","",
 "",
 "MNAA runs BNA and JWN. BNA Vision / New Horizon capital programs; among the fastest-growing US mid-size hubs.",
 "us","na","MNAA procurement"),
("austintexas.gov","Austin-Bergstrom International Airport","AUS","KAUS","Austin, TX","United States","North America",22,
 "Municipal department","City of Austin Department of Aviation","austintexas.gov","City of Austin","austintexas.gov","",
 "WARNING: no dedicated corporate domain - shares austintexas.gov with all of city government, so domain-based people enrichment WILL return non-airport staff. Must filter by department. Journey With AUS expansion program.",
 "us_tx","na","City of Austin procurement"),
("bwiairport.com","Baltimore/Washington International Thurgood Marshall Airport","BWI","KBWI","Baltimore, MD","United States","North America",27,
 "State aviation administration","Maryland Aviation Administration (MAA)","bwiairport.com","Maryland Department of Transportation","mdot.maryland.gov","",
 "State-DOT-owned model (distinct from city/county/authority peers). IT and procurement governance sit partly at MDOT level - buyer may be at the state.",
 "us","na","Maryland eMMA / MDOT procurement"),
# ---- Canada (3) ---------------------------------------------------------------------------
("torontopearson.com","Toronto Pearson International Airport","YYZ","CYYZ","Toronto, ON","Canada","North America",46,
 "Not-for-profit airport authority","Greater Toronto Airports Authority (GTAA)","gtaa.com","","",
 "",
 "GTAA is a private not-for-profit corporation leasing from Transport Canada. Corporate domain gtaa.com vs passenger domain torontopearson.com. Terminal 1/3 modernization + LINK program.",
 "ca","na","GTAA procurement / MERX"),
("yvr.ca","Vancouver International Airport","YVR","CYVR","Vancouver, BC","Canada","North America",26,
 "Not-for-profit airport authority","Vancouver Airport Authority","yvr.ca","","",
 "",
 "Community-based not-for-profit authority. Runs its own innovation/technology arm and has commercialized its own systems IP.",
 "ca","na","YVR procurement / MERX"),
("admtl.com","Montreal-Trudeau International Airport","YUL","CYUL","Montreal, QC","Canada","North America",22,
 "Not-for-profit airport authority","Aeroports de Montreal (ADM)","admtl.com","","",
 "",
 "ADM runs YUL and Mirabel cargo. French-language procurement and press; Claygent must search FR-language sources.",
 "ca","na","ADM procurement / SEAO Quebec"),
# ---- Latin America (3) --------------------------------------------------------------------
("aicm.com.mx","Mexico City International Airport","MEX","MMMX","Mexico City","Mexico","Latin America",45,
 "State-owned operator (military-administered)","Aeropuerto Internacional de la Ciudad de Mexico (AICM)","aicm.com.mx","Government of Mexico (SEDENA-administered)","gob.mx","",
 "Administered by SEDENA (defence ministry) since 2021 - procurement is federal/military, not commercial. Very different sales path from the rest of the list; treat as public-sector federal.",
 "latam","latam","CompraNet (federal MX)"),
("gru.com.br","Sao Paulo/Guarulhos International Airport","GRU","SBGR","Sao Paulo","Brazil","Latin America",43,
 "Private concession","GRU Airport - Concessionaria do Aeroporto Internacional de Sao Paulo","gru.com.br","Invepar / concession consortium","invepar.com.br","",
 "30-year private concession under ANAC regulation. Commercial procurement, Portuguese-language sources. Concession economics drive capex timing.",
 "latam","latam","Private concession RFP + ANAC filings"),
("eldorado.aero","El Dorado International Airport (Bogota)","BOG","SKBO","Bogota","Colombia","Latin America",44,
 "Private concession","Opain S.A.","eldorado.aero","Opain consortium / Aeronautica Civil (grantor)","aerocivil.gov.co","",
 "Opain holds the terminal concession; Aerocivil retains airside/ATC. Buyer split between concessionaire and civil aviation authority. Spanish-language sources.",
 "latam","latam","Opain private RFP + SECOP (CO public)"),
# ---- Europe / UK (10) ---------------------------------------------------------------------
("heathrow.com","London Heathrow Airport","LHR","EGLL","London","United Kingdom","Europe",84,
 "Private airport company","Heathrow Airport Limited","heathrow.com","Heathrow Airport Holdings (Ardian / PIF-led consortium)","heathrow.com","British Airways (Terminal 5 anchor) | britishairways.com",
 "Fully private, CAA-regulated (RAB model) - capex is set in regulatory settlements (H7), so procurement timing follows the regulatory cycle, not annual budgets. Third-runway/expansion decision is the dominant signal.",
 "uk","eu","Heathrow supplier portal / Jaggaer"),
("gatwickairport.com","London Gatwick Airport","LGW","EGKK","London","United Kingdom","Europe",43,
 "Private airport company","Gatwick Airport Limited","gatwickairport.com","VINCI Airports (majority) / Global Infrastructure Partners","vinci-airports.com","",
 "VINCI Airports is the parent group - VINCI runs 70+ airports and centralizes some technology standards, so a group-level buyer exists ABOVE the airport. Northern Runway project is the live capital signal.",
 "uk","eu","Gatwick supplier portal / VINCI group sourcing"),
("parisaeroport.fr","Paris-Charles de Gaulle Airport","CDG","LFPG","Paris","France","Europe",70,
 "Listed airport group (state-majority)","Aeroports de Paris (Groupe ADP)","adp.fr","Groupe ADP","adp.fr","",
 "Groupe ADP operates CDG + ORY + LBG and holds stakes in TAV Airports and GMR - group-level CIO/CISO plus airport-level teams. Corporate domain adp.fr differs from the passenger domain parisaeroport.fr (the row key). FR-language sources; EU TED tenders.",
 "fr","eu","Groupe ADP e-sourcing / EU TED"),
("schiphol.nl","Amsterdam Airport Schiphol","AMS","EHAM","Amsterdam","Netherlands","Europe",67,
 "State/municipal-owned airport group","Royal Schiphol Group","schiphol.nl","Royal Schiphol Group (Dutch State, Amsterdam, Rotterdam)","schiphol.nl","",
 "Schiphol Group also owns Rotterdam-The Hague and Eindhoven and holds a JFK T4 stake - the group is itself a terminal operator abroad. Publishes detailed multi-year capital and digital plans. EU TED tenders.",
 "eu","eu","Schiphol sourcing / EU TED"),
("frankfurt-airport.com","Frankfurt Airport","FRA","EDDF","Frankfurt","Germany","Europe",63,
 "Listed airport group (state-anchored)","Fraport AG","fraport.com","Fraport AG","fraport.com","Lufthansa (Terminal 1 anchor) | lufthansa.com",
 "Fraport is a global operator (Greece, Brazil, Peru, Antalya) with a group IT organization - a group-level buyer sits above FRA. Terminal 3 is a multi-billion active build. Corporate domain fraport.com.",
 "de","eu","Fraport supplier portal / EU TED"),
("aena.es","Adolfo Suarez Madrid-Barajas Airport","MAD","LEMD","Madrid","Spain","Europe",66,
 "Listed national network operator","Aena S.M.E., S.A.","aena.es","Aena (Spanish State majority via ENAIRE)","aena.es","",
 "CRITICAL: Aena operates 46 Spanish airports on ONE domain. There is no MAD-specific domain or MAD-specific CIO - the buyer is the Aena network organization. Row is really 'Aena network, MAD as flagship'. EU TED tenders.",
 "eu","eu","Aena Plataforma de Contratacion / EU TED"),
("istairport.com","Istanbul Airport","IST","LTFM","Istanbul","Turkey","Europe",80,
 "Private BOT concession","iGA Airport Operations (Istanbul Grand Airport)","istairport.com","iGA consortium (Limak / Kalyon / Cengiz)","","",
 "25-year build-operate-transfer concession - iGA is a purpose-built operating company with its own full C-suite including CIO/CTO. Greenfield digital estate; strong public technology posture.",
 "eu","eu","iGA private RFP"),
("munich-airport.com","Munich Airport","MUC","EDDM","Munich","Germany","Europe",42,
 "State-owned airport company","Flughafen Muenchen GmbH (FMG)","munich-airport.com","Bavaria / Federal Republic / City of Munich","","",
 "FMG sells airport operations expertise through Munich Airport International (MAI), which OPERATES Terminal A at Newark (EWR) and manages airports in Bulgaria, Honduras and El Salvador - a peer operator and competitor as well as a buyer. EU TED tenders; DE-language sources.",
 "de","eu","FMG supplier portal / EU TED"),
("flughafen-zuerich.ch","Zurich Airport","ZRH","LSZH","Zurich","Switzerland","Europe",31,
 "Listed airport company (canton-anchored)","Flughafen Zuerich AG","flughafen-zuerich.ch","Flughafen Zuerich AG (Canton of Zurich anchor shareholder)","","",
 "Also operates concessions in Brazil and India (Noida/Jewar) - international portfolio creates group-level technology decisions. DE-language sources.",
 "eu","eu","Flughafen Zuerich sourcing"),
("dublinairport.com","Dublin Airport","DUB","EIDW","Dublin","Ireland","Europe",33,
 "State-owned airport company","daa (Dublin Airport Authority)","daa.ie","daa plc (Irish State)","daa.ie","",
 "daa also runs Cork and a large international retail/management arm (ARI). Corporate domain daa.ie vs passenger dublinairport.com. Passenger cap regulation is the dominant live policy signal. EU TED tenders.",
 "eu","eu","daa e-tenders / EU TED"),
# ---- Middle East (2) ----------------------------------------------------------------------
("dubaiairports.ae","Dubai International Airport","DXB","OMDB","Dubai","United Arab Emirates","Middle East",92,
 "Government-owned operator","Dubai Airports","dubaiairports.ae","Government of Dubai","","Emirates (Terminal 3 exclusive) | emirates.com; dnata (ground/cargo handling) | dnata.com",
 "Dubai Airports is a thin asset-owner/operator that outsources heavily; Emirates and dnata own large parts of the passenger and baggage estate. The announced move to Al Maktoum (DWC) is a generational capital signal.",
 "me","me","Dubai Airports / Dubai Government eSupply"),
("dohahamadairport.com","Hamad International Airport","DOH","OTHH","Doha","Qatar","Middle East",53,
 "Airline-group-owned operator","MATAR (Qatar Company for Airports Operation & Management)","dohahamadairport.com","Qatar Airways Group","qatarairways.com","Qatar Aviation Services (handling) | qas.com.qa",
 "Owned and run by the airline group - so the airport buyer and the airline buyer are the SAME parent. Expansion phases C/D are active. Treat Qatar Airways Group as the true account.",
 "me","me","Qatar Airways Group / MATAR tenders"),
# ---- Asia-Pacific (4) ---------------------------------------------------------------------
("changiairport.com","Singapore Changi Airport","SIN","WSSS","Singapore","Singapore","Asia-Pacific",68,
 "Government-linked airport company","Changi Airport Group (CAG)","changiairport.com","Changi Airport Group (Temasek-held)","","",
 "CAG also runs Changi Airports International (consulting/concessions abroad) and is widely treated as the global reference airport for passenger technology - high bar, strong in-house capability, active Terminal 5 mega-program.",
 "apac","apac","CAG procurement / GeBIZ"),
("tokyo-haneda.com","Tokyo International Airport (Haneda)","HND","RJTT","Tokyo","Japan","Asia-Pacific",86,
 "Split: state airside + private terminal companies","Tokyo International Air Terminal Corporation (TIAT) / Japan Airport Terminal Co.","tokyo-airport-bldg.co.jp","Ministry of Land, Infrastructure, Transport and Tourism (MLIT) - airside","mlit.go.jp",
 "Japan Airport Terminal Co. (Terminals 1/2 domestic) | tokyo-airport-bldg.co.jp; Tokyo International Air Terminal Corp / TIAT (Terminal 3 international) | tiat.co.jp",
 "STRUCTURALLY the most split account: MLIT owns runways/airside, Japan Airport Terminal Co. (listed) runs domestic terminals, TIAT runs the international terminal. Three separate buying centers, no single airport-wide IT owner. JP-language sources.",
 "apac","apac","MLIT public tender + private terminal RFP"),
("airport.kr","Incheon International Airport","ICN","RKSI","Seoul","South Korea","Asia-Pacific",71,
 "State-owned corporation","Incheon International Airport Corporation (IIAC)","airport.kr","Government of South Korea (MOLIT)","molit.go.kr","",
 "IIAC is a public corporation with a formal, published procurement process and a strong smart-airport / biometric program. KR-language sources; public tender notices are the primary signal.",
 "apac","apac","IIAC e-procurement / KONEPS"),
("sydneyairport.com.au","Sydney Airport","SYD","YSSY","Sydney","Australia","Asia-Pacific",41,
 "Private airport company","Sydney Airport (Sydney Airport Corporation Limited)","sydneyairport.com.au","Sydney Aviation Alliance (IFM Investors-led consortium)","","",
 "Taken private in 2022 by an IFM-led consortium - now unlisted, so financial disclosure dropped and Claygent must lean on consortium/investor reporting. Competes with the new Western Sydney (Nancy-Bird Walton) airport.",
 "apac","apac","Sydney Airport procurement"),
]

FIELDS = ["airport_domain","airport_name","iata_code","icao_code","city","country","region",
          "annual_passengers_m_2024_est","passenger_volume_tier","operator_model",
          "airport_authority_name","airport_authority_domain",
          "parent_authority_name","parent_authority_domain",
          "terminal_operators","has_separate_terminal_operators","buying_center_count",
          "enrichment_domain","enrichment_domain_differs",
          "systems_owner_note","trade_associations","airport_publications",
          "procurement_system","primary_language","account_tier"]

def tier(p):
    if p >= 70: return "Mega hub (70M+)"
    if p >= 45: return "Large hub (45-70M)"
    if p >= 30: return "Mid hub (30-45M)"
    return "Small hub (<30M)"

LANG = {"Mexico":"Spanish","Brazil":"Portuguese","Colombia":"Spanish","France":"French",
        "Germany":"German","Spain":"Spanish","Switzerland":"German","Turkey":"Turkish",
        "Japan":"Japanese","South Korea":"Korean","Netherlands":"Dutch/English",
        "United Arab Emirates":"English/Arabic","Qatar":"English/Arabic"}

out = []
for r in ROWS:
    (dom,name,iata,icao,city,country,region,pax,model,auth,authdom,par,pardom,
     terms,note,akey,pkey,proc) = r
    n_terms = len([t for t in terms.split(";") if t.strip()]) if terms else 0
    # buying centers: the airport-wide authority, the parent (if distinct), + each terminal operator
    centers = 1 + (1 if pardom and pardom != authdom else 0) + n_terms
    lang = LANG.get(country, "English")
    if country == "Canada" and iata == "YUL": lang = "French/English"
    out.append({
        "airport_domain": dom, "airport_name": name, "iata_code": iata, "icao_code": icao,
        "city": city, "country": country, "region": region,
        "annual_passengers_m_2024_est": pax, "passenger_volume_tier": tier(pax),
        "operator_model": model,
        "airport_authority_name": auth, "airport_authority_domain": authdom,
        "parent_authority_name": par, "parent_authority_domain": pardom,
        "terminal_operators": terms,
        "has_separate_terminal_operators": "Yes" if n_terms else "No",
        "buying_center_count": centers,
        "enrichment_domain": (authdom or dom),
        "enrichment_domain_differs": "Yes" if (authdom and authdom != dom) else "No",
        "systems_owner_note": note,
        "trade_associations": ASSOC[akey], "airport_publications": PUBS[pkey],
        "procurement_system": proc, "primary_language": lang,
        "account_tier": "Tier 1" if (pax >= 60 or centers >= 3) else ("Tier 2" if pax >= 30 else "Tier 3"),
    })

assert len(out) == 50, len(out)
doms = [o["airport_domain"] for o in out]
dupes = {d for d in doms if doms.count(d) > 1}

os.makedirs(os.path.join(BASE,"data"), exist_ok=True)
with open(os.path.join(BASE,"data","airports.csv"),"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(out)
with open(os.path.join(BASE,"data","airports.json"),"w",encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("rows:", len(out))
print("duplicate domains:", dupes or "none")
print("regions:", {r: sum(1 for o in out if o['region']==r) for r in sorted({o['region'] for o in out})})
print("with terminal operators:", sum(1 for o in out if o['has_separate_terminal_operators']=="Yes"))
print("distinct parent authorities:", len({o['parent_authority_domain'] for o in out if o['parent_authority_domain']}))
print("tiers:", {t: sum(1 for o in out if o['account_tier']==t) for t in ["Tier 1","Tier 2","Tier 3"]})
