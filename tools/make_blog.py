"""Build a branded, SEO-optimised blog article page for Satnampal Singh and refresh the blog index.

Usage: python3 tools/make_blog.py article.json
Writes:  blog/<slug>/index.html   (the article)
         blog/index.html          (list of all articles, newest first)
         blog/articles.json       (registry the index is built from)
         sitemap.xml, robots.txt, .nojekyll
         posts/links.json -> "pages"[<slug>] = article URL (so daily posts / Shorts can link to it)

article.json keys:
  slug          url-safe, e.g. "fhsa-vs-rrsp-brampton-first-home"
  title         H1 / <title> (max ~65 chars)
  description   meta description (140-160 chars)
  date          YYYY-MM-DD
  category      short label, e.g. "First-Time Buyers"
  keywords      list of 5-10 search phrases
  hero_sub      one-sentence standfirst under the H1
  takeaways     3-5 short bullet strings ("Key takeaways" box)
  sections      list of {"h2": "...", "html": "<p>..</p>"} - html may use p, ul, ol, li, strong, em,
                table/thead/tbody/tr/th/td, h3, blockquote, a. No images of people.
  faq           list of {"q": "...", "a": "plain text answer"} (4-6 items)
  sources       list of {"name": "...", "url": "https://..."}
  cover         optional: path (relative to repo) of the cover image, e.g. "blog/<slug>/cover.jpg"
"""
import json, sys, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://satnampalsingh-social-images.github.io/Social-Images/"
e = lambda s: html.escape(s or "", quote=True)

AGENT = {
    "name": "Satnampal Singh", "title": "Sales Representative",
    "brokerage": "Royal Canadian Realty, Brokerage", "phone": "647-780-2560", "tel": "+16477802560",
    "email": "ssingh@royalcanadianrealty.com",
    "sites": ["https://www.findyourhouseingta.com/", "https://www.dreamhomeseller.ca/"],
    "linkedin": "https://www.linkedin.com/in/satnampalsingh",
    "instagram": "https://www.instagram.com/akshomes/",
}
OFFICES = [
    ("Mississauga", "Unit 1 - 2896 Slough St", "Mississauga", "L4T 1G3", "Peel Region & West GTA"),
    ("Markham", "Suite 206 - 3 Centre St", "Markham", "L3P 3P9", "York, Durham & North/East GTA"),
    ("Kitchener", "Suite 2B - 625 King St E", "Kitchener", "N2G 2M2", "Waterloo Region"),
    ("Hamilton", "Suite 300 - 163 Centennial Pkwy N", "Hamilton", "L8E 1H8", "Hamilton-Burlington Area"),
]
HOURS = "Mon–Fri 9am–6pm · Sat 11am–6pm · Sun 10am–5pm"
AREAS = ["Toronto", "Peel", "York", "Durham", "Halton", "Hamilton", "Waterloo Region", "Brampton", "Mississauga"]

