# Shopify snelheid tips: meetbare checklist

Een checklist om een Shopify-winkel sneller te maken, met nadruk op wat je kunt **meten**. Erbij zit een script (`render_blocking_apps.py`) dat uit de HTML van een winkelpagina laat zien welke scripts en stylesheets het laden blokkeren en van welke externe partijen ze komen. Zo zie je welke app of tag de pagina vertraagt, in plaats van te raden.

Shopify zelf (servers, netwerk, checkout) is zelden de oorzaak van een trage winkel. Meestal zit het probleem in wat er bovenop is gebouwd: apps, trackingcode, grote afbeeldingen en een zwaar thema.

## Voor wie

- Winkeleigenaren die willen weten waarom hun winkel traag voelt.
- Webbouwers die een thema of een set apps willen opschonen.

## Wat zit erin

| Bestand | Doel |
|---|---|
| `README.md` | De checklist |
| `render_blocking_apps.py` | Toont blokkerende scripts, stylesheets en externe domeinen op een pagina |
| `voorbeeld/pagina.html` | Voorbeeld-HTML om het script mee uit te proberen |

## Stap 1: meet voordat je iets verandert

- [ ] Meet de **homepage, een collectiepagina en een productpagina** op mobiel met PageSpeed Insights. Noteer de scores en de waarden.
- [ ] Kijk naar de veldgegevens ("Echte gebruikers") als die er zijn. Labscores zijn een indicatie; veldgegevens zijn wat Google gebruikt.
- [ ] Richtwaarden voor "goed" bij Core Web Vitals: **LCP** onder 2,5 s, **INP** onder 200 ms, **CLS** onder 0,1.
- [ ] Bewaar de meting met datum. Na elke wijziging meet je opnieuw, zodat je ziet wat werkte.

| Pagina | LCP | INP | CLS | Datum |
|---|---|---|---|---|
| Home | | | | |
| Collectie | | | | |
| Product | | | | |

## Stap 2: apps opschonen

Elke app die iets op de voorkant toont, laadt meestal een of meer scripts op **elke** pagina, ook waar je ze niet gebruikt.

