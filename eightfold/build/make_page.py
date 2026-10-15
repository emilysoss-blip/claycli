# -*- coding: utf-8 -*-
"""
Render the Eightfold signal engine as one self-contained HTML page.

The stylesheet is lifted from the airport page's generator (build/make_page.py at the repo
root) so both views share one design system; only Eightfold-specific rules are added here.
"""
import csv, json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)
D = lambda n: json.load(open(os.path.join(BASE, "data", n), encoding="utf-8"))

accounts, divisions = D("accounts.json"), D("divisions.json")
tiers = {t["account_key"]: t for t in D("tiered_accounts.json")}
# Default build is the public one: no names, profile URLs or locations. `--private` renders the
# named version from the gitignored local files, to a gitignored page.
PRIVATE = "--private" in sys.argv
leaders = D("talent_leaders.json" if PRIVATE else "talent_leaders_public.json")
briefs = {b["account_key"]: b for b in D("why_now.json" if PRIVATE else "why_now_public.json")}
match = D("clay_match_quality.json")
signals = list(csv.DictReader(open(os.path.join(BASE, "data", "signals.csv"), encoding="utf-8")))

for a in accounts:
    k = a["account_key"]
    a["tier"] = tiers[k]
    a["brief"] = briefs[k]
    a["entities"] = [d for d in divisions if d["account_key"] == k]
    a["leaders"] = [p for p in leaders if p["account_key"] == k]
    a["qualified"] = sum(p["qualified"] == "yes" for p in a["leaders"])

q = [p for p in leaders if p["qualified"] == "yes"]
stats = {
    "parents": len(accounts),
    "entities_in": sum(d["include_in_cohort"] == "yes" for d in divisions),
    "entities_out": sum(d["include_in_cohort"] == "no" for d in divisions),
    "pinned": sum(a["enrichment_identifier"] != a["account_domain"] for a in accounts),
    "returned": len(leaders),
    "qualified": len(q),
    "q_accounts": len({p["account_key"] for p in q}),
    "review": sum(t["fit_tier"] == "Review" for t in tiers.values()),
    "tasks": sum(b["create_task_now"] == "yes" for b in briefs.values()),
    "signal_led": sum(b["motion"] == "signal-led" for b in briefs.values()),
    "domains": len(match),
    "entities": len(divisions),
    "clean": sum(m["match_class"] == "clean" for m in match),
    "in_division": sum(p["division"] != next(a["account_name"] for a in accounts if a["account_key"] == p["account_key"])
                       and p["division"] not in {d["entity_name"] for d in divisions if d["account_key"] == p["account_key"] and d["role"] == "parent"}
                       for p in q),
}
stats["fit_led"] = stats["parents"] - stats["signal_led"]

payload = json.dumps({"accounts": accounts, "leaders": leaders, "match": match,
                      "signals": signals, "stats": stats}, ensure_ascii=False, separators=(",", ":"))

src = open(os.path.join(ROOT, "build", "make_page.py"), encoding="utf-8").read()
css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)

EXTRA_CSS = r"""
.pill.review{background:color-mix(in oklab,var(--warn) 15%,transparent);color:var(--warn)}
.pill.yes{background:color-mix(in oklab,var(--ok) 16%,transparent);color:var(--ok)}
.pill.no{background:transparent;color:var(--muted);border:1px solid var(--line)}
.pill.sig{background:color-mix(in oklab,var(--brand) 16%,transparent);color:var(--brand)}
.why{font-size:13.5px;color:var(--ink-2);background:var(--surface);border:1px solid var(--line);
  border-left:3px solid var(--brand);border-radius:0 7px 7px 0;padding:9px 11px}
.why.fit{border-left-color:var(--line-strong);color:var(--muted)}
.why a{color:var(--brand)}
.score{font-variant-numeric:tabular-nums;white-space:nowrap}
.score i{font-style:normal;color:var(--muted);font-size:11.5px}
.reason{font-size:12px;color:var(--muted)}
.chk3{font-family:"IBM Plex Mono";font-size:11.5px;white-space:nowrap}
.chk3 .y{color:var(--ok)} .chk3 .u{color:var(--warn)} .chk3 .n{color:var(--bad)}
ol.fixes{margin:6px 0 0;padding-left:20px;color:var(--ink-2);font-size:13.5px;max-width:86ch}
ol.fixes li{margin-bottom:9px}
ol.fixes code{font-size:12px;background:var(--surface-2);padding:1px 4px;border-radius:4px}
td a{color:var(--brand)}
td.num{white-space:nowrap}
/* Seven tiles in a sticky header leave no room for the table on a phone. */
@media (max-width:560px){header.top{position:static}}
"""

