"""Render an engaging branded 1080x1920 YouTube Short (MP4, 30 fps) with photos of Satnampal.
Usage: python3 make_short.py '<json>' out.mp4
JSON keys:
  tag      short uppercase topic label, e.g. "BRAMPTON BUYERS"
  hook     opening headline, max ~7 words; wrap 1-3 words in <em></em> for gold italic
  hookSub  one line under the hook, max ~10 words
  points   exactly 3 objects {"title": max ~5 words, "text": max ~16 words}
  cta      call to action, e.g. "Book a free 15-min call"
  voice    optional list of 5 narration lines (hook, point 1, 2, 3, closing). Spoken by a Piper
           text-to-speech narrator (third person); each scene stretches to fit its line.
  photos   optional list of 4 file names from assets/photos for hook, point 1, 2, 3
           (default: a rotation of the non-headshot photos). CTA always uses headshot.jpg.
Scenes: hook 3.4s, three points 4.2s each, CTA 4.6s (~20.6s). Photos slowly zoom; text slides in.
Keep text out of the bottom ~420px and right ~160px (YouTube Shorts UI covers them).
Env FRAMES_ONLY=1 writes the final-state still of each scene to <out>.s<N>.png instead of a video.
"""
import json, sys, html, asyncio, os, subprocess, tempfile, shutil, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHOTOS = os.path.join(ROOT, "assets", "photos")
FONTS = os.path.join(HERE, "fonts")
PF, LA = f"{FONTS}/playfair-display-latin", f"{FONTS}/lato-latin"
RED, GOLD_L, GOLD_D, INK = "#e8323a", "#f4eb8d", "#b07a3c", "#31312f"
GOLDBAR = f"linear-gradient(90deg,{GOLD_D} 0%,#d9b25e 25%,{GOLD_L} 50%,#d9b25e 75%,{GOLD_D} 100%)"
W, H, FPS = 1080, 1920, 30

d = json.loads(sys.argv[1]); out = sys.argv[2]
e = lambda s: html.escape(s or "")

pool = sorted(f for f in os.listdir(PHOTOS) if f.lower().endswith((".jpg", ".jpeg", ".png")) and not f.startswith("headshot"))
photos = d.get("photos") or (lambda p: (p * 4)[:4])(random.sample(pool, len(pool)))
headshot = os.path.join(PHOTOS, "headshot.jpg")

crest = f'''<svg viewBox="0 0 64 64" width="58" height="58"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_L}"/><stop offset=".5" stop-color="#d9b25e"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient></defs>
<path d="M14 14l6-8 6 6 6-9 6 9 6-6 6 8" fill="none" stroke="url(#g)" stroke-width="3.4" stroke-linejoin="round"/>
<circle cx="32" cy="36" r="20" fill="none" stroke="url(#g)" stroke-width="3.8"/>
<circle cx="32" cy="32" r="6" fill="#fff"/><path d="M29 35h6l2 12H27z" fill="#fff"/></svg>'''

