# -*- coding: utf-8 -*-
"""Builds the five Vim POC pages from data/poc_results_10.json.

Run: python3 pages/build_pages.py   (from vim/)
Artifact URLs for the series nav live in LINKS; fill them after the first publish.
"""
import json, os, html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "pages")
CSS = open(os.path.join(OUT, "shared.css")).read()
ROWS = json.load(open(os.path.join(BASE, "data", "poc_results_10.json")))
BY = {r["company_name"]: r for r in ROWS}
WF_URL = "https://app.clay.com/workspaces/91642/terracotta/tc-workflows/wf_0tm72qo2fw4Z5DAGxGn"
WF_ID = "wf_0tm72qo2fw4Z5DAGxGn"

LINKS = {
    "hub": "https://claude.ai/code/artifact/HUB",
    "brief": "https://claude.ai/code/artifact/BRIEF",
    "engine": "https://claude.ai/code/artifact/ENGINE",
    "dossier": "https://claude.ai/code/artifact/DOSSIER",
    "reference": "https://claude.ai/code/artifact/REFERENCE",
}
if os.path.exists(os.path.join(OUT, "links.json")):
    LINKS.update(json.load(open(os.path.join(OUT, "links.json"))))

NAV = [("hub", "POC Hub"), ("brief", "Executive Brief"), ("engine", "The Engine"),
       ("dossier", "DaVita Dossier"), ("reference", "Account Reference")]
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" '
         'href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..900&'
         'family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">')
FOOT = ("Prepared by Clay for Vim · Sep 30 2026 · Ten accounts run through workflow " + WF_ID +
        " in the Clay Demos (GTM) workspace · Measured figures come from the run log; anything marked "
        "'example' is an editable assumption, not a Vim number · Clinical and ICP criteria are placeholders "
        "until Vim confirms them")

e = html.escape


def page(key, title, css, body, script=""):
    nav = ['<nav class="series" aria-label="POC pages"><span class="brand">Clay × Vim</span>']
    for k, label in NAV:
        nav.append(f'<span class="cur" aria-current="page">{label}</span>' if k == key
                   else f'<a href="{LINKS[k]}">{label}</a>')
    nav.append("</nav>")
    doc = (f"<title>{title}</title>\n{FONTS}\n<style>\n{CSS}\n{css}\n</style>\n"
           f'<div class="wrap">{"".join(nav)}\n{body}\n<footer>{e(FOOT)}</footer></div>\n{script}')
    open(os.path.join(OUT, f"{key}.html"), "w").write(doc)


def a(url, text=None):
    if not url:
        return ""
    host = url.split("/")[2] if "://" in url else url
    return f'<a href="{e(url)}">{e(text or host)}</a>'


# ---------------------------------------------------------------- measured facts
PROV = [r for r in ROWS if r["segment"] == "provider"]
PAY = [r for r in ROWS if r["segment"] == "payer"]
EHR_FOUND = [r for r in PROV if r["ehr_vendor"]]
DUR = {"VillageMD": "2m 38s", "Oak Street Health": "59s", "One Medical": "1m 51s",
       "DaVita Kidney Care": "1m 28s", "LifeStance Health": "1m 23s"}
# Human review of each provider's "latest event" pick (engine sorts by date found)
EVENT_REVIEW = {
    "VillageMD": ("stop", "Not a trigger", "A 2026 legal article about the 2022 CityMD merger. PredictLeads dates it by when the article was found."),
    "Oak Street Health": ("review", "None found", "No M&A or expansion events in the last 365 days."),
    "One Medical": ("go", "Relevant", "Montefiore partnership expanding into Westchester (Jun 2026)."),
    "DaVita Kidney Care": ("stop", "Wrong pick", "Picked a $1M charity grant. A value-based-care partnership with Humana (Aug 25 2026, confidence 0.98) was in the same feed."),
    "LifeStance Health": ("stop", "Not a trigger", "A consumer research survey, labeled as a partnership."),
}

# ---------------------------------------------------------------- HUB
hub_css = """
.hero{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(260px,.8fr);gap:28px;align-items:end}
@media (max-width:820px){.hero{grid-template-columns:1fr}}
.hero .lede{margin-top:14px}
.flow{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px;display:flex;flex-direction:column;gap:10px}
.flow .step{display:grid;grid-template-columns:22px 1fr;gap:10px;align-items:baseline;font-size:14.5px}
.flow .step span{font:700 12px var(--mono);color:var(--accent)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px 20px 18px;display:flex;flex-direction:column;gap:10px;text-decoration:none;color:var(--ink);transition:border-color .15s,transform .15s}
a.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card .k{font:600 11.5px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
.card h3{font-size:21px;font-weight:800;font-stretch:106%}
.card p{font-size:15px;color:var(--muted)}
.card .for{font:12.5px var(--mono);color:var(--faint);margin-top:auto;padding-top:6px}
.card .go{font:600 14px var(--sans);color:var(--accent)}
.three{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:22px}
.three div{display:flex;flex-direction:column;gap:8px}
.three p{font-size:15px;color:var(--muted)}
"""
cards = [
    ("brief", "Executive Brief", "What it proved, and what's still open",
     "Five claims marked proven, partly proven or not yet, an editable cost model, the pilot metrics to hold it to, and four decisions for Vim.",
     "For Raveed, Daryl and Vim leadership · 5 minutes"),
    ("engine", "The Engine", "How the workflow works",
     "Six stages and ten steps, what each one saw on the ten accounts, the bugs the test caught, the scoring rules, and what's left to connect.",
     "For RevOps and whoever runs it"),
    ("dossier", "DaVita Dossier", "One provider record, end to end",
     "Footprint, EHR evidence, parent, dated signals and hiring, the flags a rep should see, and the record as structured data.",
     "For the provider sellers"),
    ("reference", "Account Reference", "All ten accounts, side by side",
     "Filter payers and providers, open any account to see every value with its source, and see what production changes.",
     "For anyone checking the data"),
]
hub_body = f"""
<header class="hero">
  <div>
    <p class="eyebrow acc">Clay × Vim · proof of concept</p>
    <h1>Find the provider groups Vim can serve, and know what changed</h1>
    <p class="lede">We built Vim's provider account engine in Clay and ran ten real organizations through it: five payers and the five provider groups Vim's ICP is modeled on. Every value it kept has a source. This page links everything it produced.</p>
  </div>
  <aside class="flow" aria-label="What the engine does">
    <p class="eyebrow">The engine, in order</p>
    <div class="step"><span>A</span><p>Pin each account to one company, even on shared domains</p></div>
    <div class="step"><span>B</span><p>Pull company, tech stack, parent, news and hiring from Clay's catalog</p></div>
    <div class="step"><span>C</span><p>Extract EHR, parent and M&amp;A evidence with plain rules</p></div>
    <div class="step"><span>D</span><p>Send only providers with a gap to research</p></div>
    <div class="step"><span>E</span><p>Research only the missing fields, with a source for each</p></div>
    <div class="step"><span>F</span><p>Reconcile, score and tier by rules, then write the why-now</p></div>
  </aside>
</header>

<section>
  <div class="stats">
    <div class="stat"><span class="n">10<small>/ 10</small></span><span class="l">accounts processed end to end, each pinned to the right company</span></div>
    <div class="stat"><span class="n">{len(EHR_FOUND)}<small>/ 5</small></span><span class="l">providers with an EHR backed by a source. Web tech data found none; research found all three</span></div>
    <div class="stat"><span class="n">7.5<small>credits</small></span><span class="l">data credits per provider account, plus 5–6 actions; payers cost 6.5</span></div>
    <div class="stat"><span class="n">0<small>/ 10</small></span><span class="l">accounts tiered. All wait on Vim's supported-EHR list and a payer scorecard</span></div>
  </div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Four pages</p><h2>Start with the one that fits who's reading</h2></div>
  <div class="cards">{"".join(f'<a class="card" href="{LINKS[k]}"><span class="k">{kk}</span><h3>{h}</h3><p>{p}</p><span class="for">{f}</span><span class="go">Open →</span></a>' for k, kk, h, p, f in cards)}</div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">What we learned</p><h2>Three things worth knowing</h2></div>
  <div class="three">
    <div><h3>EHR isn't in web tech data</h3><p>HG Insights returned 146 website technologies for UnitedHealthcare alone, and no clinical system for any of the ten. The EHR answers came from each organization's own pages, SEC filings and job posts, found by a research step that only ran where the gap existed.</p></div>
    <div><h3>A count is only as good as its date</h3><p>Oak Street's 67 locations and One Medical's 107 come from 2020 SEC filings. The engine kept the date beside each count, which is how we caught it. Production needs a freshness rule and a structured footprint source.</p></div>
    <div><h3>Signals need a stricter filter</h3><p>DaVita's news feed held a value-based-care partnership with Humana, one of the other nine accounts. The engine surfaced a charity grant instead, because it picked the newest item. Ranking by category and confidence fixes that.</p></div>
  </div>
</section>
"""
page("hub", "Vim POC Hub", hub_css, hub_body)

