"""Render a premium "infographic" post (navy + gold + red mixed with the brand colours).
Usage: python3 make_infographic.py '<json>' out.png
JSON keys:
  photo      file in assets/photos (approved photos of Satnampal / homes only), photoPos e.g. "50% 30%"
  tag        red ribbon text, e.g. "MORTGAGE 101"
  kicker     small caps line beside the ribbon, e.g. "FIRST-TIME BUYERS  ·  ONTARIO"
  headline   2-3 short lines; <em>..</em> = gold, <br> allowed
  sub        one sentence under the headline (max ~18 words)
  badge      {"top","value","label"}: gold coin with the big number (verified numbers only)
  cards      4 x {"icon": home|lock|cal|check|coin|people|chart|doc|pin, "title" (max 3 words), "text" (max ~9 words)}
  source     small source + disclaimer line
  cta        gold pill text, e.g. "Book a free buyer call"
  coinTop, subTop  optional pixel positions for the coin and the sub line
  size       optional headline font size (default 74)
  theme      "navy" (default) | "charcoal" | "red" (deep brand red with a gold ribbon): rotate daily
  format     "portrait" (1080x1350, default) or "landscape" (1200x900, for GBP)
Footer (fixed): official Royal Canadian Realty white logo, his name, title, phone, email, website, offices.
Never put other people, stock or AI images in "photo"; never recolour or redraw the logo.
"""
import json, sys, html, asyncio, os, tempfile
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
F = f"{HERE}/fonts"
d = json.loads(sys.argv[1]); out = sys.argv[2]
e = lambda s: html.escape(s or "")
land = d.get("format") == "landscape"
W, H = (1200, 900) if land else (1080, 1350)

NAVY, NAVY2, GOLD, GOLD_L, RED, INK = "#0E1B36", "#16294F", "#C79A3B", "#E8CF8E", "#ED1C24", "#252525"
# Colour theme for the top band, card titles and footer ("theme" key): navy (default) | charcoal | red
THEMES = {"navy": ("#0E1B36", "14,27,54"), "charcoal": ("#252525", "37,37,37"), "red": ("#7E0E14", "126,14,20")}
NAVY, RGB = THEMES.get(d.get("theme", "navy"), THEMES["navy"])
RIB_BG, RIB_FG = (GOLD, INK) if d.get("theme") == "red" else (RED, "#fff")
ic = {
 "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
 "lock": '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 018 0v3"/><circle cx="12" cy="15" r="1.4"/>',
 "cal": '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/><path d="M9 15l2 2 4-4"/>',
 "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16.5 9"/>',
 "coin": '<ellipse cx="12" cy="7" rx="7" ry="3"/><path d="M5 7v5c0 1.7 3.1 3 7 3s7-1.3 7-3V7"/><path d="M5 12v5c0 1.7 3.1 3 7 3s7-1.3 7-3v-5"/>',
 "people": '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M15 14.5c3 0 6 2 6 5.5"/>',
 "chart": '<path d="M4 20h16"/><rect x="6" y="12" width="3" height="6"/><rect x="11" y="8" width="3" height="10"/><rect x="16" y="4" width="3" height="14"/>',
 "doc": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
 "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 00-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
}
svg = lambda k, c="#fff": f'<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="{c}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ic.get(k, ic["check"])}</svg>'
cards = "".join(
    f'<div class="card"><div class="ci {"r" if i % 2 else ""}">{svg(c.get("icon"))}</div>'
    f'<div><div class="ct">{e(c.get("title"))}</div><div class="cx">{e(c.get("text"))}</div></div></div>'
    for i, c in enumerate(d.get("cards", [])[:4]))
b = d.get("badge")
badge = (f'<div class="coin"><div class="ring"><small>{e(b.get("top"))}</small><b>{e(b.get("value"))}</b>'
         f'<span>{e(b.get("label"))}</span></div></div>') if b else ""
photo = d.get("photo", "listing-facing.jpg")
hl = d.get("headline", "")  # trusted template input (em / br only)

