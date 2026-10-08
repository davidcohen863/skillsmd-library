#!/usr/bin/env python3
"""Builds the public data the Skills MD site reads.

  python3 build.py   ->  index.json (the card list) + guides/<slug>.json (one full guide each)

Source: issues/issue-NN.json, one file per newsletter issue. It stops with a list of
problems if a guide breaks a rule in GUIDES.md, and writes nothing in that case.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REQ = ["kind", "name", "repo", "level", "cost", "works_with", "short", "what", "who", "needs", "steps", "try", "sources"]
BAD = ["—", "–", "Claude skills"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def check(n, it, errs):
    w = f"issue {n} / {it.get('name', '?')}"
    for k in REQ:
        if not it.get(k):
            errs.append(f"{w}: missing {k}")
    if it.get("kind") not in ("Repo", "Skill"):
        errs.append(f"{w}: kind must be Repo or Skill")
    if len(it.get("short", "")) > 150:
        errs.append(f"{w}: short is over 150 characters")
    if not str(it.get("repo", "")).startswith("github.com/"):
        errs.append(f"{w}: repo must look like github.com/owner/name")
    if not 1 <= len(it.get("steps") or []) <= 8:
        errs.append(f"{w}: needs 1 to 8 steps")
    for s in it.get("steps") or []:
        if not s.get("title"):
            errs.append(f"{w}: a step has no title")
    for u in it.get("sources") or []:
        if not u.startswith("https://"):
            errs.append(f"{w}: source is not an https link: {u}")
    text = json.dumps(it, ensure_ascii=False)
    for b in BAD:
        if b in text:
            errs.append(f"{w}: contains {b!r}")


def main():
    errs, issues, guides, seen = [], [], {}, set()
    for f in sorted(glob.glob(os.path.join(HERE, "issues", "issue-*.json"))):
        d = json.load(open(f))
        n = d.get("issue")
        if not isinstance(n, int) or not d.get("date"):
            errs.append(f"{os.path.basename(f)}: needs an integer issue and a date")
            continue
        cards = []
        for it in d.get("items", []):
            check(n, it, errs)
            s = slug(it.get("name", ""))
            if s in seen:
                s = f"{s}-{n}"
            seen.add(s)
            guides[s] = {"slug": s, "issue": n, "date": d["date"], "checked": d.get("checked", d["date"]), **it}
            cards.append({"s": s, "n": it.get("name"), "k": it.get("kind"), "by": str(it.get("repo", "")).split("/")[1:2][0] if "/" in str(it.get("repo", "")) else "",
                          "st": it.get("stars") or "", "d": it.get("short")})
        issues.append({"n": n, "date": d["date"], "items": cards})
    if errs:
        print("NOT BUILT. Fix these first:\n- " + "\n- ".join(errs))
        sys.exit(1)
    issues.sort(key=lambda i: -i["n"])
    os.makedirs(os.path.join(HERE, "guides"), exist_ok=True)
    for s, g in guides.items():
        json.dump(g, open(os.path.join(HERE, "guides", s + ".json"), "w"), ensure_ascii=False, separators=(",", ":"))
    idx = {"updated": issues[0]["date"] if issues else "", "count": len(guides), "issues": issues}
    json.dump(idx, open(os.path.join(HERE, "index.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"built {len(guides)} guides across {len(issues)} issues; index.json is {os.path.getsize(os.path.join(HERE, 'index.json'))} bytes")


if __name__ == "__main__":
    main()
