# © @MuskanBot — Ultra Premium Vinyl Split Thumbnail v5
#
# Concept: "Ultra Premium Vinyl Split"
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │  LEFT HALF: Full album art (vivid) fading into dark                 │
#   │    └── Floating VINYL DISC with album art in center, gold rings     │
#   │  RIGHT HALF: Dark glass card                                        │
#   │    ▶ NOW PLAYING badge  (gold dot)                                  │
#   │    Song Title (large bold white)                                    │
#   │    Channel / Artist  (smoke)                                        │
#   │    Views                                                            │
#   │    ──── gold divider (fading)                                       │
#   │    ████████░░░ progress bar  0:00 ── total                          │
#   │    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  eq bars (gold)                            │
#   │    ♪  MUSKAN MUSIC  (brand pill, bottom-right)                      │
#   └──────────────────────────────────────────────────────────────────────┘

import asyncio
import math
import os
import re
import time
from io import BytesIO
from typing import Optional, Tuple

from PIL import (
    Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
)

# ── Cache ──────────────────────────────────────────────────────────────────────
_CACHE_DIR = "/tmp/muskan_thumbs"
os.makedirs(_CACHE_DIR, exist_ok=True)

# ── Canvas ─────────────────────────────────────────────────────────────────────
_W, _H = 1280, 720

# ── Palette ────────────────────────────────────────────────────────────────────
_BG      = (  5,   3,  12)
_CARD    = ( 12,   8,  24)
_CARD2   = (  7,   5,  17)
_VINYL   = (  7,   5,  17)
_GROOVE  = ( 40,  35,  60)
_GOLD    = (212, 175,  55)
_GOLD_LT = (255, 235, 120)
_GOLD_DM = (150, 120,  35)
_AMBER   = (255, 180,  50)
_WHITE   = (255, 255, 255)
_SMOKE   = (198, 192, 220)
_DIM     = (155, 150, 180)
_STEEL   = (100,  90, 140)

# ── Vinyl geometry ─────────────────────────────────────────────────────────────
_VCX = 325
_VCY = 362
_VR  = 255
_AR  = 154

# ── Text zone ──────────────────────────────────────────────────────────────────
_TX    = 682
_BAR_W = 540

# ── Font paths ─────────────────────────────────────────────────────────────────
_BOLD_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]
_REG_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]
_font_cache: dict = {}


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    for p in (_BOLD_FONTS if bold else _REG_FONTS):
        if os.path.isfile(p):
            try:
                f = ImageFont.truetype(p, size)
                _font_cache[key] = f
                return f
            except Exception:
                continue
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f


def _strip(t: str) -> str:
    return re.sub(r"<[^>]+>", "", t or "").strip()


def _tw(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(text) * max(getattr(font, 'size', 10) // 2, 6)


def _th(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]
    except Exception:
        return max(getattr(font, 'size', 20), 12)


# ═══════════════════════════════════════════════════════════════════════════════
#  LAYER HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _new_layer() -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _merge(base: Image.Image, layer: Image.Image) -> Image.Image:
    return Image.alpha_composite(base, layer)


def _sq_crop(img: Image.Image) -> Image.Image:
    w, h = img.size
    s = min(w, h)
    return img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))


def _circle_img(img: Image.Image, size: int) -> Image.Image:
    img = img.resize((size, size), Image.LANCZOS).convert("RGBA")
    m   = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size, size], fill=255)
    img.putalpha(m)
    return img


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — BACKGROUND (blurred art + dark overlay)
# ═══════════════════════════════════════════════════════════════════════════════

