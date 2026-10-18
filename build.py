#!/usr/bin/env python3
"""
Static site generator for Brahim's hub.
Reads:  content/*.md   (front-matter + light markdown)
Writes: posts/<slug>.html  +  blog.html  +  sitemap.xml  +  robots.txt

No dependencies. Run:  python3 build.py
Affiliate tag lives in TAG below - change it once and rebuild.
"""
import os, re, glob, html, urllib.parse, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
TAG = "brahimpicks-21"                     # <-- Amazon Associates tracking ID
SITE = "https://benbrahim93.github.io"
AUTHOR = "Brahim Ben Sliman"

# ───────────────────────────── markdown-lite ─────────────────────────────
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)",
               r'<a href="\2" target="_blank" rel="noopener sponsored">\1</a>', t)
    return t

def aff_link(query):
    q = urllib.parse.quote_plus(query)
    return f"https://www.amazon.co.uk/s?k={q}&amp;tag={TAG}"

def render(md):
    md = md.strip()
    out, i = [], 0
    blocks = re.split(r"\n\s*\n", md)
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith("### "):
            out.append(f"<h3>{inline(b[4:])}</h3>")
        elif b.startswith("## "):
            out.append(f"<h2>{inline(b[3:])}</h2>")
        elif b.startswith("> "):
            txt = " ".join(l[2:].strip() for l in b.splitlines() if l.startswith("> "))
            out.append(f'<div class="callout">{inline(txt)}</div>')
        elif re.match(r"^[-*] ", b):
            items = "\n".join(
                f"<li>{inline(l.lstrip('-* ').strip())}</li>"
                for l in b.splitlines() if l.strip())
            out.append(f"<ul>{items}</ul>")
        elif re.match(r"^\d+\. ", b):
            items = "\n".join(
                f"<li>{inline(re.sub(r'^[0-9]+[.] ', '', l.strip()))}</li>"
                for l in b.splitlines() if l.strip())
            out.append(f"<ol>{items}</ol>")
        else:
            out.append(f"<p>{inline(b)}</p>")
    doc = "\n".join(out)
    # affiliate search buttons
    def _link(m):
        return f'<a class="btn p" href="{aff_link(m.group(1))}" target="_blank" rel="noopener sponsored">See current options: {html.escape(m.group(1))} ↗</a>'
    doc = re.sub(r"\{\{LINK:(.+?)\}\}", _link, doc)
    return doc

