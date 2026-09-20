# Status, teknisk gjeld og backlog

Overført fra claude.ai-prosjektet 2026-09-20. Status sist registrert 2026-09-06 — verifiser mot repoet.

## Versjoner (per 2026-09-06)
- Audna v1.160 · Lygna v1.062 · Mandalselva v1.055 · Otra v1.038 · Sygna v1.038
- Tovdalselva v0.006 (ikke på oversiktskartet; go-live blir v1.007+)
- Oversiktskart (`index.html`) v1.047 · Statistikk (`statistikk/index.html`) v0.013
- Sesongoppsummeringer 2026 laget som frittstående HTML + Facebook-poster for Otra, Lygna, Audna, Tovdalselva.

## Aktive funksjoner (alle seks elver)
Sonescoring-pipeline og frikoblet elvenivå-score · foto-/video-pipelines med km-sortering ·
fiskemelding (uregulerte) · rekorddag-popup («Les mer →») · fullskjermkart · flow-bin-stepper
(‹ 💧 bin ›) i foto/video-panel · `data/sesong.json` som felles sesongkilde · GoatCounter-events ·
sonebevisste sesongvinduer på kartet · nyhetsbanner (`data/nyheter.json`, CRUD i admin) ·
nedbørslogging · statistikkside med animerte grafer, SSB-data, sammenleggbare seksjoner.
Admin har Sesong-, Media- og scoringparameter-seksjoner.

## Kjent teknisk gjeld
- `P90_RATE_ELV`/`P90_VOL_ELV` kan ikke reproduseres fra embeddede data i Otra eller Lygna.
- Otra og Sygna mangler i `issue_foto_pipeline.py`.
- Sone 5A/5B-grense i Audna: ~670 m avvik mellom pipeline og dashboard.
- Mandalselva `fetchNedbor()` har fortsatt aktiv nedbørsterskel-fiskemelding selv om elva er regulert.
- Lygna-dashboardet er ikke konvertert til fetch-basert PHOTOS-mønster (pipeline klar).
- Tovdalselva ikke lagt til oversiktskartet (venter på eksplisitt go-live).
- `videoer_audna.json`: `vannforing: 0` betyr «ikke registrert» — admin bør skrive `null`.

## Horisont
- Tovdalselva go-live på oversiktskartet (v1.007).
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
- (g) Fiskeområde-polygoner tegnet i geojson.io med Inatur-kart som referanse → `data/soner_<elv>.geojson`,
  med disclaimer om at Inatur-kartet kun er veiledende.
- (k) Brukerbidrag med sonetips via Google Forms → admin-moderering → `data/tips_<elv>.json`.
  Åpne spørsmål: kreditering, konflikt med grunneiere, tidløshet.
- Video etter vannføring i sonepanel (mockup for Audna; blokkert av `vannforing: 0`-problemet).
- Nåtidsrelevans i scoring: fallende fangstrater i Audna, Lygna, Mandalselva. Alternativer:
  recency-vekting, rullerende 5-årsvindu, eller tydeligere «historisk sonekvalitet». Vent på full 2026-data.
- Sesongoppsummering som lavsesonginnhold (nesten fullt automatiserbar).
- Oversiktskart: sesongtotal eller nedtelling på stengte markører; «planleggingsmodus» i dashboard.
- Turlogg / fangstregistrering — se `docs/ideer/turlogg.md`.