def _make_bg(art: Optional[Image.Image]) -> Image.Image:
    canvas = Image.new("RGBA", (_W, _H), (*_BG, 255))
    if art:
        bg2 = art.resize((_W, _H), Image.LANCZOS).convert("RGBA")
        bg2 = ImageEnhance.Brightness(bg2).enhance(0.28)
        bg2 = bg2.filter(ImageFilter.GaussianBlur(50))
        canvas = Image.alpha_composite(canvas, bg2)
    dark, dd = _new_layer()
    dd.rectangle([0, 0, _W, _H], fill=(5, 3, 12, 208))
    canvas = _merge(canvas, dark)
    return canvas


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — LEFT ART PANEL with fade
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_left_panel(canvas: Image.Image, art: Optional[Image.Image]) -> Image.Image:
    if not art:
        return canvas
    left = art.resize((660, _H), Image.LANCZOS).convert("RGBA")
    canvas.alpha_composite(left, (0, 0))
    fade, fd = _new_layer()
    for x in range(660):
        a = int(255 * (x / 660) ** 1.2)
        fd.line([(x, 0), (x, _H)], fill=(5, 3, 12, a))
    return _merge(canvas, fade)


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — VINYL DISC (floating over left art)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_vinyl(canvas: Image.Image, art: Optional[Image.Image]) -> Image.Image:
    # Vinyl drop shadow
    glow, _ = _new_layer()
    for r in range(_VR + 40, _VR - 12, -3):
        frac = (r - (_VR - 12)) / 52
        a    = int(22 * frac ** 2)
        ImageDraw.Draw(glow).ellipse(
            [_VCX - r, _VCY - r, _VCX + r, _VCY + r], fill=(0, 0, 0, a)
        )
    canvas = _merge(canvas, glow.filter(ImageFilter.GaussianBlur(28)))

    # Disc base + grooves
    disc, dd = _new_layer()
    dd.ellipse([_VCX - _VR, _VCY - _VR, _VCX + _VR, _VCY + _VR], fill=(*_VINYL, 248))
    for r in range(_VR - 10, 115, -7):
        dd.ellipse([_VCX - r, _VCY - r, _VCX + r, _VCY + r],
                   outline=(*_GROOVE, 195), width=1)
    # Highlight arc (top-left)
    for deg in range(208, 312):
        ang  = math.radians(deg)
        x1   = int(_VCX + (_VR - 4) * math.cos(ang))
        y1   = int(_VCY + (_VR - 4) * math.sin(ang))
        x2   = int(_VCX + (_VR - 1) * math.cos(ang))
        y2   = int(_VCY + (_VR - 1) * math.sin(ang))
        a    = int(62 * math.sin(math.radians((deg - 208) * 1.8)))
        if 0 < a < 256:
            dd.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, a), width=1)
    dd.ellipse([_VCX - _VR, _VCY - _VR, _VCX + _VR, _VCY + _VR],
               outline=(*_GOLD, 90), width=2)
    canvas = _merge(canvas, disc)

    # Art circle in vinyl center
    if art:
        ar_sq = _sq_crop(art)
        ac    = _circle_img(ar_sq, _AR * 2)
        # Warm glow behind art
        aglow, _ = _new_layer()
        for r2 in range(_AR + 20, _AR - 5, -3):
            frac = (r2 - (_AR - 5)) / 25
            a    = int(28 * frac ** 2)
            ImageDraw.Draw(aglow).ellipse(
                [_VCX - r2, _VCY - r2, _VCX + r2, _VCY + r2], fill=(*_AMBER, a)
            )
        canvas = _merge(canvas, aglow.filter(ImageFilter.GaussianBlur(5)))
        canvas.alpha_composite(ac, (_VCX - _AR, _VCY - _AR))
    else:
        al2, ad = _new_layer()
        ad.ellipse([_VCX - _AR, _VCY - _AR, _VCX + _AR, _VCY + _AR],
                   fill=(*_CARD2, 255))
        ad.text((_VCX - 22, _VCY - 30), "♪",
                font=_font(58, bold=True), fill=(*_GOLD, 130))
        canvas = _merge(canvas, al2)

    # Gold ring + outer shimmer
    rl, rd = _new_layer()
    rd.ellipse([_VCX - _AR - 2, _VCY - _AR - 2, _VCX + _AR + 2, _VCY + _AR + 2],
               outline=(*_GOLD, 235), width=3)
    rd.ellipse([_VCX - _AR - 8, _VCY - _AR - 8, _VCX + _AR + 8, _VCY + _AR + 8],
               outline=(*_GOLD, 60), width=2)
    canvas = _merge(canvas, rl)

    # Spindle
    sl, sd = _new_layer()
    sd.ellipse([_VCX - 14, _VCY - 14, _VCX + 14, _VCY + 14], fill=(*_CARD2, 255))
    sd.ellipse([_VCX - 7,  _VCY - 7,  _VCX + 7,  _VCY + 7],  fill=(*_GOLD, 228))
    sd.ellipse([_VCX - 3,  _VCY - 3,  _VCX + 3,  _VCY + 3],  fill=(*_GOLD_LT, 248))
    canvas = _merge(canvas, sl)

    return canvas


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — RIGHT GLASS CARD
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_card(canvas: Image.Image) -> Image.Image:
    # Outer gold card glow
    glow, gd = _new_layer()
    for i in range(12, 0, -1):
        a = int(18 * (i / 12) ** 2)
        gd.rounded_rectangle(
            [642 - i, 72 - i, 1234 + i, 648 + i],
            radius=32 + i // 2, fill=(*_GOLD, a)
        )
    canvas = _merge(canvas, glow.filter(ImageFilter.GaussianBlur(6)))

    # Card fill
    cl, cd = _new_layer()
    cd.rounded_rectangle([645, 75, 1232, 645], radius=32, fill=(*_CARD, 228))

    # Gold border top + left (fading)
    for i in range(587):
        a = int(200 * (1 - i / 587) ** 0.55)
        cd.point((645 + i, 75), fill=(*_GOLD, a))
    for i in range(570):
        a = int(180 * (1 - i / 570) ** 0.6)
        cd.point((645, 75 + i), fill=(*_GOLD, a))
    # Faint steel bottom + right
    for i in range(587):
        a = int(28 * (i / 587) ** 1.5)
        cd.point((645 + i, 645), fill=(*_STEEL, a))
    for i in range(570):
        a = int(22 * (i / 570) ** 1.5)
        cd.point((1232, 75 + i), fill=(*_STEEL, a))
    canvas = _merge(canvas, cl)

    # Top sheen
    sheen, sd = _new_layer()
    for i in range(220):
        frac = 1 - i / 220
        a    = int(12 * frac ** 2.2)
        sd.line(
            [(648, 78 + i), (648 + int(580 * (1 - i / 220)), 78 + i)],
            fill=(255, 255, 255, a)
        )
    canvas = _merge(canvas, sheen)

    # Corner L-accents
    acc, ad = _new_layer()
    ad.rectangle([645, 75, 720, 78],  fill=(*_GOLD, 210))
    ad.rectangle([645, 75, 648, 140], fill=(*_GOLD, 210))
    ad.rectangle([645, 75, 722, 76],  fill=(*_GOLD_LT, 120))
    ad.rectangle([1162, 642, 1232, 645], fill=(*_GOLD_DM, 100))
    ad.rectangle([1229, 580, 1232, 645], fill=(*_GOLD_DM, 100))
    canvas = _merge(canvas, acc)

    return canvas


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 5 — PROGRESS BAR
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_progress(
    canvas: Image.Image, draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, duration: str, seed: int,
) -> Tuple[str, str]:
    try:
        parts   = [p for p in re.split(r"[:\s]", duration) if p.isdigit()]
        total_s = int(parts[-2]) * 60 + int(parts[-1]) if len(parts) >= 2 else int(parts[0]) if parts else 210
    except Exception:
        total_s = 210

    progress  = 0.26 + (seed % 100) / 190.0
    elapsed_s = int(total_s * progress)
    filled    = int(w * progress)
    bar_h, bar_r = 8, 4

    # Track
    track, td = _new_layer()
    ImageDraw.Draw(track).rounded_rectangle(
        [x, y, x + w, y + bar_h], radius=bar_r, fill=(48, 40, 68, 200)
    )
    canvas = _merge(canvas, track)

    # Fill (gold)
    if filled > bar_r * 2:
        fill_l, fl = _new_layer()
        fl.rounded_rectangle([x, y, x + filled, y + bar_h],
                              radius=bar_r, fill=(*_GOLD, 252))
        if filled > 10:
            fl.rounded_rectangle([x + 2, y, x + filled - 2, y + 1],
                                  radius=1, fill=(*_GOLD_LT, 160))
        canvas = _merge(canvas, fill_l)

    # Playhead
    ph_x = x + filled
    ph, pd = _new_layer()
    pd.ellipse([ph_x - 11, y - 7,  ph_x + 11, y + bar_h + 7], fill=(*_WHITE, 255))
    pd.ellipse([ph_x - 5,  y - 1,  ph_x + 5,  y + bar_h + 1], fill=(*_GOLD, 255))
    canvas = _merge(canvas, ph)
    draw   = ImageDraw.Draw(canvas)

    el_str  = f"{elapsed_s // 60}:{elapsed_s % 60:02d}"
    tot_str = duration or "0:00"
    return el_str, tot_str


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 6 — TITLE WRAP
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap_title(draw: ImageDraw.ImageDraw, text: str, max_w: int):
    for sz in [68, 56, 46, 36]:
        fnt   = _font(sz, bold=True)
        words = text.split()
        lines = []
        cur   = ""
        for w in words:
            test = (cur + " " + w).strip()
            if _tw(draw, test, fnt) <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) <= 2 and all(_tw(draw, ln, fnt) <= max_w for ln in lines):
            return [(ln, fnt) for ln in lines[:2]]
    fnt = _font(34, bold=True)
    return [(text[:30] + ("…" if len(text) > 30 else ""), fnt)]


