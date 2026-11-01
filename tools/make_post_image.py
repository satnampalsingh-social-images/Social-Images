"""Render a branded 1080x1080 real-estate post image (business-card palette: red, white, gold).
Usage: python3 make_post_image.py '<json>' out.png
JSON keys: tag, headline (may use <em>..</em> for gold italic), sub, points (<=3), cta
"""
import json, sys, html, asyncio, os, tempfile
from playwright.async_api import async_playwright

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
PF = f"{FONTS}/playfair-display-latin"
LA = f"{FONTS}/lato-latin"

d = json.loads(sys.argv[1]); out = sys.argv[2]
e = lambda s: html.escape(s or "")
check = '<svg viewBox="0 0 24 24" width="34" height="34"><circle cx="12" cy="12" r="11" fill="#e8323a"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
pts = "".join(f'<li>{check}<span>{e(p)}</span></li>' for p in d.get("points", [])[:3])

# Brand palette (from business card): bright red, white, gold gradient, charcoal
RED, RED_D, GOLD_L, GOLD_D, INK = "#e8323a", "#b8202a", "#f4eb8d", "#b07a3c", "#31312f"

# keyhole crest mark
crest = f'''<svg viewBox="0 0 64 64" width="62" height="62"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_L}"/><stop offset=".5" stop-color="#d9b25e"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>
<path d="M14 14l6-8 6 6 6-9 6 9 6-6 6 8" fill="none" stroke="url(#g)" stroke-width="3" stroke-linejoin="round"/>
<circle cx="32" cy="36" r="20" fill="none" stroke="url(#g)" stroke-width="3.5"/>
<circle cx="32" cy="32" r="6" fill="{INK}"/><path d="M29 35h6l2 12H27z" fill="{INK}"/></svg>'''

# house + key line illustration
house = f'''<svg viewBox="0 0 400 360" width="400" height="360"><defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2c463"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>
<g fill="none" stroke="url(#h)" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
<path d="M40 170L200 40l160 130"/><path d="M80 140v190h240V140"/><path d="M290 108V58h-34v22"/>
<rect x="170" y="230" width="60" height="100" rx="4"/><rect x="105" y="190" width="50" height="50"/><rect x="245" y="190" width="50" height="50"/>
<path d="M130 190v50M105 215h50M270 190v50M245 215h50"/><path d="M20 330h360"/></g>
<g transform="translate(250 268) rotate(-30)"><circle cx="0" cy="0" r="30" fill="{RED}" stroke="#fff" stroke-width="7"/><circle cx="0" cy="0" r="10" fill="#fff"/>
<path d="M30 0h86M92 0v22M108 0v16" stroke="{RED}" stroke-width="9" stroke-linecap="round" fill="none"/></g></svg>'''

