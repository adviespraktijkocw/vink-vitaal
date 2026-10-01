"""Bouwt de drie Vink Vitaal landingspagina-templates.

Uit één beschrijving per template maakt dit script:
  1. divi/<naam>.json        -> importeren in de Divi Visual Builder
  2. preview/<naam>.html     -> voorbeeld in de browser (zelfde CSS-klassen)

Gebruik:  python3 tools/build.py
"""
import base64
import html
import json
import os
import re
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HIER, ".."))
BUILDER_VERSION = "4.27.4"

# Placeholders staan in deze (publieke) repo. Divi uploadt ze bij het
# importeren naar je Mediabibliotheek; mocht dat niet lukken, dan laadt de
# pagina ze rechtstreeks van GitHub tot je eigen foto's erin zet.
BRANCH = "claude/zen-keller-5e4p6m"
IMG_BASE = f"https://raw.githubusercontent.com/adviespraktijkocw/vink-vitaal/refs/heads/{BRANCH}/afbeeldingen/"

KLEUR = {
    "creme": "#EFF1E9",
    "creme_licht": "#F7F8F3",
    "salie_licht": "#DFE8D6",
    "salie": "#CEDEC2",
    "blauw_zacht": "#C7D6DD",
    "hemel": "#DBE4E3",
    "zand": "#ECDAC4",
}


def img(naam):
    return IMG_BASE + naam


# ---------------------------------------------------------------------------
# Bouwstenen
# ---------------------------------------------------------------------------

ANIM = {
    "animation_style": "slide",
    "animation_direction": "bottom",
    "animation_intensity_slide": "6%",
    "animation_duration": "900ms",
    "animation_speed_curve": "ease-out",
    "animation_starting_opacity": "0%",
}


class Module:
    kind = ""

    def __init__(self, cls="", anim=True, center=False, margin=None, **extra):
        self.cls = cls
        self.anim = anim
        self.center = center
        self.margin = margin  # (top, bottom) in px
        self.extra = extra


class Text(Module):
    kind = "text"

    def __init__(self, inhoud, **kw):
        super().__init__(**kw)
        self.inhoud = inhoud.strip()


class Button(Module):
    kind = "button"

    def __init__(self, tekst, url="#", align="left", variant="", **kw):
        kw.setdefault("anim", True)
        cls = "vv-btn" + "".join(f" vv-btn--{v}" for v in variant.split() if v)
        super().__init__(cls=cls, **kw)
        self.tekst, self.url, self.align = tekst, url, align


class Image(Module):
    kind = "image"

    def __init__(self, src, alt, **kw):
        super().__init__(**kw)
        self.src, self.alt = src, alt


class Code(Module):
    kind = "code"

    def __init__(self, inhoud, **kw):
        kw.setdefault("anim", False)
        super().__init__(**kw)
        self.inhoud = re.sub(r"\s*\n\s*", "", inhoud.strip())


class Toggle(Module):
    kind = "toggle"

    def __init__(self, titel, inhoud, **kw):
        super().__init__(**kw)
        self.titel, self.inhoud = titel, inhoud.strip()


class Col:
    def __init__(self, type_, modules, cls="", bg=None, bg_img=None, padding=None, padding_phone=None):
        self.type, self.modules, self.cls = type_, modules, cls
        self.bg, self.bg_img, self.padding, self.padding_phone = bg, bg_img, padding, padding_phone


class Row:
    def __init__(self, cols, cls="", width="88%", max_width="1240px", gutter=3, equal=False, padding=(0, 0)):
        self.cols, self.cls, self.width, self.max_width = cols, cls, width, max_width
        self.gutter, self.equal, self.padding = gutter, equal, padding


class Section:
    def __init__(self, rows, cls="", bg=KLEUR["creme"], bg_img=None, padding=(100, 100), padding_phone=None, admin=""):
        self.rows, self.cls, self.bg, self.bg_img = rows, cls, bg, bg_img
        self.padding = padding
        self.padding_phone = padding_phone or (min(padding[0], 64), min(padding[1], 64))
        self.admin = admin


def kol(structuur, *modulelijsten, **kw):
    """Hulpje: Row met kolommen in één keer. structuur = '1_2,1_2'."""
    types = structuur.split(",")
    colkw = kw.pop("cols", [{}] * len(types))
    return Row([Col(t, m, **ck) for t, m, ck in zip(types, modulelijsten, colkw)], **kw)


# ---------------------------------------------------------------------------
# Divi-shortcodes
# ---------------------------------------------------------------------------

def pad(t, b, r="", l=""):
    return f"{t}px|{r}|{b}px|{l}|false|false"


def attrs(d):
    out = []
    for k, v in d.items():
        if v is None or v == "":
            continue
        v = str(v).replace('"', "%22").replace("[", "%91").replace("]", "%93")
        out.append(f'{k}="{v}"')
    return " ".join(out)


def base_attrs(m):
    d = {"_builder_version": BUILDER_VERSION, "_module_preset": "default"}
    if m.cls:
        d["module_class"] = m.cls
    if m.margin:
        d["custom_margin"] = f"{m.margin[0]}px||{m.margin[1]}px||false|false"
    if m.anim:
        d.update(ANIM)
    return d


