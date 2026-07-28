# © @MuskanBot — OBSIDIAN VINYL Premium Thumbnail v4
#
# Concept: "Obsidian Vinyl Stage"
#   ┌─────────────────────────────────────────────────────────────────┐
#   │ CARD (deep obsidian, gradient gold border, corner L-accent)     │
#   │                                                                 │
#   │   ┌──────────────────────┐  ▶ NOW PLAYING                      │
#   │   │  VINYL DISC          │                                      │
#   │   │   (groove rings)     │  SONG TITLE                         │
#   │   │  ┌──────────┐        │  (large bold white)                 │
#   │   │  │ ALBUM ART│        │                                      │
#   │   │  │ (circle) │        │  Artist / Channel ──── (gold)       │
#   │   │  └──────────┘        │  ──────────── (gold divider)        │
#   │   │       ● (center dot) │  ████████░░░ (progress bar)         │
#   │   └──────────────────────┘   0:47              3:37            │
#   │                                                                 │
#   │  (vertical freq bars on card left edge, subtle)   ♪ MUSKAN  ↗  │
#   └─────────────────────────────────────────────────────────────────┘

import asyncio
import math
import os
import re
import time
from io import BytesIO
from typing import Optional, List, Tuple

from PIL import (
    Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
)

# ── Cache ─────────────────────────────────────────────────────────────
_CACHE_DIR = "/tmp/muskan_thumbs"
os.makedirs(_CACHE_DIR, exist_ok=True)

# ── Canvas ────────────────────────────────────────────────────────────
_W, _H = 1280, 720

# ── Palette ───────────────────────────────────────────────────────────
_BG       = (  6,   6,   9)
_CARD     = ( 16,  15,  22)
_CARD2    = ( 12,  11,  18)   # darker variant for depth
_VINYL    = ( 10,   9,  14)   # vinyl disc base
_GROOVE   = ( 28,  26,  36)   # vinyl groove ring color
_GOLD     = (212, 175,  55)
_GOLD_LT  = (255, 220, 100)
_GOLD_DIM = (140, 110,  25)
_AMBER    = (255, 158,  30)
_WHITE    = (255, 255, 255)
_SMOKE    = (210, 205, 222)
_DIM      = (120, 115, 138)
_STEEL    = ( 80,  78,  95)

# ── Card geometry ─────────────────────────────────────────────────────
_CX1, _CY1 = 50, 48       # card top-left
_CX2, _CY2 = _W - 50, _H - 48  # card bottom-right
_CRAD = 32                 # card corner radius

# ── Vinyl / art geometry ──────────────────────────────────────────────
_VCX  = 310                # vinyl center X
_VCY  = _H // 2 + 8       # vinyl center Y (slightly below center)
_VR   = 235                # vinyl outer radius
_AR   = 152                # album art circle radius

# ── Text zone ─────────────────────────────────────────────────────────
_TX   = 596                # text left edge
_TW   = _CX2 - _TX - 52   # text width

# ── Font paths (Heroku Ubuntu + common Linux) ─────────────────────────
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


# ═══════════════════════════════════════════════════════════════════════
#  LAYER HELPERS — always use alpha_composite to avoid banding
# ═══════════════════════════════════════════════════════════════════════

def _new_layer() -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _merge(base: Image.Image, layer: Image.Image) -> Image.Image:
    return Image.alpha_composite(base, layer)


# ═══════════════════════════════════════════════════════════════════════
#  STEP 1: BACKGROUND
# ═══════════════════════════════════════════════════════════════════════

