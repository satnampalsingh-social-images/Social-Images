"""Build a branded, SEO-optimised blog article page for Satnampal Singh and refresh the blog index.

Usage: python3 tools/make_blog.py article.json
Writes:  blog/<slug>/index.html      (the article)
         blog/<slug>/boldtrail.html  (paste version for BoldTrail > Web & IDX > Blog, inline styles)
         blog/index.html             (list of all articles, newest first)
         blog/articles.json          (registry the index is built from)
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
  stats         optional, 3-4 headline numbers shown as stat cards under the hero:
                [{"value": "$60,000", "label": "Max RRSP Home Buyers' Plan withdrawal"}]
  takeaways     3-5 short bullet strings ("Key takeaways" box)
  sections      list of {"h2", "html", optional "label", optional "chart"}
                  label  short uppercase eyebrow above the h2, e.g. "THE SHORT ANSWER"
                  html   may use p, ul, ol, li, strong, em, h3, blockquote, a, and tables
                         (table/caption/thead/tbody/tfoot/tr/th/td). Design helpers (use 2-4 per article):
                           <div class="callout">..</div>                      gold-edged tip box
                           <div class="cards"><div class="c"><span class="tag">SCENARIO A</span><h3>..</h3>
                             <div class="big">$83,000</div><p>..</p></div> ... </div>   scenario/audience cards
                             (add class "featured" to one card for the red highlighted card)
                           <ol class="steps"><li>..</li></ol>                  numbered step list
                         No images of people.
                  chart  optional bar chart drawn in brand colours after the html:
                         {"title": "..", "sub": "..", "bars": [{"label": "Single buyer", "value": 84000, "display": "$84K"}]}
                         (2-6 bars; the largest bar is red, the rest gold)
  faq           list of {"q": "...", "a": "plain text answer"} (5-6 items)
  sources       list of {"name": "...", "url": "https://..."}
  cover         optional: path (relative to repo) of the cover image, e.g. "blog/<slug>/cover.jpg"
"""
import json, sys, os, html, datetime, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://satnampalsingh-social-images.github.io/Social-Images/"
RAW = "https://raw.githubusercontent.com/satnampalsingh-social-images/Social-Images/main/"  # always-on image host
SITE_BLOG = "https://www.findyourhouseingta.com/blog.php"  # his BoldTrail blog page (newest post on top)
CDN = "https://cdn.jsdelivr.net/gh/satnampalsingh-social-images/Social-Images@main/"  # image host for BoldTrail pages
e = lambda s: html.escape(s or "", quote=True)

AGENT = {
    "name": "Satnampal Singh", "title": "Sales Representative",
    "brokerage": "Royal Canadian Realty, Brokerage", "phone": "647-780-2560", "tel": "+16477802560",
    "email": "ssingh@royalcanadianrealty.com",
    "sites": ["https://www.findyourhouseingta.com/", "https://www.dreamhomeseller.ca/"],
    "linkedin": "https://www.linkedin.com/in/satnampalsingh",
    "instagram": "https://www.instagram.com/akshomes/",
}
# Royal Canadian Realty, Brokerage offices (royalcanadianrealty.com/resources/office-locations, checked 2026-11-03)
# (name, street, city, postal, serving, office phone)
OFFICES = [
    ("Mississauga", "Unit 1 - 2896 Slough St", "Mississauga", "L4T 1G3", "Peel Region & West GTA", "905-364-0727"),
    ("Markham", "Suite 206 - 3 Centre St", "Markham", "L3P 3P9", "York, Durham & North/East GTA", "905-201-0727"),
    ("Kitchener", "Suite 2B - 625 King St E", "Kitchener", "N2G 2M2", "Waterloo Region", "519-279-1198"),
    ("Hamilton", "Suite 300 - 163 Centennial Pkwy N", "Hamilton", "L8E 1H8", "Hamilton-Burlington Area", "905-218-8127"),
    ("Commercial Division", "Unit 1 - 2896 Slough St", "Mississauga", "L4T 1G3", "Commercial & investment property, GTA-wide", "905-364-0727"),
]
HOURS = "Mon–Fri 9am–6pm · Sat 11am–6pm · Sun 10am–5pm"
AREAS = ["Toronto", "Brampton", "Mississauga", "Peel", "York", "Durham", "Halton", "Hamilton", "Waterloo Region"]

RED, RED_D, RED_DD, GOLD_L, GOLD, GOLD_D, INK, SOFT = "#ED1C24", "#C4161D", "#B3141B", "#E8CF8E", "#C79A3B", "#A57E2C", "#252525", "#F5F5F5"


def maps(o):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f"Royal Canadian Realty {o[1]}, {o[2]}, ON {o[3]}")


def tel(p):
    return "+1" + p.replace("-", "")


