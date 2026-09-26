# Automatisering

Workflows, planlagte jobber og hemmeligheter.

> Sist konsolidert mot koden: **2026-09-26**. Senere endringer står i
> [`docs/endringer/`](endringer/).

---

## ⏰ Utløpskalender

Les denne først. Alle punktene under feiler **stille** — ingenting krasjer, dataene
slutter bare å oppdatere seg.

| Hva | Utløper | Symptom ved utløp | Deteksjon |
|---|---|---|---|
| `elvedata-cron` (PAT for cron-job.org) | **11. juli 2027** | Vannføring og fangster fryser | Varsling fra cron-job.org |
| Admin-PAT (fine-grained) | Selvvalgt | Lagring i admin feiler | Feilmelding i admin |
| NVE API-nøkkel | Ingen kjent utløpsdato | Tomme vannføringsfiler | Ingen |

Fornyelse av cron-tokenet: nytt fine-grained PAT med **Actions: read/write** på kun
`elvedata`-repoet, deretter oppdatere det i cron-job.org-jobbene.

---

## Workflows

Alle ligger i `.github/workflows/`.

### `nve_cache.yml` — vannføring og nedbør

Kjerneworkflowen. Kjører hver time og henter:

- Vannføring fra NVE HydAPI for alle seks stasjoner, `ResolutionTime=60`, `ReferenceTime=P7D`
- Nedbørsprognose fra MET for fire punkter (Konsmo/Audna, Eiken/Lygna, Nodeland/Sygna,
  Hynnekleiv/Tovdalselva)

Deretter kjører `scripts/logg_nedbor.py`, som logger varslet nedbør mot vannføring i
`data/logg/nedbor_vf_2026.csv`.

Verifiserer at hver fil faktisk lot seg parse før commit, og pusher med inntil fem
forsøk med `git pull --rebase` mellom hvert — nødvendig fordi flere workflows kan skrive
samtidig.

Krever hemmeligheten `NVE_API_KEY`.

### `fangst_pipeline.yml` — ferske fangster

Kjører `scripts/fangst_pipeline.py`, som henter siste 72 timer fra Inaturs GraphQL-endepunkt.
Planlagt på **:30 over hver time** for ikke å kollidere med NVE-cachen på hel time.

Kun laks, bortsett fra Sygna og Tovdalselva som også tar med sjøørret. Fiskernavn hentes aldri inn.

> ⚠️ Skriptet henter seks elver, men `git add`-steget i workflowen lister bare fem —
> `data/fangster_tovdalselva.json` blir derfor aldri committet.

### `foto_pipeline.yml` — bildeprosessering

Utløses av push til `bilder/innboks/<elv>/` (alle seks elver). Leser EXIF, henter GPS, finner nærmeste sone,
komprimerer til maks 1600 px bredde, stripper EXIF og skriver til `photos_<elv>.json`.

Bruker `concurrency: foto-pipeline` for å hindre at to bildejobber skriver samtidig.

### `issue_foto_pipeline.yml` — opplasting via issue

Utløses når et nytt GitHub-issue åpnes. Parser `<img src="...">` fra issue-teksten og
laster ned bildene derfra.

Finnes fordi bilder lastet opp til et issue lagres på GitHubs eget CDN og **ikke** teller
mot repoets 1 GB-grense. Det er den anbefalte veien for større mengder bilder.

Elva leses fra issue-tittelen. Støtter Audna, Lygna, Mandalselva og Tovdalselva — **ikke**
Otra og Sygna. Bruker også `NVE_API_KEY` for å slå opp vannføring på bildetidspunktet.

### `bulk_foto_pipeline.yml` — masseopplasting

Manuell utløsning med en release-tag som parameter. Forventer en zip med undermapper per
elv (pakkes ut av `scripts/bulk_unpack.py`, deretter kjøres `foto_pipeline.py`). Brukes ved
engangsimport av store bildesamlinger. Deler `concurrency: foto-pipeline` med foto-pipelinen.

### Manuelle kalibreringsjobber

Kun `workflow_dispatch`, normalt kjørt én gang. Grunnlaget for fiskemeldingens responsfaktorer:

| Workflow | Gjør |
|---|---|
| `frost_stasjoner.yml` | Finner kandidatstasjoner for nedbør nær hver elv (`data/logg/frost_stasjoner.md`) |
| `frost_dekning.yml` | Måler datadekning 2016–2025 for kandidatene (`data/logg/frost_dekning.md`) |
| `frost_hent_nedbor.yml` | Henter observert døgnnedbør 2016–2025 (`data/logg/nedbor_obs_<elv>.csv`) |
| `nve_hent_dogn.yml` | Henter døgnvannføring 2016–2025, 06–06-døgn (`data/logg/vannforing_dogn_<elv>.csv`) |

---

## Ekstern planlegging

GitHub sin egen `schedule`-utløser er ikke pålitelig — jobber kan bli forsinket eller
hoppet over under last på plattformen. Derfor kaller **cron-job.org** i tillegg
workflowene via `workflow_dispatch`:

| Jobb | Tidspunkt |
|---|---|
| `nve_cache.yml` | Hver time, :05 |
| `fangst_pipeline.yml` | Hver time, :35 |

Dette betyr at hver workflow i praksis har to utløsere. Det er tilsiktet redundans, ikke
en feil — kjøringene er idempotente, og en ekstra kjøring gjør ingen skade utover å bruke
litt kvote.

---

## Hemmeligheter og tilgang

| Navn | Hvor lagret | Rekkevidde |
|---|---|---|
| `NVE_API_KEY` | GitHub Secrets + lokal `.env` | Actions (`nve_cache`, `issue_foto_pipeline`) og lokale skript |
| NVE-nøkkel i admin | `localStorage` i din nettleser | Vannføringsoppslag ved videoregistrering |
| `elvedata-cron` | cron-job.org | Actions read/write, kun `elvedata` |
| Admin-PAT | `localStorage` i din nettleser | Contents read/write, kun `elvedata` |

**NVE-nøkkelen skal aldri hardkodes i en HTML-fil.** Den hører hjemme i GitHub Secrets og
brukes serverside i Actions. Dashbordene leser ferdig mellomlagrede JSON-filer, aldri
NVE direkte. Eneste unntak er adminpanelet, der du selv limer inn nøkkelen og den bare
lagres i din egen nettleser.

Admin-PAT ligger kun lokalt i nettleseren din. Bytter du enhet, må du opprette et nytt —
GitHub viser aldri en eksisterende tokenverdi på nytt.

---

## Feilmoduser verdt å kjenne

**Push-konflikt mellom workflows.** To jobber som pusher samtidig gir avvist push.
`nve_cache.yml` håndterer dette med fem forsøk og rebase. Skjer det likevel, kjør
workflowen på nytt manuelt.

**Tomme JSON-filer.** Hvis NVE svarer med feil, kan en fil bli skrevet med feilmeldingen
som innhold. Verifiseringssteget i workflowen fanger dette opp og feiler jobben før
commit — men bare for filene som verifiseres eksplisitt.

**Stille cron-stopp.** Se utløpskalenderen øverst. Dette er den mest sannsynlige årsaken
hvis alt plutselig slutter å oppdatere seg uten synlige feil noe sted.
