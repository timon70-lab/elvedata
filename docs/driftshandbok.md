# Driftshåndbok

Kjente feilmoduser og hva man gjør. Sortert etter hvor sannsynlig de er.

---

## Data slutter å oppdatere seg

**Symptom:** vannføringen står stille, «siste fangster» er utdatert, men ingenting ser
ødelagt ut.

**Sjekk i denne rekkefølgen:**

1. **Actions-fanen i GitHub** — kjører workflowene? Feiler de?
2. **cron-job.org** — har jobbene sluttet å svare?
3. **Utløpsdato på `elvedata-cron`** — dette tokenet dør **11. juli 2027**. Etter det
   stopper de eksterne triggerne uten spor i repoet.
4. **`NVE_API_KEY`** — sjekk om vannføringsfilene inneholder en feilmelding i stedet for
   data.

Dette er den mest sannsynlige årsaken til «alt ser normalt ut, men tallene er gamle».

---

## Git-konfliktmarkører i publisert fil

**Symptom:** siden ser ødelagt ut, eller deler av den fungerer ikke. Filen inneholder
`<<<<<<<`, `=======` eller `>>>>>>>`.

Har skjedd på **Audna, Mandalselva og Sygna**. Årsaken er som regel lokale
stash/pull-operasjoner som er committet uten at konflikten ble løst.

**Fiks:**

1. Hent fersk fil fra `raw.githubusercontent.com`
2. Identifiser hvilken side som er riktig — normalt den sist leverte versjonen
3. Fjern markørene og den forkastede siden
4. Kjør full valideringssekvens
5. Publiser ren fil med økt versjonsnummer

**Forebygging:** valideringssekvensens steg 2 fanger dette før publisering. Hopp aldri over
det steget.

---

## Nyhet vises ikke i banneret

Sjekk i rekkefølge:

1. **Datoene** — `startDate` må være i dag eller tidligere, `stopDate` i dag eller senere.
   Status-merket i admin viser AKTIV / KOMMENDE / UTLØPT.
2. **Pages-cache** — det tar inntil ~10 minutter før en ny `nyheter.json` serveres.
3. **Tidssone** — «dagens dato» beregnes i UTC. Rundt midnatt norsk tid kan en nyhet med
   dagens dato ligge et par timer bak.
4. **Er filen faktisk skrevet?** Sjekk `data/nyheter.json` direkte i repoet.

---

## Fiskemeldingen forsvinner

Boksen er bygget med `if (!res.ok) return;` og skjules stille dersom nedbørsfilen mangler
eller ikke lar seg parse.

**Vanligste årsak:** dashbordet peker på en fil som ennå ikke finnes. Skjedde sist da Lygna
fikk eget nedbørspunkt — dashbordet må publiseres *etter* at workflowen har opprettet
`nedbor_lygna.json`.

**Sjekk:** åpne `data/nedbor_<elv>.json` i nettleseren. Får du 404, er det årsaken.

---

## Admin-panelet kan ikke lagre

| Feilmelding | Årsak |
|---|---|
| «Lagre GitHub-token først» | Ingen PAT i `localStorage` på denne enheten |
| HTTP 401 | Token utløpt eller trukket tilbake |
| HTTP 403 | Token mangler `Contents: read/write` |
| HTTP 404 | Token har ikke tilgang til repoet |
| HTTP 409 | SHA-konflikt — filen ble endret av noen andre |

Ved 409: last siden på nytt slik at fersk SHA hentes, og prøv igjen.

Husk at tokenet er lagret **per nettleser og per enhet**. PC og mobil trenger hvert sitt.

---

## Bilde havner i feil sone

Sonen utledes fra GPS. Sjekk `soneAvstandM` i `photos_<elv>.json` — er den over 300 m, er
tilordningen usikker.

For Audna gjelder i tillegg tidsregelen: bilder fra 2021 eller tidligere hører til Sone 5
(udelt), fra 2022 til Sone 5A/5B. Nær grensene Sone 2/3 og Sone 7/8 kreves manuell
kontroll.

Rettes ved å redigere `photos_<elv>.json` direkte.

---

## Bilde mangler GPS helt

Forventet oppførsel — ikke en feil.

Android sin bildevelger og Gmail stripper EXIF. Koordinatene overlever kun ved bruk av
**Kamera-valget direkte i GitHubs opplastingsdialog**, eller ved nedlasting fra OneDrive.

Bilder uten GPS må registreres manuelt via admin-panelet.

---

## Score ser feil ut etter endring i config.json

**Oversiktskartets score-tabeller er forhåndsberegnede** og reagerer ikke på
`config.json`. Endrer du vekting eller `shrinkC`, vil elve-dashbordene oppdatere seg, mens
oversiktskartet fortsatt viser gamle tall inntil det bygges på nytt.

Dette er en kjent inkonsistens uten løsning per i dag.

---

## Sone mangler score helt

`computeScores()` returnerer `null` når verken senterbin eller nabobins har observerte
dager i det valgte år-/månedsvinduet. Sonen vises da uten score, med vilje — alternativet
ville vært å gjette.

Utvid år- eller månedsintervallet, eller velg en vannføring nærmere det som faktisk har
forekommet.

---

## Push-konflikt mellom workflows

`nve_cache.yml` prøver fem ganger med `git pull --rebase` mellom hvert forsøk. Feiler den
likevel, kjør workflowen manuelt på nytt fra Actions-fanen. Dataene er idempotente — en
ekstra kjøring gjør ingen skade.

---

## Repoet nærmer seg 1 GB

Bilder er den store posten. Bruk **issue-basert opplasting**
(`issue_foto_pipeline.yml`) — bilder lastet opp til et issue lagres på GitHubs CDN og
teller ikke mot repogrensen.
