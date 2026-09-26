# Arkitektur

Oversikt over hvordan Elvedata er satt sammen, og hvorfor.

> Sist konsolidert mot koden: **2026-09-26**. Senere endringer står i
> [`docs/endringer/`](endringer/).

---

## Kort oppsummert

Elvedata er en **ren statisk nettside** på GitHub Pages. Det finnes ingen server, ingen
database og ingen backend-kode som kjører når en besøkende åpner siden. Alt består av
HTML-filer med innebygget JavaScript, pluss noen JSON-filer som oppdateres av
planlagte jobber i bakgrunnen.

Denne begrensningen forklarer nesten alle designvalgene lenger ned i dokumentet.

---

## Komponenter

| Del | Sti | Rolle |
|---|---|---|
| Oversiktskart | `index.html` | Landingsside, kart over alle elvene, nyhetsbanner |
| Elve-dashboard × 6 | `audna/`, `lygna/`, `mandalselva/`, `otra/`, `sygna/`, `tovdalselva/` | Sonekart, score, historikk, media |
| Statistikk | `statistikk/index.html`, `statistikk/{elv}2026.html` | Statistikkside og sesongside per elv |
| Admin-panel | `admin/index.html` | Redigering av nyheter, kilder, media, sesong, scoreparametre |
| Staging | `staging/index.html` | Testversjon av oversiktskartet før publisering |
| Data | `data/*.json` | Mellomlagrede data fra eksterne kilder |
| Rådata | `data/raw/` | Komplette fangstlogger og vannføringsserier 2016–2026 |
| Bilder | `bilder/<elv>/` | Sonebilder lastet opp via foto-pipeline |
| Pipelines | `.github/workflows/`, `scripts/` | Automatisk henting og prosessering |

Hver elv er én selvstendig HTML-fil. Det er ingen delt kodebase eller byggesteg mellom
dem — endringer må derfor gjentas per elv. Det er tungvint, men holder hver elv isolert
og gjør at en feil i én elv ikke kan velte de andre.

---

## Hvor dataene kommer fra

**NVE HydAPI** — vannføring
Hentes hver time av `nve_cache.yml` og lagres i `data/vannforing*.json`. Alltid med
`ResolutionTime=60` (timesoppløsning). Døgnmiddel (`1440`) må ikke brukes, da det
ligger omtrent et døgn etter virkeligheten og gjør «live»-visningen misvisende.

**MET locationforecast** — nedbørsprognose
Hentes hver time av samme workflow. Merk at dette er **modellert punktprognose**, ikke
observasjoner fra en fysisk målestasjon. Punktet velges per nedbørfelt:

| Fil | Punkt | Brukes av |
|---|---|---|
| `data/nedbor.json` | 58.27 N, 7.40 Ø (Konsmo, 328 moh.) | Audna |
| `data/nedbor_lygna.json` | 58.4786 N, 7.2083 Ø (Eiken, 189 moh.) | Lygna |
| `data/nedbor_sygna.json` | 58.1551 N, 7.8358 Ø (Nodeland) | Sygna |
| `data/nedbor_tovdalselva.json` | 58.6020 N, 8.4181 Ø (Hynnekleiv) | Tovdalselva |

Lygna fikk eget punkt fordi Konsmo-punktet ligger i Audnas nedbørfelt, på feil side av
vannskillet. Sammenligning viste at Eiken-punktet konsekvent får mer nedbør, noe som
gjorde fiskemeldingen for Lygna systematisk for konservativ.

**Inatur GraphQL** — ferske fangster
Hentes av `fangst_pipeline.py` til `data/fangster_<elv>.json`. Kun laks, bortsett fra
Sygna og Tovdalselva som også tar med sjøørret. Fiskernavn hentes aldri inn. Filene brukes
av oversiktskartet, ikke av dashbordene.

**Historisk fangstlogg og vannføring** — CSV, manuelt vedlikeholdt
Ligger i `data/raw/` (komplette og uendrede, inkludert navnekolonner som aldri vises) og brukes
til å forhåndsberegne tallene som bakes inn i HTML-en.

**MET Frost og NVE døgnverdier** — kalibreringsgrunnlag
Observert nedbør og døgnvannføring 2016–2025 i `data/logg/`, hentet én gang med de manuelle
`frost_*`- og `nve_hent_dogn`-workflowene. Grunnlaget for fiskemeldingens responsfaktorer.

---

## Byggetid kontra kjøretid

Dette skillet er sentralt for å forstå systemet.

**Bakt inn i HTML-filen** (endres kun når en ny fil publiseres):

- `ALL_DATA` / `FLY_DATA` — fangster per år/måned/vannføringsbin/sone
- `DAYS_DATA` — antall observerte dager per bin, nevneren i fangstraten
- `FLOW_LOOKUP` — daglig vannføring 2016–2025
- `BOOM_DAYS`, `REKORDLAKS_DATA` — rekorddag og tyngste laks per sone
- `ZONE_INFO`, `ZONE_COORDS` — beskrivelser, sesong, kvoter, koordinater
- `P90_*` / `MAX_*` — normaliseringskonstanter for scoren