CSS = """
:root{--red:#e8323a;--red-d:#b8202a;--red-dd:#9c1a22;--gold-l:#f4eb8d;--gold:#d9b25e;--gold-d:#b07a3c;--ink:#31312f;--muted:#5d5d59;--bg:#ffffff;--soft:#faf6ee;--line:#e8e1d2}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:400 18px/1.7 Lato,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--red-d)}a:hover{color:var(--red-dd)}
.wrap{max-width:780px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:10;background:#fff;border-bottom:3px solid var(--red);box-shadow:0 2px 10px rgba(0,0,0,.05)}
header.top .bar{max-width:1100px;margin:0 auto;padding:10px 20px;display:flex;align-items:center;justify-content:space-between;gap:12px}
header.top img{height:46px;width:auto;display:block}
header.top .call{background:var(--red);color:#fff;text-decoration:none;font-weight:700;padding:10px 16px;border-radius:999px;font-size:15px;white-space:nowrap}
header.top .call:hover{background:var(--red-d);color:#fff}
.hero{background:linear-gradient(135deg,var(--red-d),var(--red-dd));color:#fff;padding:56px 0 48px}
.hero .cat{display:inline-block;background:linear-gradient(90deg,var(--gold-d),var(--gold-l));color:var(--ink);font-weight:900;font-size:13px;letter-spacing:.08em;text-transform:uppercase;padding:5px 12px;border-radius:4px}
.hero h1{font:900 clamp(32px,5.5vw,48px)/1.15 'Playfair Display',Georgia,serif;margin:16px 0 14px}
.hero p.sub{font-size:20px;margin:0;color:#fff}
.hero .meta{margin-top:18px;font-size:15px;color:#fff;opacity:.95}
.gold-rule{height:6px;background:linear-gradient(90deg,var(--gold-d),var(--gold-l),var(--gold-d))}
main{padding:36px 0 20px}
.take{background:var(--soft);border-left:6px solid var(--gold-d);border-radius:8px;padding:18px 22px;margin:0 0 32px}
.take h2{font:700 22px/1.3 'Playfair Display',Georgia,serif;margin:0 0 8px}
.take ul{margin:0;padding-left:22px}
article h2{font:900 30px/1.25 'Playfair Display',Georgia,serif;margin:44px 0 12px;color:var(--ink)}
article h2::after{content:"";display:block;width:56px;height:4px;background:var(--red);margin-top:10px;border-radius:2px}
article h3{font:700 22px/1.3 'Playfair Display',Georgia,serif;margin:28px 0 8px}
article table{width:100%;border-collapse:collapse;margin:18px 0;font-size:16px;display:block;overflow-x:auto}
article th{background:var(--red-d);color:#fff;text-align:left;padding:10px 12px;white-space:nowrap}
article td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
article tr:nth-child(even) td{background:var(--soft)}
article blockquote{margin:20px 0;padding:14px 20px;border-left:5px solid var(--red);background:#fff4f4;border-radius:6px}
.note{font-size:15px;color:var(--muted);border-top:1px solid var(--line);margin-top:36px;padding-top:14px}
.faq h2{font:900 30px/1.25 'Playfair Display',Georgia,serif;margin:44px 0 14px}
.faq details{border:1px solid var(--line);border-radius:8px;margin:10px 0;background:#fff}
.faq summary{cursor:pointer;font-weight:700;padding:14px 18px;list-style:none;position:relative;padding-right:44px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:18px;top:10px;font-size:24px;color:var(--red)}
.faq details[open] summary::after{content:"–"}
.faq details p{margin:0;padding:0 18px 16px}
.cta{background:linear-gradient(135deg,var(--red-d),var(--red-dd));color:#fff;border-radius:14px;padding:30px 26px;margin:44px 0 10px;text-align:center}
.cta h2{font:900 28px/1.25 'Playfair Display',Georgia,serif;margin:0 0 8px;color:#fff}
.cta p{margin:0 0 18px;color:#fff}
.cta .btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.cta a{display:inline-block;text-decoration:none;font-weight:900;padding:13px 22px;border-radius:999px}
.cta a.p{background:linear-gradient(90deg,var(--gold-d),var(--gold-l));color:var(--ink)}
.cta a.s{background:#fff;color:var(--red-dd)}
.sources{font-size:15px}.sources li{margin:4px 0}
footer.site{background:var(--ink);color:#fff;margin-top:48px;padding:36px 0 28px;font-size:15px}
footer.site .grid{max-width:1100px;margin:0 auto;padding:0 20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:22px}
footer.site h3{font:700 18px/1.3 'Playfair Display',Georgia,serif;margin:0 0 6px;color:var(--gold-l)}
footer.site p{margin:0;color:#fff}footer.site a{color:#fff}
footer.site .agent{max-width:1100px;margin:0 auto 22px;padding:0 20px}
footer.site .agent strong{font-size:20px}
footer.site .legal{max-width:1100px;margin:24px auto 0;padding:16px 20px 0;border-top:1px solid #55554f;color:#d8d8d2;font-size:13px}
.list{display:grid;gap:18px;margin:8px 0 30px}
.card{display:block;text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:20px 22px;border-top:5px solid var(--red);background:#fff}
.card:hover{box-shadow:0 6px 20px rgba(0,0,0,.08);color:var(--ink)}
.card .cat{font-size:12px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:var(--gold-d)}
.card h2{font:900 23px/1.3 'Playfair Display',Georgia,serif;margin:6px 0}
.card p{margin:0;color:var(--muted);font-size:16px}
@media (max-width:600px){body{font-size:17px}header.top img{height:38px}.hero{padding:40px 0 36px}article h2,.faq h2{font-size:26px}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">')


def agent_schema():
    return {
        "@type": "RealEstateAgent", "@id": BASE + "#agent", "name": AGENT["name"], "jobTitle": AGENT["title"],
        "telephone": AGENT["tel"], "email": AGENT["email"], "url": AGENT["sites"][0],
        "sameAs": AGENT["sites"] + [AGENT["linkedin"], AGENT["instagram"]],
        "worksFor": {"@type": "RealEstateAgent", "name": AGENT["brokerage"]},
        "areaServed": [{"@type": "Place", "name": a + ", Ontario"} for a in AREAS],
        "award": "Royal Canadian Realty Gold Club Award Winner (August 2026)",
        "openingHours": ["Mo-Fr 09:00-18:00", "Sa 11:00-18:00", "Su 10:00-17:00"],
        "department": [{"@type": "RealEstateAgent", "name": f"{AGENT['brokerage']} – {o[0]}",
                        "address": {"@type": "PostalAddress", "streetAddress": o[1], "addressLocality": o[2],
                                    "addressRegion": "ON", "postalCode": o[3], "addressCountry": "CA"},
                        "areaServed": o[4], "telephone": AGENT["tel"]} for o in OFFICES],
    }


def header(home):
    return (f'<header class="top"><div class="bar"><a href="{home}" aria-label="Satnampal Singh blog home">'
            f'<img src="{BASE}assets/brand/logo-gold.png" alt="Royal Canadian Realty, Brokerage" width="86" height="46"></a>'
            f'<a class="call" href="tel:{AGENT["tel"]}">Call {AGENT["phone"]}</a></div></header>')


def footer():
    offices = "".join(f'<div><h3>{e(o[0])} Office</h3><p>{e(o[1])}<br>{e(o[2])}, ON {e(o[3])}<br>Serving {e(o[4])}</p></div>' for o in OFFICES)
    return (f'<footer class="site"><div class="agent"><strong>{AGENT["name"]}</strong><br>{AGENT["title"]} | {AGENT["brokerage"]}<br>'
            f'Gold Club Award Winner · Believe In The Best<br>'
            f'📞 <a href="tel:{AGENT["tel"]}">{AGENT["phone"]}</a> · ✉️ <a href="mailto:{AGENT["email"]}">{AGENT["email"]}</a><br>'
            f'🌐 <a href="{AGENT["sites"][0]}">FindYourHouseInGTA.com</a> · <a href="{AGENT["sites"][1]}">DreamHomeSeller.ca</a> · '
            f'<a href="{AGENT["linkedin"]}">LinkedIn</a> · <a href="{AGENT["instagram"]}">Instagram</a><br>Hours: {HOURS}</div>'
            f'<div class="grid">{offices}</div>'
            f'<div class="legal">This article is general information, not financial, legal or tax advice. Programs, rates and limits change; '
            f'confirm your situation with a licensed mortgage professional, lawyer or accountant. Not intended to solicit buyers or sellers already under contract. '
            f'© {datetime.date.today().year} {AGENT["name"]}, {AGENT["brokerage"]}.</div></footer>')


def page(title, desc, url, body, schema, og_img, og_type="article", keywords=None):
    kw = f'<meta name="keywords" content="{e(", ".join(keywords))}">' if keywords else ""
    return f"""<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{kw}
