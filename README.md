# AI Security Trainer (A&M Strategies)

A study app for the ISC2 AI Security pilot exam:
- daily rapid-fire checks, plus lessons for every subdomain
- flashcards, trap patterns and a day-by-day study plan
- timed practice exams weighted like the real exam (500 fact-checked questions)
- progress tracking, a blueprint and a resource library

It is one static page with no server. Each person's progress stays in their own browser.

Study partners report wrong answers, fixes and ideas from the **Feedback** page or the **Report a problem**
link under any answer or lesson. Each one opens an email to mgalloway@amstrategiesnv.com with the
question id filled in.

Independent study aid. Not affiliated with or endorsed by ISC2.

Live site (once published): https://galloway03.github.io/ai-security-trainer/

---

## 1. Move this folder to GitHub (VS Code)

You need VS Code signed in to GitHub (account `galloway03`) and Python 3.10 or later.

1. Unzip `ai-security-trainer.zip` somewhere permanent, such as `Documents/GitHub/ai-security-trainer`.
2. In VS Code, open the folder with **File → Open Folder**.
3. Open **Source Control** (the branch icon on the left) and click **Publish to GitHub**.
   - Name the repository `ai-security-trainer`. If you pick another name, update the two URLs in
     `.well-known/security.txt` and the "Live site" line above.
   - Choose **public**. GitHub Pages on a free plan needs a public repository.
     Nothing in the repo is secret: no keys, no personal data, and no real exam content.
   - When VS Code asks which files to include, include them all. `.gitignore` already leaves out
     test output and raw imports.
4. On github.com, open the repository, then **Settings → Pages**:
   - Under **Build and deployment**, set **Source** to **Deploy from a branch**, the branch to `main`,
     and the folder to `/ (root)`. Click **Save**.
   - When the page shows your site address, tick **Enforce HTTPS**.
5. Wait a minute or two, then open https://galloway03.github.io/ai-security-trainer/.
   Share that link with your study group.
6. Recommended in **Settings**:
   - **Code security**: turn on **Dependabot alerts**, **Secret scanning** and **Private vulnerability reporting**.
   - **Rules → Rulesets**: protect `main` by requiring a pull request and the **Checks** workflow to pass.
     Do this after your first push, so the setup commits can go straight to `main`.

The **Checks** workflow (`.github/workflows/checks.yml`) runs on every push and pull request. It runs
three checks, and a red X on a commit means one of them failed:
- validates the pack
- confirms `index.html` was rebuilt
- runs the 14 security tests

---

## 2. Work with Claude on this repo

Claude reads `CLAUDE.md` in every session. That file holds the project rules: fact-checking, the
building-blocks wording, security rules, brand colors and the publish checklist. Here are three ways to
work with Claude; use any of them.

### A. In VS Code (your computer)
1. Install the **Claude Code** extension by Anthropic (Extensions view → search "Claude Code").
2. Open this folder, then click the Spark icon at the top right of an open file and sign in with your
   Claude account.
3. Ask for what you need, for example: "Add these 20 questions from incoming/batch.json, fact-check
   them, rebuild and run the checks." Claude shows each change for you to approve.
4. Commit and push from Source Control when you're happy with the changes.

### B. On claude.ai (browser or phone, no setup on your computer)
1. Go to https://claude.ai/code and connect GitHub when asked. This installs the **Claude GitHub App**;
   allow it on `galloway03/ai-security-trainer`.
2. Pick the repository and describe the task. Claude works on its own branch and opens a pull request.
3. Review the pull request on GitHub. When **Checks** passes, merge it, and the site updates.

You can also attach the repo to a regular Claude chat or Project. Ask Claude to "add the
galloway03/ai-security-trainer repo" and it can read the code and push branches to it.

### C. Mention @claude in GitHub issues and pull requests (optional)
`.github/workflows/claude.yml` lets you type `@claude` in an issue or pull request comment. For example:
"@claude question q3.4-012 has the wrong answer; check it against the source and fix it."

It needs one-time setup:
1. Install the Claude GitHub App on the repo: https://github.com/apps/claude
2. On your computer, install Claude Code and run `claude setup-token` to create a token tied to your
   Claude subscription.
3. In the repo, go to **Settings → Secrets and variables → Actions → New repository secret**.
   Name it `CLAUDE_CODE_OAUTH_TOKEN` and paste the token. Never commit the token to a file.

Only people with write access to the repo can trigger `@claude`. Runs use GitHub Actions minutes and
count toward your Claude usage. If you'd rather not set this up, delete `claude.yml`; options A and B
work without it.

---

## 3. Everyday tasks

### Add questions from another system (Gemini, NotebookLM)
1. Put the export in `incoming/`. That folder is never committed.
2. Import it:
   ```bash
   python3 tools/import_questions.py incoming/new-questions.json --origin Gemini
   ```
3. Imported questions are marked `needs-review` and "Lego" becomes "building blocks". Before publishing:
   - fact-check each question against a primary source
   - add the chapter and section where one clearly fits
   - set `review.status` to `fact-checked`

   Claude can do this step with you.
4. Rebuild and check, then commit and push:
   ```bash
   python3 tools/check_pack.py packs/isc2-ai-security-pilot.json
   python3 build.py
   ```

### Change how the app works
Edit `engine.template.html`, never `index.html`. Then run `python3 build.py`.

### Security checks before publishing
```bash
pip install playwright && playwright install chromium   # first time only
python3 tools/check_pack.py packs/isc2-ai-security-pilot.json
python3 build.py
python3 tools/pentest/pentest.py index.html packs/isc2-ai-security-pilot.json release
```
All 14 tests must pass. The same checks run on GitHub automatically.

---

## What's in this repo

| Path | What it is |
| --- | --- |
| `index.html` | The built app. GitHub Pages serves this file. Generated: don't edit it by hand. |
| `engine.template.html` | The app without exam content. Edit this to change how the app works. |
| `packs/isc2-ai-security-pilot.json` | The exam pack: domains and weights, references, lessons, flashcards, trap patterns and questions. |
| `build.py` | Combines the template, pack and fonts into `index.html`. It also pins the Content Security Policy to the script hash. |
| `fonts/` | Self-hosted Inter Tight and IBM Plex Mono (SIL Open Font License), with SHA-256 sums. |
| `assets/` | Mimi's minifig: the logo (`avatar.webp`), the dashboard greeter (`greeter.webp`) and the browser-tab icon (`favicon.png`). Embedded by the build. |
| `tools/check_pack.py` | Checks a pack: structure, duplicates, answer-length tells and review status. |
| `tools/import_questions.py` | Imports questions from another system. |
| `tools/pentest/pentest.py` | The 14-test security regression (OWASP Top 10:2025). |
| `.github/workflows/checks.yml` | Runs the checks on every push and pull request. |
| `.github/workflows/claude.yml` | Optional: lets `@claude` respond in issues and pull requests. |
| `.github/ISSUE_TEMPLATE/` | Forms for reporting a wrong answer or requesting a feature. |
| `.github/dependabot.yml` | Keeps the workflow actions up to date. |
| `.claude/settings.json` | Pre-approves the project's build and check commands for Claude. |
| `CLAUDE.md` | Project rules Claude follows. |
| `SECURITY.md`, `.well-known/security.txt` | How to report a security issue. |

## Report a security issue

Email mgalloway@amstrategiesnv.com. Please don't open a public issue. See `SECURITY.md`.
