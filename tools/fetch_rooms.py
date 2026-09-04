#!/usr/bin/env python3
"""Collect image posts from r/LiminalSpace into rooms.json.

liminal.html hangs one of these photographs at the end of every corridor,
so the file is the page's supply of rooms. Nothing here needs an API key:
reddit still serves its public listings as JSON to a plain GET.

    python3 tools/fetch_rooms.py                 # refresh rooms.json
    python3 tools/fetch_rooms.py --limit 400     # collect more
    python3 tools/fetch_rooms.py --sub Backrooms # somewhere else

Reddit is the first choice and is not always available. It serves its
public listings to home connections and answers 403 to anonymous requests
from datacentres, which is every CI runner. Credentials lift that:

    make a "script" app at https://www.reddit.com/prefs/apps
    export REDDIT_CLIENT_ID=... REDDIT_CLIENT_SECRET=...
    python3 tools/fetch_rooms.py

When reddit cannot be reached, --source auto falls through to Openverse
and then Wikimedia Commons, which block nobody and carry openly licensed
photographs of the same kind of place: corridors nobody is in, pools with
the lights on, car parks at four in the morning. Every room credits its
photographer and links back either way.

    python3 tools/fetch_rooms.py --source openverse
    python3 tools/fetch_rooms.py --source commons

Run it locally and commit the result, or let .github/workflows/refresh-rooms.yml
do it on a schedule. The page keeps working when the file is stale or empty;
it falls back to asking reddit from the visitor's own browser, and failing
that to the drawn corridor.
"""

import argparse
import base64
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = "catofminerva.com liminal-space room collector (+https://catofminerva.com/liminal.html)"

# direct image files only. galleries, videos and album links all need a
# second request and none of them hang on a wall.
IMAGE_URL = re.compile(r"^https://i\.redd\.it/[\w.\-]+\.(?:jpg|jpeg|png|webp)$", re.I)


# Filled in by authenticate() when credentials are present. Anonymous
# requests are fine from a home connection and refused from a datacentre.
TOKEN = None
HOST = "https://www.reddit.com"