def front_matter(text):
    meta, body = {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    return meta, body

# ───────────────────────────── page shells ─────────────────────────────
CSS = """
:root{--bg:#0b0f17;--panel:#131a26;--panel2:#182130;--line:#243044;--txt:#e8eef8;
--mut:#93a3bb;--acc:#2ee6a8;--acc2:#7c6cff}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);line-height:1.7;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
-webkit-font-smoothing:antialiased}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
nav{position:sticky;top:0;z-index:20;backdrop-filter:blur(12px);background:rgba(11,15,23,.85);
border-bottom:1px solid var(--line)}
nav .w{max-width:960px;margin:0 auto;padding:0 20px;height:58px;display:flex;
align-items:center;justify-content:space-between}
.brand{font-weight:700;letter-spacing:-.02em;color:var(--txt)}
.brand span{color:var(--acc)}
.navlinks{display:flex;gap:20px;font-size:14px;color:var(--mut)}
.navlinks a{color:var(--mut)}
.navlinks a:hover{color:var(--txt);text-decoration:none}
@media(max-width:640px){.navlinks{display:none}}
main{max-width:720px;margin:0 auto;padding:52px 20px 40px}
.crumb{font-size:13px;color:var(--mut);margin-bottom:22px}
h1{font-size:clamp(28px,5.4vw,40px);line-height:1.14;letter-spacing:-.03em;font-weight:800;
margin-bottom:14px}
.meta{color:var(--mut);font-size:13.5px;padding-bottom:22px;border-bottom:1px solid var(--line);
margin-bottom:30px}
.disc{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--acc);
border-radius:8px;padding:14px 16px;font-size:13.5px;color:var(--mut);margin:0 0 30px}
article p{color:#d3dcea;margin:0 0 20px;font-size:16.5px}
article h2{font-size:clamp(21px,3.4vw,25px);letter-spacing:-.02em;font-weight:750;
margin:38px 0 14px}
article h3{font-size:18px;margin:26px 0 10px;font-weight:700}
article ul,article ol{margin:0 0 20px 22px;color:#d3dcea}
article li{margin-bottom:9px}
article strong{color:#fff}
article a{text-decoration:underline}
.callout{background:var(--panel);border:1px solid var(--line);border-radius:10px;
padding:16px 18px;color:#cfd9e8;font-size:15.5px;margin:0 0 22px}
.btn{display:inline-block;padding:12px 18px;border-radius:10px;font-weight:600;font-size:14.5px;
margin:2px 0 22px;border:1px solid var(--line)}
.btn:hover{text-decoration:none;transform:translateY(-2px)}
.btn.p{background:linear-gradient(135deg,var(--acc),var(--acc2));color:#08111a;border:none}
.rel{margin-top:46px;padding-top:26px;border-top:1px solid var(--line)}
.rel h2{font-size:16px;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);
margin-bottom:16px}
.rel a{display:block;padding:13px 16px;border:1px solid var(--line);border-radius:10px;
margin-bottom:9px;color:var(--txt);background:var(--panel)}
.rel a:hover{background:var(--panel2);text-decoration:none}
footer{max-width:720px;margin:0 auto;padding:30px 20px 70px;color:var(--mut);font-size:13px;
border-top:1px solid var(--line)}
.note{margin-top:10px;color:#6b7c94;font-size:12.5px}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));margin-top:30px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px;
transition:.18s;display:block;color:var(--txt)}
.card:hover{border-color:#31435e;transform:translateY(-3px);text-decoration:none;background:var(--panel2)}
.card h3{font-size:17px;margin-bottom:8px;letter-spacing:-.01em}
.card p{color:var(--mut);font-size:14.5px}
.card .rt{color:var(--acc);font-size:13px;font-weight:600;margin-top:14px;display:block}
.wide{max-width:960px}
"""

def nav():
    return ('<nav><div class="w"><a class="brand" href="/">Brahim<span>.</span></a>'
            '<div class="navlinks"><a href="/blog.html">Guides</a><a href="/winter.html">Winter</a>'
            '<a href="/october.html">This month</a><a href="/about.html">About</a>'
            '<a href="/#work">Work with me</a><a href="/#links">Links</a>'
            '<a href="/#picks">Picks</a></div></div></nav>')

FOOT = ('<footer><div>© %d %s. Written and researched by hand. '
        '<a href="/privacy.html">Privacy &amp; affiliate disclosure</a></div>'
        '<div class="note">As an Amazon Associate I earn from qualifying purchases. '
        'Links marked ↗ are affiliate links — they cost you nothing extra.</div></footer>'
        % (datetime.date.today().year, AUTHOR))

def head(title, desc, canonical):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#0b0f17">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>{CSS}</style>
</head>
<body>
{nav()}"""

# ───────────────────────────── hubs (seasonal clusters) ─────────────────────────────
HUBS = [
    dict(file="winter.html",
         title="Get winter-ready without wasting money",
         lead="Every winter guide in one place: fix the free things first, seal the cheap things second, then buy the right machine once.",
         cards=[
             ("Heated clothes airers vs tumble dryers", "The honest watts x hours comparison, and the loads where each one wins.", "heated-clothes-airer-dryer"),
             ("Dehumidifiers: compressor or desiccant", "Which type suits your room, and why the £50–£120 band is usually the smart money.", "dehumidifier-choice"),
             ("Condensation on windows: the fix ladder", "Free fixes first, absorbers for corners, a machine for the real problem.", "condensation-fix"),
             ("Draught-proofing: what pays for itself", "Letterbox to chimney: the payback ladder, and where it's just tape.", "draught-proofing"),
             ("Electric heaters that are cheap to run", "The maths behind 'cheap to run', and what actually controls the cost.", "electric-heater-running-cost"),
             ("The energy-saving upgrade kit", "LED bulbs, timer sockets and monitoring plugs — sorted from the gimmicks.", "energy-saving-plugs-upgrades"),
         ],
         btns=["heated clothes airer", "dehumidifier desiccant", "draught excluder tape"],
         note="Order matters more than brand: free fixes, then cheap fixes, then the right machine."),
    dict(file="october.html",
         title="October: what's worth buying right now",
         lead="The mid-October honest list. What makes sense this month, what to wait for, and what to skip.",
         cards=[
             ("Fix the free stuff first", "Ventilation and drying habits before anybody spends a pound.", "condensation-fix"),
             ("Seal the gaps before the cold lands", "Draught-proofing pays back quickest in October, not January.", "draught-proofing"),
             ("Dry laundry without the tumble dryer", "Heated airers: cheaper now than when the December rush bites.", "heated-clothes-airer-dryer"),
             ("Beat the damp before it beats you", "Dehumidifiers: buy before the condensation weeks arrive.", "dehumidifier-choice"),
             ("Warmer nights, small spend", "A mattress topper is the cheapest comfort win of the season.", "mattress-topper-guide"),
             ("Cuts bills without a sales pitch", "The boring, reliable energy upgrades — and the gimmicks to skip.", "energy-saving-plugs-upgrades"),
         ],
         btns=["heated clothes airer", "dehumidifier desiccant", "draught excluder tape", "led bulbs energy saving"],
         note="Electronics can wait for Black Friday in late November. Heating prep doesn't wait for anything."),
    dict(file="kitchen.html",
         title="The kitchen, without the marketing",
         lead="Small appliances are where most household money is wasted. These guides slow that down.",
         cards=[
             ("Air fryers: what size you actually need", "Litres per person, dual baskets, and the capacity trap.", "air-fryer-size-guide"),
             ("Espresso machines under £200", "Why the grinder comes first, and where the money should go.", "budget-espresso-machine"),
             ("Smart plugs: get them working first try", "Protocols, sockets and what never to plug into one.", "smart-plugs-alexa-uk"),
         ],
         btns=["air fryer dual basket", "espresso machine and grinder", "fast boil kettle"],
         note=None),
    dict(file="home-office.html",
         title="Home office: buy it once, properly",
         lead="The room you work in eight hours a day. Spend where your back notices, not where the marketing shouts.",
         cards=[
             ("Standing desks that don't wobble", "Why stability is the whole product, and what causes wobble.", "home-office-standing-desk"),
             ("Office chairs: what your back needs", "The five adjustments that matter, and the price band where they exist.", "office-chair-guide"),
             ("Home office lighting", "Why your screen is fine and your room isn't.", "desk-lamps-home-office"),
             ("Keyboards and mice", "Stop paying for specs you can't feel.", "mechanical-keyboard-mouse"),
         ],
         btns=["standing desk frame", "ergonomic office chair", "desk lamp home office"],
         note=None),
]

def shopbtn(query):
    return (f'<a class="btn p" href="{aff_link(query)}" target="_blank" rel="noopener sponsored">'
            f'See {html.escape(query)} ↗</a>')

def build_hubs():
    names = []
    for h in HUBS:
        cards = "\n".join(
            f'<a class="card" href="/posts/{slug}.html"><h3>{html.escape(t)}</h3>'
            f'<p>{html.escape(d)}</p><span class="rt">Read the guide →</span></a>'
            for (t, d, slug) in h["cards"])
        btns = "\n".join(shopbtn(q) for q in h["btns"])
        note = f'<div class="callout">{html.escape(h["note"])}</div>' if h.get("note") else ""
        page = (head(h["title"] + " | " + AUTHOR, h["lead"], f"{SITE}/{h['file']}")
                + f"""
<main class="wide">
  <div class="crumb"><a href="/">Home</a> › <a href="/blog.html">Guides</a> › {html.escape(h["title"])}</div>
  <h1>{html.escape(h["title"])}</h1>
  <p style="color:var(--mut);max-width:640px">{html.escape(h["lead"])}</p>
  {note}
  <div class="grid">{cards}</div>
  <div style="margin-top:38px">
    <h2 style="font-size:22px;margin-bottom:4px">Go straight to Amazon</h2>
    <p style="color:var(--mut);margin-bottom:14px">Tagged search links — no extra cost to you, they keep this site alive.</p>
    {btns}
  </div>
</main>
""" + FOOT + "\n</body>\n</html>")
        open(os.path.join(ROOT, h["file"]), "w", encoding="utf-8").write(page)
        names.append(h["file"])
    print(f"built {len(names)} hub pages: " + ", ".join(names))
    return names

# ───────────────────────────── build ─────────────────────────────
def build():
    os.makedirs(os.path.join(ROOT, "posts"), exist_ok=True)
    posts = []
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "*.md"))):
        meta, body = front_matter(open(path, encoding="utf-8").read())
        slug = meta.get("slug") or os.path.splitext(os.path.basename(path))[0]
        title = meta.get("title", slug)
        desc = meta.get("desc", "")
        date = meta.get("date", datetime.date.today().isoformat())
        rt = meta.get("readtime", "5 min")
        url = f"{SITE}/posts/{slug}.html"
        art = render(body)
        related = ""  # filled in second pass
        page = f"""{head(title + " | " + AUTHOR, desc, url)}
<main>
  <div class="crumb"><a href="/">Home</a> › <a href="/blog.html">Guides</a> › {html.escape(title)}</div>
  <h1>{html.escape(title)}</h1>
  <div class="meta">By {AUTHOR} · Updated {date} · {rt} read</div>
  <div class="disc"><strong>Heads up:</strong> this page contains affiliate links. If you buy
  through them I may earn a small commission — it never costs you more, and it doesn't change
  what I recommend.</div>
  <article>{art}</article>
  <div class="rel"><h2>Read next</h2>{{{{RELATED}}}}</div>
</main>
{FOOT}
</body>
</html>"""
        with open(os.path.join(ROOT, "posts", slug + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        posts.append(dict(slug=slug, title=title, desc=desc, date=date, rt=rt, url=url))

    posts.sort(key=lambda p: p["date"], reverse=True)

    # second pass: inject 3 related links per post
    for p in posts:
        rel = [q for q in posts if q["slug"] != p["slug"]][:3]
        block = "\n".join(f'<a href="/posts/{q["slug"]}.html">{html.escape(q["title"])}</a>'
                          for q in rel)
        fp = os.path.join(ROOT, "posts", p["slug"] + ".html")
        s = open(fp, encoding="utf-8").read().replace("{{RELATED}}", block)
        open(fp, "w", encoding="utf-8").write(s)

    # index of guides
    cards = "\n".join(
        f'<a class="card" href="/posts/{p["slug"]}.html"><h3>{html.escape(p["title"])}</h3>'
        f'<p>{html.escape(p["desc"])}</p><span class="rt">{p["rt"]} read →</span></a>'
        for p in posts)
    idx = f"""{head("Guides — honest buying advice | " + AUTHOR,
                    "Straight-talking buying guides: what actually matters, what to spend, and what to avoid.", SITE + "/blog.html")}
<main class="wide">
  <div class="crumb"><a href="/">Home</a> › Guides</div>
  <h1>Buying guides</h1>
  <p style="color:var(--mut);max-width:600px">No hype, no spec-sheet theatre. What actually
  matters, roughly what it should cost, and the mistakes that waste your money.</p>
  <div class="callout" style="max-width:640px;margin-top:24px"><strong>How I write these:</strong>
  each guide is researched properly and written to stay useful for years. Nothing here is a paid
  placement and no brand gets a better write-up for it. Where a link earns me a commission, the
  page says so at the top.</div>
  <div class="grid">{cards}</div>
</main>
{FOOT}
</body>
</html>"""
    open(os.path.join(ROOT, "blog.html"), "w", encoding="utf-8").write(idx)

    # cluster hub pages + sitemap + robots
    hub_names = build_hubs()
    urls = [SITE + "/", SITE + "/blog.html", SITE + "/about.html"] + [SITE + "/" + n for n in hub_names] + [p["url"] for p in posts]
    today = datetime.date.today().isoformat()
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "\n".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls) +
          "\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

    print(f"built {len(posts)} posts -> posts/, blog.html, sitemap.xml, robots.txt")
    for p in posts:
        print("  -", p["slug"], "|", p["date"])

if __name__ == "__main__":
    build()
