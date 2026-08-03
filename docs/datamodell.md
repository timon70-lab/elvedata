# Datamodell

Referanse over datafilene i `data/`, hvem som skriver dem, og hvilke særegenheter man må
kjenne til.

---

## Filoversikt

| Fil | Skrives av | Frekvens | Konsekvens hvis borte |
|---|---|---|---|
| `config.json` | Admin-panelet | Manuelt | Dashbordene bruker innebygget fallback |
| `vannforing.json` (Audna) | `nve_cache.yml` | Hver time | Live-vannføring vises ikke |
| `vannforing_lygna.json` | `nve_cache.yml` | Hver time | Samme |
| `vannforing_mandalselva.json` | `nve_cache.yml` | Hver time | Samme |
| `vannforing_otra.json` | `nve_cache.yml` | Hver time | Samme |
| `vannforing_sygna.json` | `nve_cache.yml` | Hver time | Samme |
| `nedbor.json` (Audna) | `nve_cache.yml` | Hver time | Fiskemelding skjules stille |
| `nedbor_lygna.json` | `nve_cache.yml` | Hver time | Samme |
| `nedbor_sygna.json` | `nve_cache.yml` | Hver time | Samme |
| `fangster_<elv>.json` | `fangst_pipeline.py` | Hver time | «Siste fangster» tom |
| `photos_<elv>.json` | Foto-pipelines / admin | Ved opplasting | Bildegalleri tomt |
| `videoer_<elv>.json` | Admin-panelet | Manuelt | Videogalleri tomt |
| `nyheter.json` | Admin-panelet | Manuelt | Nyhetsbanner skjules |
| `nyhetskilder.json` | Admin-panelet | Manuelt | Kildevelger tom |
| `soner.json` | Manuelt | Ved soneendring | Admin-nedtrekk tomme |

Merk navneinkonsekvensen: Audna bruker `vannforing.json` og `nedbor.json` uten
elvesuffiks, fordi de var først. De øvrige har suffiks. Ikke rør dette uten å oppdatere
alle referansene samtidig.

`videoer_lygna.json` og `videoer_otra.json` finnes ikke ennå — dashbordene håndterer det
ved å vise et tomt galleri.

---

## Formater

### `config.json`

Scoringsparametre per elv, pluss sparkline-skalering.

```json
{
  "score": {
    "default": { "rateWeight": 0.8, "volWeight": 0.2, "shrinkC": 15, "knee": 80 },
    "mandalselva": { "rateWeight": 1, "volWeight": 0, "shrinkC": 15, "knee": 80 }
  },
  "sparkline": {
    "otra": { "max": 150, "normal": 94 }
  }
}
```

`sparkline` styrer skaleringen av vannføringsgrafen i banneret — `normal` er referansenivå,
`max` er toppen av y-aksen.

### `nyheter.json`

```json
[
  {
    "id": "N-001",
    "elv": "Mandalselva",
    "sourceType": "side",
    "headline": "Ny bro sperrer adkomst til Sone 3",
    "link": "https://...",
    "startDate": "2026-08-01",
    "stopDate": null
  }
]
```

`sourceType` er `side`, `apen` eller `lukket` og styrer fargemerket i banneret.
`stopDate: null` betyr «vis til den slettes manuelt». ID-er tildeles fortløpende som
`N-001`, `N-002` … Banneret viser kun oppføringer der `startDate ≤ i dag ≤ stopDate`.

### `nyhetskilder.json`

```json
[
  { "id": "K-001", "navn": "Mandalselva Elveeierlag",
    "type": "side", "elv": "Mandalselva", "url": "https://..." }
]
```

Sletter du en kilde, beholder eksisterende nyheter sin `elv` og `sourceType` uendret —
de er kopiert inn ved registrering, ikke slått opp dynamisk.

### `photos_<elv>.json`

```json
[
  { "id": "M-001", "lat": 58.139581, "lon": 7.542667,
    "file": "HaugeB1_20260601_1759.jpg", "caption": "Hauge B1",
    "zone": "Hauge B1", "dateISO": "2026-06-01", "timeUTC": "15:59",
    "vannforing": 72.4, "autoSone": true, "soneAvstandM": 8 }
]
```

`autoSone` viser om sonen ble utledet automatisk fra GPS. `soneAvstandM` er avstanden til
nærmeste sonepunkt — er den over 300 m, bør sonetilordningen kontrolleres manuelt.

---

## Historiske CSV-filer

Disse ligger utenfor repoet og brukes kun ved bygging av nye dashboard-versjoner. Hver
elv har sine egne fallgruver.

**Audna og Lygna** — fangstlogg
Semikolondelt, dato som `DD.MM.YYYY`, kolonner `Dato;Vekt;Fisk;Redskap;Sone;Fisker`.

> ⚠️ Mellom 7 og 26 rader har komma i fiskernavnet, noe som forskyver kolonnene. Filtrer
> alltid radene med et regex på datoformatet før parsing, i stedet for å stole på at
> kolonnetellingen stemmer.

Vannføringsfilene for disse to bruker `DD-MM-YY` — **tosifret årstall**, og semikolon.

**Mandalselva og Otra** — fangstlogg
Kommadelt, ISO-dato `YYYY-MM-DD` i noen eksporter og `DD.MM.YYYY` i andre, sonekolonne
heter `Vald_Sone`, artskolonne `Art`.

> ⚠️ Otra har tomme `Vannføring`-verdier for hele 2019 (datahull hos NVE). Bruk en
> `if val:`-vakt, ellers kræsjer parsingen.
> ⚠️ Otras vannføringsverdier er desimaltall — bruk `round()`, ikke `int()`, ellers
> systematisk underrapportering.

**Sygna** — fangstlogg
Semikolondelt, ISO-dato, sonekolonne `Sone`, kun én sone («Alle åpne soner»).

---

## Soner som ekskluderes

Noen soneverdier finnes i fangstloggene, men skal ikke vises som soner i dashbordene.
De teller fortsatt i elvas totaltall.

| Elv | Ekskluderes |
|---|---|
| Audna | `Alle åpene soner`, `Grunneier`, `Sone2C` |
| Lygna | `Lygna 1 u. private soner`, `Lygna II Kvåsfossen til Lygne` |
| Mandalselva | `Østerland og Malmø laksefiskeri` |
| Otra | `Egen eiendom`, `Egen rettighet` |

Fasit for hvilke soner som er gyldige er `ZONE_INFO` i den enkelte elvs HTML-fil.

---

## Foto og GPS

GPS-koordinater leses fra EXIF. Det er skjørt:

- **Android sin bildevelger stripper EXIF.** Det samme gjør Gmail.
- Koordinatene overlever kun ved bruk av **Kamera-valget direkte i GitHubs
  opplastingsdialog**, eller ved nedlasting fra OneDrive.

Bilder uten GPS kan ikke sonetilordnes automatisk og må registreres manuelt via admin.

**Audna har en egen regel:** bilder fra 2021 eller tidligere hører til Sone 5 (udelt), mens
bilder fra 2022 og senere hører til Sone 5A eller 5B. Nær grensene Sone 2/3 og Sone 7/8
kreves manuell bekreftelse når avstanden overstiger 300 m.
