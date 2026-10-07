# Eightfold: New HR Leader Signal account prep

Prep for the Oct 7 call with Emi Witt, Yash Garg and Sue Ostaszewski. It covers the four
accounts behind the six qualified rows in the demo build doc, plus one Clay account agent
that produces this prep automatically for every account the signal catches.

```
eightfold/README.md                  this file: agent prompt, per-account prep, caveats
eightfold/account_agent_tasks.json   the agent's task list, in Clay outputSchema format
eightfold/account-prep.html          the same prep as a page to have open during the call
```

All facts below came back from Clay on Oct 7, 2026, in the Clay Demos (GTM) workspace:
contact lookups for the six leaders, and Open Jobs, Recent News plus two custom research
columns (HR and Talent Tech Stack, Workforce and Talent Initiatives) on the four companies.
Source URLs are the ones Clay's research cited. They were not opened separately, so check
any figure before quoting it to the customer.

## Read this before presenting

- **Only 3 of the 6 rows hold an exact step-3 title.** The signal is defined on CHRO, Chief
  People Officer, Head of Talent Intelligence and Head of Talent Acquisition. Raynee Meyer,
  Amy Richman and Jonathan Collett match. Julie Moura (AVP, HRBP to the CHRO), Amy Lee Sewell
  (SVP, Senior Talent Acquisition Manager) and Ashley Phillips (Director of TA) do not. Either
  present those three as an expanded title set or tighten the gate before the call. Yash or
  Sue may ask why a Director passed.
- **Amy Richman's start date is year-only.** Clay returns `2026` with no month. Her Audiences
  record still carries an `@starbucks.com` email.
- **Open Jobs does not give the step-6 volume number.** Clay returns a 10-posting sample per
  account, not a total requisition count. The sample is still useful for the hiring mix
  (below), but the open req count needs another source, such as the careers site total.
- **Step 2 suppression could not be checked from here.** Eightfold's Salesforce isn't
  connected. Public research found no evidence that any of the four accounts is an Eightfold
  customer, which is not the same as confirming they aren't.
- **Pin the LinkedIn company page before enriching.** Each domain returns several satellite
  company pages in Clay. The first page of results alone held 8 for UnitedHealth Group, 6 for
  CVS, 4 for Flex and 2 for Lockton. Enrich on the pages listed under each account below.

## The account agent

One agent for the workflow, not one per account. It runs once per account that passes the
step-4 gate and reads that account's audience record, contacts and signals, plus web search.
In the build this replaces the step-5 Claygent: per Clay's workflow guidance, an account agent
with several tasks beats a chain of single-purpose Claygents, and it sees the account's
contacts without a separate lookup step.

**Name:** `Eightfold - New HR Leader Account Prep`

**Build steps (in the workflow, once the CLI works):**
1. Create the agent node bare, wired after the step-4 gate.
2. `clay workflows nodes create-account-agent <workflowId> <nodeId> --name "Eightfold - New HR Leader Account Prep"`
3. Update the node with the prompt below, then, in a separate call, set `outputSchema` to
   `account_agent_tasks.json`.
4. Confirm `accountId` auto-wired from the accounts trigger. Under a people trigger, wire it to
   the person's associated account id.
5. Add a write-to-Audiences node after it, `entityType: ACCOUNT`, so the prep lands on the
   company record.

**Prompt:**

```
You are preparing an Eightfold AI account executive for first outreach to an enterprise
account where a senior HR or talent acquisition leader was appointed in the last 18 months.
Eightfold sells talent intelligence: skills-based hiring, talent CRM and sourcing, internal
mobility and talent marketplace, and workforce planning with skills analytics.

Work from this account's audience record, its contacts and its signals first, then search
the web. The contact who triggered the New HR Leader signal is the subject of the first
three tasks.

Rules:
1. Every claim must be supported by a source you opened. Give the URL.
2. If a field cannot be supported, return exactly NOT_FOUND. Never estimate a start date,
   headcount or deal value.
3. Prefer sources from the last 12 months. If the best source is older, use it and keep its
   real date.
4. Treat the account's own newsroom, investor relations pages and filings as the strongest
   sources, then trade press, then LinkedIn. Use LinkedIn only to confirm a person's title and
   start date.
5. Report only what is publicly disclosed. Do not include personal contact details.

Account-specific focus, if provided: {{account_focus}}
```

`{{account_focus}}` is optional. Map it from an Audiences field if you want per-account steering
(the focus lines under each account below are examples). Leave it empty and the agent runs the
same research on every account.

**Tasks:** the 12 fields in `account_agent_tasks.json`: `appointment_status`,
`appointment_start`, `appointment_source_url`, `signal_rationale`, `work_history_summary`,
`workforce_context`, `hr_tech_stack`, `eightfold_relationship`, `entry_point`,
`first_contact`, `opener`, `open_risks`. Field ids avoid Clay's reserved output names
(`confidence`, `reasoning`, `evidence`, `response`).

---

