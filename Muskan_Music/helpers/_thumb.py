# © @MuskanBot — Premium Music Player Card Thumbnail v3
# Style: Frosted dark card, circular album art, progress bar, gold accents

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

# ── Cache ──────────────────────────────────────────────────────────────
_CACHE_DIR = "/tmp/muskan_thumbs"
os.makedirs(_CACHE_DIR, exist_ok=True)

# ── Canvas ─────────────────────────────────────────────────────────────
_W, _H = 1280, 720

# ── Palette ────────────────────────────────────────────────────────────
_BLACK    = (  8,   8,  10)
_CARD_BG  = ( 22,  22,  30)
_CARD_BG2 = ( 16,  16,  22)
_GOLD     = (212, 175,  55)
_GOLD_LT  = (255, 220, 100)
_AMBER    = (255, 165,  40)
_WHITE    = (255, 255, 255)
_SMOKE    = (210, 205, 220)
_DIM      = (130, 125, 145)
_BAR_BG   = ( 45,  40,  55)
_BAR_FILL = (212, 175,  55)

# ── Font Paths (in priority order, covers Heroku Ubuntu + local dev) ───
_BOLD_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
]
_REG_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]

_font_cache: dict = {}

def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    paths = _BOLD_FONTS if bold else _REG_FONTS
    for p in paths:
        if os.path.isfile(p):
            try:
                f = ImageFont.truetype(p, size)
                _font_cache[key] = f
                return f
            except Exception:
                continue
    # last resort: default bitmap font
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
        return len(text) * (getattr(font, 'size', 10) // 2)


def _th(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]
    except Exception:
        return getattr(font, 'size', 20)


# ═══════════════════════════════════════════════════════════════════════
#  BACKGROUND — dark blurred art
# ═══════════════════════════════════════════════════════════════════════

def _make_bg(art: Optional[Image.Image]) -> Image.Image:
    bg = Image.new("RGBA", (_W, _H), (*_BLACK, 255))

    if art:
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
                       .filter(ImageFilter.GaussianBlur(28)))
        blurred = ImageEnhance.Brightness(blurred).enhance(0.18)
        blurred.putalpha(180)
        bg = Image.alpha_composite(bg, blurred)

    # Dark gradient overlay (top darker, bottom slightly lighter)
    grad = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(_H):
        a = int(90 * (1 - y / _H))
        gd.line([(0, y), (_W, y)], fill=(0, 0, 0, a))
    bg = Image.alpha_composite(bg, grad)
    return bg


# ═══════════════════════════════════════════════════════════════════════
#  CARD — frosted dark rounded rectangle
# ═══════════════════════════════════════════════════════════════════════

def _draw_card(canvas: Image.Image) -> Image.Image:
    pad_x, pad_y = 64, 56
    r = 36

    card = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    cd   = ImageDraw.Draw(card)

    # Shadow layers (multiple blurred rects)
    for i in range(8, 0, -1):
        s = i * 6
        a = int(80 * (i / 8))
        cd.rounded_rectangle(
            [pad_x - s, pad_y - s, _W - pad_x + s, _H - pad_y + s],
            radius=r + s // 2,
            fill=(0, 0, 0, a),
        )
    shadow = card.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.alpha_composite(canvas, shadow)

    # Card fill (two-tone gradient via two overlapping rects)
    card2 = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    cd2   = ImageDraw.Draw(card2)
    cd2.rounded_rectangle(
        [pad_x, pad_y, _W - pad_x, _H - pad_y],
        radius=r,
        fill=(*_CARD_BG, 245),
    )
    # Subtle lighter top half
    top_h = (_H - 2 * pad_y) // 2
    for i in range(top_h):
        frac = 1 - i / top_h
        a    = int(18 * frac)
        cd2.line(
            [(pad_x + r, pad_y + i), (_W - pad_x - r, pad_y + i)],
            fill=(255, 255, 255, a)
        )
    canvas = Image.alpha_composite(canvas, card2)

    # Card border (gold glow, 1px)
    border_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    bd            = ImageDraw.Draw(border_layer)
    bd.rounded_rectangle(
        [pad_x, pad_y, _W - pad_x, _H - pad_y],
        radius=r,
        outline=(*_GOLD, 80),
        width=1,
    )
    canvas = Image.alpha_composite(canvas, border_layer)

    return canvas


# ═══════════════════════════════════════════════════════════════════════
#  CIRCULAR ALBUM ART
# ═══════════════════════════════════════════════════════════════════════

