# © @MuskanBot — Aurora Neon Premium Thumbnail v1

import asyncio
import os
import random
import re
import textwrap
import time
import math
from io import BytesIO

from PIL import (
    Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
)

# ── Cache dir ──────────────────────────────────────────────────────────
_CACHE_DIR = "/tmp/muskan_thumbs"
os.makedirs(_CACHE_DIR, exist_ok=True)

# ── Canvas ─────────────────────────────────────────────────────────────
_W, _H = 1280, 720

# ── Aurora palette ─────────────────────────────────────────────────────
_ROSE    = (255,  80, 140)
_PURPLE  = (160,  40, 220)
_TEAL    = (  0, 210, 190)
_AMBER   = (255, 190,  60)
_WHITE   = (255, 255, 255)
_NAVY    = (  6,   8,  22)
_LAVENDER= (200, 160, 255)

# ── Fonts ──────────────────────────────────────────────────────────────
def _find_font(bold=True):
    paths = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSans.ttf"]
    )
    for p in paths:
        if os.path.isfile(p):
            return p
    return None

_FB = _find_font(True)
_FR = _find_font(False)

def _font(size, bold=True):
    try:
        p = _FB if bold else _FR
        if p:
            return ImageFont.truetype(p, size)
    except Exception:
        pass
    return ImageFont.load_default()

def _strip(t):
    return re.sub(r"<[^>]+>", "", t or "").strip()

def _tw(draw, text, font):
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(text) * 12


# ═══════════════════════════════════════════════════════════════════════
#  BACKGROUND — deep navy with subtle radial glow
# ═══════════════════════════════════════════════════════════════════════

def _make_bg() -> Image.Image:
    bg = Image.new("RGBA", (_W, _H), _NAVY)
    d  = ImageDraw.Draw(bg)
    # Vertical gradient: slightly lighter top
    for y in range(_H):
        t = y / _H
        r = int(6  + 10 * (1 - t))
        g = int(8  +  4 * (1 - t))
        b = int(22 + 20 * (1 - t))
        d.line([(0, y), (_W, y)], fill=(r, g, b, 255))
    return bg


# ═══════════════════════════════════════════════════════════════════════
#  AURORA STREAKS — diagonal light sweeps
# ═══════════════════════════════════════════════════════════════════════

