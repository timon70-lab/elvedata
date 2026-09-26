# Datakilder og infrastruktur

Revidert mot repoet 2026-09-26.

## API-er
- NVE HydAPI (vannføring). Nøkkel: GitHub Actions-secret + lokal `.env` (`NVE_API_KEY`). Aldri i HTML.
  Live: `ResolutionTime=60`.
- MET Locationforecast (varsel) / Frost API (observert nedbør).
- Inatur laksebørs GraphQL: `laksebors.inatur.no/graphql` — ser åpen ut (ingen auth-cookie observert),
  men er ikke offisielt dokumentert. Vurder å kontakte Inatur om automatisert tilgang.
- SSB (historisk statistikk tilbake til 1993, `ssb_historikk_1993_2015.json`).

## Per elv
| Elv | NVE-stasjon | Inatur riverId | Nedbørspunkt (MET) | Regulert |
|---|---|---|---|---|
| Audna | Gaupefossen 23.8.0 | 621 | Konsmo 58.27/7.40 → `nedbor.json` | Nei |
| Lygna | Tingvatn (Lygne) 24.9.0 | 25 | Eiken 58.4786/7.2083 → `nedbor_lygna.json` | Nei |
| Mandalselva | Kjølemo 22.4.0 | 1542 | — | Ja |
| Otra | Heisel 21.11.0 | 6 | — | Ja |
| Sygna | Søgne 22.22.0 | 717 | Nodeland 58.1551/7.8358 → `nedbor_sygna.json` | Nei |
| Tovdalselva | Flakksvann 20.3.0 | 5 | Hynnekleiv 58.6020/8.4181 → `nedbor_tovdalselva.json` | Nei |

## GitHub Actions og cron
- `nve_cache.yml`: NVE (seks stasjoner) + MET (fire punkter) + `logg_nedbor.py`, `schedule` hver hele time.
- `fangst_pipeline.yml`: Inatur, `schedule` kl. :30 hver time.
- Ekstern cron på cron-job.org trigger i tillegg `nve_cache.yml` kl. :05 og `fangst_pipeline.yml` kl. :35.
- **PAT «elvedata-cron» (cron-job.org) utløper 11./12. juli 2027 — stille feil hvis den ikke fornyes.**
  Sett påminnelse i kalenderen.
- Foto: `foto_pipeline.yml` (push til `bilder/innboks/<elv>/`, alle seks elver),
  `issue_foto_pipeline.yml` (nytt issue), `bulk_foto_pipeline.yml` (manuell, release-zip).
- Engangs-/manuelle jobber for kalibrering: `frost_stasjoner.yml`, `frost_dekning.yml`,
  `frost_hent_nedbor.yml`, `nve_hent_dogn.yml` (kun `workflow_dispatch`).
- Adminpanel `admin/index.html`: skriver via GitHub Contents API med fine-grained PAT i localStorage;
  noindex; ikke lenket fra dashboard.

## Skript (scripts/)
`foto_pipeline.py` (flerelvs innboks), `issue_foto_pipeline.py` (GitHub Issues-staging, omgår 1 GB-grense),
`bulk_unpack.py` (pakker ut release-zip for bulk-foto), `fangst_pipeline.py` (Inatur GraphQL),
`logg_nedbor.py`, `frost_stasjoner.py`, `frost_dekning.py`, `frost_hent_nedbor.py`, `nve_hent_dogn.py`,
`km_ref.py`, `beregn_km.py`, `valider.py` + `jsdom_smoke.js` (validering før commit).

## Datafiler (data/)
`config.json` (scoringvekter + sparkline), `sesong.json` (sesongdatoer for alle kartelver, også de uten
dashboard), `statistikk.json`, `nyheter.json`, `nyhetskilder.json`, `soner.json`,
`vannforing*.json`, `nedbor*.json`, `fangster_<elv>.json`, `photos_<elv>.json`, `videoer_<elv>.json`,
`senterlinje_<elv>.geojson`, `ssb_historikk_1993_2015.json`,
`logg/nedbor_vf_2026.csv`, `logg/nedbor_obs_<elv>.csv`, `logg/vannforing_dogn_<elv>.csv`
(de to siste for Audna, Lygna, Sygna, Tovdalselva), `raw/` (komplette rådata 2016–2026 +
`elvesoner.xlsx`; navnekolonner beholdes, vises aldri). Se `docs/datamodell.md` for formater.

## Analyse og sosialt
- GoatCounter: `elvedata.goatcounter.com` (bevisst uendret navn; Per Lasses egen trafikk filtrert bort).
  Event-tracking på oversiktskartet: markør-åpning, dashboard-klikk, laksebørs-klikk.
- Facebook-gruppe og -side «Elvesona»; YouTube-kanal.
- Tilbakemelding: 💬-lenke til Google Forms i headeren på oversiktskartet (kun der). Erstattes av
  tilbakemeldingssiden under når den er satt i drift.

## Tilbakemeldingsside (runde 1, ikke lenket ennå)
Statisk side kan ikke ha skrivetoken, så innsendinger går via en Cloudflare Worker som holder tokenet
og skriver til et **privat** repo (e-post og fritekst blir aldri offentlig).

```
tilbakemelding/index.html ──POST──► Cloudflare Worker ──Contents API──► elvesona-tilbakemeldinger/tilbakemeldinger.json
                                     (worker/tilbakemelding.js)                    ▲
                                                                  admin/index.html «💬 Tilbakemeldinger»
```

- **Side:** `tilbakemelding/index.html` (`noindex` til den lenkes). Forhåndsutfylling med
  `?elv=&sone=&type=&v=`. `WORKER_URL` øverst i skriptet fylles inn etter deploy; tom verdi viser
  reservelenken (Google-skjemaet). GoatCounter-event `tilbakemelding-sendt-{type}`.
- **Worker:** `worker/tilbakemelding.js` + `worker/wrangler.toml`. CORS kun `elvesona.no` og localhost.
  Honeypot-feltet `website`, lengdegrenser, maks 5 innsendinger per IP per time (KV `RATE`, IP lagres
  kun som SHA-256-hash), retry ved sha-konflikt (409/422). Secret: `GH_TOKEN`.
- **Privat repo:** `timon70-lab/elvesona-tilbakemeldinger`, fil `tilbakemeldinger.json` (liste).
  Post: `{id, mottatt, status: ny|lest|ferdig, type: ide|feil|fangst|annet, elv, sone, melding, epost, side, versjon}`.
- **Admin:** seksjonen «💬 Tilbakemeldinger» leser lista og setter status. Admin-PAT-en må ha tilgang
  til både `elvedata` og `elvesona-tilbakemeldinger`.

**Oppsett (engangs, gjøres av Per Lasse):**
1. Opprett privat repo `elvesona-tilbakemeldinger` med `tilbakemeldinger.json` = `[]`.
2. Fine-grained PAT **kun** for det repoet, Contents: read/write (Workerens token).
3. Legg det nye repoet til på admin-PAT-en (Contents: read/write).
4. I `worker/`: `npx wrangler login` → `npx wrangler kv namespace create RATE` (lim id inn i
   `wrangler.toml`) → `npx wrangler secret put GH_TOKEN` → `npx wrangler deploy`.
5. Sett `WORKER_URL` i `tilbakemelding/index.html` til Worker-URL-en.

Lokal test: `npx wrangler dev` i `worker/`, med `GH_TOKEN=...` i `worker/.dev.vars` (gitignored).
