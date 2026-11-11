# Target account list: industrial + rail / people-mover expansion

96 accounts, 41 Tier 1. 47 were returned by a live Clay company search on 2026-11-11
(`clay_verified = Y`); the rest were hand-added where Clay's industry taxonomy or semantic
search did not surface them (short-line holdings, airport authorities, APM contractors).

Source of truth is `build/seed_target_accounts.py`; it regenerates `data/target_accounts.csv`.

## How the list was built

1. Clay company searches by industry (Mining, Oil and Gas, Rail Transportation, Urban Transit
   Services, Railroad Equipment Manufacturing) and by semantic description (steel mill, pulp mill,
   cement plant, automated people mover, monorail, cable-propelled people mover), filtered to
   North America and 1,000+ employees for current markets, 200+ for expansion.
2. Removed vendors and competitors that share the industry code but are not buyers (Komatsu
   Mining, Weir, Orica, Halliburton, Weatherford, TechnipFMC, Trapeze, Optibus, ADB Safegate).
3. Removed noise from semantic search (warehouse robotics, elevator subsidiaries, ad agencies).
4. Added the hand list where the buyer is a public authority or a private holding that Clay
   indexes thinly: airport authorities with APMs, short-line holdings, APM O&M contractors,
   monorail operators.
5. Tiered: 1 = anchor with many sites and confirmed buyer titles, 2 = strong fit, 3 = stretch.

## Tier 1 (41)