- [ ] Maak een lijst van alle geïnstalleerde apps. Noteer per app: wat doet hij, hoe vaak gebruik je hem, en laadt hij iets op de winkelpagina's?
- [ ] Verwijder wat je niet gebruikt. Een app verwijderen haalt niet altijd de code uit je thema. Zoek in `theme.liquid`, `snippets` en `assets` naar resten (bijvoorbeeld de naam van de app of zijn domein).
- [ ] Gebruik waar kan **app-embeds en app-blokken** in de thema-editor, zodat je een app per pagina kunt uitzetten.
- [ ] Vervang drie apps die een klein ding doen door een stukje themacode als dat kan.
- [ ] Voer `render_blocking_apps.py` uit op de drie meetpagina's (zie onder) en zoek de domeinen die vaak terugkomen.
- [ ] Let op: oudere review-, pop-up- en chatapps die nog script tags gebruiken, stoppen op 1 maart 2027. Controleer dit met [joepify-kennisbank](https://github.com/Joepify/joepify-kennisbank/blob/main/gidsen/shopify-script-tags-2027.md).

## Stap 3: externe scripts en tracking

- [ ] Staan alle meetcodes (GA4, Meta, TikTok, Hotjar) nog in gebruik? Verwijder wat niemand bekijkt.
- [ ] Laad tracking via een tag manager of Shopify Customer Events (Pixels) in plaats van losse code in het thema.
- [ ] Zorg dat de cookiebanner niet de hoofdinhoud blokkeert.
- [ ] Gebruik `async` of `defer` voor scripts die niet nodig zijn om de pagina te tekenen.
- [ ] Laad chatwidgets en pop-ups pas na interactie of na een korte vertraging.
- [ ] Beperk het aantal externe domeinen. Elk extra domein betekent een DNS-opzoeking en een verbinding.

## Stap 4: afbeeldingen

Afbeeldingen zijn bijna altijd het grootste deel van het paginagewicht en vaak het LCP-element.

- [ ] Upload niet breder dan nodig. Een afbeelding van 4000 pixels breed voor een vak van 600 is verspilling.
- [ ] Gebruik in Liquid de filter `image_url` met een breedte en `image_tag` met `widths` en `sizes`, zodat de browser de juiste maat kiest.
- [ ] De **eerste grote afbeelding** (hero, eerste productfoto) krijgt `loading="eager"` en `fetchpriority="high"`. Alles onder de vouw krijgt `loading="lazy"`.
- [ ] Zet `width` en `height` op elke afbeelding, zodat de pagina niet verspringt.
- [ ] Geen slider met vijf banners als bezoekers er één zien.
- [ ] Gebruik video's alleen waar ze waarde toevoegen en laad ze pas bij interactie.

Een voorbeeld in Liquid:

```liquid
{{ product.featured_image | image_url: width: 1200 | image_tag:
   widths: '400, 600, 800, 1200',
   sizes: '(min-width: 990px) 50vw, 100vw',
   loading: 'eager', fetchpriority: 'high' }}
```

## Stap 5: thema en Liquid

- [ ] Gebruik een actueel thema (bijvoorbeeld een Online Store 2.0-thema) en houd het bijgewerkt.
- [ ] Verwijder secties en blokken die je niet gebruikt van de pagina's.
- [ ] Voorkom geneste loops over grote collecties. Gebruik `paginate` en haal niet alle producten op een pagina op.
- [ ] Gebruik `{% render %}` in plaats van `{% include %}`.
- [ ] Zet kritieke CSS niet in een groot extern bestand dat de pagina blokkeert; laad niet-kritieke CSS later.
- [ ] Houd lettertypen beperkt: maximaal twee families, en gebruik `font-display: swap`.
- [ ] Laad JavaScript van het thema als module of met `defer`.

## Stap 6: herhaal en bewaak

- [ ] Na elke nieuwe app of campagne: meet opnieuw.
- [ ] Kijk elke maand in Search Console bij Core Web Vitals naar nieuwe slechte URL-groepen.
- [ ] Wijs één persoon aan die bij elke nieuwe app de impact controleert.

## Het script gebruiken

Het script leest HTML van een URL of van een bestand, en rapporteert:

- scripts in de `<head>` zonder `async`, `defer` of `type="module"` (blokkerend);
- stylesheets in de `<head>` (blokkerend, tenzij met een `media`-waarde die niet `all` is);
- per extern domein het aantal scripts en stylesheets;
- de grootte van inline scripts en een lijst van bekende app- en trackingdomeinen.

```bash
python3 render_blocking_apps.py https://jouwwinkel.nl
python3 render_blocking_apps.py voorbeeld/pagina.html
python3 render_blocking_apps.py https://jouwwinkel.nl/products/voorbeeld --json
```

Voorbeeld van de uitvoer voor `voorbeeld/pagina.html`:

```
Blokkerende scripts in <head>: 3
  cdn.shopify.com   /s/files/1/0000/assets/theme.js
  widget.reviews-app.example   /loader.js
  static.klaviyo.com   /onsite/js/klaviyo.js

Blokkerende stylesheets in <head>: 2
  cdn.shopify.com   /s/files/1/0000/assets/base.css
  fonts.googleapis.com   /css2

Externe domeinen en eigen bestanden (scripts + stylesheets):
  4x  cdn.shopify.com   <- Shopify (thema of app-extensie)
  1x  widget.reviews-app.example
  1x  static.klaviyo.com   <- Klaviyo
  1x  www.googletagmanager.com   <- Google Tag Manager / GA4
  1x  (eigen domein)
  1x  fonts.googleapis.com   <- Google Fonts

Inline scripts in <head>: 1 (126 bytes)
```

Let op: het script kijkt naar de **HTML** zoals de server die levert. Scripts die pas later via JavaScript worden toegevoegd, zie je niet. Gebruik daarvoor het tabblad Netwerk in de ontwikkelaarstools van je browser of PageSpeed Insights. Het script bewijst ook niet dat een script de oorzaak is: het wijst aan waar je moet kijken.

## Laat het mij doen

Ik meet je winkel en haal de echte vertragers weg. Vaste prijs: vanaf €395 eenmalig (excl. btw). [Meer over snelheid](https://www.joepify.nl/shopify-snelheid-optimalisatie?utm_source=github&utm_medium=readme&utm_campaign=shopify-snelheid-tips) of [stuur een WhatsApp-bericht](https://wa.me/31687195043?text=Hoi%20Ayoub%2C%20ik%20kom%20via%20GitHub%20%28shopify-snelheid-tips%29%20en%20wil%20hulp%20met%20shopify%20snelheid.).

## Over Joepify

[Joepify](https://www.joepify.nl?utm_source=github&utm_medium=readme&utm_campaign=shopify-snelheid-tips) is een webbureau aan de Metaalhof 27 in Rotterdam. Ayoub Assaidi meet en verbetert Shopify-winkels voor een vaste prijs vooraf, zoals beschreven op [Shopify snelheid optimaliseren](https://www.joepify.nl/shopify-snelheid-optimalisatie?utm_source=github&utm_medium=readme&utm_campaign=shopify-snelheid-tips). Voor een snelle indruk van je winkel is er de gratis [Shopify winkelcheck](https://www.joepify.nl/shopify-winkel-check?utm_source=github&utm_medium=readme&utm_campaign=shopify-snelheid-tips).

## English

A measurable Shopify speed checklist (apps, tracking, images, Liquid, Core Web Vitals thresholds: LCP under 2.5 s, INP under 200 ms, CLS under 0.1) plus `render_blocking_apps.py`, a standard-library Python 3 script that lists render-blocking scripts and stylesheets in the page `<head>`, counts third-party domains and flags known app and tracking hosts. It reads server HTML only; late injected scripts need browser dev tools.

## Licentie

Tekst: CC BY 4.0. Code: MIT. Zie [LICENSE](LICENSE).