def sc_module(m):
    d = base_attrs(m)
    if m.kind == "text":
        if m.center:
            d["text_orientation"] = "center"
        d["global_colors_info"] = "{}"
        return f"[et_pb_text {attrs(d)}]{m.inhoud}[/et_pb_text]"
    if m.kind == "button":
        d = {"button_url": m.url, "button_text": m.tekst, "button_alignment": m.align,
             "button_use_icon": "off", **d, "global_colors_info": "{}"}
        return f"[et_pb_button {attrs(d)}][/et_pb_button]"
    if m.kind == "image":
        d = {"src": m.src, "alt": m.alt, "title_text": m.alt, "force_fullwidth": "on",
             "show_bottom_space": "off", **d, "global_colors_info": "{}"}
        return f"[et_pb_image {attrs(d)}][/et_pb_image]"
    if m.kind == "code":
        d["global_colors_info"] = "{}"
        return f"[et_pb_code {attrs(d)}]{m.inhoud}[/et_pb_code]"
    if m.kind == "toggle":
        d = {"title": m.titel, "open": "off", **d, "global_colors_info": "{}"}
        return f"[et_pb_toggle {attrs(d)}]{m.inhoud}[/et_pb_toggle]"
    raise ValueError(m.kind)


def sc_section(s):
    d = {"fb_built": "1", "admin_label": s.admin, "module_class": f"vv {s.cls}".strip(),
         "_builder_version": BUILDER_VERSION, "_module_preset": "default",
         "background_color": s.bg}
    if s.bg_img:
        d.update({"background_image": s.bg_img, "background_size": "cover", "background_position": "center"})
    d["custom_padding"] = pad(*s.padding)
    d["custom_padding_tablet"] = ""
    d["custom_padding_phone"] = pad(*s.padding_phone)
    d["custom_padding_last_edited"] = "on|phone"
    d["global_colors_info"] = "{}"
    out = [f"[et_pb_section {attrs(d)}]"]
    for r in s.rows:
        rd = {"column_structure": ",".join(c.type for c in r.cols),
              "use_custom_gutter": "on" if r.gutter != 3 else "",
              "gutter_width": str(r.gutter) if r.gutter != 3 else "",
              "make_equal": "on" if r.equal else "",
              "module_class": r.cls,
              "_builder_version": BUILDER_VERSION, "_module_preset": "default",
              "width": r.width, "max_width": r.max_width,
              "custom_padding": pad(*r.padding),
              "global_colors_info": "{}"}
        out.append(f"[et_pb_row {attrs(rd)}]")
        for c in r.cols:
            cd = {"type": c.type, "_builder_version": BUILDER_VERSION, "_module_preset": "default",
                  "module_class": c.cls, "background_color": c.bg}
            if c.bg_img:
                cd.update({"background_image": c.bg_img, "background_size": "cover", "background_position": "center"})
            if c.padding:
                cd["custom_padding"] = pad(*c.padding)
                if c.padding_phone:
                    cd["custom_padding_phone"] = pad(*c.padding_phone)
                    cd["custom_padding_last_edited"] = "on|phone"
            cd["global_colors_info"] = "{}"
            out.append(f"[et_pb_column {attrs(cd)}]")
            out.extend(sc_module(m) for m in c.modules)
            out.append("[/et_pb_column]")
        out.append("[/et_pb_row]")
    out.append("[/et_pb_section]")
    return "".join(out)


def divi_json(secties, gebruikte_beelden):
    content = "".join(sc_section(s) for s in secties)
    images = {}
    for naam in sorted(gebruikte_beelden):
        with open(os.path.join(ROOT, "afbeeldingen", naam), "rb") as f:
            images[img(naam)] = {"encoded": base64.b64encode(f.read()).decode(), "url": img(naam)}
    return {"context": "et_builder", "data": {"1": content}, "presets": {},
            "global_colors": [], "images": images, "thumbnails": {}}


# ---------------------------------------------------------------------------
# Preview-HTML (zelfde klassen als Divi uitvoert)
# ---------------------------------------------------------------------------

class Teller:
    def __init__(self):
        self.n = defaultdict(int)

    def __call__(self, soort):
        i = self.n[soort]
        self.n[soort] += 1
        return f"{soort}_{i}"


def css_pad(p):
    return f"padding-top:{p[0]}px;padding-bottom:{p[1]}px;" + (f"padding-right:{p[2]};padding-left:{p[3]};" if len(p) > 2 else "")


