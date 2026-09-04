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

# Reddit asks for a user agent in this shape and refuses a good many
# others outright, which is the likeliest reason a plain curl gets a 403
# from a perfectly ordinary home connection.
REDDIT_USER="${REDDIT_USER:-catofminerva}"
UA="macos:com.catofminerva.liminal:v1.0 (by /u/${REDDIT_USER})"
BASE='https://www.reddit.com/r/LiminalSpace'
OLD='https://old.reddit.com/r/LiminalSpace'
FILES=()

# Report what actually came back. Swallowing the status code turns every
# distinct failure into the same unhelpful sentence.
grab () {
  local name="$1" url="$2" out="$DIR/$1.json" err="$DIR/$1.err" code
  if [ -n "$TOKEN" ]; then
    code=$(curl -sSL -A "$UA" -H "Authorization: bearer $TOKEN" \
             -w '%{http_code}' -o "$out" "$url" 2>"$err")
  else
    code=$(curl -sSL -A "$UA" -w '%{http_code}' -o "$out" "$url" 2>"$err")
  fi
  if [ -z "$code" ] || [ "$code" = "000" ]; then
    echo "  $name: no reply. $(head -1 "$err" 2>/dev/null)"
  elif [ "$code" != "200" ]; then
    echo "  $name: http $code"
  elif [ -s "$out" ] && head -c 1 "$out" | grep -q '{'; then
    echo "  $name: saved"
    FILES+=("$out")
  else
    echo "  $name: http 200 but not a listing ($(head -c 40 "$out" | tr -d '\n'))"
  fi
  sleep 1
}

# With a script app's credentials reddit answers through oauth.reddit.com,
# which is the route it actually sanctions and the one that works when the
# public listings will not.
#   REDDIT_CLIENT_ID=... REDDIT_CLIENT_SECRET=... bash tools/fetch_reddit.sh
TOKEN=""
if [ -n "${REDDIT_CLIENT_ID:-}" ] && [ -n "${REDDIT_CLIENT_SECRET:-}" ]; then
  echo "authenticating..."
  TOKEN=$(curl -sS -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
            -d grant_type=client_credentials -A "$UA" \
            https://www.reddit.com/api/v1/access_token \
          | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get("access_token",""))
except Exception:
    print("")' 2>/dev/null)
  if [ -n "$TOKEN" ]; then
    echo "  got a token. using oauth.reddit.com"
    BASE='https://oauth.reddit.com/r/LiminalSpace'
    OLD="$BASE"
  else
    echo "  could not get a token. carrying on without one."
  fi
fi

echo "asking reddit for five listings..."
EXT='.json'
[ -n "$TOKEN" ] && EXT=''

grab top-all   "$BASE/top$EXT?t=all&limit=100&raw_json=1"
grab top-year  "$BASE/top$EXT?t=year&limit=100&raw_json=1"
grab top-month "$BASE/top$EXT?t=month&limit=100&raw_json=1"
grab hot       "$BASE/hot$EXT?limit=100&raw_json=1"
grab new       "$BASE/new$EXT?limit=100&raw_json=1"

# www is not the only door. old.reddit.com is served by different
# front ends and sometimes answers when www will not.
if [ ${#FILES[@]} -eq 0 ]; then
  echo
  echo "www refused everything. trying old.reddit.com..."
  grab old-top "$OLD/top$EXT?t=year&limit=100&raw_json=1"
  grab old-hot "$OLD/hot$EXT?limit=100&raw_json=1"
fi

if [ ${#FILES[@]} -eq 0 ]; then
  echo
  echo "nothing came back, so rooms.json is untouched."
  echo "the codes above say why: 403 means reddit is refusing this"
  echo
  echo "if it is 403, credentials get past it. make a \"script\" app at"
  echo "https://www.reddit.com/prefs/apps and run:"
  echo "  REDDIT_CLIENT_ID=xxx REDDIT_CLIENT_SECRET=yyy bash tools/fetch_reddit.sh"
  echo "address, 429 means too many requests for now, and no reply at"
  echo "all points at dns or a vpn. the page keeps the photographs it"
  echo "already has either way."
  exit 1
fi

echo
python3 tools/fetch_rooms.py --from-file "${FILES[@]}" --limit 250
