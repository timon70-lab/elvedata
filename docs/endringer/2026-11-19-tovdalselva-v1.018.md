# Tovdalselva v1.018 — hel sonelinje for Sone 4 og 5

**Dato:** 2026-11-19
**Fil:** `tovdalselva/index.html`
**Forrige versjon:** v1.017

## Hva ble endret

- **Sonelinja i oversikten går nå hele veien for Sone 4 og 5**, fra Flakksvannet til
  Herefossfjorden. Før stoppet den ved Teinefoss.
  - Polygonet for Sone 4 og 5 er delt i fire biter, fordi delsonene Teinefoss, Buhølen og
    Laksefoss er klippet ut.
  - `lagSoneLinjer()` brukte bare den første biten, og den slutter ved Teinefoss. Nå regnes
    linja ut fra alle bitene.
- **Ikonet for Sone 4 og 5 står nå i den største biten** av sonen, ved Senumstadfjorden.
  `plasserSoneMarkorer()` brukte også bare den første biten, og satte ikonet nederst ved
  Flakksvannet.

Ingen andre elver har soner i flere biter, så Otra, Mandalselva og Audna er ikke berørt.

## Hvorfor

Per Lasse: «sone 4 og 5 mangler hel strek etter teinefoss fluefiske».

## Validering

- `python scripts/valider.py tovdalselva/index.html` — OK.
- I nettleseren går linja for Sone 4 og 5 fra 58.3292 til 58.4559 nord, og det er ingen
  konsollfeil.
