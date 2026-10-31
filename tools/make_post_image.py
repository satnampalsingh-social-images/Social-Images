"""Render a branded 1080x1080 real-estate post image (blog palette).
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
check = '<svg viewBox="0 0 24 24" width="34" height="34"><circle cx="12" cy="12" r="11" fill="#efd87b"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#9c0c23" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
pts = "".join(f'<li>{check}<span>{e(p)}</span></li>' for p in d.get("points", [])[:3])

# keyhole crest mark
crest = '''<svg viewBox="0 0 64 64" width="58" height="58"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#efd87b"/><stop offset="1" stop-color="#bf883b"/></linearGradient></defs>
<path d="M32 3l24 9v16c0 16-10 27-24 33C18 55 8 44 8 28V12z" fill="none" stroke="url(#g)" stroke-width="3"/>
<circle cx="32" cy="26" r="7" fill="url(#g)"/><path d="M28.5 30h7l2.5 15h-12z" fill="url(#g)"/></svg>'''

# house + key line illustration
house = '''<svg viewBox="0 0 400 360" width="400" height="360"><defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#efd87b"/><stop offset="1" stop-color="#bf883b"/></linearGradient></defs>
<g fill="none" stroke="url(#h)" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
<path d="M40 170L200 40l160 130"/><path d="M80 140v190h240V140"/><path d="M290 108V58h-34v22"/>
<rect x="170" y="230" width="60" height="100" rx="4"/><rect x="105" y="190" width="50" height="50"/><rect x="245" y="190" width="50" height="50"/>
<path d="M130 190v50M105 215h50M270 190v50M245 215h50"/><path d="M20 330h360"/></g>
<g transform="translate(250 268) rotate(-30)"><circle cx="0" cy="0" r="30" fill="#9c0c23" stroke="#efd87b" stroke-width="7"/><circle cx="0" cy="0" r="10" fill="#efd87b"/>
<path d="M30 0h86M92 0v22M108 0v16" stroke="#efd87b" stroke-width="9" stroke-linecap="round" fill="none"/></g></svg>'''

page = f"""<html><head><style>
@font-face{{font-family:PF;font-weight:700;src:url(file://{PF}-700-normal.woff2)}}
@font-face{{font-family:PF;font-weight:900;src:url(file://{PF}-900-normal.woff2)}}
@font-face{{font-family:PF;font-weight:700;font-style:italic;src:url(file://{PF}-700-italic.woff2)}}
@font-face{{font-family:LA;font-weight:400;src:url(file://{LA}-400-normal.woff2)}}
@font-face{{font-family:LA;font-weight:700;src:url(file://{LA}-700-normal.woff2)}}
@font-face{{font-family:LA;font-weight:900;src:url(file://{LA}-900-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;font-family:LA;color:#fff;position:relative;overflow:hidden;
 background:radial-gradient(circle at 85% 20%,#d81a3a 0%,#c8102e 35%,#9c0c23 75%,#7a0819 100%)}}
.pattern{{position:absolute;inset:0;opacity:.07;background:repeating-linear-gradient(45deg,#efd87b 0 2px,transparent 2px 38px)}}
.frame{{position:absolute;inset:30px 30px 210px 30px;border:2px solid rgba(239,216,123,.55)}}
.brand{{position:absolute;left:84px;top:78px;display:flex;align-items:center;gap:16px}}
.brand b{{display:block;font-family:PF;font-weight:700;font-size:24px;letter-spacing:3px;color:#efd87b}}
.brand i{{display:block;font-style:normal;font-size:16px;letter-spacing:5px;color:#f5e6c8;margin-top:2px}}
.tag{{position:absolute;left:84px;top:178px;background:linear-gradient(90deg,#efd87b,#bf883b);color:#7a0819;font-weight:900;font-size:22px;letter-spacing:3px;text-transform:uppercase;padding:11px 22px;border-radius:40px}}
h1{{font-variant-numeric:lining-nums;position:absolute;left:84px;right:84px;top:248px;font-family:PF;font-weight:900;font-size:78px;line-height:1.05;text-shadow:0 3px 18px rgba(60,0,10,.35)}}
h1 em{{font-weight:700;font-style:italic;color:#efd87b}}
.body{{position:absolute;left:84px;width:590px;top:{d.get('subTop',540)}px}}
.sub{{font-size:29px;line-height:1.4;color:#fbe9ea}}
ul{{list-style:none;margin-top:22px}}
li{{display:flex;align-items:center;gap:16px;font-size:29px;font-weight:700;line-height:1.3;margin-top:18px;background:rgba(122,8,25,.45);border-left:4px solid #efd87b;padding:12px 18px}}
li svg{{flex:0 0 34px;margin-top:0}}
.house{{position:absolute;right:40px;bottom:236px;opacity:.95;transform:scale(.85);transform-origin:bottom right}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:180px;background:#0e0e0e;display:flex;align-items:center;justify-content:space-between;padding:0 84px}}
.foot:before{{content:'';position:absolute;left:0;right:0;top:0;height:6px;background:linear-gradient(90deg,#bf883b,#efd87b,#bf883b)}}
.name{{font-family:PF;font-weight:700;font-size:40px}}
.role{{font-size:18px;color:#cfcfcf;margin-top:6px;letter-spacing:.5px}}
.motto{{font-family:PF;font-style:italic;font-weight:700;font-size:21px;color:#efd87b;margin-top:8px}}
.contact{{text-align:right}}
.phone{{font-weight:900;font-size:44px;color:#efd87b;letter-spacing:1px}}
.web{{font-size:22px;color:#fff;margin-top:4px}}
.cta{{display:inline-block;margin-top:8px;background:#c8102e;color:#fff;font-weight:900;font-size:17px;letter-spacing:2px;text-transform:uppercase;padding:7px 16px;border-radius:30px}}
</style></head><body>
<div class="pattern"></div><div class="frame"></div>
<div class="brand">{crest}<div><b>ROYAL CANADIAN</b><i>REALTY BROKERAGE</i></div></div>
<span class="tag">{e(d.get('tag'))}</span>
<h1>{d.get('headline','')}</h1>
<div class="body"><p class="sub">{e(d.get('sub'))}</p>
<ul>{pts}</ul></div>
<div class="house">{house}</div>
<div class="foot">
  <div><div class="name">Satnampal Singh</div>
  <div class="role">Sales Representative · Gold Club Award Winner</div>
  <div class="motto">Believe In The Best</div></div>
  <div class="contact"><div class="phone">647-780-2560</div>
  <div class="web">findyourhouseingta.com</div>
  <div class="cta">{e(d.get('cta','Book a free call'))}</div></div>
</div></body></html>"""

async def main():
    f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False); f.write(page); f.close()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox","--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width":1080,"height":1080})
        await pg.goto("file://" + f.name); await pg.evaluate("document.fonts.ready")
        await pg.screenshot(path=out); await b.close()
asyncio.run(main())
