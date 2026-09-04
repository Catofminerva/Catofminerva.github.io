#!/usr/bin/env python3
"""Look at rooms.json before it goes anywhere.

A clipboard that held something else turns into a rooms.json with nothing
in it, and the first sign of that is a page full of drawn corridors an
hour later. This says what is in the file now.

    python3 tools/check_rooms.py
"""

import json
import sys


def main(path="rooms.json"):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print("%s is not here." % path)
        return 1
    except json.JSONDecodeError as e:
        print("%s is not valid JSON: %s" % (path, e))
        print("if this came from the clipboard, the copy did not take.")
        return 1

    rooms = data.get("rooms") if isinstance(data, dict) else None
    if not isinstance(rooms, list):
        print("%s has no rooms list in it." % path)
        return 1

    bad = [r for r in rooms
           if not isinstance(r, dict)
           or not str(r.get("u", "")).startswith("https://")]
    sources = sorted({r.get("s", "?") for r in rooms if isinstance(r, dict)})

    print("%s: %d rooms" % (path, len(rooms)))
    print("  from: %s" % ", ".join(sources))
    print("  collected: %s" % (data.get("generated") or "unknown"))
    if bad:
        print("  %d entries have no usable image url" % len(bad))
    for r in rooms[:5]:
        if isinstance(r, dict):
            print("    - %s (%s)" % (str(r.get("t", ""))[:58], r.get("a", "?")))

    if not rooms:
        print("\nempty. the doors will open onto drawn corridors.")
        return 1
    if len(rooms) < 20:
        print("\nthat is very few. worth collecting more listings first.")
    print("\nlooks usable.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "rooms.json"))