TOP = 440 if land else 700
page = f"""<html><head><style>
@font-face{{font-family:PF;font-weight:900;src:url(file://{F}/playfair-display-latin-900-normal.woff2)}}
@font-face{{font-family:PF;font-weight:700;font-style:italic;src:url(file://{F}/playfair-display-latin-700-italic.woff2)}}
@font-face{{font-family:LA;font-weight:400;src:url(file://{F}/lato-latin-400-normal.woff2)}}
@font-face{{font-family:LA;font-weight:700;src:url(file://{F}/lato-latin-700-normal.woff2)}}
@font-face{{font-family:LA;font-weight:900;src:url(file://{F}/lato-latin-900-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:LA;background:#F3F3F1;position:relative}}
.top{{position:absolute;left:0;top:0;width:{W}px;height:{TOP}px;overflow:hidden;background:{NAVY}}}
.top .ph{{position:absolute;right:0;top:0;width:{int(W*0.62)}px;height:100%;background:url(file://{ROOT}/assets/photos/{photo}) {d.get("photoPos","50% 35%")}/cover}}
.top .fade{{position:absolute;inset:0;background:linear-gradient(90deg,{NAVY} 0%,{NAVY} 38%,rgba({RGB},.82) 55%,rgba({RGB},.15) 82%,rgba({RGB},0) 100%)}}
.top .fade2{{position:absolute;left:0;right:0;bottom:0;height:160px;background:linear-gradient(0deg,rgba({RGB},.85),rgba({RGB},0))}}
.swoosh{{position:absolute;left:0;top:{TOP-46}px;width:{W}px;height:90px}}
.logo{{position:absolute;left:56px;top:44px;height:{70 if land else 84}px}}
.rib{{position:absolute;left:56px;top:{150 if land else 168}px;display:flex;align-items:center;gap:18px}}
.rib b{{background:{RIB_BG};color:{RIB_FG};font-weight:900;letter-spacing:3px;font-size:22px;padding:10px 22px;border-radius:6px;box-shadow:0 6px 18px rgba(237,28,36,.35)}}
.rib span{{color:{GOLD_L};font-weight:700;letter-spacing:3px;font-size:18px}}
h1{{position:absolute;left:56px;top:{200 if land else 238}px;width:{620 if land else 640}px;color:#fff;font-family:PF;font-weight:900;font-size:{d.get("size",66 if land else 74)}px;line-height:1.06;text-shadow:0 3px 16px rgba(0,0,0,.35)}}
h1 em{{font-style:italic;color:{GOLD};background:linear-gradient(180deg,{GOLD_L},{GOLD});-webkit-background-clip:text;color:transparent}}
.sub{{position:absolute;left:56px;top:{d.get("subTop", 352 if land else 512)}px;width:{600 if land else 560}px;color:#E9ECF3;font-size:{24 if land else 27}px;line-height:1.38}}
.coin{{position:absolute;transform:scale({0.8 if land else 1});transform-origin:top right;right:{40 if land else 44}px;top:{d.get("coinTop", 250 if land else 300)}px;width:250px;height:250px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#F6E7B8 0%,{GOLD_L} 30%,{GOLD} 70%,#9A7429 100%);box-shadow:0 18px 40px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center}}
.ring{{width:212px;height:212px;border-radius:50%;border:3px solid rgba(255,255,255,.65);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.ring small{{font-weight:900;font-size:15px;letter-spacing:2px;color:{NAVY}}}
.ring b{{font-weight:900;font-size:50px;color:{RED};line-height:1.05;margin:4px 0}}
.ring span{{font-weight:700;font-size:16px;color:{NAVY};width:170px;line-height:1.2}}
.grid{{position:absolute;left:44px;right:44px;top:{TOP+44}px;display:grid;grid-template-columns:{"1fr 1fr 1fr 1fr" if land else "1fr 1fr"};gap:{16 if land else 20}px}}
.card{{background:#fff;border-radius:16px;padding:{"18px 14px" if land else "30px 24px"};display:flex;gap:{12 if land else 16}px;align-items:flex-start;box-shadow:0 10px 26px rgba({RGB},.10);border-top:5px solid {GOLD}}}
.ci{{flex:none;width:{56 if land else 70}px;height:{56 if land else 70}px;border-radius:50%;background:linear-gradient(145deg,{GOLD_L},{GOLD});display:flex;align-items:center;justify-content:center}}
.ci.r{{background:linear-gradient(145deg,#FF5A5F,{RED})}}
.ct{{font-weight:900;color:{NAVY};font-size:{16 if land else 25}px;letter-spacing:.5px;text-transform:uppercase;margin:4px 0 6px}}
.cx{{color:#4A5163;font-size:{15 if land else 21}px;line-height:1.35}}
.src{{position:absolute;left:56px;right:370px;top:{H-205 if not land else H-215}px;color:#6B7183;font-size:15px;line-height:1.35}}
.cta{{position:absolute;right:44px;top:{H-218 if not land else H-230}px;background:linear-gradient(90deg,{RED},#C4161D);color:#fff;font-weight:900;font-size:21px;letter-spacing:1px;padding:15px 26px;border-radius:40px;box-shadow:0 8px 20px rgba(237,28,36,.35)}}
.foot{{position:absolute;left:0;bottom:0;width:{W}px;height:{150 if land else 160}px;background:{NAVY};border-top:5px solid {GOLD};display:flex;align-items:center;padding:0 44px;gap:26px}}
.foot .lg{{height:74px}}
.foot .bar{{width:2px;height:92px;background:{GOLD};opacity:.8}}
.who b{{display:block;color:#fff;font-family:PF;font-weight:900;font-size:32px}}
.who span{{display:block;color:#D9DDE7;font-size:16px;margin-top:2px}}
.who i{{display:block;font-style:normal;color:{GOLD_L};font-size:14px;letter-spacing:1.5px;margin-top:6px;font-weight:700}}
.ph2{{margin-left:auto;text-align:right}}
.ph2 b{{display:inline-block;background:linear-gradient(90deg,{GOLD_L},{GOLD});color:{NAVY};font-weight:900;font-size:31px;padding:8px 22px;border-radius:30px}}
.ph2 span{{display:block;color:#fff;font-size:16px;margin-top:8px}}
.corner{{position:absolute;right:0;bottom:0;width:0;height:0;border-left:70px solid transparent;border-bottom:70px solid {RED}}}
</style></head><body>
<div class="top"><div class="ph"></div><div class="fade"></div><div class="fade2"></div></div>
<svg class="swoosh" viewBox="0 0 {W} 90" preserveAspectRatio="none"><path d="M0 46 C {W*0.3} 0, {W*0.6} 90, {W} 30 L {W} 90 L 0 90 Z" fill="#F3F3F1"/><path d="M0 46 C {W*0.3} 0, {W*0.6} 90, {W} 30" fill="none" stroke="{GOLD}" stroke-width="5"/></svg>
<img class="logo" src="file://{ROOT}/assets/brand/logo-white.png">
<div class="rib"><b>{e(d.get("tag"))}</b><span>{e(d.get("kicker"))}</span></div>
<h1>{hl}</h1>
<div class="sub">{e(d.get("sub"))}</div>
{badge}
<div class="grid">{cards}</div>
<div class="src">{e(d.get("source"))}</div>
<div class="cta">{e(d.get("cta"))}</div>
<div class="foot"><img class="lg" src="file://{ROOT}/assets/brand/logo-white.png"><div class="bar"></div>
<div class="who"><b>Satnampal Singh</b><span>Real Estate Sales Representative · Gold Club Award Winner</span><i>MISSISSAUGA · MARKHAM · KITCHENER · HAMILTON</i></div>
<div class="ph2"><b>647-780-2560</b><span>FindYourHouseInGTA.com</span></div></div>
<div class="corner"></div>
</body></html>"""

async def main():
    f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False); f.write(page); f.close()
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": W, "height": H})
        await pg.goto("file://" + f.name); await pg.evaluate("document.fonts.ready")
        await pg.screenshot(path=out); await br.close()
asyncio.run(main())