CSS = f"""
@font-face{{font-family:PF;font-weight:700;src:url(file://{PF}-700-normal.woff2)}}
@font-face{{font-family:PF;font-weight:900;src:url(file://{PF}-900-normal.woff2)}}
@font-face{{font-family:PF;font-weight:700;font-style:italic;src:url(file://{PF}-700-italic.woff2)}}
@font-face{{font-family:LA;font-weight:400;src:url(file://{LA}-400-normal.woff2)}}
@font-face{{font-family:LA;font-weight:700;src:url(file://{LA}-700-normal.woff2)}}
@font-face{{font-family:LA;font-weight:900;src:url(file://{LA}-900-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:transparent}}
body{{width:{W}px;height:{H}px;font-family:LA;position:relative;overflow:hidden;font-variant-numeric:lining-nums;color:#fff}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 18%,rgba(0,0,0,0) 38%,rgba(0,0,0,.78) 60%,rgba(0,0,0,.88) 100%)}}
.brand{{position:absolute;left:60px;top:90px;display:flex;align-items:center;gap:14px;text-shadow:0 2px 8px rgba(0,0,0,.5)}}
.brand b{{display:block;font-family:PF;font-weight:700;font-size:30px;letter-spacing:3px;border-bottom:3px solid #d9b25e;padding-bottom:2px}}
.brand i{{display:block;font-style:normal;font-family:PF;font-weight:700;font-size:17px;letter-spacing:4px;margin-top:5px}}
.who{{position:absolute;right:60px;top:96px;text-align:right;text-shadow:0 2px 8px rgba(0,0,0,.6)}}
.who b{{display:block;font-family:PF;font-weight:900;font-size:34px}}
.who span{{display:block;font-weight:900;font-size:28px;color:{GOLD_L};margin-top:4px}}
.zone{{position:absolute;left:60px;right:170px}}
.tag{{display:inline-block;background:{RED};color:#fff;font-weight:900;font-size:32px;letter-spacing:4px;text-transform:uppercase;padding:12px 28px;border-radius:50px;box-shadow:0 6px 20px rgba(0,0,0,.35)}}
h1{{font-family:PF;font-weight:900;font-size:104px;line-height:1.02;text-shadow:0 4px 18px rgba(0,0,0,.6)}}
h1 em,h2 em{{font-weight:700;font-style:italic;color:{GOLD_L}}}
.sub{{font-size:42px;font-weight:700;line-height:1.3;text-shadow:0 2px 10px rgba(0,0,0,.7)}}
.num{{display:flex;align-items:flex-end;gap:18px}}
.num b{{font-family:PF;font-weight:900;font-size:150px;line-height:.8;color:{RED};text-shadow:0 4px 14px rgba(0,0,0,.5)}}
.num span{{font-family:PF;font-weight:700;font-size:48px;color:{GOLD_L};padding-bottom:6px}}
h2{{font-family:PF;font-weight:900;font-size:82px;line-height:1.05;margin-top:22px;text-shadow:0 4px 16px rgba(0,0,0,.6)}}
.card{{background:rgba(255,255,255,.95);color:{INK};border-left:12px solid {RED};border-radius:10px;padding:30px 34px;font-size:44px;line-height:1.32;font-weight:700;box-shadow:0 10px 30px rgba(0,0,0,.35)}}
.bar{{position:absolute;left:60px;right:60px;top:186px;height:8px;background:rgba(255,255,255,.3);border-radius:8px;overflow:hidden}}
.bar i{{display:block;height:100%;background:{RED}}}
.cta-bg{{position:absolute;inset:0;background:#fff}}
.cta-bg:before{{content:'';position:absolute;left:0;top:0;width:40px;height:100%;background:{RED}}}
.cta-bg:after{{content:'';position:absolute;right:0;top:0;border-top:200px solid {RED};border-left:200px solid transparent}}
.photo{{position:absolute;left:50%;top:150px;transform:translateX(-50%);width:560px;height:560px;border-radius:50%;overflow:hidden;border:12px solid {RED};box-shadow:0 0 0 8px #e6cf8a,0 18px 40px rgba(0,0,0,.25)}}
.photo img{{width:100%;height:100%;object-fit:cover;object-position:50% 20%}}
.c{{position:absolute;left:80px;right:80px;text-align:center;color:{INK}}}
.cname{{font-family:PF;font-weight:900;font-size:86px;line-height:1}}
.cname span{{font-style:italic;font-weight:700;color:{RED}}}
.crole{{font-size:30px;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-top:14px}}
.award{{display:inline-block;margin-top:20px;background:{GOLDBAR};font-family:PF;font-weight:700;font-size:32px;padding:10px 30px;border-radius:50px}}
.ccta{{background:{RED};color:#fff;font-weight:900;font-size:46px;letter-spacing:2px;text-transform:uppercase;padding:30px 20px;border-radius:24px;box-shadow:0 10px 24px rgba(232,50,58,.35)}}
.phone{{font-family:PF;font-weight:900;font-size:92px;color:{RED};line-height:1}}
.mail{{font-size:36px;font-weight:700;margin-top:16px}}
.sites{{font-family:PF;font-weight:700;font-size:36px;margin-top:10px}}
.subs{{position:absolute;left:0;right:0;bottom:0;height:150px;background:{GOLDBAR};display:flex;align-items:center;justify-content:center;font-family:PF;font-weight:900;font-size:50px;color:{INK}}}
"""

def page(inner):
    return f'<html><head><style>{CSS}</style></head><body>{inner}</body></html>'

TOP = (f'<div class="shade"></div><div class="brand">{crest}<div><b>ROYAL CANADIAN</b><i>REALTY, BROKERAGE</i></div></div>'
       f'<div class="who"><b>Satnampal Singh</b><span>647-780-2560</span></div>')