def _place_circular_art(canvas: Image.Image,
                         art: Optional[Image.Image]) -> Image.Image:
    cx, cy = 350, _H // 2   # center of the circle
    R      = 218             # outer radius

    layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    ld    = ImageDraw.Draw(layer)

    # Outer glow ring (gold, blurred later)
    for i in range(20, 0, -1):
        a = int(55 * (i / 20) ** 2)
        ld.ellipse(
            [cx - R - i, cy - R - i, cx + R + i, cy + R + i],
            outline=(*_GOLD, a),
            width=2,
        )
    canvas = Image.alpha_composite(canvas,
                 layer.filter(ImageFilter.GaussianBlur(6)))

    # Dark ring just inside glow
    ring_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    rd         = ImageDraw.Draw(ring_layer)
    rd.ellipse([cx - R, cy - R, cx + R, cy + R],
               fill=(*_CARD_BG2, 255))
    canvas = Image.alpha_composite(canvas, ring_layer)

    # Thin gold ring border
    border_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    brd          = ImageDraw.Draw(border_layer)
    brd.ellipse([cx - R, cy - R, cx + R, cy + R],
                outline=(*_GOLD, 200), width=3)
    canvas = Image.alpha_composite(canvas, border_layer)

    # Album art clipped to circle
    art_r = R - 6
    if art:
        # Crop to square, resize
        ow, oh = art.size
        side   = min(ow, oh)
        left   = (ow - side) // 2
        top    = (oh - side) // 2
        sq     = art.crop((left, top, left + side, top + side))
        sq     = sq.resize((art_r * 2, art_r * 2), Image.LANCZOS).convert("RGBA")
        sq     = ImageEnhance.Brightness(sq).enhance(0.92)
        sq     = ImageEnhance.Color(sq).enhance(1.12)

        # Circular mask
        mask = Image.new("L", (art_r * 2, art_r * 2), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, art_r * 2, art_r * 2], fill=255)
        sq.putalpha(mask)

        art_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
        art_layer.alpha_composite(sq, dest=(cx - art_r, cy - art_r))
        canvas = Image.alpha_composite(canvas, art_layer)
    else:
        # Placeholder gradient circle
        ph = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
        pd = ImageDraw.Draw(ph)
        pd.ellipse([cx - art_r, cy - art_r, cx + art_r, cy + art_r],
                   fill=(*_CARD_BG2, 255))
        # Music note placeholder
        pd.text((cx - 24, cy - 32), "♪", font=_font(64, bold=True),
                fill=(*_GOLD, 140))
        canvas = Image.alpha_composite(canvas, ph)

    # Small center dot (vinyl style)
    dot_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    dd        = ImageDraw.Draw(dot_layer)
    dd.ellipse([cx - 14, cy - 14, cx + 14, cy + 14],
               fill=(*_CARD_BG2, 255))
    dd.ellipse([cx - 6, cy - 6, cx + 6, cy + 6],
               fill=(*_GOLD, 220))
    canvas = Image.alpha_composite(canvas, dot_layer)

    return canvas


# ═══════════════════════════════════════════════════════════════════════
#  PROGRESS BAR
# ═══════════════════════════════════════════════════════════════════════

