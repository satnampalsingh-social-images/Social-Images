"""Turn a feed post image into a branded 1080x1920 Story image (Instagram / Facebook Stories).
Usage: python3 tools/make_story.py posts/YYYY-MM-DD.jpg out.jpg ["TOP LINE"] ["BOTTOM LINE"]
Defaults: top "NEW POST", bottom "Tap the link in bio  ·  FindYourHouseInGTA.com".
Uses the official white Royal Canadian Realty logo; never recolour or stretch it.
"""
import sys, os, asyncio, tempfile, html
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FONTS = os.path.join(HERE, "fonts"); PF = f"{FONTS}/playfair-display-latin"; LA = f"{FONTS}/lato-latin"
src = os.path.abspath(sys.argv[1]); out = sys.argv[2]
top = html.escape(sys.argv[3] if len(sys.argv) > 3 else "NEW POST")
bot = html.escape(sys.argv[4] if len(sys.argv) > 4 else "Tap the link in bio  ·  FindYourHouseInGTA.com")
page = f"""<html><head><style>
@font-face{{font-family:PF;font-weight:900;src:url(file://{PF}-900-normal.woff2)}}
@font-face{{font-family:LA;font-weight:900;src:url(file://{LA}-900-normal.woff2)}}
@font-face{{font-family:LA;font-weight:700;src:url(file://{LA}-700-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:LA;color:#fff;
background:radial-gradient(circle at 50% 30%,#3a3a3a 0%,#252525 55%,#1a1a1a 100%);display:flex;flex-direction:column;align-items:center}}
.logo{{height:120px;margin-top:110px}}
.top{{margin-top:44px;background:#ED1C24;font-weight:900;letter-spacing:4px;font-size:30px;padding:14px 30px;border-radius:40px}}
.card{{margin:auto 0;width:940px;border-radius:22px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.55);border:4px solid #C79A3B}}
.card img{{display:block;width:100%}}
.bot{{margin-bottom:150px;text-align:center;font-weight:900;font-size:34px}}
.bot small{{display:block;margin-top:14px;font-weight:700;font-size:26px;color:#C79A3B;letter-spacing:1px}}
</style></head><body>
<img class="logo" src="file://{ROOT}/assets/brand/logo-white.png"><div class="top">{top}</div>
<div class="card"><img src="file://{src}"></div>
<div class="bot">{bot}<small>Satnampal Singh · 647-780-2560 · Royal Canadian Realty, Brokerage</small></div>
</body></html>"""
async def main():
    f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False); f.write(page); f.close()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox","--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width":1080,"height":1920})
        await pg.goto("file://" + f.name); await pg.evaluate("document.fonts.ready")
        png = out + ".png"; await pg.screenshot(path=png); await b.close()
    from PIL import Image
    Image.open(png).convert("RGB").save(out, quality=88, optimize=True); os.remove(png)
asyncio.run(main())
