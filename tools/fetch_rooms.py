#!/usr/bin/env python3
"""Collect image posts from r/LiminalSpace into rooms.json.

liminal.html hangs one of these photographs at the end of every corridor,
so the file is the page's supply of rooms. Nothing here needs an API key:
reddit still serves its public listings as JSON to a plain GET.

    python3 tools/fetch_rooms.py                 # refresh rooms.json
    python3 tools/fetch_rooms.py --limit 400     # collect more
    python3 tools/fetch_rooms.py --sub Backrooms # somewhere else

Run it locally and commit the result, or let .github/workflows/refresh-rooms.yml
do it on a schedule. The page keeps working when the file is stale or empty;
it falls back to asking reddit from the visitor's own browser, and failing
that to the drawn corridor.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UA = "catofminerva.com liminal-space room collector (+https://catofminerva.com/liminal.html)"

# direct image files only. galleries, videos and album links all need a
# second request and none of them hang on a wall.
IMAGE_URL = re.compile(r"^https://i\.redd\.it/[\w.\-]+\.(?:jpg|jpeg|png|webp)$", re.I)


def fetch(url, tries=4):
    """GET a reddit listing, backing off when it says slow down."""
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                wait = 5 * (attempt + 1)
                print("  %s, waiting %ds" % (e.code, wait), file=sys.stderr)
                time.sleep(wait)
                continue
            print("  http %s on %s" % (e.code, url), file=sys.stderr)
            return None
        except Exception as e:                        # noqa: BLE001 - network is network
            if attempt < tries - 1:
                time.sleep(4)
                continue
            print("  %s on %s" % (e, url), file=sys.stderr)
            return None
    return None


def keep(post):
    """Is this post a plain, safe-for-work photograph we can hotlink?"""
    if not post:
        return False
    if post.get("over_18") or post.get("is_video") or post.get("is_gallery"):
        return False
    if post.get("removed_by_category") or post.get("author") == "[deleted]":
        return False
    if post.get("stickied") or post.get("pinned"):
        return False
    url = post.get("url_overridden_by_dest") or post.get("url") or ""
    return bool(IMAGE_URL.match(url))


def as_room(post):
    url = post.get("url_overridden_by_dest") or post["url"]
    created = datetime.fromtimestamp(post.get("created_utc", 0), tz=timezone.utc)
    title = " ".join((post.get("title") or "").split())
    return {
        "i": post["id"],
        "u": url,
        "t": title[:180],
        "a": post.get("author") or "unknown",
        "p": "https://www.reddit.com" + post.get("permalink", ""),
        "d": created.strftime("%Y-%m-%d"),
        "w": (post.get("preview") or {}).get("images", [{}])[0].get("source", {}).get("width", 0),
        "h": (post.get("preview") or {}).get("images", [{}])[0].get("source", {}).get("height", 0),
    }


def harvest(sub, limit, pause):
    """Walk several listings so the file is not all one month of posts."""
    listings = [
        ("top", "?t=all&limit=100&raw_json=1"),
        ("top", "?t=year&limit=100&raw_json=1"),
        ("top", "?t=month&limit=100&raw_json=1"),
        ("hot", "?limit=100&raw_json=1"),
        ("new", "?limit=100&raw_json=1"),
    ]
    seen, rooms = set(), []

    for sort, query in listings:
        after = None
        pages = 0
        while len(rooms) < limit and pages < 4:
            url = "https://www.reddit.com/r/%s/%s.json%s" % (sub, sort, query)
            if after:
                url += "&after=" + after
            print("%s %s page %d (%d kept)" % (sub, sort, pages + 1, len(rooms)), file=sys.stderr)
            data = fetch(url)
            if not data:
                break

            children = (data.get("data") or {}).get("children") or []
            if not children:
                break
            for child in children:
                post = child.get("data") or {}
                if post.get("id") in seen or not keep(post):
                    continue
                seen.add(post["id"])
                rooms.append(as_room(post))

            after = (data.get("data") or {}).get("after")
            pages += 1
            if not after:
                break
            time.sleep(pause)

        if len(rooms) >= limit:
            break

    return rooms[:limit]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sub", default="LiminalSpace")
    ap.add_argument("--limit", type=int, default=250)
    ap.add_argument("--pause", type=float, default=1.5, help="seconds between requests")
    ap.add_argument("--out", default="rooms.json")
    args = ap.parse_args()

    rooms = harvest(args.sub, args.limit, args.pause)
    if not rooms:
        print("collected nothing. rooms.json left as it was.", file=sys.stderr)
        return 1

    payload = {
        "subreddit": args.sub,
        "generated": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "photographs stay on reddit's servers. the page hotlinks them and credits every post.",
        "count": len(rooms),
        "rooms": rooms,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote %s with %d rooms" % (args.out, len(rooms)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