def _aurora(canvas: Image.Image, seed: int) -> Image.Image:
    rng = random.Random(seed)
    layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    streaks = [
        (_PURPLE,  0.22, 140, 70),
        (_ROSE,    0.18, 180, 55),
        (_TEAL,    0.15, 120, 45),
        (_PURPLE,  0.28, 100, 35),
        (_ROSE,    0.12, 200, 30),
        (_TEAL,    0.20, 160, 40),
    ]

    for col, width_frac, alpha, blur_steps in streaks:
        # Random diagonal band
        cx = rng.randint(-100, _W + 100)
        cy = rng.randint(-_H // 4, _H + _H // 4)
        angle = rng.uniform(-25, 25)
        rad   = math.radians(angle)
        half_w = int(_W * width_frac)
        length  = int(math.hypot(_W, _H) * 1.4)

        for step in range(blur_steps, 0, -1):
            frac  = step / blur_steps
            aw    = int(alpha * (frac ** 2.2))
            off   = int(half_w * (1 - frac))
            # Perpendicular offset direction
            px = int(-math.sin(rad) * off)
            py = int( math.cos(rad) * off)
            dx = int( math.cos(rad) * length / 2)
            dy = int( math.sin(rad) * length / 2)
            pts = [
                (cx + dx + px, cy + dy + py),
                (cx - dx + px, cy - dy + py),
            ]
            d.line(pts, fill=(*col, aw), width=max(1, int(half_w * frac * 2)))

    blurred = layer.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(canvas, blurred)


# ═══════════════════════════════════════════════════════════════════════
#  GRID LINES — subtle tech feel
# ═══════════════════════════════════════════════════════════════════════

def _grid(canvas: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    spacing = 80
    for x in range(0, _W, spacing):
        d.line([(x, 0), (x, _H)], fill=(255, 255, 255, 6), width=1)
    for y in range(0, _H, spacing):
        d.line([(0, y), (_W, y)], fill=(255, 255, 255, 6), width=1)
    return Image.alpha_composite(canvas, layer)


# ═══════════════════════════════════════════════════════════════════════
#  VIGNETTE
# ═══════════════════════════════════════════════════════════════════════

def _vignette(w, h, strength=160, steps=80) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    for i in range(steps):
        t = i / steps
        a = int(strength * (1 - t) ** 2.0)
        m = i * 5
        if w - 2*m <= 0 or h - 2*m <= 0:
            break
        d.rectangle([m, m, w-m-1, h-m-1], outline=(0, 0, 0, a), width=1)
    return img


# ═══════════════════════════════════════════════════════════════════════
#  LEFT GRADIENT SHADOW (text legibility)
# ═══════════════════════════════════════════════════════════════════════

def _left_fade(w, h) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    end = int(w * 0.65)
    for x in range(end):
        a = int(200 * (1 - x / end) ** 0.55)
        d.line([(x, 0), (x, h)], fill=(0, 0, 0, a))
    return img


# ═══════════════════════════════════════════════════════════════════════
#  ALBUM ART — right side, hexagonal frame with glow
# ═══════════════════════════════════════════════════════════════════════

def _hex_mask(size: int) -> Image.Image:
    """Create a hexagon mask."""
    mask = Image.new("L", (size, size), 0)
    d    = ImageDraw.Draw(mask)
    cx = cy = size // 2
    r  = size // 2 - 4
    pts = [
        (cx + r * math.cos(math.radians(60 * i - 30)),
         cy + r * math.sin(math.radians(60 * i - 30)))
        for i in range(6)
    ]
    d.polygon(pts, fill=255)
    return mask


def _circle_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    return mask


def _art_with_glow(canvas: Image.Image, art: Image.Image,
                   cx: int, cy: int, size: int) -> Image.Image:
    # Glow rings
    glow = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    ring_cols = [_ROSE, _PURPLE, _TEAL, _AMBER]
    for i, col in enumerate(ring_cols):
        steps = 50 - i * 8
        for s in range(steps, 0, -1):
            a = int(55 * (s / steps) ** 2.5)
            offset = size // 2 + s * 3
            gd.ellipse([cx - offset, cy - offset, cx + offset, cy + offset],
                       fill=(*col, a))
    blurred_glow = glow.filter(ImageFilter.GaussianBlur(radius=18))
    canvas = Image.alpha_composite(canvas, blurred_glow)

    # Spinning color ring (neon border)
    ring_layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_layer)
    r0 = size // 2 + 6
    colors_ring = [_ROSE, _PURPLE, _TEAL, _AMBER, _ROSE]
    num_segs = 120
    for i in range(num_segs):
        t  = i / num_segs
        ni = (i + 1) % num_segs
        a1 = math.radians(360 * t - 90)
        a2 = math.radians(360 * ni / num_segs - 90)
        ci = int(t * (len(colors_ring) - 1))
        cn = min(ci + 1, len(colors_ring) - 1)
        ft = t * (len(colors_ring) - 1) - ci
        c1, c2 = colors_ring[ci], colors_ring[cn]
        cr = int(c1[0] + (c2[0]-c1[0]) * ft)
        cg = int(c1[1] + (c2[1]-c1[1]) * ft)
        cb = int(c1[2] + (c2[2]-c1[2]) * ft)
        x1 = cx + int(r0 * math.cos(a1))
        y1 = cy + int(r0 * math.sin(a1))
        x2 = cx + int(r0 * math.cos(a2))
        y2 = cy + int(r0 * math.sin(a2))
        rd.line([(x1, y1), (x2, y2)], fill=(cr, cg, cb, 240), width=4)
    # Thin white inner ring
    rd.ellipse([cx - size//2 - 2, cy - size//2 - 2,
                cx + size//2 + 2, cy + size//2 + 2],
               outline=(255, 255, 255, 60), width=1)
    canvas = Image.alpha_composite(canvas, ring_layer)

    # Paste cropped circular art
    art_sq = art.resize((size, size), Image.LANCZOS).convert("RGBA")
    mask   = _circle_mask(size)
    art_sq.putalpha(mask)
    canvas.paste(art_sq, (cx - size//2, cy - size//2), art_sq)

    # Shine overlay (top-left glint)
    shine = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    for si in range(size // 3, 0, -2):
        sa = int(40 * (si / (size // 3)) ** 0.5)
        sd.ellipse([-si, -si, si, si], fill=(255, 255, 255, sa))
    canvas.paste(shine, (cx - size//2, cy - size//2), shine)

    return canvas


# ═══════════════════════════════════════════════════════════════════════
#  WAVEFORM BAR — decorative bottom element
# ═══════════════════════════════════════════════════════════════════════

def _waveform(draw: ImageDraw.ImageDraw, x: int, y: int,
              w: int, seed: int):
    rng    = random.Random(seed)
    n      = 42
    bar_w  = max(2, (w - n * 2) // n)
    gap    = (w - n * bar_w) // (n + 1)
    cols   = [_ROSE, _PURPLE, _TEAL, _AMBER]
    heights_base = [
        int(28 + 34 * abs(math.sin(i * 0.55 + rng.uniform(0, 1))))
        for i in range(n)
    ]
    for i, bh in enumerate(heights_base):
        t  = i / (n - 1)
        ci = int(t * (len(cols) - 1))
        cn = min(ci + 1, len(cols) - 1)
        ft = t * (len(cols) - 1) - ci
        c1, c2 = cols[ci], cols[cn]
        cr = int(c1[0] + (c2[0]-c1[0]) * ft)
        cg = int(c1[1] + (c2[1]-c1[1]) * ft)
        cb = int(c1[2] + (c2[2]-c1[2]) * ft)
        bx = x + i * (bar_w + gap)
        # Mirror: bar above and below center
        for sign in [1, -1]:
            h2   = bh // 2
            ya   = y - sign * h2
            yb   = y - sign * 2
            draw.rectangle(
                [bx, min(ya, yb), bx + bar_w, max(ya, yb)],
                fill=(cr, cg, cb, 180)
            )
        # Top cap glow
        draw.rectangle(
            [bx, y - heights_base[i] // 2 - 2,
             bx + bar_w, y - heights_base[i] // 2],
            fill=(255, 255, 255, 100)
        )


# ═══════════════════════════════════════════════════════════════════════
#  GRADIENT LINE
# ═══════════════════════════════════════════════════════════════════════

def _gradient_line(canvas, x, y, w, h_px=2):
    bar  = Image.new("RGBA", (w, h_px), (0, 0, 0, 0))
    d    = ImageDraw.Draw(bar)
    cols = [_ROSE, _PURPLE, _TEAL, _AMBER, _ROSE]
    for px in range(w):
        t  = px / w
        ci = int(t * (len(cols) - 1))
        cn = min(ci + 1, len(cols) - 1)
        ft = t * (len(cols) - 1) - ci
        c1, c2 = cols[ci], cols[cn]
        cr = int(c1[0] + (c2[0]-c1[0]) * ft)
        cg = int(c1[1] + (c2[1]-c1[1]) * ft)
        cb = int(c1[2] + (c2[2]-c1[2]) * ft)
        a  = int(230 * (1 - abs(t - 0.5) * 0.4))
        d.line([(px, 0), (px, h_px - 1)], fill=(cr, cg, cb, a))
    canvas.paste(bar, (x, y), bar)


# ═══════════════════════════════════════════════════════════════════════
#  TITLE AUTO-FIT
# ═══════════════════════════════════════════════════════════════════════

def _fit_title(draw, text, max_w, max_lines=2):
    for size in range(62, 26, -4):
        f = _font(size)
        wrapped = textwrap.wrap(text, width=max(6, int(max_w / (size * 0.54))))
        lines   = wrapped[:max_lines]
        if not lines:
            lines = [text[:16]]
        if all(_tw(draw, l, f) <= max_w for l in lines):
            return [(l, f) for l in lines]
    f = _font(26)
    t = text
    while _tw(draw, t, f) > max_w and len(t) > 4:
        t = t[:-2] + "…"
    return [(t, f)]


# ═══════════════════════════════════════════════════════════════════════
#  NETWORK HELPERS
# ═══════════════════════════════════════════════════════════════════════

async def _fetch_thumbnail(videoid: str) -> Image.Image | None:
    try:
        import aiohttp
        urls = [
            f"https://i.ytimg.com/vi/{videoid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/mqdefault.jpg",
        ]
        async with aiohttp.ClientSession() as s:
            for url in urls:
                try:
                    async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                        if r.status != 200:
                            continue
                        data = await r.read()
                        img  = Image.open(BytesIO(data)).convert("RGBA")
                        if img.size[0] < 200:
                            continue
                        return img
                except Exception:
                    continue
    except Exception:
        pass
    return None


async def _fetch_video_info(videoid: str):
    try:
        from py_yt import VideosSearch
        res = await VideosSearch(f"https://youtu.be/{videoid}", limit=1).next()
        r   = res["result"][0]
        title   = _strip(r.get("title", "")) or "Unknown Title"
        dur     = r.get("duration", "") or "00:00"
        ch_raw  = r.get("channel", {})
        channel = ch_raw.get("name", "YouTube") if isinstance(ch_raw, dict) else "YouTube"
        return title, dur, channel
    except Exception:
        return "Unknown Title", "00:00", "YouTube"


# ═══════════════════════════════════════════════════════════════════════
#  NOISE GRAIN
# ═══════════════════════════════════════════════════════════════════════

def _noise(w, h, intensity=14, alpha=16) -> Image.Image:
    T   = 256
    raw = bytearray(
        random.randint(max(0, 128 - intensity), min(255, 128 + intensity))
        for _ in range(T * T)
    )
    tile = Image.frombytes("L", (T, T), bytes(raw))
    full = Image.new("L", (w, h))
    for y in range(0, h, T):
        for x in range(0, w, T):
            full.paste(tile, (x, y))
    rgba = full.convert("RGBA")
    r_, g_, b_, _ = rgba.split()
    a_ = Image.new("L", (w, h), alpha)
    return Image.merge("RGBA", (r_, g_, b_, a_))


# ═══════════════════════════════════════════════════════════════════════
#  GLASS CARD (left panel)
# ═══════════════════════════════════════════════════════════════════════

def _glass_card(bg: Image.Image, box, radius=28) -> Image.Image:
    x1, y1, x2, y2 = box
    pw, ph = x2 - x1, y2 - y1

    region  = bg.crop((x1, y1, x2, y2)).convert("RGBA")
    blurred = region.filter(ImageFilter.GaussianBlur(radius=32))
    blurred = ImageEnhance.Brightness(blurred).enhance(0.22)

    # Tints
    for tint, a in [((255,255,255), 12), (_PURPLE, 8), (_ROSE, 5)]:
        t = Image.new("RGBA", (pw, ph), (*tint, a))
        blurred = Image.alpha_composite(blurred, t)

    # Left-to-right sweep highlight
    sweep = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    sd    = ImageDraw.Draw(sweep)
    for x in range(pw):
        t = x / pw
        a = int(22 * (1 - t) ** 1.5)
        sd.line([(x, 0), (x, ph)], fill=(255, 255, 255, a))
    blurred = Image.alpha_composite(blurred, sweep)

    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw-1, ph-1], radius=radius, fill=255)
    blurred.putalpha(mask)

    out = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    out.paste(blurred, (x1, y1), blurred)
    d = ImageDraw.Draw(out)

    # Gradient border (rose → purple → teal)
    for shrink, col, width, alpha in [
        (0, _ROSE,   2, 90),
        (2, _PURPLE, 1, 60),
        (4, _TEAL,   1, 40),
    ]:
        d.rounded_rectangle(
            [x1+shrink, y1+shrink, x2-shrink, y2-shrink],
            radius=max(1, radius-shrink),
            outline=(*col, alpha), width=width
        )

    # Top shimmer line
    sh = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    sd2 = ImageDraw.Draw(sh)
    sd2.line([(x1+radius, y1+1), (x2-radius, y1+1)],
             fill=(255, 255, 255, 70), width=2)
    out = Image.alpha_composite(out, sh)

    return out


# ═══════════════════════════════════════════════════════════════════════
#  MAIN GENERATOR
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

    (yt_title, yt_dur, channel), original = await asyncio.gather(
        _fetch_video_info(videoid),
        _fetch_thumbnail(videoid),
    )

    title    = _strip(title) or yt_title
    duration = duration or yt_dur
    seed     = sum(ord(c) for c in videoid) % 9999

    # ── 1. Base background ────────────────────────────────────────────
    bg = _make_bg()

    # ── 2. Album art as blurred BG overlay ───────────────────────────
    if original:
        bw, bh = original.size
        ratio  = _W / _H
        if bw / bh > ratio:
            nw  = int(bh * ratio)
            art_bg = original.crop(((bw-nw)//2, 0, (bw-nw)//2+nw, bh))
        else:
            nh  = int(bw / ratio)
            art_bg = original.crop((0, (bh-nh)//2, bw, (bh-nh)//2+nh))
        art_bg = art_bg.resize((_W, _H), Image.LANCZOS).convert("RGBA")
        art_bg = art_bg.filter(ImageFilter.GaussianBlur(radius=10))
        art_bg = ImageEnhance.Brightness(art_bg).enhance(0.18)
        art_bg.putalpha(Image.new("L", (_W, _H), 140))
        bg = Image.alpha_composite(bg, art_bg)

    # ── 3. Aurora streaks ─────────────────────────────────────────────
    bg = _aurora(bg, seed)

    # ── 4. Subtle grid ────────────────────────────────────────────────
    bg = _grid(bg)

    # ── 5. Left fade + vignette ───────────────────────────────────────
    bg = Image.alpha_composite(bg, _left_fade(_W, _H))
    bg = Image.alpha_composite(bg, _vignette(_W, _H))

    # ── 6. Glass card ─────────────────────────────────────────────────
    CARD = (28, 38, 640, 682)
    bg   = Image.alpha_composite(bg, _glass_card(bg, CARD, radius=30))

    # ── 7. Album art circle (right side) ──────────────────────────────
    ART_SIZE = 340
    ART_CX   = _W - 60 - ART_SIZE // 2
    ART_CY   = _H // 2
    if original:
        # Square-crop to 1:1 first
        ow, oh = original.size
        s  = min(ow, oh)
        sq = original.crop(((ow-s)//2, (oh-s)//2, (ow+s)//2, (oh+s)//2))
        bg = _art_with_glow(bg, sq, ART_CX, ART_CY, ART_SIZE)

    # ── 8. Film grain ─────────────────────────────────────────────────
    bg = Image.alpha_composite(bg, _noise(_W, _H))

    # ── 9. Card text ──────────────────────────────────────────────────
    draw  = ImageDraw.Draw(bg)
    PAD   = CARD[0] + 44
    TW    = CARD[2] - PAD - 36       # usable text width ≈ 568px
    TY    = CARD[1] + 48

    # ▸ "NOW PLAYING" neon badge
    badge   = "▶  NOW PLAYING"
    f_badge = _font(18)
    bpw, bph = 200, 30

    # Badge outer glow
    glow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    for gi in range(14, 0, -1):
        ga = int(28 * (gi / 14))
        gd.rounded_rectangle(
            [PAD-gi, TY-gi, PAD+bpw+gi, TY+bph+gi],
            radius=10+gi, fill=(*_ROSE, ga)
        )
    bg   = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(4)))
    draw = ImageDraw.Draw(bg)

    draw.rounded_rectangle([PAD, TY, PAD+bpw, TY+bph],
                            radius=10, fill=(*_ROSE, 200))
    draw.rounded_rectangle([PAD, TY, PAD+bpw, TY+bph],
                            radius=10, outline=(*_WHITE, 80), width=1)
    draw.text((PAD+10, TY+6), badge, font=f_badge, fill=(*_WHITE, 255))
    TY += bph + 18

    # ▸ Channel name
    ch_clean = _strip(channel)[:40]
    draw.text((PAD, TY), f"♪  {ch_clean}",
              font=_font(22, bold=False), fill=(*_LAVENDER, 200))
    TY += 38

    # ▸ Gradient divider
    _gradient_line(bg, PAD, TY, TW, 2)
    draw = ImageDraw.Draw(bg)
    TY  += 20

    # ▸ Song title — neon glow text
    title_lines = _fit_title(draw, title or "Unknown Title", TW, max_lines=2)
    for i, (line, fnt) in enumerate(title_lines):
        # Glow layers
        for goff, gcol, ga in [
            ((4, 4), _ROSE,   50),
            ((2, 2), _PURPLE, 80),
            ((1, 1), _TEAL,   40),
        ]:
            draw.text((PAD+goff[0], TY+goff[1]), line,
                      font=fnt, fill=(*gcol, ga))
        # Shadow
        draw.text((PAD+2, TY+2), line, font=fnt, fill=(0, 0, 0, 140))
        # Main white text
        draw.text((PAD, TY), line, font=fnt, fill=(*_WHITE, 255))
        try:
            lh = draw.textbbox((0, 0), line, font=fnt)[3]
        except Exception:
            lh = fnt.size if hasattr(fnt, "size") else 42
        TY += lh + 10
    TY += 12

    # ▸ Gradient divider
    _gradient_line(bg, PAD, TY, TW, 2)
    draw = ImageDraw.Draw(bg)
    TY  += 20

    # ▸ Duration chip
    dur_txt = f"⏱  {duration}"
    f_dur   = _font(28)
    # Chip bg
    dur_w = _tw(draw, dur_txt, f_dur) + 24
    draw.rounded_rectangle([PAD, TY, PAD+dur_w, TY+40],
                            radius=8, fill=(*_TEAL, 40))
    draw.rounded_rectangle([PAD, TY, PAD+dur_w, TY+40],
                            radius=8, outline=(*_TEAL, 100), width=1)
    draw.text((PAD+12, TY+6), dur_txt, font=f_dur, fill=(*_TEAL, 240))

    # ▸ Requester
    req = _strip(requester)
    if req:
        draw.text(
            (PAD + dur_w + 20, TY + 9),
            f"▸  {req[:24]}",
            font=_font(21, bold=False),
            fill=(*_LAVENDER, 180),
        )

    # ▸ Waveform (bottom of card)
    WY = CARD[3] - 52
    _waveform(draw, PAD, WY, TW, seed)

    # ▸ Branding watermark
    brand   = "🎵 Muskan Music"
    f_br    = _font(21, bold=False)
    brand_w = _tw(draw, brand, f_br)
    bx      = PAD + (TW - brand_w) // 2
    # Subtle glow behind brand
    for gi in range(8, 0, -1):
        ga = int(20 * (gi / 8))
        draw.text((bx-gi//2, WY - 36 - gi//2), brand,
                  font=f_br, fill=(*_ROSE, ga))
    draw.text((bx, WY - 36), brand, font=f_br, fill=(*_ROSE, 210))

    # ── 10. Save ─────────────────────────────────────────────────────
    bg.convert("RGB").save(out, "JPEG", quality=96, optimize=True)
    return out