def _draw_progress(draw: ImageDraw.ImageDraw,
                   x: int, y: int, w: int,
                   duration: str, seed: int) -> None:
    bar_h = 5
    r     = bar_h // 2

    # Parse duration to get a fixed progress fraction
    try:
        parts    = duration.replace(":", " ").split()
        nums     = [int(p) for p in parts if p.isdigit()]
        total_s  = nums[-2] * 60 + nums[-1] if len(nums) >= 2 else int(nums[0]) if nums else 200
    except Exception:
        total_s = 200
    # Pseudo-random playback position based on seed
    progress = 0.28 + (seed % 100) / 200.0   # 28%–78% range
    filled   = int(w * progress)

    # Background track
    draw.rounded_rectangle(
        [x, y, x + w, y + bar_h],
        radius=r,
        fill=(*_BAR_BG, 255),
    )
    # Filled portion (gold gradient effect: two rects)
    if filled > 0:
        draw.rounded_rectangle(
            [x, y, x + filled, y + bar_h],
            radius=r,
            fill=(*_GOLD, 240),
        )
        # Bright highlight on filled bar
        if filled > 8:
            draw.rounded_rectangle(
                [x + 2, y, x + filled - 2, y + 2],
                radius=1,
                fill=(*_GOLD_LT, 180),
            )

    # Playhead dot
    ph_x = x + filled
    ph_r = 7
    draw.ellipse([ph_x - ph_r, y - ph_r + bar_h // 2,
                  ph_x + ph_r, y + ph_r + bar_h // 2],
                 fill=(*_WHITE, 255))
    draw.ellipse([ph_x - 3, y - 3 + bar_h // 2,
                  ph_x + 3, y + 3 + bar_h // 2],
                 fill=(*_GOLD, 255))


# ═══════════════════════════════════════════════════════════════════════
#  TITLE WRAP
# ═══════════════════════════════════════════════════════════════════════

def _wrap_title(draw: ImageDraw.ImageDraw,
                text: str, max_w: int) -> List[Tuple[str, object]]:
    for sz in [64, 54, 44, 36]:
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
    fnt = _font(34, bold=True)
    return [(text[:30] + ("…" if len(text) > 30 else ""), fnt)]


# ═══════════════════════════════════════════════════════════════════════
#  NETWORK helpers
# ═══════════════════════════════════════════════════════════════════════

async def _fetch_thumbnail(videoid: str) -> Optional[Image.Image]:
    try:
        import aiohttp
        urls = [
            f"https://i.ytimg.com/vi/{videoid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/mqdefault.jpg",
        ]
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=8)
                    ) as r:
                        if r.status != 200:
                            continue
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
        res  = await VideosSearch(
            f"https://youtu.be/{videoid}", limit=1
        ).next()
        item    = res["result"][0]
        title   = _strip(item.get("title", "")) or "Unknown Title"
        dur     = item.get("duration", "") or "0:00"
        ch_raw  = item.get("channel", {})
        channel = (
            ch_raw.get("name", "YouTube")
            if isinstance(ch_raw, dict) else "YouTube"
        )
        return title, dur, channel
    except Exception:
        return "Unknown Title", "0:00", "YouTube"


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
#
#  Layout (1280 × 720):
#  ┌──────────────────────────────────────────────────────────────────┐
#  │  DARK BG (blurred art)                                           │
#  │  ┌─────────────────────────── CARD ──────────────────────────┐  │
#  │  │  ┌───────────────┐   NOW PLAYING  ●                       │  │
#  │  │  │               │   SONG TITLE  (large bold)             │  │
#  │  │  │  CIRCULAR ART │   Artist / Channel Name                │  │
#  │  │  │               │   ──────────────── (gold divider)      │  │
#  │  │  └───────────────┘   ██████░░░░░░░  (progress bar)        │  │
#  │  │                       0:47          3:37                  │  │
#  │  │                       ♪ MUSKAN MUSIC                      │  │
#  │  └───────────────────────────────────────────────────────────┘  │
#  └──────────────────────────────────────────────────────────────────┘

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

    # ── 1. Dark blurred background ───────────────────────────────────
    canvas = _make_bg(art)

    # ── 2. Frosted card ──────────────────────────────────────────────
    canvas = _draw_card(canvas)

    # ── 3. Circular album art (left side) ────────────────────────────
    canvas = _place_circular_art(canvas, art)

    # ── 4. Text on right side ────────────────────────────────────────
    draw = ImageDraw.Draw(canvas)

    # Card boundaries
    pad_x, pad_y = 64, 56
    card_x2      = _W - pad_x
    card_y2      = _H - pad_y

    # Right text zone starts after circular art center area
    TX   = 590          # left edge of text zone
    TW   = card_x2 - TX - 48   # available text width
    TY   = pad_y + 52   # top of text zone

    # ── 4a. "NOW PLAYING" badge ──────────────────────────────────────
    f_badge  = _font(16, bold=True)
    badge_tx = "NOW PLAYING"

    # Dot indicator before badge
    dot_r = 5
    draw.ellipse(
        [TX, TY + 6, TX + dot_r * 2, TY + 6 + dot_r * 2],
        fill=(*_AMBER, 255)
    )
    # Pulsing ring
    draw.ellipse(
        [TX - 3, TY + 3, TX + dot_r * 2 + 3, TY + 9 + dot_r * 2],
        outline=(*_AMBER, 80), width=1
    )
    bx = TX + dot_r * 2 + 12
    bw = _tw(draw, badge_tx, f_badge) + 24
    bh = 28

    # Badge fill + border (drawn separately to avoid Pillow compat issues)
    badge_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    bl          = ImageDraw.Draw(badge_layer)
    bl.rounded_rectangle([bx, TY, bx + bw, TY + bh],
                         radius=6, fill=(*_GOLD, 22))
    bl.rounded_rectangle([bx, TY, bx + bw, TY + bh],
                         radius=6, outline=(*_GOLD, 180), width=1)
    canvas = Image.alpha_composite(canvas, badge_layer)
    draw   = ImageDraw.Draw(canvas)  # refresh draw after composite

    draw.text((bx + 12, TY + 6), badge_tx, font=f_badge, fill=(*_GOLD, 235))
    TY += bh + 28

    # ── 4b. Song title ───────────────────────────────────────────────
    title_lines = _wrap_title(draw, title or "Unknown Title", TW)
    for line, fnt in title_lines:
        # Shadow
        draw.text((TX + 2, TY + 2), line, font=fnt,
                  fill=(0, 0, 0, 100))
        # Text
        draw.text((TX, TY), line, font=fnt,
                  fill=(*_WHITE, 255))
        TY += _th(draw, line, fnt) + 10
    TY += 14

    # ── 4c. Channel / artist name ────────────────────────────────────
    ch_disp = channel[:38]
    f_ch    = _font(27, bold=False)
    draw.text((TX + 1, TY + 1), ch_disp, font=f_ch, fill=(0, 0, 0, 70))
    draw.text((TX, TY), ch_disp, font=f_ch, fill=(*_GOLD_LT, 210))
    TY += _th(draw, ch_disp, f_ch) + 24

    # ── 4d. Gold divider ─────────────────────────────────────────────
    draw.rectangle([TX, TY, TX + TW - 20, TY + 1], fill=(*_GOLD, 130))
    draw.rectangle([TX, TY + 1, TX + TW - 20, TY + 2],
                   fill=(*_GOLD_LT, 40))
    TY += 22

    # ── 4e. Progress bar ─────────────────────────────────────────────
    bar_w = TW - 20
    _draw_progress(draw, TX, TY, bar_w, duration, seed)
    TY += 22

    # Time labels below bar
    f_time = _font(21, bold=False)

    # Elapsed (fake, ~28% of total)
    try:
        parts   = duration.replace(":", " ").split()
        nums    = [int(p) for p in parts if p.isdigit()]
        total_s = nums[-2] * 60 + nums[-1] if len(nums) >= 2 else (int(nums[0]) if nums else 200)
    except Exception:
        total_s = 200
    progress  = 0.28 + (seed % 100) / 200.0
    elapsed_s = int(total_s * progress)
    el_str    = f"{elapsed_s // 60}:{elapsed_s % 60:02d}"

    draw.text((TX, TY), el_str, font=f_time, fill=(*_DIM, 200))
    dur_w = _tw(draw, duration, f_time)
    draw.text((TX + bar_w - dur_w, TY), duration,
              font=f_time, fill=(*_SMOKE, 200))
    TY += _th(draw, el_str, f_time) + 28

    # ── 4f. Requester ────────────────────────────────────────────────
    req = _strip(requester)
    if req:
        f_req = _font(20, bold=False)
        req_t = f"Requested by  {req[:24]}"
        draw.text((TX, TY), req_t, font=f_req, fill=(*_DIM, 180))
        TY += _th(draw, req_t, f_req) + 10

    # ── 4g. Branding ─────────────────────────────────────────────────
    brand   = "♪  MUSKAN MUSIC"
    f_brand = _font(20, bold=True)
    by      = card_y2 - 52
    draw.text((TX + 1, by + 1), brand, font=f_brand, fill=(0, 0, 0, 90))
    draw.text((TX, by), brand, font=f_brand, fill=(*_GOLD, 190))

    # Bot tag
    f_bot = _font(18, bold=False)
    draw.text((TX, by + 28), "@MuskanMusicBot",
              font=f_bot, fill=(*_DIM, 130))

    # ── 5. Top gold accent bar on card ───────────────────────────────
    # Short gold line under card top edge
    draw.rectangle([pad_x + 36, pad_y, pad_x + 36 + 80, pad_y + 2],
                   fill=(*_GOLD, 200))
    draw.rectangle([pad_x + 36 + 84, pad_y, pad_x + 36 + 100, pad_y + 2],
                   fill=(*_GOLD, 80))

    # ── 6. Save ──────────────────────────────────────────────────────
    canvas.convert("RGB").save(out, "JPEG", quality=96, optimize=True)
    return out
