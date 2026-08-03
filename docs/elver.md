# Elvereferanse

Oppslagstabeller per elv. Alle tall er verifisert mot publiserte `index.html`-filer.

---

## Kilder og identifikatorer

| Elv | NVE-stasjon | ID | Inatur riverId | Nedbørspunkt |
|---|---|---|---|---|
| Audna | Gaupefossen | 23.8.0 | 621 | `nedbor.json` (Konsmo) |
| Lygna | Tingvatn (Lygne) | 24.9.0 | 25 | `nedbor_lygna.json` (Eiken) |
| Mandalselva | Kjølemo | 22.4.0 | 1542 | — |
| Otra | Heisel | 21.11.0 | 6 | — |
| Sygna | Søgne | 22.22.0 | 717 | `nedbor_sygna.json` (Nodeland) |

---

## Vannføringsbins

| Elv | Binstørrelse | Sliderområde | Samlebin | Glatting |
|---|---|---|---|---|
| Audna | 5 m³/s | 0–55 | 55+ | ±5 |
| Lygna | 5 m³/s | 0–55 | 55+ | ±5 |
| Mandalselva | 5 m³/s | 15–150 | 150+ | ±5 |
| Otra | 25 m³/s | 50–300 | 300+ | ±25 |
| Sygna | 2 m³/s | 0–18 | 18+ | ±2 |

Glattingen er alltid nøyaktig én binbredde i hver retning.

> ℹ️ Mandalselva ble tidligere notert med 15 m³/s bins. Det er feil — koden bruker
> `Math.floor(f / 5) * 5` og slider-`step="5"`. Sliderens *startpunkt* er 15, noe som
> trolig er kilden til forvekslingen.

---

## Scoringskonstanter

| Elv | P90 rate | P90 volum | MAKS rate | MAKS volum | Vekting rate/volum |
|---|---|---|---|---|---|
| Audna | 5,30 | 173,5 | 11,0 | 1356 | 0,8 / 0,2 |
| Lygna | 1,58 | 63,4 | 6,57 | 599 | 0,8 / 0,2 |
| Mandalselva | 0,82 | 38,0 | 17,9 | 2043 | **1,0 / 0,0** |
| Otra | 1,95 | 199 | 2,81 | 775 | 0,8 / 0,2 |
| Sygna | 7,00 | 301,0 | 7,02 | 418 | 0,8 / 0,2 |

Alle elver har i tillegg egne konstanter for «kun flue»:

| Elv | P90 rate (flue) | P90 volum (flue) | MAKS rate (flue) | MAKS volum (flue) |
|---|---|---|---|---|
| Audna | 3,00 | 77,4 | 6,00 | 326 |
| Lygna | 0,86 | 33,6 | 1,94 | 165 |
| Mandalselva | 0,64 | 28,0 | 11,56 | 1077 |
| Otra | 0,83 | 94 | 1,20 | 416 |
| Sygna | 5,25 | 218,1 | 5,55 | 255 |

**Sygna har et fjerde sett** for «kun laks»-visningen, siden standardvisningen teller laks
og sjøørret samlet:

| | P90 rate | P90 volum | MAKS rate | MAKS volum |
|---|---|---|---|---|
| Laks | 2,68 | 103,2 | 2,87 | 186 |
| Laks + flue | 1,63 | 54,5 | 2,07 | 104 |

---

## Sesong og kvoter 2026

| Elv | Sesong | Døgnkvote | Sesongkvote |
|---|---|---|---|
| Audna | 1. juni – 31. aug | 1 laks | 3 laks ≥ 65 cm |
| Lygna | — | 1 laks | 5 laks |
| Mandalselva | 1. juni – 31. aug* | 1 laks | 5 laks (maks 1 ≤ 90 cm) |
| Otra | 15. juni – 17. aug | 1 laks | 25 kg |
| Sygna | 15. juli – 31. aug | 2 fisk (laks/sjøørret) | Ukjent |

\* Mandalselva: **Sone 4 og dens delsoner har sesongslutt 15. september.** Det gjelder
Sone 4 selv pluss Bjåhylen, Klevelandsfossen, Laksehylen, Nodehylen, Steinshylen og
Strædethylen — alle nord for Sone 3. Alle andre soner slutter 31. august.

Utfyllende regler:

- **Audna:** ingen begrensning på laks under 65 cm. Maks 3 gjenutsettinger per døgn.
  Oppfordring om å gjenutsette hunnlaks ≥ 65 cm.
- **Lygna:** all laks over 65 cm skal gjenutsettes.
- **Mandalselva:** all laks over 65 cm skal gjenutsettes. Alt fiske stoppes ved
  vanntemperatur over 21 °C.
- **Otra:** agn tillatt. Sone 5B Rød åpner 1. juli.

---

## Fiskemelding

| Elv | Status | Logikk |
|---|---|---|
| Audna | Aktiv | Samme døgn — uregulert, rask respons |
| Lygna | Aktiv | 1–2 døgn — Lygne buffrer tilsiget |
| Sygna | Aktiv | Samme døgn — liten flomelv |
| Mandalselva | Ikke implementert | Regulert; nedbørmetoden gjelder ikke |
| Otra | Deaktivert | Regulert; vannføring styres av kraftverksdrift |

Terskler (Audna og Sygna):

| Nedbør | Melding |
|---|---|
| ≥ 10 mm neste 24 t | 🌧️ Gode forhold i vente |
| ≥ 3 mm neste 24 t | 🌦️ Litt regn i vente |
| ≥ 10 mm i 24–48 t | 🌧️ Regn om 1–2 døgn |
| ellers | ☀️ Tørt i vente |

> ⚠️ **Kjent skjevhet:** tersklene er asymmetriske. 3 mm utløser melding hvis det kommer i
> dag, men det kreves 10 mm hvis det kommer i morgen. I tillegg ser logikken kun 48 timer
> frem. For Lygna, som uansett har forsinket respons, er dette dårlig tilpasset — varsel om
> morgendagens regn er der mer nyttig enn dagens. Ikke endret; under vurdering.

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
