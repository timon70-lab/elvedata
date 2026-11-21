# Status, teknisk gjeld og backlog

Overført fra claude.ai-prosjektet 2026-09-20. Revidert mot repoet 2026-09-26 og 2026-11-21.

## Versjoner (per 2026-11-21)
Øyeblikksbilde — gjeldende versjon finnes alltid med `grep -oE 'v[0-9]+\.[0-9]{3}' <fil>`.
- Audna v1.171 · Lygna v1.074 · Mandalselva v1.068 · Otra v1.091 · Sygna v1.050 · Tovdalselva v1.020
- Alle seks elver ligger på oversiktskartet (Tovdalselva gikk live v0.009 → v1.010).
- Oversiktskart (`index.html`) v1.064 · Staging v1.035 · Statistikk (`statistikk/index.html`) v0.038
- Sesongsider `statistikk/{elv}2026.html` for alle seks elver (v1.001–v1.002).

## Aktive funksjoner (alle seks elver)
Sonescoring-pipeline · frikoblet elvenivå-score (Audna, Lygna, Tovdalselva — de øvrige bruker
fangstvektet snitt av sonescorene) · foto-/video-pipelines med km-sortering · kalibrert
fiskemelding (uregulerte: Audna, Lygna, Sygna, Tovdalselva) · rekorddag-popup («Les mer →») ·
fullskjermkart · flow-bin-stepper (‹ 💧 bin ›) i foto/video-panel · fetch-basert `photos_<elv>.json`
i alle seks · `data/sesong.json` som felles sesongkilde · GoatCounter-events · sonebevisste
sesongvinduer på kartet · nyhetsbanner (`data/nyheter.json`, CRUD i admin) · nedbørslogging ·
statistikkside med animerte grafer, SSB-data, sammenleggbare seksjoner.
Det nye kartet (2026-11-17 – 2026-11-20, først i Otra): kartlagene Kart/Topo/Flyfoto (Esri),
sonepolygoner (`data/soner_<elv>.geojson`), PC-layout med kartet som hovedflate, sonelinjer på lav
zoom, dagsstatus, delbare lenker, «Hvor er jeg?» med «Du står i …», steder og hendelser
(`data/steder_<elv>.json`, `data/hendelser_<elv>.json`) og feltregistrering av punkter
(`felles/registrering.js`, bare med admin-token).
Admin har seksjonene Nyheter, Media, Sesong, Tilbakemeldinger, Feltpunkter, Scoringsparametre og
Nøkler og tilgang.

## Kjent teknisk gjeld
- Desinfeksjonsposter finnes kun i Otra. Koden (`fetchDesinf`, `nearestPost`, «Nærmeste
  desinfeksjonspost»-knappen, `desinfZoneHtml`) er med i alle seks kart etter kartoppgraderingen;
  det som mangler, er postene for de fem andre elvene i `data/desinfisering.json`.
- Parkering, kortsalg og hendelser finnes kun for Otra. De andre elvene har tomme
  `steder_<elv>.json` og `hendelser_<elv>.json`.
- `P90_RATE_ELV`/`P90_VOL_ELV` kan ikke reproduseres fra embeddede data i Lygna. (Tidligere også
  notert for Otra, men Otra har ikke lenger egne ELV-konstanter.)
- Otra og Sygna mangler i `issue_foto_pipeline.py` (som også har en utdatert feilmelding som bare
  nevner audna/mandalselva/lygna).
- Sone 5A/5B-grense i Audna: ~670 m avvik mellom pipeline og dashboard.
- Mandalselva `ZONE_INFO` sier fortsatt «Alt fiske stoppes ved vanntemperatur over 21 °C», selv om
  21 °C-stoppen ikke lenger er del av kvotesettet (jf. `docs/kvoter-2026.md`).
- `videoer_audna.json`: `vannforing: 0` betyr «ikke registrert» — admin bør skrive `null`.

## Horisont
- AI-synlighet: robots.txt, sitemap.xml, statisk HTML-innhold, schema.org, llms.txt,
  bot-allowlist (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Bingbot).
- Lavsesong: nåtidsrelevans i scoring, innsatsjustering, fullføre kalibrering.
- Gytefisktellinger fra elveeierlag okt/nov — anledning til dialog om innsatsdata.

## Backlog (loggført, ikke implementert)
- (b) Facebook-lenker per elv i dashboard/oversiktskart.
- (c) **Prioritet:** innsats- og kvotejustering i score — fangst per kortdøgn i stedet for kalenderdøgn.
  Case: Strædethylen (Mandalselva) 16 laks 2016–2025, null etter 2021, men nesten ingen kjøpere.
  Støttecase: Otra 2026 (+~16 % fiskere), Audna Sone 4 Berge øvre (én fluefisker dominerer),
  Lygna Øyvind Kleiven-analysen. Inatur-webshopkalender som proxy for fisketrykk.
- (g) Sonepolygoner → `data/soner_<elv>.geojson`. **Gjort for alle seks (2026-11-17 – 2026-11-20)**:
  polygonene regnes ut av `scripts/sonepolygoner.py` fra OSM-elveflaten + kutt vinkelrett på
  midtlinja ved sonepunktene (oppsett i `scripts/sonepolygoner_oppsett.json`). Gjenstår grensesjekk,
  helst med feltpunkter eller koordinater fra elveeierlagene:
  - Lygna: de fleste grensene er beregnet og merket «omtrentlig».
  - Audna Sone 1–3 (mulig overlapp) og Tovdalselva i Flakksvannet og Herefossfjorden.
  - Otra 3B Hageodden og 4B Ravnås har begge punktene på én bredd — kanskje bare én side?
  - Strekninger med fiske fra én side (f.eks. Tovdalselva Sone 2, der østsida er privat).
- (k) Brukerbidrag med sonetips via Google Forms → admin-moderering → `data/tips_<elv>.json`.
  Åpne spørsmål: kreditering, konflikt med grunneiere, tidløshet.
- Video etter vannføring i sonepanel (mockup for Audna; blokkert av `vannforing: 0`-problemet).
- Nåtidsrelevans i scoring: fallende fangstrater i Audna, Lygna, Mandalselva. Alternativer:
  recency-vekting, rullerende 5-årsvindu, eller tydeligere «historisk sonekvalitet». Vent på full 2026-data.
- Sesongoppsummering som lavsesonginnhold (nesten fullt automatiserbar).
- Oversiktskart: sesongtotal eller nedtelling på stengte markører; «planleggingsmodus» i dashboard.
- Turlogg / fangstregistrering — se `docs/ideer/turlogg.md`.
- Kartløsning: **live i alle seks elver** (Otra v1.078 2026-11-17, deretter Mandalselva, Audna,
  Tovdalselva, Sygna og Lygna til 2026-11-20). Testklonene `{elv}2` er slettet; `otra2` står igjen.
  Gjenstår: admin kan ikke redigere `ukedager`/`steder_<elv>.json` og har ingen bryter for `stengt`;
  parkeringer og kortsalg for de fem andre elvene; offline-kart (på is). Ikke målt: tomme fliser ved
  panorering/zoom i de fem siste kartene (samme kode som Otra).
  Se `docs/ideer/otra-kart-forbedringer.md`.
- Egen tilbakemeldingsside — runde 1 (Worker, side, admin) er bygd, men ikke satt i drift eller lenket.
  Neste runder: lenke fra alle seks dashboard, statistikk og 💬 på oversiktskartet; deretter
  «Stemte dette? 👍/👎» under topp 3. Se `docs/ideer/tilbakemeldingsside.md`.