def html_module(m, t, extra_css):
    anim = ' data-vv-anim' if m.anim else ""
    cls = f" {m.cls}" if m.cls else ""
    if m.kind == "text":
        id_ = t("et_pb_text")
        align = "center" if m.center else "left"
        if m.margin:
            extra_css.append(f".{id_}{{margin-top:{m.margin[0]}px!important;margin-bottom:{m.margin[1]}px!important}}")
        return (f'<div class="et_pb_module et_pb_text {id_} et_pb_text_align_{align} et_pb_bg_layout_light{cls}"{anim}>'
                f'<div class="et_pb_text_inner">{m.inhoud}</div></div>')
    if m.kind == "button":
        id_ = t("et_pb_button")
        if m.margin:
            extra_css.append(f".{id_}_wrapper{{margin-top:{m.margin[0]}px!important;margin-bottom:{m.margin[1]}px!important}}")
        return (f'<div class="et_pb_button_module_wrapper {id_}_wrapper et_pb_button_alignment_{m.align} et_pb_module"{anim}>'
                f'<a class="et_pb_button {id_}{cls} et_pb_bg_layout_light" href="{html.escape(m.url)}">{html.escape(m.tekst)}</a></div>')
    if m.kind == "image":
        id_ = t("et_pb_image")
        extra_css.append(f".{id_} .et_pb_image_wrap,.{id_} img{{width:100%}}")
        if m.margin:
            extra_css.append(f".{id_}{{margin-top:{m.margin[0]}px!important;margin-bottom:{m.margin[1]}px!important}}")
        src = "../afbeeldingen/" + m.src.rsplit("/", 1)[1]
        return (f'<div class="et_pb_module et_pb_image {id_}{cls}"{anim}><span class="et_pb_image_wrap">'
                f'<img src="{src}" alt="{html.escape(m.alt)}"></span></div>')
    if m.kind == "code":
        id_ = t("et_pb_code")
        if m.margin:
            extra_css.append(f".{id_}{{margin-top:{m.margin[0]}px!important;margin-bottom:{m.margin[1]}px!important}}")
        return f'<div class="et_pb_module et_pb_code {id_}{cls}"><div class="et_pb_code_inner">{m.inhoud}</div></div>'
    if m.kind == "toggle":
        id_ = t("et_pb_toggle")
        return (f'<div class="et_pb_module et_pb_toggle {id_} et_pb_toggle_item et_pb_toggle_close{cls}"{anim}>'
                f'<h5 class="et_pb_toggle_title">{html.escape(m.titel)}</h5>'
                f'<div class="et_pb_toggle_content clearfix">{m.inhoud}</div></div>')
    raise ValueError(m.kind)


def preview_url(u):
    return "../afbeeldingen/" + u.rsplit("/", 1)[1]


def html_sections(secties):
    t = Teller()
    extra = []
    out = []
    for s in secties:
        sid = t("et_pb_section")
        st = f"background-color:{s.bg};"
        if s.bg_img:
            st += f"background-image:url({preview_url(s.bg_img)});background-size:cover;background-position:center;"
        extra.append(f".{sid}{{{css_pad(s.padding)}}}")
        extra.append(f"@media (max-width:767px){{.{sid}{{{css_pad(s.padding_phone)}}}}}")
        out.append(f'<div class="et_pb_section {sid} vv {s.cls} et_section_regular" style="{st}">')
        for r in s.rows:
            rid = t("et_pb_row")
            extra.append(f".{rid}{{width:{r.width};max-width:{r.max_width};{css_pad(r.padding)}}}")
            rcls = f"et_pb_row {rid} et_pb_gutters{r.gutter}"
            if r.equal:
                rcls += " et_pb_equal_columns"
            if r.cls:
                rcls += " " + r.cls
            out.append(f'<div class="{rcls}">')
            for i, c in enumerate(r.cols):
                cid = t("et_pb_column")
                st = ""
                if c.bg:
                    st += f"background-color:{c.bg};"
                if c.bg_img:
                    st += f"background-image:url({preview_url(c.bg_img)});background-size:cover;background-position:center;"
                if c.padding:
                    p = c.padding
                    extra.append(f".{cid}{{padding:{p[0]}px {p[2] or 0} {p[1]}px {p[3] or 0}}}")
                    if c.padding_phone:
                        pp = c.padding_phone
                        extra.append(f"@media (max-width:767px){{.{cid}{{padding:{pp[0]}px {pp[2] or 0} {pp[1]}px {pp[3] or 0}}}}}")
                last = " et-last-child" if i == len(r.cols) - 1 else ""
                ccls = f"et_pb_column et_pb_column_{c.type} {cid}{last}" + (f" {c.cls}" if c.cls else "")
                out.append(f'<div class="{ccls}" style="{st}">')
                out.extend(html_module(m, t, extra) for m in c.modules)
                out.append("</div>")
            out.append("</div>")
        out.append("</div>")
    return "\n".join(out), "\n".join(extra)


def preview_html(titel, secties, fonts_head):
    body, extra = html_sections(secties)
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titel)}</title>
{fonts_head}
<link rel="stylesheet" href="divi-shim.css">
<link rel="stylesheet" href="../divi/vink-vitaal.css">
<style>
{extra}
</style>
</head>
<body>
<div id="page-container"><div id="et-main-area"><div id="main-content"><div class="et-l et-l--post"><div class="et_builder_inner_content">
{body}
</div></div></div></div></div>
<script src="divi-shim.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Gedeelde stukjes
# ---------------------------------------------------------------------------

def band(woorden, variant=""):
    spans = "".join(f"<span>{w}</span>" for w in woorden) * 2
    return Code(f'<div class="vv-band {variant}" aria-hidden="true"><div class="vv-band__spoor">{spans}</div></div>')


def citaat(initialen, kop, tekst, naam):
    return Text(f'<span class="vv-initialen">{initialen}</span><h3>{kop}</h3><p>{tekst}</p><h5>— {naam}</h5>',
                cls="vv-citaat")