# ---------------------------------------------------------------- BRIEF
brief_css = """
.claims{display:flex;flex-direction:column;gap:12px}
.claim{display:grid;grid-template-columns:130px minmax(0,1fr);gap:18px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 20px;align-items:start}
@media (max-width:640px){.claim{grid-template-columns:1fr}}
.claim p{color:var(--muted);font-size:15px;margin-top:4px}
.calc{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:18px}
@media (max-width:820px){.calc{grid-template-columns:1fr}}
.inputs,.results{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px;display:flex;flex-direction:column;gap:14px;min-width:0}
.field{display:flex;flex-direction:column;gap:6px}
.field label{font-size:14.5px;font-weight:500;display:flex;justify-content:space-between;gap:10px}
.field label output{font-family:var(--mono);color:var(--accent);font-weight:600}
.field input[type=range]{width:100%;accent-color:var(--accent)}
.field small{color:var(--faint);font-size:12.5px}
.res{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.res div{background:var(--panel);padding:14px 16px;display:flex;flex-direction:column;gap:4px}
.res .n{font:800 30px/1 var(--display);font-stretch:110%;font-variant-numeric:tabular-nums}
.res .l{font-size:13.5px;color:var(--muted)}
.res .n.acc{color:var(--accent)}
.kpis td:first-child{font-weight:600}
.decisions{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
.decisions div{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;display:flex;flex-direction:column;gap:6px}
.decisions p{color:var(--muted);font-size:15px}
"""
brief_body = """
<header>
  <p class="eyebrow acc">Executive brief · 5-minute read</p>
  <h1>Ten accounts researched with sources in under three minutes each</h1>
  <p class="lede" style="margin-top:14px">Vim's five sellers need a replenished, prioritized book without hand research. We built the provider engine in Clay and ran ten real organizations through it. Here's what it showed, what it didn't, and what it adds up to at scale.</p>
</header>

<section>
  <div class="sec-head"><p class="eyebrow">What the run proved</p><h2>Five claims, ten accounts, all measured</h2></div>
  <div class="claims">
    <div class="claim"><span class="pill p-go">Proven</span><div><h3>Shared domains don't cause bad matches</h3><p>Elevance Health and LifeStance each share a domain with other Clay companies (the legacy Anthem page, two small LifeStance practice pages). Every account was pinned to one company ID and LinkedIn page, and all ten matched.</p></div></div>
    <div class="claim"><span class="pill p-go">Proven</span><div><h3>AI runs only where there's a gap, and only with a source</h3><p>Payers skipped research entirely. The five providers were researched only for the fields still missing. Two EHR answers were only a patient-portal brand (athenahealth for VillageMD, AdvancedMD for LifeStance), and the rules correctly refused to count them.</p></div></div>
    <div class="claim"><span class="pill p-signal">Partly proven</span><div><h3>The EHR question gets a sourced answer</h3><p>Three of five providers came back with evidence: Oak Street runs its own platform, Canopy; One Medical runs its own, 1Life; DaVita cites Epic, backed by an open "Epic Analyst II" role. VillageMD and LifeStance stay unknown until a stronger source turns up.</p></div></div>
    <div class="claim"><span class="pill p-review">Not yet</span><div><h3>Accounts land in a tier</h3><p>All ten sit in Review. Providers score 70 of 100 but can't tier until Vim publishes which EHRs it supports, and payers have no scorecard yet. That's the rules working as designed: unknown never counts as a yes.</p></div></div>
    <div class="claim"><span class="pill p-review">Not yet</span><div><h3>Why-now can be trusted as-is</h3><p>On review, three of the five provider "latest events" weren't buying triggers. The right signals were in the data (DaVita's Humana partnership, Oak Street's five informatics and population-health roles), so this is a ranking fix, not a data gap.</p></div></div>
  </div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">At scale · editable model</p><h2>What it costs to run, and the research time it replaces</h2>
  <p>Credits per account are measured on this run. Everything else is an example assumption. The guide warns against pricing all 81,000 call-reported accounts, so the default is the 1,000-record provider cohort. Set the inputs to Vim's own numbers and the model updates.</p></div>
  <div class="calc">
    <form class="inputs" id="calcform" onsubmit="return false">
      <div class="field"><label for="accts">Eligible accounts in scope <output id="o_accts"></output></label><input type="range" id="accts" min="100" max="20000" step="100" value="1000"><small>Example: the provider POC cohort. Scope eligible, fresh records, not all 81K.</small></div>
      <div class="field"><label for="mins">Manual research minutes per account <output id="o_mins"></output></label><input type="range" id="mins" min="5" max="120" step="5" value="30"><small>Example: finding footprint, EHR, parent and recent news by hand</small></div>
      <div class="field"><label for="refresh">Refreshes per year <output id="o_refresh"></output></label><input type="range" id="refresh" min="1" max="12" step="1" value="4"><small>Example: quarterly re-score</small></div>
      <div class="field"><label for="rate">Loaded seller cost per hour <output id="o_rate"></output></label><input type="range" id="rate" min="30" max="200" step="5" value="85"><small>Example</small></div>
      <div class="field"><label for="cpc">Price per data credit <output id="o_cpc"></output></label><input type="range" id="cpc" min="0.01" max="0.10" step="0.005" value="0.05"><small>Example rate. Actions priced at $0.008 each. AI model usage isn't broken out in the run log.</small></div>
    </form>
    <div class="results" aria-live="polite">
      <span class="eyebrow">Per year</span>
      <div class="res">
        <div><span class="n acc" id="r_hours"></span><span class="l">seller research hours handed to the engine</span></div>
        <div><span class="n" id="r_fte"></span><span class="l">of Vim's five sellers' time, at 1,800 hours each</span></div>
        <div><span class="n" id="r_manual"></span><span class="l">cost of that research by hand</span></div>
        <div><span class="n" id="r_clay"></span><span class="l">Clay data and action cost to run it</span></div>
      </div>
      <p class="muted" style="font-size:14px" id="r_line"></p>
      <p class="muted" style="font-size:13px">Measured: 7.5 data credits and about 5.4 actions per provider account. Excludes the Clay platform subscription, contact sourcing (not built yet) and any pipeline upside.</p>
    </div>
  </div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">The needle</p><h2>Metrics to hold the engine to in a pilot</h2>
  <p>The middle column is measured on this run. Targets are ours to agree with Daryl and Raveed after they see the sample.</p></div>
  <div class="tablewrap kpis"><table><thead><tr><th>Metric</th><th>Why it matters</th><th>This run (n = 10)</th><th>Pilot target</th></tr></thead><tbody>
  <tr><td>Time to a scored account</td><td>Sellers sell instead of researching</td><td class="mono">7–8 s payer · 59 s–2 m 38 s provider</td><td>Under 5 min, fully automated</td></tr>
  <tr><td>EHR evidence coverage</td><td>EHR compatibility decides fit for Vim</td><td class="mono">3 / 5 providers, each sourced</td><td>Agree after the 50-record test</td></tr>
  <tr><td>Footprint freshness</td><td>Stale counts misrank accounts</td><td class="mono">3 / 5 counts older than 2 years</td><td>Every count dated within 12 months</td></tr>
  <tr><td>Signal precision</td><td>Sellers stop trusting a noisy queue</td><td class="mono">1 of 4 provider events relevant</td><td>≥80% relevant on human review</td></tr>
  <tr><td>Identity accuracy</td><td>Parent and site records must not collapse</td><td class="mono">10 / 10 pinned · 1 stale parent</td><td>0 wrong merges; ambiguous goes to review</td></tr>
  <tr><td>Buying-committee coverage</td><td>Multi-threaded deals close more often</td><td class="mono">Not built yet</td><td>≥70% of Tier 1 with 2+ personas verified</td></tr>
  <tr><td>Seller-ready accounts</td><td>The number that pays for it</td><td class="mono">0 · waiting on EHR list and contacts</td><td>Baseline against Vim's current research time</td></tr>
  </tbody></table></div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Next phase</p><h2>Four decisions for Vim</h2></div>
  <div class="decisions">
    <div><h3>Publish the supported-EHR list</h3><p>It's the 30-point criterion and the only thing keeping the five providers out of a tier. Epic, Canopy and 1Life are already on the table.</p></div>
    <div><h3>Decide what happens to payers</h3><p>Enterprise is about 90% outbound. Either give payers their own scorecard, or keep this engine to providers and route payers straight to sellers.</p></div>
    <div><h3>Pick a footprint source</h3><p>No structured action in this workspace returns clinic counts, so research filled them and found 2020 figures. Choose a source and a freshness rule.</p></div>
    <div><h3>Approve contacts and HubSpot</h3><p>Next come the buying committee (up to three personas, five contacts per account) and the HubSpot connection, with writes held until the 50-record test passes.</p></div>
  </div>
</section>
"""
brief_js = """<script>
(function(){
  var DATA=7.5, ACTIONS=5.4, APRICE=0.008;
  function $(i){return document.getElementById(i);}
  function money(n){return n>=1e6?'$'+(n/1e6).toFixed(1)+'M':n>=1e3?'$'+Math.round(n/1e3)+'K':'$'+Math.round(n);}
  function num(n){return n>=1e4?Math.round(n/1e3)+'K':Math.round(n).toLocaleString();}
  function calc(){
    var a=+$('accts').value,m=+$('mins').value,r=+$('refresh').value,rate=+$('rate').value,cpc=+$('cpc').value;
    $('o_accts').textContent=a.toLocaleString();$('o_mins').textContent=m+' min';$('o_refresh').textContent=r+'×';$('o_rate').textContent='$'+rate;$('o_cpc').textContent='$'+cpc.toFixed(3);
    var per=DATA*cpc+ACTIONS*APRICE,runs=a*r,hours=runs*m/60,manual=hours*rate,clay=runs*per;
    $('r_hours').textContent=num(hours);$('r_fte').textContent=Math.round(hours/(5*1800)*100)+'%';$('r_manual').textContent=money(manual);$('r_clay').textContent=money(clay);
    $('r_line').textContent=runs.toLocaleString()+' account runs a year at $'+per.toFixed(2)+' each, against '+money(manual)+' of seller time.';
  }
  ['accts','mins','refresh','rate','cpc'].forEach(function(i){$(i).addEventListener('input',calc);});calc();
})();
</script>"""
page("brief", "Vim Executive Brief", brief_css, brief_body, brief_js)

