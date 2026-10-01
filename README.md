# Vink Vitaal: drie Divi-landingspagina's

Drie templates voor vink-vitaal.nl, gebouwd voor de **Divi Visual Builder**. Alle drie gebruiken het kleurenpalet uit `VitaalLeiderschap_kleuropties.pdf`, en de opzet is gebaseerd op de voorbeeldsites die je mooi vond.

| Template | Gebaseerd op | Karakter |
|---|---|---|
| **1 · Groei** | Astrid Jade + Molly Atkins | Foto naast een grote kop, een lopende tekstband, twee aanbodkaarten op foto's en ervaringen in kaarten. Warm en uitnodigend. |
| **2 · Natuur** | Etta's Acres | Volle natuurfoto bovenaan, een persoonlijk welkom met handgeschreven accenten, een grote lopende band met kernwoorden en een gratis gids. Het meest persoonlijk. |
| **3 · Rust** | August (+ video-idee van Eva Red Path) | Rustig en strak, met dunne lijnen, rechte knoppen, werkwijze in 4 stappen en veelgestelde vragen. Bovenaan kan een video. |

Previews openen: `preview/index.html` (of de gedeelde preview-link).

---

## De rode draad (uit jullie feedback)

Deze punten zitten in alle drie de templates verwerkt:

| Feedback | Zo zit het erin |
|---|---|
| *Jill van den Bosch: kleuren te donker* · *Scalable Coach: zwart-wit niet leuk* | Geen zwart en geen fel wit. De basis is crème `#EFF1E9` en de tekst antraciet `#464347`. Groen, oranje en blauw komen puur terug als accenten, met per template één groot blauw vlak; de overige vlakken zijn zachte tinten. |
| *Kristin Webster / Madison Arnholt: kleuren mooi, vriendelijk* | Salie-, zand- en blauwgrijze vlakken, ronde vormen en zachte schaduwen. |
| *Grace Brodeur: zachte beelden* · briefing: *foto's brengen de kleur* | De kleur komt uit natuur- en zonbeelden, en de vlakken blijven rustig. |
| *Esther Perel: te druk, niet persoonlijk, niet warm* | Eén boodschap per sectie, veel witruimte, de coach vroeg in beeld, "ik/jij"-taal en handgeschreven accenten. |
| *Jill van den Bosch: vlotte beweging, knoppen op de goede plek* | Teksten schuiven zacht in beeld en er loopt een tekstband. Er is één hoofdactie, **Plan een kennismaking**, die terugkomt in de hero, na het aanbod en onderaan. |
| *Eva Red Path: dynamiek, filmpje in het begin* | Template 3 is voorbereid op een achtergrondvideo in de hero. |

## Kleuren

**Basispalet (uit de pdf), alle vijf puur gebruikt:**

| Naam | Hex | Waar je hem ziet |
|---|---|---|
| Antraciet | `#464347` | alle tekst |
| Crème | `#EFF1E9` | achtergrond |
| Groen | `#6CA54D` | de lopende tekstband, vinkjes, lijnen boven de stappen, de cijfers |
| Oranje | `#E18030` | de warme knoppen, het hover-effect van alle knoppen, het cirkeltje om een woord, de sterretjes en schuine strepen in de banden, het sterretje in de badge, onderstrepingen van "meer"-links |
| Blauw | `#286BAE` | de kleine labels boven koppen, de grote letters "START JOUW TRAJECT", en per template één blauw vlak (met witte tekst) |

Groen, oranje en blauw zijn accenten: ze komen terug, maar nooit allemaal tegelijk in één groot vlak. Zo blijft het rustig.

**Leesbaarheid.** Niet elke paletkleur is geschikt voor tekst (norm: contrast 4,5):
- Witte tekst op het pdf-groen haalt maar 2,9. Knoppen en groene koppen zijn daarom diepgroen `#4E7F36` (4,8).
- Op oranje staat altijd donkere tekst `#2B282C` (5,1). Witte tekst op oranje zou 2,9 halen.
- Witte tekst op blauw haalt 5,5, dat is prima. Blauwe labels op crème halen 4,8. Op de getinte vlakken (salie, zand) is blauw te licht voor kleine tekst; daar worden de labels automatisch antraciet.

**Afgeleide tinten** voor de rustige kleurvlakken (de felle kleuren gemengd met crème):

