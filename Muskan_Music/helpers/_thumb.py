# © @MuskanBot — Cinematic Dark Gold Premium Thumbnail v2

import asyncio
import math
import os
import random
import re
import time
from io import BytesIO

from PIL import (
    Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
)

# ── Cache ──────────────────────────────────────────────────────────────
_CACHE_DIR = "/tmp/muskan_thumbs"
os.makedirs(_CACHE_DIR, exist_ok=True)

# ── Canvas ─────────────────────────────────────────────────────────────
_W, _H = 1280, 720

# ── Palette ────────────────────────────────────────────────────────────
_BLACK   = (  8,   8,  10)
_DEEP    = ( 14,  12,  18)
_GOLD    = (212, 175,  55)
_GOLD_LT = (255, 220, 100)
_AMBER   = (255, 160,  40)
_WHITE   = (255, 255, 255)
_SMOKE   = (200, 195, 210)
_DIM     = (120, 115, 130)

# ── Font loader ────────────────────────────────────────────────────────
_FONT_PATHS = {
    True: [
        "/home/runner/workspace/Muskan_Music/assets/fonts/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ],
    False: [
        "/home/runner/workspace/Muskan_Music/assets/fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ],
}

def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for p in _FONT_PATHS[bold]:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def _strip(t: str) -> str:
    return re.sub(r"<[^>]+>", "", t or "").strip()

def _text_w(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(text) * 10

def _text_h(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]
    except Exception:
        return getattr(font, "size", 20)


# ═══════════════════════════════════════════════════════════════════════
#  BACKGROUND — deep dark with warm ambient glow bottom-left
# ═══════════════════════════════════════════════════════════════════════

def _make_bg() -> Image.Image:
    bg = Image.new("RGBA", (_W, _H), (*_BLACK, 255))
    d  = ImageDraw.Draw(bg)
    # Subtle vertical gradient: very slightly lighter at top
    for y in range(_H):
        t = y / _H
        r = int(_BLACK[0] + 8  * (1 - t))
        g = int(_BLACK[1] + 4  * (1 - t))
        b = int(_BLACK[2] + 14 * (1 - t))
        d.line([(0, y), (_W, y)], fill=(r, g, b, 255))

    # Warm amber radial glow — bottom-left corner
    glow = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    cx, cy = 0, _H
    for r in range(600, 0, -6):
        frac = r / 600
        # Gold tint fading out
        a  = int(28 * (1 - frac) ** 2.5)
        rc = int(_AMBER[0] * (1 - frac * 0.6))
        gc = int(_AMBER[1] * (1 - frac * 0.8))
        bc = int(_AMBER[2] * (1 - frac))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(rc, gc, bc, a))
    bg = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(30)))
    return bg


# ═══════════════════════════════════════════════════════════════════════
#  ALBUM ART — right-side cinematic panel with gradient fade
# ═══════════════════════════════════════════════════════════════════════

def _place_art(canvas: Image.Image, art: Image.Image) -> Image.Image:
    # Scale art to fill right panel (full height)
    art_w = int(_H * (art.width / art.height)) if art.height > 0 else _H
    art_r = art.resize((max(art_w, 700), _H), Image.LANCZOS).convert("RGBA")

    # Crop to right 700px wide panel
    panel_w = 700
    aw = art_r.width
    # Take rightmost portion
    x_off = max(0, aw - panel_w)
    art_r = art_r.crop((x_off, 0, x_off + panel_w, _H))

    # Dim the art for cinematic feel
    art_r = ImageEnhance.Brightness(art_r).enhance(0.72)
    art_r = ImageEnhance.Color(art_r).enhance(1.15)

    # Horizontal left-to-right fade mask (art becomes transparent on left edge)
    fade = Image.new("L", (panel_w, _H), 0)
    fd   = ImageDraw.Draw(fade)
    fade_width = 320
    for x in range(fade_width):
        alpha = int(255 * (x / fade_width) ** 1.8)
        fd.line([(x, 0), (x, _H)], fill=alpha)
    for x in range(fade_width, panel_w):
        fade.putpixel((x, 0) if False else (0, 0), 0)
    # Right side solid
    fd.rectangle([fade_width, 0, panel_w, _H], fill=255)
    art_r.putalpha(fade)

    # Place at right edge
    pos_x = _W - panel_w
    canvas.alpha_composite(art_r, dest=(pos_x, 0))
    return canvas