def _make_bg(art: Optional[Image.Image]) -> Image.Image:
    canvas = Image.new("RGBA", (_W, _H), (*_BG, 255))

    if art:
        # Blurred art fill — very dark
        ow, oh = art.size
        ratio  = _W / _H
        if ow / oh > ratio:
            nw   = int(oh * ratio)
            crop = art.crop(((ow - nw) // 2, 0, (ow + nw) // 2, oh))
        else:
            nh   = int(ow / ratio)
            crop = art.crop((0, (oh - nh) // 2, ow, (oh + nh) // 2))
        blurred = (crop.resize((_W, _H), Image.LANCZOS)
                       .convert("RGBA")
                       .filter(ImageFilter.GaussianBlur(32)))
        blurred = ImageEnhance.Brightness(blurred).enhance(0.09)
        # Multiply alpha down
        r, g, b, a = blurred.split()
        a = a.point(lambda v: int(v * 0.65))
        blurred = Image.merge("RGBA", (r, g, b, a))
        canvas = Image.alpha_composite(canvas, blurred)

    # Subtle radial amber glow behind vinyl position
    glow, gd = _new_layer()
    for rad in range(420, 0, -5):
        frac = rad / 420
        a    = int(22 * (1 - frac) ** 2.8)
        rc   = int(_AMBER[0] * (1 - frac * 0.5))
        gc   = int(_AMBER[1] * (1 - frac * 0.82))
        bc   = int(8  * (1 - frac))
        gd.ellipse(
            [_VCX - rad, _VCY - rad, _VCX + rad, _VCY + rad],
            fill=(rc, gc, bc, a)
        )
    canvas = _merge(canvas, glow.filter(ImageFilter.GaussianBlur(18)))
    return canvas


# ═══════════════════════════════════════════════════════════════════════
#  STEP 2: CARD
# ═══════════════════════════════════════════════════════════════════════

def _draw_card(canvas: Image.Image) -> Image.Image:
    # Deep shadow
    for i in range(10, 0, -1):
        sh, sd = _new_layer()
        s      = i * 5
        a      = int(60 * (i / 10))
        sd.rounded_rectangle(
            [_CX1 - s, _CY1 - s, _CX2 + s, _CY2 + s],
            radius=_CRAD + s // 2,
            fill=(0, 0, 0, a),
        )
        canvas = _merge(canvas, sh.filter(ImageFilter.GaussianBlur(12)))

    # Card fill — solid dark
    fill_l, fd = _new_layer()
    fd.rounded_rectangle(
        [_CX1, _CY1, _CX2, _CY2],
        radius=_CRAD,
        fill=(*_CARD, 250),
    )
    canvas = _merge(canvas, fill_l)

    # Subtle top-left light sheen (very slight, like a light source from top-left)
    sheen, sd = _new_layer()
    for i in range(240):
        frac = 1 - i / 240
        a    = int(14 * frac ** 2.2)
        sd.line(
            [(_CX1 + _CRAD, _CY1 + i), (_CX1 + _CRAD + int(((_CX2 - _CX1) * 0.55) * (1 - i / 240)), _CY1 + i)],
            fill=(255, 255, 255, a)
        )
    canvas = _merge(canvas, sheen)

    # Gradient border: gold top+left edges → invisible bottom+right
    # Top edge
    border_top, bt = _new_layer()
    w_card = _CX2 - _CX1
    for x in range(w_card):
        frac = 1 - x / w_card
        a    = int(170 * frac ** 0.6)
        bt.line(
            [(_CX1 + x, _CY1), (_CX1 + x, _CY1 + 1)],
            fill=(*_GOLD, a)
        )
    canvas = _merge(canvas, border_top)

    # Left edge
    border_left, bl = _new_layer()
    h_card = _CY2 - _CY1
    for y in range(h_card):
        frac = 1 - y / h_card
        a    = int(150 * frac ** 0.7)
        bl.line(
            [(_CX1, _CY1 + y), (_CX1 + 1, _CY1 + y)],
            fill=(*_GOLD, a)
        )
    canvas = _merge(canvas, border_left)

    # Bottom + right — very faint steel
    border_br, bb = _new_layer()
    h_card = _CY2 - _CY1
    w_card = _CX2 - _CX1
    for y in range(h_card):
        frac = y / h_card
        a    = int(30 * frac ** 1.5)
        bb.line(
            [(_CX2 - 1, _CY1 + y), (_CX2, _CY1 + y)],
            fill=(*_STEEL, a)
        )
    for x in range(w_card):
        frac = x / w_card
        a    = int(25 * frac ** 1.5)
        bb.line(
            [(_CX1 + x, _CY2 - 1), (_CX1 + x, _CY2)],
            fill=(*_STEEL, a)
        )
    canvas = _merge(canvas, border_br)

    # Top-left corner L-accent (gold, 3 px wide, ~70px long)
    accent, ad = _new_layer()
    ad.rectangle([_CX1 + 2, _CY1 + 2, _CX1 + 70, _CY1 + 3],
                 fill=(*_GOLD, 230))
    ad.rectangle([_CX1 + 2, _CY1 + 2, _CX1 + 3, _CY1 + 50],
                 fill=(*_GOLD, 230))
    # Tiny highlight
    ad.rectangle([_CX1 + 2, _CY1 + 2, _CX1 + 70, _CY1 + 2],
                 fill=(*_GOLD_LT, 120))
    canvas = _merge(canvas, accent)

    # Bottom-right corner L-accent (dimmer)
    accent2, ad2 = _new_layer()
    ad2.rectangle([_CX2 - 70, _CY2 - 3, _CX2 - 2, _CY2 - 2],
                  fill=(*_GOLD_DIM, 100))
    ad2.rectangle([_CX2 - 3, _CY2 - 50, _CX2 - 2, _CY2 - 2],
                  fill=(*_GOLD_DIM, 100))
    canvas = _merge(canvas, accent2)

    return canvas


# ═══════════════════════════════════════════════════════════════════════
#  STEP 3: VINYL DISC + ALBUM ART
# ═══════════════════════════════════════════════════════════════════════

def _draw_vinyl(canvas: Image.Image,
                art: Optional[Image.Image]) -> Image.Image:
    # Outer glow (gold halo behind disc)
    glow, gd = _new_layer()
    for r in range(_VR + 40, _VR - 10, -2):
        frac = (r - (_VR - 10)) / 50
        a    = int(40 * frac ** 2)
        gd.ellipse(
            [_VCX - r, _VCY - r, _VCX + r, _VCY + r],
            outline=(*_GOLD, a), width=2
        )
    canvas = _merge(canvas, glow.filter(ImageFilter.GaussianBlur(8)))

    # Vinyl disc base
    disc, dd = _new_layer()
    dd.ellipse(
        [_VCX - _VR, _VCY - _VR, _VCX + _VR, _VCY + _VR],
        fill=(*_VINYL, 255)
    )

    # Groove rings — many thin concentric circles
    groove_step = 6
    r = _AR + 20
    while r < _VR - 4:
        dd.ellipse(
            [_VCX - r, _VCY - r, _VCX + r, _VCY + r],
            outline=(*_GROOVE, 255), width=1
        )
        r += groove_step

    # Highlight arc (top-left quarter, simulates light hitting vinyl)
    # Draw a thin white arc manually using line segments
    for angle_deg in range(210, 310):
        angle = math.radians(angle_deg)
        rx1   = int(_VCX + (_VR - 3) * math.cos(angle))
        ry1   = int(_VCY + (_VR - 3) * math.sin(angle))
        rx2   = int(_VCX + (_VR - 1) * math.cos(angle))
        ry2   = int(_VCY + (_VR - 1) * math.sin(angle))
        a     = int(55 * math.sin(math.radians(angle_deg - 210) * 1.8))
        if 0 <= a <= 255:
            dd.line([(rx1, ry1), (rx2, ry2)],
                    fill=(255, 255, 255, a), width=1)

    # Outer thin gold ring
    dd.ellipse(
        [_VCX - _VR, _VCY - _VR, _VCX + _VR, _VCY + _VR],
        outline=(*_GOLD, 120), width=2
    )
    canvas = _merge(canvas, disc)

    # Album art circle
    art_l, _ = _new_layer()
    if art:
        ow, oh = art.size
        side   = min(ow, oh)
        sq     = art.crop(((ow - side) // 2, (oh - side) // 2,
                            (ow + side) // 2, (oh + side) // 2))
        dim    = _AR * 2
        sq     = sq.resize((dim, dim), Image.LANCZOS).convert("RGBA")
        sq     = ImageEnhance.Brightness(sq).enhance(0.88)
        sq     = ImageEnhance.Color(sq).enhance(1.18)

        # Circular clip
        mask = Image.new("L", (dim, dim), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, dim, dim], fill=255)
        sq.putalpha(mask)
        art_l.alpha_composite(sq, dest=(_VCX - _AR, _VCY - _AR))
    else:
        ad = ImageDraw.Draw(art_l)
        ad.ellipse(
            [_VCX - _AR, _VCY - _AR, _VCX + _AR, _VCY + _AR],
            fill=(*_CARD2, 255)
        )
        ad.text((_VCX - 22, _VCY - 30), "♪",
                font=_font(58, bold=True), fill=(*_GOLD, 130))
    canvas = _merge(canvas, art_l)

    # Gold ring around art
    ring_l, rd = _new_layer()
    rd.ellipse(
        [_VCX - _AR - 1, _VCY - _AR - 1,
         _VCX + _AR + 1, _VCY + _AR + 1],
        outline=(*_GOLD, 200), width=3
    )
    canvas = _merge(canvas, ring_l)

    # Inner glow on art edge (soft warm light)
    iglow, ig = _new_layer()
    for i in range(12, 0, -1):
        a = int(28 * (i / 12) ** 2)
        ig.ellipse(
            [_VCX - _AR + i, _VCY - _AR + i,
             _VCX + _AR - i, _VCY + _AR - i],
            outline=(*_AMBER, a), width=2
        )
    canvas = _merge(canvas, iglow.filter(ImageFilter.GaussianBlur(3)))

    # Center spindle hole
    center_l, cd = _new_layer()
    cd.ellipse([_VCX - 16, _VCY - 16, _VCX + 16, _VCY + 16],
               fill=(*_CARD2, 255))
    cd.ellipse([_VCX - 7,  _VCY - 7,  _VCX + 7,  _VCY + 7],
               fill=(*_GOLD, 200))
    cd.ellipse([_VCX - 3,  _VCY - 3,  _VCX + 3,  _VCY + 3],
               fill=(*_GOLD_LT, 240))
    canvas = _merge(canvas, center_l)

    # Thin vertical separator line between vinyl section and text
    sep, sd = _new_layer()
    sep_x   = _TX - 28
    for y in range(_CY1 + 60, _CY2 - 60):
        frac = 1 - abs(y - _H / 2) / (_H / 2 - 60)
        a    = int(55 * frac ** 1.5)
        sd.point((sep_x, y), fill=(*_GOLD, a))
    canvas = _merge(canvas, sep)

    return canvas


# ═══════════════════════════════════════════════════════════════════════
#  STEP 4: PROGRESS BAR
# ═══════════════════════════════════════════════════════════════════════

def _draw_progress(
    canvas: Image.Image,
    draw:   ImageDraw.ImageDraw,
    x: int, y: int, w: int,
    duration: str, seed: int,
) -> Tuple[int, int]:
    """Draws progress bar; returns (elapsed_str, total_str)."""
    try:
        parts   = [p for p in re.split(r"[:\s]", duration) if p.isdigit()]
        total_s = int(parts[-2]) * 60 + int(parts[-1]) if len(parts) >= 2 else int(parts[0]) if parts else 210
    except Exception:
        total_s = 210

    progress  = 0.26 + (seed % 100) / 190.0
    elapsed_s = int(total_s * progress)
    filled    = int(w * progress)

    bar_h = 4
    bar_r = 2

    # Track
    track, td = _new_layer()
    ImageDraw.Draw(track).rounded_rectangle(
        [x, y, x + w, y + bar_h],
        radius=bar_r, fill=(50, 46, 62, 255)
    )
    canvas = _merge(canvas, track)

    # Filled — gold with brightness gradient (brighter on right tip)
    if filled > bar_r * 2:
        fill_l, fl = _new_layer()
        fl.rounded_rectangle(
            [x, y, x + filled, y + bar_h],
            radius=bar_r, fill=(*_GOLD, 250)
        )
        # Bright highlight line on top of fill
        if filled > 10:
            fl.rounded_rectangle(
                [x + 2, y, x + filled - 2, y + 1],
                radius=1, fill=(*_GOLD_LT, 160)
            )
        canvas = _merge(canvas, fill_l)

    # Playhead
    ph_x = x + filled
    ph_r = 8
    ph_l, pd = _new_layer()
    pd.ellipse(
        [ph_x - ph_r, y - ph_r + bar_h // 2,
         ph_x + ph_r, y + ph_r + bar_h // 2],
        fill=(*_WHITE, 255)
    )
    # Gold core
    pd.ellipse(
        [ph_x - 4, y - 4 + bar_h // 2,
         ph_x + 4, y + 4 + bar_h // 2],
        fill=(*_GOLD, 255)
    )
    canvas = _merge(canvas, ph_l)
    draw   = ImageDraw.Draw(canvas)   # refresh

    el_str  = f"{elapsed_s // 60}:{elapsed_s % 60:02d}"
    tot_str = duration or "0:00"
    return el_str, tot_str


# ═══════════════════════════════════════════════════════════════════════
#  STEP 5: TITLE WRAP
# ═══════════════════════════════════════════════════════════════════════

def _wrap_title(
    draw: ImageDraw.ImageDraw, text: str, max_w: int
) -> List[Tuple[str, object]]:
    for sz in [62, 52, 42, 34]:
        fnt   = _font(sz, bold=True)
        words = text.split()
        lines: List[str] = []
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
        if len(lines) <= 2 and all(_tw(draw, l, fnt) <= max_w for l in lines):
            return [(l, fnt) for l in lines[:2]]
    fnt = _font(32, bold=True)
    return [(text[:30] + ("…" if len(text) > 30 else ""), fnt)]


# ═══════════════════════════════════════════════════════════════════════
#  NETWORK
# ═══════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════
#  MAIN COMPOSER
# ═══════════════════════════════════════════════════════════════════════

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

    title    = _strip(title)   or yt_title
    duration = duration        or yt_dur
    channel  = _strip(channel) or "YouTube"
    seed     = sum(ord(c) for c in videoid) % 9999

    # ── Compose layers ────────────────────────────────────────────────
    canvas = _make_bg(art)
    canvas = _draw_card(canvas)
    canvas = _draw_vinyl(canvas, art)

    draw   = ImageDraw.Draw(canvas)

    # ── TEXT ZONE ─────────────────────────────────────────────────────
    TY = _CY1 + 68

    # ── NOW PLAYING badge ─────────────────────────────────────────────
    f_np    = _font(14, bold=True)
    np_text = "N O W   P L A Y I N G"
    # Amber pulse dot
    draw.ellipse([_TX, TY + 4, _TX + 9, TY + 13],
                 fill=(*_AMBER, 255))
    draw.ellipse([_TX - 3, TY + 1, _TX + 12, TY + 16],
                 outline=(*_AMBER, 60), width=1)
    # Text
    draw.text((_TX + 18, TY + 1), np_text, font=f_np, fill=(*_GOLD, 210))
    TY += 32

    # ── Song title ────────────────────────────────────────────────────
    title_lines = _wrap_title(draw, title, _TW)
    for i, (line, fnt) in enumerate(title_lines):
        # Soft shadow
        draw.text((_TX + 2, TY + 3), line, font=fnt, fill=(0, 0, 0, 90))
        # White text
        draw.text((_TX, TY), line, font=fnt, fill=(*_WHITE, 255))
        TY += _th(draw, line, fnt) + (8 if i < len(title_lines) - 1 else 0)
    TY += 22

    # ── Channel / artist ──────────────────────────────────────────────
    f_ch    = _font(26, bold=False)
    ch_disp = channel[:40]
    draw.text((_TX + 1, TY + 1), ch_disp, font=f_ch, fill=(0, 0, 0, 60))
    draw.text((_TX, TY), ch_disp, font=f_ch, fill=(*_SMOKE, 215))
    TY += _th(draw, ch_disp, f_ch) + 24

    # ── Gold divider (with fade) ───────────────────────────────────────
    div_len = _TW - 10
    div_l, dd = _new_layer()
    for x in range(div_len):
        frac = 1 - (x / div_len) ** 0.6
        a    = int(160 * frac)
        dd.point((_TX + x, TY), fill=(*_GOLD, a))
    canvas = _merge(canvas, div_l)
    # Highlight flare at start
    div_l2, dd2 = _new_layer()
    dd2.point((_TX, TY), fill=(*_GOLD_LT, 220))
    dd2.point((_TX + 1, TY), fill=(*_GOLD_LT, 140))
    canvas = _merge(canvas, div_l2)
    draw   = ImageDraw.Draw(canvas)
    TY += 22

    # ── Progress bar ──────────────────────────────────────────────────
    bar_w  = _TW - 12
    el_str, tot_str = _draw_progress(canvas, draw, _TX, TY, bar_w,
                                     duration, seed)
    draw   = ImageDraw.Draw(canvas)
    TY += 22

    # Time labels
    f_time = _font(20, bold=False)
    draw.text((_TX, TY), el_str, font=f_time, fill=(*_DIM, 200))
    tw_str = _tw(draw, tot_str, f_time)
    draw.text((_TX + bar_w - tw_str, TY), tot_str,
              font=f_time, fill=(*_DIM, 200))
    TY += _th(draw, el_str, f_time) + 26

    # ── Requester (optional) ──────────────────────────────────────────
    req = _strip(requester)
    if req:
        f_req = _font(20, bold=False)
        req_t = f"Requested by  {req[:24]}"
        draw.text((_TX, TY), req_t, font=f_req, fill=(*_STEEL, 200))
        TY += _th(draw, req_t, f_req) + 16

    # ── BRAND — bottom-right corner of card ───────────────────────────
    brand   = "♪  MUSKAN MUSIC"
    f_brand = _font(18, bold=True)
    bw      = _tw(draw, brand, f_brand)
    bx      = _CX2 - bw - 28
    by      = _CY2 - 46

    # Subtle pill behind brand
    bp_l, bp = _new_layer()
    bp.rounded_rectangle(
        [bx - 10, by - 4, bx + bw + 10, by + _th(draw, brand, f_brand) + 4],
        radius=8, fill=(*_CARD2, 140)
    )
    canvas = _merge(canvas, bp_l)
    draw   = ImageDraw.Draw(canvas)

    draw.text((bx + 1, by + 1), brand, font=f_brand, fill=(0, 0, 0, 80))
    draw.text((bx, by), brand, font=f_brand, fill=(*_GOLD, 195))

    # ── Frequency bars — left edge of card (subtle decoration) ────────
    bars_l, bd = _new_layer()
    bar_x      = _CX1 + 18
    bar_base   = _VCY + _VR - 10
    n_bars     = 16
    for i in range(n_bars):
        wave = math.sin(i * 0.55) * 0.5 + 0.5
        bh   = int(12 + wave * 38)
        frac = 1 - abs(i / n_bars - 0.5) * 2
        a    = int(50 + 60 * frac)
        bby  = bar_base - bh
        bbx  = bar_x + i * 8
        bd.rounded_rectangle(
            [bbx, bby, bbx + 4, bar_base],
            radius=2, fill=(*_GOLD, a)
        )
    canvas = _merge(canvas, bars_l)

    # ── Save ──────────────────────────────────────────────────────────
    canvas.convert("RGB").save(out, "JPEG", quality=97, optimize=True)
    return out
