# Project rules for Claude

This repo is a static study app for the ISC2 AI Security pilot exam, owned by Mimi Galloway (A&M Strategies),
GitHub `galloway03/ai-security-trainer`, served by GitHub Pages from `main` at
https://galloway03.github.io/ai-security-trainer/. Mimi and two or three study partners use it.

## How to work here
- `index.html` is generated. Never edit it by hand. Change `engine.template.html` or the pack, then rebuild.
- Before you say a change is done, run these and confirm they pass:
  ```
  python3 tools/check_pack.py packs/isc2-ai-security-pilot.json
  python3 build.py
  python3 tools/pentest/pentest.py index.html packs/isc2-ai-security-pilot.json local   # all 14 must pass
  ```
  The pentest needs `pip install playwright` and `playwright install chromium`.
- Commit the rebuilt `index.html` with the change. CI (`.github/workflows/checks.yml`) fails if it's stale.
- Work on a branch and open a pull request; don't push straight to `main`. Say in the PR what changed,
  how it was checked, and any answer keys you're unsure of.
- When `@claude` is triggered from an issue, do what the issue asks, and nothing else, in one focused PR.
- Questions to import arrive in `incoming/`, which isn't committed. Use `tools/import_questions.py`.
- Keep this file short; it's read on every run.

## Content rules
- Accuracy over volume. Fact-check every question, answer, distractor and explanation. Check anything based
  on a standard or regulation (EU AI Act, NIST, ISO/IEC, OWASP, MITRE ATLAS) against a primary or
  authoritative source and add it to the question's `sources` list. Don't state things more firmly than
  the evidence supports.
- Only set `review.status` to `fact-checked` after that check. Flag doubtful answer keys to Mimi instead
  of silently changing them.
- Never write the word "Lego". Use "building blocks". Memory anchors go in a question's `anchor` field
  and show in the app as "Build it". Don't add toy brand names or logos anywhere.
- The only character art is Mimi's own minifig in `assets/` (logo, favicon, dashboard greeter).
  Don't add other characters or alter her likeness.
- Never add real exam questions or text copied from the reference books.
- Avoid answer-length tells: the correct option should be the longest in about 25–35% of questions.
  Distractors must be plausible, not throwaway.
- Keep the question mix at the exam weights: D1 10%, D2 17%, D3 19%, D4 18%, D5 19%, D6 17%.
- Reference locations (`chapter`, `chapterTitle`, `section`) must come from the publisher's published
  table of contents. Leave them out rather than guess.
- Remove duplicates of existing questions by concept, not just wording.

## Security rules
- Treat packs and progress backups as untrusted input. Escape all text with `esc()`; render links only
  through `safeUrl()` (https only); keep `sanitizeProgress()` for anything read from storage or pasted in.
- Keep the Content Security Policy strict. `build.py` pins `script-src` to the SHA-256 hash of the one
  inline app script: never add `'unsafe-inline'`, `'unsafe-eval'`, inline event handlers (`onclick=` and
  the like) or a second inline script. Wire events with `addEventListener`.
- No third-party requests: no CDNs, analytics or web fonts. Fonts are self-hosted in `fonts/` (OFL) and
  embedded by the build.
- Validate every value read from storage or a pack by type (`validatePack`, `sanitizeSession`,
  `sanitizeProgress`); look up views and ids with own-property checks or null-prototype maps.
- Never commit secrets. The `@claude` workflow reads `CLAUDE_CODE_OAUTH_TOKEN` from repository secrets only.
- Pin GitHub Actions to a commit SHA with the version in a comment; Dependabot proposes updates.
- Security reports go to mgalloway@amstrategiesnv.com (see `SECURITY.md`).

## Style
- Look: "Night bold". Near-black plum background (#110919), gold accent #E3B94E (brand gold #C9A84C/#C9952A),
  brand purple #2D0A4E/#4A2070, gold underline navigation, 6px corners, uppercase buttons. Sans-serif text only.
- App and docs text: plain, short sentences. Avoid jargon a study partner wouldn't know.
