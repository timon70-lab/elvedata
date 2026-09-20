# Datakilder og infrastruktur

## API-er
- NVE HydAPI (vannføring). Nøkkel: GitHub Actions-secret + lokal `.env` (`NVE_API_KEY`). Aldri i HTML.
  Live: `ResolutionTime=60`.
- MET Locationforecast (varsel) / Frost API (observert nedbør).
- Inatur laksebørs GraphQL: `laksebors.inatur.no/graphql` — ser åpen ut (ingen auth-cookie observert),
  men er ikke offisielt dokumentert. Vurder å kontakte Inatur om automatisert tilgang.
- SSB (historisk statistikk tilbake til 1993, `ssb_historikk_1993_2015.json`).

## Per elv
| Elv | NVE-stasjon | Inatur riverId | Regulert |
|---|---|---|---|
| Audna | Gaupefossen 23.8.0 | 621 | Nei |
| Lygna | Tingvatn (Lygne) 24.9.0 | 25 | Nei |
| Mandalselva | Kjølemo 22.4.0 | 1542 | Ja |
| Otra | Heisel 21.11.0 | 6 | Ja |
| Sygna | Søgne 22.22.0 | 717 | Nei |
| Tovdalselva | Flakksvann 20.3.0 | (ikke registrert i prosjektet — finn på laksebors.inatur.no/bors/{id}) | Nei |

## GitHub Actions og cron
- `nve_cache.yml` (NVE + MET, hver time), `fangst_pipeline.yml` (Inatur, hver time).
- Ekstern cron på cron-job.org trigger `nve_cache.yml` kl. :05 og `fangst_pipeline.yml` kl. :35.
- **PAT «elvedata-cron» (cron-job.org) utløper 11./12. juli 2027 — stille feil hvis den ikke fornyes.**
  Sett påminnelse i kalenderen.
- Adminpanel `admin/index.html`: skriver via GitHub Contents API med fine-grained PAT i localStorage;
  noindex; ikke lenket fra dashboard.

## Skript (scripts/)
`foto_pipeline.py` (flerelvs innboks), `issue_foto_pipeline.py` (GitHub Issues-staging, omgår 1 GB-grense),
`fangst_pipeline.py` (Inatur GraphQL), `logg_nedbor.py`, `frost_hent_nedbor.py`, `nve_hent_dogn.py`,
`km_ref.py`, `beregn_km.py`, `valider.py` (ny).

## Datafiler (data/)
`config.json` (scoringvekter), `sesong.json` (sesongdatoer + tillegg for elleve kartelver),
`statistikk.json`, `nyheter.json`, `soner.json`, `all_river_zones.json`,
`videoer_<elv>.json`, `logg/nedbor_vf_2026.csv`, `logg/nedbor_obs_<elv>.csv`,
`logg/vannforing_dogn_<elv>.csv`, `raw/` (komplette rådata 2016–2026 + `elvesoner.xlsx`; navnekolonner beholdes, vises aldri).

## Analyse og sosialt
- GoatCounter: `elvedata.goatcounter.com` (bevisst uendret navn; Per Lasses egen trafikk filtrert bort).
  Event-tracking på oversiktskartet: markør-åpning, dashboard-klikk, laksebørs-klikk.
- Facebook-gruppe og -side «Elvesona»; YouTube-kanal; Google Forms-tilbakemelding i oversiktskartet.