<meta name="author" content="Satnampal Singh"><meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og_img}"><meta property="og:site_name" content="Satnampal Singh – GTA Real Estate">
<meta property="og:locale" content="en_CA"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{og_img}">
<link rel="icon" href="{BASE}assets/brand/logo-gold.png">{FONTS}<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>
<body>{body}</body></html>"""


def build_article(a):
    url = f"{BASE}blog/{a['slug']}/"
    cover = BASE + a["cover"] if a.get("cover") else BASE + "assets/brand/logo-gold.png"
    pretty = datetime.date.fromisoformat(a["date"]).strftime("%B %-d, %Y")
    words = sum(len(s["html"].split()) for s in a["sections"])
    mins = max(3, round(words / 220))
    take = "".join(f"<li>{e(t)}</li>" for t in a["takeaways"])
    secs = "".join(f'<section><h2 id="s{i}">{e(s["h2"])}</h2>{s["html"]}</section>' for i, s in enumerate(a["sections"]))
    faq = "".join(f"<details><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>" for f in a["faq"])
    srcs = "".join(f'<li><a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s["name"])}</a></li>' for s in a.get("sources", []))
    book = f"{AGENT['sites'][0]}?utm_source=blog&utm_medium=article&utm_campaign={a['slug']}"
    body = (header(BASE + "blog/") +
            f'<div class="hero"><div class="wrap"><span class="cat">{e(a["category"])}</span><h1>{e(a["title"])}</h1>'
            f'<p class="sub">{e(a["hero_sub"])}</p><div class="meta">By {AGENT["name"]}, {AGENT["title"]} · {pretty} · {mins} min read</div></div></div>'
            f'<div class="gold-rule"></div><main><div class="wrap"><div class="take"><h2>Key takeaways</h2><ul>{take}</ul></div>'
            f'<article>{secs}</article>'
            f'<section class="faq"><h2>Frequently asked questions</h2>{faq}</section>'
            f'<div class="cta"><h2>Talk it through with Satnampal</h2><p>Book a free 15-minute call — no pressure, just a clear plan for your next move in the GTA.</p>'
            f'<div class="btns"><a class="p" href="tel:{AGENT["tel"]}">📞 {AGENT["phone"]}</a><a class="s" href="{book}">Visit FindYourHouseInGTA.com</a></div></div>'
            + (f'<div class="note"><strong>Sources</strong><ul class="sources">{srcs}</ul></div>' if srcs else "") +
            '</div></main>' + footer())
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": a["title"], "description": a["description"], "datePublished": a["date"],
         "dateModified": a["date"], "inLanguage": "en-CA", "mainEntityOfPage": url, "image": cover,
         "keywords": ", ".join(a.get("keywords", [])), "articleSection": a["category"], "wordCount": words,
         "author": {"@id": BASE + "#agent"}, "publisher": {"@id": BASE + "#agent"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"],
                                              "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in a["faq"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Blog", "item": BASE + "blog/"},
            {"@type": "ListItem", "position": 2, "name": a["title"], "item": url}]},
        agent_schema()]}
    out = os.path.join(ROOT, "blog", a["slug"])
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(page(a["title"] + " | Satnampal Singh", a["description"], url, body, schema, cover, keywords=a.get("keywords")))
    with open(os.path.join(out, "boldtrail.html"), "w") as f:
        f.write(boldtrail_fragment(a, cover))
    return url


def boldtrail_fragment(a, cover):
    """Body-only HTML with inline styles, for pasting into the BoldTrail blog editor's source/HTML view."""
    R, RD, GD, INK, SOFT = "#e8323a", "#b8202a", "#b07a3c", "#31312f", "#faf6ee"
    h2 = f'style="font-family:Georgia,serif;color:{INK};border-bottom:3px solid {R};padding-bottom:6px;margin:32px 0 12px"'
    take = "".join(f"<li>{e(t)}</li>" for t in a["takeaways"])
    secs = "".join(f'<h2 {h2}>{e(s["h2"])}</h2>{s["html"]}' for s in a["sections"])
    faq = "".join(f'<h3 style="font-family:Georgia,serif;color:{RD};margin:18px 0 6px">{e(f["q"])}</h3><p>{e(f["a"])}</p>' for f in a["faq"])
    srcs = "".join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a></li>' for s in a.get("sources", []))
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in a["faq"]]}, ensure_ascii=False)
    return (f'<!-- BoldTrail paste version: {a["title"]} -->\n'
            f'<div style="font-family:Lato,Arial,sans-serif;color:{INK};line-height:1.7;font-size:17px">'
            f'<p><img src="{cover}" alt="{e(a["title"])}" style="max-width:100%;height:auto;border-radius:8px"></p>'
            f'<p style="font-size:19px"><strong>{e(a["hero_sub"])}</strong></p>'
            f'<div style="background:{SOFT};border-left:6px solid {GD};padding:14px 20px;border-radius:6px;margin:20px 0">'
            f'<p style="margin:0 0 6px;font-weight:bold">Key takeaways</p><ul style="margin:0">{take}</ul></div>'
            f'{secs}<h2 {h2}>Frequently asked questions</h2>{faq}'
            f'<div style="background:{RD};color:#fff;padding:22px;border-radius:10px;margin:30px 0;text-align:center">'
            f'<p style="font-size:22px;font-family:Georgia,serif;margin:0 0 8px;color:#fff"><strong>Talk it through with Satnampal</strong></p>'
            f'<p style="margin:0 0 10px;color:#fff">Book a free 15-minute call — no pressure, just a clear plan for your next move in the GTA.</p>'
            f'<p style="margin:0;color:#fff">📞 <a href="tel:{AGENT["tel"]}" style="color:#fff">{AGENT["phone"]}</a> · ✉️ '
            f'<a href="mailto:{AGENT["email"]}" style="color:#fff">{AGENT["email"]}</a></p></div>'
            + (f'<p style="font-size:14px"><strong>Sources</strong></p><ul style="font-size:14px">{srcs}</ul>' if srcs else "") +
            f'<p style="font-size:13px;color:#5d5d59">{AGENT["name"]}, {AGENT["title"]} | {AGENT["brokerage"]} | Gold Club Award Winner · Believe In The Best. '
            f'General information only, not financial, legal or tax advice.</p></div>\n'
            f'<script type="application/ld+json">{faq_ld}</script>\n')