def ssl_context():
    """A verifying SSL context that also works on python.org's macOS build.

    That build ships without a certificate store, so every https request
    dies with CERTIFICATE_VERIFY_FAILED until someone runs its
    "Install Certificates.command". Where certifi is available we hand
    urllib those roots instead. Verification stays on either way: a
    crawler that skips it is worse than a crawler that fails.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:                                 # noqa: BLE001
        return None


CTX = None


def authenticate():
    """Swap a script app's id and secret for an app-only bearer token.

    Without this every request from a CI runner comes back 403, because
    reddit does not serve its public JSON to datacentre addresses.
    """
    global TOKEN, HOST
    cid = os.environ.get("REDDIT_CLIENT_ID", "").strip()
    secret = os.environ.get("REDDIT_CLIENT_SECRET", "").strip()
    if not cid or not secret:
        return False

    body = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    basic = base64.b64encode(("%s:%s" % (cid, secret)).encode()).decode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=body,
        headers={"Authorization": "Basic " + basic, "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
            TOKEN = json.loads(r.read().decode("utf-8")).get("access_token")
    except Exception as e:                            # noqa: BLE001
        print("could not authenticate: %s" % e, file=sys.stderr)
        return False

    if not TOKEN:
        return False
    HOST = "https://oauth.reddit.com"
    print("authenticated. using %s" % HOST, file=sys.stderr)
    return True


def fetch(url, tries=4):
    """GET a reddit listing, backing off when it says slow down."""
    for attempt in range(tries):
        headers = {"User-Agent": UA, "Accept": "application/json"}
        if TOKEN:
            headers["Authorization"] = "bearer " + TOKEN
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                wait = 5 * (attempt + 1)
                print("  %s, waiting %ds" % (e.code, wait), file=sys.stderr)
                time.sleep(wait)
                continue
            print("  http %s on %s" % (e.code, url), file=sys.stderr)
            if e.code in (401, 403) and not TOKEN:
                print("  reddit refuses anonymous requests from this address."
                      " set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET, or run"
                      " this from a home connection.", file=sys.stderr)
            return None
        except Exception as e:                        # noqa: BLE001 - network is network
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                print("  this python has no certificate store. either run"
                      " /usr/bin/python3 instead, or run the"
                      " \"Install Certificates.command\" that came with your"
                      " python, or pip3 install certifi.", file=sys.stderr)
                return None
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
        "a": "u/" + (post.get("author") or "unknown"),
        "p": "https://www.reddit.com" + post.get("permalink", ""),
        "d": created.strftime("%Y-%m-%d"),
        "s": "r/LiminalSpace",
        "l": "",
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
            suffix = "" if TOKEN else ".json"      # oauth.reddit.com wants no extension
            url = "%s/r/%s/%s%s%s" % (HOST, sub, sort, suffix, query)
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


# What a liminal photograph is, expressed as things to search for. The
# list is the whole aesthetic: an interior with the lights on and nobody
# in it, photographed by someone who was passing through.
QUERIES = [
    "empty corridor", "hotel hallway night", "abandoned shopping mall interior",
    "empty indoor swimming pool", "underground car park interior",
    "empty waiting room", "office corridor fluorescent", "empty airport terminal night",
    "concrete stairwell", "empty classroom", "empty subway station platform",
    "motel exterior night", "empty car park at night", "hospital corridor empty",
]


def strip_tags(text):
    return " ".join(re.sub(r"<[^>]+>", " ", text or "").split())


def harvest_openverse(limit, pause):
    """Openverse indexes openly licensed photographs and blocks nobody."""
    seen, rooms = set(), []
    for q in QUERIES:
        if len(rooms) >= limit:
            break
        url = ("https://api.openverse.org/v1/images/?q=%s&page_size=40"
               "&license_type=all-cc&mature=false&format=json"
               % urllib.parse.quote(q))
        print("openverse: %s (%d kept)" % (q, len(rooms)), file=sys.stderr)
        data = fetch(url)
        if not data:
            continue
        for r in data.get("results") or []:
            u = r.get("url") or ""
            rid = r.get("id")
            if not u.startswith("https://") or rid in seen:
                continue
            seen.add(rid)
            rooms.append({
                "i": str(rid),
                "u": u,
                "t": " ".join((r.get("title") or q).split())[:180],
                "a": (r.get("creator") or "unknown")[:80],
                "p": r.get("foreign_landing_url") or u,
                "d": (r.get("created_on") or "")[:10],
                "s": "Openverse",
                "l": (r.get("license") or "").upper() + " " + (r.get("license_version") or ""),
            })
        time.sleep(pause)
    return rooms[:limit]


def harvest_commons(limit, pause):
    """Wikimedia Commons. Slower to look at, but it is always there."""
    seen, rooms = set(), []
    for q in QUERIES:
        if len(rooms) >= limit:
            break
        url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
               "&formatversion=2&generator=search&gsrsearch=%s&gsrnamespace=6"
               "&gsrlimit=40&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1600"
               % urllib.parse.quote(q + " filetype:bitmap"))
        print("commons: %s (%d kept)" % (q, len(rooms)), file=sys.stderr)
        data = fetch(url)
        if not data:
            continue
        for page in ((data.get("query") or {}).get("pages") or []):
            info = (page.get("imageinfo") or [{}])[0]
            u = info.get("thumburl") or info.get("url") or ""
            pid = page.get("pageid")
            if not u.lower().endswith((".jpg", ".jpeg", ".png")) or pid in seen:
                continue
            seen.add(pid)
            meta = info.get("extmetadata") or {}
            rooms.append({
                "i": str(pid),
                "u": u,
                "t": " ".join((page.get("title") or "").replace("File:", "").rsplit(".", 1)[0].split())[:180],
                "a": strip_tags((meta.get("Artist") or {}).get("value", ""))[:80] or "unknown",
                "p": info.get("descriptionurl") or u,
                "d": ((meta.get("DateTimeOriginal") or {}).get("value", "") or "")[:10],
                "s": "Wikimedia Commons",
                "l": strip_tags((meta.get("LicenseShortName") or {}).get("value", "")),
            })
        time.sleep(pause)
    return rooms[:limit]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sub", default="LiminalSpace")
    ap.add_argument("--limit", type=int, default=250)
    ap.add_argument("--pause", type=float, default=1.5, help="seconds between requests")
    ap.add_argument("--out", default="rooms.json")
    ap.add_argument("--source", default="auto",
                    choices=["auto", "reddit", "openverse", "commons"],
                    help="auto tries reddit first, then the sources that block nobody")
    args = ap.parse_args()

    global CTX
    CTX = ssl_context()

    rooms, source = [], args.source
    if args.source in ("auto", "reddit"):
        authenticate()
        rooms = harvest(args.sub, args.limit, args.pause)
        source = "reddit"
        if not rooms and args.source == "auto":
            print("reddit gave nothing here. trying the open sources.", file=sys.stderr)
    if not rooms and args.source in ("auto", "openverse"):
        rooms = harvest_openverse(args.limit, args.pause)
        source = "openverse"
    if not rooms and args.source in ("auto", "commons"):
        rooms = harvest_commons(args.limit, args.pause)
        source = "commons"

    if not rooms:
        print("collected nothing. rooms.json left as it was.", file=sys.stderr)
        return 1

    payload = {
        "source": source,
        "subreddit": args.sub if source == "reddit" else None,
        "generated": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "photographs stay on their own servers. the page hotlinks them and credits every one.",
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
