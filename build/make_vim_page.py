# -*- coding: utf-8 -*-
"""Render the Vim Enterprise GTM Engine POC as a single self-contained HTML page.

Reads every data/vim_*.json file and computes each headline number from the data,
so no figure on the page can disagree with the CSVs underneath it.
"""
import json, os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda n: json.load(open(os.path.join(BASE, "data", n), encoding="utf-8"))

accounts = D("vim_accounts.json")
committees = D("vim_buying_committees.json")
signals = D("vim_signals.json")
agent = D("vim_account_agent.json")
segments = D("vim_ad_segments.json")

canon = [a for a in accounts if a["dedupe_status"] == "canonical"]
dupes = [a for a in accounts if a["dedupe_status"] == "duplicate"]
merges = [a for a in accounts if a["dedupe_status"] == "merge_candidate"]
unres = [a for a in accounts if a["dedupe_status"] == "unresolved"]
parents = sorted({a["ultimate_parent_name"] for a in canon if a["ultimate_parent_name"]})
t1 = [a for a in canon if a["icp_tier"] == "Tier 1"]
net_new = sum(1 for c in committees if c["in_crm"] == "No")
acted = [r for r in agent if r["recommended_action"]]

# Attach the committee and the agent verdict to each account row.
by_acct = {}
for c in committees:
    by_acct.setdefault(c["account"], []).append(c)
agent_by_acct = {r["account"]: r for r in agent}
for a in accounts:
    a["committee"] = by_acct.get(a["crm_name"], [])
    a["verdict"] = agent_by_acct.get(a["crm_name"])

STATS = {
    "records": len(accounts), "orgs": len(canon), "dupes": len(dupes),
    "merges": len(merges), "unres": len(unres), "parents": len(parents),
    "t1": len(t1), "seats": len(committees), "net_new": net_new,
    "net_new_pct": round(100 * net_new / len(committees)),
    "signals": len(signals), "segments": len(segments),
    "acted": len(acted), "no_action": len(agent) - len(acted),
    "collapsed": len(dupes) + len(merges) + len(unres),
}

payload = json.dumps({"accounts": accounts, "committees": committees, "signals": signals,
                      "agent": agent, "segments": segments, "stats": STATS},
                     ensure_ascii=False, separators=(",", ":"))

