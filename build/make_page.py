# -*- coding: utf-8 -*-
"""Render the browsable airport intelligence table as a single self-contained HTML page."""
import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda n: json.load(open(os.path.join(BASE,"data",n), encoding="utf-8"))

airports, centers = D("airports.json"), D("buying_centers.json")
match, signals = D("clay_match_quality.json"), None
import csv
signals = list(csv.DictReader(open(os.path.join(BASE,"data","signals.csv"), encoding="utf-8")))

by_dom = {}
for c in centers: by_dom.setdefault(c["airport_domain"], []).append(c)
mq = {m["enrichment_domain"]: m for m in match}
for a in airports:
    a["centers"] = by_dom.get(a["airport_domain"], [])
    m = mq.get(a["enrichment_domain"], {})
    a["match_quality"] = m.get("match_quality","")
    a["match_issue"] = m.get("issue","")
    a["match_action"] = m.get("required_action","")
    a["matched_name"] = m.get("clay_matched_name","")
    a["linkedin_company_url"] = m.get("linkedin_company_url","")
    a["clay_employee_count"] = m.get("clay_employee_count","")
    a["headcount_trustworthy"] = m.get("headcount_trustworthy","")

payload = json.dumps({"airports":airports,"signals":signals,"match":match},
                     ensure_ascii=False, separators=(",",":"))