CREST = (f'<svg viewBox="0 0 64 64" width="28" height="28" aria-hidden="true"><defs><linearGradient id="cg" x1="0" y1="0" x2="1" y2="1">'
         f'<stop offset="0" stop-color="{GOLD_L}"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>'
         f'<circle cx="32" cy="32" r="29" fill="none" stroke="url(#cg)" stroke-width="3"/><circle cx="32" cy="27" r="7" fill="url(#cg)"/>'
         f'<path d="M28 31h8l2 14H26z" fill="url(#cg)"/></svg>')

CSS = """
:root{--red:#ED1C24;--red-d:#C4161D;--red-dd:#B3141B;--gold-l:#E8CF8E;--gold:#C79A3B;--gold-d:#A57E2C;--ink:#252525;--muted:#5A5A5A;--bg:#ffffff;--soft:#F5F5F5;--line:#E2E2E2}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:400 18px/1.7 Lato,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--red-d)}a:hover{color:var(--red-dd)}
.wrap{max-width:820px;margin:0 auto;padding:0 20px}
#prog{position:fixed;top:0;left:0;height:4px;width:0;background:linear-gradient(90deg,var(--gold-d),var(--gold-l));z-index:20}
header.top{position:sticky;top:0;z-index:10;background:#fff;border-bottom:3px solid var(--red);box-shadow:0 2px 10px rgba(0,0,0,.05)}
header.top .bar{max-width:1100px;margin:0 auto;padding:10px 20px;display:flex;align-items:center;justify-content:space-between;gap:12px}
header.top img{height:46px;width:auto;display:block}
header.top .tag{font:italic 700 16px 'Playfair Display',Georgia,serif;color:var(--gold-d)}
header.top .call{background:var(--red);color:#fff;text-decoration:none;font-weight:700;padding:10px 16px;border-radius:999px;font-size:15px;white-space:nowrap}
header.top .call:hover{background:var(--red-d);color:#fff}
.hero{background:radial-gradient(900px 360px at 12% -10%,rgba(217,178,94,.35),transparent 60%),linear-gradient(150deg,var(--red-d),var(--red-dd) 70%,#8E1015);color:#fff;padding:58px 0 50px}
.hero .cat{display:inline-block;background:linear-gradient(90deg,var(--gold-d),var(--gold-l));color:var(--ink);font-weight:900;font-size:13px;letter-spacing:.08em;text-transform:uppercase;padding:5px 12px;border-radius:4px}
.hero h1{font:900 clamp(32px,5.5vw,48px)/1.15 'Playfair Display',Georgia,serif;margin:16px 0 14px;color:#fff}
.hero p.sub{font-size:20px;margin:0;color:#fff;max-width:62ch}
.hero .meta{margin-top:18px;font-size:15px;color:#fff;display:flex;flex-wrap:wrap;gap:6px 18px}
.hero .meta b{color:var(--gold-l)}
.gold-rule{height:6px;background:linear-gradient(90deg,var(--gold-d),var(--gold-l),var(--gold-d))}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:-34px auto 8px;position:relative;z-index:2}
.stat{background:#fff;border:1px solid var(--line);border-top:5px solid var(--red);border-radius:12px;padding:16px 18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}
.stat .v{font:900 30px/1.1 'Playfair Display',Georgia,serif;color:var(--red-dd)}
.stat .l{font-size:14px;color:var(--muted);margin-top:4px;line-height:1.4}
main{padding:30px 0 10px}
.take{background:var(--soft);border-left:6px solid var(--gold-d);border-radius:8px;padding:18px 22px;margin:18px 0 22px}
.take h2{font:700 22px/1.3 'Playfair Display',Georgia,serif;margin:0 0 8px}
.take ul{margin:0;padding-left:22px}
.toc{border:1px solid var(--line);border-radius:10px;padding:14px 20px;margin:0 0 10px;font-size:16px}
.toc b{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--gold-d);margin-bottom:6px}
.toc ol{margin:0;padding-left:20px}.toc li{margin:3px 0}.toc a{text-decoration:none}
article section{padding:8px 0}
article section.tint{background:var(--soft);margin:24px -20px;padding:10px 20px 26px;border-radius:14px}
.label{font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase;color:var(--red);margin:30px 0 -4px}
article h2{font:900 30px/1.25 'Playfair Display',Georgia,serif;margin:36px 0 12px;color:var(--ink)}
.label+h2{margin-top:8px}
article h2::after{content:"";display:block;width:56px;height:4px;background:var(--red);margin-top:10px;border-radius:2px}
article h3{font:700 22px/1.3 'Playfair Display',Georgia,serif;margin:26px 0 8px}
.tbl{overflow-x:auto;margin:18px 0}
article table{width:100%;border-collapse:collapse;font-size:16px;background:#fff}
article caption{caption-side:top;text-align:left;font:700 18px 'Playfair Display',Georgia,serif;margin-bottom:8px;color:var(--red-dd)}
article th{background:var(--red-d);color:#fff;text-align:left;padding:10px 12px;white-space:nowrap}
article td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
article tbody tr:nth-child(even) td{background:var(--soft)}
article tfoot td{font-weight:900;background:#fbeee1;border-top:2px solid var(--gold-d)}
article blockquote{margin:20px 0;padding:14px 20px;border-left:5px solid var(--red);background:#fff4f4;border-radius:6px}
.callout{border-left:5px solid var(--gold-d);background:#fff;padding:16px 20px;border-radius:6px;margin:20px 0;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.callout strong{color:var(--red-dd)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:20px 0}
.c{background:#fff;border:1px solid var(--line);border-top:5px solid var(--gold-d);border-radius:10px;padding:18px}
.c .tag{font-size:12px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:var(--red)}
.c h3{font-size:19px;margin:4px 0 6px}
.c .big{font:900 26px/1.2 'Playfair Display',Georgia,serif;color:var(--ink);margin:4px 0}
.c p{font-size:16px;margin:6px 0 0}
.c.featured{background:linear-gradient(160deg,var(--red-d),var(--red-dd));border-top-color:var(--gold-l);color:#fff}
.c.featured .tag{color:var(--gold-l)}.c.featured h3,.c.featured .big,.c.featured p{color:#fff}
ol.steps{list-style:none;counter-reset:s;padding:0;margin:18px 0}
ol.steps li{counter-increment:s;position:relative;padding:10px 0 10px 50px;border-bottom:1px solid var(--line)}
ol.steps li:last-child{border-bottom:none}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:8px;width:34px;height:34px;border-radius:50%;background:var(--red);color:#fff;font:700 16px/34px 'Playfair Display',Georgia,serif;text-align:center}
.chart{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 18px 8px;margin:22px 0}
.chart h3{margin:0 0 2px;font-size:19px}.chart .s{font-size:14px;color:var(--muted);margin-bottom:8px}
.chart svg{width:100%;height:auto;display:block}
.faq h2{font:900 30px/1.25 'Playfair Display',Georgia,serif;margin:40px 0 14px}
.faq details{border:1px solid var(--line);border-radius:8px;margin:10px 0;background:#fff}
.faq summary{cursor:pointer;font-weight:700;padding:14px 18px;list-style:none;position:relative;padding-right:44px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:18px;top:10px;font-size:24px;color:var(--red)}
.faq details[open] summary::after{content:"–"}
.faq details p{margin:0;padding:0 18px 16px}
.author{display:flex;gap:16px;align-items:flex-start;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:34px 0 0;background:var(--soft)}
.author .mark{flex:0 0 56px;height:56px;border-radius:50%;background:var(--red-d);display:flex;align-items:center;justify-content:center}
.author p{margin:2px 0;font-size:16px}.author strong{font-size:18px}
.badge{display:inline-block;background:linear-gradient(90deg,var(--gold-d),var(--gold-l));color:var(--ink);font-size:12px;font-weight:900;padding:2px 8px;border-radius:4px;margin-left:6px;vertical-align:middle}
.share{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:22px 0 0;font-size:15px}
.share a{text-decoration:none;border:1px solid var(--line);padding:7px 14px;border-radius:999px;color:var(--ink);font-weight:700}
.share a:hover{border-color:var(--red);color:var(--red-d)}
.cta{background:linear-gradient(150deg,var(--red-d),var(--red-dd));color:#fff;border-radius:16px;padding:30px 26px;margin:34px 0 10px;text-align:center}
.cta h2{font:900 28px/1.25 'Playfair Display',Georgia,serif;margin:0 0 8px;color:#fff}
.cta p{margin:0 0 18px;color:#fff}
.cta .btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.cta a{display:inline-block;text-decoration:none;font-weight:900;padding:13px 22px;border-radius:999px}
.cta a.p{background:linear-gradient(90deg,var(--gold-d),var(--gold-l));color:var(--ink)}
.cta a.s{background:#fff;color:var(--red-dd)}
.related h2{font:900 26px 'Playfair Display',Georgia,serif;margin:38px 0 12px}
.note{font-size:15px;color:var(--muted);border-top:1px solid var(--line);margin-top:30px;padding-top:14px}
.sources li{margin:4px 0}
.offices{background:var(--ink);color:#fff;margin-top:44px;padding:40px 0 10px}
.offices .in{max-width:1100px;margin:0 auto;padding:0 20px}
.offices h2{font:900 28px 'Playfair Display',Georgia,serif;color:#fff;margin:0 0 4px}
.offices .lead{color:#E6E6E6;margin:0 0 18px}
.ogrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.o{border:1px solid #555555;border-top:4px solid var(--gold);border-radius:10px;padding:16px;background:#333333}
.o h3{font:700 18px 'Playfair Display',Georgia,serif;color:var(--gold-l);margin:0 0 4px}
.o .r{font-size:13px;color:#E6E6E6;margin-bottom:8px}
.o address{font-style:normal;font-size:15px;color:#fff;line-height:1.5}
.o a{color:#fff;font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 6px}
.chips span{border:1px solid var(--gold-d);color:var(--gold-l);border-radius:999px;padding:4px 12px;font-size:14px}
footer.site{background:#1E1E1E;color:#fff;padding:26px 0 90px;font-size:15px}
footer.site .in{max-width:1100px;margin:0 auto;padding:0 20px}
footer.site a{color:#fff}
footer.site .legal{margin-top:16px;padding-top:14px;border-top:1px solid #444444;color:#D6D6D6;font-size:13px}
.mbar{position:fixed;left:0;right:0;bottom:0;display:none;gap:8px;padding:10px 12px;background:#fff;border-top:3px solid var(--red);z-index:15;box-shadow:0 -4px 14px rgba(0,0,0,.08)}
.mbar a{flex:1;text-align:center;text-decoration:none;font-weight:900;padding:11px 8px;border-radius:999px;font-size:15px}
.mbar a.p{background:var(--red);color:#fff}.mbar a.s{border:2px solid var(--red);color:var(--red-d)}
.list{display:grid;gap:18px;margin:8px 0 30px}
.card{display:block;text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:20px 22px;border-top:5px solid var(--red);background:#fff}
.card:hover{box-shadow:0 6px 20px rgba(0,0,0,.08);color:var(--ink)}
.card .cat{font-size:12px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:var(--gold-d)}
.card h2,.card h3{font:900 22px/1.3 'Playfair Display',Georgia,serif;margin:6px 0}
.card p{margin:0;color:var(--muted);font-size:16px}
@media (max-width:700px){header.top .tag{display:none}}
@media (max-width:600px){body{font-size:17px}header.top img{height:38px}.hero{padding:40px 0 48px}article h2,.faq h2{font-size:26px}.mbar{display:flex}.stats{grid-template-columns:1fr 1fr}.stat .v{font-size:24px}article section.tint{margin:20px -12px;padding:6px 12px 20px}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap" rel="stylesheet">')

JS = ("<script>(function(){var p=document.getElementById('prog');if(!p)return;function u(){var h=document.documentElement;"
      "var m=h.scrollHeight-h.clientHeight;p.style.width=(m>0?h.scrollTop/m*100:0)+'%'}addEventListener('scroll',u,{passive:true});u()})();</script>")


def chart_svg(c, uid):
    bars = c["bars"][:6]
    n = len(bars)
    W, H, top, base = 640, 300, 40, 240
    mx = max(b["value"] for b in bars) or 1
    slot = (W - 40) / n
    bw = min(110, slot * 0.6)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(c["title"])}: ' +
           e("; ".join(f'{b["label"]} {b.get("display", b["value"])}' for b in bars)) + '">',
           f'<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient>'
           f'<linearGradient id="r{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{RED}"/><stop offset="1" stop-color="{RED_DD}"/></linearGradient></defs>',
           f'<line x1="20" y1="{base}" x2="{W-20}" y2="{base}" stroke="{RED_D}" stroke-width="2"/>']
    for i, b in enumerate(bars):
        h = (base - top) * b["value"] / mx
        x = 20 + slot * i + (slot - bw) / 2
        fill = f"url(#r{uid})" if b["value"] == mx else f"url(#g{uid})"
        cx = x + bw / 2
        out.append(f'<rect x="{x:.1f}" y="{base-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="6" fill="{fill}"/>')
        out.append(f'<text x="{cx:.1f}" y="{base-h-10:.1f}" text-anchor="middle" font-family="Playfair Display,Georgia,serif" font-weight="900" font-size="20" fill="{INK}">{e(str(b.get("display", b["value"])))}</text>')
        words, lines, cur = b["label"].split(), [], ""
        for w in words:
            if len(cur + " " + w) > 16 and cur:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        for j, ln in enumerate(lines[:2]):
            out.append(f'<text x="{cx:.1f}" y="{base+22+j*17}" text-anchor="middle" font-family="Lato,Arial,sans-serif" font-size="14" fill="{INK}">{e(ln)}</text>')
    out.append("</svg>")
    return "".join(out)


def chart_block(c, uid):
    return (f'<figure class="chart"><h3>{e(c["title"])}</h3>' + (f'<div class="s">{e(c["sub"])}</div>' if c.get("sub") else "") +
            chart_svg(c, uid) + "</figure>")


def wrap_tables(h):
    return h.replace("<table", '<div class="tbl"><table').replace("</table>", "</table></div>")


def agent_schema():
    return {
        "@type": "RealEstateAgent", "@id": BASE + "#agent", "name": AGENT["name"], "jobTitle": AGENT["title"],
        "telephone": AGENT["tel"], "email": AGENT["email"], "url": AGENT["sites"][0],
        "logo": BASE + "assets/brand/logo-gold.png", "image": BASE + "assets/brand/logo-gold.png",
        "sameAs": AGENT["sites"] + [AGENT["linkedin"], AGENT["instagram"]],
        "worksFor": {"@type": "RealEstateAgent", "name": AGENT["brokerage"], "url": "https://www.royalcanadianrealty.com/"},
        "areaServed": [{"@type": "Place", "name": a + ", Ontario"} for a in AREAS],
        "award": "Royal Canadian Realty Gold Club Award Winner (August 2026)",
        "openingHours": ["Mo-Fr 09:00-18:00", "Sa 11:00-18:00", "Su 10:00-17:00"],
        "department": [{"@type": "RealEstateAgent", "name": f"Royal Canadian Realty, Brokerage – {o[0]}",
                        "address": {"@type": "PostalAddress", "streetAddress": o[1], "addressLocality": o[2],
                                    "addressRegion": "ON", "postalCode": o[3], "addressCountry": "CA"},
                        "areaServed": o[4], "telephone": tel(o[5]), "hasMap": maps(o)} for o in OFFICES],
    }


def header(home):
    return (f'<div id="prog"></div><header class="top"><div class="bar"><a href="{home}" aria-label="Satnampal Singh blog home">'
            f'<img src="{BASE}assets/brand/logo-gold.png" alt="Royal Canadian Realty, Brokerage" width="86" height="46"></a>'
            f'<span class="tag">“Believe In The Best”</span>'
            f'<a class="call" href="tel:{AGENT["tel"]}">Call {AGENT["phone"]}</a></div></header>')


def offices_block():
    cards = "".join(
        f'<div class="o"><h3>{e(o[0])}</h3><div class="r">Serving {e(o[4])}</div>'
        f'<address>{e(o[1])}<br>{e(o[2])}, ON {e(o[3])}</address>'
        f'<p style="margin:8px 0 0"><a href="tel:{tel(o[5])}">Office {e(o[5])}</a> · <a href="{maps(o)}" target="_blank" rel="noopener">Map</a></p></div>'
        for o in OFFICES)
    chips = "".join(f"<span>{e(a)}</span>" for a in AREAS)
    return (f'<section class="offices"><div class="in"><h2>Royal Canadian Realty offices</h2>'
            f'<p class="lead">Meet Satnampal at any of our offices across the GTA and Southern Ontario — or call him directly at '
            f'<a href="tel:{AGENT["tel"]}" style="color:var(--gold-l)">{AGENT["phone"]}</a>.</p>'
            f'<div class="ogrid">{cards}</div><div class="chips">{chips}</div></div></section>')


def footer():
    return (f'<footer class="site"><div class="in"><strong style="font-size:19px">{AGENT["name"]}</strong> · {AGENT["title"]} | {AGENT["brokerage"]}<br>'
            f'Gold Club Award Winner · Believe In The Best<br>'
            f'📞 <a href="tel:{AGENT["tel"]}">{AGENT["phone"]}</a> · ✉️ <a href="mailto:{AGENT["email"]}">{AGENT["email"]}</a><br>'
            f'🌐 <a href="{AGENT["sites"][0]}">FindYourHouseInGTA.com</a> · <a href="{AGENT["sites"][1]}">DreamHomeSeller.ca</a> · '
            f'<a href="{AGENT["linkedin"]}">LinkedIn</a> · <a href="{AGENT["instagram"]}">Instagram</a> · <a href="{BASE}blog/">All articles</a><br>Hours: {HOURS}'
            f'<div class="legal">This article is general information, not financial, legal or tax advice. Programs, rates and limits change; '
            f'confirm your situation with a licensed mortgage professional, lawyer or accountant. Not intended to solicit buyers or sellers already under contract. '
            f'© {datetime.date.today().year} {AGENT["name"]}, {AGENT["brokerage"]}.</div></div></footer>'
            f'<div class="mbar"><a class="p" href="tel:{AGENT["tel"]}">📞 Call</a><a class="s" href="sms:{AGENT["tel"]}">💬 Text</a>'
            f'<a class="s" href="mailto:{AGENT["email"]}">✉️ Email</a></div>')


def page(title, desc, url, body, schema, og_img, og_type="article", keywords=None):
    kw = f'<meta name="keywords" content="{e(", ".join(keywords))}">' if keywords else ""
    return f"""<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{kw}