| Account | Segment | Tier | Why | Clay |
|---|---|---|---|---|
| Freeport-McMoRan | Mining - copper/moly | 1 | 7 US copper mines (Morenci, Bagdad, Safford, Sierrita, Chino, Tyrone) plus Climax and Henderson moly; largest US copper operator and the clearest multi-site target. | Y |
| Newmont | Mining - gold/copper | 1 | Nevada Gold Mines JV (with Barrick), Cripple Creek, Peñasquito, Brucejack, Red Chris. Clay returned Mine Ops Manager and site IT Ops Manager titles at Newmont sites. | Y |
| Barrick Mining | Mining - gold/copper | 1 | Operator of Nevada Gold Mines (Carlin, Cortez, Turquoise Ridge, Goldstrike), the largest gold complex in the world; Hemlo in Ontario. | Y |
| Rio Tinto | Mining - copper/iron ore/borates | 1 | Kennecott Utah Copper (mine, smelter, refinery), Iron Ore Company of Canada (Labrador City), US Borax (Boron, CA), Rio Tinto Fer et Titane (Quebec). Clay found Mine Ops Manager at Labrador City and site support manager at Kennecott. | Y |
| Teck Resources | Mining - copper/zinc | 1 | Highland Valley Copper, Trail smelter, Red Dog (Alaska), Quebrada Blanca. Canadian anchor with large processing plants. | Y |
| Vale Base Metals | Mining - nickel/copper | 1 | Sudbury (Copper Cliff, Creighton, Coleman, Totten), Thompson, Voisey's Bay, Long Harbour. Clay returned GM Copper Cliff Mine Complex and a Mine Manager with verified emails. | Y |
| Agnico Eagle Mines | Mining - gold | 1 | Detour Lake, Canadian Malartic, LaRonde, Macassa, Meadowbank, Meliadine, Fosterville. Largest Canadian gold miner by output; 10+ operating sites. | N |
| Nutrien | Mining - potash | 1 | Six potash mines in Saskatchewan (Allan, Cory, Lanigan, Rocanville, Vanscoy, Patience Lake) plus phosphate (Aurora NC, White Springs FL). Underground mining + mills. | N |
| Cleveland-Cliffs | Mining + steel (integrated) | 1 | Iron ore mines (Hibbing, Minorca, Northshore, Tilden, United) feeding integrated mills (Burns Harbor, Indiana Harbor, Cleveland, Middletown, Dearborn). Both a mining and a mill account. Clay returned Ops Manager HBI and Shift Manager titles. | Y |
| Nucor | Steel mills | 1 | 26 steel mills and 300+ facilities; the largest US steelmaker. Clay returned Plant Manager, Rolling Mill Manager, Beam Mill Manager and Melt Shop Manager titles with verified emails. | Y |
| Steel Dynamics | Steel mills | 1 | Butler, Columbus, Sinton, Roanoke, Structural & Rail (Columbia City), plus OmniSource recycling yards. Fast-growing, decentralized plant leadership. | Y |
| U.S. Steel | Steel mills | 1 | Gary Works, Mon Valley, Granite City, Big River Steel (AR), Keetac/Minntac mines. Now Nippon Steel-owned with committed capital investment. | Y |
| ConocoPhillips | Oil & gas - upstream | 1 | Largest US independent; Permian, Eagle Ford, Bakken, Alaska (Kuparuk, Prudhoe), Canadian oil sands (Surmont). Clay returned it with 16.5k employees. | Y |
| Chevron | Oil & gas - integrated | 1 | Permian, Gulf of Mexico, refineries (Pascagoula, El Segundo, Richmond, Pasadena), Hess assets post-2025. Clay flags new exec hires and expansion signals. | Y |
| ExxonMobil | Oil & gas - integrated | 1 | Baytown, Beaumont, Baton Rouge, Joliet refineries and chemical plants; Permian (Pioneer); largest US refiner by capacity. | N |
| Marathon Petroleum | Oil & gas - refining | 1 | 13 refineries (Galveston Bay, Garyville, Robinson, Catlettsburg, Los Angeles) plus MPLX midstream. Refinery managers are a classic off-LinkedIn persona. | N |
| Valero Energy | Oil & gas - refining | 1 | 15 refineries across US, Canada and UK; renewable diesel plants (Diamond Green Diesel). | N |
| Suncor Energy | Oil & gas - oil sands/refining | 1 | Base Plant, Firebag, Fort Hills, Syncrude; refineries in Edmonton, Sarnia, Montreal, Commerce City. Mining-style operations plus refining in one account. | N |
| Canadian Natural Resources | Oil & gas - oil sands/upstream | 1 | Horizon and Athabasca Oil Sands Project (mining + upgrading), Albian, Jackfish; largest Canadian producer. | N |
| Union Pacific | Rail - Class I freight | 1 | 32k route miles; major shops at North Little Rock, Fort Worth (Centennial), Roseville, Bailey Yard. Pending merger with Norfolk Southern announced 2025. | Y |
| BNSF Railway | Rail - Class I freight | 1 | Berkshire-owned; Topeka, Alliance, Argentine and Barstow shops; largest intermodal network. | N |
| CSX | Rail - Class I freight | 1 | Huntington and Waycross locomotive shops; 21k route miles in the East. | Y |
| Norfolk Southern | Rail - Class I freight | 1 | Juniata (Altoona) and Roanoke shops; 19k route miles. Merger with UP pending. | Y |
| CPKC | Rail - Class I freight | 1 | Only US-Canada-Mexico single-line network; Ogden (Calgary) and Kansas City shops. | Y |
| CN | Rail - Class I freight | 1 | Transcona (Winnipeg), Woodcrest (Chicago) and Pointe St-Charles shops; 20k route miles. | N |
| Genesee & Wyoming | Rail - short line holding | 1 | 100+ short lines under one domain: each railroad has its own GM and mechanical lead. Needs Get Company Hierarchy to unpack. Clay returned it at 1.3k employees (undercounted). | Y |
| Amtrak | Rail - intercity passenger | 1 | Beech Grove, Bear and Wilmington heavy-maintenance shops; Acela and Airo fleet rollouts. Clay scores it as the top-fit rail account (90). | Y |
| MTA (NYCT, LIRR, Metro-North) | Rail - transit | 1 | Largest NA transit network; three rail agencies with separate maintenance shops (207th St, Coney Island, Hillside, Croton-Harmon). Dedupe at the MTA parent. | Y |
| WMATA | Rail - transit | 1 | Metrorail 8000-series fleet rollout; Greenbelt, Shady Grove, Brentwood rail yards. | Y |
| Chicago Transit Authority | Rail - transit | 1 | 7000-series railcar delivery; Skokie Shops, Red Line extension. | Y |
| BART | Rail - transit | 1 | Fleet of the Future complete; Hayward Maintenance Complex expansion; train control modernization. | Y |
| Metrolinx | Rail - transit | 1 | GO Expansion (electrification), Ontario Line, Eglinton Crosstown, UP Express; largest transit capital program in Canada. | Y |
| LA Metro | Rail - transit | 1 | D Line extension, Sepulveda, Olympics 2028 readiness; HR4000 fleet. | N |
| Wabtec | Rail - OEM plants | 1 | Erie and Fort Worth locomotive plants, hundreds of component plants; also sells into mining (Wabtec Mining). Clay best-fit score 83. | Y |
| Progress Rail (Caterpillar) | Rail - OEM/MRO plants | 1 | EMD Muncie locomotive plant, dozens of trackwork and repair shops; Caterpillar parent. | Y |
| Alstom Americas | Rail - OEM + APM | 1 | Hornell NY (largest US passenger rail plant), Plattsburgh, La Pocatière; also the Innovia APM/monorail line and APM O&M contracts from Bombardier. One account bridging rail and people movers. | Y |
| Los Angeles World Airports | People mover - airport authority | 1 | LAX Automated People Mover opening; 30-year O&M concession with LINXS. Clay returned LAWA with the APM named in its description. | Y |
| Hartsfield-Jackson Atlanta | People mover - airport authority | 1 | Plane Train (busiest APM in the world) mid-life extension and West extension. | Y |
| DFW Airport | People mover - airport authority | 1 | Skylink APM (Innovia); terminal F and modernization program. | N |
| Port Authority of NY & NJ | People mover - airport authority | 1 | JFK AirTrain, EWR AirTrain replacement ($2B+ program). One buying center behind JFK, LGA and EWR. Note: domain resolves badly in Clay; pin the LinkedIn URL. | N |
| Mitsubishi Heavy Industries America | People mover - OEM + O&M | 1 | Crystal Mover APMs at ATL, MIA, Orlando, Tampa, DCA, Dulles; O&M contracts. Second major APM contractor after Alstom. | N |