| Naam | Hex | Gebruik |
|---|---|---|
| Diepgroen | `#4E7F36` | knoppen en groene koppen. Het pdf-groen is met witte tekst te slecht leesbaar (contrast 2,9); diepgroen haalt 4,8. |
| Salie | `#CEDEC2` | kleurvlak (25% groen) |
| Salie licht | `#DFE8D6` | kleurvlak (12% groen) |
| Blauwgrijs | `#C7D6DD` | kleurvlak (20% blauw) |
| Zand | `#ECDAC4` | kleurvlak (20% oranje) |
| Crème licht | `#F7F8F3` | kaarten |

## Lettertypes

- **Instrument Serif**: koppen, met *cursieve* accentwoorden zoals in de voorbeelden
- **DM Sans**: lopende tekst, knoppen en labels
- **Caveat**: handgeschreven accenten (vooral template 2)

---

## Installatie (eenmalig, ±15 minuten)

### Stap 1: Lettertypes laden
**Divi → Thema-opties → Integratie → "Code toevoegen aan de &lt;head&gt; van je blog"**
Plak de inhoud van `divi/head-fonts.html` en sla op.

> **Privacy (AVG):** zo worden de lettertypes bij Google opgehaald. Wil je dat niet, gebruik dan een plugin als *OMGF* om ze lokaal te hosten. Dat werkt hiermee ook.

### Stap 2: Het stylesheet plakken
**Divi → Thema-opties → Algemeen → Aangepaste CSS**
Plak de volledige inhoud van `divi/vink-vitaal.css` en sla op.
De opmaak geldt alleen voor secties met de klasse `vv`, dus de rest van je site verandert niet.

### Stap 3 (aanrader): Paletkleuren in Divi zetten
**Divi → Thema-opties → Algemeen → "Standaardpalet kleurkiezers"**
Vul in: `#464347` `#EFF1E9` `#6CA54D` `#E18030` `#286BAE` `#4E7F36` `#CEDEC2` `#ECDAC4`.
Dan heb je deze kleuren met één klik bij de hand in de Visual Builder.

### Stap 4: Een template op een pagina zetten
1. **Pagina's → Nieuwe pagina**, geef een titel en kies **Divi gebruiken**, dan **Bouwen op de voorkant (Visual Builder)**.
2. Kies **Vanaf nul bouwen** (Build from scratch).
3. Klik onderaan op de paarse **⋯**-knop en dan op het icoon met de **pijltjes omhoog/omlaag** (*Portability*).
4. Tabblad **Importeren**, kies `divi/vv-template-1-groei.json` (of 2 of 3), vink **Bestaande inhoud vervangen** aan en klik **Importeren**.
5. Divi zet de placeholder-foto's automatisch in je Mediabibliotheek. Opslaan en klaar.

**Tip:** de templates hebben een eigen topbalk. Wil je de standaard Divi-header en footer verbergen, kies dan rechts in de pagina-instellingen bij *Paginasjabloon* **Blank Page**. Gebruik je liever je gewone header, verwijder dan de bovenste sectie "Topbalk" (template 1), of de menurij in de hero (template 2 en 3).

**Als herbruikbaar sjabloon:** zet je het template na het importeren in de Divi-bibliotheek (**⋯ → Opslaan in bibliotheek**), dan kun je het bij elke nieuwe pagina laden via **Uit bibliotheek laden**.

> **Divi 5?** De bestanden staan in het Divi 4-formaat. Divi 5 zet zulke layouts bij het importeren automatisch om.

---

## Werken in de Visual Builder

**Gewoon in Divi aanpassen:** teksten, foto's, knopteksten en links, sectie-achtergronden (kleur, foto, video), de volgorde van secties, en secties of modules kopiëren en verwijderen.

**Centraal geregeld via CSS:** lettertypes, tekstgroottes, tekstkleuren en de vorm van knoppen en kaarten. Zo blijven alle pagina's consistent. Wil je iets anders, bijvoorbeeld een andere knopkleur, pas dan de variabele bovenaan `vink-vitaal.css` aan. Dat werkt meteen op alle pagina's door.

**Tekst opmaken in een tekstmodule:**
- *Cursief* maken in een kop geeft het elegante accentwoord.
- Een **Kop 4** werkt als klein label boven een kop (zoals "VITAAL LEIDERSCHAP").
- In de HTML-weergave kun je `<span class="vv-cirkel">woord</span>` gebruiken voor een handgetekende cirkel om een woord, of `<p class="vv-hand">Welkom!</p>` voor handschrift.

