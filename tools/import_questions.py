"""Import questions from another system (for example a Gemini JSON export) into a pack.

Accepts a list of objects with: question, options (dict A-D or list), correct_answer (letter or index),
explanation, subdomain ("1.2 - ..." or "1.2"), optional id and memory anchor.
Imported questions are marked "needs-review": fact-check them before publishing.

Usage: python3 tools/import_questions.py incoming.json --origin Gemini [--pack packs/isc2-ai-security-pilot.json]
"""
import argparse, json, random, re, collections

ap = argparse.ArgumentParser()
ap.add_argument("incoming"); ap.add_argument("--origin", required=True)
ap.add_argument("--pack", default="packs/isc2-ai-security-pilot.json")
a = ap.parse_args()

def blocks(s):
    s = re.sub(r"\bLEGO®?\s*(bricks?)\b", "building blocks", s, flags=re.I)
    s = re.sub(r"\bminifig(ure)?s\b", "figures", s, flags=re.I)
    s = re.sub(r"\bminifig(ure)?\b", "figure", s, flags=re.I)
    return re.sub(r"\bLEGO®?\b", "building block", s, flags=re.I)

p = json.load(open(a.pack, encoding="utf-8"))
src = json.load(open(a.incoming, encoding="utf-8"))
subs = {s["id"] for d in p["domains"] for s in d["subdomains"]}
stems = {re.sub(r"\W+", " ", q["stem"].lower()).strip() for q in p["questions"]}
count = collections.Counter(q["subdomain"] for q in p["questions"])
ids = {q["id"] for q in p["questions"]}
pos = collections.Counter(q["answer"] for q in p["questions"])
added, skipped = 0, []
for item in src:
    sub = re.match(r"\s*(\d+\.\d+)", str(item.get("subdomain", "")))
    sub = sub.group(1) if sub else None
    if sub not in subs: skipped.append((item.get("id"), "unknown subdomain")); continue
    opts = item.get("options")
    keys = list(opts.keys()) if isinstance(opts, dict) else None
    opts = [opts[k] for k in keys] if keys else list(opts)
    ca = item.get("correct_answer", item.get("answer"))
    ai = keys.index(ca) if keys and ca in keys else int(ca)
    stem = blocks(item.get("question") or item.get("stem", ""))
    norm = re.sub(r"\W+", " ", stem.lower()).strip()
    if norm in stems: skipped.append((item.get("id"), "duplicate stem")); continue
    correct = opts[ai]; others = [o for i, o in enumerate(opts) if i != ai]
    target = min(range(len(opts)), key=lambda k: (pos[k], random.random())); pos[target] += 1
    random.shuffle(others); others.insert(target, correct)
    count[sub] += 1; qid = f"q{sub}-{count[sub]:03d}"
    while qid in ids: count[sub] += 1; qid = f"q{sub}-{count[sub]:03d}"
    anchor = next((v for k, v in item.items() if "anchor" in k.lower()), None)
    q = {"id": qid, "domain": "D" + sub.split(".")[0], "subdomain": sub, "type": "scenario", "difficulty": 2,
         "stem": stem, "options": [blocks(o) for o in others], "answer": target,
         "explanation": blocks(item.get("explanation", "")), "references": [],
         "origin": a.origin, "originId": item.get("id"), "review": {"status": "needs-review"}}
    if anchor: q["anchor"] = blocks(anchor)
    p["questions"].append(q); ids.add(qid); stems.add(norm); added += 1
json.dump(p, open(a.pack, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Added {added} questions as needs-review. Skipped {len(skipped)}: {skipped}")
print("Next: fact-check them, fix answer-length tells, set review.status to fact-checked, then run tools/check_pack.py and build.py.")
