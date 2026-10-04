# Oversiktskart v1.056 — 💬-lenka peker til egen tilbakemeldingsside

**Dato:** 2026-10-05
**Fil:** `index.html` (oversiktskartet), `tilbakemelding/index.html`
**Forrige versjon:** v1.055 / v0.003

## Hva ble endret

- `index.html`: 💬-lenka i headeren peker fra `forms.gle/JbZt3QCmrVAGJnAT9` til
  `tilbakemelding/`. `target="_blank" rel="noopener"` er fjernet — siden er nå
  intern og har sin egen «← Tilbake til oversiktskartet»-lenke, så den skal åpnes
  i samme fane.
- `tilbakemelding/index.html`: `<meta name="robots" content="noindex">` fjernet.
  Driftsdokumentasjonen slo fast at den sto der «til den lenkes», og det er nå.
  Versjonen går fra v0.003 til **v1.004**: major 1 betyr lenket fra oversiktskartet.
- `docs/datakilder-og-infrastruktur.md` og `docs/ideer/tilbakemeldingsside.md`
  oppdatert — begge beskrev siden som ikke lenket.

Andre filer i samme commit: ingen.

## Hvorfor

Tilbakemeldingssiden ble bygget 2026-09-26 (idé-logg: `docs/ideer/tilbakemeldingsside.md`)
og Workeren satt i drift samme dag, men lenka på oversiktskartet pekte fortsatt til
Google Forms. Planens punkt 4 sa at kartet skulle legges om til slutt, når alt
fungerte. Per Lasse ba om det 2026-10-05.

To endringer i én commit fordi de utgjør én logisk handling: å ta siden i bruk.
Å lenke siden uten å fjerne `noindex` ville etterlatt den usynlig for søkemotorer
uten at noe tilsa det.

## Validering

- `python scripts/valider.py index.html tilbakemelding/index.html` — OK, alle seks
  sjekker på begge.
- Siden ble kontrollert live på `elvesona.no/tilbakemelding/` før lenka ble lagt om:
  skjemaet rendres, alle felt er på plass, Workeren er i drift siden 2026-09-26.
- Lenka kontrollert i nettleserpanelet etter endringen: `href="tilbakemelding/"`.
- Skjemaet ble ikke sendt inn under testen, for ikke å legge testdata i det private
  tilbakemeldingsrepoet.
- Kart-UX A–C: ikke berørt, endringen er én `href` i headeren.

## Oppfølging

- **`staging/index.html` er ikke endret** og peker fortsatt til Google Forms (linje 89).
  Staging er ment som speil av oversiktskartet, så de to spriker nå. Egen runde når
  Per Lasse vil.
- Resten av planens punkt 4 gjenstår: lenker fra de seks dashboardene
  (`/tilbakemelding/?elv={elv}`), fra statistikksidene, og 👍/👎-hurtigrespons under
  topp 3-sonene.
- `tilbakemelding/index.html` har to treff på versjonsmønsteret `v[0-9]+\.[0-9]{3}`:
  selve versjonen på linje 142, og `v1.066` i en kommentar på linje 180 som viser
  formatet på `?v=`-parameteren. Repo-kartet i CLAUDE.md sier at mønsteret har
  nøyaktig ett treff per fil — det stemmer ikke for denne fila. `rep()` på
  `· v{gammel}<` virker fortsatt, men en rå `grep` gir to linjer.
