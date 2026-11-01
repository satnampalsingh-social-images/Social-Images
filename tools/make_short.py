"""Render a branded 1080x1920 YouTube Short (MP4, 30 fps) in the business-card palette.
Usage: python3 make_short.py '<json>' out.mp4
JSON keys:
  tag      short uppercase topic label, e.g. "BRAMPTON BUYERS"
  hook     opening headline, max ~8 words; wrap 1-3 words in <em></em> for red italic
  hookSub  one line under the hook, max ~12 words
  points   exactly 3 objects {"title": max ~5 words, "text": max ~18 words}
  cta      call to action, e.g. "Book a free 15-min call"
Scenes: hook 3.5s, three points 4.5s each, contact card 4.5s (~21.5s total). Silent audio track.
"""
import json, sys, html, asyncio, os, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
PF, LA = f"{FONTS}/playfair-display-latin", f"{FONTS}/lato-latin"
RED, GOLD_L, GOLD_D, INK = "#e8323a", "#f4eb8d", "#b07a3c", "#31312f"
GOLDBAR = f"linear-gradient(90deg,{GOLD_D} 0%,#d9b25e 25%,{GOLD_L} 50%,#d9b25e 75%,{GOLD_D} 100%)"
W, H, FPS = 1080, 1920, 30

d = json.loads(sys.argv[1]); out = sys.argv[2]
e = lambda s: html.escape(s or "")

crest = f'''<svg viewBox="0 0 64 64" width="84" height="84"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_L}"/><stop offset=".5" stop-color="#d9b25e"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>
<path d="M14 14l6-8 6 6 6-9 6 9 6-6 6 8" fill="none" stroke="url(#g)" stroke-width="3" stroke-linejoin="round"/>
<circle cx="32" cy="36" r="20" fill="none" stroke="url(#g)" stroke-width="3.5"/>
<circle cx="32" cy="32" r="6" fill="{INK}"/><path d="M29 35h6l2 12H27z" fill="{INK}"/></svg>'''
house = f'''<svg viewBox="0 0 400 360" width="520" height="468"><defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2c463"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>
<g fill="none" stroke="url(#h)" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
<path d="M40 170L200 40l160 130"/><path d="M80 140v190h240V140"/><path d="M290 108V58h-34v22"/>
<rect x="170" y="230" width="60" height="100" rx="4"/><rect x="105" y="190" width="50" height="50"/><rect x="245" y="190" width="50" height="50"/>
<path d="M130 190v50M105 215h50M270 190v50M245 215h50"/><path d="M20 330h360"/></g>
<g transform="translate(250 268) rotate(-30)"><circle r="30" fill="{RED}" stroke="#fff" stroke-width="7"/><circle r="10" fill="#fff"/>
<path d="M30 0h86M92 0v22M108 0v16" stroke="{RED}" stroke-width="9" stroke-linecap="round" fill="none"/></g></svg>'''

CSS = f"""
@font-face{{font-family:PF;font-weight:700;src:url(file://{PF}-700-normal.woff2)}}
@font-face{{font-family:PF;font-weight:900;src:url(file://{PF}-900-normal.woff2)}}
@font-face{{font-family:PF;font-weight:700;font-style:italic;src:url(file://{PF}-700-italic.woff2)}}
@font-face{{font-family:LA;font-weight:400;src:url(file://{LA}-400-normal.woff2)}}
@font-face{{font-family:LA;font-weight:700;src:url(file://{LA}-700-normal.woff2)}}
@font-face{{font-family:LA;font-weight:900;src:url(file://{LA}-900-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;font-family:LA;color:{INK};position:relative;overflow:hidden;background:#fff;font-variant-numeric:lining-nums}}
.wedge{{position:absolute;left:0;top:0;width:44px;height:1500px;background:{RED}}}
.corner{{position:absolute;right:0;top:0;border-top:200px solid {RED};border-left:200px solid transparent}}
.brand{{position:absolute;left:96px;top:150px;display:flex;align-items:center;gap:18px}}
.brand b{{display:block;font-family:PF;font-weight:700;font-size:36px;letter-spacing:3px;border-bottom:3px solid #d9b25e;padding-bottom:3px}}
.brand i{{display:block;font-style:normal;font-family:PF;font-weight:700;font-size:20px;letter-spacing:4.5px;margin-top:6px}}
.tag{{display:inline-block;background:{RED};color:#fff;font-weight:900;font-size:34px;letter-spacing:4px;text-transform:uppercase;padding:14px 30px;border-radius:50px}}
.main{{position:absolute;left:96px;right:84px;top:380px}}
h1{{font-family:PF;font-weight:900;font-size:112px;line-height:1.04;margin-top:40px}}
h1 em,h2 em{{font-weight:700;font-style:italic;color:{RED}}}
.sub{{font-size:46px;line-height:1.35;color:#4a4a48;margin-top:40px}}
.num{{font-family:PF;font-weight:900;font-size:220px;line-height:1;color:{RED}}}
.num small{{font-size:70px;color:#c9a14f;font-weight:700}}
h2{{font-family:PF;font-weight:900;font-size:92px;line-height:1.06;margin-top:24px}}
.card{{margin-top:48px;background:#fbf3df;border-left:10px solid #d9b25e;padding:36px 40px;font-size:50px;line-height:1.38;font-weight:700}}
.house{{position:absolute;left:50%;transform:translateX(-50%);bottom:430px}}
.bar{{position:absolute;left:0;right:0;bottom:250px;height:10px;background:#eee}}
.bar i{{display:block;height:100%;background:{RED}}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:250px;background:{RED};color:#fff;text-align:center;padding-top:44px}}
.foot:before{{content:'';position:absolute;left:0;right:0;top:0;height:8px;background:{GOLDBAR}}}
.foot .n{{font-family:PF;font-weight:900;font-size:56px}}
.foot .n span{{font-style:italic;font-weight:700;color:#ffe2e3}}
.foot .r{{font-size:26px;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-top:12px}}
.foot .p{{font-family:PF;font-weight:900;font-size:46px;margin-top:10px}}
.cname{{font-family:PF;font-weight:900;font-size:104px;line-height:1}}
.cname span{{font-style:italic;font-weight:700;color:{RED}}}
.crole{{font-size:34px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;margin-top:22px}}
.award{{display:inline-block;margin-top:30px;background:{GOLDBAR};font-family:PF;font-weight:700;font-size:36px;padding:14px 32px;border-radius:50px}}
.ccta{{margin-top:70px;background:{RED};color:#fff;font-weight:900;font-size:50px;letter-spacing:2px;text-transform:uppercase;padding:34px 20px;border-radius:24px;text-align:center}}
.line{{font-size:46px;font-weight:700;margin-top:44px}}
.line.big{{font-family:PF;font-weight:900;font-size:84px;color:{RED};margin-top:56px}}
.sites{{font-family:PF;font-weight:700;font-size:44px;line-height:1.5;margin-top:40px}}
.subs{{position:absolute;left:0;right:0;bottom:0;height:200px;background:{GOLDBAR};display:flex;align-items:center;justify-content:center;font-family:PF;font-weight:900;font-size:54px}}
.motto{{font-family:PF;font-style:italic;font-weight:700;font-size:40px;margin-top:40px}}
"""