## Full list by market

### Current markets: mining, mills, oil & gas (48)

| Account | Segment | Tier | Why | Clay |
|---|---|---|---|---|
| Mosaic | Mining - phosphate/potash | 2 | Florida phosphate mines and chemical plants (Four Corners, South Fort Meade, New Wales, Bartow), potash mines in Saskatchewan (Esterhazy, Belle Plaine). | N |
| Peabody Energy | Mining - coal | 2 | Powder River Basin (North Antelope Rochelle, Caballo, Rawhide) plus Illinois Basin underground mines. Clay returned Mine Manager and Plant Manager titles with emails. | Y |
| Core Natural Resources | Mining - coal | 2 | 2025 merger of Arch Resources and CONSOL: Leer, Leer South, Pennsylvania Mining Complex (Bailey, Enlow Fork, Harvey), West Elk, Black Thunder. Largest US met coal operator. | N |
| Alcoa | Mining + smelting - aluminum | 2 | Bauxite, alumina refining and smelters: Warrick (IN), Massena (NY), Intalco, Deschambault and Baie-Comeau (QC). Clay returned it under Mining with 18k employees. | Y |
| Glencore Canada | Mining - nickel/copper/zinc | 2 | Sudbury Integrated Nickel Operations, Raglan, Horne smelter, CCR refinery, CEZ zinc, Kidd Operations. Large Canadian processing footprint. | Y |
| Kinross Gold | Mining - gold | 2 | Round Mountain and Bald Mountain (NV), Fort Knox (AK), Great Bear project (ON), Paracatu (Brazil). | Y |
| Vulcan Materials | Mining - aggregates | 2 | 400+ quarries and plants. The clearest case of plant managers who are not on LinkedIn: hundreds of site leads, almost none with public profiles. Facility-first approach required. | N |
| Martin Marietta | Mining - aggregates/cement | 2 | Quarries, cement plants (Midlothian TX) and magnesia plants. Same off-LinkedIn site-manager profile as Vulcan. | N |
| Hecla Mining | Mining - silver | 3 | Greens Creek (AK), Lucky Friday (ID), Keno Hill (YT), Casa Berardi (QC). Smaller but fully North American. | N |
| ArcelorMittal Dofasco | Steel mills | 2 | Canada's largest flat-rolled producer; DRI-EAF conversion underway (major capex). | N |
| Algoma Steel | Steel mills | 2 | Converting to EAF steelmaking (2025-2026); single large integrated site. | N |
| EVRAZ North America | Steel mills | 2 | Pueblo (CO) rail mill, Regina (SK), Portland (OR), Calgary/Camrose/Red Deer pipe mills. Largest NA rail producer, so also a rail-market bridge. | Y |
| Commercial Metals Company | Steel mills | 2 | Micro-mills and minimills (Mesa, Durant, Seguin, Cayce, Jacksonville) plus fabrication plants. | N |
| Gerdau North America | Steel mills | 2 | Long steel mills (Midlothian, Charlotte, Jackson, Cartersville, Whitby, Cambridge). | N |
| International Paper | Pulp and paper mills | 2 | 20+ North American containerboard and pulp mills; 2025 DS Smith acquisition. Mill managers are the buyer. | N |
| Georgia-Pacific | Pulp and paper mills | 2 | Koch-owned; dozens of pulp, paper and building-products mills across the US South. | N |
| Domtar | Pulp and paper mills | 2 | Combined Domtar + Resolute + Paper Excellence: pulp, paper and sawmills across US and Canada. | N |
| Weyerhaeuser | Wood products mills | 2 | Lumber, OSB and engineered-wood mills; Clay returned it at 7.4k employees. | Y |
| Amrize (formerly Holcim US) | Cement plants | 2 | 1,000+ sites, 12 US cement plants; newly spun out and listed, with its own procurement. | Y |
| Cemex USA | Cement plants | 2 | US cement plants (Victorville, Balcones, Brooksville, Demopolis) plus aggregates. | Y |
| Sylvamo | Pulp and paper mills | 3 | Eastover (SC), Ticonderoga (NY) and Riverdale mills; smaller uncoated-freesheet pure play. | Y |
| Phillips 66 | Oil & gas - refining/midstream | 2 | Sweeny, Wood River, Lake Charles, Bayway, Ponca City refineries; large midstream footprint. | N |
| Cenovus Energy | Oil & gas - integrated | 2 | Foster Creek, Christina Lake, Sunrise; refineries at Lima, Toledo, Superior, Lloydminster upgrader. | N |
| Imperial Oil | Oil & gas - integrated | 2 | Kearl oil sands mine, Cold Lake, Syncrude stake; Strathcona, Sarnia, Nanticoke refineries. | N |
| Oxy (Occidental) | Oil & gas - upstream/chemicals | 2 | Permian leader, OxyChem plants (chlor-alkali), Stratos DAC plant. Clay returned it with 15k employees. | Y |
| Enbridge | Oil & gas - midstream | 2 | Largest NA liquids pipeline network; hundreds of pump and compressor stations, terminals, gas plants. | N |
| Kinder Morgan | Oil & gas - midstream | 2 | 70k miles of pipeline, 139 terminals; terminal and station managers are site-level buyers. | N |
| Energy Transfer | Oil & gas - midstream | 2 | Gas processing plants, fractionators (Mont Belvieu), Nederland and Marcus Hook terminals. | N |
| NOV | Oil & gas - equipment plants | 3 | Dozens of manufacturing plants and service yards; an industrial-plant account inside the energy vertical. | Y |

