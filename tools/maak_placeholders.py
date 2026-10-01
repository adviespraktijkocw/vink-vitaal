"""Maakt rustige placeholder-foto's in het Vink Vitaal palet.

Elke placeholder heeft een label dat zegt welke foto er later moet komen,
zodat de set meteen dienstdoet als shotlijst voor de fotograaf.

Gebruik:  python3 tools/maak_placeholders.py
"""
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HIER = os.path.dirname(os.path.abspath(__file__))
UIT = os.path.join(HIER, "..", "afbeeldingen")

CREME = (239, 241, 233)
GROEN = (108, 165, 77)
BLAUW = (40, 107, 174)
ORANJE = (225, 128, 48)
ANTRACIET = (70, 67, 71)


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def verloop(w, h, stops, richting="v"):
    """Lineair verloop door meerdere kleurstops [(pos, kleur), ...]."""
    n = h if richting == "v" else w
    lijn = np.zeros((n, 3))
    for i in range(n):
        p = i / max(n - 1, 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= p <= p1:
                t = (p - p0) / max(p1 - p0, 1e-6)
                lijn[i] = mix(c0, c1, t)
                break
    if richting == "v":
        arr = np.repeat(lijn[:, None, :], w, axis=1)
    else:
        arr = np.repeat(lijn[None, :, :], h, axis=0)
    return Image.fromarray(arr.astype("uint8"), "RGB")


def vlekken(img, kleuren, aantal, rmin, rmax, blur, alpha=150, seed=1):
    rnd = random.Random(seed)
    laag = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(laag)
    w, h = img.size
    for _ in range(aantal):
        r = rnd.randint(rmin, rmax)
        x, y = rnd.randint(-r // 2, w), rnd.randint(-r // 2, h)
        c = rnd.choice(kleuren)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (alpha,))
    laag = laag.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"), laag).convert("RGB")


def korrel(img, sterkte=7, seed=3):
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.int16)
    ruis = rng.normal(0, sterkte, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + ruis, 0, 255).astype("uint8"))