def frame(inner, progress=None, footer=True):
    bar = f'<div class="bar"><i style="width:{progress*100:.0f}%"></i></div>' if progress is not None else ""
    foot = ('<div class="foot"><div class="n">SATNAMPAL <span>Singh</span></div>'
            '<div class="r">Royal Canadian Realty, Brokerage</div><div class="p">647-780-2560</div></div>') if footer else ""
    return (f'<html><head><style>{CSS}</style></head><body><div class="wedge"></div><div class="corner"></div>'
            f'<div class="brand">{crest}<div><b>ROYAL CANADIAN</b><i>REALTY, BROKERAGE</i></div></div>'
            f'{inner}{bar}{foot}</body></html>')

pts = d["points"][:3]
scenes = [(frame(f'<div class="main"><span class="tag">{e(d.get("tag"))}</span><h1>{d["hook"]}</h1>'
                 f'<p class="sub">{e(d.get("hookSub"))}</p></div><div class="house">{house}</div>'), 3.5)]
for i, p in enumerate(pts, 1):
    scenes.append((frame(f'<div class="main"><div class="num">{i}<small>/3</small></div><h2>{e(p["title"])}</h2>'
                         f'<div class="card">{e(p["text"])}</div></div>', progress=i / 3), 4.5))
scenes.append((frame(f'<div class="main" style="top:330px"><div class="cname">SATNAMPAL <span>Singh</span></div>'
                     f'<div class="crole">Sales Representative</div><div class="award">Gold Club Award Winner</div>'
                     f'<div class="ccta">{e(d.get("cta","Book a free 15-min call"))}</div>'
                     f'<div class="line big">647-780-2560</div><div class="line">ssingh@royalcanadianrealty.com</div>'
                     f'<div class="sites">FindYourHouseInGTA.com<br>DreamHomeSeller.ca</div>'
                     f'<div class="motto">&ldquo;Believe In The Best&rdquo;</div></div>'
                     f'<div class="subs">Subscribe for weekly GTA tips</div>', footer=False), 4.5))

async def shoot(tmp):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        for i, (htm, _) in enumerate(scenes):
            hp = f"{tmp}/s{i}.html"; open(hp, "w").write(htm)
            await pg.goto("file://" + hp); await pg.evaluate("document.fonts.ready")
            await pg.screenshot(path=f"{tmp}/s{i}.png")
        await b.close()

tmp = tempfile.mkdtemp()
asyncio.run(shoot(tmp))
if os.environ.get("FRAMES_ONLY"):  # preview stills only
    for i in range(len(scenes)): shutil.copy(f"{tmp}/s{i}.png", f"{out}.s{i}.png")
    sys.exit(0)

enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS)]
lst = []
for i, (_, dur) in enumerate(scenes):
    fin = "" if i == 0 else "fade=t=in:st=0:d=0.3,"
    vf = f"format=yuv420p,loop=-1:1,trim=duration={dur},setpts=PTS-STARTPTS,{fin}fade=t=out:st={dur-0.3}:d=0.3"
    part, fin_path = f"{tmp}/p{i}.tmp.mp4", f"{tmp}/p{i}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/s{i}.png", "-vf", vf, *enc, part], check=True)
    os.rename(part, fin_path); lst.append(f"file '{fin_path}'")
open(f"{tmp}/list.txt", "w").write("\n".join(lst))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", f"{tmp}/v.mp4"], check=True)
tmpout = out + ".tmp.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/v.mp4", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", tmpout], check=True)
os.rename(tmpout, out)
shutil.rmtree(tmp)
print(out)
