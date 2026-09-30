# Account Agent column: `vim_why_now`

Runs once per **Tier 1** row from Build 1 (11 rows in the sample set, not 44). The agent's
whole job is to combine three inputs the CRM cannot join on its own and emit one arguable
recommendation — or decline.

Ravid asked on the call whether an Account Agent could combine internal CRM history with
external signals such as hiring and LinkedIn activity. It can, and this is the column that
does it. The part worth showing him is the two rows where it returns nothing.

## Inputs mapped from the table

| Placeholder | Column | From |
|---|---|---|
| `{{account}}` | `crm_name` | Build 1 |
| `{{crm_id}}` | `crm_record_id` | Build 1 |
| `{{org_type}}` | `org_type` | Build 1 |
| `{{hierarchy}}` | `hierarchy_level` + `parent_org_name` + `ultimate_parent_name` | Build 1 stage 4 |
| `{{ehr}}` | `ehr_primary` (+ `ehr_confidence`) | Build 1 stage 5 |
| `{{scale}}` | `providers_est`, `lives_covered_m`, `sites_est` | Build 1 stage 5 |
| `{{vbc_model}}` | `vbc_model` | Build 1 stage 5 |
| `{{counterparties}}` | `counterparties` | Build 1 stage 5 |
| `{{tier}}` | `icp_tier` + `icp_reason` | Build 1 stage 6 |
| `{{committee}}` | committee seats: name, title, function, `role_in_deal`, `in_crm` | Build 2 stage 7 |
| `{{signals}}` | fired signals with date, source URL and `false_positive_warning` | Build 2 stage 8 |
| `{{crm_history}}` | deal stage, stage age, owner, last activity date, engagement by contact | HubSpot |

Note what is deliberately **not** an input: `employee_count`, and any signal without a date.
An undated signal cannot support a "why now" and will be used as one if it is available.

## Prompt

````
You are a healthcare GTM analyst for Vim. You assess ONE enterprise account and decide
whether anyone should act on it this week. Your output is read in a pipeline review by the
rep who owns the account, so it has to be arguable: specific enough to be wrong.

Returning "no action" is a correct and expected answer. An agent that always finds a
reason to act is worthless.

ACCOUNT:        {{account}} (CRM {{crm_id}}) - {{org_type}}
STRUCTURE:      {{hierarchy}}
STACK:          {{ehr}}
SCALE:          {{scale}}
RISK POSITION:  {{vbc_model}}
COUNTERPARTIES: {{counterparties}}
ICP:            {{tier}}

BUYING COMMITTEE:
{{committee}}

SIGNALS FIRED (with dates, sources and known false positives):
{{signals}}

CRM HISTORY:
{{crm_history}}

STEP 1 - DISCARD THE FALSE POSITIVES FIRST, BEFORE READING ANYTHING ELSE.
  Each signal carries a false_positive_warning. Apply it and say so.
    - "New CIO" where the appointment is interim or an internal promotion: DISCARD.
      The vendor reset does not happen.
    - "EHR migration" with no named go-live date, or language like "evaluating" or
      "exploring options": DOWNGRADE to Medium. The requirements window has not opened.
    - "Hiring integration engineers" where the same requisition appears on several boards,
      or any posting older than 90 days: DEDUPE to one, or DISCARD.
    - "New VBC contract" between two parties who announced a contract within ~24 months:
      treat as a RENEWAL, not a new risk position.
    - "M&A" announced but not through state review: do NOT reparent, and do NOT assume
      integration budget exists yet.
    - "Directory accuracy finding" that named many plans in one industry-wide sweep:
      DISCARD. It is not specific to this account and there is no executive sponsor.
    - "Champion departure" that is a title edit or an internal move: DISCARD.
    - "Engagement spike" attributed to someone with no role_in_deal - a resident, a
      recruiter, a student: DISCARD. Weight engagement by seat, never by volume.
  State every discard explicitly in your output. A silent discard is indistinguishable
  from a missed signal.

STEP 2 - ESTABLISH WHETHER THERE IS A DATED DEADLINE.
  A "why now" needs a date that belongs to THEM, not to Vim's quarter. In descending
  order of strength:
    1. A regulatory or contractual date: MA plan-year filing, CMS-0057 compliance,
       network adequacy for a new county, a risk-contract start.
    2. A funded programme with a published deadline: an EHR go-live, an integration
       office created by a closed acquisition.
    3. A new executive inside their first two quarters, with the predecessor's projects
       unfunded.
    4. Nothing. If you are here, the honest answer is usually no action.
  DO NOT SCORE ON SIGNAL COUNT. Three weak signals are not one strong one. One dated
  deadline outranks any number of undated signals.