# ---------------------------------------------------------------- ENGINE
engine_css = """
.stages{display:flex;flex-direction:column;gap:14px}
.stage{display:grid;grid-template-columns:200px minmax(0,1fr);gap:20px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
@media (max-width:760px){.stage{grid-template-columns:1fr}}
.stage .hd{display:flex;flex-direction:column;gap:6px}
.stage .letter{font:800 30px/1 var(--display);color:var(--accent);font-stretch:112%}
.stage .body{display:flex;flex-direction:column;gap:10px;min-width:0}
.nodes{display:flex;flex-wrap:wrap;gap:6px}
.node{font:500 12px/1.2 var(--mono);padding:6px 8px;border-radius:6px;border:1px solid var(--line);background:var(--panel-2)}
.node.code{border-color:transparent;background:var(--accent-soft);color:var(--accent)}
.node.ai{border-color:transparent;background:var(--review-soft);color:var(--review)}
.saw{font-size:14.5px;border-top:1px dashed var(--line-2);padding-top:10px}
.saw b{font-family:var(--mono);font-weight:600;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);margin-right:6px}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:13.5px;color:var(--muted);margin-bottom:14px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:12px;height:12px;border-radius:3px;display:inline-block}
.catch{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.catch .box.bad{border-left:3px solid var(--stop)} .catch .box.good{border-left:3px solid var(--go)}
"""
stages = [
    ("A", "Identity", [("01 Normalize + identity check", "code")],
     "Ten rows in, ten pinned to a Clay company ID and LinkedIn page. <code>elevancehealth.com</code> also resolves to the legacy Anthem entity, and <code>lifestance.com</code> to two small practice pages. Neither domain decided the match."),
    ("B", "Native enrichment", [("02 Clay: enrich company", ""), ("03 HG Insights: website tech stack", ""),
                                ("04 HG Insights: corporate structure", ""), ("05 PredictLeads: company news", ""),
                                ("06 Clay: IT / VBC job openings, 90 d", "")],
     "Five catalog actions, no AI. HG returned 146 web technologies for UnitedHealthcare and a full corporate tree for all ten. PredictLeads returned up to 100 news events per account. Oak Street had five informatics and population-health openings, DaVita four."),
    ("C", "Evidence rules", [("07 Extract EHR / parent / M&A evidence", "code")],
     "A vendor dictionary checks installs for 25 EHR and 10 portal brands. None matched on any account, because web tech data doesn't see clinical systems. Parent comes from the root of the HG tree. M&amp;A and expansion events are kept for 365 days."),
    ("D", "Research gate", [("08 Needs healthcare fallback?", "code")],
     "A rule, not a model: identity-matched providers with an unresolved EHR, parent or location count go to research. All five providers went; all five payers skipped it."),
    ("E", "Gap research", [("09 Claygent: healthcare gap research", "ai")],
     "Researches only the missing fields and must return a URL and quote for each. It found evidence-backed EHRs for three providers and refused to turn two portal brands into an EHR."),
    ("F", "Reconcile + score", [("10 Reconcile + score + why-now", "code")],
     "Structured data wins over research. A research value counts only with a source URL, and a disagreement goes to Review. Providers scored 70, payers 10, and all ten landed in Review."),
]
def _nodes(nodes):
    return "".join('<span class="node %s">%s</span>' % (c, e(n)) for n, c in nodes)