**Hentet ved kjøretid** (oppdateres uten ny publisering):

- `data/config.json` — vekting, `shrinkC`, `shrinkCElv`, `knee`, sparkline-skala
- `data/sesong.json` — sesongdatoer (dashbord og oversiktskart)
- `data/vannforing*.json` — dagens vannføring
- `data/nedbor*.json` — fiskemelding
- `data/photos_<elv>.json`, `data/videoer_<elv>.json` — mediegalleri
- `data/nyheter.json` — nyhetsbanner (kun oversiktskartet; `nyhetskilder.json` brukes bare av admin)
- `data/fangster_<elv>.json` — siste fangster (kun oversiktskartet)
- `data/statistikk.json` — statistikksiden

**Konsekvens verdt å merke seg:** historiske score endrer seg aldri av seg selv. Skal en
elv få oppdatert fangsthistorikk, må HTML-filen bygges og publiseres på nytt. Det samme
gjelder oversiktskartets score-tabeller, som er statiske og ikke reagerer på endringer i
`config.json`.

---

## Skriving til repoet

Siden det ikke finnes en backend, skjer all skriving gjennom GitHub Contents API:

**Admin-panelet** bruker et personlig fine-grained token (PAT) som ligger i
`localStorage` i din egen nettleser. Tokenet forlater aldri enheten og ligger ikke i
repoet. Andre som åpner admin-siden ser skjemaene, men får feilmelding ved forsøk på å
lagre. Siden har `noindex` og er ikke lenket fra dashbordene.

**Dette er også grunnen til at brukerinnsendt innhold ikke kan bygges på samme mønster.**
Å la besøkende stemme eller registrere fangster ville krevd at et skrivetoken var
tilgjengelig i nettleseren til alle — altså full skrivetilgang til repoet for hvem som
helst. Slike funksjoner må derfor gå via eksterne tjenester (Google Forms, Strawpoll
eller tilsvarende) eller via et mellomledd som holder tokenet — se forslaget i
[`ideer/tilbakemeldingsside.md`](ideer/tilbakemeldingsside.md).

---

## Automatisering

| Workflow | Utløser | Gjør |
|---|---|---|
| `nve_cache.yml` | Hver time + `workflow_dispatch` | Vannføring (6 elver) + nedbør (4 punkter) + nedbørslogg |
| `fangst_pipeline.yml` | Hver time (:30) + `workflow_dispatch` | Ferske fangster fra Inatur |
| `foto_pipeline.yml` | Push til `bilder/innboks/<elv>/` | Prosesserer bilder, leser GPS |
| `issue_foto_pipeline.yml` | Nytt GitHub-issue | Bildeopplasting via issue (omgår 1 GB-grensen) |
| `bulk_foto_pipeline.yml` | Manuell | Masseopplasting |
| `frost_*.yml`, `nve_hent_dogn.yml` | Manuell | Engangsuthenting av kalibreringsdata |

GitHub sin egen `schedule`-utløser er upålitelig under last, så **cron-job.org** kaller i
tillegg workflowene via `workflow_dispatch`: `nve_cache` på :05 og `fangst_pipeline` på
:35 hver time.

> ⚠️ **Tidsbombe:** cron-tokenet `elvedata-cron` utløper **11. juli 2027**. Etter det
> stopper de eksterne triggerne uten noen feilmelding i repoet. Varsling fra cron-job.org
> er eneste deteksjonsmekanisme.

---

## Publiseringsflyt

1. `git pull`, deretter redigeres `{elv}/index.html` direkte i repoet (ingen nummererte kopier)
2. Versjonsnummeret i footeren bumpes +1
3. `python scripts/valider.py {elv}/index.html` (konfliktmarkører, `node --check`, div-balanse,
   HTML-nesting, deklarasjonsdiff mot `HEAD`, jsdom-røyktest)
4. For oversiktskartet: testes først i `staging/index.html`
5. Endringsnotat i `docs/endringer/`, én commit per elv per runde (se `/runde`), push
6. GitHub Pages bruker inntil ~10 minutter på å servere den nye filen

Versjonsnummeret vises i footeren som `v{major}.{iterasjon}`, der major er 1 for elver
som er koblet til oversiktskartet. Detaljer: [utviklerkonvensjoner.md](utviklerkonvensjoner.md).

---

## Analyse

GoatCounter, cookieløst og uten samtykkebanner. Gir sidevisninger, henvisninger og
grovt geografi — men **ikke** tid på side eller gjenbesøk, siden ingen vedvarende
besøks-ID lagres. Det er en bevisst avveining: personvern foran innsikt.

Staging-versjonen har analysen deaktivert, slik at egne tester ikke forurenser tallene.
