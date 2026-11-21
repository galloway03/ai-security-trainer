# Security policy

## Reporting a vulnerability
Email **mgalloway@amstrategiesnv.com** with a description, steps to reproduce and the version (commit) you tested.
Please don't open a public issue for a security problem. You can also use GitHub's private **Report a vulnerability** button on the repository's Security tab, if it's turned on. You'll get an acknowledgment within 5 business days.
The same policy is shown in the app under **Disclosure → Security** and in `/.well-known/security.txt`.

## Scope
The static app (`index.html`, `engine.template.html`), the build script and the tools in `tools/`.
Content accuracy problems (a wrong answer key) are welcome too, but aren't security issues.

## How the app is protected
- No server, accounts or network calls. Progress stays in the browser's localStorage.
- Content Security Policy pinned to the SHA-256 hash of the app script; no inline handlers, eval, frames,
  outside images, fonts or connections.
- All pack and progress text is escaped before display; links render only for https URLs.
- Packs, sessions, profiles and progress read from storage are validated by type; prototype keys are dropped.
- Pack data is embedded with `<`, `>` and `&` escaped so it can't break out of its script element.
- Replacing the built-in pack requires confirmation.

## Known limits
- GitHub Pages can't send HTTP headers, and `frame-ancestors` doesn't work from a `<meta>` tag, so the page
  can be framed by another site. It holds no credentials and destructive actions ask for confirmation.
- Anyone using the same browser profile can see every practitioner's progress. Practitioners aren't accounts.