stage_html = "".join(
    f'<div class="stage"><div class="hd"><span class="letter">{L}</span><h3>{t}</h3></div><div class="body">'
    f'<div class="nodes">{_nodes(nodes)}</div>'
    f'<p class="saw"><b>Across the ten</b>{saw}</p></div></div>'
    for L, t, nodes, saw in stages)
engine_body = f"""
<header>
  <p class="eyebrow acc">The engine · how it works</p>
  <h1>One workflow, ten steps, ten accounts followed end to end</h1>
  <p class="lede" style="margin-top:14px">This is Vim's provider account workflow as built in Clay, stage by stage, with what it found at each step. Catalog data and plain code do most of the work. One AI step fills gaps it's handed, and it can't change a score.</p>
</header>

<section>
  <div class="stats">
    <div class="stat"><span class="n">1:28</span><span class="l">for DaVita, from a CSV row to a scored, sourced record; payers finish in about 7 seconds</span></div>
    <div class="stat"><span class="n">7.5<small>credits</small></span><span class="l">data credits per provider run; 6.5 per payer run, which skips research</span></div>
    <div class="stat"><span class="n">1<small>/ 10</small></span><span class="l">steps use AI; the other nine are catalog actions or plain code</span></div>
    <div class="stat"><span class="n">25<small>runs</small></span><span class="l">to get ten clean results. Fifteen failed on three build bugs, now fixed (below)</span></div>
  </div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">The six stages</p><h2>What each stage does, and what it saw</h2></div>
  <div class="legend"><span><i class="sw" style="background:var(--panel-2);border:1px solid var(--line)"></i>Clay catalog action</span><span><i class="sw" style="background:var(--accent-soft)"></i>Deterministic code or rule</span><span><i class="sw" style="background:var(--review-soft)"></i>AI (narrow, cited)</span></div>
  <div class="stages">{stage_html}</div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">What the test caught</p><h2>Three build bugs and two data problems</h2>
  <p>Testing ten records before a thousand is the point of the 10 → 50 → cohort plan. Each of these would have cost a full batch at scale.</p></div>
  <div class="tablewrap"><table><thead><tr><th>Found</th><th>Effect</th><th>Fix</th></tr></thead><tbody>
  <tr><td>Job search limit set to 25; the action accepts 1–10</td><td>All ten first-batch runs failed at step 06</td><td><span class="pill p-go">Fixed</span> Limit set to 10</td></tr>
  <tr><td>HG returns the parent in a tree, not the company list</td><td>Parent would have read "unknown" on every account</td><td><span class="pill p-go">Fixed</span> Parent read from the tree root</td></tr>
  <tr><td>An empty location count was typed as a number</td><td>The five payer runs failed at the final step</td><td><span class="pill p-go">Fixed</span> Blank now allowed; payers re-run</td></tr>
  <tr><td>HG lists Oak Street as its own parent; Clay's company record says "part of CVS Health"</td><td>Structured data won, so research never checked it</td><td><span class="pill p-review">To do</span> Cross-check HG against the seed parent hint</td></tr>
  <tr><td>The newest news item wins the why-now slot</td><td>DaVita surfaced a charity grant over a Humana partnership</td><td><span class="pill p-review">To do</span> Rank by category, confidence and event date</td></tr>
  </tbody></table></div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Scoring rules, in the open</p><h2>Placeholder provider scorecard</h2>
  <p>These weights are the guide's illustrative model, versioned <span class="mono">provider-v0-placeholder</span>. They're not Vim's agreed ICP. Unknown is never scored as a no; it keeps the account in Review.</p></div>
  <div class="tablewrap"><table><thead><tr><th>Criterion</th><th class="num">Weight</th><th>Rule</th><th>This run</th></tr></thead><tbody>
  <tr><td>Supported EHR confirmed</td><td class="num">30</td><td>EHR in Vim's supported list</td><td class="muted">Unknown on all ten. The list is empty until Vim confirms it</td></tr>
  <tr><td>Approved organization type</td><td class="num">25</td><td>Primary care network, multi-site group or specialty network</td><td class="muted">Yes on all five providers (from research)</td></tr>
  <tr><td>Target specialty</td><td class="num">20</td><td>Primary care, multi-specialty, behavioral health, nephrology</td><td class="muted">Yes on all five providers</td></tr>
  <tr><td>Target footprint</td><td class="num">15</td><td>50+ care locations, with a source</td><td class="muted">Yes on all five, though three counts date from 2020–2023</td></tr>
  <tr><td>Target geography</td><td class="num">10</td><td>US</td><td class="muted">Yes on all ten</td></tr>
  </tbody><tfoot><tr><td>fit_score</td><td class="num">100</td><td colspan="2" class="muted">Providers 70 · payers 10 (no payer scorecard yet)</td></tr></tfoot></table></div>
  <p class="muted" style="margin-top:12px;font-size:14px">Tiers: excluded organization or unsupported EHR → Excluded; unknown identity or a missing required field → Review; all required fields known and fit ≥80 → Tier 1; 60–79 → Tier 2; otherwise Tier 3.</p>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Built, designed, and not yet connected</p><h2>What's left before this runs on Vim's book</h2></div>
  <div class="tablewrap"><table><thead><tr><th>Piece</th><th>State</th><th>What it needs</th></tr></thead><tbody>
  <tr><td>Buying committee + verified email</td><td><span class="pill p-review">Designed</span></td><td>Scoped people search per validated company, up to three personas and five contacts per account; managed email routine; only verified emails pass.</td></tr>
  <tr><td>Signals: NewHire, JobPost, News, JobChange</td><td><span class="pill p-review">Designed</span></td><td>Pick the populations and cadence; create them paused; review default confidence filters before resuming.</td></tr>
  <tr><td>Weekly net-new provider discovery</td><td><span class="pill p-review">Designed</span></td><td>Native company search on the agreed criteria, excluding CRM accounts, capped at 50 new organizations a week.</td></tr>
  <tr><td>HubSpot lookup + writeback</td><td><span class="pill p-review">Not connected</span></td><td>Connect Vim's HubSpot, map real properties, update known companies by ID first, create net-new only after duplicate checks.</td></tr>
  <tr><td>Structured footprint source</td><td><span class="pill p-review">Open</span></td><td>No catalog action returns clinic counts. Choose a source (for example an NPI registry via HTTP) and a freshness rule.</td></tr>
  </tbody></table></div>
  <p class="muted" style="margin-top:12px;font-size:14px">Workflow: <a href="{WF_URL}">{WF_ID}</a> in the Clay Demos (GTM) workspace. Draft, unpublished, with no schedule or live trigger. HubSpot writes were never connected.</p>
</section>
"""
page("engine", "Vim Account Engine", engine_css, engine_body)