# Each scene: background (photo path or None for white), duration, html (one flowing layout), layer start times.
# Elements tagged class="Lk" belong to layer k; each layer is rendered alone with the others hidden,
# so every layer keeps its exact position in the shared layout and nothing can overlap.
pts = d["points"][:3]
scenes = [dict(bg=os.path.join(PHOTOS, photos[0]), dur=3.4, starts=[0, 0.1, 0.3, 1.1], html=
    f'<div class="L0">{TOP}</div><div class="zone" style="top:960px">'
    f'<div class="L1"><span class="tag">{e(d.get("tag"))}</span></div>'
    f'<h1 class="L2" style="margin-top:26px">{d["hook"]}</h1>'
    f'<p class="sub L3" style="margin-top:24px">{e(d.get("hookSub"))}</p></div>')]
for i, p in enumerate(pts, 1):
    scenes.append(dict(bg=os.path.join(PHOTOS, photos[i]), dur=4.2, starts=[0, 0.1, 0.6], html=
        f'<div class="L0">{TOP}<div class="bar"><i style="width:{i/3*100:.0f}%"></i></div></div>'
        f'<div class="zone" style="top:900px"><div class="L1"><div class="num"><b>{i}</b><span>/ 3</span></div><h2>{e(p["title"])}</h2></div>'
        f'<div class="card L2" style="margin-top:30px">{e(p["text"])}</div></div>'))
scenes.append(dict(bg=None, dur=4.6, starts=[0, 0.15, 0.5, 0.85, 1.2], html=
    f'<div class="L0"><div class="cta-bg"></div><div class="photo"><img src="file://{headshot}"></div></div>'
    f'<div class="c" style="top:770px"><div class="L1"><div class="cname">SATNAMPAL <span>Singh</span></div>'
    f'<div class="crole">Sales Representative · Royal Canadian Realty</div><div class="award">Gold Club Award Winner</div></div>'
    f'<div class="L2" style="margin-top:44px"><div class="ccta">{e(d.get("cta","Book a free 15-min call"))}</div></div>'
    f'<div class="L3" style="margin-top:40px"><div class="phone">647-780-2560</div><div class="mail">ssingh@royalcanadianrealty.com</div>'
    f'<div class="sites">FindYourHouseInGTA.com · DreamHomeSeller.ca</div></div></div>'
    f'<div class="subs L4">Subscribe for weekly GTA tips</div>'))
for sc in scenes:
    sc["layers"] = [(k, st) for k, st in enumerate(sc["starts"])]

async def shoot(tmp):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        for si, sc in enumerate(scenes):
            n = len(sc["layers"])
            for li, _ in sc["layers"]:
                hide = ",".join(f".L{k}" for k in range(n) if k != li)
                hp = f"{tmp}/s{si}l{li}.html"
                open(hp, "w").write(page(sc["html"]).replace("</style>", f"{hide}{{visibility:hidden!important}}</style>"))
                await pg.goto("file://" + hp); await pg.evaluate("document.fonts.ready")
                await pg.wait_for_timeout(50)
                await pg.screenshot(path=f"{tmp}/s{si}l{li}.png", omit_background=True)
        await b.close()

def prep_bg(src, dst):
    """Cover-crop to 9:16, upscale to 1.25x output for the zoom, light sharpen."""
    from PIL import Image, ImageFilter, ImageEnhance
    im = Image.open(src).convert("RGB"); tw, th = int(W * 1.25), int(H * 1.25)
    s = max(tw / im.width, th / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - tw) // 2, (im.height - th) // 2
    im = im.crop((x, y, x + tw, y + th)).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    ImageEnhance.Contrast(im).enhance(1.05).save(dst, quality=95)

VOICE = os.environ.get("PIPER_VOICE", "en-us-ryan-high")
VOICE_DIR = os.path.expanduser("~/.cache/piper")

def ensure_voice():
    model = os.path.join(VOICE_DIR, f"{VOICE}.onnx")
    if not os.path.exists(model):
        os.makedirs(VOICE_DIR, exist_ok=True)
        tgz = os.path.join(VOICE_DIR, f"{VOICE}.tar.gz")
        subprocess.run(["curl", "-sSL", "-o", tgz, f"https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-{VOICE}.tar.gz"], check=True)
        subprocess.run(["tar", "xzf", tgz, "-C", VOICE_DIR], check=True)
    return model

def dur_of(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True, check=True).stdout)

