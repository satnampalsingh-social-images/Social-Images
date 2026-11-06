"""Render a branded 1080x1080 real-estate post image (business-card palette: red, white, gold).
Usage: python3 make_post_image.py '<json>' out.png
JSON keys: tag, headline (may use <em>..</em> for red italic), sub, points (<=3), cta, subTop,\n  art: "headshot" (default; his photo in a gold ring, bottom right) or "house" (line illustration)\n  Portrait layouts (1080x1350, 4:5, best for IG/FB feeds):\n    "photo":    full-bleed photo of Satnampal (photo: autumn-suit-full.jpg | staircase-pose.jpg | silver-club-award-2023.jpg; photoY e.g. "18%"), tag, headline, sub, cta\n    "split":    charcoal text panel + photo column (photo: listing-facing.jpg | listing-gesture.jpg | luxury-home.jpg | any assets/photos file), tag, headline, sub, points (3), cta\n    "bold":     red myth-vs-fact card, no photo: tag, headline, myth, fact, cta\n    "question": charcoal poll/question, no photo: tag, headline, sub, options (3), cta\n    optional "size" overrides the headline font size
    optional "theme" (brand colour scheme): "charcoal" (default) | "red" (red gradient) | "gold" (gold gradient, charcoal text) | "light" (white/light grey)
      split + question use all four; bold uses red (default) | charcoal | gold; photo uses charcoal (default) | red | gold for the shading behind the text\n  layout: "stats" (optional, for market updates): hero {value,label,note}, stats [{value,label,change,dir:"down"|"up"}] (3), takeaway\nTop-left uses the official Royal Canadian Realty logo from assets/brand/logo-gold.png.
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

# ---------- 4:5 portrait layouts (1080x1350): photo, split, bold, question ----------
H = 1080
PHOTOS = os.path.join(os.path.dirname(HERE), "assets", "photos")
FONTCSS = f"""@font-face{{font-family:PF;font-weight:700;src:url(file://{PF}-700-normal.woff2)}}
@font-face{{font-family:PF;font-weight:900;src:url(file://{PF}-900-normal.woff2)}}
@font-face{{font-family:PF;font-weight:700;font-style:italic;src:url(file://{PF}-700-italic.woff2)}}
@font-face{{font-family:LA;font-weight:400;src:url(file://{LA}-400-normal.woff2)}}
@font-face{{font-family:LA;font-weight:700;src:url(file://{LA}-700-normal.woff2)}}
@font-face{{font-family:LA;font-weight:900;src:url(file://{LA}-900-normal.woff2)}}"""
lay = d.get("layout", "")
if lay in ("photo", "split", "bold", "question"):
    H = 1350
    GOLD = "#C79A3B"
    # Colour themes (all from his brand palette). "theme" key: charcoal | red | gold | light
    GOLDGRAD = f"linear-gradient(135deg,{GOLD_D} 0%,#C79A3B 40%,{GOLD_L} 75%,#C79A3B 100%)"
    REDGRAD = f"linear-gradient(160deg,{RED} 0%,{RED_D} 100%)"
    THEMES = {
      "charcoal": dict(bg=INK, fg="#fff", sub="#d8d8d8", em=GOLD, pill=RED, dot=RED, dotfg="#fff", stripe=RED, logo="logo-white.png",
                       ctabg="#fff", ctafg=RED, opbg="#333", opbd="#4a4a4a", glyph=GOLD, shade="20,20,20"),
      "red":      dict(bg=REDGRAD, fg="#fff", sub="#ffe3e4", em="#FFE7A8", pill=INK, dot=INK, dotfg=GOLD_L, stripe=GOLD, logo="logo-white.png",
                       ctabg="#fff", ctafg=RED, opbg="rgba(0,0,0,.18)", opbd="rgba(255,255,255,.35)", glyph="#fff", shade="150,14,20"),
      "gold":     dict(bg=GOLDGRAD, fg=INK, sub="#3a3226", em=RED, pill=RED, dot=INK, dotfg=GOLD_L, stripe=INK, logo="logo-black.png",
                       ctabg=INK, ctafg="#fff", opbg="rgba(255,255,255,.55)", opbd="rgba(37,37,37,.25)", glyph="#fff", shade="120,90,30"),
      "light":    dict(bg="linear-gradient(180deg,#FFFFFF 0%,#EFEFEF 100%)", fg=INK, sub="#555", em=RED, pill=RED, dot=RED, dotfg="#fff", stripe=GOLD, logo="logo-gold.png",
                       ctabg=RED, ctafg="#fff", opbg="#fff", opbd="#DCC38A", glyph=RED, shade="20,20,20"),
    }
    T = THEMES.get(d.get("theme", "charcoal"), THEMES["charcoal"])
    foot = f"""<div class="ft"><div><div class="nm">SATNAMPAL <i>Singh</i></div>
<div class="rl">Real Estate Sales Representative · Royal Canadian Realty, Brokerage</div></div>
<div class="ct"><div class="ph">647-780-2560</div><div class="wb">FindYourHouseInGTA.com</div></div></div><div class="gb"></div>"""
    base = f"""{FONTCSS}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:LA;position:relative;overflow:hidden;background:#fff;color:{INK}}}
.ft{{position:absolute;left:0;right:0;bottom:14px;height:150px;background:{INK};color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 56px}}
.ft .nm{{font-family:PF;font-weight:900;font-size:44px;line-height:1}} .ft .nm i{{font-weight:700;color:{GOLD}}}
.ft .rl{{font-size:17px;font-weight:700;letter-spacing:1px;margin-top:10px;text-transform:uppercase;color:#ddd;white-space:nowrap}}
.ft .ct{{text-align:right}} .ft .ph{{font-family:PF;font-weight:900;font-size:44px;font-variant-numeric:lining-nums;white-space:nowrap}}
.ft .wb{{font-size:22px;font-weight:700;color:{GOLD};margin-top:6px}}
.gb{{position:absolute;left:0;right:0;bottom:0;height:14px;background:{GOLDBAR}}}
.logo{{position:absolute;left:56px;top:50px;height:96px}}
.pill{{display:inline-block;background:{RED};color:#fff;font-weight:900;font-size:22px;letter-spacing:3px;text-transform:uppercase;padding:11px 22px;border-radius:40px}}
.cta{{display:inline-block;background:#fff;color:{RED};font-weight:900;font-size:24px;letter-spacing:2px;text-transform:uppercase;padding:14px 28px;border-radius:40px;box-shadow:0 6px 18px rgba(0,0,0,.25)}}
h1{{font-family:PF;font-weight:900;line-height:1.04;font-variant-numeric:lining-nums}}
"""
    if lay == "photo":
        img = d.get("photo", "staircase-pose.jpg")
        body = f"""<style>{base}
.bg{{position:absolute;inset:0 0 164px 0;background:url(file://{PHOTOS}/{img}) center {d.get('photoY','18%')}/cover}}
.sh{{position:absolute;inset:0 0 164px 0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 40%,rgba({T['shade']},.88) 66%,rgba({T['shade']},.97) 100%)}}
.tx{{position:absolute;left:56px;right:56px;bottom:200px;color:#fff}}
.tx h1{{font-size:{d.get('size',88)}px;margin:22px 0 18px;text-shadow:0 3px 14px rgba(0,0,0,.4)}} .tx h1 em{{font-style:italic;font-weight:700;color:{T['em'] if d.get('theme') in ('red',) else GOLD}}}
.tx p{{font-size:32px;line-height:1.35;color:#f1f1f1;max-width:900px;margin-bottom:28px}}
</style><div class="bg"></div><div class="sh"></div><img class="logo" src="file://{BRAND}/logo-white.png">
<div class="tx"><span class="pill">{e(d.get('tag'))}</span><h1>{d.get('headline','')}</h1><p>{e(d.get('sub'))}</p><span class="cta">{e(d.get('cta','Book a free call'))}</span></div>{foot}"""
    elif lay == "split":
        img = d.get("photo", "listing-facing.jpg")
        lis = "".join(f'<li><b>{i+1}</b><span>{e(x)}</span></li>' for i, x in enumerate(d.get("points", [])[:3]))
        body = f"""<style>{base}
body{{background:{T['bg']}}}
.ph2{{position:absolute;right:0;top:0;width:440px;bottom:164px;background:url(file://{PHOTOS}/{img}) {d.get('photoX','50%')} {d.get('photoY','30%')}/cover}}
.ph2:before{{content:'';position:absolute;left:0;top:0;bottom:0;width:10px;background:{T['stripe']}}}
.lt{{position:absolute;left:56px;width:550px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;top:170px;bottom:184px;color:{T['fg']}}}
.lt h1{{font-size:{d.get('size',76)}px;margin:24px 0 18px}} .lt h1 em{{font-style:italic;font-weight:700;color:{T['em']}}}
.lt p{{font-size:31px;line-height:1.4;color:{T['sub']}}}
.lt .pill{{background:{T['pill']}}} .lt .cta{{background:{T['ctabg']};color:{T['ctafg']}}}
.lt ul{{list-style:none;margin:28px 0 34px}} .lt li{{display:flex;gap:18px;align-items:center;font-size:32px;font-weight:700;margin:20px 0}}
.lt li b{{flex:0 0 52px;height:52px;border-radius:50%;background:{T['dot']};color:{T['dotfg']};display:flex;align-items:center;justify-content:center;font-family:PF;font-size:28px}}
</style><img class="logo" src="file://{BRAND}/{T['logo']}"><div class="ph2"></div>
<div class="lt"><span class="pill">{e(d.get('tag'))}</span><h1>{d.get('headline','')}</h1><p>{e(d.get('sub'))}</p><ul>{lis}</ul><span class="cta">{e(d.get('cta','Book a free call'))}</span></div>{foot}"""
    elif lay == "bold":
        TB = T if d.get("theme") in ("charcoal","gold") else THEMES["red"]
        body = f"""<style>{base}
body{{background:{TB['bg']}}}
.bx{{position:absolute;left:56px;right:56px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;top:170px;bottom:184px;color:{TB['fg']}}}
.bx h1{{font-size:{d.get('size',92)}px;margin:26px 0 34px}} .bx h1 em{{font-style:italic;font-weight:700;color:{TB['em']}}}
.card{{align-self:stretch;border-radius:18px;padding:30px 34px;margin-bottom:24px;font-size:37px;line-height:1.35}}
.card small{{display:block;font-size:20px;font-weight:900;letter-spacing:3px;margin-bottom:8px}}
.myth{{background:{'rgba(0,0,0,.18)' if TB is THEMES['red'] else TB['opbg']};color:{'#ffe0e0' if TB is THEMES['red'] else TB['fg']}}} .myth span{{text-decoration:line-through;text-decoration-thickness:3px}}
.fact{{background:#fff;color:{INK};border-left:12px solid {GOLD}}} .fact small{{color:#1d8a4a}}
.bx .cta{{background:{INK if TB is not THEMES['charcoal'] else RED};color:#fff;margin-top:8px}}
</style><img class="logo" src="file://{BRAND}/{TB['logo']}">
<div class="bx"><span class="pill" style="background:{INK if TB is not THEMES['charcoal'] else RED}">{e(d.get('tag','MYTH VS FACT'))}</span><h1>{d.get('headline','')}</h1>
<div class="card myth"><small>&#10007; MYTH</small><span>{e(d.get('myth'))}</span></div>
<div class="card fact"><small>&#10003; FACT</small>{e(d.get('fact'))}</div><span class="cta">{e(d.get('cta','Ask me anything'))}</span></div>{foot}"""
    else:  # question
        opts = "".join(f'<div class="op"><b>{"ABC"[i]}</b>{e(x)}</div>' for i, x in enumerate(d.get("options", [])[:3]))
        body = f"""<style>{base}
body{{background:{T['bg']}}}
.q{{position:absolute;right:30px;top:120px;font-family:PF;font-weight:900;font-size:560px;line-height:1;color:{T['glyph']};opacity:.16}}
.qx{{position:absolute;left:56px;right:56px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;top:170px;bottom:184px;color:{T['fg']}}}
.qx h1{{font-size:{d.get('size',80)}px;margin:26px 0 20px}} .qx h1 em{{font-style:italic;font-weight:700;color:{T['em']}}}
.qx p{{font-size:29px;color:{T['sub']};margin-bottom:30px}}
.qx .pill{{background:{T['pill']}}}
.op{{align-self:stretch;display:flex;align-items:center;gap:22px;background:{T['opbg']};border:2px solid {T['opbd']};border-radius:16px;padding:20px 26px;margin:16px 0;font-size:32px;font-weight:700}}
.op b{{flex:0 0 58px;height:58px;border-radius:50%;background:{T['dot']};color:{T['dotfg']};display:flex;align-items:center;justify-content:center;font-family:PF;font-size:30px}}
.qx .cta{{margin-top:18px;background:{T['ctabg']};color:{T['ctafg']}}}
</style><div class="q">?</div><img class="logo" src="file://{BRAND}/{T['logo']}">
<div class="qx"><span class="pill">{e(d.get('tag','YOUR TURN'))}</span><h1>{d.get('headline','')}</h1><p>{e(d.get('sub'))}</p>{opts}<span class="cta">{e(d.get('cta','Comment A, B or C'))}</span></div>{foot}"""
    page = f"<html><head></head><body>{body}</body></html>"

async def main():
    f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False); f.write(page); f.close()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox","--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width":1080,"height":H})
        await pg.goto("file://" + f.name); await pg.evaluate("document.fonts.ready")
        await pg.screenshot(path=out); await b.close()
asyncio.run(main())