# ---------------------------------------------------------------- DOSSIER (DaVita)
d = BY["DaVita Kidney Care"]
record = {
    "account": {"name": "DaVita Kidney Care", "domain": "davita.com", "clay_company_id": "14405981",
                "linkedin": d["company_linkedin_url"], "identity_status": "matched"},
    "segment": "provider",
    "fit": {"score": 70, "tier": "Review", "missing_required": "supported_ehr",
            "reasons": d["score_reasons"], "score_version": d["score_version"]},
    "footprint": {"location_count": 3166, "as_of": d["location_count_as_of"], "source": d["location_evidence_url"]},
    "ehr": {"vendor": d["ehr_vendor"], "source": d["ehr_source"], "evidence_url": d["ehr_evidence_url"],
            "quote": d["ehr_evidence_quote"],
            "corroboration": "Open role 'Epic Analyst II', Denver CO, posted 2026-09-26",
            "review_flag": "Evidence names DaVita Physician Solutions' CKD EHR, not the dialysis operations EHR"},
    "parent": {"name": d["parent_company"], "source": "HG Insights corporate tree",
               "research_check": d["parent_evidence_url"]},
    "signals": {"engine_pick": {"type": "invests_into", "date": "2026-09-09", "review": "not a buying trigger"},
                "strongest_on_review": {"type": "partners_with", "date": "2026-08-25", "confidence": 0.9772,
                                        "summary": "Value-based partnership with Humana for chronic kidney disease",
                                        "url": "https://newsroom.davita.com/2026-08-25-davita-announces-new-value-based-partnership-with-humana-to-expand-care-for-patients-with-chronic-kidney-disease"},
                "it_vbc_jobs_90d": 4},
    "workflow_run_id": d["workflow_run_id"],
}
DAV_EVENTS = [
    ("2026-08-25", "p-go", "VBC partnership", "DaVita announces a value-based partnership with Humana to expand care for chronic kidney disease", "0.98", "https://newsroom.davita.com/2026-08-25-davita-announces-new-value-based-partnership-with-humana-to-expand-care-for-patients-with-chronic-kidney-disease", "Strongest trigger"),
    ("2026-02-02", "p-go", "Strategic investment", "Elara Caring secures new strategic investment from Ares and DaVita", "0.92", "https://newsroom.davita.com/2026-02-02-elara-caring-secures-new-strategic-investment-from-ares-and-davita", "Relevant: home care expansion"),
    ("2026-01-27", "p-signal", "Partnership", "Puget Sound Kidney Centers and DaVita worked with Comagine Health and Phreesia on patient activation", "0.91", "https://comagine.org/article/harnessing-patient-activation-dialysis-care", "Relevant: patient engagement tooling"),
    ("2026-09-09", "p-stop", "Investment (charity)", "DaVita Giving Foundation's $1M, four-year commitment to KaBoom!", "0.64", "https://www.csr-company.com/blog/commitment-helping-communities-thrive-davita-community-care-report-2025", "Engine's pick · not a trigger"),
]
DAV_JOBS = [
    ("Epic Analyst II", "Denver, CO", "2026-09-26", "https://www.linkedin.com/jobs/view/epic-analyst-ii-at-davita-kidney-care-4436768999"),
    ("Value Based Care, Sr Analyst", "Denver, CO", "2026-09-27", "https://www.linkedin.com/jobs/view/value-based-care-sr-analyst-at-davita-kidney-care-4436773849"),
    ("Manager, Value-Based Care, Strategic Payor Account Management", "Denver, CO", "2026-09-21", "https://www.linkedin.com/jobs/view/manager-value-based-care-strategic-payor-account-management-at-davita-kidney-care-4469947187"),
    ("Market Director of Operations (Value Based Care, OH / PA)", "Cincinnati, OH", "2026-09-09", "https://www.linkedin.com/jobs/view/market-director-of-operations-value-based-care-oh-pa-at-davita-kidney-care-4465348912"),
]
dossier_css = """
.hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(280px,.9fr);gap:28px;align-items:start}
@media (max-width:860px){.hero{grid-template-columns:1fr}}
.hero .lede{margin-top:14px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.chart{background:var(--paper);border:1px solid var(--line);border-radius:6px;box-shadow:var(--shadow);font-family:var(--mono);font-size:13.5px;overflow:hidden}
.chart .band{background:var(--accent);color:var(--paper);padding:10px 18px;font:700 12px var(--mono);letter-spacing:.14em;text-transform:uppercase;display:flex;justify-content:space-between;gap:10px}
.chart .inner{padding:16px 18px 18px;display:flex;flex-direction:column}
.chart .row{display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px dotted var(--perf)}
.chart .row span:last-child{text-align:right;font-weight:600;font-variant-numeric:tabular-nums}
.chart .big{font:800 44px/1 var(--display);font-stretch:112%;color:var(--accent)}
.chart .total{display:flex;justify-content:space-between;align-items:end;padding-top:12px}
.chart .motion{margin-top:14px;padding:10px 12px;background:var(--review-soft);color:var(--review);font:600 13px/1.4 var(--sans);border-radius:6px}
pre.json{margin:0;padding:16px;overflow-x:auto;font:12.5px/1.55 var(--mono);background:var(--panel-2);border-radius:10px;border:1px solid var(--line);max-height:420px}
.copy{align-self:flex-start;font:600 13px var(--sans);padding:8px 12px;border-radius:7px;border:1px solid var(--line-2);background:var(--panel);color:var(--ink);cursor:pointer}
.copy:hover{border-color:var(--accent);color:var(--accent)}
"""
ev_rows = "".join(
    f'<tr><td class="mono">{dt}</td><td><span class="pill {pc}">{e(t)}</span></td><td>{e(s)}</td>'
    f'<td class="num">{c}</td><td>{a(u)}</td><td class="muted">{e(rv)}</td></tr>'
    for dt, pc, t, s, c, u, rv in DAV_EVENTS)
