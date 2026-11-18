# Mandalselva2 v0.064 — testklone med det nye kartet fra Otra

**Dato:** 2026-11-18
**Fil:** `mandalselva2/index.html` (ny)
**Forrige versjon:** `mandalselva/index.html` v1.063

## Hva ble endret

- **Ny testklone `mandalselva2/index.html`.** Den er bygd på `otra/index.html` v1.089, med
  Mandalselvas data satt inn: soner, koordinater, priser, fangst, vannføring, rekorder, bilder,
  video, NVE-stasjonen Kjølemo og kvoter.
  - Vannføringssliderne går fra 15 til 150 m³/s i steg på 5. Årene går fra 2016 til 2025.
  - Testmerkingen er som i otra2: `noindex`, oransje stripe, ingen GoatCounter, major 0 og
    toppavstand 34/24 px.
- **Alt Otra har fått, er med:**
  - Kartlagene Kart, Topo og Flyfoto. Flyfoto bruker Esri-nøkkelen.
  - PC- og mobiloppsett, fullskjerm og forhåndslasting av fliser.
  - Sonelinjer i oversikten, ikon midt i sonen og dagsstatus.
  - Delbare lenker, for eksempel `#sone=Hauge_A`.
  - «Hvor er jeg?» med «Du står i …».
  - Ingen zoom ved klikk på sone, og mobilknappene fra v1.089.
- **Knappene «Desinfisering» og P (parkering)** vises bare når elva har slike data. Mandalselva
  har foreløpig ingen desinfeksjonsposter i `desinfisering.json` og ingen parkering.
- **Sonepolygoner:** `data/soner_mandalselva.geojson` dekker 39 soner, laget fra OpenStreetMap
  (midtlinje vei 5083244, vannflate relasjon 4039102, lagret i `data/raw/osm_mandalselva.json`).
- **`scripts/sonepolygoner.py` har fått nye valg i oppsettet:**
  - `egne_grenser`: hver sone går fra sin egen start til sin egen slutt. Hull mellom valdene
    blir stående, og overlapp mellom naboer går til den minste sonen.
  - `kutt_i_vann`: kuttene måles fra bredd til bredd i vannflaten. Landstripa legges rundt
    vannbiten etterpå, så den ikke henger sammen over et nes i trange svinger.
- **Rettelser i skriptet:**
  - En bit tas også med når mesteparten av midtlinja gjennom den ligger innenfor sonen.
  - Vest og øst regnes nå som venstre og høyre side sett oppover elva. Før ble bare
    x-koordinaten sammenlignet, og det slo feil der elva renner mot øst eller vest.
  - `data/soner_otra.geojson` blir nøyaktig lik med det nye skriptet.
- **Sidene i oppsettet** (vest/øst) er satt ut fra hvilken side av midtlinja start- og
  sluttpunktene ligger på, og stemmer med beskrivelsene (Holmesland på vestsiden).
  - Vest: Fuskeland, Fossefjellene, Furuholmen, Bjørkenes, Smeland, Holmesland, Holmegård og
    Strædethylen.
  - Øst: Bringsdal, Grimefossen, Stoveland, Øvre Nøding, Hauge, Heia og Nedre Nøding.
  - Rundt Storøy er Nodehylen og Laksehylen satt til bare østsiden der de overlapper med
    Strædethylen.
- **Nye, tomme datafiler:** `data/steder_mandalselva.json` og `data/hendelser_mandalselva.json`,
  med samme format som Otra-filene.

Andre filer i samme commit: `CLAUDE.md` (Esri-unntaket gjelder også mandalselva2, og
mandalselva2 er lagt inn i repo-kartet), `scripts/sonepolygoner.py`,
`scripts/sonepolygoner_oppsett.json`, `data/soner_mandalselva.geojson`,
`data/raw/osm_mandalselva.json`, `data/steder_mandalselva.json`,
`data/hendelser_mandalselva.json`.

## Hvorfor

Per Lasse ville ha de samme kartendringene på Mandalselva som på Otra. Han valgte testklone
først, kart med sonepolygoner, og flyfoto med Esri-nøkkelen.

## Validering

- `python scripts/valider.py mandalselva2/index.html` — OK.
- I nettleseren:
  - 39 polygoner og 39 sonelinjer er lastet. Ingen JS-feil og ingen 404.
  - Lenken `#sone=Hauge_A` åpner Hauge A. Klikk på Holmesland A-ikonet holder zoom 15.
  - Flyfoto lastes. Desinfeksjons- og parkeringsknappen er skjult.
  - Mobil 375 px: ingen vannrett rulling, og teststripa står på én linje.
- Forhåndslastingen henter 513 fliser for Topo og Flyfoto.

## Kjente mangler / oppfølging

- **Sone 4** ligger over demningen ved Manflåvann og går gjennom magasinet. Midtlinja i OSM
  stopper ved demningen, så sonen har ikke polygon og vises bare med ikonet ved startpunktet.
- **16 soner har ikke koordinater** og vises ikke i kartet, som i dag: Båtkort, Fuskeland E,
  Fuskeland Nedre, Fuskeland Revestien, Fuskeland privat, Fuskeland Øvre, Hauge B, Haugefossen,
  Haugefossen Vest, Haugefossen Øst, Lakseøya, Nødingfossen, Sandnes fiskeri, Strømmen, Åsefoss
  og Øvre Holum.
- **Sonegrensene** er beregnet ut fra start- og sluttpunktene og bør kontrolleres av Per Lasse,
  særlig rundt Storøy (Nodehylen, Strædethylen og Laksehylen) og i Bringsdal/Fuskeland.
- **Mangler data:** desinfeksjonsposter, parkering, kortsalg og strekninger med fiske fra én
  side.
