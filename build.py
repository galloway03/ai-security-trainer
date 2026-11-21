"""Build index.html from the engine template and a pack.

Usage: python3 build.py [packs/isc2-ai-security-pilot.json] [index.html]

What the build does (security notes in SECURITY.md):
- Embeds the pack as JSON with every <, > and & written as \\u escapes, so pack
  text can never close or re-open the <script> element it lives in.
- Embeds the self-hosted fonts in fonts/ and the images in assets/ as data: URIs,
  so the page makes no third-party requests.
- Computes the SHA-256 hash of the app's one inline script and writes it into the
  Content-Security-Policy, so no other inline script or event handler can run.
"""
import base64, hashlib, json, os, re, sys

here = os.path.dirname(os.path.abspath(__file__))
pack_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "packs", "isc2-ai-security-pilot.json")
out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "index.html")

pack = json.load(open(pack_path, encoding="utf-8"))
template = open(os.path.join(here, "engine.template.html"), encoding="utf-8").read()

# 1. pack data: escape characters that matter to the HTML parser
data = json.dumps(pack, ensure_ascii=False, separators=(",", ":"))
data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
data = data.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")

# 2. fonts
FONTS = [("Inter Tight", "normal", 400, "inter-tight-latin-400-normal.woff2"),
         ("Inter Tight", "italic", 400, "inter-tight-latin-400-italic.woff2"),
         ("Inter Tight", "normal", 600, "inter-tight-latin-600-normal.woff2"),
         ("Inter Tight", "normal", 800, "inter-tight-latin-800-normal.woff2"),
         ("IBM Plex Mono", "normal", 400, "ibm-plex-mono-latin-400-normal.woff2"),
         ("IBM Plex Mono", "normal", 500, "ibm-plex-mono-latin-500-normal.woff2")]
faces = []
for fam, style, wt, fn in FONTS:
    fp = os.path.join(here, "fonts", fn)
    if not os.path.exists(fp):
        continue  # fall back to the system font stack
    b64 = base64.b64encode(open(fp, "rb").read()).decode()
    faces.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{wt};font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")

# 2b. images: the owner's own minifig avatar (logo, favicon, dashboard greeter)
def data_uri(name, mime):
    fp = os.path.join(here, "assets", name)
    return f"data:{mime};base64," + base64.b64encode(open(fp, "rb").read()).decode()

html = template.replace("/*__FONTS__*/", "\n".join(faces))
html = html.replace("__AVATAR__", data_uri("avatar.webp", "image/webp"))
html = html.replace("__GREETER__", data_uri("greeter.webp", "image/webp"))
html = html.replace("__FAVICON__", data_uri("favicon.png", "image/png"))
html = html.replace("__DEFAULT_PACK__", data)

# 3. CSP hash of the single executable inline script
scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
if len(scripts) != 1:
    sys.exit(f"Expected exactly one inline app script, found {len(scripts)}")
digest = base64.b64encode(hashlib.sha256(scripts[0].encode("utf-8")).digest()).decode()
html = html.replace("'__SCRIPT_HASH__'", f"'sha256-{digest}'")
if re.search(r"<[^>]*\son[a-z]+\s*=", template.split("<script>")[0]):
    sys.exit("Inline event handler attributes are not allowed (they would be blocked by the CSP).")

# Always LF line endings: the CSP hash must match the bytes the browser receives on every OS.
open(out_path, "w", encoding="utf-8", newline="\n").write(html)
print(f"Built {os.path.relpath(out_path)} from {os.path.relpath(pack_path)}: {len(pack['questions'])} questions, "
      f"{len(faces)} embedded fonts, script-src sha256-{digest[:12]}…")