job_rows = "".join(f'<tr><td>{e(t)}</td><td>{e(l)}</td><td class="mono">{dt}</td><td>{a(u, "LinkedIn")}</td></tr>'
                   for t, l, dt, u in DAV_JOBS)
dossier_body = f"""
<header class="hero">
  <div>
    <p class="eyebrow acc">Account dossier · one provider record</p>
    <h1>DaVita Kidney Care</h1>
    <p class="lede">The largest footprint in the test: 3,166 dialysis centers at the end of 2024. In the last six weeks it signed a value-based-care partnership with Humana and opened an Epic analyst role. This is everything the engine produced for it, including where a person should step in.</p>
    <div class="chips">
      <span class="pill p-review">Fit 70 · Review</span>
      <span class="pill p-signal">EHR: Epic, needs confirming</span>
      <span class="pill p-go">Humana VBC partnership · Aug 25</span>
      <span class="pill p-acc">HubSpot not connected</span>
    </div>
  </div>
  <aside class="chart" aria-label="Account summary">
    <div class="band"><span>Account chart</span><span>davita.com</span></div>
    <div class="inner">
      <div class="row"><span>Segment</span><span>Provider · nephrology</span></div>
      <div class="row"><span>Type</span><span>Specialty provider network</span></div>
      <div class="row"><span>Centers</span><span>3,166 · Dec 31 2024</span></div>
      <div class="row"><span>EHR</span><span>Epic (review)</span></div>
      <div class="row"><span>Parent</span><span>DaVita Inc.</span></div>
      <div class="total"><span>FIT SCORE</span><span class="big">70</span></div>
      <div class="row"><span>Missing</span><span>supported_ehr</span></div>
      <div class="row"><span>Run</span><span>1 m 28 s · 7.5 cr</span></div>
      <div class="motion">Review: tiers as soon as Vim confirms Epic support</div>
    </div>
  </aside>
</header>

<section>
  <div class="sec-head"><p class="eyebrow">What a seller does with it</p><h2>Lead with the Humana partnership</h2></div>
  <div class="grid2">
    <div class="box"><span class="eyebrow">Suggested next action · once tiered</span><p>Open with DaVita's August 25 value-based partnership with Humana. More payer-provider programs mean more point-of-care workflow inside Epic, which is where Vim sits. Confirm the Epic footprint on the first call. The "Epic Analyst II" and three value-based-care roles are the people building it.</p><p class="muted" style="font-size:13.5px">Written by hand from the record for this page. The engine's own why-now template picked the charity grant, which is the ranking fix listed on The Engine page.</p></div>
    <div class="box"><span class="eyebrow">Why it's not tiered yet</span><p>Four of five criteria pass for 70 points. The 30-point EHR criterion is unknown because Vim hasn't published its supported list. If Epic is on it, DaVita moves to Tier 1 at 100.</p><span class="eyebrow" style="margin-top:6px">Cross-account note</span><p>Humana is one of the ten seed accounts. A partnership between two accounts in Vim's book is worth a coordinated play across the payer and provider sellers.</p></div>
  </div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Fit · deterministic, 0–100</p><h2>Why it scores 70</h2>
  <p>Code sets the score from the criterion flags. The research step supplied organization type and footprint, each with a source, and can't change the weights.</p></div>
  <div class="tablewrap"><table><thead><tr><th>Criterion</th><th class="num">Weight</th><th class="num">Scored</th><th>Evidence</th></tr></thead><tbody>
  <tr><td>Supported EHR confirmed</td><td class="num">30</td><td class="num"><b>0</b></td><td class="muted">Epic found, but the supported list is empty, so it stays unknown</td></tr>
  <tr><td>Approved organization type</td><td class="num">25</td><td class="num"><b>+25</b></td><td class="muted">Specialty provider network (research)</td></tr>
  <tr><td>Target specialty</td><td class="num">20</td><td class="num"><b>+20</b></td><td class="muted">Nephrology; dialysis</td></tr>
  <tr><td>Target footprint (50+ locations)</td><td class="num">15</td><td class="num"><b>+15</b></td><td class="muted">3,166 centers, {a(d["location_evidence_url"], "Q4 2024 results")}</td></tr>
  <tr><td>Target geography</td><td class="num">10</td><td class="num"><b>+10</b></td><td class="muted">Denver, CO</td></tr>
  </tbody><tfoot><tr><td>fit_score</td><td class="num">100</td><td class="num">70</td><td class="muted">Tier held at Review while a required field is unknown</td></tr></tfoot></table></div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Timing · reviewed by hand</p><h2>What changed in the last year</h2>
  <p>PredictLeads returned ten M&amp;A and partnership events for the last 365 days. Here are the four that matter, including the one the engine picked and shouldn't have.</p></div>
  <div class="tablewrap"><table><thead><tr><th>Found</th><th>Type</th><th>What happened</th><th class="num">Conf.</th><th>Source</th><th>Review</th></tr></thead>
  <tbody>{ev_rows}</tbody></table></div>
  <div class="tablewrap" style="margin-top:14px"><table><thead><tr><th>Open role · last 90 days</th><th>Location</th><th>Posted</th><th>Link</th></tr></thead><tbody>{job_rows}</tbody></table></div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Record · structured first, research for gaps</p><h2>What the engine knows, and from where</h2></div>
  <div class="grid2">
    <div class="box">
      <div class="fact"><span class="k">Identity</span><span class="v"><span>DaVita Kidney Care · Clay 14405981</span><span><span class="tag det">pinned</span> {a(d["company_linkedin_url"], "LinkedIn")}</span></span></div>
      <div class="fact"><span class="k">EHR</span><span class="v"><span>Epic</span><span><span class="tag ai">research</span> {a(d["ehr_evidence_url"])}</span><span class="muted" style="font-size:13.5px">"CKD EHR by Epic", "Built in partnership with Epic"</span></span></div>
      <div class="fact"><span class="k">Portal</span><span class="v"><span class="muted">Not established</span></span></div>
      <div class="fact"><span class="k">Parent</span><span class="v"><span>DaVita Inc.</span><span><span class="tag det">HG Insights</span> <span class="tag ai">research agrees</span> {a(d["parent_evidence_url"], "SEC 10-K")}</span></span></div>
      <div class="fact"><span class="k">Centers</span><span class="v"><span>3,166 · as of Dec 31 2024</span><span><span class="tag ai">research</span> {a(d["location_evidence_url"])}</span></span></div>
      <div class="fact"><span class="k">Employees</span><span class="v"><span>40,410 on LinkedIn</span><span><span class="tag det">Clay</span> <span class="muted">Headcount isn't used for footprint</span></span></span></div>
    </div>
    <div class="box">
      <span class="eyebrow">Flag for the seller</span>
      <p>The Epic source is DaVita Physician Solutions' CKD EHR, a product DaVita offers nephrology practices. It doesn't name the system its dialysis centers run. The open "Epic Analyst II" role in Denver is independent support. Confirm before counting it.</p>
      <span class="eyebrow" style="margin-top:8px">Buyers</span>
      <p>Not sourced yet; contact sourcing is the next build step. The guide's persona hypotheses for a large provider are IT / CIO, clinical or digital transformation, population health / value-based care, and operations. The four open roles above point at the value-based-care and informatics teams.</p>
    </div>
  </div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">Destination · writes disabled</p><h2>The record, ready for HubSpot</h2>
  <p>Nothing was written to HubSpot. This is the object the workflow holds for DaVita, plus the review notes from this page.</p></div>
  <div class="box"><pre class="json" id="obj">{e(json.dumps(record, indent=1))}</pre><button class="copy" id="copybtn" type="button">Copy JSON</button></div>
</section>
"""
dossier_js = """<script>
(function(){var b=document.getElementById('copybtn');if(!b)return;b.addEventListener('click',function(){var t=document.getElementById('obj').textContent;
function sel(){var r=document.createRange();r.selectNodeContents(document.getElementById('obj'));var s=window.getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selected, press Ctrl/Cmd+C';}
try{navigator.clipboard.writeText(t).then(function(){b.textContent='Copied';},sel);}catch(e){sel();}});})();
</script>"""
page("dossier", "DaVita Account Dossier", dossier_css, dossier_body, dossier_js)

