# Elvereferanse

Oppslagstabeller per elv. Alle tall er verifisert mot publiserte `index.html`-filer og
`data/sesong.json` 2026-09-26. Konstantene bakes inn ved bygging — sjekk fila hvis en runde
har regenerert dem siden.

---

## Kilder og identifikatorer

| Elv | NVE-stasjon | ID | Inatur riverId | Nedbørspunkt |
|---|---|---|---|---|
| Audna | Gaupefossen | 23.8.0 | 621 | `nedbor.json` (Konsmo) |
| Lygna | Tingvatn (Lygne) | 24.9.0 | 25 | `nedbor_lygna.json` (Eiken) |
| Mandalselva | Kjølemo | 22.4.0 | 1542 | — |
| Otra | Heisel | 21.11.0 | 6 | — |
| Sygna | Søgne | 22.22.0 | 717 | `nedbor_sygna.json` (Nodeland) |
| Tovdalselva | Flakksvann | 20.3.0 | 5 | `nedbor_tovdalselva.json` (Hynnekleiv) |

---

## Vannføringsbins

| Elv | Binstørrelse | Sliderområde | Samlebin | Glatting |
|---|---|---|---|---|
| Audna | 5 m³/s | 0–55 | 55+ | ±5 |
| Lygna | 5 m³/s | 0–55 | 55+ | ±5 |
| Mandalselva | 5 m³/s | 15–150 | 150+ | ±5 |
| Otra | 25 m³/s | 50–300 | 300+ | ±25 |
| Sygna | 2 m³/s | 0–18 | 18+ | ±2 |
| Tovdalselva | 5 m³/s | 0–85 | 85+ | ±5 |

Glattingen er alltid nøyaktig én binbredde i hver retning.

> ℹ️ Mandalselva ble tidligere notert med 15 m³/s bins. Det er feil — koden bruker
> `Math.floor(f / 5) * 5` og slider-`step="5"`. Sliderens *startpunkt* er 15, noe som
> trolig er kilden til forvekslingen.

---

## Scoringskonstanter

| Elv | P90 rate | P90 volum | MAKS rate | MAKS volum | Vekting rate/volum |
|---|---|---|---|---|---|
| Audna | 5,1 | 175,5 | 11,0 | 1374 | 0,8 / 0,2 |
| Lygna | 1,58 | 63,8 | 6,57 | 612 | 0,8 / 0,2 |
| Mandalselva | 0,82 | 38,0 | 17,9 | 2043 | **1,0 / 0,0** |
| Otra | 1,89 | 204 | 2,53 | 873 | 0,8 / 0,2 |
| Sygna | 7,0 | 301,0 | 7,02 | 418 | 0,8 / 0,2 |
| Tovdalselva | 2,77 | 96,5 | 6,3 | 150 | 0,8 / 0,2 |

Alle elver har i tillegg egne konstanter for «kun flue»:

| Elv | P90 rate (flue) | P90 volum (flue) | MAKS rate (flue) | MAKS volum (flue) |
|---|---|---|---|---|
| Audna | 2,68 | 77,4 | 5,67 | 326 |
| Lygna | 0,86 | 33,6 | 1,94 | 168 |
| Mandalselva | 0,64 | 28,0 | 11,56 | 1077 |
| Otra | 0,78 | 94 | 1,16 | 454 |
| Sygna | 5,25 | 218,1 | 5,55 | 255 |
| Tovdalselva | 1,99 | 57,5 | 5,0 | 100 |

**Sygna og Tovdalselva har egne sett** for «kun laks»-visningen, siden standardvisningen teller
laks og sjøørret samlet:

| | P90 rate | P90 volum | MAKS rate | MAKS volum |
|---|---|---|---|---|
| Sygna laks | 2,68 | 103,2 | 2,87 | 186 |
| Sygna laks + flue | 1,63 | 54,5 | 2,07 | 104 |
| Tovdalselva laks | 2,6 | 84,5 | 6,0 | 135 |
| Tovdalselva laks + flue | 1,78 | 55,0 | 4,8 | 97 |

**Elvenivå-score** (`computeRiverScore()`, `shrinkCElv` = 8) finnes kun i tre elver:

| Elv | P90 rate (elv) | P90 volum (elv) | MAKS rate (elv) | MAKS volum (elv) |
|---|---|---|---|---|
| Audna | 21,25 | 137,9 | 69,50 | 443,0 |
| Lygna | 17,125 | 86,0 | 50,00 | 316,0 |
| Tovdalselva | 10,33 | 37,0 | 32,50 | 146,0 |

Mandalselva og Otra viser elvescore som fangstvektet snitt av sonescorene.

---

## Sesong og kvoter 2026

Sesongdatoer leses fra `data/sesong.json` (endres i admin). Kvoter står i banneret i hvert
dashboard; utfyllende regler i [kvoter-2026.md](kvoter-2026.md).

| Elv | Sesong | Døgnkvote | Sesongkvote |
|---|---|---|---|
| Audna | 1. juni – 31. aug | 1 laks | 3 laks ≥ 65 cm |
| Lygna | 15. juni – 30. aug | 1 laks | 5 laks |
| Mandalselva | 1. juni – 31. aug* | 1 laks | 5 laks (maks 1 ≤ 90 cm) |
| Otra | 15. juni – 17. aug | 1 laks + 1 sjøørret | 25 kg |
| Sygna | 15. juli – 15. sept | 2 fisk (laks/sjøørret) | Ikke fastsatt |
| Tovdalselva | 1. juni – 31. aug | 1 laks / 2 sjøørret | 5 laks (fra 15/8 maks 1 > 65 cm) |

