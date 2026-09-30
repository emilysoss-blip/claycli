#!/usr/bin/env bash
# Vim provider POC — phase 1 build through the Clay CLI.
# Spends no credits: inventories the workspace, creates the draft workflow and CSV trigger,
# links the seed CSV. Does NOT run rows, create Signals, write to HubSpot, or publish.
set -euo pipefail
CLAY="${CLAY:-clay}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HERE/clay/manifest"; mkdir -p "$OUT"

"$CLAY" --version
"$CLAY" whoami | tee "$OUT/whoami.json"

# 1. Inventory (guide §2)
"$CLAY" workflows actions list   > "$OUT/actions-catalog.json"
"$CLAY" routines list            > "$OUT/routines.json"
"$CLAY" signals list             > "$OUT/signals.json"
"$CLAY" workflows list           > "$OUT/workflows-existing.json" || true
"$CLAY" audiences fields list --entity-type companies > "$OUT/company-fields.json"
"$CLAY" audiences fields list --entity-type people    > "$OUT/people-fields.json"

jq '.data[] | select(((.displayName // .name // "") + " " + (.description // "") + " " + (.packageDisplayName // ""))
    | test("company|domain|healthcare|NPI|technolog|parent|hierarch|email|phone|HubSpot|news|job"; "i"))
    | {displayName, packageDisplayName, packageId, actionKey, priorityTier, creditCost}' \
  "$OUT/actions-catalog.json" > "$OUT/actions-candidates.json"

# 2. Draft workflow + CSV trigger (guide §4)
"$CLAY" workflows create --name "Vim | Provider Account Intelligence POC" | tee "$OUT/workflow.json"
WF=$(jq -r '.id // .workflowId // .data.id' "$OUT/workflow.json")
"$CLAY" workflows triggers create "$WF" --input '{"triggerType":"csv_upload"}' | tee "$OUT/trigger.json"
TR=$(jq -r '.resourceId // .id // .data.resourceId' "$OUT/trigger.json")
"$CLAY" workflows triggers csv upload "$TR" --file "$HERE/data/seed_accounts.csv" | tee "$OUT/csv-upload.json"
jq -r '.csvFile.headers[]' "$OUT/csv-upload.json" | sort | uniq -d | grep . && { echo "duplicate CSV headers"; exit 1; } || true
"$CLAY" workflows graph get "$WF" > "$OUT/graph.json"

echo "workflowId=$WF triggerId=$TR"
echo "Next: pick actions from $OUT/actions-candidates.json, run 'clay workflows actions schema <pkg> <key>', then create nodes."