def ul(*items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


LOGO = Image(img("vv-logo.png"), "Vink Vitaal", cls="vv-logo", anim=False)


# ---------------------------------------------------------------------------
# TEMPLATE 1 — GROEI   (opzet: Astrid Jade + Molly Atkins)
# ---------------------------------------------------------------------------

def template_groei():
    return [
        Section(admin="Topbalk", bg=KLEUR["hemel"], padding=(22, 0), padding_phone=(16, 0), rows=[
            kol("1_4,1_2,1_4",
                [LOGO],
                [Text('<p><a href="#">Over mij</a><a href="#">Aanbod</a><a href="#">Ervaringen</a><a href="#">Blog</a></p>',
                      cls="vv-menu", center=True, anim=False)],
                [Button("Plan een kennismaking", align="right", variant="klein lijn", anim=False)],
                cls="vv-midden", width="92%", max_width="1360px"),
        ]),
        Section(admin="Hero", bg=KLEUR["hemel"], padding=(40, 110), padding_phone=(20, 64), rows=[
            kol("1_2,1_2",
                [Image(img("vv-hero-portret.jpg"), "Portret van de coach van Vink Vitaal", cls="vv-beeld vv-beeld--hero")],
                [Text("""
<h4>Vitaal Leiderschap</h4>
<h1>Vitaal <em>leiden</em> begint bij <em>jezelf</em></h1>
<p>Voor leidinggevenden en ondernemers die veel ballen hooghouden en merken dat hun energie opraakt. Samen bouwen we aan rust in je hoofd, ruimte in je agenda en plezier in je werk.</p>
""", cls="vv-hoofdletters vv-intro vv-smal"),
                 Button("Start jouw traject →")],
                cls="vv-midden", width="88%", max_width="1240px"),
        ]),
        Section(admin="Lopende band", bg=KLEUR["creme_licht"], cls="vv-lijnen", padding=(20, 20), padding_phone=(16, 16), rows=[
            kol("4_4", [band(["Vitaal leiderschap", "Meer energie", "Rust in je hoofd", "Leiden vanuit jezelf", "Balans in werk en leven"])],
                width="100%", max_width="100%"),
        ]),
        Section(admin="Intro", bg=KLEUR["creme"], cls="vv-overflow", padding=(120, 130), rows=[
            kol("4_4", [Text("""
<h2>Ik help <em>leidinggevenden</em> om met <span class="vv-cirkel">energie</span> en rust te leiden, <em>zonder zichzelf te verliezen.</em></h2>
""", cls="vv-statement", center=True)], max_width="980px", padding=(0, 70)),
            kol("1_2,1_2",
                [Image(img("vv-sfeer-detail.jpg"), "Sfeerbeeld: thee en notitieboek", cls="vv-beeld vv-beeld--vierkant vv-zweef vv-zweef--lb"),
                 Image(img("vv-portret-staand.jpg"), "Portret van de coach", cls="vv-beeld vv-beeld--staand")],
                [Text("""
<p>Je bent er niet om alleen maar te overleven tussen de vergaderingen door. Je wilt leidinggeven op een manier die klopt: met aandacht voor je mensen én voor jezelf.</p>
<p>Bij Vink Vitaal werken we aan wat jou energie geeft en wat je energie kost. We combineren praktische inzichten over vitaliteit met coaching op jouw rol als leider.</p>
<p><strong>De kern: goed leiderschap hoeft niet zwaar te voelen.</strong> Je hoeft niet harder te werken, je hebt richting, rust en een aanpak nodig die bij jou past.</p>
"""),
                 Button("Start jouw traject →", margin=(30, 0)),
                 Image(img("vv-sfeer-gras.jpg"), "Sfeerbeeld: veld met gras", cls="vv-beeld vv-beeld--vierkant vv-zweef vv-zweef--rb")],
                cls="vv-midden", max_width="1000px"),
        ]),
        Section(admin="Start jouw traject (grote letters)", bg=KLEUR["creme"], cls="vv-overflow", padding=(0, 0), padding_phone=(0, 0), rows=[
            kol("4_4", [Text("<h2>Start <em>jouw</em> traject</h2>", cls="vv-reuze", center=True, margin=(0, -6))],
                width="100%", max_width="100%"),
        ]),
        Section(admin="Aanbod (2 kaarten op foto)", bg=KLEUR["creme"], padding=(0, 0), padding_phone=(0, 0), rows=[
            Row([
                Col("1_2", [Text("""
<h4>1-op-1</h4>
<h3>Persoonlijke <em>coaching</em></h3>
<p>Een traject helemaal rond jou. We brengen in kaart waar je energie heen lekt, maken keuzes die rust geven en zetten stappen die je direct merkt, op je werk en thuis.</p>
""", cls="vv-kaart"), Button("Plan een kennismaking →", align="center", variant="lijn", anim=False)],
                    bg_img=img("vv-sfeer-gras.jpg"), bg=KLEUR["salie"], padding=(110, 110, "12%", "12%"), padding_phone=(56, 56, "6%", "6%")),
                Col("1_2", [Text("""
<h4>Groepsprogramma</h4>
<h3>Vitaal <em>Leiderschap</em></h3>
<p>Een programma voor leidinggevenden die samen willen groeien. Met kennis over energie en herstel, intervisie met gelijkgestemden en tijd om te oefenen in de praktijk.</p>
""", cls="vv-kaart"), Button("Bekijk het programma →", align="center", variant="lijn", anim=False)],
                    bg_img=img("vv-sfeer-bos.jpg"), bg=KLEUR["zand"], padding=(110, 110, "12%", "12%"), padding_phone=(56, 56, "6%", "6%")),
            ], width="100%", max_width="100%", gutter=1, equal=True),
        ]),
        Section(admin="Ervaringen", bg=KLEUR["salie"], padding=(110, 110), rows=[
            kol("4_4", [Text("<h4>Ervaringen</h4><h2>Wat klanten <em>ervaren</em></h2>", center=True)], padding=(0, 40)),
            kol("1_3,1_3,1_3",
                [citaat("A", "“Ik weet weer waar ik naartoe wil, en het voelt licht.”",
                        "Ik liep vast in een agenda vol verwachtingen. Nu kies ik bewuster en heb ik ’s avonds weer energie over.", "Naam klant, teamleider")],
                [citaat("B", "“Ik ben gestopt met duwen. Alles kwam in beweging.”",
                        "Ik dacht dat harder werken de oplossing was. Ik leerde mijn grenzen voelen en mijn team meer vertrouwen.", "Naam klant, manager")],
                [citaat("C", "“Ik leid weer vanuit rust in plaats van vanuit stress.”",
                        "Praktisch, warm en eerlijk. Ik merk het verschil in mijn gesprekken, mijn slaap en mijn plezier in het werk.", "Naam klant, directeur")],
                cls="vv-gelijk", equal=True),
            kol("4_4", [Button("Lees alle ervaringen", align="center", variant="lijn")], padding=(40, 0)),
        ]),
        Section(admin="Jouw verandering", bg=KLEUR["creme"], padding=(0, 0), padding_phone=(0, 0), rows=[
            Row([
                Col("1_2", [Image(img("vv-werk-gesprek.jpg"), "Coachgesprek aan tafel", cls="vv-beeld vv-beeld--liggend")],
                    bg=KLEUR["blauw_zacht"], cls="vv-kolom-midden", padding=(100, 100, "12%", "12%"), padding_phone=(48, 48, "6%", "6%")),
                Col("1_2", [Text(f"""
<h4>Het traject</h4>
<h2>Van <em>overleven</em> naar vitaal leiden</h2>
<p>In een traject bij Vink Vitaal ga je van rennen op reserve naar leidinggeven met energie, focus en vertrouwen.</p>
<div class="vv-vinklijst">{ul("Je weet wat je energie geeft en wat het kost", "Je maakt keuzes die passen bij wie je bent", "Je team merkt het verschil in jouw rust")}</div>
"""), Button("Plan een kennismaking →")],
                    cls="vv-kolom-midden", padding=(100, 100, "10%", "10%"), padding_phone=(56, 56, "6%", "6%")),
            ], width="100%", max_width="100%", gutter=1, equal=True),
        ]),
        Section(admin="Afsluitende oproep", bg=KLEUR["zand"], padding=(120, 120), rows=[
            kol("4_4", [
                Text("<h4>Kennismaken</h4><h2>Klaar voor meer <em>rust</em> en <em>energie</em>?</h2><p>Plan een vrijblijvend gesprek. We kijken samen waar je nu staat en wat jou verder helpt.</p>",
                     center=True),
                Button("Plan een kennismaking →", align="center", margin=(30, 18)),
                Text("<p>Gratis · 30 minuten · online of in de praktijk</p>", cls="vv-noot", center=True),
            ], max_width="760px"),
        ]),
    ]


# ---------------------------------------------------------------------------
# TEMPLATE 2 — NATUUR   (opzet: Etta's Acres)
# ---------------------------------------------------------------------------

def template_natuur():
    return [
        Section(admin="Hero met natuurfoto", bg="#5C6B45", bg_img=img("vv-hero-natuur.jpg"), cls="vv-hero-vol vv-overlay",
                padding=(130, 110), padding_phone=(110, 80), rows=[
            kol("1_3,1_3,1_3",
                [Text('<p><a href="#">Over mij</a><a href="#">Aanbod</a></p>', cls="vv-menu vv-op-foto", anim=False)],
                [Text("<p>Vink Vitaal</p>", cls="vv-merknaam vv-op-foto", center=True, anim=False)],
                [Text('<p style="text-align:right"><a href="#">Blog</a><a href="#">Contact</a></p>', cls="vv-menu vv-op-foto", anim=False)],
                cls="vv-topbalk vv-midden", width="92%", max_width="1360px", padding=(28, 28)),
            kol("4_4", [
                Text("""
<h4>Vitaal Leiderschap</h4>
<h1>Energie, rust &amp; richting</h1>
<p class="vv-hand">voor wie leiding geeft</p>
<p>Coaching voor leidinggevenden die weer willen leiden vanuit hun kracht, met een frisse blik en een rustig hoofd.</p>
""", cls="vv-op-foto vv-hoofdletters vv-smal", center=True),
                Button("Ontdek meer ↓", url="#welkom", align="center", variant="licht", margin=(26, 0)),
            ], max_width="900px"),
        ]),
        Section(admin="Welkom / over mij", bg=KLEUR["creme"], padding=(120, 120), rows=[
            kol("1_4,1_2,1_4",
                [Code('<div class="vv-badge" aria-hidden="true"></div>', cls="vv-badge-wrap"),
                 Image(img("vv-portret-buiten.jpg"), "Portret van de coach buiten", cls="vv-beeld vv-beeld--staand")],
                [Text("""
<p class="vv-hand">Welkom!</p>
<h2>Hoi, ik ben [Naam]</h2>
<p>Coach, ervaringsdeskundige en liefhebber van lange wandelingen. Ik neem je mee in wat ik zelf heb geleerd: dat je pas echt goed voor anderen kunt zorgen als je ook goed voor jezelf zorgt.</p>
""", cls="vv-hoofdletters vv-groen-kop", center=True),
                 Button("Mijn verhaal", align="center", variant="warm", margin=(24, 0))],
                [Image(img("vv-portret-staand.jpg"), "Portret van de coach", cls="vv-beeld vv-beeld--staand vv-omlaag")],
                cls="vv-midden", width="92%", max_width="1300px", gutter=4),
        ]),
        Section(admin="Natuurbeeld met handgeschreven zin", bg=KLEUR["salie"], bg_img=img("vv-sfeer-gras.jpg"), cls="vv-hoog",
                padding=(80, 300), padding_phone=(56, 200), rows=[
            kol("1_2,1_2",
                [Text("<p>Ik geloof in leiden vanuit rust, in terug naar de basis, en in anderen helpen hetzelfde te doen.</p>", cls="vv-hand-groot")],
                [],
                width="90%", max_width="1300px"),
        ]),
        Section(admin="Grote lopende band", bg=KLEUR["creme"], cls="vv-lijnen", padding=(26, 26), padding_phone=(18, 18), rows=[
            kol("4_4", [band(["Vitaliteit", "Leiderschap", "Balans", "Energie", "Rust"], "vv-band--groot")], width="100%", max_width="100%"),
        ]),
        Section(admin="Aanbod", bg=KLEUR["creme"], padding=(110, 120), rows=[
            kol("4_4", [Text('<p class="vv-hand">Zo kan ik je helpen</p><h2>Mijn aanbod</h2>', cls="vv-hoofdletters", center=True)], padding=(0, 50)),
            kol("1_3,1_3,1_3",
                [Image(img("vv-werk-gesprek.jpg"), "Coachgesprek", cls="vv-beeld vv-beeld--boog"),
                 Text('<h3>1-op-1 coaching</h3><p>Persoonlijke begeleiding in jouw tempo, gericht op energie, grenzen en keuzes die kloppen.</p><p class="vv-meer"><a href="#">Meer weten</a></p>', cls="vv-dienst", center=True, margin=(26, 0))],
                [Image(img("vv-werk-team.jpg"), "Teamsessie", cls="vv-beeld vv-beeld--boog"),
                 Text('<h3>Vitaal Leiderschap</h3><p>Het groepsprogramma voor leidinggevenden. Leren, delen en oefenen met gelijkgestemden.</p><p class="vv-meer"><a href="#">Bekijk het programma</a></p>', cls="vv-dienst", center=True, margin=(26, 0))],
                [Image(img("vv-sfeer-bos.jpg"), "Sfeerbeeld bos", cls="vv-beeld vv-beeld--boog"),
                 Text('<h3>Workshops &amp; lezingen</h3><p>Inspirerende sessies voor teams en organisaties over vitaliteit, werkplezier en duurzaam presteren.</p><p class="vv-meer"><a href="#">Vraag een workshop aan</a></p>', cls="vv-dienst", center=True, margin=(26, 0))],
                gutter=4),
        ]),
        Section(admin="Ervaring (groot citaat)", bg=KLEUR["salie_licht"], padding=(120, 120), rows=[
            kol("4_4", [Text("""
<p>“Ik kwam binnen met een volle agenda en een leeg gevoel. Nu kies ik weer bewust, en mijn team merkt het ook.”</p>
<p class="vv-hand">Naam klant, teamleider</p>
""", cls="vv-groot-citaat", center=True)], max_width="900px"),
        ]),
        Section(admin="Werkwijze", bg=KLEUR["creme"], padding=(110, 110), rows=[
            kol("4_4", [Text("<h4>Zo werkt het</h4><h2>In drie stappen naar meer <em>vitaliteit</em></h2>", center=True)], max_width="900px", padding=(0, 50)),
            kol("1_3,1_3,1_3",
                [Text('<span class="vv-nummer">01</span><h3>Kennismaken</h3><p>We bespreken waar je staat en wat je nodig hebt. Gratis en vrijblijvend.</p>', cls="vv-stap")],
                [Text('<span class="vv-nummer">02</span><h3>Traject op maat</h3><p>Een plan dat past bij jouw rol, jouw tempo en jouw doelen.</p>', cls="vv-stap")],
                [Text('<span class="vv-nummer">03</span><h3>Vitaal verder</h3><p>Je neemt nieuwe gewoontes mee die blijven werken, ook als het druk wordt.</p>', cls="vv-stap")]),
        ]),
        Section(admin="Gratis gids", bg=KLEUR["creme"], padding=(0, 0), padding_phone=(0, 0), rows=[
            Row([
                Col("1_2", [], bg=KLEUR["zand"], bg_img=img("vv-sfeer-detail.jpg"), cls="vv-beeldkolom"),
                Col("1_2", [Text("""
<p class="vv-hand">Gratis</p>
<h2>5 vitaliteitstips voor drukke leiders</h2>
<p>Kleine stappen met groot effect. Ontvang de gids in je mailbox en begin vandaag nog.</p>
"""), Button("Download de gids →", variant="warm", margin=(24, 14)),
                    Text("<p>Geen spam. Afmelden kan altijd.</p>", cls="vv-noot")],
                    bg=KLEUR["salie"], padding=(110, 110, "10%", "10%"), padding_phone=(56, 56, "6%", "6%")),
            ], width="100%", max_width="100%", gutter=1, equal=True),
        ]),
    ]


# ---------------------------------------------------------------------------
# TEMPLATE 3 — RUST   (opzet: August + video-optie zoals evaredpath)
# ---------------------------------------------------------------------------

def template_rust():
    return [
        Section(admin="Hero (foto of video)", bg="#5B5A3E", bg_img=img("vv-sfeer-bos.jpg"), cls="vv-hero-vol vv-overlay",
                padding=(130, 110), padding_phone=(120, 80), rows=[
            kol("1_3,1_3,1_3",
                [Text('<p><a href="#">Aanbod</a><a href="#">Blog</a><a href="#">Over mij</a></p>', cls="vv-menu vv-op-foto", anim=False)],
                [Text("<p>Vink Vitaal</p>", cls="vv-merknaam vv-op-foto", center=True, anim=False)],
                [Button("Plan kennismaking", align="right", variant="klein lijn-licht recht", anim=False)],
                cls="vv-topbalk vv-topbalk--lijn vv-midden", width="92%", max_width="1360px", padding=(24, 24)),
            kol("4_4", [
                Text("""
<h1>Voel je weer <em>als jezelf</em>, ook als leider</h1>
<p>Coaching voor leidinggevenden die willen leiden vanuit rust, energie en vertrouwen.</p>
""", cls="vv-op-foto", center=True),
                Button("Plan een kennismaking", align="center", variant="licht recht", margin=(28, 0)),
            ], max_width="880px"),
        ]),
        Section(admin="Lopende band", bg=KLEUR["creme"], cls="vv-lijnen", padding=(20, 20), padding_phone=(16, 16), rows=[
            kol("4_4", [band(["Leiden vanuit rust"] * 5)], width="100%", max_width="100%"),
        ]),
        Section(admin="Kernboodschap", bg=KLEUR["salie_licht"], padding=(130, 130), rows=[
            kol("4_4", [Text("<h2>Vitaliteit is geen extra taak op je lijst. Het is de basis waar goed leiderschap op rust.</h2>",
                             cls="vv-statement", center=True)], max_width="860px"),
        ]),
        Section(admin="Maak kennis", bg=KLEUR["creme"], cls="vv-lijnen", padding=(0, 0), padding_phone=(0, 0), rows=[
            Row([
                Col("1_2", [Image(img("vv-portret-buiten.jpg"), "Portret van de coach", cls="vv-beeld vv-beeld--staand"),
                            Code('<div class="vv-lijntekst">Leiden vanuit <i></i> <em>verbinding</em></div>', margin=(24, 0))],
                    padding=(70, 70, "8%", "8%"), padding_phone=(40, 40, "0", "0")),
                Col("1_2", [Text("""
<h4>Maak kennis</h4>
<h2>Hoi, fijn dat je er bent</h2>
<p>Ik ben [Naam], coach en oprichter van Vink Vitaal. Ik help leidinggevenden om weer in contact te komen met wat hen energie geeft, zodat ze met rust en overtuiging kunnen leiden.</p>
<p>Mijn aanpak is persoonlijk en praktisch: wat we bespreken, kun je de volgende dag toepassen.</p>
"""), Button("Meer over mij", variant="lijn recht", margin=(26, 0))],
                    cls="vv-kolom-midden", padding=(70, 70, "12%", "12%"), padding_phone=(40, 56, "0", "0")),
            ], cls="vv-lijnkolommen", gutter=1, equal=True, width="88%", max_width="1240px"),
        ]),
        Section(admin="Hoe ik je kan helpen", bg=KLEUR["salie_licht"], padding=(110, 120), rows=[
            kol("4_4", [Text("<h2>Hoe ik je kan <em>helpen</em></h2>", center=True)], padding=(0, 50)),
            Row([
                Col("1_3", [Image(img("vv-werk-gesprek.jpg"), "Coachgesprek", cls="vv-beeld vv-beeld--liggend vv-beeld--klein"),
                            Text('<h3>1-op-1 coaching</h3><p>Een persoonlijk traject rond jouw vragen over energie, grenzen en leiderschap.</p><p class="vv-meer"><a href="#">Meer info</a></p>', cls="vv-dienst", center=True)],
                    cls="vv-rand"),
                Col("1_3", [Image(img("vv-werk-team.jpg"), "Teamsessie", cls="vv-beeld vv-beeld--liggend vv-beeld--klein"),
                            Text('<h3>Vitaal Leiderschap</h3><p>Het groepsprogramma waarin je samen met andere leiders bouwt aan duurzame energie.</p><p class="vv-meer"><a href="#">Meer info</a></p>', cls="vv-dienst", center=True)],
                    cls="vv-rand"),
                Col("1_3", [Image(img("vv-sfeer-detail.jpg"), "Sfeerbeeld", cls="vv-beeld vv-beeld--liggend vv-beeld--klein"),
                            Text('<h3>Workshops voor teams</h3><p>Praktische sessies over vitaliteit en werkplezier, op locatie of online.</p><p class="vv-meer"><a href="#">Meer info</a></p>', cls="vv-dienst", center=True)],
                    cls="vv-rand"),
            ], equal=True, gutter=2),
        ]),
        Section(admin="Werkwijze", bg=KLEUR["creme"], padding=(110, 110), rows=[
            kol("1_2,1_2",
                [Text("<h4>Werkwijze</h4><h2>Stap voor stap, in <em>jouw</em> tempo</h2>")],
                [Text("<p>Geen standaardprogramma, wel een duidelijke route. Elke stap bouwt voort op de vorige, zodat veranderingen blijven hangen.</p>")],
                padding=(0, 40)),
            kol("1_4,1_4,1_4,1_4",
                [Text('<span class="vv-nummer">01</span><h3>Kennismaken</h3><p>Een open gesprek over waar je staat en wat je zoekt.</p>', cls="vv-stap")],
                [Text('<span class="vv-nummer">02</span><h3>Inzicht</h3><p>We brengen in kaart wat je energie geeft en wat het kost.</p>', cls="vv-stap")],
                [Text('<span class="vv-nummer">03</span><h3>Traject</h3><p>Coaching en oefeningen die passen bij jouw dagelijkse praktijk.</p>', cls="vv-stap")],
                [Text('<span class="vv-nummer">04</span><h3>Borgen</h3><p>Je verankert nieuwe gewoontes, zodat ze blijven werken.</p>', cls="vv-stap")]),
        ]),
        Section(admin="Citaat op foto", bg="#6E7F52", bg_img=img("vv-sfeer-gras.jpg"), cls="vv-overlay", padding=(150, 150), padding_phone=(90, 90), rows=[
            kol("4_4", [Text("""
<p>“Voor het eerst in jaren heb ik het gevoel dat ik mijn werk weer aankan, en dat ik er zelf ook nog ben.”</p>
<h4>Naam klant, afdelingshoofd</h4>
""", cls="vv-groot-citaat vv-op-foto", center=True)], max_width="900px"),
        ]),
        Section(admin="Veelgestelde vragen", bg=KLEUR["creme"], padding=(110, 110), rows=[
            kol("1_3,2_3",
                [Text("<h4>Veelgestelde vragen</h4><h2>Goed om te <em>weten</em></h2>")],
                [Toggle("Voor wie is coaching bij Vink Vitaal?", "<p>Voor leidinggevenden, ondernemers en professionals met verantwoordelijkheid die merken dat hun energie of plezier onder druk staat.</p>", cls="vv-vraag"),
                 Toggle("Hoe lang duurt een traject?", "<p>De meeste trajecten duren drie tot zes maanden. In het kennismakingsgesprek kijken we wat bij jou past.</p>", cls="vv-vraag"),
                 Toggle("Kan mijn werkgever het traject betalen?", "<p>Vaak wel. Coaching valt regelmatig onder het opleidings- of vitaliteitsbudget. Ik denk graag mee over een voorstel.</p>", cls="vv-vraag"),
                 Toggle("Werk je online of op locatie?", "<p>Allebei. Veel klanten kiezen voor een mix, en een wandelcoachsessie in de natuur is ook mogelijk.</p>", cls="vv-vraag")]),
        ]),
        Section(admin="Afsluitende oproep", bg=KLEUR["blauw_zacht"], padding=(120, 120), rows=[
            kol("4_4", [
                Text("<h2>Klaar om te <em>beginnen</em>?</h2><p>Plan een kennismaking en ontdek wat coaching voor jou kan betekenen.</p>", center=True),
                Button("Plan een kennismaking", align="center", variant="recht", margin=(30, 18)),
                Text("<p>Gratis en vrijblijvend · 30 minuten</p>", cls="vv-noot", center=True),
            ], max_width="720px"),
        ]),
    ]


# ---------------------------------------------------------------------------

TEMPLATES = [
    ("vv-template-1-groei", "Vink Vitaal – Template 1 Groei", template_groei),
    ("vv-template-2-natuur", "Vink Vitaal – Template 2 Natuur", template_natuur),
    ("vv-template-3-rust", "Vink Vitaal – Template 3 Rust", template_rust),
]


def gebruikte_beelden(secties):
    namen = set()
    for s in secties:
        if s.bg_img:
            namen.add(s.bg_img.rsplit("/", 1)[1])
        for r in s.rows:
            for c in r.cols:
                if c.bg_img:
                    namen.add(c.bg_img.rsplit("/", 1)[1])
                for m in c.modules:
                    if m.kind == "image":
                        namen.add(m.src.rsplit("/", 1)[1])
    return namen


def main():
    with open(os.path.join(ROOT, "divi", "head-fonts.html")) as f:
        fonts_head = f.read().strip()
    for naam, titel, maak in TEMPLATES:
        secties = maak()
        data = divi_json(secties, gebruikte_beelden(secties))
        with open(os.path.join(ROOT, "divi", naam + ".json"), "w") as f:
            json.dump(data, f, ensure_ascii=False)
        with open(os.path.join(ROOT, "preview", naam + ".html"), "w") as f:
            f.write(preview_html(titel, secties, fonts_head))
        grootte = os.path.getsize(os.path.join(ROOT, "divi", naam + ".json")) // 1024
        print(f"  {naam}: {len(secties)} secties, {grootte} KB")


if __name__ == "__main__":
    main()