# ---------------------------------------------------------------- REFERENCE (all ten, interactive)
ref_data = []
for r in ROWS:
    rv = EVENT_REVIEW.get(r["company_name"])
    ref_data.append({
        "name": r["company_name"], "segment": r["segment"], "domain": r["company_domain"],
        "linkedin": r["company_linkedin_url"], "employees": r["clay_employee_count"], "industry": r["clay_industry"],
        "tier": r["fit_tier"], "fit": r["fit_score"], "reasons": r["score_reasons"],
        "missing": r["missing_required_fields"], "orgType": r["org_type"],
        "ehr": r["ehr_vendor"], "ehrSource": r["ehr_source"], "ehrUrl": r["ehr_evidence_url"], "ehrQuote": r["ehr_evidence_quote"],
        "portal": r["portal_vendor_clue"], "parent": r["parent_company"], "parentSource": r["parent_source"],
        "parentUrl": r["parent_evidence_url"], "locs": r["location_count"], "locsAsOf": r["location_count_as_of"],
        "locsUrl": r["location_evidence_url"], "evType": r["latest_event_type"], "evDate": r["latest_event_date"],
        "evSummary": r["latest_event_summary"], "evUrl": r["latest_event_url"], "evCount": r["ma_expansion_events_365d"],
        "jobs": r["digital_it_vbc_jobs_90d"], "research": r["research_status"], "notes": r["ai_uncertainty_notes"],
        "run": r["workflow_run_id"], "dur": DUR.get(r["company_name"], "7–8 s"),
        "review": ({"cls": rv[0], "label": rv[1], "text": rv[2]} if rv else None),
    })
