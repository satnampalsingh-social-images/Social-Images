"""Render a branded 1080x1080 real-estate post image (business-card palette: red, white, gold).
Usage: python3 make_post_image.py '<json>' out.png
JSON keys: tag, headline (may use <em>..</em> for red italic), sub, points (<=3), cta, subTop,\n  art: "headshot" (default; his photo in a gold ring, bottom right) or "house" (line illustration)\n  layout: "stats" (optional, for market updates): hero {value,label,note}, stats [{value,label,change,dir:"down"|"up"}] (3), takeaway\nTop-left uses the official Royal Canadian Realty logo from assets/brand/logo-gold.png.
"""
import json, sys, html, asyncio, os, tempfile
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
BRAND = os.path.join(os.path.dirname(HERE), "assets", "brand")
PORTRAITS = os.path.join(os.path.dirname(HERE), "assets", "portraits")
PF = f"{FONTS}/playfair-display-latin"
LA = f"{FONTS}/lato-latin"

d = json.loads(sys.argv[1]); out = sys.argv[2]
e = lambda s: html.escape(s or "")
check = '<svg viewBox="0 0 24 24" width="34" height="34"><circle cx="12" cy="12" r="11" fill="#ED1C24"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
pts = "".join(f'<li>{check}<span>{e(p)}</span></li>' for p in d.get("points", [])[:3])

# Brand palette (Satnampal, Nov 2026): red #ED1C24, gold #C79A3B, charcoal #252525, white, light grey
RED, RED_D, GOLD_L, GOLD_D, INK = "#ED1C24", "#C4161D", "#E8CF8E", "#A57E2C", "#252525"

# keyhole crest mark
crest = f'''<svg viewBox="0 0 64 64" width="62" height="62"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_L}"/><stop offset=".5" stop-color="#C79A3B"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>
<path d="M14 14l6-8 6 6 6-9 6 9 6-6 6 8" fill="none" stroke="url(#g)" stroke-width="3" stroke-linejoin="round"/>
<circle cx="32" cy="36" r="20" fill="none" stroke="url(#g)" stroke-width="3.5"/>
<circle cx="32" cy="32" r="6" fill="{INK}"/><path d="M29 35h6l2 12H27z" fill="{INK}"/></svg>'''

# house + key line illustration
house = f'''<svg viewBox="0 0 400 360" width="400" height="360"><defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D6B25E"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>
<g fill="none" stroke="url(#h)" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
<path d="M40 170L200 40l160 130"/><path d="M80 140v190h240V140"/><path d="M290 108V58h-34v22"/>
<rect x="170" y="230" width="60" height="100" rx="4"/><rect x="105" y="190" width="50" height="50"/><rect x="245" y="190" width="50" height="50"/>
<path d="M130 190v50M105 215h50M270 190v50M245 215h50"/><path d="M20 330h360"/></g>
<g transform="translate(250 268) rotate(-30)"><circle cx="0" cy="0" r="30" fill="{RED}" stroke="#fff" stroke-width="7"/><circle cx="0" cy="0" r="10" fill="#fff"/>
<path d="M30 0h86M92 0v22M108 0v16" stroke="{RED}" stroke-width="9" stroke-linecap="round" fill="none"/></g></svg>'''

phone_ic = '<svg viewBox="0 0 24 24" width="30" height="30"><path fill="#fff" d="M6.6 10.8a15.1 15.1 0 006.6 6.6l2.2-2.2a1 1 0 011-.25 11.4 11.4 0 003.6.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.45.57 3.57a1 1 0 01-.25 1z"/></svg>'
mail_ic = '<svg viewBox="0 0 24 24" width="26" height="26"><path fill="#fff" d="M3 5h18a1 1 0 011 1v12a1 1 0 01-1 1H3a1 1 0 01-1-1V6a1 1 0 011-1zm9 7.2L4 7v1.9l8 5 8-5V7z"/></svg>'
globe_ic = f'<svg viewBox="0 0 24 24" width="26" height="26"><g fill="none" stroke="{INK}" stroke-width="1.8"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c3 3 3 16 0 19M12 2.5c-3 3-3 16 0 19"/></g></svg>'
GOLDBAR = f"linear-gradient(90deg,{GOLD_D} 0%,#C79A3B 25%,{GOLD_L} 50%,#C79A3B 75%,{GOLD_D} 100%)"