tmp = tempfile.mkdtemp()
asyncio.run(shoot(tmp))

voice = d.get("voice")
if voice and not os.environ.get("FRAMES_ONLY"):
    model = ensure_voice()
    for si, line in enumerate(voice[:len(scenes)]):
        wav = f"{tmp}/vo{si}.wav"
        subprocess.run(["piper", "-m", model, "--length_scale", "0.92", "--sentence_silence", "0.15", "-f", wav],
                       input=line, text=True, check=True, capture_output=True)
        scenes[si]["vo"] = wav
        scenes[si]["dur"] = round(max(scenes[si]["dur"], 0.25 + dur_of(wav) + 0.35), 2)

if os.environ.get("FRAMES_ONLY"):
    from PIL import Image
    for si, sc in enumerate(scenes):
        if sc["bg"]:
            prep_bg(sc["bg"], f"{tmp}/bg{si}.jpg"); base = Image.open(f"{tmp}/bg{si}.jpg").resize((W, H)).convert("RGBA")
        else:
            base = Image.new("RGBA", (W, H), "white")
        for li in range(len(sc["layers"])):
            base.alpha_composite(Image.open(f"{tmp}/s{si}l{li}.png").convert("RGBA"))
        base.convert("RGB").save(f"{out}.s{si}.png")
    shutil.rmtree(tmp); sys.exit(0)

enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS)]
lst = []
for si, sc in enumerate(scenes):
    dur = sc["dur"]; n = round(dur * FPS)
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    if sc["bg"]:
        prep_bg(sc["bg"], f"{tmp}/bg{si}.jpg")
        args += ["-i", f"{tmp}/bg{si}.jpg"]
        zin = si % 2 == 0  # alternate zoom in / zoom out
        z = f"1+0.10*on/{n}" if zin else f"1.10-0.10*on/{n}"
        f = [f"[0:v]scale={W*2}:{H*2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},setsar=1,format=rgba[v0]"]
    else:
        args += ["-f", "lavfi", "-i", f"color=c=white:s={W}x{H}:r={FPS}:d={dur}"]
        f = ["[0:v]format=rgba[v0]"]
    cur = "v0"
    for li, (_, st) in enumerate(sc["layers"]):
        args += ["-framerate", str(FPS), "-loop", "1", "-t", str(dur), "-i", f"{tmp}/s{si}l{li}.png"]
        k = li + 1
        if st <= 0:
            f.append(f"[{k}:v]format=rgba[l{k}]")
            f.append(f"[{cur}][l{k}]overlay=0:0:shortest=1[v{k}]")
        else:
            f.append(f"[{k}:v]format=rgba,fade=t=in:st={st}:d=0.25:alpha=1[l{k}]")
            f.append(f"[{cur}][l{k}]overlay=x=0:y='if(lt(t,{st}),70,max(0,70-(t-{st})*280))':shortest=1[v{k}]")
        cur = f"v{k}"
    fin = "" if si == 0 else "fade=t=in:st=0:d=0.15:color=white,"
    f.append(f"[{cur}]{fin}trim=duration={dur},setpts=PTS-STARTPTS,format=yuv420p[out]")
    part, done = f"{tmp}/p{si}.tmp.mp4", f"{tmp}/p{si}.mp4"
    subprocess.run(args + ["-filter_complex", ";".join(f), "-map", "[out]", *enc, part], check=True)
    os.rename(part, done); lst.append(f"file '{done}'")

open(f"{tmp}/list.txt", "w").write("\n".join(lst))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", f"{tmp}/v.mp4"], check=True)
tmpout = out + ".tmp.mp4"
if all("vo" in sc for sc in scenes):
    # each scene's narration starts 0.25s in and is padded to the scene's length
    parts = []
    for si, sc in enumerate(scenes):
        a = f"{tmp}/a{si}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", sc["vo"], "-af",
                        f"aresample=44100,adelay=250|250,apad,atrim=0:{sc['dur']}", "-ac", "2", a], check=True)
        parts.append(f"file '{a}'")
    open(f"{tmp}/alist.txt", "w").write("\n".join(parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/alist.txt",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", f"{tmp}/vo.wav"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/v.mp4", "-i", f"{tmp}/vo.wav",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", tmpout], check=True)
else:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/v.mp4", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", tmpout], check=True)
os.rename(tmpout, out)
shutil.rmtree(tmp)
print(out, "photos:", photos)
