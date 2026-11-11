"""Tier 1 contacts sourced via Clay Find People on 2026-11-11.

Regenerates data/target_contacts.csv. One row per person. `email_status` records whether Clay's
Work Email waterfall returned a verified address (found / not_found / pending). The addresses
themselves are not stored in this repository; pull them from the Clay task in `clay_task_id`. `fit` flags rows to drop before outreach.
"""
import csv, pathlib

# (account, segment, name, title, location, linkedin, email, fit, task_id)
M="mcp-task_0tockruZewhzTZMv9iR"; S="mcp-task_0tockrrz3jyxkm3CBYt"; F="mcp-task_0tocks4RjqTVNGyGRor"
T="mcp-task_0tocks3YWEZ8X8DZvSz"; O="mcp-task_0tocksimsssEXxEFpef"
ROWS = [
# ---- Mining ----
("Agnico Eagle","Mining","Michael Perron","Directeur d'usine (Mill Manager), Canadian Malartic","Malartic, QC","https://www.linkedin.com/in/michaelperron28/","found","target",M),
("Agnico Eagle","Mining","Hafedh Tbaybi","Mill Superintendent","Canada","https://www.linkedin.com/in/hafedh-tbaybi-p-eng-1a606280/","found","target",M),
("Agnico Eagle","Mining","Raphael Boutin","Process Plant Maintenance Manager","Gallichan, QC","https://www.linkedin.com/in/raphael-boutin-bb1a54aa/","found","target",M),
("Rio Tinto","Mining","Dustin Morris","Maintenance Manager - Underground (Kennecott)","Salt Lake City, UT","https://www.linkedin.com/in/dustin-morris-875b9424/","found","target",M),
("Rio Tinto","Mining","Matthew Thomas","Mine Operations Manager (IOC)","Labrador City, NL","https://www.linkedin.com/in/matthewthomaslicensedplumber/","found","target",M),
("Rio Tinto","Mining","Eric Planque","General Manager Operations (RTFT)","Varennes, QC","https://www.linkedin.com/in/eric-planque-155858b9/","found","target",M),
("Teck Resources","Mining","Aaron Wylie","Mine Manager (Highland Valley Copper)","Kamloops, BC","https://www.linkedin.com/in/aaron-wylie-0b043746/","found","target",M),
("Teck Resources","Mining","Darren McIlwain","Mill Operations Superintendent (Highland Valley Copper)","Kamloops, BC","https://www.linkedin.com/in/darren-mcilwain-70b98946/","found","target",M),
("Newmont","Mining","Ramon Arnaudez","Mine Operations Manager - Peñasquito","Calgary, AB","https://www.linkedin.com/in/ramon-arnaudez-p-eng-671246b/","found","target",M),
("Newmont","Mining","Gordon Ruttenbur","Mine Manager","United States","https://www.linkedin.com/in/gordon-ruttenbur-70676340/","found","target",M),
("Newmont","Mining","Mark Ward","Mine Manager","Spring Creek, NV","https://www.linkedin.com/in/mark-ward-61a13748/","pending","target - email pending",M),
("Nutrien","Mining","Tim Mbanga","Mill Operations Superintendent (potash)","Regina, SK","https://www.linkedin.com/in/tim-mbanga-p-eng-pmp-83292350/","found","target",M),
("Nutrien","Mining","Christopher Pierce","Maintenance Manager (nitrogen plant)","Borger, TX","https://www.linkedin.com/in/christopher-g-pierce-cmrt-62705112/","found","target",M),
("Cleveland-Cliffs","Mining + steel","Michael Jones","Section Manager - Maintenance, Iron Producing","Akron, OH","https://www.linkedin.com/in/michael-jones-371688161/","found","target",M),
("Cleveland-Cliffs","Mining + steel","Zachary Oldfield","Maintenance Manager (Middletown Works)","Middletown, OH","https://www.linkedin.com/in/zachary-oldfield-7186067b/","found","target",M),
("Cleveland-Cliffs","Mining + steel","David Sena","Plant Operations Manager (Burns Harbor)","Valparaiso, IN","https://www.linkedin.com/in/david-sena-04b9498b/","found","target",M),
("Barrick","Mining","Tony Woodfine","Manager of Mine Operations","Canada","https://www.linkedin.com/in/tony-woodfine-614678119/","pending","target - email pending",M),
("Vale Base Metals","Mining","Nathan Farrow","Mine Manager (Sudbury)","Chelmsford, ON","https://www.linkedin.com/in/nathan-farrow-25479b144/","found","target",M),
("Vale Base Metals","Mining","Stephanie Bleker","General Manager, Copper Cliff Mine Complex","Canada","https://www.linkedin.com/in/stephanie-bleker-b46464a2/","found","target",M),
("Vale Base Metals","Mining","Mike Vallance","Mine Manager, Manitoba Operations (Thompson)","Thompson, MB","https://www.linkedin.com/in/mike-vallance-138b5012/","found","target",M),
# ---- Mills ----
("Nucor","Steel mills","Gustavo Fuentes","Plant Manager - Nucor Wire Products","Maryville, MO","https://www.linkedin.com/in/gustavo-fuentes-0b24237/","found","target",S),
("Nucor","Steel mills","Kaleb Fitch","Melt Shop Manager","Lexington, NC","https://www.linkedin.com/in/kaleb-fitch-33467415/","found","target",S),
("Nucor","Steel mills","Peyton Nicholson","Beam Mill Manager (Nucor Steel Berkeley)","Charleston, SC","https://www.linkedin.com/in/peyton-nicholson-57019b128/","found","target",S),
("U.S. Steel","Steel mills","Giuseppe Randazzo","Plant Manager (Fairfield Works)","Bessemer, AL","https://www.linkedin.com/in/giuseppe-randazzo-0548ba45/","found","target",S),
("U.S. Steel","Steel mills","Gino DiDomenico","BOP Operations Manager (Mon Valley)","Pittsburgh, PA","https://www.linkedin.com/in/didomenicpgh/","not_found","target - no email found; try mobile waterfall",S),
("U.S. Steel","Steel mills","Josh Mangus","Gas Handling & Light Oil Recovery Operations Manager (Clairton)","Pittsburgh, PA","https://www.linkedin.com/in/joshmangus/","found","target",S),
# ---- Oil & gas ----
("Chevron","Oil & gas","Caleb Eide","Upstream Operations Manager (Bakken)","Tioga, ND","https://www.linkedin.com/in/caleb-eide-4287949a/","found","target",S),
("Chevron","Oil & gas","Franklin Levis","Operations Manager","United States","https://www.linkedin.com/in/franklin-levis-27aab022a/","pending","target - email pending",S),
("ExxonMobil","Oil & gas","Regina Davis","Global Reliability and Maintenance Manager","United States","https://www.linkedin.com/in/regina-davis-91306260/","found","target",S),
("Marathon Petroleum","Oil & gas","Scott Dose","Maintenance Manager (St. Paul Park refinery)","St Paul Park, MN","https://www.linkedin.com/in/scott-dose-a59a95150/","found","target - verify email (name order looks inverted)",S),
("Marathon Petroleum","Oil & gas","Tyler Beck","Sr. Operations Manager","Prospect, PA","https://www.linkedin.com/in/tyler-beck-84394384/","found","target - verify email (non-standard pattern)",S),
("Valero","Oil & gas","Mike Mankopf","Operations Manager (Port Arthur refinery)","Port Arthur, TX","https://www.linkedin.com/in/mike-mankopf-95737aa4/","found","target",S),
("Valero","Oil & gas","Justin Moen","Plant Manager (renewables plant)","Okoboji, IA","https://www.linkedin.com/in/justin-moen-b982945b/","found","target",S),
("Suncor","Oil & gas","Jonah Donald","Site Operations Manager (oil sands)","Fort McMurray, AB","https://www.linkedin.com/in/jonah-donald-6aa08787/","found","target",S),
("Suncor","Oil & gas","Ross Carruthers","Operations Manager and Chief Power Engineer - Upgrading","Canada","https://www.linkedin.com/in/ross-carruthers-mba-peng-21672752/","found","target",S),
# ---- Freight rail ----
("BNSF","Rail - Class I","Chris Sanford","AVP & Chief Mechanical Officer","Dallas-Fort Worth","https://www.linkedin.com/in/chris-sanford-7674261b/","found","target",F),
("BNSF","Rail - Class I","Demond Dortch","AVP & Chief Mechanical Officer","United States","https://www.linkedin.com/in/demond-dortch-591a78a/","found","target",F),
("BNSF","Rail - Class I","Robert Podawiltz","Superintendent II, Argentine LMIT (locomotive shop)","Lawrence, KS","https://www.linkedin.com/in/robert-podawiltz-418018102/","found","target",F),
("Union Pacific","Rail - Class I","Grace Olsen","General Director Mechanical Engineering & Quality","Omaha, NE","https://www.linkedin.com/in/grace-olsen-6b85b419/","found","target - verify email (different surname)",F),
("Union Pacific","Rail - Class I","Marquis Davis","General Director of Track Maintenance","Chicago, IL","https://www.linkedin.com/in/marquis-davis-78600b76/","pending","target - email pending",F),
("Union Pacific","Rail - Class I","Tamra Milone","Senior Director Engineering Planning","Omaha, NE","https://www.linkedin.com/in/tamra-milone/","found","target",F),
("CSX","Rail - Class I","Kelly Park","Senior Director: Engineering, Facilities, and C&S","Jacksonville, FL","https://www.linkedin.com/in/kellyparkcsx/","pending","target - email pending",F),
("CSX","Rail - Class I","Thomas Munns","Director - Engineering Procurement","Jacksonville, FL","https://www.linkedin.com/in/tmunns/","not_found","target - no email found; try mobile waterfall",F),
("CSX","Rail - Class I","Cory Oakley","Director Engineering Safety","Waverly, TN","https://www.linkedin.com/in/cory-oakley-mba-665a44189/","not_found","secondary - no email found",F),
("Norfolk Southern","Rail - Class I","Kevin Krull","Senior Director Mechanical Operations, Southern Region","Atlanta, GA","https://www.linkedin.com/in/kevin-krull-6a032a30b/","found","target",F),
("Norfolk Southern","Rail - Class I","Gabriel Broberg","Sr. Director Mechanical, Northern Region","Homewood, IL","https://www.linkedin.com/in/gabrielbroberg/","found","target",F),
("Norfolk Southern","Rail - Class I","Eric Thomas","Director Mechanical Operations","Norfolk, VA","https://www.linkedin.com/in/eric-thomas-37961125/","found","target",F),
("CPKC","Rail - Class I","Brandon Heilig","Director Mechanical","Shreveport, LA","https://www.linkedin.com/in/brandon-heilig-463454103/","found","target",F),
("CPKC","Rail - Class I","Solange de Blois","Assistant Director Mechanical Technology","Calgary, AB","https://www.linkedin.com/in/solangedeblois/","found","target",F),
("CN","Rail - Class I","Manuel Salazar","Chief Mechanical Officer - East/South","Chicago, IL","https://www.linkedin.com/in/manuel-salazar-1741bb25/","found","target",F),
("CN","Rail - Class I","Daniel Clements","Chief Mechanical Officer - Western Region","Edmonton, AB","https://www.linkedin.com/in/daniel-clements-0b9458284/","found","target",F),
("CN","Rail - Class I","Steven Albright","Assistant Chief Mechanical Officer","Canada","https://www.linkedin.com/in/steven-albright-514a1852/","found","target",F),
("Genesee & Wyoming","Rail - short line","Michael Collier","Corporate Director Mechanical","St Augustine, FL","https://www.linkedin.com/in/michael-collier-91670022/","found","target",F),
("Genesee & Wyoming","Rail - short line","Murray MacBeth","Chief Mechanical Officer, West Region Canada","Bayfield, ON","https://www.linkedin.com/in/murray-macbeth-9a0b5547/","found","target",F),
("Genesee & Wyoming","Rail - short line","Ryan Carlson","Director of Engineering","Phoenix, AZ","https://www.linkedin.com/in/ryan-carlson-720931162/","found","target",F),
# ---- Transit / passenger ----
("Amtrak","Rail - passenger","George Hull","Vice President, Chief Mechanical Officer","Chesapeake, VA","https://www.linkedin.com/in/george-hull-4a29897/","found","target",T),
("Amtrak","Rail - passenger","Dale Engelhardt","Deputy Chief Mechanical Officer","Blue Island, IL","https://www.linkedin.com/in/dale-engelhardt-78285044/","not_found","target - no email found; try mobile waterfall",T),
("Amtrak","Rail - passenger","Tammy Krause","Director Rolling Stock Engineering","Wilmington, DE","https://www.linkedin.com/in/krause-tammy-16b816146/","not_found","target - no email found; try mobile waterfall",T),
("MTA","Rail - transit","Laura Smith","Chief Operations Officer","Huntington Station, NY","https://www.linkedin.com/in/laura-smith-0875247/","found","target - verify email (Metro-North domain)",T),
("MTA","Rail - transit","Paul de Konkoly Thege","Senior Director, Rolling Stock Strategy","New York, NY","https://www.linkedin.com/in/pauldekt/","pending","secondary (bus-side) - email pending",T),
("MTA","Rail - transit","Paul Dvoskin","Director","New York, NY","https://www.linkedin.com/in/paul-dvoskin-a466785/","pending","verify title - email pending",T),
("WMATA","Rail - transit","Leroy Jones","EVP & Chief Operations Officer","Washington, DC","https://www.linkedin.com/in/leroy-jones-68a25413/","found","target",T),
("Chicago Transit Authority","Rail - transit","Cara Bader","Chief Operating Officer","Chicago, IL","https://www.linkedin.com/in/carabader/","found","target",T),
("Chicago Transit Authority","Rail - transit","William Mooney","Chief Operating Officer (verify; may be prior)","Chicago, IL","https://www.linkedin.com/in/william-mooney-a6854911/","found","verify title",T),
("BART","Rail - transit","Robert Fitzgerald","Assistant Chief Mechanical Officer","Concord, CA","https://www.linkedin.com/in/robert-fitzgerald-96a606136/","found","target",T),
("Metrolinx","Rail - transit","Sean Fuller","Chief Operating Officer","Toronto, ON","https://www.linkedin.com/in/sean-fuller-4aaa059b/","found","target",T),
("Metrolinx","Rail - transit","Michael DiGirolamo","Director, Rolling Stock, Systems, Operations & Maintenance","Toronto, ON","https://www.linkedin.com/in/mdigirolamocclp/","found","target",T),
("Metrolinx","Rail - transit","Bahaa Kordab","Construction Manager","Toronto, ON","https://www.linkedin.com/in/bahaa-kordab/","found","secondary",T),
("LA Metro","Rail - transit","Conan Cheung","Chief Operations Officer","Los Angeles, CA","https://www.linkedin.com/in/conan-cheung-5153a12a/","found","target",T),
("LA Metro","Rail - transit","Errol Taylor","Deputy COO, Infrastructure Maintenance & Engineering","United States","https://www.linkedin.com/in/errol-taylor-p-e-8351635/","found","target",T),
("LA Metro","Rail - transit","Steven Gota","Deputy COO, Shared Mobility (Interim)","Los Angeles, CA","https://www.linkedin.com/in/steve-gota-8949837/","found","secondary",T),
# ---- Rail OEM plants / people movers ----
("Wabtec","Rail - OEM plants","Jason Danowski","Plant Manager - Cabs (Erie)","Erie, PA","https://www.linkedin.com/in/jason-danowski-2908598/","found","target",O),
("Wabtec","Rail - OEM plants","Audie Penn","Plant Manager","Albia, IA","https://www.linkedin.com/in/audiepenn/","found","target",O),
("Wabtec","Rail - OEM plants","Marcio Marques","Director, Engineering Operations","Chicago, IL","https://www.linkedin.com/in/marcioltmarques/","found","target",O),
("Progress Rail","Rail - OEM plants","Benji Stamford","Plant Manager","Louisville, KY","https://www.linkedin.com/in/benji-stamford-b728221/","found","target",O),
("Progress Rail","Rail - OEM plants","Prakash Satsangi","Director of Operations","Greenwood, IN","https://www.linkedin.com/in/prakash-s-satsangi-a5a326122/","found","target",O),
("Progress Rail","Rail - OEM plants","Brandon Smith","Director of Operations","Waskom, TX","https://www.linkedin.com/in/brandon-smith-13b132125/","found","target",O),
("Alstom","Rail OEM + APM","George Carroll","Site Director - JFK AirTrain (APM O&M)","New York, NY","https://www.linkedin.com/in/george-carroll-73a3aa7/","found","target - already in Clay Audiences",O),
("Alstom","Rail OEM + APM","Christophe Raulet","RSC Engineering Director North America","Canada","https://www.linkedin.com/in/christophe-raulet-77403065/","found","target",O),
("Alstom","Rail OEM + APM","Jean-François Nadeau","Engineering Director, Services North America","Montreal, QC","https://www.linkedin.com/in/jf-nadeau/","found","target",O),
("DFW Airport","People mover - airport","Don Riney","District Energy Plant Manager","Arlington, TX","https://www.linkedin.com/in/don-riney-09496547/","found","secondary (energy plant, not APM)",O),
("DFW Airport","People mover - airport","James Williams","Director of Operations","Fort Worth, TX","https://www.linkedin.com/in/james-williams-07a32b21a/","not_found","target - no email found; try mobile waterfall",O),
("Hartsfield-Jackson Atlanta","People mover - airport","Harland Warner","Assistant Airport Operations Director","Acworth, GA","https://www.linkedin.com/in/harland-warner-46193558/","not_found","target - no email found; try mobile waterfall",O),
("Hartsfield-Jackson Atlanta","People mover - airport","Enrique Victrum","Assistant Site Manager","Decatur, GA","https://www.linkedin.com/in/enrique-victrum-795276139/","pending","verify title - email pending",O),
]
HEADER=["account","segment","name","title","location","linkedin","email_status","fit","clay_task_id"]
out = pathlib.Path(__file__).resolve().parent.parent/"data"/"target_contacts.csv"
with out.open("w",newline="") as f:
    w=csv.writer(f); w.writerow(HEADER); w.writerows(ROWS)
print(f"wrote {len(ROWS)} rows; emails found {sum(1 for r in ROWS if r[6]=='found')}")