HTML = r"""<title>Airport Intelligence Table</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Barlow:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#F6F8FA; --surface:#FFFFFF; --surface-2:#EFF3F7; --ink:#15202D; --ink-2:#44576E;
  --muted:#6B7F94; --line:#DAE2EA; --line-strong:#BDCAD6;
  --brand:#1F5573; --brand-ink:#FFFFFF; --accent:#B4711A;
  --r-authority:#1F5573; --r-parent:#6A4C8C; --r-terminal:#B4711A;
  --r-handling:#1B7264; --r-state:#4F5D6E;
  --ok:#1B7264; --warn:#B4711A; --bad:#A33A2E;
  --shadow:0 1px 2px rgba(21,32,45,.06),0 4px 12px rgba(21,32,45,.05);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0E141B; --surface:#171F28; --surface-2:#1E2831; --ink:#E7EDF4; --ink-2:#B4C2D0;
  --muted:#8A9AAB; --line:#28333E; --line-strong:#3A4754;
  --brand:#7FB3D3; --brand-ink:#0E141B; --accent:#E0A758;
  --r-authority:#7FB3D3; --r-parent:#B79BD6; --r-terminal:#E0A758;
  --r-handling:#5FBFAE; --r-state:#93A3B4;
  --ok:#5FBFAE; --warn:#E0A758; --bad:#E4897C;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 4px 14px rgba(0,0,0,.25);
  color-scheme:dark;
}}
:root[data-theme="dark"]{
  --bg:#0E141B; --surface:#171F28; --surface-2:#1E2831; --ink:#E7EDF4; --ink-2:#B4C2D0;
  --muted:#8A9AAB; --line:#28333E; --line-strong:#3A4754;
  --brand:#7FB3D3; --brand-ink:#0E141B; --accent:#E0A758;
  --r-authority:#7FB3D3; --r-parent:#B79BD6; --r-terminal:#E0A758;
  --r-handling:#5FBFAE; --r-state:#93A3B4;
  --ok:#5FBFAE; --warn:#E0A758; --bad:#E4897C;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 4px 14px rgba(0,0,0,.25);
  color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:Barlow,"Helvetica Neue",Arial,sans-serif;font-size:15px;line-height:1.45;
  -webkit-text-size-adjust:100%}
.wrap{max-width:1500px;margin:0 auto;padding-inline:20px;padding-block:0 56px}
h1,h2,h3{font-family:Archivo,"Helvetica Neue",Arial,sans-serif;margin:0;text-wrap:balance}
code,.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
.num{font-variant-numeric:tabular-nums}

header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:30;background:var(--bg);
  border-bottom:1px solid var(--line);padding-block:16px 12px}
.brandrow{display:flex;flex-wrap:wrap;gap:12px 18px;align-items:baseline}
h1{font-size:23px;font-weight:700;letter-spacing:-.015em}
.sub{color:var(--muted);font-size:13.5px;max-width:70ch}

.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:11px 13px}
.tile .v{font-family:Archivo;font-size:25px;font-weight:700;line-height:1.05;letter-spacing:-.02em}
.tile .k{font-size:10.5px;text-transform:uppercase;letter-spacing:.075em;color:var(--muted);margin-top:4px}
.tile.flag .v{color:var(--warn)}

nav.tabs{display:flex;gap:2px;margin-top:16px;border-bottom:1px solid var(--line);overflow-x:auto}
nav.tabs button{appearance:none;background:none;border:0;border-bottom:2px solid transparent;
  font:600 13.5px Archivo,sans-serif;color:var(--muted);padding:9px 13px;cursor:pointer;white-space:nowrap}
nav.tabs button[aria-selected="true"]{color:var(--ink);border-bottom-color:var(--brand)}
nav.tabs button:hover{color:var(--ink-2)}

.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:16px 0 12px}
input[type=search],select{font:400 13.5px Barlow,sans-serif;color:var(--ink);background:var(--surface);
  border:1px solid var(--line-strong);border-radius:7px;padding:7px 10px}
input[type=search]{min-width:210px;flex:1 1 210px;max-width:340px}
.chk{display:inline-flex;gap:6px;align-items:center;font-size:13px;color:var(--ink-2);
  background:var(--surface);border:1px solid var(--line-strong);border-radius:7px;padding:6px 10px;cursor:pointer}
.count{color:var(--muted);font-size:13px;margin-left:auto}
.btn-reset{font:500 13px Barlow,sans-serif;background:none;border:1px solid var(--line-strong);
  border-radius:7px;padding:6px 11px;color:var(--ink-2);cursor:pointer}

.tblwrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line);
  border-radius:10px;box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;min-width:900px}
th,td{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}
thead th{position:sticky;top:0;background:var(--surface-2);font:600 11px Archivo,sans-serif;
  text-transform:uppercase;letter-spacing:.06em;color:var(--ink-2);white-space:nowrap;z-index:2}
thead th.s{cursor:pointer;user-select:none}
thead th.s:hover{color:var(--ink)}
thead th .ar{opacity:.45;font-size:9px;margin-left:3px}
tbody tr.row{cursor:pointer}
tbody tr.row:hover{background:var(--surface-2)}
tbody tr.row.open{background:var(--surface-2)}
td.iata{font-family:"IBM Plex Mono";font-weight:500;font-size:13px;letter-spacing:.02em}
.aname{font-weight:500}
.dom{font-family:"IBM Plex Mono";font-size:11.5px;color:var(--muted);display:block;margin-top:1px}
.pax{font-variant-numeric:tabular-nums;white-space:nowrap}
.pax b{font-weight:600}
.pax i{font-style:normal;color:var(--muted);font-size:11.5px}

.pill{display:inline-block;font:600 10.5px Archivo,sans-serif;text-transform:uppercase;
  letter-spacing:.055em;padding:2.5px 7px;border-radius:999px;white-space:nowrap}
.pill.t1{background:color-mix(in oklab,var(--brand) 16%,transparent);color:var(--brand)}
.pill.t2{background:var(--surface-2);color:var(--ink-2);border:1px solid var(--line)}
.pill.t3{background:transparent;color:var(--muted);border:1px solid var(--line)}
.bc{display:inline-flex;align-items:center;gap:5px;font-variant-numeric:tabular-nums;font-weight:600}
.bc .dot{width:7px;height:7px;border-radius:50%;background:var(--r-terminal)}
.bc.one{font-weight:400;color:var(--muted)}
.bc.one .dot{background:var(--line-strong)}
.flagdot{display:inline-block;font:600 10.5px Archivo,sans-serif;padding:2.5px 7px;border-radius:5px;
  white-space:nowrap;background:color-mix(in oklab,var(--warn) 17%,transparent);color:var(--warn)}
.flagdot.none{background:color-mix(in oklab,var(--bad) 15%,transparent);color:var(--bad)}
.flagdot.ok{background:transparent;color:var(--muted);font-weight:400}
.model{font-size:12.5px;color:var(--ink-2)}

tr.detail>td{background:var(--bg);padding:0 11px 18px;border-bottom:2px solid var(--line-strong)}
.dgrid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:18px;padding-top:4px;align-items:start}
.dsec h3{font:600 11px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);margin-bottom:7px}
.note{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:0 7px 7px 0;padding:9px 11px;font-size:13.5px;color:var(--ink-2)}
.ctable{width:100%;min-width:0;border-collapse:collapse;background:var(--surface);
  border:1px solid var(--line);border-radius:7px;overflow:hidden}
.ctable th,.ctable td{padding:7px 9px;font-size:12.5px;border-bottom:1px solid var(--line)}
.ctable thead th{position:static;font-size:10px}
.ctable tr:last-child td{border-bottom:0}
.role{font:600 10.5px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.role.authority{color:var(--r-authority)} .role.parent{color:var(--r-parent)}
.role.terminal{color:var(--r-terminal)} .role.handling{color:var(--r-handling)}
.role.state{color:var(--r-state)}
.kv{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 12px;font-size:13px}
.kv dt{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em;padding-top:3px}
.kv dd{margin:0;color:var(--ink-2)}
.tags{display:flex;flex-wrap:wrap;gap:4px}
.tag{font-size:11.5px;background:var(--surface);border:1px solid var(--line);
  border-radius:5px;padding:2px 6px;color:var(--ink-2)}
.warnbox{background:color-mix(in oklab,var(--warn) 11%,var(--surface));
  border:1px solid color-mix(in oklab,var(--warn) 34%,var(--line));border-radius:7px;
  padding:9px 11px;font-size:13px;color:var(--ink-2)}
.warnbox.none{background:color-mix(in oklab,var(--bad) 10%,var(--surface));
  border-color:color-mix(in oklab,var(--bad) 32%,var(--line))}
.warnbox b{color:var(--ink);font-weight:600}
.empty{padding:34px 14px;text-align:center;color:var(--muted);font-size:14px}
.legend{display:flex;flex-wrap:wrap;gap:12px;margin:11px 0 0;font-size:12px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:5px}
.legend i{width:8px;height:8px;border-radius:50%;display:inline-block;font-style:normal}
.prio{font:600 10.5px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.prio.Critical{color:var(--bad)} .prio.High{color:var(--warn)}
.prio.Medium{color:var(--ink-2)} .prio.Low{color:var(--muted)}
.fp{color:var(--muted);font-size:12px;font-style:italic}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:16px 18px;box-shadow:var(--shadow);margin-top:14px}
.panel h2{font-size:16px;font-weight:600;margin-bottom:6px}
.panel p{color:var(--ink-2);font-size:13.5px;margin:0 0 10px;max-width:78ch}
@media (max-width:820px){.dgrid{grid-template-columns:1fr}}
@media (max-width:560px){h1{font-size:20px}.wrap{padding-inline:16px}.tile .v{font-size:21px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
:focus-visible{outline:2px solid var(--brand);outline-offset:2px}
</style>

<div class="wrap">
<header class="top">
  <div class="brandrow">
    <h1>Airport Intelligence Table</h1>
    <p class="sub">50 airports keyed on airport domain, with the airport-wide authority separated from terminal operators. Click any row for its buying centers.</p>
  </div>
  <div class="tiles" id="tiles"></div>
  <nav class="tabs" role="tablist">
    <button role="tab" aria-selected="true" data-tab="airports">Airports</button>
    <button role="tab" aria-selected="false" data-tab="centers">Buying centers</button>
    <button role="tab" aria-selected="false" data-tab="signals">Signal dictionary</button>
    <button role="tab" aria-selected="false" data-tab="match">Clay match quality</button>
  </nav>
</header>

<section id="tab-airports">
  <div class="controls">
    <input type="search" id="q" placeholder="Airport, domain, IATA, authority, operator…" aria-label="Search airports">
    <select id="fRegion" aria-label="Region"><option value="">All regions</option></select>
    <select id="fTier" aria-label="Tier"><option value="">All tiers</option></select>
    <select id="fModel" aria-label="Operator model"><option value="">All operator models</option></select>
    <label class="chk"><input type="checkbox" id="fMulti"> Multi-buyer only</label>
    <label class="chk"><input type="checkbox" id="fRisk"> Enrichment risk only</label>
    <button class="btn-reset" id="reset">Reset</button>
    <span class="count" id="count"></span>
  </div>
  <div class="tblwrap">
    <table>
      <thead><tr>
        <th class="s" data-k="iata_code">IATA<span class="ar"></span></th>
        <th class="s" data-k="airport_name">Airport / domain<span class="ar"></span></th>
        <th class="s" data-k="country">Country<span class="ar"></span></th>
        <th class="s" data-k="annual_passengers_m_2024_est">Pax<span class="ar"></span></th>
        <th class="s" data-k="account_tier">Tier<span class="ar"></span></th>
        <th class="s" data-k="operator_model">Operator model<span class="ar"></span></th>
        <th class="s" data-k="buying_center_count">Buyers<span class="ar"></span></th>
        <th class="s" data-k="match_quality">Clay match<span class="ar"></span></th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="legend">
    <span><i style="background:var(--r-authority)"></i>Airport-wide authority</span>
    <span><i style="background:var(--r-parent)"></i>Parent authority</span>
    <span><i style="background:var(--r-terminal)"></i>Terminal operator</span>
    <span><i style="background:var(--r-handling)"></i>Handling / subsidiary</span>
    <span><i style="background:var(--r-state)"></i>State / regulator</span>
  </div>
</section>

<section id="tab-centers" hidden>
  <div class="panel">
    <h2>87 buying centers across 50 airports</h2>
    <p>The airport is the account; the buying center is who signs. Dedupe at the parent — PANYNJ is one buyer behind JFK, LGA and EWR; MWAA is one behind IAD and DCA. And an authority-level contract never implies coverage of a concessionaire's terminal.</p>
  </div>
  <div class="controls">
    <input type="search" id="cq" placeholder="Buying center, airport, domain…" aria-label="Search buying centers">
    <select id="cRole" aria-label="Role"><option value="">All roles</option></select>
    <span class="count" id="ccount"></span>
  </div>
  <div class="tblwrap"><table>
    <thead><tr><th>Airport</th><th>Buying center</th><th>Role</th><th>Asset</th><th>Owns budget for</th><th>Target titles</th></tr></thead>
    <tbody id="cbody"></tbody>
  </table></div>
</section>

<section id="tab-signals" hidden>
  <div class="panel">
    <h2>17 aviation signals</h2>
    <p>Each signal names where it actually surfaces, which buying center usually owns it, and how it produces false positives — a re-posted public-sector requisition and a net-zero pledge both read as intent and neither is a deal.</p>
  </div>
  <div class="tblwrap"><table>
    <thead><tr><th>Signal</th><th>Category</th><th>Priority</th><th>Where it appears</th><th>Detection</th><th>Usual owner</th><th>Why it matters / false positive</th></tr></thead>
    <tbody id="sbody"></tbody>
  </table></div>
</section>

<section id="tab-match" hidden>
  <div class="panel">
    <h2>What Clay returned for all 47 enrichment domains</h2>
    <p>Run live against every unique enrichment domain. 35 matched cleanly, 4 resolved to the wrong company, 8 returned nothing — so 14 of 50 airport rows cannot be enriched by domain alone. The 4 wrong ones are the hazard, because they succeed silently: <code>panynj.gov</code> returns two stale stubs of 58 and 17 employees and it backs the JFK, LGA and EWR rows.</p>
  </div>
  <div class="controls">
    <select id="mQ" aria-label="Match quality"><option value="">All match qualities</option></select>
    <span class="count" id="mcount"></span>
  </div>
  <div class="tblwrap"><table>
    <thead><tr><th>Enrichment domain</th><th>Airports</th><th>Quality</th><th>What Clay matched</th><th>Headcount</th><th>Issue</th><th>Required action</th></tr></thead>
    <tbody id="mbody"></tbody>
  </table></div>
</section>
</div>

<script>
const DATA = __PAYLOAD__;
const A = DATA.airports, S = DATA.signals, MQ = DATA.match;
const esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const uniq = (arr,k) => [...new Set(arr.map(x=>x[k]).filter(Boolean))].sort();

/* ---- tiles ---- */
const multi = A.filter(a=>a.buying_center_count>1).length;
const risk  = A.filter(a=>a.match_quality!=="clean_match").length;
const terms = A.reduce((n,a)=>n+a.centers.filter(c=>c.role.startsWith("Terminal")||c.role.startsWith("Handling")).length,0);
document.getElementById("tiles").innerHTML = [
  ["50","Airports",""],
  [String(A.reduce((n,a)=>n+a.centers.length,0)),"Buying centers",""],
  [String(multi),"With more than one buyer",""],
  [String(terms),"Terminal / handling operators",""],
  [String(risk),"Rows needing a pinned LinkedIn URL","flag"],
  [String(A.filter(a=>a.enrichment_domain_differs==="Yes").length),"Enrich on a different domain","flag"],
].map(([v,k,c])=>`<div class="tile ${c}"><div class="v num">${v}</div><div class="k">${k}</div></div>`).join("");

/* ---- tabs ---- */
const tabs=[...document.querySelectorAll('nav.tabs button')];
tabs.forEach(b=>b.onclick=()=>{
  tabs.forEach(x=>x.setAttribute("aria-selected", String(x===b)));
  ["airports","centers","signals","match"].forEach(t=>
    document.getElementById("tab-"+t).hidden = (t!==b.dataset.tab));
  try{localStorage.setItem("ait.tab",b.dataset.tab)}catch(e){}
});

/* ---- filters ---- */
const el=id=>document.getElementById(id);
const fill=(sel,vals)=>vals.forEach(v=>sel.insertAdjacentHTML("beforeend",`<option value="${esc(v)}">${esc(v)}</option>`));
fill(el("fRegion"),uniq(A,"region")); fill(el("fTier"),uniq(A,"account_tier")); fill(el("fModel"),uniq(A,"operator_model"));
fill(el("cRole"),uniq(DATA.airports.flatMap(a=>a.centers),"role"));
fill(el("mQ"),uniq(MQ,"match_quality"));

let sortK="annual_passengers_m_2024_est", sortDir=-1, open=new Set();

const ROLECLS = r => r.startsWith("Airport-wide")?"authority":r.startsWith("Parent")?"parent"
  :r.startsWith("Terminal")?"terminal":r.startsWith("Handling")?"handling":"state";

function matched(){
  const q=el("q").value.trim().toLowerCase(), r=el("fRegion").value, t=el("fTier").value,
        m=el("fModel").value, mo=el("fMulti").checked, rk=el("fRisk").checked;
  return A.filter(a=>{
    if(r&&a.region!==r) return false;
    if(t&&a.account_tier!==t) return false;
    if(m&&a.operator_model!==m) return false;
    if(mo&&a.buying_center_count<2) return false;
    if(rk&&a.match_quality==="clean_match") return false;
    if(!q) return true;
    return [a.airport_name,a.airport_domain,a.iata_code,a.icao_code,a.city,a.country,
            a.airport_authority_name,a.parent_authority_name,a.terminal_operators,
            a.operator_model,a.enrichment_domain,a.trade_associations]
           .join(" ").toLowerCase().includes(q);
  }).sort((x,y)=>{
    let p=x[sortK],n=y[sortK];
    if(typeof p==="number"||typeof n==="number") return ((p||0)-(n||0))*sortDir;
    return String(p).localeCompare(String(n))*sortDir;
  });
}

function detail(a){
  const rows=a.centers.map(c=>`<tr>
    <td><span class="role ${ROLECLS(c.role)}">${esc(c.role)}</span></td>
    <td><b>${esc(c.buying_center_name)}</b><span class="dom">${esc(c.buying_center_domain)}</span></td>
    <td>${esc(c.terminal_or_asset)}</td>
    <td>${esc(c.owns_budget_for)}</td></tr>
    <tr><td></td><td colspan="3" style="color:var(--muted);font-size:12px">Titles: ${esc(c.target_titles)}</td></tr>`).join("");
  const mqCls = a.match_quality==="no_match"?"none":"";
  const mqBox = a.match_quality==="clean_match" ? "" :
    `<div class="warnbox ${mqCls}"><b>${a.match_quality==="no_match"?"No Clay company match":"Clay resolves to the wrong company"}</b><br>
      ${esc(a.match_issue)}<br><b>Action:</b> ${esc(a.match_action)}</div>`;
  return `<tr class="detail"><td colspan="8"><div class="dgrid">
    <div class="dsec">
      <h3>Buying centers (${a.centers.length})</h3>
      <table class="ctable"><thead><tr><th>Role</th><th>Organization</th><th>Asset</th><th>Owns budget for</th></tr></thead><tbody>${rows}</tbody></table>
    </div>
    <div class="dsec">
      <h3>Who owns the systems</h3>
      <div class="note">${esc(a.systems_owner_note)}</div>
      ${mqBox?`<h3 style="margin-top:14px">Enrichment</h3>${mqBox}`:""}
      <h3 style="margin-top:14px">Row reference</h3>
      <dl class="kv">
        <dt>Key</dt><dd class="mono">${esc(a.airport_domain)}</dd>
        <dt>Enrich on</dt><dd class="mono">${esc(a.enrichment_domain)}${a.enrichment_domain_differs==="Yes"?' <span style="color:var(--warn)">(differs)</span>':""}</dd>
        ${a.linkedin_company_url?`<dt>LinkedIn</dt><dd class="mono" style="word-break:break-all">${esc(a.linkedin_company_url)}</dd>`:""}
        ${a.clay_employee_count?`<dt>Clay count</dt><dd>${esc(a.clay_employee_count)}${a.headcount_trustworthy==="No"?' <span style="color:var(--warn)">— do not trust as airport size</span>':""}</dd>`:""}
        <dt>ICAO</dt><dd class="mono">${esc(a.icao_code)}</dd>
        <dt>Language</dt><dd>${esc(a.primary_language)}</dd>
        <dt>Procurement</dt><dd>${esc(a.procurement_system)}</dd>
      </dl>
      <h3 style="margin-top:14px">Associations</h3>
      <div class="tags">${a.trade_associations.split("; ").map(x=>`<span class="tag">${esc(x)}</span>`).join("")}</div>
      <h3 style="margin-top:14px">Publications the agent searches</h3>
      <div class="tags">${a.airport_publications.split("; ").map(x=>`<span class="tag">${esc(x)}</span>`).join("")}</div>
    </div></div></td></tr>`;
}

function render(){
  const rows=matched();
  el("count").textContent=`${rows.length} of ${A.length} airports`;
  el("tbody").innerHTML = rows.length ? rows.map(a=>{
    const isOpen=open.has(a.airport_domain);
    const tierCls=a.account_tier==="Tier 1"?"t1":a.account_tier==="Tier 2"?"t2":"t3";
    const mq=a.match_quality;
    const flag = mq==="clean_match"?'<span class="flagdot ok">clean</span>'
      : mq==="no_match"?'<span class="flagdot none">no match</span>'
      : '<span class="flagdot">wrong company</span>';
    return `<tr class="row ${isOpen?"open":""}" data-d="${esc(a.airport_domain)}">
      <td class="iata">${esc(a.iata_code)}</td>
      <td><span class="aname">${esc(a.airport_name)}</span><span class="dom">${esc(a.airport_domain)}</span></td>
      <td>${esc(a.country)}<span class="dom">${esc(a.region)}</span></td>
      <td class="pax"><b>${a.annual_passengers_m_2024_est}</b><i>M</i></td>
      <td><span class="pill ${tierCls}">${esc(a.account_tier)}</span></td>
      <td class="model">${esc(a.operator_model)}</td>
      <td><span class="bc ${a.buying_center_count>1?"":"one"}"><i class="dot"></i>${a.buying_center_count}</span></td>
      <td>${flag}</td></tr>` + (isOpen?detail(a):"");
  }).join("") : `<tr><td colspan="8" class="empty">No airports match these filters.</td></tr>`;

  el("tbody").querySelectorAll("tr.row").forEach(tr=>tr.onclick=()=>{
    const d=tr.dataset.d; open.has(d)?open.delete(d):open.add(d); render();
  });
  document.querySelectorAll("thead th.s").forEach(th=>{
    th.querySelector(".ar").textContent = th.dataset.k===sortK ? (sortDir>0?"▲":"▼") : "";
    th.onclick=()=>{ if(sortK===th.dataset.k) sortDir*=-1; else {sortK=th.dataset.k; sortDir=1;} render(); };
  });
}

function renderCenters(){
  const q=el("cq").value.trim().toLowerCase(), r=el("cRole").value;
  const all=A.flatMap(a=>a.centers.map(c=>({...c,_a:a})));
  const rows=all.filter(c=>{
    if(r&&c.role!==r) return false;
    if(!q) return true;
    return [c.buying_center_name,c.buying_center_domain,c.airport_name,c.iata_code,
            c.terminal_or_asset,c.target_titles].join(" ").toLowerCase().includes(q);
  });
  el("ccount").textContent=`${rows.length} of ${all.length} buying centers`;
  el("cbody").innerHTML = rows.length ? rows.map(c=>`<tr>
    <td class="iata">${esc(c.iata_code)}<span class="dom">${esc(c.airport_domain)}</span></td>
    <td><b>${esc(c.buying_center_name)}</b><span class="dom">${esc(c.buying_center_domain)}</span></td>
    <td><span class="role ${ROLECLS(c.role)}">${esc(c.role)}</span></td>
    <td>${esc(c.terminal_or_asset)}</td>
    <td style="font-size:12.5px;color:var(--ink-2)">${esc(c.owns_budget_for)}</td>
    <td style="font-size:12.5px;color:var(--muted)">${esc(c.target_titles)}</td></tr>`).join("")
    : `<tr><td colspan="6" class="empty">No buying centers match.</td></tr>`;
}

el("sbody").innerHTML = S.map(s=>`<tr>
  <td><b>${esc(s.signal)}</b></td>
  <td style="font-size:12.5px">${esc(s.category)}</td>
  <td><span class="prio ${esc(s.priority)}">${esc(s.priority)}</span></td>
  <td style="font-size:12.5px;color:var(--ink-2)">${esc(s.where_it_appears)}</td>
  <td style="font-size:12.5px;color:var(--ink-2)">${esc(s.detection_method)}</td>
  <td style="font-size:12.5px;color:var(--ink-2)">${esc(s.buying_center_usually_responsible)}</td>
  <td style="font-size:12.5px;color:var(--ink-2)">${esc(s.why_it_matters)}<br><span class="fp">False positive: ${esc(s.false_positive_warning)}</span></td>
</tr>`).join("");

function renderMatch(){
  const v=el("mQ").value;
  const rows=MQ.filter(m=>!v||m.match_quality===v);
  el("mcount").textContent=`${rows.length} of ${MQ.length} domains`;
  el("mbody").innerHTML=rows.map(m=>{
    const cls=m.match_quality==="clean_match"?"ok":m.match_quality==="no_match"?"none":"";
    return `<tr>
      <td class="mono" style="font-size:12.5px">${esc(m.enrichment_domain)}</td>
      <td class="iata" style="font-size:12px">${esc(m.airports_affected)}</td>
      <td><span class="flagdot ${cls}">${esc(m.match_quality.replace("_"," "))}</span></td>
      <td style="font-size:12.5px">${esc(m.clay_matched_name)||'<span style="color:var(--muted)">—</span>'}</td>
      <td class="num" style="font-size:12.5px">${esc(m.clay_employee_count)||"—"}${m.headcount_trustworthy==="No"&&m.clay_employee_count?' <span style="color:var(--warn)">⚠</span>':""}</td>
      <td style="font-size:12.5px;color:var(--ink-2)">${esc(m.issue)||'<span style="color:var(--muted)">—</span>'}</td>
      <td style="font-size:12.5px;color:var(--ink-2)">${esc(m.required_action)}</td></tr>`;
  }).join("");
}

["q","fRegion","fTier","fModel","fMulti","fRisk"].forEach(id=>{
  el(id).addEventListener("input",()=>{open.clear();render()});
});
el("reset").onclick=()=>{["q","fRegion","fTier","fModel"].forEach(i=>el(i).value="");
  el("fMulti").checked=el("fRisk").checked=false; open.clear(); render();};
["cq","cRole"].forEach(id=>el(id).addEventListener("input",renderCenters));
el("mQ").addEventListener("input",renderMatch);

render(); renderCenters(); renderMatch();
try{const t=localStorage.getItem("ait.tab");
  if(t){const b=tabs.find(x=>x.dataset.tab===t); if(b)b.click();}}catch(e){}
</script>
"""

out = HTML.replace("__PAYLOAD__", payload)
path = os.path.join(BASE,"airport-intelligence-table.html")
open(path,"w",encoding="utf-8").write(out)
print("wrote", path, f"{len(out)/1024:.0f} KB")