def lichtstralen(img, seed=2):
    rnd = random.Random(seed)
    w, h = img.size
    laag = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(laag)
    bron = (int(w * 0.78), -int(h * 0.2))
    for _ in range(9):
        x = rnd.randint(-w // 3, int(w * 0.9))
        breedte = rnd.randint(w // 30, w // 10)
        d.polygon([bron, (x, h), (x + breedte, h)], fill=(255, 236, 190, rnd.randint(40, 80)))
    laag = laag.filter(ImageFilter.GaussianBlur(w // 60))
    return Image.alpha_composite(img.convert("RGBA"), laag).convert("RGB")


def grassprieten(img, seed=4, hoogte=0.55):
    rnd = random.Random(seed)
    w, h = img.size
    laag = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(laag)
    for _ in range(int(w * 1.4)):
        x = rnd.randint(0, w)
        top = int(h * (1 - hoogte) + rnd.randint(-h // 10, h // 6))
        buig = rnd.randint(-w // 25, w // 25)
        kleur = rnd.choice([mix(GROEN, (210, 220, 150), 0.4), mix(GROEN, ANTRACIET, 0.25), (190, 200, 140), GROEN])
        d.line([(x, h), (x + buig // 2, (h + top) // 2), (x + buig, top)], fill=kleur + (rnd.randint(90, 200),), width=rnd.randint(1, 3))
    laag = laag.filter(ImageFilter.GaussianBlur(1.6))
    return Image.alpha_composite(img.convert("RGBA"), laag).convert("RGB")


def silhouet(img, cx, cy, schaal, kleur, blur=6, staand=True):
    """Abstract figuurtje (hoofd + schouders): leest als 'hier komt een persoon'."""
    w, h = img.size
    laag = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(laag)
    r = int(schaal * 0.13 * h)
    hx, hy = int(cx * w), int(cy * h)
    d.ellipse([hx - r, hy - int(r * 1.15), hx + r, hy + int(r * 1.15)], fill=kleur + (255,))
    # haar / volume rond het hoofd
    d.ellipse([hx - int(r * 1.25), hy - int(r * 1.35), hx + int(r * 1.25), hy + int(r * 0.9)], fill=mix(kleur, ANTRACIET, 0.35) + (190,))
    d.ellipse([hx - r, hy - int(r * 1.05), hx + r, hy + int(r * 1.2)], fill=kleur + (255,))
    sb = int(r * (3.4 if staand else 4.2))
    top = hy + int(r * 1.5)
    d.rounded_rectangle([hx - sb // 2, top, hx + sb // 2, top + int(r * 9)], radius=int(r * 1.4), fill=mix(kleur, CREME, 0.15) + (255,))
    d.rectangle([hx - int(r * 0.35), hy + int(r * 0.9), hx + int(r * 0.35), top + r], fill=kleur + (255,))
    laag = laag.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"), laag).convert("RGB")


def label(img, tekst):
    w, h = img.size
    grootte = max(14, int(min(w, h) * 0.026))
    font = ImageFont.truetype(os.path.join(HIER, "DMSans-Medium.ttf"), grootte)
    d = ImageDraw.Draw(img, "RGBA")
    regel = "FOTO  ·  " + tekst
    bb = d.textbbox((0, 0), regel, font=font)
    pad = int(grootte * 0.75)
    x0, y0 = int(grootte * 1.4), h - int(grootte * 1.4) - (bb[3] - bb[1]) - 2 * pad
    d.rounded_rectangle([x0, y0, x0 + bb[2] - bb[0] + 2 * pad, y0 + bb[3] - bb[1] + 2 * pad], radius=999, fill=CREME + (225,))
    d.text((x0 + pad - bb[0], y0 + pad - bb[1]), regel, font=font, fill=ANTRACIET)
    return img


def opslaan(img, naam, tekst):
    img.thumbnail((1600, 1600), Image.LANCZOS)
    img = korrel(img, sterkte=4)
    img = label(img, tekst)
    img.save(os.path.join(UIT, naam), "JPEG", quality=72, optimize=True, progressive=True)
    print("  ", naam, img.size)


def main():
    os.makedirs(UIT, exist_ok=True)
    salie = mix(CREME, GROEN, 0.28)
    blauwgrijs = mix(CREME, BLAUW, 0.22)
    zand = mix(CREME, ORANJE, 0.22)

    # 1. Hero portret (liggend): persoon links, rust rechts voor tekst
    img = verloop(1800, 1200, [(0, mix(blauwgrijs, CREME, 0.3)), (1, blauwgrijs)], "h")
    img = vlekken(img, [CREME, mix(blauwgrijs, BLAUW, 0.2)], 10, 180, 420, 160, 120)
    img = silhouet(img, 0.30, 0.34, 1.05, mix(blauwgrijs, ANTRACIET, 0.45), blur=10)
    opslaan(img, "vv-hero-portret.jpg", "Portret coach, zittend, natuurlijk licht, ruimte rechts")

    # 2. Portret staand (binnen)
    img = verloop(900, 1125, [(0, mix(zand, CREME, 0.4)), (1, zand)])
    img = vlekken(img, [CREME, mix(zand, ORANJE, 0.25)], 8, 120, 280, 90, 110, seed=5)
    img = silhouet(img, 0.5, 0.30, 1.0, mix(zand, ANTRACIET, 0.42), blur=8)
    opslaan(img, "vv-portret-staand.jpg", "Portret staand, warme glimlach")

    # 3. Portret buiten in het groen
    img = verloop(900, 1125, [(0, (214, 226, 214)), (0.55, salie), (1, mix(GROEN, ANTRACIET, 0.2))])
    img = vlekken(img, [mix(GROEN, CREME, 0.5), (226, 214, 160)], 14, 60, 200, 60, 120, seed=6)
    img = silhouet(img, 0.52, 0.32, 1.0, mix(salie, ANTRACIET, 0.5), blur=8)
    opslaan(img, "vv-portret-buiten.jpg", "Portret buiten in het groen")

    # 4. Sfeer: zonlicht door het bos
    img = verloop(1920, 1080, [(0, (231, 214, 168)), (0.45, (170, 156, 98)), (1, (78, 86, 52))])
    img = vlekken(img, [(110, 128, 64), (60, 72, 40), (200, 170, 100)], 22, 80, 260, 70, 140, seed=7)
    img = lichtstralen(img)
    opslaan(img, "vv-sfeer-bos.jpg", "Sfeer: zonlicht door de bomen")

    # 5. Sfeer: wuivend gras / veld met lucht
    img = verloop(1920, 1080, [(0, (200, 218, 228)), (0.42, (226, 232, 220)), (0.5, (176, 196, 140)), (1, mix(GROEN, ANTRACIET, 0.3))])
    img = vlekken(img, [(240, 244, 246)], 6, 160, 380, 120, 120, seed=8)
    img = grassprieten(img)
    opslaan(img, "vv-sfeer-gras.jpg", "Sfeer: veld met wuivend gras")

    # 6. Sfeer: warm detail (thee, notitieboek, licht)
    img = verloop(1200, 1500, [(0, mix(CREME, ORANJE, 0.12)), (1, mix(zand, ORANJE, 0.25))])
    img = vlekken(img, [(255, 240, 210), mix(ORANJE, CREME, 0.4)], 14, 60, 220, 50, 150, seed=9)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([300, 520, 900, 1240], radius=26, fill=(250, 248, 240, 230))
    d.ellipse([760, 330, 1040, 610], fill=mix(zand, ANTRACIET, 0.15) + (210,))
    img = img.filter(ImageFilter.GaussianBlur(5))
    opslaan(img, "vv-sfeer-detail.jpg", "Detail: thee, notitieboek, ochtendlicht")

    # 7. Coachgesprek aan tafel
    img = verloop(1500, 1125, [(0, mix(CREME, blauwgrijs, 0.5)), (1, mix(blauwgrijs, CREME, 0.2))], "h")
    img = vlekken(img, [CREME, (255, 255, 255)], 6, 160, 300, 120, 120, seed=10)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([-50, 760, 1550, 1200], radius=40, fill=mix(zand, ANTRACIET, 0.1) + (255,))
    img = silhouet(img, 0.28, 0.33, 0.95, mix(blauwgrijs, ANTRACIET, 0.45), blur=9)
    img = silhouet(img, 0.72, 0.36, 0.9, mix(salie, ANTRACIET, 0.45), blur=9)
    opslaan(img, "vv-werk-gesprek.jpg", "Coachgesprek aan tafel, twee personen")

    # 8. Teamsessie
    img = verloop(1500, 1125, [(0, mix(salie, CREME, 0.5)), (1, salie)])
    img = vlekken(img, [CREME], 6, 160, 300, 120, 120, seed=11)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([-50, 800, 1550, 1200], radius=40, fill=mix(zand, ANTRACIET, 0.12) + (255,))
    for x, k in [(0.18, blauwgrijs), (0.42, zand), (0.64, salie), (0.86, blauwgrijs)]:
        img = silhouet(img, x, 0.40, 0.72, mix(k, ANTRACIET, 0.45), blur=8)
    opslaan(img, "vv-werk-team.jpg", "Teamsessie / workshop")

    # 9. Hero natuur (persoon wandelt door het veld)
    img = verloop(2000, 1200, [(0, (214, 222, 214)), (0.45, (232, 228, 206)), (0.52, (168, 178, 120)), (1, (70, 82, 48))])
    img = vlekken(img, [(120, 136, 80), (96, 110, 60)], 18, 60, 200, 80, 150, seed=12)
    img = grassprieten(img, seed=13, hoogte=0.5)
    img = silhouet(img, 0.80, 0.44, 0.5, (228, 224, 210), blur=6)
    opslaan(img, "vv-hero-natuur.jpg", "Coach wandelt door een veld, zon in de rug")


if __name__ == "__main__":
    main()