phone_ic = '<svg viewBox="0 0 24 24" width="30" height="30"><path fill="#fff" d="M6.6 10.8a15.1 15.1 0 006.6 6.6l2.2-2.2a1 1 0 011-.25 11.4 11.4 0 003.6.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.45.57 3.57a1 1 0 01-.25 1z"/></svg>'
mail_ic = '<svg viewBox="0 0 24 24" width="26" height="26"><path fill="#fff" d="M3 5h18a1 1 0 011 1v12a1 1 0 01-1 1H3a1 1 0 01-1-1V6a1 1 0 011-1zm9 7.2L4 7v1.9l8 5 8-5V7z"/></svg>'
globe_ic = f'<svg viewBox="0 0 24 24" width="26" height="26"><g fill="none" stroke="{INK}" stroke-width="1.8"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c3 3 3 16 0 19M12 2.5c-3 3-3 16 0 19"/></g></svg>'
GOLDBAR = f"linear-gradient(90deg,{GOLD_D} 0%,#d9b25e 25%,{GOLD_L} 50%,#d9b25e 75%,{GOLD_D} 100%)"

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
.frame{{position:absolute;left:58px;right:30px;top:30px;bottom:240px;border:2px solid #e6cf8a}}
.brand{{position:absolute;left:84px;top:66px;display:flex;align-items:center;gap:14px}}
.brand b{{display:block;font-family:PF;font-weight:700;font-size:27px;letter-spacing:2px;color:{INK};border-bottom:3px solid #d9b25e;padding-bottom:2px}}
.brand i{{display:block;font-style:normal;font-family:PF;font-weight:700;font-size:15px;letter-spacing:3.5px;color:{INK};margin-top:4px}}
.motto{{position:absolute;right:170px;top:86px;font-family:PF;font-style:italic;font-weight:700;font-size:24px;color:{INK}}}
.tag{{position:absolute;left:84px;top:178px;background:{RED};color:#fff;font-weight:900;font-size:22px;letter-spacing:3px;text-transform:uppercase;padding:11px 22px;border-radius:40px}}
h1{{font-variant-numeric:lining-nums;position:absolute;left:84px;right:84px;top:248px;font-family:PF;font-weight:900;font-size:78px;line-height:1.05;color:{INK}}}
h1 em{{font-weight:700;font-style:italic;color:{RED}}}
.body{{position:absolute;left:84px;width:590px;top:{d.get('subTop',540)}px}}
.sub{{font-size:29px;line-height:1.4;color:#4a4a48}}
ul{{list-style:none;margin-top:22px}}
li{{display:flex;align-items:center;gap:16px;font-size:29px;font-weight:700;line-height:1.3;margin-top:18px;background:#fbf3df;border-left:5px solid #d9b25e;padding:12px 18px;color:{INK}}}
li svg{{flex:0 0 34px}}
.house{{position:absolute;right:40px;bottom:262px;transform:scale(.85);transform-origin:bottom right}}
.redband{{position:absolute;left:0;right:0;bottom:70px;height:170px;background:{RED};display:flex;align-items:center;justify-content:space-between;padding:0 44px 0 70px;color:#fff}}
.redband:before{{content:'';position:absolute;left:0;right:0;top:0;height:6px;background:{GOLDBAR}}}
.name{{font-family:PF;font-weight:900;font-size:46px;letter-spacing:1px;line-height:1}}
.name span{{font-style:italic;font-weight:700;color:#ffe2e3}}
.role{{font-size:18px;font-weight:700;letter-spacing:1.5px;margin-top:10px;text-transform:uppercase}}
.cta{{display:inline-block;margin-top:12px;background:#fff;color:{RED};font-weight:900;font-size:17px;letter-spacing:2px;text-transform:uppercase;padding:7px 16px;border-radius:30px}}
.contact{{text-align:left}}
.row{{display:flex;align-items:center;gap:12px}}
.phone{{font-variant-numeric:lining-nums;font-family:PF;font-weight:900;font-size:42px;letter-spacing:0;white-space:nowrap}}
.phone small{{font-size:30px}}
.mail{{font-size:23px;font-weight:700;margin-top:8px}}
.goldbar{{position:absolute;left:0;right:0;bottom:0;height:70px;background:{GOLDBAR};display:flex;align-items:center;justify-content:center;gap:14px;font-family:PF;font-weight:700;font-size:27px;color:{INK}}}
.goldbar .sep{{opacity:.7}}
</style></head><body>
<div class="wedge"></div><div class="corner"></div><div class="frame"></div>
<div class="brand">{crest}<div><b>ROYAL CANADIAN</b><i>REALTY, BROKERAGE</i></div></div>
<div class="motto">&ldquo;Believe In The Best&rdquo;</div>
<span class="tag">{e(d.get('tag'))}</span>
<h1>{d.get('headline','')}</h1>
<div class="body"><p class="sub">{e(d.get('sub'))}</p>
<ul>{pts}</ul></div>
<div class="house">{house}</div>
<div class="redband">
  <div><div class="name">SATNAMPAL <span>Singh</span></div>
  <div class="role">Sales Representative · Gold Club Award Winner</div>
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