### Expansion: rail, transit, airport people movers, monorail (48)

| Account | Segment | Tier | Why | Clay |
|---|---|---|---|---|
| Watco | Rail - short line holding | 2 | 40+ short lines plus terminals and mechanical shops; private, so public org data is thin. | N |
| TTX Company | Rail - railcar pool | 2 | 180k railcars, field maintenance and repair shops (Mira Loma, North Augusta, Jacksonville). | Y |
| GATX | Rail - railcar leasing | 2 | Railcar maintenance network (Colton, Hearne, Waycross, Red Deer); tank car heavy. | Y |
| SEPTA | Rail - transit | 2 | New Market-Frankford cars, Regional Rail fleet replacement (Siemens), Trolley Modernization. | N |
| MBTA | Rail - transit | 2 | Red/Orange Line fleet (CRRC), commuter rail electrification planning, Green Line Type 10. | N |
| NJ Transit | Rail - transit | 2 | Multilevel III cars, Portal North Bridge, Meadows Maintenance Complex. | N |
| Sound Transit | Rail - transit | 2 | Light rail quadrupling (ST3); OMF East and South; Clay returned it at 1.9k employees. | Y |
| Brightline | Rail - private intercity | 2 | Florida operation plus Brightline West (Las Vegas to LA) under construction; first private intercity rail buyer in decades. | N |
| California High-Speed Rail Authority | Rail - HSR | 3 | Central Valley segment in construction; trainset procurement ongoing. Long sales cycle. | Y |
| Siemens Mobility North America | Rail - OEM plants | 2 | Sacramento rolling-stock plant (Charger, Venture, Airo), Lexington NC plant. | N |
| Stadler US | Rail - OEM plants | 2 | Salt Lake City plant building FLIRT and KISS trainsets for US agencies. | Y |
| Greenbrier | Rail - railcar plants | 2 | Railcar manufacturing (Gunderson, Sahagún Mexico) and repair shops network. | N |
| Trinity Rail | Rail - railcar plants | 2 | Railcar plants and maintenance shops across Texas, Alabama, Mexico. | N |
| Metropolitan Washington Airports Authority | People mover - airport authority | 2 | IAD AeroTrain and mobile lounges; Tier 2 APM extension to Concourse D. | N |
| Greater Orlando Aviation Authority | People mover - airport authority | 2 | Four APM lines (Mitsubishi Crystal Mover and Innovia) including Terminal C. | N |
| Phoenix Sky Harbor | People mover - airport authority | 2 | PHX Sky Train (Innovia) extended to rental car center 2022; city-run. | N |
| Tampa International (HCAA) | People mover - airport authority | 2 | SkyConnect APM (Mitsubishi) to rental car center; Airside D expansion. | N |
| Miami-Dade Aviation Department | People mover - airport authority | 2 | MIA Mover and Skytrain; county-run. | N |
| San Francisco International | People mover - airport authority | 2 | AirTrain (Innovia) extended 2020; owned by City of SF. | N |
| Houston Airports | People mover - airport authority | 2 | IAH Skyway and Subway; one domain covers IAH, HOU and EFD. | N |
| Doppelmayr Cable Car | People mover - cable APM | 2 | Cable Liner APMs at Oakland Airport Connector, Mexico City, Toronto Pearson LINK, Birmingham. Clay returned Doppelmayr under ropeway engineering. | Y |
| Leitner-Poma of America | People mover - cable APM | 2 | MiniMetro cable people movers (Cairo Airport, Perugia, Pisa Pisamover) and US urban gondola projects. Clay returned POMA and LEITNER. | Y |
| Hitachi Rail | People mover - monorail/APM | 2 | Monorail systems (Honolulu Skyline O&M, Taipei, Daegu), acquired Thales GTS signalling, acquired Clever Devices 2026. Growing NA footprint. | Y |
| Las Vegas Monorail (LVCVA) | People mover - monorail | 2 | 3.9-mile Bombardier monorail owned by the Las Vegas Convention and Visitors Authority since 2020; aging fleet. | N |
| Walt Disney World | People mover - monorail | 3 | Mark VI monorail fleet (1989) overdue for replacement; Disney Transportation runs it in-house. | N |
| Schwager Davis Inc | People mover - O&M contractor | 3 | Small US specialist that operates and maintains airport APMs and monorails (e.g., Indianapolis, Jacksonville Skyway, Mandalay Bay tram). | N |

## Loading into Clay

- Import `data/target_accounts.csv` as a company table keyed on `domain`.
- Pin `linkedin_company_url` on the rows flagged in `why` as resolving badly (PANYNJ, Houston
  Airports, Genesee & Wyoming) before enriching.
- Run Get Company Hierarchy on G&W, MTA, Alstom and Cleveland-Cliffs to expand to subsidiaries.
- Then Find People at Company with the `buyer_titles` column as the title filter, 3 to 5 per
  account, followed by Work Email and Mobile Phone.
