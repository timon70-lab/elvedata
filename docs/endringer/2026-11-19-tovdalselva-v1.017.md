# Tovdalselva v1.017 — nytt kart går live (tovdalselva2 → tovdalselva)

**Dato:** 2026-11-19
**Fil:** `tovdalselva/index.html`
**Forrige versjon:** v1.015 (testklonen var på v0.016)

## Hva ble endret

- **`tovdalselva/index.html` er erstattet av testklonen tovdalselva2 v0.016.** Den har det nye
  kartet fra Otra:
  - Kartlagene Kart, Topo og Flyfoto.
  - Oppsett for PC og mobil, og fullskjerm.
  - Sonepolygoner for alle 7 soner, sonelinjer i oversikten og dagsstatus.
  - Delbare lenker, nå også med `laks=1`, og «Hvor er jeg?».
  - Fiskemeldingen, elvescoren og «Kun laks» virker som før.
  - Se `2026-11-19-tovdalselva2-v0.016.md` for detaljer.
- **Testmerkingen er fjernet:**
  - Uten `noindex` og uten oransje stripe.
  - Tittel og `<h1>` er «Tovdalselva · Dynamisk oversikt».
  - GoatCounter er satt inn igjen.
  - Toppavstanden er 16 px på PC og 8 px på mobil.

Andre filer i samme commit: `CLAUDE.md`. Esri-unntaket gjelder nå `tovdalselva/index.html`, og
alle Tovdalselva-endringer gjøres fra nå av direkte i `tovdalselva/index.html`.

## Hvorfor

Per Lasse: «Gå live».

## Validering

- `python scripts/valider.py tovdalselva/index.html` — OK. Ingen deklarasjoner er borte
  sammenlignet med v1.015.
- I nettleseren:
  - Ingen teststripe, ingen `noindex`, og GoatCounter er med.
  - `#sone=Laksefoss&laks=1` åpner Laksefoss med «Kun laks» på, og alle 7 polygonene er
    lastet.
  - Score 32 og fiskemeldingen «Tørt, men fallende vann», som før.
  - Ingen konsollfeil.

## Kjente mangler / oppfølging

- Sonegrensene i Flakksvannet og øverst i Herefossfjorden bør kontrolleres.
- Mangler data for desinfeksjonsposter, parkering, kortsalg, hendelser og fiske fra én side
  (privat østside i Sone 2).
