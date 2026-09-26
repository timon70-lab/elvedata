# Status, teknisk gjeld og backlog

Overført fra claude.ai-prosjektet 2026-09-20. Revidert mot repoet 2026-09-26.

## Versjoner (per 2026-09-26)
Øyeblikksbilde — gjeldende versjon finnes alltid med `grep -oE 'v[0-9]+\.[0-9]{3}' <fil>`.
- Audna v1.164 · Lygna v1.066 · Mandalselva v1.060 · Otra v1.044 · Sygna v1.043 · Tovdalselva v1.012
- Alle seks elver ligger på oversiktskartet (Tovdalselva gikk live v0.009 → v1.010).
- Oversiktskart (`index.html`) v1.054 · Staging v1.034 · Statistikk (`statistikk/index.html`) v0.036
- Sesongsider `statistikk/{elv}2026.html` for alle seks elver (v1.001–v1.002).

## Aktive funksjoner (alle seks elver)
Sonescoring-pipeline · frikoblet elvenivå-score (Audna, Lygna, Tovdalselva — de øvrige bruker
fangstvektet snitt av sonescorene) · foto-/video-pipelines med km-sortering · kalibrert
fiskemelding (uregulerte: Audna, Lygna, Sygna, Tovdalselva) · rekorddag-popup («Les mer →») ·
fullskjermkart · flow-bin-stepper (‹ 💧 bin ›) i foto/video-panel · fetch-basert `photos_<elv>.json`
i alle seks · `data/sesong.json` som felles sesongkilde · GoatCounter-events · sonebevisste
sesongvinduer på kartet · nyhetsbanner (`data/nyheter.json`, CRUD i admin) · nedbørslogging ·
statistikkside med animerte grafer, SSB-data, sammenleggbare seksjoner.
Admin har seksjonene Nyheter, Media, Sesong, Scoringsparametre og Nøkler og tilgang.

## Kjent teknisk gjeld
- `P90_RATE_ELV`/`P90_VOL_ELV` kan ikke reproduseres fra embeddede data i Lygna. (Tidligere også
  notert for Otra, men Otra har ikke lenger egne ELV-konstanter.)
- Otra og Sygna mangler i `issue_foto_pipeline.py` (som også har en utdatert feilmelding som bare
  nevner audna/mandalselva/lygna).
- `fangst_pipeline.yml` committer ikke `data/fangster_tovdalselva.json`: skriptet henter Tovdalselva
  (riverId 5), men `git add`-linjen i workflowen lister bare de fem andre. Fila finnes derfor ikke
  i repoet, selv om oversiktskartet peker på den (`catchUrl`).
- Sone 5A/5B-grense i Audna: ~670 m avvik mellom pipeline og dashboard.
- Mandalselva `ZONE_INFO` sier fortsatt «Alt fiske stoppes ved vanntemperatur over 21 °C», selv om
  21 °C-stoppen ikke lenger er del av kvotesettet (jf. `docs/kvoter-2026.md`).
- `videoer_audna.json`: `vannforing: 0` betyr «ikke registrert» — admin bør skrive `null`.
- To ulike Google Forms-lenker for tilbakemelding (💬 på oversiktskartet vs. nyhet N-006).

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
- Egen tilbakemeldingsside (erstatter Google Forms) — se `docs/ideer/tilbakemeldingsside.md`.