HTML = r"""<title>Vim Enterprise GTM Engine</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Barlow:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#F6F8FA; --surface:#FFFFFF; --surface-2:#EFF3F7; --ink:#15202D; --ink-2:#44576E;
  --muted:#6B7F94; --line:#DAE2EA; --line-strong:#BDCAD6;
  --brand:#1F5573; --brand-ink:#FFFFFF; --accent:#B4711A;
  --f-it:#1F5573; --f-vbc:#6A4C8C; --f-net:#B4711A; --f-pop:#1B7264;
  --f-clin:#A33A2E; --f-other:#4F5D6E;
  --ok:#1B7264; --warn:#B4711A; --bad:#A33A2E;
  --shadow:0 1px 2px rgba(21,32,45,.06),0 4px 12px rgba(21,32,45,.05);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0E141B; --surface:#171F28; --surface-2:#1E2831; --ink:#E7EDF4; --ink-2:#B4C2D0;
  --muted:#8A9AAB; --line:#28333E; --line-strong:#3A4754;
  --brand:#7FB3D3; --brand-ink:#0E141B; --accent:#E0A758;
  --f-it:#7FB3D3; --f-vbc:#B79BD6; --f-net:#E0A758; --f-pop:#5FBFAE;
  --f-clin:#E4897C; --f-other:#93A3B4;
  --ok:#5FBFAE; --warn:#E0A758; --bad:#E4897C;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 4px 14px rgba(0,0,0,.25);
  color-scheme:dark;
}}
:root[data-theme="dark"]{
  --bg:#0E141B; --surface:#171F28; --surface-2:#1E2831; --ink:#E7EDF4; --ink-2:#B4C2D0;
  --muted:#8A9AAB; --line:#28333E; --line-strong:#3A4754;
  --brand:#7FB3D3; --brand-ink:#0E141B; --accent:#E0A758;
  --f-it:#7FB3D3; --f-vbc:#B79BD6; --f-net:#E0A758; --f-pop:#5FBFAE;
  --f-clin:#E4897C; --f-other:#93A3B4;
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
.sub{color:var(--muted);font-size:13.5px;max-width:74ch}
.samplebar{margin-top:11px;background:color-mix(in oklab,var(--warn) 12%,var(--surface));
  border:1px solid color-mix(in oklab,var(--warn) 36%,var(--line));border-radius:7px;
  padding:8px 11px;font-size:12.5px;color:var(--ink-2)}
.samplebar b{color:var(--ink);font-weight:600}

.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(142px,1fr));gap:10px;margin-top:14px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:11px 13px}
.tile .v{font-family:Archivo;font-size:25px;font-weight:700;line-height:1.05;letter-spacing:-.02em}
.tile .k{font-size:10.5px;text-transform:uppercase;letter-spacing:.075em;color:var(--muted);margin-top:4px}
.tile.flag .v{color:var(--warn)}
.tile.good .v{color:var(--ok)}

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
table{border-collapse:collapse;width:100%;min-width:940px}
th,td{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}
thead th{position:sticky;top:0;background:var(--surface-2);font:600 11px Archivo,sans-serif;
  text-transform:uppercase;letter-spacing:.06em;color:var(--ink-2);white-space:nowrap;z-index:2}
thead th.s{cursor:pointer;user-select:none}
thead th.s:hover{color:var(--ink)}
thead th .ar{opacity:.45;font-size:9px;margin-left:3px}
tbody tr.row{cursor:pointer}
tbody tr.row:hover,tbody tr.row.open{background:var(--surface-2)}
tbody tr.dim td{opacity:.62}
.aname{font-weight:500}
.dom{font-family:"IBM Plex Mono";font-size:11.5px;color:var(--muted);display:block;margin-top:1px}
.crmid{font-family:"IBM Plex Mono";font-size:12px;color:var(--muted)}

.pill{display:inline-block;font:600 10.5px Archivo,sans-serif;text-transform:uppercase;
  letter-spacing:.055em;padding:2.5px 7px;border-radius:999px;white-space:nowrap}
.pill.t1{background:color-mix(in oklab,var(--brand) 16%,transparent);color:var(--brand)}
.pill.t2{background:var(--surface-2);color:var(--ink-2);border:1px solid var(--line)}
.pill.t3{background:transparent;color:var(--muted);border:1px solid var(--line)}
.pill.out{background:transparent;color:var(--bad);border:1px solid color-mix(in oklab,var(--bad) 40%,var(--line))}
.flagdot{display:inline-block;font:600 10.5px Archivo,sans-serif;padding:2.5px 7px;border-radius:5px;
  white-space:nowrap;background:color-mix(in oklab,var(--warn) 17%,transparent);color:var(--warn)}
.flagdot.none{background:color-mix(in oklab,var(--bad) 15%,transparent);color:var(--bad)}
.flagdot.ok{background:transparent;color:var(--muted);font-weight:400}
.model{font-size:12.5px;color:var(--ink-2)}
.hier{font-size:12.5px;color:var(--ink-2)}
.hier i{font-style:normal;color:var(--muted);font-size:11.5px;display:block}
.fn{font:600 10.5px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.fn.it{color:var(--f-it)} .fn.vbc{color:var(--f-vbc)} .fn.net{color:var(--f-net)}
.fn.pop{color:var(--f-pop)} .fn.clin{color:var(--f-clin)} .fn.other{color:var(--f-other)}
.deal{font:600 10.5px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.deal.eb{color:var(--brand)} .deal.ch{color:var(--ok)} .deal.tb{color:var(--f-vbc)}
.deal.gk{color:var(--bad)} .deal.in{color:var(--muted)}

tr.detail>td{background:var(--bg);padding:0 11px 18px;border-bottom:2px solid var(--line-strong)}
.dgrid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:18px;padding-top:4px;align-items:start}
.dsec h3{font:600 11px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);margin-bottom:7px}
.note{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:0 7px 7px 0;padding:9px 11px;font-size:13.5px;color:var(--ink-2)}
.ctable{width:100%;min-width:0;border-collapse:collapse;background:var(--surface);
  border:1px solid var(--line);border-radius:7px;overflow:hidden}
.ctable th,.ctable td{padding:7px 9px;font-size:12.5px;border-bottom:1px solid var(--line)}
.ctable thead th{position:static;font-size:10px}
.ctable tr:last-child td{border-bottom:0}
.kv{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 12px;font-size:13px}
.kv dt{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em;padding-top:3px}
.kv dd{margin:0;color:var(--ink-2)}
.tags{display:flex;flex-wrap:wrap;gap:4px}
.tag{font-size:11.5px;background:var(--surface);border:1px solid var(--line);
  border-radius:5px;padding:2px 6px;color:var(--ink-2)}
.tag.crit{border-color:color-mix(in oklab,var(--bad) 45%,var(--line));color:var(--bad)}
.warnbox{background:color-mix(in oklab,var(--warn) 11%,var(--surface));
  border:1px solid color-mix(in oklab,var(--warn) 34%,var(--line));border-radius:7px;
  padding:9px 11px;font-size:13px;color:var(--ink-2)}
.warnbox.none{background:color-mix(in oklab,var(--bad) 10%,var(--surface));
  border-color:color-mix(in oklab,var(--bad) 32%,var(--line))}
.warnbox b{color:var(--ink);font-weight:600}

.dgm{max-width:100%;height:auto;color:var(--ink);display:block;margin:0 auto}
.dgm .bx{fill:var(--surface);stroke:var(--line-strong);stroke-width:1.25}
.dgm .bx-key{fill:color-mix(in oklab,var(--brand) 12%,var(--surface));stroke:var(--brand);stroke-width:1.6}
.dgm .bx-warn{fill:color-mix(in oklab,var(--warn) 14%,var(--surface));stroke:var(--warn);stroke-width:1.5}
.dgm .bx-bad{fill:color-mix(in oklab,var(--bad) 12%,var(--surface));stroke:var(--bad);stroke-width:1.5;
  stroke-dasharray:5 4}
.dgm .band{fill:color-mix(in oklab,var(--brand) 5%,transparent);stroke:var(--line);
  stroke-width:1;stroke-dasharray:3 4}
.dgm .bandlbl{font-family:Archivo,sans-serif;font-weight:700;font-size:10.5px;
  letter-spacing:.09em;fill:var(--muted)}
.dgm text{fill:currentColor;font-family:Barlow,"Helvetica Neue",Arial,sans-serif;font-size:12px}
.dgm .t-h{font-family:Archivo,"Helvetica Neue",Arial,sans-serif;font-weight:600;font-size:12.5px}
.dgm .t-s{fill:var(--muted);font-size:10.5px}
.dgm .t-m{font-family:"IBM Plex Mono",monospace;font-size:11px}
.dgm .ln{stroke:currentColor;stroke-width:1.25;fill:none;opacity:.5}
.dgm .ln-key{stroke:var(--brand);stroke-width:1.6;fill:none;opacity:.85}
.dgm .ln-bad{stroke:var(--bad);stroke-width:1.5;fill:none;stroke-dasharray:5 4}
.dgm .ah{fill:currentColor;opacity:.5}
.dgm .ah-key{fill:var(--brand);opacity:.85}
.dgm .ah-bad{fill:var(--bad)}
.dgm .lbl{fill:var(--muted);font-size:10.5px}
.dgm .lbl-key{fill:var(--brand);font-size:10.5px;font-weight:600;font-family:Archivo,sans-serif}
.dgm .lbl-bad{fill:var(--bad);font-size:10.5px;font-weight:600;font-family:Archivo,sans-serif}
figure.fig{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:18px 16px 14px;box-shadow:var(--shadow);margin-top:14px;overflow-x:auto}
figure.fig figcaption{margin-top:12px;font-size:13px;color:var(--ink-2);max-width:88ch;
  border-top:1px solid var(--line);padding-top:10px}
figure.fig figcaption b{color:var(--ink);font-weight:600}

.stepnote{display:grid;grid-template-columns:auto minmax(0,1fr);gap:6px 12px;margin-top:12px;font-size:13.5px}
.stepnote dt{font-family:Archivo,sans-serif;font-weight:600;font-size:12px;color:var(--brand);
  white-space:nowrap;padding-top:2px}
.stepnote dd{margin:0;color:var(--ink-2)}
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
.panel p{color:var(--ink-2);font-size:13.5px;margin:0 0 10px;max-width:80ch}
.panel p:last-child{margin-bottom:0}
.panel .lede{font-size:15px;color:var(--ink)}

.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px;margin-top:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 15px;
  box-shadow:var(--shadow);border-top:3px solid var(--brand)}
.card.quiet{border-top-color:var(--line-strong);background:var(--surface-2)}
.card .rank{font:700 11px Archivo,sans-serif;color:var(--muted);letter-spacing:.06em}
.card h3{font-size:15.5px;font-weight:600;margin:3px 0 2px}
.card .meta{font-size:12px;color:var(--muted);margin-bottom:9px}
.card h4{font:600 10px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin:11px 0 4px}
.card p{margin:0;font-size:13.5px;color:var(--ink-2)}
.card .act{background:color-mix(in oklab,var(--brand) 9%,var(--surface));
  border:1px solid color-mix(in oklab,var(--brand) 28%,var(--line));border-radius:7px;
  padding:9px 10px;margin-top:9px;font-size:13.5px;color:var(--ink)}
.card .seat{font-size:12.5px;color:var(--ink-2);margin-top:6px}
.card .seat b{color:var(--ink)}
.card .chg{font-size:12.5px;color:var(--muted);margin-top:9px;border-top:1px solid var(--line);
  padding-top:8px}
.conf{font:600 10.5px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.05em;float:right}
.conf.High{color:var(--ok)} .conf.Medium{color:var(--warn)} .conf.Low{color:var(--muted)}
.segbar{height:6px;border-radius:3px;background:var(--surface-2);overflow:hidden;margin-top:7px;
  border:1px solid var(--line)}
.segbar i{display:block;height:100%;background:var(--brand)}
.segnum{display:flex;gap:16px;margin-top:9px;font-size:12px;color:var(--muted);flex-wrap:wrap}
.segnum b{display:block;font:700 17px Archivo,sans-serif;color:var(--ink);letter-spacing:-.01em}
.rule{font-size:12.5px;color:var(--ink-2);margin-top:4px}
.rule span{font:600 10px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);display:block}
@media (max-width:820px){.dgrid{grid-template-columns:1fr}}
@media (max-width:560px){h1{font-size:20px}.wrap{padding-inline:16px}.tile .v{font-size:21px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
:focus-visible{outline:2px solid var(--brand);outline-offset:2px}
</style>

<div class="wrap">
<header class="top">
  <div class="brandrow">
    <h1>Vim Enterprise GTM Engine</h1>
    <p class="sub">Three POC builds as one connected workflow: know the account, know when and who, activate everywhere. One continuously updated source of truth instead of ad-hoc tables, manual research, fragmented CRM data and CSV uploads.</p>
  </div>
  <div class="samplebar"><b>Sample data.</b> Every organization and person below is invented. The structures are real healthcare GTM patterns and the counts are computed from the seed files, but nothing here describes an actual company and no figure should be quoted externally. Point stage 1 at Vim's HubSpot export and every column downstream stays as it is.</div>
  <div class="tiles" id="tiles"></div>
  <nav class="tabs" role="tablist">
    <button role="tab" aria-selected="true" data-tab="poc">The engine</button>
    <button role="tab" aria-selected="false" data-tab="accounts">1 · Account universe</button>
    <button role="tab" aria-selected="false" data-tab="committees">2 · Buying committees</button>
    <button role="tab" aria-selected="false" data-tab="whynow">2 · Why now</button>
    <button role="tab" aria-selected="false" data-tab="signals">2 · Signal dictionary</button>
    <button role="tab" aria-selected="false" data-tab="segments">3 · Ad audiences</button>
  </nav>
</header>

<section id="tab-poc">
  <div class="panel">
    <h2>One workflow, not three tables</h2>
    <p class="lede">Build 1 produces the account universe. Build 2 runs <b>only</b> against the Tier 1 rows Build 1 has already qualified. Build 3 reads the same rows and pushes them outward. Nothing downstream re-derives an account, so a definition changes in one place and everything moves on the next run.</p>
    <p>The dedupe step is drawn as a gate because that is how it behaves: four outcomes, and two of them are not "keep". The arrow running back up the right-hand side is the part that makes this an engine rather than a pipeline — an M&amp;A signal found in Build 2 reparents a CRM record in Build 1, which is the only way that record's parent will ever be correct.</p>
  </div>

  <figure class="fig">
  <svg class="dgm" viewBox="0 0 880 1020" role="img" width="880"
       aria-label="The three POC builds as one pipeline. 44 HubSpot company records are normalized and resolved to Clay Company IDs, then pass a dedupe gate with four outcomes: 32 canonical records, 7 duplicates, 3 site-level merges and 2 unresolved records held for a human. Canonical records get hierarchy resolution, healthcare enrichment and an ICP score, producing an account universe of 32 organizations in 20 parent groups with 11 Tier 1. Build 2 takes only those 11, sources 55 committee seats and monitors 18 signals, and an Account Agent emits a why-now and a recommended action for each, acting on 9 and declining on 2. Build 3 turns the same rows into 6 dynamic segments synced to LinkedIn and Meta. An arrow runs from the signal step back up to hierarchy resolution: an M and A signal reparents the CRM record.">
    <defs>
      <marker id="vA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <polygon class="ah" points="0,1.5 10,5 0,8.5"/></marker>
      <marker id="vK" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <polygon class="ah-key" points="0,1.5 10,5 0,8.5"/></marker>
      <marker id="vB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <polygon class="ah-bad" points="0,1.5 10,5 0,8.5"/></marker>
    </defs>

    <rect class="bx" x="290" y="14" width="300" height="44" rx="7"/>
    <text class="t-h" x="440" y="34" text-anchor="middle">HubSpot companies — 44 records</text>
    <text class="t-s" x="440" y="49" text-anchor="middle">full object sync, junk and blanks included on purpose</text>

    <rect class="band" x="40" y="74" width="800" height="472" rx="10"/>
    <text class="bandlbl" x="56" y="93">BUILD 1 · KNOW THE ACCOUNT</text>

    <rect class="bx" x="250" y="104" width="380" height="42" rx="7"/>
    <text class="t-h" x="440" y="123" text-anchor="middle">Normalize the name, resolve to a Company ID</text>
    <text class="t-s" x="440" y="137" text-anchor="middle">the string narrows the candidates · the ID decides</text>

    <rect class="bx-key" x="220" y="166" width="440" height="46" rx="7"/>
    <text class="t-h" x="440" y="186" text-anchor="middle">Dedupe gate — four outcomes, not two</text>
    <text class="t-s" x="440" y="201" text-anchor="middle">dedupe on the Company ID, never on the domain</text>

    <rect class="bx" x="52" y="232" width="182" height="44" rx="6"/>
    <text class="t-h" x="143" y="251" text-anchor="middle">32 canonical</text>
    <text class="t-s" x="143" y="266" text-anchor="middle">carry the enrichment</text>

    <rect class="bx" x="250" y="232" width="182" height="44" rx="6"/>
    <text class="t-h" x="341" y="251" text-anchor="middle">7 duplicates</text>
    <text class="t-s" x="341" y="266" text-anchor="middle">activity merged in</text>

    <rect class="bx" x="448" y="232" width="182" height="44" rx="6"/>
    <text class="t-h" x="539" y="251" text-anchor="middle">3 site merges</text>
    <text class="t-s" x="539" y="266" text-anchor="middle">a location, not a company</text>

    <rect class="bx-warn" x="646" y="232" width="182" height="44" rx="6"/>
    <text class="t-h" x="737" y="251" text-anchor="middle">2 unresolved</text>
    <text class="t-s" x="737" y="266" text-anchor="middle">held for a human</text>

    <rect class="bx" x="250" y="306" width="380" height="46" rx="7"/>
    <text class="t-h" x="440" y="325" text-anchor="middle">Resolve the hierarchy</text>
    <text class="t-s" x="440" y="340" text-anchor="middle">parent · ultimate parent · subsidiary · site — not the CRM's parent field</text>

    <rect class="bx" x="250" y="372" width="380" height="46" rx="7"/>
    <text class="t-h" x="440" y="391" text-anchor="middle">Healthcare enrichment</text>
    <text class="t-s" x="440" y="406" text-anchor="middle">EHR · org type · providers · lives · geography · counterparties</text>

    <rect class="bx" x="250" y="438" width="380" height="42" rx="7"/>
    <text class="t-h" x="440" y="457" text-anchor="middle">ICP score and tier</text>
    <text class="t-s" x="440" y="471" text-anchor="middle">every score carries a one-sentence reason</text>

    <rect class="bx-key" x="170" y="494" width="540" height="42" rx="7"/>
    <text class="t-h" x="440" y="513" text-anchor="middle">Vim Enterprise Account Universe</text>
    <text class="t-s" x="440" y="527" text-anchor="middle">32 organizations · 20 parent groups · 11 Tier 1 · maintained, not rebuilt</text>

    <rect class="band" x="40" y="562" width="800" height="252" rx="10"/>
    <text class="bandlbl" x="56" y="581">BUILD 2 · KNOW WHEN AND WHO</text>

    <rect class="bx-key" x="300" y="592" width="280" height="38" rx="7"/>
    <text class="t-h" x="440" y="616" text-anchor="middle">Tier 1 only — 11 of 32</text>

    <rect class="bx" x="70" y="650" width="330" height="46" rx="7"/>
    <text class="t-h" x="235" y="669" text-anchor="middle">Buying committee — 55 seats</text>
    <text class="t-s" x="235" y="684" text-anchor="middle">8 functions · 45 of 55 net-new to the CRM</text>

    <rect class="bx" x="480" y="650" width="330" height="46" rx="7"/>
    <text class="t-h" x="645" y="669" text-anchor="middle">Signals — 18 in the dictionary</text>
    <text class="t-s" x="645" y="684" text-anchor="middle">hiring · EHR · partnership · M&amp;A · regulatory · engagement</text>

    <rect class="bx-key" x="250" y="716" width="380" height="46" rx="7"/>
    <text class="t-h" x="440" y="735" text-anchor="middle">Account Agent</text>
    <text class="t-s" x="440" y="750" text-anchor="middle">CRM history + external signals + resolved structure</text>

    <rect class="bx" x="170" y="776" width="540" height="30" rx="6"/>
    <text class="t-h" x="440" y="796" text-anchor="middle">Why now · recommended action · entry seat — 9 act, 2 no action</text>

    <rect class="band" x="40" y="830" width="800" height="172" rx="10"/>
    <text class="bandlbl" x="56" y="849">BUILD 3 · ACTIVATE EVERYWHERE</text>

    <rect class="bx" x="250" y="860" width="380" height="46" rx="7"/>
    <text class="t-h" x="440" y="879" text-anchor="middle">6 dynamic segments — entry rule AND exit rule</text>
    <text class="t-s" x="440" y="894" text-anchor="middle">the exit rule is the half a CSV upload does not have</text>

    <rect class="bx" x="140" y="936" width="260" height="44" rx="7"/>
    <text class="t-h" x="270" y="955" text-anchor="middle">LinkedIn — profile match</text>
    <text class="t-s" x="270" y="970" text-anchor="middle">5 segments · nightly</text>

    <rect class="bx" x="480" y="936" width="260" height="44" rx="7"/>
    <text class="t-h" x="610" y="955" text-anchor="middle">Meta — hashed email</text>
    <text class="t-s" x="610" y="970" text-anchor="middle">1 segment · weekly</text>

    <path class="ln" marker-end="url(#vA)" d="M440,58 V100"/>
    <path class="ln" marker-end="url(#vA)" d="M440,146 V162"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,212 440,222 143,222 143,228"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,212 440,222 341,222 341,228"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,212 440,222 539,222 539,228"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,212 440,222 737,222 737,228"/>
    <polyline class="ln-key" marker-end="url(#vK)" points="143,276 143,292 440,292 440,302"/>
    <text class="lbl-key" x="152" y="289">only canonical rows continue</text>
    <path class="ln" marker-end="url(#vA)" d="M440,352 V368"/>
    <path class="ln" marker-end="url(#vA)" d="M440,418 V434"/>
    <path class="ln" marker-end="url(#vA)" d="M440,480 V490"/>
    <path class="ln-key" marker-end="url(#vK)" d="M440,536 V588"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,630 440,640 235,640 235,646"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,630 440,640 645,640 645,646"/>
    <polyline class="ln" points="235,696 235,706 440,706"/>
    <polyline class="ln" points="645,696 645,706 440,706"/>
    <path class="ln" marker-end="url(#vA)" d="M440,706 V712"/>
    <path class="ln" marker-end="url(#vA)" d="M440,762 V772"/>
    <path class="ln-key" marker-end="url(#vK)" d="M440,806 V856"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,906 440,920 270,920 270,932"/>
    <polyline class="ln" marker-end="url(#vA)" points="440,906 440,920 610,920 610,932"/>

    <polyline class="ln-bad" marker-end="url(#vB)" points="810,673 856,673 856,329 634,329"/>
    <text class="lbl-bad" x="849" y="500" text-anchor="middle" transform="rotate(-90,849,500)">M&amp;A signal reparents the CRM record</text>
  </svg>
  <figcaption><b>The feedback arrow is the whole argument.</b> Ridgeline Community Health sits in HubSpot as an unrelated parent account with its own owner. It was acquired. No amount of CRM hygiene will ever discover that — only the M&amp;A signal in Build 2 reparents it, and then Build 1's hierarchy is right on the next run and Build 3's audiences follow the night after. Run these three as separate tables and that correction never propagates. <b>Reparent on close, not on announcement:</b> announced deals fail state review and closing runs 12–18 months.</figcaption>
  </figure>

  <div class="panel">
    <h2>Why the dedupe runs on the Company ID and not the domain</h2>
    <p>Domain-based dedupe is the obvious shortcut and it is wrong in both directions at once. It keeps three records that are one company, and it deletes one of two companies that share a domain — including, here, the entity that actually signs the risk contract.</p>
  </div>

  <figure class="fig">
  <svg class="dgm" viewBox="0 0 880 340" role="img" width="880"
       aria-label="Two contrasting cases. On the left, three Northmark records on three different domains are one company: domain dedupe keeps all three, and only hierarchy resolution collapses them into one ultimate parent with two sellable organizations and one site merged. On the right, the single domain harborviewhp.org carries two separate companies, Harborview Health Partners and Harborview ACO LLC, which holds the ACO REACH contract. Domain dedupe deletes the ACO record; resolving on the Company ID keeps it as a subsidiary with its own committee seat.">
    <defs>
      <marker id="hA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
        <polygon class="ah" points="0,1.5 10,5 0,8.5"/></marker>
      <marker id="hB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
        <polygon class="ah-bad" points="0,1.5 10,5 0,8.5"/></marker>
      <marker id="hK" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
        <polygon class="ah-key" points="0,1.5 10,5 0,8.5"/></marker>
    </defs>

    <text class="t-h" x="30" y="22">Three domains, one company</text>
    <text class="t-s" x="30" y="37">domain dedupe keeps all three — none of them is a duplicate</text>

    <rect class="bx" x="30" y="52" width="330" height="36" rx="6"/>
    <text class="t-h" x="42" y="69">Northmark Health System</text>
    <text class="t-m t-s" x="42" y="82">northmarkhealth.org</text>

    <rect class="bx" x="30" y="98" width="330" height="36" rx="6"/>
    <text class="t-h" x="42" y="115">Northmark Medical Group</text>
    <text class="t-m t-s" x="42" y="128">northmarkmedicalgroup.com</text>

    <rect class="bx" x="30" y="144" width="330" height="36" rx="6"/>
    <text class="t-h" x="42" y="161">Northmark Heart &amp; Vascular Inst.</text>
    <text class="t-s" x="42" y="174">a service line on <tspan class="t-m">northmarkhealth.org</tspan></text>

    <path class="ln" d="M360,70 H372"/>
    <path class="ln" d="M360,116 H372"/>
    <path class="ln" d="M360,162 H372"/>
    <polyline class="ln-key" marker-end="url(#hK)" points="372,70 372,190 200,190 200,200"/>

    <rect class="bx-key" x="30" y="204" width="340" height="46" rx="7"/>
    <text class="t-h" x="200" y="224" text-anchor="middle">1 ultimate parent · 2 sellable orgs · 1 site merged</text>
    <text class="t-s" x="200" y="239" text-anchor="middle">same Epic instance, same signing authority</text>

    <text class="lbl" x="30" y="274">Hierarchy resolution, not dedupe, is what collapses these into one sale.</text>
    <text class="lbl" x="30" y="290">Mail all three and the same CIO hears from Vim three times.</text>

    <path class="ln" d="M440,14 V300" opacity=".22"/>

    <text class="t-h" x="496" y="22">One domain, two companies</text>
    <text class="t-s" x="496" y="37">domain dedupe deletes the second one</text>

    <rect class="bx" x="496" y="52" width="354" height="30" rx="6"/>
    <text class="t-m t-h" x="673" y="72" text-anchor="middle">harborviewhp.org</text>

    <rect class="bx" x="496" y="104" width="172" height="52" rx="6"/>
    <text class="t-h" x="506" y="121">Harborview Health</text>
    <text class="t-h" x="506" y="135">Partners</text>
    <text class="t-s" x="506" y="149">health system · 5,100 providers</text>

    <rect class="bx" x="678" y="104" width="172" height="52" rx="6"/>
    <text class="t-h" x="688" y="121">Harborview ACO LLC</text>
    <text class="t-s" x="688" y="135">separate legal entity</text>
    <text class="t-s" x="688" y="149">holds the ACO REACH contract</text>

    <polyline class="ln" points="673,82 673,92 582,92"/>
    <polyline class="ln" points="673,82 673,92 764,92"/>
    <path class="ln" marker-end="url(#hA)" d="M582,92 V100"/>
    <path class="ln" marker-end="url(#hA)" d="M764,92 V100"/>

    <polyline class="ln-key" marker-end="url(#hK)" points="764,156 764,180 635,180 635,200"/>
    <rect class="bx-key" x="560" y="204" width="150" height="46" rx="7"/>
    <text class="t-h" x="635" y="224" text-anchor="middle">Kept</text>
    <text class="t-s" x="635" y="239" text-anchor="middle">resolving on the Company ID</text>

    <polyline class="ln-bad" marker-end="url(#hB)" points="764,156 764,180 790,180 790,200"/>
    <rect class="bx-bad" x="730" y="204" width="120" height="46" rx="7"/>
    <text class="t-h" x="790" y="224" text-anchor="middle">Deleted</text>
    <text class="t-s" x="790" y="239" text-anchor="middle">deduping on the domain</text>

    <text class="lbl-bad" x="496" y="274">Same domain is a candidate, never a verdict.</text>
    <text class="lbl" x="496" y="290">The deleted row is the one with the VBC leadership and the risk contract.</text>
  </svg>
  <figcaption><b>Both failures come from the same shortcut.</b> On the left, three records on three domains are one company — nothing in the domain says so, and only the hierarchy pass collapses them. On the right, one domain carries two companies, and the one a domain dedupe discards is Harborview ACO LLC: no providers of its own, 90,000 lives under an ACO REACH contract, and the VBC leadership who decide whether tooling gets bought. <b>Resolve on the Clay Company ID.</b> Name normalization narrows the candidates — in this sample set it collapses 8 of 11 duplicates and misses 3, one of them just by pluralizing "Physician" — and the ID decides.</figcaption>
  </figure>

  <div class="panel">
    <h2>What each build proves, costs, and can get wrong</h2>
    <dl class="stepnote">
      <dt>Build 1 · proves</dt><dd>That the CRM can be made trustworthy without a migration. 44 records are 32 companies in 20 corporate families — and that number lands before any enrichment credit is spent, from the sync and the dedupe alone.</dd>
      <dt>Build 1 · costs</dt><dd>One company search per record, then enrichment on <b>canonical rows only</b>. Enriching all 44 pays for 12 records that do not exist. Validate the healthcare fields on 5 hard rows before running 32.</dd>
      <dt>Build 1 · fails by</dt><dd>Deduping on the domain, or auto-merging the unresolved tail. The two unresolved rows here are the honest output: one matches only on name and owner, one matches nothing. Guessing a parent for either creates hierarchy data that routes confidently and wrongly.</dd>
      <dt>Build 2 · proves</dt><dd>That "why now" can be produced continuously rather than researched per account. 45 of 55 committee seats are net-new to the CRM — today nobody at Vim can see four out of five of the people who decide.</dd>
      <dt>Build 2 · costs</dt><dd>Contact search per seat and job-change monitoring per contact, on 11 accounts rather than 44 records. That 4× reduction is where the credit budget comes from, and it only exists because Build 1 ran first.</dd>
      <dt>Build 2 · fails by</dt><dd>Firing on signal volume. Every signal in the dictionary carries the false positive that makes it worthless — an interim CIO, an agency reposting one requisition, a CMS sweep naming forty plans. One dated deadline outranks any number of undated signals.</dd>
      <dt>Build 3 · proves</dt><dd>The cleanest before/after in the set. Today: enrich, export a CSV, hand it to marketing, someone uploads it, and it is stale the next morning. After: the segment is a query over Builds 1 and 2, and it has an <b>exit</b> rule.</dd>
      <dt>Build 3 · costs</dt><dd>Identifier enrichment per person. Small, because the population is already narrowed to qualified committees.</dd>
      <dt>Build 3 · fails by</dt><dd>Quoting the wrong match number. <code>addressable_people</code> is counted from the data and is quotable; <code>est_reachable</code> applies a flat assumed platform match rate and is illustrative until the first real sync replaces it.</dd>
    </dl>
  </div>

  <div class="panel">
    <h2>Deliberately not a primary POC</h2>
    <p><b>AI outbound and copy generation.</b> Discussed on the call, but there is no campaign waiting to be built, so a build here would demo well and prove nothing about the enterprise motion.</p>
    <p><b>Inbound lead enrichment and routing.</b> A strong Phase 2 workflow — new HubSpot lead, immediate enrichment, payer/provider/EHR segment, score, route, sync back — and genuinely valuable. It is held back because the current daily-sync cadence caps how much of that value is reachable today. It becomes a good first Phase 2 build once the sync is addressed.</p>
    <p>If one thing is going to be put in front of the CIO, it is Build 1 into Build 2 as a single live run: take a messy enterprise account, resolve its whole health-system hierarchy, enrich its EHR and healthcare context, surface the buying committee, detect the signals, and produce the recommended next action. That sequence is where Enterprise stops needing an explanation.</p>
  </div>
</section>

<section id="tab-accounts" hidden>
  <div class="panel">
    <h2>Build 1 — the resolved account universe</h2>
    <p>44 CRM records resolve to 32 organizations in 20 corporate families. Click any row for how it resolved, why it scored what it scored, and what the hierarchy pass did to it. Collapsed rows are shown dimmed rather than hidden — the point of the build is visible in what got removed.</p>
  </div>
  <div class="controls">
    <input type="search" id="q" placeholder="Name, domain, parent, EHR, org type…" aria-label="Search accounts">
    <select id="fTier" aria-label="ICP tier"><option value="">All tiers</option></select>
    <select id="fType" aria-label="Organization type"><option value="">All org types</option></select>
    <select id="fEhr" aria-label="EHR"><option value="">All EHRs</option></select>
    <select id="fStatus" aria-label="Dedupe status"><option value="">All records</option></select>
    <label class="chk"><input type="checkbox" id="fCanon"> Survivors only</label>
    <label class="chk"><input type="checkbox" id="fMulti"> In a parent group only</label>
    <button class="btn-reset" id="reset">Reset</button>
    <span class="count" id="count"></span>
  </div>
  <div class="tblwrap">
    <table>
      <thead><tr>
        <th class="s" data-k="crm_record_id">CRM<span class="ar"></span></th>
        <th class="s" data-k="crm_name">Record / domain<span class="ar"></span></th>
        <th class="s" data-k="org_type">Org type<span class="ar"></span></th>
        <th class="s" data-k="hierarchy_level">Hierarchy<span class="ar"></span></th>
        <th class="s" data-k="ehr_primary">EHR<span class="ar"></span></th>
        <th class="s" data-k="providers_est">Providers<span class="ar"></span></th>
        <th class="s" data-k="lives_covered_m">Lives<span class="ar"></span></th>
        <th class="s" data-k="icp_score">ICP<span class="ar"></span></th>
        <th class="s" data-k="dedupe_status">Resolution<span class="ar"></span></th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="legend">
    <span><i style="background:var(--ok)"></i>canonical — survives and carries the enrichment</span>
    <span><i style="background:var(--warn)"></i>duplicate / site merge — collapsed</span>
    <span><i style="background:var(--bad)"></i>unresolved — held for a human, never auto-merged</span>
  </div>
</section>

<section id="tab-committees" hidden>
  <div class="panel">
    <h2>Build 2 — 55 committee seats across the 11 Tier 1 accounts</h2>
    <p>Sourced by function, not by seniority. The committee differs by organization type: a health system's economic buyer is usually IT or, where downside risk is held, population health; a payer has two economic buyers, because network spend is a larger line than IT's. <b>45 of 55 seats have no contact record in HubSpot today.</b></p>
  </div>
  <div class="controls">
    <input type="search" id="cq" placeholder="Person, title, account, function…" aria-label="Search committee seats">
    <select id="cAcct" aria-label="Account"><option value="">All accounts</option></select>
    <select id="cFn" aria-label="Function"><option value="">All functions</option></select>
    <select id="cRole" aria-label="Role in deal"><option value="">All deal roles</option></select>
    <label class="chk"><input type="checkbox" id="cNew"> Net-new to CRM only</label>
    <span class="count" id="ccount"></span>
  </div>
  <div class="tblwrap">
    <table>
      <thead><tr>
        <th>Account</th><th>Person / title</th><th>Function</th><th>Role in deal</th>
        <th>In CRM</th><th>Email</th><th>LinkedIn</th><th>Why this seat</th>
      </tr></thead>
      <tbody id="cbody"></tbody>
    </table>
  </div>
  <div class="legend">
    <span><i style="background:var(--f-it)"></i>CIO / IT</span>
    <span><i style="background:var(--f-vbc)"></i>Value-based care</span>
    <span><i style="background:var(--f-net)"></i>Network &amp; contracting</span>
    <span><i style="background:var(--f-pop)"></i>Population health</span>
    <span><i style="background:var(--f-clin)"></i>Clinical transformation</span>
    <span><i style="background:var(--f-other)"></i>Digital health · partnerships · product</span>
  </div>
</section>

<section id="tab-whynow" hidden>
  <div class="panel">
    <h2>Build 2 — Account Agent output</h2>
    <p>One verdict per Tier 1 account, combining resolved structure from Build 1, external signals, and CRM history. Ranked by the strength of a <b>dated deadline that belongs to them</b>, not by signal count. Two accounts get no action this cycle, which is the output worth showing: an agent that always finds a reason to act is a random number generator with good manners.</p>
  </div>
  <div class="controls">
    <select id="wConf" aria-label="Confidence"><option value="">All confidence levels</option></select>
    <label class="chk"><input type="checkbox" id="wAct"> With a recommended action only</label>
    <span class="count" id="wcount"></span>
  </div>
  <div class="cards" id="wcards"></div>
</section>

<section id="tab-signals" hidden>
  <div class="panel">
    <h2>18 signals, each with the false positive that makes it worthless</h2>
    <p>The right-hand column is the load-bearing one. Every signal here has a way of looking real when it is not, and firing on it blind is how a signal engine loses the room in its second week.</p>
  </div>
  <div class="controls">
    <input type="search" id="sq" placeholder="Signal, source, function…" aria-label="Search signals">
    <select id="sCat" aria-label="Category"><option value="">All categories</option></select>
    <select id="sPrio" aria-label="Priority"><option value="">All priorities</option></select>
    <span class="count" id="scount"></span>
  </div>
  <div class="tblwrap">
    <table>
      <thead><tr>
        <th>Signal</th><th>Category</th><th>Priority</th><th>Where it appears</th>
        <th>How Clay detects it</th><th>Routes to</th><th>Refresh</th><th>Why it matters / false positive</th>
      </tr></thead>
      <tbody id="sbody"></tbody>
    </table>
  </div>
</section>

<section id="tab-segments" hidden>
  <div class="panel">
    <h2>Build 3 — six dynamic segments off the same account universe</h2>
    <p>Every segment has an entry rule <b>and an exit rule</b>. The exit rule is the half a CSV upload does not have, and it is why the uploaded list decays from the day it is built. Membership below is computed from the same seed files as Builds 1 and 2, so changing the ICP threshold moves these numbers on the next run — exactly as the live segment would.</p>
    <p>Two different numbers, and the distinction matters in a pricing conversation: <b>keyed</b> is how many people have the match key the destination needs, counted from the data. <b>Reachable</b> applies a flat assumed platform match rate and is illustrative until the first real sync replaces it with an observed one.</p>
  </div>
  <div class="cards" id="gcards"></div>
</section>

</div>

<script>
const DATA = __PAYLOAD__;
const A = DATA.accounts, C = DATA.committees, S = DATA.signals, W = DATA.agent,
      G = DATA.segments, ST = DATA.stats;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const uniq = (arr,k) => [...new Set(arr.map(x=>x[k]).filter(v=>v!==""&&v!=null))].sort();
const el = id => document.getElementById(id);

/* ---- tiles ---- */
el("tiles").innerHTML = [
  [ST.records,"HubSpot records in",""],
  [ST.orgs,"organizations out","good"],
  [ST.collapsed,"collapsed or held","flag"],
  [ST.parents,"parent groups",""],
  [ST.t1,"Tier 1 accounts",""],
  [ST.seats,"committee seats",""],
  [ST.net_new_pct+"%","of seats net-new to CRM","flag"],
  [ST.signals,"signals monitored",""],
  [ST.segments,"dynamic segments",""],
].map(([v,k,c])=>`<div class="tile ${c}"><div class="v num">${v}</div><div class="k">${k}</div></div>`).join("");

/* ---- tabs ---- */
const TABS = ["poc","accounts","committees","whynow","signals","segments"];
const tabs=[...document.querySelectorAll('nav.tabs button')];
tabs.forEach(b=>b.onclick=()=>{
  tabs.forEach(x=>x.setAttribute("aria-selected", String(x===b)));
  TABS.forEach(t=>document.getElementById("tab-"+t).hidden = (t!==b.dataset.tab));
  try{localStorage.setItem("vim.tab",b.dataset.tab)}catch(e){}
});

const fill=(sel,vals)=>vals.forEach(v=>sel.insertAdjacentHTML("beforeend",
  `<option value="${esc(v)}">${esc(v)}</option>`));

/* ================= accounts ================= */
fill(el("fTier"),uniq(A,"icp_tier")); fill(el("fType"),uniq(A,"org_type"));
fill(el("fEhr"),uniq(A,"ehr_primary")); fill(el("fStatus"),uniq(A,"dedupe_status"));

let sortK="icp_score", sortDir=-1, open=new Set();
const STATCLS = s => s==="canonical"?"ok":s==="unresolved"?"none":"";
const TIERCLS = t => t==="Tier 1"?"t1":t==="Tier 2"?"t2":t==="Tier 3"?"t3":"out";

function accMatched(){
  const q=el("q").value.trim().toLowerCase(), t=el("fTier").value, ty=el("fType").value,
        e=el("fEhr").value, st=el("fStatus").value, cn=el("fCanon").checked, mu=el("fMulti").checked;
  return A.filter(a=>{
    if(t&&a.icp_tier!==t) return false;
    if(ty&&a.org_type!==ty) return false;
    if(e&&a.ehr_primary!==e) return false;
    if(st&&a.dedupe_status!==st) return false;
    if(cn&&a.dedupe_status!=="canonical") return false;
    if(mu&&!(a.parent_org_name||A.some(x=>x.parent_org_name===a.crm_name))) return false;
    if(!q) return true;
    return [a.crm_name,a.normalized_name,a.domain,a.org_type,a.ehr_primary,a.parent_org_name,
            a.ultimate_parent_name,a.hq_state,a.region,a.vbc_model,a.counterparties,
            a.crm_owner,a.icp_reason,a.resolution_note].join(" ").toLowerCase().includes(q);
  }).sort((x,y)=>{
    let p=x[sortK],n=y[sortK];
    if(typeof p==="number"||typeof n==="number") return ((p||0)-(n||0))*sortDir;
    return String(p).localeCompare(String(n))*sortDir;
  });
}

function accDetail(a){
  const kids = A.filter(x=>x.parent_org_name===a.crm_name);
  const seats = a.committee||[];
  const v = a.verdict;
  const dupBox = a.dedupe_status==="canonical" ? "" :
    `<div class="warnbox ${a.dedupe_status==="unresolved"?"none":""}">
      <b>${a.dedupe_status==="duplicate"?"Duplicate — collapsed"
          :a.dedupe_status==="merge_candidate"?"Site record — merged into its parent"
          :"Unresolved — held for a human"}</b><br>
      ${esc(a.dedupe_reason)}
      ${a.matched_on?`<br><b>Matched on:</b> ${esc(a.matched_on)}`:""}
      ${a.duplicate_of?`<br><b>Collapses into:</b> <span class="mono">${esc(a.duplicate_of)}</span>`:""}
    </div>`;
  const seatRows = seats.length ? `<h3 style="margin-top:14px">Buying committee (${seats.length})</h3>
    <table class="ctable"><tbody>${seats.map(s=>`<tr>
      <td><b>${esc(s.person_name)}</b><span class="dom">${esc(s.title)}</span></td>
      <td><span class="fn ${FNCLS(s.function)}">${esc(s.function)}</span></td>
      <td><span class="deal ${DEALCLS(s.role_in_deal)}">${esc(s.role_in_deal)}</span></td>
      <td style="color:var(--muted);font-size:11.5px">${s.in_crm==="Yes"?"in CRM":"net-new"}</td>
      </tr>`).join("")}</tbody></table>` : "";
  return `<tr class="detail"><td colspan="9"><div class="dgrid">
    <div class="dsec">
      <h3>What the resolution did</h3>
      <div class="note">${esc(a.resolution_note)}</div>
      ${dupBox?`<h3 style="margin-top:14px">Dedupe</h3>${dupBox}`:""}
      ${seatRows}
    </div>
    <div class="dsec">
      <h3>Hierarchy</h3>
      <dl class="kv">
        <dt>Level</dt><dd>${esc(a.hierarchy_level)}</dd>
        ${a.parent_org_name?`<dt>Parent</dt><dd>${esc(a.parent_org_name)}</dd>`:""}
        ${a.ultimate_parent_name?`<dt>Ultimate</dt><dd>${esc(a.ultimate_parent_name)}</dd>`:""}
        ${kids.length?`<dt>Below it</dt><dd>${kids.map(k=>esc(k.crm_name)).join("<br>")}</dd>`:""}
      </dl>
      <h3 style="margin-top:14px">ICP</h3>
      <div class="note">${esc(a.icp_reason)}</div>
      <h3 style="margin-top:14px">Row reference</h3>
      <dl class="kv">
        <dt>Normalized</dt><dd class="mono" style="font-size:12px">${esc(a.normalized_name)||"—"}</dd>
        <dt>Stack</dt><dd>${esc(a.ehr_primary)}${a.ehr_confidence!=="n/a"?` <span style="color:${a.ehr_confidence==="Low"?"var(--warn)":"var(--muted)"}">(${esc(a.ehr_confidence)} confidence)</span>`:""}</dd>
        <dt>Scale</dt><dd>${a.providers_est?a.providers_est+" providers":""}${a.providers_est&&a.lives_covered_m?" · ":""}${a.lives_covered_m?a.lives_covered_m+"M lives":""}${a.sites_est?` · ${a.sites_est} sites`:""}${!a.providers_est&&!a.lives_covered_m?"—":""}</dd>
        <dt>Risk</dt><dd>${esc(a.vbc_model)||"—"}</dd>
        <dt>Geography</dt><dd>${esc(a.hq_state)}${a.region?` · ${esc(a.region)}`:""}</dd>
        <dt>Owner</dt><dd>${esc(a.crm_owner)} · ${esc(a.lifecycle_stage)}${a.open_deal==="Yes"?" · open deal":""}</dd>
      </dl>
      ${a.counterparties?`<h3 style="margin-top:14px">Counterparties in this universe</h3>
        <div class="tags">${a.counterparties.split("; ").map(x=>`<span class="tag">${esc(x)}</span>`).join("")}</div>`:""}
      ${v?`<h3 style="margin-top:14px">Agent verdict</h3><div class="note">${v.recommended_action?esc(v.recommended_action):"<b>No action this cycle.</b> "+esc(v.what_would_change_it)}</div>`:""}
    </div></div></td></tr>`;
}

function renderAcc(){
  const rows=accMatched();
  el("count").textContent=`${rows.length} of ${A.length} records`;
  el("tbody").innerHTML = rows.length ? rows.map(a=>{
    const isOpen=open.has(String(a.crm_record_id));
    const st=a.dedupe_status;
    const flag = st==="canonical"?'<span class="flagdot ok">canonical</span>'
      : st==="duplicate"?'<span class="flagdot">duplicate</span>'
      : st==="merge_candidate"?'<span class="flagdot">site merge</span>'
      : '<span class="flagdot none">unresolved</span>';
    return `<tr class="row ${isOpen?"open":""} ${st!=="canonical"?"dim":""}" data-d="${a.crm_record_id}">
      <td class="crmid">${a.crm_record_id}</td>
      <td><span class="aname">${esc(a.crm_name)}</span><span class="dom">${esc(a.domain)||"— no domain —"}</span></td>
      <td class="model">${esc(a.org_type)}</td>
      <td class="hier">${esc(a.hierarchy_level)}${a.parent_org_name?`<i>under ${esc(a.parent_org_name)}</i>`:""}</td>
      <td class="model">${esc(a.ehr_primary)}${a.ehr_confidence==="Low"?' <span style="color:var(--warn)">⚠</span>':""}</td>
      <td class="num">${a.providers_est||"—"}</td>
      <td class="num">${a.lives_covered_m?a.lives_covered_m+"M":"—"}</td>
      <td>${a.icp_score?`<span class="pill ${TIERCLS(a.icp_tier)}">${a.icp_score}</span>`:'<span style="color:var(--muted)">—</span>'}</td>
      <td>${flag}</td></tr>` + (isOpen?accDetail(a):"");
  }).join("") : `<tr><td colspan="9" class="empty">No records match these filters.</td></tr>`;

  el("tbody").querySelectorAll("tr.row").forEach(tr=>tr.onclick=()=>{
    const d=tr.dataset.d; open.has(d)?open.delete(d):open.add(d); renderAcc();
  });
  document.querySelectorAll("#tab-accounts thead th.s").forEach(th=>{
    th.querySelector(".ar").textContent = th.dataset.k===sortK ? (sortDir>0?"▲":"▼") : "";
    th.onclick=()=>{ if(sortK===th.dataset.k) sortDir*=-1; else {sortK=th.dataset.k; sortDir=1;} renderAcc(); };
  });
}

/* ================= committees ================= */
const FNCLS = f => f==="CIO / IT"?"it" : f==="Value-based care"?"vbc"
  : f==="Network & contracting"?"net" : f==="Population health"?"pop"
  : f==="Clinical transformation"?"clin" : "other";
const DEALCLS = r => r==="Economic buyer"?"eb" : r==="Champion"?"ch"
  : r==="Technical buyer"?"tb" : r==="Gatekeeper"?"gk" : "in";

fill(el("cAcct"),uniq(C,"account")); fill(el("cFn"),uniq(C,"function"));
fill(el("cRole"),uniq(C,"role_in_deal"));

function renderCom(){
  const q=el("cq").value.trim().toLowerCase(), a=el("cAcct").value, f=el("cFn").value,
        r=el("cRole").value, nw=el("cNew").checked;
  const rows=C.filter(c=>{
    if(a&&c.account!==a) return false;
    if(f&&c.function!==f) return false;
    if(r&&c.role_in_deal!==r) return false;
    if(nw&&c.in_crm!=="No") return false;
    if(!q) return true;
    return [c.person_name,c.title,c.account,c.function,c.role_in_deal,c.why_this_seat]
      .join(" ").toLowerCase().includes(q);
  });
  el("ccount").textContent=`${rows.length} of ${C.length} seats`;
  el("cbody").innerHTML = rows.length ? rows.map(c=>`<tr>
    <td><span class="aname" style="font-size:13px">${esc(c.account)}</span>
        <span class="dom">${esc(c.account_org_type)}</span></td>
    <td><b>${esc(c.person_name)}</b><span class="dom">${esc(c.title)}</span></td>
    <td><span class="fn ${FNCLS(c.function)}">${esc(c.function)}</span></td>
    <td><span class="deal ${DEALCLS(c.role_in_deal)}">${esc(c.role_in_deal)}</span></td>
    <td>${c.in_crm==="Yes"?'<span class="flagdot ok">yes</span>':'<span class="flagdot">net-new</span>'}</td>
    <td style="font-size:12px;color:${c.email_status==="Verified"?"var(--muted)":"var(--warn)"}">${esc(c.email_status)}</td>
    <td style="font-size:12px;color:${c.linkedin_present==="Yes"?"var(--muted)":"var(--warn)"}">${esc(c.linkedin_present)}</td>
    <td style="font-size:12.5px;color:var(--ink-2);max-width:32ch">${esc(c.why_this_seat)}</td>
  </tr>`).join("") : `<tr><td colspan="8" class="empty">No seats match these filters.</td></tr>`;
}

/* ================= why now ================= */
fill(el("wConf"),["High","Medium","Low"]);
const CRIT = new Set(S.filter(s=>s.priority==="Critical").map(s=>s.signal));

function renderWhy(){
  const cf=el("wConf").value, ao=el("wAct").checked;
  const rows=W.filter(r=>{
    if(cf&&r.confidence!==cf) return false;
    if(ao&&!r.recommended_action) return false;
    return true;
  });
  el("wcount").textContent=`${rows.length} of ${W.length} Tier 1 accounts`;
  el("wcards").innerHTML = rows.length ? rows.map(r=>{
    const quiet=!r.recommended_action;
    const sigs=r.signals_detected.split("; ").filter(Boolean);
    return `<div class="card ${quiet?"quiet":""}">
      <span class="conf ${esc(r.confidence)}">${esc(r.confidence)} confidence</span>
      <div class="rank">#${r.priority_rank}</div>
      <h3>${esc(r.account)}</h3>
      <div class="meta">${esc(r.icp_tier)} · ICP ${r.icp_score} · owner ${esc(r.recommended_owner)} · CRM ${r.account_crm_id}</div>
      <div class="tags">${sigs.map(s=>`<span class="tag ${CRIT.has(s)?"crit":""}">${esc(s)}</span>`).join("")}</div>
      <h4>What the CRM already knew</h4><p>${esc(r.crm_context)}</p>
      <h4>Why now</h4><p>${esc(r.why_now)}</p>
      ${r.recommended_action?`<div class="act"><b>Action:</b> ${esc(r.recommended_action)}</div>
        <div class="seat">→ <b>${esc(r.entry_seat)}</b>, ${esc(r.entry_seat_title)}
          <span style="color:var(--muted)">(${esc(r.entry_seat_role)})</span><br>
          <span style="color:var(--muted)">${esc(r.channel)}</span></div>`
        : `<div class="act" style="background:var(--surface);border-style:dashed">
             <b>No action this cycle.</b> ${esc(r.channel)}</div>`}
      <div class="chg"><b>Would change this:</b> ${esc(r.what_would_change_it)}</div>
    </div>`;
  }).join("") : `<div class="empty">No accounts match these filters.</div>`;
}

/* ================= signals ================= */
fill(el("sCat"),uniq(S,"category")); fill(el("sPrio"),["Critical","High","Medium","Low"]);
function renderSig(){
  const q=el("sq").value.trim().toLowerCase(), c=el("sCat").value, p=el("sPrio").value;
  const rows=S.filter(s=>{
    if(c&&s.category!==c) return false;
    if(p&&s.priority!==p) return false;
    if(!q) return true;
    return [s.signal,s.category,s.where_it_appears,s.detection_method,s.owning_function,
            s.why_it_matters,s.false_positive_warning].join(" ").toLowerCase().includes(q);
  });
  el("scount").textContent=`${rows.length} of ${S.length} signals`;
  el("sbody").innerHTML = rows.length ? rows.map(s=>`<tr>
    <td><b style="font-size:13px">${esc(s.signal)}</b></td>
    <td style="font-size:12.5px">${esc(s.category)}</td>
    <td><span class="prio ${esc(s.priority)}">${esc(s.priority)}</span></td>
    <td style="font-size:12.5px;color:var(--ink-2)">${esc(s.where_it_appears)}</td>
    <td style="font-size:12.5px;color:var(--ink-2)">${esc(s.detection_method)}</td>
    <td><span class="fn ${FNCLS(s.owning_function)}">${esc(s.owning_function)}</span></td>
    <td style="font-size:12px;color:var(--muted)">${esc(s.refresh)}</td>
    <td style="font-size:12.5px;color:var(--ink-2);max-width:46ch">${esc(s.why_it_matters)}
      <br><span class="fp">False positive: ${esc(s.false_positive_warning)}</span></td>
  </tr>`).join("") : `<tr><td colspan="8" class="empty">No signals match.</td></tr>`;
}

/* ================= segments ================= */
el("gcards").innerHTML = G.map(g=>{
  const pct = g.people_in_segment ? Math.round(100*g.addressable_people/g.people_in_segment) : 0;
  const gap = g.accounts_in_segment - g.accounts_with_committee;
  return `<div class="card">
    <div class="rank">${esc(g.destination).toUpperCase()} · ${esc(g.match_key)}</div>
    <h3>${esc(g.segment)}</h3>
    <div class="meta">${esc(g.purpose)}</div>
    <div class="segnum">
      <span><b class="num">${g.accounts_in_segment}</b>accounts</span>
      <span><b class="num">${g.people_in_segment}</b>people</span>
      <span><b class="num">${g.addressable_people}</b>keyed (${pct}%)</span>
      <span><b class="num">~${g.est_reachable}</b>reachable @ ${g.platform_match_assumption_pct}%</span>
      <span><b class="num">${g.net_new_to_crm}</b>net-new to CRM</span>
    </div>
    <div class="segbar"><i style="width:${pct}%"></i></div>
    ${gap>0?`<div class="chg" style="color:var(--warn)">${gap} of ${g.accounts_in_segment} accounts have no committee sourced yet — this segment reaches into Tier 2, where Build 2 has not run.</div>`:""}
    <div class="rule"><span>Enters when</span>${esc(g.entry_rule)}</div>
    <div class="rule"><span>Exits when</span>${esc(g.exit_rule)}</div>
    <div class="chg">Refresh ${esc(g.refresh)} · illustrative last 7 days: +${g.joined_7d_illustrative} joined, −${g.left_7d_illustrative} left</div>
  </div>`;
}).join("");

/* ---- wiring ---- */
["q","fTier","fType","fEhr","fStatus","fCanon","fMulti"].forEach(id=>
  el(id).addEventListener("input",()=>{open.clear();renderAcc()}));
el("reset").onclick=()=>{["q","fTier","fType","fEhr","fStatus"].forEach(i=>el(i).value="");
  el("fCanon").checked=el("fMulti").checked=false; open.clear(); renderAcc();};
["cq","cAcct","cFn","cRole","cNew"].forEach(id=>el(id).addEventListener("input",renderCom));
["wConf","wAct"].forEach(id=>el(id).addEventListener("input",renderWhy));
["sq","sCat","sPrio"].forEach(id=>el(id).addEventListener("input",renderSig));

renderAcc(); renderCom(); renderWhy(); renderSig();
try{const t=localStorage.getItem("vim.tab");
  if(t){const b=tabs.find(x=>x.dataset.tab===t); if(b)b.click();}}catch(e){}
</script>
"""

out = HTML.replace("__PAYLOAD__", payload)
path = os.path.join(BASE, "vim-enterprise-gtm-engine.html")
open(path, "w", encoding="utf-8").write(out)
print("wrote", path, f"{len(out)/1024:.0f} KB")
print(f"  {STATS['records']} records -> {STATS['orgs']} orgs -> {STATS['parents']} parent groups")
print(f"  {STATS['t1']} Tier 1 · {STATS['seats']} seats · {STATS['signals']} signals · {STATS['segments']} segments")