# ═══════════════════════════════════════════════════════════════════════
#  BLURRED BG LAYER — full canvas from album art, very dimmed
# ═══════════════════════════════════════════════════════════════════════

def _bg_art(canvas: Image.Image, art: Image.Image) -> Image.Image:
    # Fill entire canvas with blurred, very dark version of art
    ratio = _W / _H
    ow, oh = art.size
    if ow / oh > ratio:
        nw  = int(oh * ratio)
        art_c = art.crop(((ow - nw) // 2, 0, (ow - nw) // 2 + nw, oh))
    else:
        nh  = int(ow / ratio)
        art_c = art.crop((0, (oh - nh) // 2, ow, (oh - nh) // 2 + nh))

    art_c = art_c.resize((_W, _H), Image.LANCZOS).convert("RGBA")
    art_c = art_c.filter(ImageFilter.GaussianBlur(radius=22))
    art_c = ImageEnhance.Brightness(art_c).enhance(0.10)
    art_c.putalpha(Image.new("L", (_W, _H), 120))
    return Image.alpha_composite(canvas, art_c)


# ═══════════════════════════════════════════════════════════════════════
#  VIGNETTE — darkens corners
# ═══════════════════════════════════════════════════════════════════════

def _vignette(w: int, h: int) -> Image.Image:
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d   = ImageDraw.Draw(vig)
    steps = 90
    for i in range(steps, 0, -1):
        frac  = i / steps
        alpha = int(200 * (1 - frac) ** 2.2)
        margin = int(i * max(w, h) / steps * 0.8)
        d.rectangle(
            [margin, margin, w - margin, h - margin],
            outline=(0, 0, 0, alpha), width=6
        )
    return vig.filter(ImageFilter.GaussianBlur(20))


# ═══════════════════════════════════════════════════════════════════════
#  LEFT OVERLAY — gradient from left so text is always readable
# ═══════════════════════════════════════════════════════════════════════

def _left_overlay(w: int, h: int) -> Image.Image:
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # Strong on left, fades to transparent by x=820
    edge = 820
    for x in range(edge):
        frac  = x / edge
        alpha = int(210 * (1 - frac ** 1.4))
        d.line([(x, 0), (x, h)], fill=(0, 0, 0, alpha))
    return overlay


# ═══════════════════════════════════════════════════════════════════════
#  GOLD DECORATIVE LINE
# ═══════════════════════════════════════════════════════════════════════

def _gold_line(draw: ImageDraw.ImageDraw, x: int, y: int, length: int,
               height: int = 2, alpha: int = 200) -> None:
    # Main gold line
    draw.rectangle([x, y, x + length, y + height],
                   fill=(*_GOLD, alpha))
    # Subtle bright highlight on top
    draw.rectangle([x, y, x + length, y],
                   fill=(*_GOLD_LT, min(255, alpha + 30)))


# ═══════════════════════════════════════════════════════════════════════
#  PREMIUM WAVEFORM — thin elegant bars
# ═══════════════════════════════════════════════════════════════════════

def _waveform(draw: ImageDraw.ImageDraw, x: int, y: int,
              width: int, seed: int) -> None:
    rng    = random.Random(seed)
    count  = 52
    bar_w  = 3
    gap    = (width - count * bar_w) // count
    max_h  = 28
    min_h  = 4

    for i in range(count):
        bx  = x + i * (bar_w + gap)
        # Smooth sine-ish wave pattern with random variation
        wave = math.sin(i * 0.38) * 0.5 + 0.5
        bh   = int(min_h + (max_h - min_h) * wave * rng.uniform(0.6, 1.0))
        by   = y - bh

        # Color: brighter gold in the center-ish bars
        center_frac = 1 - abs(i / count - 0.5) * 2
        r = int(_GOLD[0] + (255 - _GOLD[0]) * center_frac * 0.3)
        g = int(_GOLD[1] + (220 - _GOLD[1]) * center_frac * 0.3)
        b = int(_GOLD[2])
        alpha = int(120 + 120 * center_frac)

        draw.rounded_rectangle(
            [bx, by, bx + bar_w, y],
            radius=1,
            fill=(r, g, b, alpha),
        )


# ═══════════════════════════════════════════════════════════════════════
#  TITLE WRAP — fits title into available width across 1–2 lines
# ═══════════════════════════════════════════════════════════════════════

def _wrap_title(draw: ImageDraw.ImageDraw, text: str, max_w: int):
    """Returns list of (line_str, font) tuples."""
    sizes = [68, 56, 46, 38]
    for sz in sizes:
        fnt    = _font(sz, bold=True)
        words  = text.split()
        lines  = []
        cur    = ""
        for w in words:
            test = (cur + " " + w).strip()
            if _text_w(draw, test, fnt) <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) <= 2 and all(_text_w(draw, l, fnt) <= max_w for l in lines):
            return [(l, fnt) for l in lines[:2]]
    # Fallback: truncate
    fnt = _font(36, bold=True)
    return [(text[:28] + ("…" if len(text) > 28 else ""), fnt)]


# ═══════════════════════════════════════════════════════════════════════
#  NETWORK: fetch YouTube thumbnail + info
# ═══════════════════════════════════════════════════════════════════════

async def _fetch_thumbnail(videoid: str) -> Image.Image | None:
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
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
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
        res  = await VideosSearch(f"https://youtu.be/{videoid}", limit=1).next()
        item = res["result"][0]
        title   = _strip(item.get("title", "")) or "Unknown Title"
        dur     = item.get("duration", "") or "00:00"
        ch_raw  = item.get("channel", {})
        channel = ch_raw.get("name", "YouTube") if isinstance(ch_raw, dict) else "YouTube"
        return title, dur, channel
    except Exception:
        return "Unknown Title", "00:00", "YouTube"


# ═══════════════════════════════════════════════════════════════════════
#  MAIN — Cinematic Dark Gold Thumbnail
# ═══════════════════════════════════════════════════════════════════════
#
#  Layout (1280 × 720):
#  ┌──────────────────────────────────────────────────────────┐
#  │  thin gold bar (top)                                     │
#  │                                                          │
#  │  LEFT TEXT ZONE (x: 72–740)   │  ALBUM ART (x: 580–1280)│
#  │  ● NOW PLAYING badge           │  (cinematic, edge-bleed)│
#  │  ● Song title (large, bold)    │                         │
#  │  ● Gold divider                │                         │
#  │  ● Channel name                │                         │
#  │  ● Duration chip               │                         │
#  │  ● Waveform bars               │                         │
#  │  ● Muskan Music watermark      │                         │
#  │                                                          │
#  │  thin gold bar (bottom)                                  │
#  └──────────────────────────────────────────────────────────┘

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

    title    = _strip(title)    or yt_title
    duration = duration         or yt_dur
    channel  = _strip(channel)
    seed     = sum(ord(c) for c in videoid) % 9999

    # ── 1. Deep dark base ────────────────────────────────────────────
    bg = _make_bg()

    # ── 2. Blurred art as full-canvas ambient fill ───────────────────
    if art:
        bg = _bg_art(bg, art)

    # ── 3. Cinematic art panel (right side) ──────────────────────────
    if art:
        bg = _place_art(bg, art)

    # ── 4. Left overlay (darkens left so text pops) ──────────────────
    bg = Image.alpha_composite(bg, _left_overlay(_W, _H))

    # ── 5. Vignette ──────────────────────────────────────────────────
    bg = Image.alpha_composite(bg, _vignette(_W, _H))

    draw = ImageDraw.Draw(bg)

    # ── 6. Thin gold letterbox bars (top & bottom) ───────────────────
    draw.rectangle([0, 0, _W, 3], fill=(*_GOLD, 200))
    draw.rectangle([0, _H - 4, _W, _H - 1], fill=(*_GOLD, 160))
    # Extra highlight line under top bar
    draw.rectangle([0, 3, _W, 4], fill=(*_GOLD_LT, 60))

    # ── 7. Text zone setup ───────────────────────────────────────────
    TX   = 72          # left margin
    TW   = 660         # text zone width
    TY   = 72          # start Y

    # ── 8. "NOW PLAYING" badge ───────────────────────────────────────
    f_badge  = _font(17, bold=True)
    badge_tx = "NOW PLAYING"
    bw       = _text_w(draw, badge_tx, f_badge) + 32
    bh       = 30

    # Badge: thin gold border, no fill
    draw.rounded_rectangle(
        [TX, TY, TX + bw, TY + bh],
        radius=6,
        outline=(*_GOLD, 220),
        width=1,
    )
    # Subtle gold tint inside
    draw.rounded_rectangle(
        [TX, TY, TX + bw, TY + bh],
        radius=6,
        fill=(*_GOLD, 18),
    )
    # Left gold accent bar
    draw.rectangle([TX, TY + 5, TX + 2, TY + bh - 5], fill=(*_GOLD, 255))
    draw.text((TX + 14, TY + 7), badge_tx, font=f_badge, fill=(*_GOLD, 255))

    # Small play dot to the right of badge
    dot_x = TX + bw + 14
    draw.ellipse([dot_x, TY + 11, dot_x + 8, TY + 19],
                 fill=(*_AMBER, 200))

    TY += bh + 32

    # ── 9. Song title ────────────────────────────────────────────────
    title_lines = _wrap_title(draw, title or "Unknown Title", TW - 20)
    for line, fnt in title_lines:
        # Subtle shadow
        draw.text((TX + 2, TY + 2), line, font=fnt, fill=(0, 0, 0, 120))
        # Main white text
        draw.text((TX, TY), line, font=fnt, fill=(*_WHITE, 252))
        lh  = _text_h(draw, line, fnt) + 8
        TY += lh
    TY += 18

    # ── 10. Gold divider ─────────────────────────────────────────────
    _gold_line(draw, TX, TY, TW - 60, height=1, alpha=180)
    TY += 18

    # ── 11. Channel name ─────────────────────────────────────────────
    ch_disp  = channel[:36] if channel else "YouTube"
    f_ch     = _font(28, bold=False)
    draw.text((TX, TY), ch_disp, font=f_ch, fill=(*_SMOKE, 210))
    TY += _text_h(draw, ch_disp, f_ch) + 22

    # ── 12. Duration pill ────────────────────────────────────────────
    dur_txt = duration or "00:00"
    f_dur   = _font(24, bold=True)
    dw      = _text_w(draw, dur_txt, f_dur) + 36
    dh      = 34
    # Dark pill with gold border
    draw.rounded_rectangle(
        [TX, TY, TX + dw, TY + dh],
        radius=17,
        fill=(0, 0, 0, 100),
    )
    draw.rounded_rectangle(
        [TX, TY, TX + dw, TY + dh],
        radius=17,
        outline=(*_GOLD, 160),
        width=1,
    )
    draw.text(
        (TX + 18, TY + 5),
        dur_txt, font=f_dur, fill=(*_GOLD_LT, 240)
    )

    # Requester next to duration
    req = _strip(requester)
    if req:
        f_req  = _font(22, bold=False)
        draw.text(
            (TX + dw + 18, TY + 7),
            f"▸  {req[:22]}",
            font=f_req,
            fill=(*_DIM, 200),
        )

    TY += dh + 16

    # ── 13. Thin accent dot row ──────────────────────────────────────
    for i in range(5):
        dx = TX + i * 14
        draw.ellipse([dx, TY + 6, dx + 5, TY + 11],
                     fill=(*_GOLD, 60 + i * 20))
    TY += 28

    # ── 14. Waveform ─────────────────────────────────────────────────
    WY = _H - 80
    _waveform(draw, TX, WY, TW - 60, seed)

    # ── 15. Bottom gold divider ──────────────────────────────────────
    _gold_line(draw, TX, WY + 14, TW - 60, height=1, alpha=80)

    # ── 16. Branding watermark ───────────────────────────────────────
    brand    = "MUSKAN MUSIC"
    f_brand  = _font(18, bold=True)
    brand_w  = _text_w(draw, brand, f_brand)
    bx       = TX
    by       = _H - 48
    # Character-spaced small caps feel (just track with letter-spacing)
    draw.text((bx + 1, by + 1), brand, font=f_brand, fill=(0, 0, 0, 100))
    draw.text((bx, by), brand, font=f_brand, fill=(*_GOLD, 160))

    # Small gold dot separator
    draw.ellipse([bx + brand_w + 8, by + 8,
                  bx + brand_w + 14, by + 14],
                 fill=(*_GOLD, 100))
    draw.text((bx + brand_w + 20, by),
              "Music Bot", font=_font(18, bold=False),
              fill=(*_DIM, 120))

    # ── 17. Subtle right-edge art glow outline ───────────────────────
    if art:
        edge_x = _W - 700
        for i in range(12, 0, -1):
            alpha = int(40 * (i / 12))
            draw.line(
                [(edge_x + i, 0), (edge_x + i, _H)],
                fill=(*_GOLD, alpha),
                width=1,
            )

    # ── 18. Save ─────────────────────────────────────────────────────
    bg.convert("RGB").save(out, "JPEG", quality=96, optimize=True)
    return out
