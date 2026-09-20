# Statistikk v0.035 — rettet to feil påstander i «Om tallene»

**Dato:** 2026-09-20
**Fil:** `statistikk/index.html`
**Forrige versjon:** v0.034

## Hva ble endret

- Avsnittet om 1993–2026-figuren: fjernet påstanden «De to kildene er kryssjekket på
  overlappende år og stemmer på under 1 % avvik for de fleste elv/år». Erstattet med at
  kildene ikke overlapper i tid og derfor ikke kan kontrolleres mot hverandre, og at et
  hopp i kurven rundt 2015/2016 kan være kildeskiftet framfor en endring i elva.
- Avsnittet «Registreringskulturen varierer» omskrevet til «Åpningsdagen skiller seg ut»:
  beskriver nå 1. juni i Tovdalselva, Otra og Mandalselva, ikke «den 1. i måneden».
  Begge mulige forklaringer — reelt fisketrykk på åpningsdagen og samlet innføring —
  står åpne, siden dataene ikke skiller dem.

Andre filer i samme commit: ingen.

## Hvorfor

Begge påstandene ble motbevist ved gjennomgang mot rådata.

Kryssjekken kan ikke ha funnet sted: SSB-serien dekker 1993–2015 og Inatur-loggene
2016–2026, altså null overlappende år. SSB-filas egen merknad sier det samme. Verken
skript, dokument eller datafelt utfører en slik sammenligning. En offentlig metodeside
bør ikke love en validering dataene ikke tillater.

«Den 1. i måneden» stemmer ikke med mønsteret. Toppen ligger nesten utelukkende på
1. juni (2,7–4,1 × månedens dagsnitt), mens 1. juli, 1. august og 1. september ligger
på 0,4–1,3 ×. Det peker mot sesongåpning, ikke etterregistrering ved månedsskifte.

## Validering

- `python scripts/valider.py statistikk/index.html` — OK, alle seks sjekker.
- Kart-UX A–C: ikke relevant. Statistikksiden har verken kart, soner eller slidere
  (null treff på `ctrl-val`, `selectZone`, `showZoneInfo`, `fitBounds`).
- Endringen er ren tekst i `<p>`-elementer; ingen JS eller datastruktur berørt.

## Oppfølging

- **Uavklart:** Sygna-sesongen oppgis som 15. juni–15. september på statistikksiden
  (93-døgnsvindu), men `data/sesong.json` og Sygna-dashboardet sier 15. juli–15. september.
  To sider på samme nettsted motsier hverandre. CLAUDE.md peker på `sesong.json` som kilde,
  så statistikksiden er den som avviker. Er 15. juli riktig, er sammenligningsvinduet
  30 døgn for langt og laks per døgn tilsvarende for lavt. Venter på avklaring mot
  elveeierlaget. Bør inn i `docs/status-og-backlog.md` som teknisk gjeld.
- `data/ssb_historikk_1993_2015.json` har merknaden «sammenhengende serie 1993–2025»,
  men serien går nå til 2026. Utdatert merknad, ikke rettet i denne runden.
- `docs/om-tallene.md` er merket som kildetekst for metodesiden, men beskriver
  sonescoring i dashboardene — ikke figurene på statistikksiden. Den har egne utdaterte
  punkter («alle fem elver» når det er seks; Otra som eneste regulerte elv uten
  fiskemelding, mens Mandalselva også er regulert). Ikke rørt i denne runden.
