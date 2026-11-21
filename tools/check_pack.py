"""Check a pack before publishing. Exits non-zero on errors.

Usage: python3 tools/check_pack.py packs/isc2-ai-security-pilot.json
"""
import json, re, sys, collections
from urllib.parse import urlparse

path = sys.argv[1] if len(sys.argv) > 1 else "packs/isc2-ai-security-pilot.json"
p = json.load(open(path, encoding="utf-8"))
errors, warnings = [], []
subs = {s["id"] for d in p["domains"] for s in d["subdomains"]}
doms = {d["id"] for d in p["domains"]}
refs = {r["id"] for r in p.get("references", [])}

if sum(d["weight"] for d in p["domains"]) != 100:
    errors.append("Domain weights don't add up to 100.")

seen_ids, seen_stems = set(), {}
for q in p["questions"]:
    qid = q.get("id", "?")
    if qid in seen_ids: errors.append(f"{qid}: duplicate id")
    seen_ids.add(qid)
    if q.get("domain") not in doms: errors.append(f"{qid}: unknown domain {q.get('domain')}")
    if q.get("subdomain") not in subs: errors.append(f"{qid}: unknown subdomain {q.get('subdomain')}")
    opts = q.get("options", [])
    if len(opts) < 2 or len(set(opts)) != len(opts): errors.append(f"{qid}: options missing or repeated")
    if not (isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(opts)): errors.append(f"{qid}: answer index out of range")
    stem = re.sub(r"\W+", " ", q.get("stem", "").lower()).strip()
    if stem in seen_stems: errors.append(f"{qid}: same stem as {seen_stems[stem]}")
    seen_stems[stem] = qid
    for r in q.get("references", []):
        rid = r if isinstance(r, str) else r.get("id")
        if rid not in refs: errors.append(f"{qid}: unknown reference {rid}")
    for s in q.get("sources", []):
        if urlparse(s.get("url", "")).scheme != "https": errors.append(f"{qid}: source URL must be https")
    if (q.get("review") or {}).get("status") != "fact-checked":
        warnings.append(f"{qid}: not fact-checked yet")

for r in p.get("references", []):
    if r.get("url") and urlparse(r["url"]).scheme != "https": errors.append(f"reference {r['id']}: URL must be https")

qs = p["questions"]
longest = sum(1 for q in qs if len(q["options"][q["answer"]]) == max(len(o) for o in q["options"]))
share = longest / len(qs)
if share > 0.35: warnings.append(f"Correct answer is the longest option in {share:.0%} of questions (aim for about 25%).")
pos = collections.Counter(q["answer"] for q in qs)
if max(pos.values()) - min(pos.values()) > max(3, len(qs) // 20): warnings.append(f"Answer positions are unbalanced: {dict(sorted(pos.items()))}")

text = json.dumps(p, ensure_ascii=False)
if re.search(r"lego", text, re.I): errors.append('The word "Lego" appears in the pack. Use "building blocks" instead.')
empty = sorted(subs - {q["subdomain"] for q in qs})
if empty: warnings.append(f"Subdomains with no questions: {', '.join(empty)}")

counts = collections.Counter(q["domain"] for q in qs)
print(f"{len(qs)} questions | by domain: {dict(sorted(counts.items()))} | correct-is-longest {share:.0%}")
for w in warnings: print("WARNING:", w)
for e in errors: print("ERROR:", e)
sys.exit(1 if errors else 0)