## UnitedHealth Group

`unitedhealthgroup.com` · Healthcare · Eden Prairie, MN · 92,856 on LinkedIn (the company page
says 340,000 colleagues) · Pin `linkedin.com/company/unitedhealth-group`

| Leader | Title | Started | In Audiences |
|---|---|---|---|
| Raynee Meyer | SVP, Human Resources (Chief People Officer), UnitedHealthcare Operations | Sep 2025 | No |

**Why now.** Raynee is 13 months into leading HR for roughly 50,000 operational employees, with
AI-enabled reskilling and succession planning in scope. UnitedHealthcare announced on May 5,
2026 that it is cutting prior authorization requirements by 30%, with more eliminations by
the end of 2026
([source](https://www.unitedhealthgroup.com/newsroom/2026/2026-05-05-uhc-cuts-prior-authorization-requirements-by-30-percent.html)).
That changes the work done in operations, the population her role covers. The link between
the two is our inference, not something the company has said.

**Account context.** Q2 2026 results beat and full-year guidance was raised on Jul 16, 2026
([source](https://www.unitedhealthgroup.com/newsroom/2026/2026-07-16-uhg-reports-second-quarter-2026-results.html)).
The open-role sample is mixed: hospice RNs, primary care physicians, enterprise security and
cyber, a contact center role, internal audit and M&A.

**HR tech stack.** Nothing publicly sourced. No public evidence of an Eightfold relationship.

**Entry point.** Talent Management and Mobility, then Workforce Planning.

**Opener draft (to Raynee).** "Raynee, you took on HR for UnitedHealthcare Operations last
September, with reskilling and succession for about 50,000 people in scope. With prior
authorizations down 30% this year and more coming, which roles do you expect to redeploy
first, and how are you mapping the skills to move them?"

**Risks.** She is a business-unit CPO, not the enterprise CHRO, so a platform decision may sit
above her and a BU pilot is the realistic first deal. No ATS or HRIS is publicly visible.

**Agent focus.** Confirm whether UHC Operations runs its own HR technology budget or buys
through UHG enterprise HR. Find any public reskilling or redeployment program tied to the
prior authorization changes.

**Live MCP question.** "What do we know about UnitedHealth Group's HR leadership, and does
anyone in Raynee Meyer's org already appear in our Salesforce or Audiences?"

---

## CVS Health

`cvshealth.com` · Healthcare and retail · Woonsocket, RI · 142,370 on LinkedIn (the company
page says over 300,000 colleagues) · Pin `linkedin.com/company/cvshealth`

| Leader | Title | Started | In Audiences |
|---|---|---|---|
| Amy Richman | VP, Head of Talent Acquisition | 2026 (year only) | Yes, stale `@starbucks.com` email |
| Julie Moura | AVP, HR Business Partner to the CHRO & Programs Lead | Jul 2026 | No |

**Why now.** A new head of TA at a company whose open roles are dominated by high-volume hourly
hiring. All 10 postings in Clay's sample are store associates, pharmacy technicians, shift
supervisors, a pharmacy intern and a network strategy analyst. Julie, three months in as the
CHRO's HR business partner, is the route to the CHRO.

**Account context.** CVS updated its strategy and issued 2026 guidance at its Dec 9, 2025
Investor Day
([source](https://www.cvshealth.com/news/company-news/cvs-health-updates-to-uniquely-reimagine-health-care-at-investor-day-event.html))
and reported full-year 2025 results on Feb 10, 2026
([source](https://investors.cvshealth.com/news/news-details/2026/CVS-HEALTH-CORPORATION-REPORTS-FOURTH-QUARTER-AND-FULL-YEAR-2025-RESULTS/default.aspx)).
No public workforce initiatives were found for the last 12 months.

**HR tech stack.** Paradox (conversational AI for high-volume hiring) appears in one third-party
roundup ([source](https://www.selectsoftwarereviews.com/buyer-guide/ai-recruiting)). That's
weak evidence, so confirm it in discovery. No HRIS or ATS was publicly sourced. No public evidence
of an Eightfold relationship.

**Entry point.** Talent Acquisition through Amy, with Julie as the path to a CHRO-level
mobility conversation.

**Opener draft (to Amy).** "Amy, CVS hires pharmacy technicians, store associates and shift
supervisors in volume every week across the country. As you set TA strategy this year, how
are you deciding which of those roles get filled from inside before they're posted?"

**Risks.** Amy's start date is unconfirmed and her Audiences email is at her previous employer.
Volunteer both on the call, since data decay is the problem being sold against. If Paradox is
in place, position Eightfold on skills and mobility rather than on conversational screening.
Julie's title is outside the step-3 title list.

**Agent focus.** Confirm Amy Richman's start month from a CVS or press source. Confirm or rule
out Paradox. Identify the CHRO and whether Julie's programs remit includes internal mobility.

**Live MCP question.** "Show me CVS Health's contacts in Audiences with HR or talent titles, and
flag any with an email domain that isn't cvshealth.com."

---

## Lockton

`lockton.com` · Insurance brokerage, privately held · Kansas City, MO · 15,209 on LinkedIn
· Pin `linkedin.com/company/lockton-companies`

| Leader | Title | Started | In Audiences |
|---|---|---|---|
| Jonathan Collett | Head of Talent Intelligence | Jan 2026 | No |
| Amy Lee Sewell | SVP, Senior Talent Acquisition Manager | Jun 2026 | Yes, no email |

**Why now.** Lockton created a Head of Talent Intelligence role this year, which is the name of
Eightfold's own category. Jonathan's job is to stand up workforce analytics and market
intelligence, and doing that at scale takes a platform. Amy Lee owns large-scale hiring plus
early-career and campus programs, and 4 of the 10 open roles in Clay's sample are 2027
internships or rotational programs.

**Account context.** Lockton reported FY2026 revenue of about $4.5 billion, its sixth straight
year of double-digit organic growth
([source](https://asiainsurancereview.com/News/ViewNewsLetterArticle/id/95884/Type/AIRPlus/Global-Lockton-FY2026-revenue-jumps-to-US-4-5bn-marking-6-consecutive-years-of-double-digit-organic-growth)),
and has announced a new global headquarters
([source](https://leadership.lockton.com/our-next-chapter/lockton-announcement-v2/)). No
public workforce initiatives were found.

**HR tech stack.** Nothing publicly sourced. As a private firm, Lockton discloses less. No public
evidence of an Eightfold relationship.

**Entry point.** Workforce Planning through Jonathan. Talent Acquisition for early careers
through Amy Lee.

**Opener draft (to Jonathan).** "Jonathan, Lockton has grown double digits organically six
years running, and you're nine months into building talent intelligence as a function. What
are you using today to see skills supply against where that growth is coming from?"

**Risks.** A new talent intelligence lead may already have chosen tools or be building in-house.
Two leaders at one account means one account sequence, not two.

**Agent focus.** Find what Jonathan has said publicly about the talent intelligence function
(posts, talks, job postings for his team). Check Lockton job postings for named HR systems.

**Live MCP question.** "Who are our contacts at Lockton with talent titles, and which one should
open a talent intelligence conversation?"

---

## Flex

`flex.com` · Manufacturing · Austin, TX · 56,696 on LinkedIn · Pin
`linkedin.com/company/flexintl`

| Leader | Title | Started | In Audiences |
|---|---|---|---|
| Ashley Phillips | Director of Talent Acquisition, Executive & Commercial | Jan 2026 | No |

**Why now.** Flex is splitting in two. It announced on May 5, 2026 that it will spin off its
Cloud & Power Infrastructure segment as a separate public company
([source](https://investors.flex.com/news/news-details/2026/Flex-Announces-Intention-to-Spin-Off-its-Cloud-and-Power-Infrastructure-Segment-into-a-New-Independent-Publicly-Traded-Company/default.aspx)),
named leadership teams for both companies in July
([source](https://investors.flex.com/news/news-details/2026/Flex-Announces-Leadership-Teams-for-Flex-and-Planned-Cloud-and-Power-Infrastructure-Spin-Off-SpinCo/default.aspx))
and set out the CFO and board composition for "Flex and Axiom" in September
([source](https://investors.flex.com/news/news-details/2026/Flex-Announces-Expected-Flex-CFO-and-Board-Composition-for-Flex-and-Axiom-Following-Separation/default.aspx)).
Clay also returned a Reuters report of a roughly $4.4 billion agreement to acquire EPC Power
([source](https://www.reuters.com/business/flex-acquire-epc-power-44-bln-2026-09-15/)). Two
companies need executive and commercial leaders at the same time, which is Ashley's exact
mandate.

**Account context.** The open-role sample is global manufacturing operations across Mexico,
Malaysia, China, India and the US, plus an HR Global Mobility Specialist in Guadalajara.

**HR tech stack.** Greenhouse ATS, from Flex's public job board
([source](https://job-boards.greenhouse.io/flex)). Nothing else was publicly sourced. No public
evidence of an Eightfold relationship.

**Entry point.** Talent Acquisition for executive and commercial hiring across both companies,
then Workforce Planning for the separation.

**Opener draft (to Ashley).** "Ashley, with Flex separating Cloud & Power into its own public
company, both businesses need executive and commercial leaders at once. How are you building
those slates without the two companies competing for the same people?"

**Risks.** Ashley is Director level, below the step-3 titles, and the platform buyer is more
likely the CHRO, or the new company's head of HR. A separation can freeze new vendor decisions
as easily as it creates them. Verify the EPC Power deal against Flex investor relations before
mentioning it. The Reuters link came from Clay's research and was not opened.

**Agent focus.** Identify the CHRO of each company after separation and the separation date.
Confirm the EPC Power deal on Flex's investor relations site.

**Live MCP question.** "What changed at Flex in the last six months, and who leads HR for the
company being spun off?"
