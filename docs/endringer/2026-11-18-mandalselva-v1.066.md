# Mandalselva v1.066 — nytt kart går live (mandalselva2 → mandalselva)

**Dato:** 2026-11-18
**Fil:** `mandalselva/index.html`
**Forrige versjon:** v1.063 (testklonen var på v0.065)

## Hva ble endret

- **`mandalselva/index.html` er erstattet av testklonen mandalselva2 v0.065.** Den har det nye
  kartet fra Otra:
  - Kartlagene Kart, Topo og Flyfoto.
  - Oppsett for PC og mobil, og fullskjerm.
  - Sonepolygoner for 40 soner, sonelinjer i oversikten og dagsstatus.
  - Delbare lenker og «Hvor er jeg?».
  - Ingen zoom ved klikk på sone, og de tettere mobilknappene.
  - Se `2026-11-18-mandalselva2-v0.064.md` og `-v0.065.md` for detaljer.
- **Testmerkingen er fjernet:**
  - Uten `noindex` og uten oransje stripe.
  - Tittel og `<h1>` er «Mandalselva · Dynamisk oversikt».
  - GoatCounter er satt inn igjen.
  - Toppavstanden er 16 px på PC og 8 px på mobil.
- **`_preloadNeighborImages()` er tatt med fra den gamle Mandalselva-siden.** Den finnes ikke i
  Otra-koden. Den forhåndslaster forrige og neste bilde i bildevisningen, så pilene virker
  raskt på trege mobilnett.

Andre filer i samme commit: `CLAUDE.md`. Esri-unntaket gjelder nå `mandalselva/index.html`, og
alle Mandalselva-endringer gjøres fra nå av direkte i `mandalselva/index.html`.

## Hvorfor

Per Lasse: «la mandalselva2 gå live».

## Validering

- `python scripts/valider.py mandalselva/index.html` — OK. Første kjøring varslet at
  `_preloadNeighborImages` var borte, og den er derfor tatt med.
- I nettleseren:
  - Ingen teststripe, ingen `noindex`, og GoatCounter er med.
  - `#sone=Hauge_A` åpner Hauge A, og alle 40 polygonene er lastet.
  - Ingen konsollfeil og ingen mislykkede forespørsler.

## Kjente mangler / oppfølging

- Mangler data for desinfeksjonsposter, parkering, kortsalg, hendelser, fiske fra én side og
  ukedagsregler. Knappene for desinfeksjon og parkering er skjult til det finnes data.
- 16 soner har ikke koordinater og vises ikke i kartet.
- Sonegrensene er beregnet og bør kontrolleres.