art = (f'<div class="house">{house}</div>' if d.get("art") == "house"
       else f'<div class="me"><img src="file://{PORTRAITS}/headshot-cutout.png"></div>')

arrow = lambda dr: ('&#9660;' if dr == "down" else '&#9650;')
stats_html = ""
if d.get("layout") == "stats":
    h = d.get("hero", {})
    cards = "".join(f'<div class="sc"><div class="sv">{e(c.get("value"))}</div><div class="sl">{e(c.get("label"))}</div>'
                    f'<div class="sd {e(c.get("dir","down"))}">{arrow(c.get("dir","down"))} {e(c.get("change"))}</div></div>' for c in d.get("stats", [])[:3])
    stats_html = (f'<div class="hero"><div class="hv">{e(h.get("value"))}</div><div class="hl"><b>{e(h.get("label"))}</b><span>{e(h.get("note"))}</span></div></div>'
                  f'<div class="cards">{cards}</div>'
                  f'<div class="take"><b>What it means:</b> {e(d.get("takeaway"))}</div>')

page = f"""<html><head><style>
@font-face{{font-family:PF;font-weight:700;src:url(file://{PF}-700-normal.woff2)}}
@font-face{{font-family:PF;font-weight:900;src:url(file://{PF}-900-normal.woff2)}}
@font-face{{font-family:PF;font-weight:700;font-style:italic;src:url(file://{PF}-700-italic.woff2)}}
@font-face{{font-family:LA;font-weight:400;src:url(file://{LA}-400-normal.woff2)}}
@font-face{{font-family:LA;font-weight:700;src:url(file://{LA}-700-normal.woff2)}}
@font-face{{font-family:LA;font-weight:900;src:url(file://{LA}-900-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;font-family:LA;color:{INK};position:relative;overflow:hidden;background:#fff}}
.wedge{{position:absolute;left:0;top:0;width:38px;height:850px;background:{RED}}}
.corner{{position:absolute;right:0;top:0;width:0;height:0;border-top:150px solid {RED};border-left:150px solid transparent}}
.frame{{position:absolute;left:58px;right:30px;top:30px;bottom:240px;border:2px solid #DCC38A}}
.brand{{position:absolute;left:84px;top:66px;display:flex;align-items:center;gap:14px}}
.brand b{{display:block;font-family:PF;font-weight:700;font-size:27px;letter-spacing:2px;color:{INK};border-bottom:3px solid #C79A3B;padding-bottom:2px}}
.brand i{{display:block;font-style:normal;font-family:PF;font-weight:700;font-size:15px;letter-spacing:3.5px;color:{INK};margin-top:4px}}
.motto{{position:absolute;right:170px;top:86px;font-family:PF;font-style:italic;font-weight:700;font-size:24px;color:{INK}}}
.tag{{position:absolute;left:84px;top:178px;background:{RED};color:#fff;font-weight:900;font-size:22px;letter-spacing:3px;text-transform:uppercase;padding:11px 22px;border-radius:40px}}
h1{{font-variant-numeric:lining-nums;position:absolute;left:84px;right:84px;top:248px;font-family:PF;font-weight:900;font-size:78px;line-height:1.05;color:{INK}}}
h1 em{{font-weight:700;font-style:italic;color:{RED}}}
.body{{position:absolute;left:84px;width:590px;top:{d.get('subTop',540)}px}}
.sub{{font-size:29px;line-height:1.4;color:#444444}}
ul{{list-style:none;margin-top:22px}}
li{{display:flex;align-items:center;gap:16px;font-size:29px;font-weight:700;line-height:1.3;margin-top:18px;background:#F4F4F4;border-left:5px solid #C79A3B;padding:12px 18px;color:{INK}}}
li svg{{flex:0 0 34px}}
.house{{position:absolute;right:40px;bottom:262px;transform:scale(.85);transform-origin:bottom right}}
.brand img{{height:100px;display:block}}
.me{{position:absolute;right:64px;bottom:276px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle at 50% 40%,#fff 0%,#F4F4F4 100%);border:9px solid {RED};box-shadow:0 0 0 6px #DCC38A,0 14px 30px rgba(0,0,0,.18);overflow:hidden}}
.me img{{position:absolute;left:50%;bottom:0;width:112%;transform:translateX(-50%)}}
.redband{{position:absolute;left:0;right:0;bottom:70px;height:170px;background:{RED};display:flex;align-items:center;justify-content:space-between;padding:0 44px 0 70px;color:#fff}}
.redband:before{{content:'';position:absolute;left:0;right:0;top:0;height:6px;background:{GOLDBAR}}}
.name{{font-family:PF;font-weight:900;font-size:46px;letter-spacing:1px;line-height:1}}
.name span{{font-style:italic;font-weight:700;color:#ffe2e3}}
.role{{font-size:15.5px;font-weight:700;letter-spacing:1px;margin-top:10px;text-transform:uppercase;white-space:nowrap}}
.cta{{display:inline-block;margin-top:12px;background:#fff;color:{RED};font-weight:900;font-size:17px;letter-spacing:2px;text-transform:uppercase;padding:7px 16px;border-radius:30px}}
.contact{{text-align:left}}
.row{{display:flex;align-items:center;gap:12px}}
.phone{{font-variant-numeric:lining-nums;font-family:PF;font-weight:900;font-size:42px;letter-spacing:0;white-space:nowrap}}
.phone small{{font-size:30px}}
.mail{{font-size:23px;font-weight:700;margin-top:8px}}
.goldbar{{position:absolute;left:0;right:0;bottom:0;height:70px;background:{GOLDBAR};display:flex;align-items:center;justify-content:center;gap:14px;font-family:PF;font-weight:700;font-size:27px;color:{INK}}}
.goldbar .sep{{opacity:.7}}
.hero{{position:absolute;left:84px;width:610px;top:{d.get('subTop',360)}px;display:flex;align-items:center;gap:22px;background:linear-gradient(135deg,#fff5f5,#F4F4F4);border:2px solid #DCC38A;border-left:10px solid {RED};padding:14px 24px}}
.hv{{font-variant-numeric:lining-nums;font-family:PF;font-weight:900;font-size:122px;line-height:1;color:{RED};letter-spacing:-3px}}
.hl b{{display:block;font-size:27px;font-weight:900;line-height:1.2;color:{INK}}}
.hl span{{display:block;font-size:21px;color:#666666;margin-top:6px}}
.cards{{position:absolute;left:84px;width:610px;top:{d.get('subTop',360)+200}px;display:flex;gap:14px}}
.sc{{flex:1;background:{INK};color:#fff;border-radius:14px;padding:16px 14px 14px;text-align:center;border-top:6px solid #C79A3B}}
.sv{{font-variant-numeric:lining-nums;font-family:PF;font-weight:900;font-size:40px;line-height:1.05}}
.sl{{font-size:18px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#E8CF8E;margin-top:6px}}
.sd{{display:inline-block;margin-top:9px;font-size:20px;font-weight:900;padding:4px 12px;border-radius:20px;background:{RED}}}
.sd.up{{background:#2f8f4e}}
.take{{position:absolute;left:84px;width:610px;top:{d.get('subTop',360)+380}px;font-size:25px;line-height:1.35;color:#444444}}
.take b{{color:{RED}}}
</style></head><body>
<div class="wedge"></div><div class="corner"></div><div class="frame"></div>
<div class="brand"><img src="file://{BRAND}/logo-gold.png"></div>
<div class="motto">&ldquo;Believe In The Best&rdquo;</div>
<span class="tag">{e(d.get('tag'))}</span>
<h1>{d.get('headline','')}</h1>
{stats_html if stats_html else f'<div class="body"><p class="sub">{e(d.get("sub"))}</p><ul>{pts}</ul></div>'}
{art}
<div class="redband">
  <div><div class="name">SATNAMPAL <span>Singh</span></div>
  <div class="role">Real Estate Sales Representative · Gold Club Award Winner</div>
  <div class="cta">{e(d.get('cta','Book a free call'))}</div></div>
  <div class="contact"><div class="row">{phone_ic}<div class="phone"><small>Dir:</small> 647-780-2560</div></div>
  <div class="row mail">{mail_ic}ssingh@royalcanadianrealty.com</div></div>
</div>
<div class="goldbar">{globe_ic}<span>www.DreamHomeSeller.ca</span><span class="sep">|</span><span>www.FindYourHouseInGTA.com</span></div>
</body></html>"""

async def main():
    f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False); f.write(page); f.close()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox","--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width":1080,"height":1080})
        await pg.goto("file://" + f.name); await pg.evaluate("document.fonts.ready")
        await pg.screenshot(path=out); await b.close()
asyncio.run(main())
