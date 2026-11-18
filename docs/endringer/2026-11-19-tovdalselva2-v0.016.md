# Tovdalselva2 v0.016 — testklone med det nye kartet fra Otra

**Dato:** 2026-11-19
**Fil:** `tovdalselva2/index.html` (ny)
**Forrige versjon:** `tovdalselva/index.html` v1.015

## Hva ble endret

- **Ny testklone `tovdalselva2/index.html`.** Den er bygd på `audna/index.html` v1.169, som har
  Otra-kartet, fiskemeldingen og elvescoren.
  - Tovdalselvas data er satt inn: soner, koordinater, priser, fangst, vannføring, rekorder,
    bilder, video, NVE-stasjonen Flakksvann og kvoter.
  - Fiskemeldingen bruker Tovdalselvas egne responsfaktorer og `data/nedbor_tovdalselva.json`.
  - Vannføringssliderne går fra 0 til 85 m³/s i steg på 5. Årene går fra 2016 til 2026.
  - Testmerkingen er som i audna2: `noindex`, oransje stripe, ingen GoatCounter, major 0 og
    toppavstand 34/24 px.
- **«Kun laks»-knappen er tatt med.** I Tovdalselva er sjøørret med i fangsttallene, og knappen
  viser bare laks, med egne skaleringskonstanter. Den kan kombineres med «Kun flue».
  - Valget huskes nå også i delbare lenker som `laks=1`, for eksempel
    `#sone=Laksefoss&laks=1`.
- **Alt fra det nye kartet er med:**
  - Kartlagene Kart, Topo og Flyfoto. Flyfoto bruker Esri-nøkkelen.
  - PC- og mobiloppsett, fullskjerm, sonelinjer, ikon midt i sonen og dagsstatus.
  - Delbare lenker og «Hvor er jeg?».
- **Sonepolygoner:** `data/soner_tovdalselva.geojson` dekker alle 7 soner.
  - Vannflatene kommer fra OpenStreetMap: elva, Flakksvannet, Senumstadfjorden,
    Sundtjønnhølen og Herefossfjorden. De er lagret i `data/raw/osm_tovdalselva.json`.
  - Laksefoss, Buhølen og Teinefoss er delsoner av «Sone 4 og 5» og klippes ut av den, fordi
    ordinært sonekort ikke gjelder der.
- **Endringer i `scripts/sonepolygoner.py`:**
  - Nytt valg `"midtlinje": "senterlinje"` bruker den manuelle senterlinja
    (`data/senterlinje_<elv>.geojson`). Elvelinja i OSM har hull gjennom innsjøene.
  - `--hent` virker også uten OSM-veier i spørringen.
  - Nederste sone går nå til munningen også når startpunktet ligger et stykke opp i elva.
    Før slo sammenligningen feil på grunn av avrunding.
  - Polygonfilene for Otra, Audna og Mandalselva blir nøyaktig like med det nye skriptet.
- **Nye, tomme datafiler:** `data/steder_tovdalselva.json` og `data/hendelser_tovdalselva.json`.

Andre filer i samme commit:
- `CLAUDE.md`: Esri-unntaket gjelder også tovdalselva2, og den er lagt inn i repo-kartet.
- `scripts/sonepolygoner.py` og `scripts/sonepolygoner_oppsett.json`.
- `data/soner_tovdalselva.geojson` og `data/raw/osm_tovdalselva.json`.
- `data/steder_tovdalselva.json` og `data/hendelser_tovdalselva.json`.

## Hvorfor

Per Lasse: «Neste elv tovdalselva». Det er samme opplegg som for Audna og Mandalselva.

## Validering

- `python scripts/valider.py tovdalselva2/index.html` — OK. Alle toppnivå-deklarasjoner i
  `tovdalselva/index.html` finnes også i tovdalselva2.
- I nettleseren:
  - 7 polygoner er lastet, og det er ingen JS-feil.
  - `#sone=Laksefoss&laks=1` åpner Laksefoss med «Kun laks» på.
  - `#sone=3` åpner Sone 3.
  - Elvescoren (32 med «Kun laks» ved 10–15 m³/s) og fiskemeldingen er de samme som på dagens
    side.
  - Mobil 375 px: ingen vannrett rulling, og teststripa står på én linje.

## Kjente mangler / oppfølging

- **Sonegrensene bør kontrolleres av Per Lasse**, særlig i Flakksvannet (grensen mellom Sone 3
  og Sone 4 og 5) og øverst i Herefossfjorden.
- Mellom Buhølen og Laksefoss står en smal stripe (ca. 2500 m²) igjen i «Sone 4 og 5», fordi
  koordinatene har et lite mellomrom der.
- **Mangler data:** desinfeksjonsposter, parkering, kortsalg, hendelser og strekninger med
  fiske fra én side. I Sone 2 er østsida privat.
