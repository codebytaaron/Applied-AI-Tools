#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f "input.txt" ]]; then
  echo "No input.txt found." >&2
  exit 1
fi

input="$(cat input.txt | sed '/^[[:space:]]*$/d' || true)"
if [[ -z "${input}" ]]; then
  echo "No input provided. Edit input.txt." >&2
  exit 1
fi

cat <<'EOF'
# Daily Crew Brief

## Today’s priorities
- 

## Risks / blockers
- 

## Safety
- PPE check
- Site hazards
- Traffic plan

EOF

echo "## Raw Notes"
echo '```text'
cat input.txt
echo '```'