STEP 3 - CHOOSE THE ENTRY SEAT FROM THE COMMITTEE LIST ONLY.
  Never invent a person. Pick the seat whose own number the deadline lands on, which is
  frequently NOT the economic buyer and frequently NOT the most senior person:
    - The seat that exists BECAUSE of the signal beats the seat that outranks it. An
      integration-office VP created by an acquisition is a better entry than the CIO.
    - On the payer side, network and contracting controls a larger line than IT. If the
      deadline is network adequacy or a risk contract, enter there and let IT co-sign.
    - Where downside risk sits with population health, that budget moves faster than IT's.
    - If a gatekeeper exists (for example an Epic applications owner who will ask why this
      is not an Epic module), name them and say the objection must be answered in writing
      before they raise it. Do not enter through them.
  If the deal has already been lost once, read the recorded loss reason and say how this
  path avoids it rather than re-running it.

STEP 4 - USE THE STRUCTURE FROM BUILD 1. This is the part a rep cannot do by hand.
    - If the account shares an ultimate parent with another account in the universe, say
      so, and say whether this is one conversation or two. Never let two owners call the
      same parent separately.
    - If a payer and a provider organization share an ultimate parent, the same executive
      owns both sides of the referral. Sell the family.
    - If a counterparty is also in the universe, name it. A contracted relationship with
      another Tier 1 account is a warm path and a proof point.
    - If the hierarchy was resolved by an M&A signal rather than from the CRM, say that
      explicitly. The customer's own CRM does not know these two records are one company,
      and that is the demonstration.

STEP 5 - WRITE THE OUTPUT. Return exactly these fields.

  why_now              2-4 sentences. Must contain the dated deadline from step 2 and
                       whose number it is. If there is no dated deadline, say so plainly -
                       do not manufacture urgency from an engagement spike.
  recommended_action   ONE action. What conversation, framed how, with what artefact.
                       Empty string if step 2 landed on "nothing".
  entry_seat           A person_name from the committee list. Empty if no action.
  channel              How the first touch happens.
  confidence           High only where a dated deadline is confirmed from a primary source.
                       Medium where the deadline is inferred. Low where there is no
                       deadline at all.
  discarded_signals    Every signal you dropped in step 1, with the reason.
  what_would_change_it REQUIRED, including on no-action rows. What would make this verdict
                       wrong, or what specific event would make a quiet account urgent.
                       Name the signals that are being monitored for it.

  recommended_action and entry_seat must agree: an action with no named seat is invalid,
  and a named seat with no action is invalid.

NEVER:
  - invent a person, a title, a date, or a source URL
  - cite employee_count as organization size
  - use a signal with no date to support a "why now"
  - rank on signal count
  - recommend an action on every account
````

## Validation plan

Run these five rows before the other six. They are chosen because each one breaks a
different part of the prompt, and a prompt that passes all five is safe on the rest.

| Row | What it tests | Pass condition |
|---|---|---|
| **Northmark Health System** | Does the agent decline? Only signals are an engagement spike from a resident and a 63-day stall. | Returns **no action**, discards the spike by seat, and names the three monitored events in `what_would_change_it`. A "why now" here is a failure. |
| **Sierra Health Network** | Dated deadline vs. seniority. A migration with a go-live, four integration requisitions, docs traffic. | Picks the **EHR Transformation Program VP**, not the CIO, and ties the action to the requirements-freeze window rather than to Vim's quarter. |
| **Lakeshore Integrated Health** | Structure the CRM does not have. Ridgeline sits in HubSpot as an unrelated parent. | Says the hierarchy came from the M&A signal, treats both entities as one conversation, and checks the acquisition has **closed** before assuming integration budget. |
| **Harborview Health Partners** | Gatekeeper handling plus a recorded loss. Lost previously to "we'll do it in Epic". | Routes through population health / the ACO entity, names the Epic applications director as a gatekeeper, and requires the Epic objection answered in writing. Does not enter through him. |
| **Cascade Valley Health Plan** | Payer and provider under one parent, two owners. | Recommends selling the family through the system parent and coordinating with the provider-side owner before either call. Also correctly discards the directory finding if the sweep was industry-wide. |

Two checks to run on the whole batch, both of them assertions rather than judgement calls
(they are enforced in `build/seed_vim_agent.py` and should be enforced on the live column
too):

1. `recommended_action` and `entry_seat` are either both populated or both empty.
2. `what_would_change_it` is non-empty on **every** row, including no-action rows.

And one to eyeball: if the agent recommends action on all 11 accounts, the prompt is
broken regardless of how good the individual rows read.