# ═══════════════════════════════════════════════════════════════════════════════
#  NETWORK HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

async def _fetch_thumbnail(videoid: str) -> Optional[Image.Image]:
    try:
        import aiohttp
        for url in [
            f"https://i.ytimg.com/vi/{videoid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/mqdefault.jpg",
        ]:
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                        if r.status == 200:
                            data = await r.read()
                            img  = Image.open(BytesIO(data)).convert("RGBA")
                            if img.size[0] >= 200:
                                return img
            except Exception:
                continue
    except Exception:
        pass
    return None


async def _fetch_video_info(videoid: str):
    try:
        from py_yt import VideosSearch
        res     = await VideosSearch(f"https://youtu.be/{videoid}", limit=1).next()
        item    = res["result"][0]
        title   = _strip(item.get("title", "")) or "Unknown Title"
        dur     = item.get("duration", "") or "0:00"
        ch_raw  = item.get("channel", {})
        channel = ch_raw.get("name", "YouTube") if isinstance(ch_raw, dict) else "YouTube"
        return title, dur, channel
    except Exception:
        return "Unknown Title", "0:00", "YouTube"


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN COMPOSER
# ═══════════════════════════════════════════════════════════════════════════════

async def get_thumb(
    videoid:   str,
    title:     str = "",
    duration:  str = "",
    requester: str = "",
) -> str:
    out = os.path.join(_CACHE_DIR, f"{videoid}.jpg")
    if os.path.exists(out) and time.time() - os.path.getmtime(out) < 600:
        return out

    (yt_title, yt_dur, channel), art = await asyncio.gather(
        _fetch_video_info(videoid),
        _fetch_thumbnail(videoid),
    )

    title    = _strip(title)  or yt_title
    duration = duration       or yt_dur
    channel  = _strip(channel) or "YouTube"
    seed     = sum(ord(c) for c in videoid) % 9999

    # ── Compose ───────────────────────────────────────────────────────────────
    canvas = _make_bg(art)
    canvas = _draw_left_panel(canvas, art)
    canvas = _draw_vinyl(canvas, art)
    canvas = _draw_card(canvas)

    draw = ImageDraw.Draw(canvas)

    # ── NOW PLAYING badge ──────────────────────────────────────────────────────
    f_np    = _font(16, bold=True)
    np_text = "N O W   P L A Y I N G"
    draw.ellipse([_TX, 138, _TX + 10, 148],       fill=(*_GOLD, 255))
    draw.ellipse([_TX - 3, 134, _TX + 13, 152],   outline=(*_GOLD, 80), width=1)
    draw.text((_TX + 18, 135), np_text, font=f_np, fill=(*_GOLD, 220))

    # ── Song title ────────────────────────────────────────────────────────────
    title_lines = _wrap_title(draw, title, _BAR_W)
    TY = 163
    for i, (line, fnt_) in enumerate(title_lines):
        draw.text((_TX + 2, TY + 2), line, font=fnt_, fill=(0, 0, 0, 100))
        draw.text((_TX, TY),         line, font=fnt_, fill=(*_WHITE, 255))
        TY += _th(draw, line, fnt_) + (8 if i < len(title_lines) - 1 else 0)
    TY += 18

    # ── Channel ───────────────────────────────────────────────────────────────
    f_ch = _font(26, bold=False)
    draw.text((_TX + 1, TY + 1), channel[:40], font=f_ch, fill=(0, 0, 0, 55))
    draw.text((_TX, TY),         channel[:40], font=f_ch, fill=(*_SMOKE, 220))
    TY += _th(draw, channel, f_ch) + 12

    # Views (optional — only if passed)
    draw.text((_TX, TY), "🎵 YouTube", font=_font(20, bold=False), fill=(*_DIM, 190))
    TY += 32

    # ── Gold separator ─────────────────────────────────────────────────────────
    sep, sd = _new_layer()
    for x in range(_BAR_W):
        frac = 1 - (x / _BAR_W) ** 0.6
        ImageDraw.Draw(sep).point((_TX + x, TY), fill=(*_GOLD, int(165 * frac)))
    ImageDraw.Draw(sep).point((_TX,     TY), fill=(*_GOLD_LT, 255))
    ImageDraw.Draw(sep).point((_TX + 1, TY), fill=(*_GOLD_LT, 180))
    canvas = _merge(canvas, sep)
    draw   = ImageDraw.Draw(canvas)
    TY += 18

    # ── Progress bar ──────────────────────────────────────────────────────────
    el_str, tot_str = _draw_progress(canvas, draw, _TX, TY, _BAR_W, duration, seed)
    draw = ImageDraw.Draw(canvas)
    TY  += 20

    f_time = _font(22, bold=False)
    draw.text((_TX, TY), el_str, font=f_time, fill=(*_DIM, 210))
    tw_str = _tw(draw, tot_str, f_time)
    draw.text((_TX + _BAR_W - tw_str, TY), tot_str, font=f_time, fill=(*_DIM, 210))
    TY += _th(draw, el_str, f_time) + 22

    # ── Requester ─────────────────────────────────────────────────────────────
    req = _strip(requester)
    if req:
        f_req = _font(20, bold=False)
        req_t = f"Requested by  {req[:24]}"
        draw.text((_TX, TY), req_t, font=f_req, fill=(*_STEEL, 205))
        TY += _th(draw, req_t, f_req) + 14

    # ── Equalizer bars (gold) ─────────────────────────────────────────────────
    eq_l, ed = _new_layer()
    for i in range(20):
        bh  = int(12 + math.sin(i * 0.55) * 0.5 * 40 + 20)
        a   = int(120 + 90 * (1 - abs(i / 20 - 0.5) * 2))
        ed.rounded_rectangle(
            [_TX + i * 26, 445 - bh, _TX + i * 26 + 17, 445],
            radius=3, fill=(*_GOLD, min(255, a))
        )
    canvas = _merge(canvas, eq_l)

    # ── Brand pill (bottom-right of card) ─────────────────────────────────────
    brand   = "♪  DOLBY MUSIC"
    f_brand = _font(22, bold=True)
    draw    = ImageDraw.Draw(canvas)
    bw      = _tw(draw, brand, f_brand)
    bx1, by1, bx2, by2 = 1222 - bw - 22, 600, 1222, 630

    pill, pd = _new_layer()
    ImageDraw.Draw(pill).rounded_rectangle(
        [bx1, by1, bx2, by2], radius=12, fill=(*_CARD2, 180)
    )
    canvas = _merge(canvas, pill)
    draw   = ImageDraw.Draw(canvas)
    draw.text((bx1 + 1, by1 + 6), brand, font=f_brand, fill=(0, 0, 0, 80))
    draw.text((bx1,     by1 + 5), brand, font=f_brand, fill=(*_GOLD, 220))

    # ── Save ──────────────────────────────────────────────────────────────────
    canvas.convert("RGB").save(out, "JPEG", quality=97, optimize=True)
    return out
