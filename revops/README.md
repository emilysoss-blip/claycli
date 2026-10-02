# RevOps contacts across my accounts

Finds every RevOps manager, head of revenue operations and RevOps leader at the accounts in
the **Emily Soss accounts** Audience segment (`audseg_0tkp7k67sq7xSYd9Wgr`, Salesforce owner
= Emily, 61 accounts), using only the Clay CLI.

```bash
npm i -g @clay-run/cli && clay login --device   # once
python3 revops/find_revops.py                    # re-run any time; picks up book changes
```

Behind a TLS-inspecting proxy, also set `NODE_EXTRA_CA_CERTS` to the proxy CA.

## How it works

1. **Accounts** — `clay audiences records search-ids/get` reads the segment, for the coverage report.
2. **RevOps pass** — one `clay searches query-mode` people search scoped with
   `clay.filter_to_companies(@audience_segment(...))`, current title containing
   *revenue operations / revops / rev ops*, minus analysts, specialists, coordinators,
   assistants and consultants.
3. **Adjacent pass** — only for accounts with no RevOps title: Sales Ops, GTM Ops,
   Commercial Ops and Business Ops at manager level or above, labeled `match_type=adjacent`.
   Skip with `--no-adjacent`.

Literal title matching is deliberate. `job_title is_similar_to ("Revenue Operations Manager")`
expands to CROs and their executive assistants.

People search uses no enrichment credits. It counts against the workspace search-result quota.
Emails and phones are not included. Run the workspace's *Work Email* function on the rows you want.

## Output

| File | Contents |
|---|---|
| `revops_contacts.csv` | One row per person: account, domain, `match_type`, name, title, `level` (Leader / Manager / Unclear), location, LinkedIn URL, role start date |
| `account_coverage.csv` | One row per account: RevOps found by level, adjacent found |

`level` comes from the title: Leader is VP / SVP / Head / Director / Chief, Manager is
Manager / Supervisor / Lead / Architect, and Unclear is a bare "Revenue Operations" title.