def build_index(reg):
    url = BASE + "blog/"
    cards = "".join(f'<a class="card" href="{BASE}blog/{r["slug"]}/"><span class="cat">{e(r["category"])} · {e(r["date"])}</span>'
                    f'<h2>{e(r["title"])}</h2><p>{e(r["description"])}</p></a>' for r in reg)
    body = (header(url) + '<div class="hero"><div class="wrap"><span class="cat">GTA Real Estate Blog</span>'
            '<h1>Real estate advice for Brampton &amp; the GTA</h1><p class="sub">Plain-English guides for first-time buyers, sellers and investors '
            'from Satnampal Singh, Royal Canadian Realty.</p></div></div><div class="gold-rule"></div>'
            f'<main><div class="wrap"><div class="list">{cards}</div></div></main>' + footer())
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "name": "Satnampal Singh – GTA Real Estate Blog", "url": url, "author": {"@id": BASE + "#agent"},
         "blogPost": [{"@type": "BlogPosting", "headline": r["title"], "url": f"{BASE}blog/{r['slug']}/", "datePublished": r["date"]} for r in reg]},
        agent_schema()]}
    with open(os.path.join(ROOT, "blog", "index.html"), "w") as f:
        f.write(page("GTA Real Estate Blog | Satnampal Singh, Royal Canadian Realty",
                     "Guides for first-time buyers, sellers and investors in Brampton, Mississauga and the GTA by Satnampal Singh, Gold Club Award Winner.",
                     url, body, schema, BASE + "assets/brand/logo-gold.png", og_type="website"))
    urls = [url] + [f"{BASE}blog/{r['slug']}/" for r in reg]
    lm = {url: reg[0]["date"] if reg else datetime.date.today().isoformat()}
    lm.update({f"{BASE}blog/{r['slug']}/": r["date"] for r in reg})
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join(f"  <url><loc>{u}</loc><lastmod>{lm[u]}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    open(os.path.join(ROOT, ".nojekyll"), "w").close()


def main():
    a = json.load(open(sys.argv[1]))
    url = build_article(a)
    regp = os.path.join(ROOT, "blog", "articles.json")
    reg = json.load(open(regp)) if os.path.exists(regp) else []
    reg = [r for r in reg if r["slug"] != a["slug"]] + [{k: a[k] for k in ("slug", "title", "description", "date", "category")}]
    reg.sort(key=lambda r: r["date"], reverse=True)
    json.dump(reg, open(regp, "w"), indent=2, ensure_ascii=False)
    build_index(reg)
    lp = os.path.join(ROOT, "posts", "links.json")
    links = json.load(open(lp))
    links.setdefault("pages", {})[a["slug"]] = url
    with open(lp, "w") as f:
        json.dump(links, f, indent=2, ensure_ascii=False); f.write("\n")
    print(url)


if __name__ == "__main__":
    main()