\* Mandalselva: **Sone 4 og dens delsoner har sesongslutt 15. september.** Det gjelder
Sone 4 selv pluss Bjåhylen, Klevelandsfossen, Laksehylen, Nodehylen, Steinshylen og
Strædethylen — alle nord for Sone 3. Alle andre soner slutter 31. august.

Soneavvik i `sesong.json`:

- **Audna:** Sone 4 er stengt kl. 23–04.
- **Otra:** Sone 5B Rød åpner 1. juli. Sone 5B Øst er stengt.

Utfyllende regler:

- **Audna:** ingen begrensning på laks under 65 cm. Maks 3 gjenutsettinger per døgn.
  Oppfordring om å gjenutsette hunnlaks ≥ 65 cm.
- **Lygna:** all laks over 65 cm skal gjenutsettes.
- **Mandalselva:** all laks over 65 cm skal gjenutsettes. 21 °C-stoppen er ikke lenger del av
  kvotesettet (bekreftet 2026-09-20), men står fortsatt i dashboardets `ZONE_INFO`.
- **Otra:** agn (meitemark) tillatt.
- **Tovdalselva:** all laks over 65 cm skal gjenutsettes. Maks 2 gjenutsettinger per døgn.

---

## Fiskemelding

| Elv | Status | Responstid |
|---|---|---|
| Audna | Aktiv, kalibrert | Samme døgn — uregulert, rask respons |
| Lygna | Aktiv, kalibrert | 1–2 døgn — Lygne buffrer tilsiget |
| Sygna | Aktiv, kalibrert | Samme døgn — liten flomelv |
| Tovdalselva | Aktiv, kalibrert | Ikke dokumentert |
| Mandalselva | Ingen | Regulert; nedbørmetoden gjelder ikke |
| Otra | Ingen | Regulert; vannføring styres av kraftverksdrift |

Meldingen velges på **forventet stigning**, ikke på nedbørmengde alene:

1. MET-varselet summeres over de neste 72 timene (i tre døgnbøtter).
2. Forventet stigning = nedbør × responsfaktor, der faktoren avhenger av dagens vannføring
   (lav elv tar opp lite; våt mark gir 3–5× større respons).
3. Meldingen avgjøres av om forventet stigning når elvas `MAALSTIGNING`:

| Elv | Responsgrenser (m³/s) | Responsfaktor (m³/s per mm) | Målstigning | «Svært lav» under |
|---|---|---|---|---|
| Audna | 1,9 · 3,8 · 6,4 · 11,6 | 0,075 · 0,121 · 0,259 · 0,264 · 0,552 | 2,0 | 3,8 |
| Lygna | 1,0 · 3,0 · 7,1 · 13,9 | 0,008 · 0,067 · 0,281 · 0,331 · 0,491 | 3,0 | 3,0 |
| Sygna | 0,5 · 0,9 · 2,0 · 4,6 | 0,032 · 0,046 · 0,183 · 0,3 · 0,373 | 2,0 | 0,9 |
| Tovdalselva | 6,8 · 11,2 · 29,7 · 55,8 | 0,04 · 0,237 · 0,237 · 1,148 · 1,293 | 3,0 | 11,2 |

| Situasjon | Melding |
|---|---|
| < 3 mm totalt, vannet faller > 0,5 m³/s siste døgn | 🌊 Tørt, men fallende vann |
| < 3 mm totalt ellers | ☀️ Tørt og stabilt |
| Vannføring utilgjengelig | ☔ Nedbør i vente (effekt usikker) |
| Forventet stigning ≥ målstigning | ☔ Gode forhold i vente |
| Forventet stigning ≥ 1 m³/s | 💦 Noe stigning i vente |
| Svært lav elv og ≥ 10 mm | 💧 Regn i vente – elva er svært lav |
| ellers | 🌂 Litt regn i vente |

Hvilken døgnbøtte som har mest nedbør styrer bare ordlyden («neste døgn» / «i
morgen/overimorgen» / «om 2–3 døgn»). Bakgrunn og kalibreringsfunn:
[scoring-og-kalibrering.md](scoring-og-kalibrering.md).

---

## Særegenheter per elv

**Audna** — egen fotoregel for Sone 5-delingen (se [datamodell.md](datamodell.md)).

**Lygna** — hybrid sonemodell med både punkt- og linjesoner. Tre soner har reell
start/slutt-referanse: `Gysfossen til Lygne`, `Kvåsfossen til Gysfossen` og
`Sone 8 Prestegården`. Resten er punktsoner.

**Mandalselva** — 56 soner, klart flest. Bruker ren rate uten volumledd fordi sonene
varierer sterkt i størrelse. Har forhåndslasting av nabobilder i galleriet.

**Otra** — regulert. `Egen eiendom` og `Egen rettighet` er ekskludert fra sonevisning, men
teller i elvetotalen. Datahull i vannføringen for 2019.

**Sygna** — kun én sone, «Alle åpne soner». Primært sjøørretelv; scorer begge arter samlet
med en «kun laks»-bryter. Minste bins av alle elvene.

**Tovdalselva** — scorer laks og sjøørret samlet med «kun laks»-bryter, som Sygna. Soner fra
Sone 1 til Laksefoss, inkludert `Teinefoss Fluefiske` og `Buhølen`. Bredest sliderområde blant
5 m³/s-elvene (0–85).