<meta name="author" content="Satnampal Singh"><meta name="robots" content="index,follow,max-image-preview:large">
<meta name="geo.region" content="CA-ON"><meta name="geo.placename" content="Brampton, Ontario">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og_img}"><meta property="og:site_name" content="Satnampal Singh – GTA Real Estate">
<meta property="og:locale" content="en_CA"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{og_img}">
<link rel="icon" href="{BASE}assets/brand/logo-gold.png">{FONTS}<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>
<body>{body}{JS}</body></html>"""


def build_article(a, reg):
    url = f"{BASE}blog/{a['slug']}/"
    cover = RAW + a["cover"] if a.get("cover") else RAW + "assets/brand/logo-gold.png"
    pretty = datetime.date.fromisoformat(a["date"]).strftime("%B %-d, %Y")
    words = sum(len(s["html"].split()) for s in a["sections"])
    mins = max(3, round(words / 220))
    stats = "".join(f'<div class="stat"><div class="v">{e(s["value"])}</div><div class="l">{e(s["label"])}</div></div>' for s in a.get("stats", [])[:4])
    take = "".join(f"<li>{e(t)}</li>" for t in a["takeaways"])
    toc = "".join(f'<li><a href="#s{i}">{e(s["h2"])}</a></li>' for i, s in enumerate(a["sections"])) + '<li><a href="#faq">Frequently asked questions</a></li>'
    secs = ""
    for i, s in enumerate(a["sections"]):
        lab = f'<div class="label">{e(s["label"])}</div>' if s.get("label") else ""
        ch = chart_block(s["chart"], i) if s.get("chart") else ""
        cls = ' class="tint"' if i % 2 else ""
        secs += f'<section{cls}>{lab}<h2 id="s{i}">{e(s["h2"])}</h2>{wrap_tables(s["html"])}{ch}</section>'
    faq = "".join(f"<details{' open' if j == 0 else ''}><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>" for j, f in enumerate(a["faq"]))
    srcs = "".join(f'<li><a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s["name"])}</a></li>' for s in a.get("sources", []))
    book = f"{AGENT['sites'][0]}?utm_source=blog&utm_medium=article&utm_campaign={a['slug']}"
    q = urllib.parse.quote
    share = (f'<div class="share"><b>Share:</b>'
             f'<a href="https://www.facebook.com/sharer/sharer.php?u={q(url)}" target="_blank" rel="noopener">Facebook</a>'
             f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={q(url)}" target="_blank" rel="noopener">LinkedIn</a>'
             f'<a href="https://wa.me/?text={q(a["title"] + " " + url)}" target="_blank" rel="noopener">WhatsApp</a>'
             f'<a href="mailto:?subject={q(a["title"])}&amp;body={q(url)}">Email</a></div>')
    rel = [r for r in reg if r["slug"] != a["slug"]][:3]
    related = ("" if not rel else '<section class="related"><h2>Keep reading</h2><div class="list">' + "".join(
        f'<a class="card" href="{BASE}blog/{r["slug"]}/"><span class="cat">{e(r["category"])}</span><h3>{e(r["title"])}</h3><p>{e(r["description"])}</p></a>'
        for r in rel) + "</div></section>")
    author = (f'<div class="author"><div class="mark">{CREST}</div><div><strong>{AGENT["name"]}</strong><span class="badge">GOLD CLUB AWARD WINNER</span>'
              f'<p>{AGENT["title"]}, {AGENT["brokerage"]}. Helping first-time buyers, sellers and investors across Brampton, Mississauga and the GTA.</p>'
              f'<p>📞 <a href="tel:{AGENT["tel"]}">{AGENT["phone"]}</a> · ✉️ <a href="mailto:{AGENT["email"]}">{AGENT["email"]}</a></p></div></div>')
    body = (header(BASE + "blog/") +
            f'<div class="hero"><div class="wrap"><span class="cat">{e(a["category"])}</span><h1>{e(a["title"])}</h1>'
            f'<p class="sub">{e(a["hero_sub"])}</p><div class="meta"><span><b>By</b> {AGENT["name"]}, Royal Canadian Realty</span>'
            f'<span><b>Updated</b> {pretty}</span><span><b>Read</b> {mins} min</span></div></div></div><div class="gold-rule"></div>'
            + (f'<div class="wrap"><div class="stats">{stats}</div></div>' if stats else "") +
            f'<main><div class="wrap"><div class="take"><h2>Key takeaways</h2><ul>{take}</ul></div>'
            f'<nav class="toc" aria-label="In this guide"><b>In this guide</b><ol>{toc}</ol></nav>'
            f'<article>{secs}</article>'
            f'<section class="faq"><h2 id="faq">Frequently asked questions</h2>{faq}</section>'
            f'<div class="cta"><h2>Talk it through with Satnampal</h2><p>Book a free 15-minute call — no pressure, just a clear plan for your next move in the GTA.</p>'
            f'<div class="btns"><a class="p" href="tel:{AGENT["tel"]}">📞 {AGENT["phone"]}</a><a class="s" href="{book}">Visit FindYourHouseInGTA.com</a></div></div>'
            + author + share + related +
            (f'<div class="note"><strong>Sources</strong> (checked {pretty})<ul class="sources">{srcs}</ul>'
             f'Scenarios are illustrations, not promises. Last reviewed {pretty}.</div>' if srcs else "") +
            '</div></main>' + offices_block() + footer())
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": a["title"], "description": a["description"], "datePublished": a["date"],
         "dateModified": a["date"], "inLanguage": "en-CA", "mainEntityOfPage": url, "image": cover,
         "keywords": ", ".join(a.get("keywords", [])), "articleSection": a["category"], "wordCount": words,
         "about": a.get("keywords", [])[:4], "spatialCoverage": [{"@type": "Place", "name": "Brampton, Ontario"}, {"@type": "Place", "name": "Greater Toronto Area"}],
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
        f.write(boldtrail_fragment(a, CDN + a["cover"] if a.get("cover") else cover))
    return url


def boldtrail_fragment(a, cover):
    """Body-only HTML with inline styles, for pasting into BoldTrail > Web & IDX > Blog (Source/HTML view)."""
    h2 = f'style="font-family:Georgia,serif;color:{INK};border-bottom:3px solid {RED};padding-bottom:6px;margin:32px 0 12px"'
    lab = f'style="font-size:12px;font-weight:bold;letter-spacing:.1em;color:{RED};margin:28px 0 0"'
    stats = "".join(f'<td style="padding:6px;vertical-align:top"><div style="border:1px solid #E2E2E2;border-top:5px solid {RED};border-radius:10px;padding:12px 14px">'
                    f'<div style="font-family:Georgia,serif;font-weight:bold;font-size:26px;color:{RED_DD}">{e(s["value"])}</div>'
                    f'<div style="font-size:14px;color:#5A5A5A">{e(s["label"])}</div></div></td>' for s in a.get("stats", [])[:4])
    take = "".join(f"<li>{e(t)}</li>" for t in a["takeaways"])

    def inline(h):  # turn design-helper classes into inline styles BoldTrail keeps
        rep = {
            '<div class="callout">': f'<div style="border-left:5px solid {GOLD_D};background:#fff;padding:14px 18px;border-radius:6px;margin:18px 0;box-shadow:0 2px 8px rgba(0,0,0,.06)">',
            '<div class="cards">': '<div style="display:flex;flex-wrap:wrap;gap:12px;margin:18px 0">',
            '<div class="c featured">': f'<div style="flex:1 1 200px;background:{RED_D};color:#fff;border-top:5px solid {GOLD_L};border-radius:10px;padding:16px">',
            '<div class="c">': f'<div style="flex:1 1 200px;background:#fff;border:1px solid #E2E2E2;border-top:5px solid {GOLD_D};border-radius:10px;padding:16px">',
            '<span class="tag">': f'<span style="font-size:12px;font-weight:bold;letter-spacing:.08em;color:{RED}">',
            '<div class="big">': '<div style="font-family:Georgia,serif;font-weight:bold;font-size:24px;margin:4px 0">',
            '<ol class="steps">': '<ol style="padding-left:24px">',
            '<th>': f'<th style="background:{RED_D};color:#fff;text-align:left;padding:8px 10px">',
            '<td>': '<td style="padding:8px 10px;border-bottom:1px solid #E2E2E2">',
            '<table>': '<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:15px">',
        }
        for k, v in rep.items():
            h = h.replace(k, v)
        return h
    secs = ""
    for i, s in enumerate(a["sections"]):
        secs += (f'<p {lab}>{e(s["label"])}</p>' if s.get("label") else "") + f'<h2 {h2}>{e(s["h2"])}</h2>{inline(s["html"])}'
        if s.get("chart"):
            secs += (f'<p style="font-family:Georgia,serif;font-weight:bold;margin:18px 0 0">{e(s["chart"]["title"])}</p>'
                     f'<div style="border:1px solid #E2E2E2;border-radius:10px;padding:10px;margin:6px 0 18px">{chart_svg(s["chart"], "bt" + str(i))}</div>')
    faq = "".join(f'<h3 style="font-family:Georgia,serif;color:{RED_D};margin:18px 0 6px">{e(f["q"])}</h3><p>{e(f["a"])}</p>' for f in a["faq"])
    srcs = "".join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a></li>' for s in a.get("sources", []))
    offs = "".join(f'<td style="padding:6px;vertical-align:top;width:20%"><div style="border-top:4px solid {GOLD};padding:8px 0;font-size:14px">'
                   f'<strong style="color:{RED_DD}">{e(o[0])}</strong><br>{e(o[1])}<br>{e(o[2])}, ON {e(o[3])}<br>'
                   f'<a href="tel:{tel(o[5])}">{e(o[5])}</a> · <a href="{maps(o)}" target="_blank" rel="noopener">Map</a></div></td>' for o in OFFICES)
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in a["faq"]]}, ensure_ascii=False)
    return (f'<!-- BoldTrail paste version: {a["title"]} -->\n'
            f'<div style="font-family:Lato,Arial,sans-serif;color:{INK};line-height:1.7;font-size:17px">'
            f'<p style="margin:0"><span style="display:inline-block;background:{GOLD_D};color:#fff;font-weight:bold;font-size:13px;letter-spacing:.08em;padding:4px 10px;border-radius:4px">{e(a["category"].upper())}</span></p>'
            f'<h1 style="font-family:Georgia,serif;color:{RED_DD};font-size:34px;line-height:1.2;margin:12px 0 8px">{e(a["title"])}</h1>'
            f'<p style="font-size:14px;color:#5A5A5A;margin:0 0 16px">By {AGENT["name"]}, {AGENT["title"]}, {AGENT["brokerage"]} · {datetime.date.fromisoformat(a["date"]).strftime("%B %-d, %Y")}</p>'
            f'<p><img src="{cover}" alt="{e(a["title"])}" style="max-width:100%;height:auto;border-radius:8px"></p>'
            f'<p style="font-size:19px"><strong>{e(a["hero_sub"])}</strong></p>'
            + (f'<table style="width:100%;border-collapse:separate"><tr>{stats}</tr></table>' if stats else "") +
            f'<div style="background:{SOFT};border-left:6px solid {GOLD_D};padding:14px 20px;border-radius:6px;margin:20px 0">'
            f'<p style="margin:0 0 6px;font-weight:bold">Key takeaways</p><ul style="margin:0">{take}</ul></div>'
            f'{secs}<h2 {h2}>Frequently asked questions</h2>{faq}'
            f'<div style="background:{RED_D};color:#fff;padding:22px;border-radius:12px;margin:30px 0;text-align:center">'
            f'<p style="font-size:22px;font-family:Georgia,serif;margin:0 0 8px;color:#fff"><strong>Talk it through with Satnampal</strong></p>'
            f'<p style="margin:0 0 10px;color:#fff">Book a free 15-minute call — no pressure, just a clear plan for your next move in the GTA.</p>'
            f'<p style="margin:0;color:#fff">📞 <a href="tel:{AGENT["tel"]}" style="color:#fff">{AGENT["phone"]}</a> · ✉️ '
            f'<a href="mailto:{AGENT["email"]}" style="color:#fff">{AGENT["email"]}</a></p></div>'
            f'<p style="font-family:Georgia,serif;font-weight:bold;font-size:20px;margin:24px 0 4px">Royal Canadian Realty offices</p>'
            f'<table style="width:100%;border-collapse:collapse"><tr>{offs}</tr></table>'
            + (f'<p style="font-size:14px"><strong>Sources</strong></p><ul style="font-size:14px">{srcs}</ul>' if srcs else "") +
            f'<p style="font-size:13px;color:#5A5A5A">{AGENT["name"]}, {AGENT["title"]} | {AGENT["brokerage"]} | Gold Club Award Winner · Believe In The Best. '
            f'General information only, not financial, legal or tax advice. Scenarios are illustrations.</p></div>\n'
            f'<script type="application/ld+json">{faq_ld}</script>\n')


def build_index(reg):
    url = BASE + "blog/"
    cards = "".join(f'<a class="card" href="{BASE}blog/{r["slug"]}/"><span class="cat">{e(r["category"])} · {e(r["date"])}</span>'
                    f'<h2>{e(r["title"])}</h2><p>{e(r["description"])}</p></a>' for r in reg)
    body = (header(url) + '<div class="hero"><div class="wrap"><span class="cat">GTA Real Estate Blog</span>'
            '<h1>Real estate advice for Brampton &amp; the GTA</h1><p class="sub">Plain-English guides for first-time buyers, sellers and investors '
            'from Satnampal Singh, Royal Canadian Realty.</p></div></div><div class="gold-rule"></div>'
            f'<main><div class="wrap"><div class="list">{cards}</div></div></main>' + offices_block() + footer())
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
    regp = os.path.join(ROOT, "blog", "articles.json")
    reg = json.load(open(regp)) if os.path.exists(regp) else []
    reg = [r for r in reg if r["slug"] != a["slug"]] + [{k: a[k] for k in ("slug", "title", "description", "date", "category")}]
    reg.sort(key=lambda r: r["date"], reverse=True)
    os.makedirs(os.path.join(ROOT, "blog"), exist_ok=True)
    json.dump(reg, open(regp, "w"), indent=2, ensure_ascii=False)
    url = build_article(a, reg)
    build_index(reg)
    lp = os.path.join(ROOT, "posts", "links.json")
    links = json.load(open(lp))
    links.setdefault("pages", {})[a["slug"]] = SITE_BLOG  # posts send readers to his BoldTrail blog
    with open(lp, "w") as f:
        json.dump(links, f, indent=2, ensure_ascii=False); f.write("\n")
    print(url)


if __name__ == "__main__":
    main()
