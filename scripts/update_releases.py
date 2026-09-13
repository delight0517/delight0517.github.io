#!/usr/bin/env python3
"""update_releases.py — detect app releases via iTunes Lookup, append a news post
carrying that version's LIVE release notes ("what changed"), and add a story
chapter the first time an app actually goes live on the App Store.
Run from the repo root; read/writes only data/*.json.
"""
import json, os, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
STATE = os.path.join(DATA, "release_state.json")
NEWS = os.path.join(DATA, "news.json")
STORY = os.path.join(DATA, "story.json")
APPS = os.path.join(DATA, "apps.json")


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def lookup(aid):
    url = f"https://itunes.apple.com/lookup?id={aid}&country=us"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            j = json.loads(r.read().decode("utf-8"))
        if j.get("resultCount", 0) > 0:
            return j["results"][0]
    except Exception as e:
        print(f"[warn] lookup {aid}: {e}")
    return None


def first_line(s):
    for line in (s or "").splitlines():
        line = line.strip()
        if line:
            return line[:140]
    return ""


def today():
    return datetime.date.today().isoformat()


def main():
    state = load(STATE)
    news = load(NEWS)
    story = load(STORY)
    apps_meta = load(APPS)
    meta_by_id = {a["id"]: a for a in apps_meta["apps"]}

    posts = news["posts"]
    chapters = story.get("chapters", [])
    changed = False

    for k, st in state["apps"].items():
        aid = st.get("itunesId")
        if not aid:
            continue
        meta = meta_by_id.get(k, {})
        name = meta.get("name", k)
        rec = lookup(aid)
        if rec is None:
            st["live"] = False
            state["apps"][k] = st
            print(f"[{name}] not live")
            continue

        rel_ver = str(rec.get("version", ""))
        rel_notes = rec.get("releaseNotes") or ""
        store_url = rec.get("trackViewUrl") or ""
        last_ver = st.get("lastVersion")
        was_live = st.get("live", False)

        # duplicate check (avoid double-posting on rerun)
        dup = False
        for p in posts:
            if p.get("date") == today() and p.get("version") == rel_ver and (p.get("appId") or p.get("app")) == k:
                dup = True
                break

        if not was_live and rel_ver:
            # first time live -> story launch chapter
            has_launch = any(
                (c.get("title", "").startswith(f"{name} 첫 출시") if not c.get("__launch__") else c.get("launchKey") == k)
                for c in chapters
            )
            if not has_launch:
                chapters.append({
                    "launchKey": k,
                    "period": today(),
                    "title": f"{name} 첫 출시",
                    "body": f"개발을 마친 {name}이(가) App Store에서 처음으로 실제 배포되었습니다. (v{rel_ver})"
                })
                changed = True
                print(f"  [story] {name} first live v{rel_ver}")

        if rel_ver and last_ver != rel_ver and not dup:
            ttl = f"{name} {rel_ver} 출시"
            if rel_notes:
                ttl += f" — {first_line(rel_notes)}"
            posts.append({
                "date": today(),
                "type": "release",
                "appId": k,
                "title": ttl,
                "body": rel_notes or "새 버전이 App Store에 배포되었습니다.",
                "version": rel_ver,
                "status": "released",
                "storeUrl": store_url
            })
            changed = True
            print(f"  [news] {name} v{rel_ver} posted with release notes")

        st["lastVersion"] = rel_ver
        st["live"] = True
        state["apps"][k] = st

    if changed:
        save(STATE, state)
        save(NEWS, news)
        save(STORY, story)
        print("WROTE data files (release detected)")
    else:
        print("no release changes")


if __name__ == "__main__":
    main()