### Klassen die je zelf kunt hergebruiken
In elke module: **Geavanceerd → CSS-ID & klassen → CSS-klasse**.

| Klasse | Waar | Effect |
|---|---|---|
| `vv` | **elke sectie** | zet de Vink Vitaal-opmaak aan (verplicht!) |
| `vv-btn` | knop | standaardknop, diepgroen en rond |
| `vv-btn vv-btn--lijn` | knop | omlijnde knop |
| `vv-btn vv-btn--warm` | knop | oranje knop met donkere tekst |
| `vv-btn vv-btn--licht` / `--lijn-licht` | knop | voor op een foto |
| `vv-btn vv-btn--recht` | knop | rechte hoeken (template Rust) |
| `vv-beeld vv-beeld--staand` | afbeelding | ronde hoeken, 4:5 |
| `vv-beeld vv-beeld--liggend` / `--vierkant` / `--boog` | afbeelding | 4:3 / 1:1 / boogvorm |
| `vv-kaart` | tekst (+ knop direct eronder) | witte kaart |
| `vv-citaat` | tekst | ervaringskaart |
| `vv-hoofdletters` | tekst | koppen in hoofdletters |
| `vv-op-foto` | tekst | witte tekst op een foto of op het blauwe vlak |
| `vv-overlay` | sectie | zachte donkere laag over de achtergrondfoto |
| `vv-lijnen` | sectie | dunne lijn boven en onder |
| `vv-band-groen` | sectie (groene achtergrond) | witte tekst in de lopende band |
| `vv-vraag` | toggle | veelgestelde vraag |

---

## Foto's vervangen (shotlijst)

Alle placeholders hebben een label dat zegt welke foto erin hoort. Klik in de Visual Builder op de afbeelding of de sectie-achtergrond en kies je eigen foto.

| Placeholder | Gewenste foto | Formaat |
|---|---|---|
| `vv-hero-portret.jpg` | Portret coach, zittend, natuurlijk licht | liggend 5:4 |
| `vv-portret-staand.jpg` | Portret, warme glimlach | staand 4:5 |
| `vv-portret-buiten.jpg` | Portret buiten in het groen | staand 4:5 |
| `vv-hero-natuur.jpg` | Coach wandelt door een veld, zon in de rug (rustig vlak in het midden voor tekst) | breed 16:9 |
| `vv-sfeer-bos.jpg` | Zonlicht door de bomen | breed 16:9 |
| `vv-sfeer-gras.jpg` | Veld met wuivend gras, lucht bovenin (ruimte voor tekst) | breed 16:9 |
| `vv-sfeer-detail.jpg` | Detail: thee, notitieboek, ochtendlicht | staand |
| `vv-werk-gesprek.jpg` | Coachgesprek aan tafel | liggend 4:3 |
| `vv-werk-team.jpg` | Teamsessie of workshop | liggend 4:3 |

Tip voor de fotograaf: zacht daglicht, warme tinten, geen zwart-wit, en laat bij brede foto's rust over voor tekst.

### Video in de hero (template 3)
Open de bovenste sectie, ga naar **Achtergrond → tabblad Video** en upload een MP4. De foto blijft staan als terugval op telefoons. Houd de video kort (10–20 sec, loopt in een lus), zonder geluid en onder 8 MB.

---

## Checklist voor livegang
- [ ] `[Naam]` vervangen door je eigen naam (template 2 en 3)
- [ ] Ervaringen vervangen door echte citaten van klanten (met hun toestemming)
- [ ] Alle knoppen en links met `#` naar de juiste pagina laten wijzen
- [ ] Placeholder-foto's vervangen door eigen foto's, en de alt-teksten aanpassen
- [ ] Op telefoon controleren met de responsive-weergave in de Visual Builder

---

## Voor de techneut: opnieuw genereren
De templates worden gegenereerd met Python (Pillow en NumPy nodig):

```bash
python3 tools/maak_placeholders.py   # placeholder-foto's in afbeeldingen/
python3 tools/build.py               # divi/*.json + preview/*.html
```

`tools/build.py` beschrijft elke sectie één keer. Daaruit komen zowel de Divi-shortcodes als de preview, met dezelfde klassen, zodat de preview en Divi hetzelfde stylesheet gebruiken.
`preview/divi-shim.css` bootst alleen Divi's eigen basis-CSS na voor de preview. Dat bestand hoort niet in WordPress.
