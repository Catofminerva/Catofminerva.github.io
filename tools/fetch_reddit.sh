#!/usr/bin/env bash
# Collect rooms from r/LiminalSpace using curl.
#
# curl has two things the python script cannot arrange for itself: working
# certificates on macOS, and a home address reddit will answer. It saves the
# listings, and fetch_rooms.py turns them into rooms.json without touching
# the network at all.
#
#   bash tools/fetch_reddit.sh
#
# Then commit rooms.json.

set -u

cd "$(dirname "$0")/.." || exit 1

DIR="${TMPDIR:-/tmp}/liminal-rooms"
mkdir -p "$DIR"

UA='liminal rooms (catofminerva.com)'
BASE='https://www.reddit.com/r/LiminalSpace'
FILES=()

grab () {
  local name="$1" query="$2" out="$DIR/$1.json"
  if curl -sfL -A "$UA" "$BASE/$query" -o "$out"; then
    if [ -s "$out" ] && head -c 1 "$out" | grep -q '{'; then
      echo "  $name: saved"
      FILES+=("$out")
    else
      echo "  $name: reddit answered with something that is not a listing"
    fi
  else
    echo "  $name: curl could not fetch it"
  fi
  sleep 1
}

echo "asking reddit for five listings..."
grab top-all   'top.json?t=all&limit=100&raw_json=1'
grab top-year  'top.json?t=year&limit=100&raw_json=1'
grab top-month 'top.json?t=month&limit=100&raw_json=1'
grab hot       'hot.json?limit=100&raw_json=1'
grab new       'new.json?limit=100&raw_json=1'

if [ ${#FILES[@]} -eq 0 ]; then
  echo
  echo "nothing came back, so rooms.json is untouched."
  echo "reddit refuses some connections outright. the page keeps the"
  echo "photographs it already has."
  exit 1
fi

echo
python3 tools/fetch_rooms.py --from-file "${FILES[@]}" --limit 250