HTML = r"""<title>Eightfold Signal Engine</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Barlow:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>__CSS__ __EXTRA__</style>

<div class="wrap">
<header class="top">
  <div class="brandrow">
    <h1>Eightfold Signal Engine</h1>
    <p class="sub">Demand-gen POC on a 30-account stand-in cohort. Parent companies are kept apart from the divisions that hire, tiering is rules-only, and every talent-leader trigger carries its evidence. Live Clay data, 2026-10-15.</p>
  </div>
  <div class="tiles" id="tiles"></div>
  <nav class="tabs" role="tablist">
    <button role="tab" aria-selected="true" data-tab="workflow">Workflow</button>
    <button role="tab" aria-selected="false" data-tab="accounts">Accounts</button>
    <button role="tab" aria-selected="false" data-tab="leaders">Talent leaders</button>
    <button role="tab" aria-selected="false" data-tab="match">Clay match quality</button>
    <button role="tab" aria-selected="false" data-tab="signals">Signals</button>
    <button role="tab" aria-selected="false" data-tab="fixes">Guide corrections</button>
  </nav>
</header>

<section id="tab-workflow">
  <div class="panel">
    <h2>How an account becomes a task</h2>
    <p>Seven stages, all native or rules except one gated AI step. The gates matter more than the stages. Identity decides whether enrichment lands on the right company, and the leader gate decides whether a rep sees a CHRO or an executive assistant.</p>
  </div>
  <figure class="fig">
  <svg class="dgm" viewBox="0 0 880 610" width="880" role="img"
    aria-label="Pipeline: @parents@ parent accounts expand to @entities_in@ in-scope hiring entities; @pinned@ parents need a pinned LinkedIn URL. Native enrichment was dispatched but not read back, so tiering puts @review@ in Review. People search returned @returned@ talent leaders; the rules gate kept @qualified@ at @q_accounts@ accounts, giving @signal_led@ signal-led briefs and @tasks@ task under the 90-day policy.">
    <defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="ah" d="M0,0 L10,5 L0,10 z"/></marker>
          <marker id="ab" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="ah-bad" d="M0,0 L10,5 L0,10 z"/></marker></defs>
    <!-- column 1: account path -->
    <rect class="bx" x="40" y="20" width="360" height="62" rx="8"/>
    <text class="t-h" x="58" y="45">1 · Seed cohort</text>
    <text class="t-s" x="58" y="66">@parents@ parents · stand-in for the Salesforce export · CRM fields blank</text>
    <line class="ln" x1="220" y1="82" x2="220" y2="112" marker-end="url(#a)"/>

    <rect class="bx-key" x="40" y="114" width="360" height="78" rx="8"/>
    <text class="t-h" x="58" y="139">2 · Identity map  (gate)</text>
    <text class="t-s" x="58" y="160">@entities@ entities → @entities_in@ in scope, @entities_out@ suppressed</text>
    <text class="t-s" x="58" y="178">@pinned@ parents enrich on a pinned LinkedIn URL, not the domain</text>
    <line class="ln" x1="220" y1="192" x2="220" y2="222" marker-end="url(#a)"/>
    <path class="ln-bad" d="M400,153 C470,153 470,240 530,240" marker-end="url(#ab)"/>
    <text class="lbl-bad" x="430" y="140">skip the pin →</text>

    <rect class="bx-warn" x="532" y="210" width="320" height="62" rx="8"/>
    <text class="t-h" x="550" y="234">Wrong company, silently</text>
    <text class="t-s" x="550" y="252">marshmclennan.com → a 31-person broker</text>
    <text class="t-s" x="550" y="266">kaiserpermanente.org → two placeholder pages</text>

    <rect class="bx" x="40" y="224" width="360" height="62" rx="8"/>
    <text class="t-h" x="58" y="249">3 · Native enrichment</text>
    <text class="t-s" x="58" y="270">Open Jobs · Tech Stack · Headcount Growth on 11 · read-back failed</text>
    <line class="ln" x1="220" y1="286" x2="220" y2="316" marker-end="url(#a)"/>

    <rect class="bx" x="40" y="318" width="360" height="62" rx="8"/>
    <text class="t-h" x="58" y="343">4 · Fallback gate → Claygent (field-level)</text>
    <text class="t-s" x="58" y="364">only unknown hcm / open_reqs that could move the tier</text>
    <line class="ln" x1="220" y1="380" x2="220" y2="410" marker-end="url(#a)"/>

    <rect class="bx-key" x="40" y="412" width="360" height="62" rx="8"/>
    <text class="t-h" x="58" y="437">5 · Rules tiering</text>
    <text class="t-s" x="58" y="458">@review@ Review · 55 of 100 known · best case 100 · no AI score</text>

    <!-- column 2: people path -->
    <rect class="bx" x="532" y="318" width="320" height="62" rx="8"/>
    <text class="t-h" x="550" y="343">6 · Talent-leader search</text>
    <text class="t-s" x="550" y="364">@returned@ people, started ≤ 18 months, all @parents@ parents</text>
    <line class="ln" x1="692" y1="380" x2="692" y2="410" marker-end="url(#a)"/>
    <rect class="bx-key" x="532" y="412" width="320" height="62" rx="8"/>
    <text class="t-h" x="550" y="437">Leader gate  (rules)</text>
    <text class="t-s" x="550" y="458">@qualified@ qualify at @q_accounts@ accounts · @in_division@ sit in a division</text>

    <line class="ln" x1="220" y1="474" x2="400" y2="534" marker-end="url(#a)"/>
    <line class="ln" x1="692" y1="474" x2="500" y2="534" marker-end="url(#a)"/>
    <rect class="bx-key" x="300" y="536" width="300" height="62" rx="8"/>
    <text class="t-h" x="318" y="561">7 · Why-now brief + task</text>
    <text class="t-s" x="318" y="582">@signal_led@ signal-led · @fit_led@ fit-led · @tasks@ task now (90-day rule)</text>
  </svg>
  <figcaption><b>The dashed path is the failure that never errors.</b> Enriching on the account's domain works cleanly on @clean@ of @domains@ domains. On the rest it returns a different company, a closed page or a member hospital, and the row still fills in. That is why identity is a gate before enrichment, not a cleanup after it.</figcaption>
  </figure>
  <dl class="stepnote">
    <dt>Live</dt><dd>Stages 2, 5, 6 and the leader gate ran on live Clay data. Stage 3 was dispatched and accepted, but every read-back returned <code>Internal error</code>.</dd>
    <dt>Not built</dt><dd>No CLI workflow, signal or segment exists yet; the CLI could not be installed in the build environment. <code>eightfold/clay/runbook.md</code> is the sequence.</dd>
    <dt>Unknown</dt><dd>CRM state (customer, opportunity, owner, suppression), intent (6sense) and engagement (Marketo). None of it is inferred.</dd>
  </dl>
</section>

<section id="tab-accounts" hidden>
  <div class="controls">
    <input type="search" id="q" placeholder="Account, domain, division, title…" aria-label="Search accounts">
    <select id="fV" aria-label="Vertical"><option value="">All verticals</option></select>
    <select id="fM" aria-label="Match status"><option value="">All match statuses</option></select>
    <label class="chk"><input type="checkbox" id="fSig"> Signal-led only</label>
    <span class="count" id="count"></span>
  </div>
  <div class="tblwrap"><table>
    <thead><tr>
      <th class="s" data-k="account_name">Account<span class="ar"></span></th>
      <th class="s" data-k="vertical">Vertical<span class="ar"></span></th>
      <th class="s" data-k="clay_employee_count">Employees<span class="ar"></span></th>
      <th class="s" data-k="hiring_entities_in_scope">Entities<span class="ar"></span></th>
      <th class="s" data-k="domain_match_status">Identity<span class="ar"></span></th>
      <th>Tier</th><th>Fit checks</th>
      <th class="s" data-k="qualified">Leaders<span class="ar"></span></th>
    </tr></thead>
    <tbody id="tbody"></tbody>
  </table></div>
</section>

<section id="tab-leaders" hidden>
  <div class="controls">
    <label class="chk"><input type="checkbox" id="lQ" checked> Qualified only</label>
    <select id="lP" aria-label="Persona"><option value="">All personas</option></select>
    <span class="count" id="lcount"></span>
  </div>
  <div class="tblwrap"><table>
    <thead><tr><th>Leader</th><th>Account / entity</th><th>Started</th><th>Persona</th><th>Level</th><th>Qualified</th><th>Why not</th></tr></thead>
    <tbody id="lbody"></tbody>
  </table></div>
</section>

<section id="tab-match" hidden>
  <div class="panel"><h2>What Clay returns when you enrich by domain</h2>
  <p>__DOMAINS__ domains used by the cohort. Counts are lower bounds where the capture stopped paging. A domain that is not <code>clean</code> is enriched on the hiring entity's LinkedIn URL instead.</p></div>
  <div class="tblwrap" style="margin-top:12px"><table>
    <thead><tr><th>Domain</th><th>Class</th><th>Entities</th><th>Stale</th><th>Finding</th><th>Fix</th></tr></thead>
    <tbody id="mbody"></tbody>
  </table></div>
</section>

<section id="tab-signals" hidden>
  <div class="tblwrap" style="margin-top:16px"><table>
    <thead><tr><th>Eightfold ask</th><th>Clay type</th><th>CLI</th><th>Watches</th><th>Watch out for</th><th>From this build</th></tr></thead>
    <tbody id="sbody"></tbody>
  </table></div>
</section>

<section id="tab-fixes" hidden>
  <div class="panel"><h2>Four guide commands that would break the build</h2>
  <p>Checked against <code>clay-run/agent-plugins</code> at <code>a813258</code>. Citations in <code>eightfold/clay/guide_corrections.md</code>.</p>
  <ol class="fixes">
    <li><b>Enrich-node fields are at <code>$.result.&lt;field&gt;</code>.</b> The guide's <code>$.toolResult.result</code> path resolves to nothing, and <code>graph validate</code> will not catch it.</li>
    <li><b>Signal <code>--input</code> uses <code>segmentIds</code>.</b> The guide's <code>{"audiences":[...]}</code> matches neither the input shape nor the read-back shape <code>input.audiences {segmentIds, entityType}</code>.</li>
    <li><b><code>runs test --trigger &lt;csv&gt; --limit 10</code> runs every row.</b> Use <code>clay workflows triggers csv run &lt;triggerId&gt; --limit 10</code>, and put rows 11–60 in a new file for the 50-row pass, because <code>--limit</code> has no offset.</li>
    <li><b>An unwired CSV trigger accepts <code>csv run</code>, then fails every row.</b> Check the wiring with <code>graph get</code> before the first run.</li>
  </ol>
  <p style="margin-top:10px">The guide asks for #1 and #2 to be copied into the Vim guide as corrections. They should not be.</p></div>
</section>
</div>

<script>
const DATA=__DATA__;
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const el=id=>document.getElementById(id);
const S=DATA.stats, A=DATA.accounts;
const fmt=n=>n===""||n==null?"—":Number(n).toLocaleString("en-US");

el("tiles").innerHTML=[
  [S.parents,"Parent accounts",""],
  [S.entities_in,"Hiring entities in scope",""],
  [S.pinned,"Parents needing a LinkedIn pin","flag"],
  [S.qualified+" / "+S.returned,"Leaders qualified / returned",""],
  [S.q_accounts,"Signal-led accounts",""],
  [S.review,"In Review (hcm, open reqs unknown)","flag"],
  [S.tasks,"Task now (90-day rule)",""],
].map(([v,k,c])=>`<div class="tile ${c}"><div class="v num">${v}</div><div class="k">${k}</div></div>`).join("");

const tabs=[...document.querySelectorAll('nav.tabs button')];
tabs.forEach(b=>b.onclick=()=>{
  tabs.forEach(x=>x.setAttribute("aria-selected",String(x===b)));
  ["workflow","accounts","leaders","match","signals","fixes"].forEach(t=>el("tab-"+t).hidden=(t!==b.dataset.tab));
  try{localStorage.setItem("efse.tab",b.dataset.tab)}catch(e){}
});

const uniq=(xs,k)=>[...new Set(xs.map(x=>x[k]).filter(Boolean))].sort();
const fill=(s,v)=>v.forEach(x=>s.insertAdjacentHTML("beforeend",`<option value="${esc(x)}">${esc(x)}</option>`));
fill(el("fV"),uniq(A,"vertical")); fill(el("fM"),uniq(A,"domain_match_status"));
fill(el("lP"),uniq(DATA.leaders,"persona_group"));

const CHK=t=>["industry","headcount","open_reqs","hcm","geography"].map(k=>{
  const v=t["check_"+k], c=v==="yes"?"y":v==="no"?"n":"u", m=v==="yes"?"✓":v==="no"?"✗":"?";
  return `<span class="${c}" title="${k}: ${v}">${m}${k.replace("_reqs","").slice(0,4)}</span>`}).join(" ");

let sortK="qualified", dir=-1, open=new Set();
function rowsA(){
  const q=el("q").value.trim().toLowerCase(), v=el("fV").value, m=el("fM").value, s=el("fSig").checked;
  return A.filter(a=>(!v||a.vertical===v)&&(!m||a.domain_match_status===m)&&(!s||a.brief.motion==="signal-led")&&
    (!q||[a.account_name,a.account_domain,...a.entities.map(e=>e.entity_name+" "+e.entity_domain),...a.leaders.map(p=>(p.name||"")+" "+p.title)].join(" ").toLowerCase().includes(q)))
   .sort((x,y)=>{const p=x[sortK],n=y[sortK];
     return (typeof p==="number"||typeof n==="number"?(+p||0)-(+n||0):String(p).localeCompare(String(n)))*dir||x.account_name.localeCompare(y.account_name)});
}
function detail(a){
  const ents=a.entities.map(e=>`<tr><td><b>${esc(e.entity_name)}</b><span class="dom">${esc(e.entity_domain)}</span></td>
    <td>${esc(e.role)}</td><td class="num">${fmt(e.clay_employee_count)}</td>
    <td><span class="pill ${e.include_in_cohort}">${e.include_in_cohort==="yes"?"in scope":"suppressed"}</span></td><td class="reason">${esc(e.note)}</td></tr>`).join("");
  const ql=a.leaders.filter(p=>p.qualified==="yes").map(p=>`<li>${p.name?`<a href="${esc(p.linkedin_url)}" target="_blank" rel="noopener">${esc(p.name)}</a> · `:""}${esc(p.title)} · ${esc(p.start)}${p.division!==p.employer_in_clay?` · <b>${esc(p.division)}</b>`:""}</li>`).join("");
  const why=a.brief.motion==="signal-led"
    ? esc(a.brief.why_now).replace(/(https:\/\/www\.linkedin\.com\/in\/[^\s.]+\/?)/,'<a href="$1" target="_blank" rel="noopener">$1</a>')
    : esc(a.brief.why_now);
  return `<tr class="detail"><td colspan="8"><div class="dgrid">
    <div class="dsec"><h3>Hiring entities</h3><table class="ctable"><thead><tr><th>Entity</th><th>Role</th><th>Employees</th><th>Status</th><th>Note</th></tr></thead><tbody>${ents}</tbody></table></div>
    <div class="dsec"><h3>Why now</h3><div class="why ${a.brief.motion==="fit-led"?"fit":""}">${why}</div>
      ${a.brief.create_task_now==="yes"?'<p class="reason" style="margin-top:6px"><b>Task now</b>: event inside the 90-day window.</p>':""}
      ${ql?`<h3 style="margin-top:14px">Qualified leaders</h3><ul style="margin:0;padding-left:18px;font-size:13px;color:var(--ink-2)">${ql}</ul>`:""}
      <h3 style="margin-top:14px">Identity</h3><div class="note">${esc(a.identity_note)}<br><span class="dom">enrich on: ${esc(a.enrichment_identifier)}</span></div>
      <h3 style="margin-top:14px">Tiering</h3><div class="reason mono">${esc(a.tier.score_reasons)} · ${esc(a.tier.score_version)}</div></div>
  </div></td></tr>`;
}
function renderA(){
  const R=rowsA(); el("count").textContent=`${R.length} of ${A.length}`;
  el("tbody").innerHTML=R.map(a=>{
    const t=a.tier, k=a.account_key;
    return `<tr class="row${open.has(k)?" open":""}" data-k="${esc(k)}" tabindex="0">
      <td><span class="aname">${esc(a.account_name)}</span><span class="dom">${esc(a.account_domain)}</span></td>
      <td class="model">${esc(a.vertical)}</td><td class="num">${fmt(a.clay_employee_count)}</td>
      <td><span class="bc ${a.hiring_entities_in_scope>1?"":"one"}"><span class="dot"></span>${a.hiring_entities_in_scope}</span>${a.entities_suppressed?` <span class="reason">+${a.entities_suppressed} suppressed</span>`:""}</td>
      <td><span class="flagdot ${a.domain_match_status==="clean"?"ok":/missing/.test(a.domain_match_status)?"none":""}">${esc(a.domain_match_status.replace(/_/g," "))}</span></td>
      <td><span class="pill review">${esc(t.fit_tier)}</span> <span class="score">${t.fit_score}<i>/${t.fit_best_case}</i></span></td>
      <td class="chk3">${CHK(t)}</td>
      <td>${a.qualified?`<span class="pill sig">${a.qualified} · ${esc(a.brief.latest_event_date)}</span>`:'<span class="reason">fit-led</span>'}</td>
    </tr>${open.has(k)?detail(a):""}`}).join("");
}
el("tbody").addEventListener("click",e=>{const r=e.target.closest("tr.row"); if(!r)return;
  const k=r.dataset.k; open.has(k)?open.delete(k):open.add(k); renderA();});
el("tbody").addEventListener("keydown",e=>{if(e.key==="Enter"){const r=e.target.closest("tr.row"); if(r) r.click();}});
document.querySelectorAll("#tab-accounts th.s").forEach(th=>th.onclick=()=>{
  const k=th.dataset.k; dir=(sortK===k)?-dir:(k==="account_name"||k==="vertical"?1:-1); sortK=k; renderA();});
["q","fV","fM","fSig"].forEach(id=>el(id).addEventListener("input",renderA));

const NAME=Object.fromEntries(A.map(a=>[a.account_key,a.account_name]));
const WHO=x=>x.name?`<a href="${esc(x.linkedin_url)}" target="_blank" rel="noopener">${esc(x.name)}</a><span class="dom">${esc(x.title)}</span>`:`<b>${esc(x.title)}</b>`;
function renderL(){
  const qo=el("lQ").checked, p=el("lP").value;
  const R=DATA.leaders.filter(x=>(!qo||x.qualified==="yes")&&(!p||x.persona_group===p))
    .sort((a,b)=>(a.qualified<b.qualified?1:a.qualified>b.qualified?-1:0)||b.start.localeCompare(a.start));
  el("lcount").textContent=`${R.length} of ${DATA.leaders.length}`;
  el("lbody").innerHTML=R.map(x=>`<tr><td>${WHO(x)}</td>
    <td>${esc(NAME[x.account_key]||"—")}<span class="dom">${esc(x.division)}</span></td><td class="num">${esc(x.start)}</td>
    <td>${esc(x.persona_group.replace(/_/g," "))}</td><td>${esc(x.level)}${x.title_banded==="yes"?' <span class="reason">(banded)</span>':""}</td>
    <td><span class="pill ${x.qualified}">${x.qualified}</span></td><td class="reason">${esc(x.disqualify_reasons)}${/kept/.test(x.us_based)?"based outside US; enterprise exec kept":""}</td></tr>`).join("");
}
["lQ","lP"].forEach(id=>el(id).addEventListener("input",renderL));

el("mbody").innerHTML=DATA.match.slice().sort((a,b)=>(a.match_class==="clean")-(b.match_class==="clean")||a.domain.localeCompare(b.domain))
  .map(m=>`<tr><td class="mono">${esc(m.domain)}</td><td><span class="flagdot ${m.match_class==="clean"?"ok":/wrong|no_usable|missing|stale_parent/.test(m.match_class)?"none":""}">${esc(m.match_class.replace(/_/g," "))}</span></td>
   <td class="num">${esc(m.entities_returned)}${m.count_is_lower_bound==="yes"?"+":""}</td><td class="num">${esc(m.stale_or_inactive_pages)}</td>
   <td class="reason">${esc(m.finding)}</td><td class="reason">${esc(m.fix)}</td></tr>`).join("");

el("sbody").innerHTML=DATA.signals.map(s=>`<tr><td>${esc(s.eightfold_ask)}</td><td class="mono">${esc(s.clay_signal_type)}</td>
  <td>${esc(s.cli_creatable)}</td><td class="reason">${esc(s.watches_by)}</td><td class="reason">${esc(s.false_positive_warning)}</td><td class="reason">${esc(s.evidence_from_this_build)}</td></tr>`).join("");

renderA(); renderL();
try{const t=localStorage.getItem("efse.tab"); if(t){const b=tabs.find(x=>x.dataset.tab===t); if(b)b.click();}}catch(e){}
</script>
"""

html = (HTML.replace("__CSS__", css).replace("__EXTRA__", EXTRA_CSS)
            .replace("__DATA__", payload.replace("</", "<\\/"))
            .replace("__DOMAINS__", str(stats["domains"])))
for k, v in stats.items():
    html = html.replace(f"@{k}@", str(v))
assert "@" not in re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "", re.search(r"<svg.*?</svg>", html, re.S).group(0)), "unfilled token in figure"
path = os.path.join(ROOT, "eightfold-demand-gen-engine" + (".private" if PRIVATE else "") + ".html")
open(path, "w", encoding="utf-8").write(html)
print(f"wrote {path} ({len(html)//1024} KB)")