ref_css = """
.seg{display:inline-flex;border:1px solid var(--line-2);border-radius:8px;overflow:hidden;margin-bottom:14px}
.seg button{font:600 13px var(--sans);padding:8px 14px;border:0;background:var(--panel);color:var(--muted);cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--accent-soft);color:var(--accent)}
.seg button+button{border-left:1px solid var(--line-2)}
.layout{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:16px;align-items:start}
@media (max-width:900px){.layout{grid-template-columns:1fr}}
.layout>*{min-width:0}
tbody tr.row{cursor:pointer}
tbody tr.row:hover td{background:var(--panel-2)}
tbody tr.row[aria-selected="true"] td{background:var(--accent-soft)}
tbody tr.row td:first-child{font-weight:600}
.sub{display:block;font:12px var(--mono);color:var(--faint);font-weight:400}
#detail{position:sticky;top:calc(env(safe-area-inset-top, 0px) + 12px)}
#detail h3{font-size:22px;font-weight:800;font-stretch:106%}
.kv{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.kv div{background:var(--panel);padding:10px 12px;display:flex;flex-direction:column;gap:2px;min-width:0}
.kv b{font:800 20px/1.1 var(--display);font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.kv span{font:600 10.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.note{font-size:13.5px;color:var(--muted);background:var(--panel-2);border-radius:8px;padding:10px 12px}
.prod td:first-child{color:var(--muted)}
.arrow{color:var(--faint);font-family:var(--mono)}
"""
ref_body = """
<header>
  <p class="eyebrow acc">Account reference · all ten</p>
  <h1>Ten accounts, every value with its source</h1>
  <p class="lede" style="margin-top:14px">Five payers and the five provider groups Vim's ICP is modeled on, exactly as the workflow left them. Where a source said nothing, the field stays empty with a note, and nothing is averaged or guessed. Select an account to see what's behind it.</p>
</header>

<section>
  <div class="seg" role="group" aria-label="Filter by segment">
    <button type="button" id="f_all" data-f="all" aria-pressed="true">All 10</button>
    <button type="button" id="f_provider" data-f="provider" aria-pressed="false">Providers (5)</button>
    <button type="button" id="f_payer" data-f="payer" aria-pressed="false">Payers (5)</button>
  </div>
  <div class="layout">
    <div class="tablewrap"><table><thead><tr><th>Account</th><th class="num">Fit</th><th>EHR</th><th class="num">Locations</th><th>Parent</th></tr></thead><tbody id="rows"></tbody></table></div>
    <aside class="box" id="detail" aria-live="polite"></aside>
  </div>
</section>

<section>
  <div class="grid2">
    <div class="box"><h3>Every value carries its source</h3><p class="muted">Each research value is stored with its URL, a short quote and its date. A research value without a URL is dropped. Where structured data and research disagree, both are kept and the account goes to Review.</p></div>
    <div class="box"><h3>The same input always gives the same answer</h3><p class="muted">Identity, the research gate, evidence extraction, reconciliation and scoring are rules, not judgment calls. Two people reviewing the same account see the same score, and any tier can be explained after the fact.</p></div>
  </div>
</section>

<section>
  <div class="sec-head"><p class="eyebrow">What production looks like</p><h2>What changes when this runs on Vim's book</h2>
  <p>Each hand step in this run has a production equivalent, and swapping one in doesn't mean rebuilding the workflow.</p></div>
  <div class="tablewrap prod"><table><thead><tr><th>In this POC</th><th></th><th>In Vim's hands</th></tr></thead><tbody>
  <tr><td>Ten example logos in a CSV</td><td class="arrow">→</td><td>The 1,000-record provider cohort, then weekly net-new discovery capped at 50</td></tr>
  <tr><td>Placeholder scorecard, empty EHR list</td><td class="arrow">→</td><td>Vim's approved criteria, versioned, with separate payer and provider scorecards</td></tr>
  <tr><td>Footprint from research, some counts from 2020</td><td class="arrow">→</td><td>A structured footprint source with a 12-month freshness rule</td></tr>
  <tr><td>Newest news item wins the why-now</td><td class="arrow">→</td><td>Ranked by category and confidence; deduped; one seller task per account per week</td></tr>
  <tr><td>Results exported to CSV</td><td class="arrow">→</td><td>HubSpot updates by company ID, net-new created only after duplicate checks</td></tr>
  <tr><td>No contacts</td><td class="arrow">→</td><td>Buying committee for Tier 1 accounts, verified emails only</td></tr>
  </tbody></table></div>
</section>
"""
ref_js = "<script>\nvar DATA=" + json.dumps(ref_data).replace("</", "<\\/") + ";\n" + r"""
(function(){
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function link(u,t){if(!u)return '';var h=u.split('/')[2]||u;return '<a href="'+esc(u)+'">'+esc(t||h)+'</a>';}
  var rows=document.getElementById('rows'),det=document.getElementById('detail'),filter='all',sel=DATA.findIndex(function(d){return d.name==='DaVita Kidney Care';});
  function tag(src){return src==='structured'?'<span class="tag det">structured</span>':src==='research_with_evidence'?'<span class="tag ai">research</span>':src==='conflict'?'<span class="tag warn">conflict</span>':'';}
  function renderRows(){
    rows.innerHTML=DATA.map(function(d,i){
      if(filter!=='all'&&d.segment!==filter)return '';
      return '<tr class="row" tabindex="0" data-i="'+i+'" aria-selected="'+(i===sel)+'"><td>'+esc(d.name)+'<span class="sub">'+esc(d.segment)+' · '+esc(d.domain)+'</span></td><td class="num">'+d.fit+'</td><td>'+(esc(d.ehr)||'<span class="muted">unknown</span>')+'</td><td class="num">'+(d.locs?Number(d.locs).toLocaleString():'<span class="muted">—</span>')+'</td><td>'+esc(d.parent)+'</td></tr>';
    }).join('');
  }
  function renderDetail(){
    var d=DATA[sel];if(!d){det.innerHTML='';return;}
    var h='<span class="eyebrow">'+esc(d.segment)+' · '+esc(d.domain)+'</span><h3>'+esc(d.name)+'</h3>';
    h+='<div style="display:flex;flex-wrap:wrap;gap:6px"><span class="pill p-review">'+esc(d.tier)+'</span>'+(d.missing?'<span class="pill p-signal">Missing: '+esc(d.missing)+'</span>':'')+'<span class="pill p-acc">'+esc(d.research.replace(/_/g,' '))+'</span></div>';
    h+='<div class="kv"><div><span>Fit</span><b>'+d.fit+'</b></div><div><span>Locations</span><b>'+(d.locs?Number(d.locs).toLocaleString():'—')+'</b></div><div><span>Run</span><b>'+esc(d.dur)+'</b></div></div>';
    h+='<div class="fact"><span class="k">EHR</span><span class="v"><span>'+(esc(d.ehr)||'<span class="muted">Not established</span>')+'</span><span>'+tag(d.ehrSource)+' '+link(d.ehrUrl)+'</span>'+(d.ehrQuote?'<span class="muted" style="font-size:13.5px">'+esc(d.ehrQuote)+'</span>':'')+'</span></div>';
    if(d.portal)h+='<div class="fact"><span class="k">Portal clue</span><span class="v"><span>'+esc(d.portal)+'</span><span class="muted" style="font-size:13px">A clue only, never counted as the EHR</span></span></div>';
    h+='<div class="fact"><span class="k">Parent</span><span class="v"><span>'+esc(d.parent)+'</span><span>'+tag(d.parentSource)+' '+link(d.parentUrl)+'</span></span></div>';
    h+='<div class="fact"><span class="k">Locations</span><span class="v"><span>'+(d.locs?Number(d.locs).toLocaleString()+' · '+esc(d.locsAsOf):'<span class="muted">Not researched (payer)</span>')+'</span><span>'+link(d.locsUrl)+'</span></span></div>';
    h+='<div class="fact"><span class="k">Latest event</span><span class="v">'+(d.evType?'<span><span class="mono">'+esc(d.evDate)+'</span> · '+esc(d.evType.replace(/_/g,' '))+'</span><span class="muted" style="font-size:13.5px">'+esc(d.evSummary)+'</span><span>'+link(d.evUrl)+'</span>':'<span class="muted">None in the last 365 days</span>')+(d.review?'<span><span class="pill '+(d.review.cls==='go'?'p-go':d.review.cls==='stop'?'p-stop':'p-review')+'">'+esc(d.review.label)+'</span> <span class="muted" style="font-size:13.5px">'+esc(d.review.text)+'</span></span>':'')+'</span></div>';
    h+='<div class="fact"><span class="k">Hiring</span><span class="v"><span>'+d.jobs+' IT / informatics / VBC openings, last 90 days</span></span></div>';
    h+='<div class="fact"><span class="k">Score</span><span class="v"><span class="mono" style="font-size:12.5px">'+esc(d.reasons)+'</span></span></div>';
    if(d.notes)h+='<p class="note"><b>Research notes · </b>'+esc(d.notes)+'</p>';
    h+='<p class="muted mono" style="font-size:11.5px">'+esc(d.run)+'</p>';
    det.innerHTML=h;
  }
  function pick(i){sel=i;renderRows();renderDetail();}
  rows.addEventListener('click',function(ev){var tr=ev.target.closest('tr.row');if(tr&&!ev.target.closest('a'))pick(+tr.dataset.i);});
  rows.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){var tr=ev.target.closest('tr.row');if(tr){ev.preventDefault();pick(+tr.dataset.i);}}});
  document.querySelectorAll('.seg button').forEach(function(b){b.addEventListener('click',function(){filter=b.dataset.f;document.querySelectorAll('.seg button').forEach(function(x){x.setAttribute('aria-pressed',String(x===b));});
    if(filter!=='all'&&DATA[sel].segment!==filter){sel=DATA.findIndex(function(d){return d.segment===filter;});}renderRows();renderDetail();});});
  renderRows();renderDetail();
})();
</script>"""
page("reference", "Vim Account Reference", ref_css, ref_body, ref_js)
print("built:", ", ".join(k for k, _ in NAV))
