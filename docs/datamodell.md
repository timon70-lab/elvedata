# Datamodell

Referanse over datafilene i `data/`, hvem som skriver dem, og hvilke særegenheter man må
kjenne til.

> Sist konsolidert mot koden: **2026-09-26**. Senere endringer står i
> [`docs/endringer/`](endringer/).

---

## Filoversikt

| Fil | Skrives av | Frekvens | Konsekvens hvis borte |
|---|---|---|---|
| `config.json` | Admin-panelet | Manuelt | Dashbordene bruker innebygget fallback |
| `sesong.json` | Admin-panelet | Manuelt | Sesongrad og kartmarkører mangler datoer |
| `vannforing.json` (Audna) | `nve_cache.yml` | Hver time | Live-vannføring vises ikke |
| `vannforing_<elv>.json` (øvrige fem) | `nve_cache.yml` | Hver time | Samme |
| `nedbor.json` (Audna) | `nve_cache.yml` | Hver time | Fiskemelding skjules stille |
| `nedbor_lygna.json`, `nedbor_sygna.json`, `nedbor_tovdalselva.json` | `nve_cache.yml` | Hver time | Samme |
| `fangster_<elv>.json` | `fangst_pipeline.py` | Hver time | «Fangst siste 3 dager» utelates på oversiktskartet |
| `photos_<elv>.json` | Foto-pipelines / admin | Ved opplasting | Bildegalleri tomt |
| `videoer_<elv>.json` | Admin-panelet | Manuelt | Videogalleri tomt |
| `nyheter.json` | Admin-panelet | Manuelt | Nyhetsbanner skjules |
| `nyhetskilder.json` | Admin-panelet | Manuelt | Kildevelger tom |
| `soner.json` | Manuelt | Ved soneendring | Admin-nedtrekk tomme |
| `statistikk.json` | Manuelt | Ved ny statistikk | Statistikksiden tom |
| `senterlinje_<elv>.geojson` | Manuelt (leses av `beregn_km.py`) | Sjelden | Nye medier får ikke `km` og sorteres på breddegrad |
| `logg/*.csv` | `nve_cache.yml` / manuelle kalibreringsjobber | Hver time / engang | Ingen synlig effekt |

`fangster_tovdalselva.json` finnes ikke i repoet: workflowens `git add` mangler den (se
[automatisering.md](automatisering.md)).

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
    "default": { "rateWeight": 0.8, "volWeight": 0.2, "shrinkC": 15, "shrinkCElv": 15, "knee": 80 },
    "mandalselva": { "rateWeight": 1, "volWeight": 0, "shrinkC": 15, "shrinkCElv": 15, "knee": 80 }
  },
  "sparkline": {
    "default": { "max": 12, "normal": 6.5 },
    "otra": { "max": 150, "normal": 94 }
  }
}
```

Alle seks elver har egen oppføring under både `score` og `sparkline`. `shrinkCElv` brukes kun
av elvenivå-scoren i Audna, Lygna og Tovdalselva (satt til 8 der).

### `sesong.json`

```json
{
  "_meta": { "endret": "2026-08-25", "av": "admin", "notat": "...", "format": { ... } },
  "elver": {
    "otra": {
      "start": "06-15", "slutt": "08-17", "tillegg": "(2026)",
      "soner": {
        "Sone 5B Rød": { "start": "07-01", "slutt": "08-17", "tillegg": "..." },
        "Sone 5B Øst": { "start": null, "slutt": null, "tillegg": "—", "stengt": true }
      }
    }
  }
}
```

Datoer er `MM-DD`. `soner` lister kun soner som avviker; `null` betyr arv fra elva, og
`stengt: true` markerer en stengt sone. Fila har også oppføringer for kartelver uten dashboard
(Storelva, Nidelva, Kvina m.fl.) — for dem brukes bare `start`/`slutt` på oversiktskartet.

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
    "zone": "Hauge B1", "dateISO": "2026-06-01", "timeUTC": "15:59", "locId": "Hauge B1",
    "vannforing": 72.4, "autoSone": true, "soneAvstandM": 8, "km": 16.33 }
]
```

`autoSone` viser om sonen ble utledet automatisk fra GPS. `soneAvstandM` er avstanden til
nærmeste sonepunkt — er den over 300 m, bør sonetilordningen kontrolleres manuelt.
`km` er avstand fra munningen langs senterlinja (`beregn_km.py`) og styrer sorteringen i
galleriet; mangler den, sorteres det på breddegrad. Manuelt registrerte oppføringer kan ha
`adkomstLat`/`adkomstLon` for «Ta meg dit»-lenken.

### `videoer_<elv>.json`

Som bildene, men med `youtubeId` i stedet for `file`. `vannforing: 0` betyr i praksis «ikke
registrert» (kjent gjeld — bør være `null`).

---

## Historiske CSV-filer (`data/raw/`)

Komplette og uendrede fangstlogger og vannføringsserier 2016–2026, pluss `elvesoner.xlsx`.
Brukes kun ved bygging av nye dashboard-versjoner. Navnekolonnene (`Fisker`/`Navn`) beholdes
i rådata, men skal aldri embeddes eller vises. Hver elv har sine egne fallgruver — sjekk
alltid headeren før parsing (flere filer har UTF-8-BOM).

| Fil | Skilletegn | Dato | Kolonner |
|---|---|---|---|
| `AudnaFangstlogg20162026.csv` | `;` | `DD.MM.YYYY` | `Dato;Vekt;Fisk;Redskap;Sone;Fisker` |
| `LygnaFangstlogg20162026.csv` | `;` | `DD.MM.YYYY` | `Dato;Vekt;Fisk;Redskap;Sone;Fisker` |
| `TovdalselvaFangstlogg20162026.csv` | `;` | `DD.MM.YYYY` | `Dato;Vekt;Fisk;Redskap;Sone;Fisker` |
| `mandalselva_siste_fangster_2016_2026.csv` | `,` | `DD.MM.YYYY` | `Aar,Dato,Vekt_kg,Art,Redskap,Vald_Sone,Navn,Satt_ut,Oppdrett` |
| `OtraFangstlogg20162026.csv` | `,` | `DD.MM.YYYY` | Som Mandalselva |
| `Sygna_fangstlogg_2016_2026.csv` | `;` | `YYYY-MM-DD` | `Dato;Vekt;Fisk;Redskap;Sone` |
| `AudnaVannforing20162026.csv`, `LygnaVannforing20162026.csv` | `;` | `DD-MM-YY` (**tosifret år**) | `Dato;Vannføring` |
| `Mandalselva…`, `Otra…`, `TovdalselvaVannforing20162026.csv` | `,` | ISO med tid og `Z` | `Dato,Vannføring` |
| `Sygna_vannforing_2016_2026.csv` | `;` | `YYYY-MM-DD` | `Dato;Vannforing_m3s` |

> ⚠️ Audna/Lygna: mellom 7 og 26 rader har komma i fiskernavnet, noe som forskyver
> kolonnene. Filtrer alltid radene med et regex på datoformatet før parsing, i stedet for å
> stole på at kolonnetellingen stemmer.
> ⚠️ Otra har tomme `Vannføring`-verdier for hele 2019 (datahull hos NVE). Bruk en
> `if val:`-vakt, ellers kræsjer parsingen.
> ⚠️ Otras vannføringsverdier er desimaltall — bruk `round()`, ikke `int()`, ellers
> systematisk underrapportering.

Sygna har kun én sone («Alle åpne soner»). Sygna og Tovdalselva har både laks og sjøørret i
`Fisk`-kolonnen; øvrige pipelines filtrerer på laks.

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
