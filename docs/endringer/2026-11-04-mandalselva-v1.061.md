# Mandalselva v1.061 — vannføringspillen viser riktig antall bilder

**Dato:** 2026-11-04
**Fil:** `mandalselva/index.html`
**Forrige versjon:** v1.060

## Hva ble endret

- `mediaCountInBin()` teller bilder/videoer i sonen som er valgt i kartet (`activeZone`), og faller
  tilbake til sonen for det åpne bildet (`_activeMediaZone`) bare når ingen sone er valgt.
- `updateMap()` kaller `_syncFlowChip()` til slutt, så pillens tekst, antall og piler oppdateres ved
  sonebytte og slider-endring — ikke bare når bildepanelet åpnes eller filteret slås av/på.
- Versjon v1.060 → v1.061.

Andre filer i samme commit: ingen.

## Hvorfor

Per Lasse så at vannføringspillen i Otra alltid viste «(0)». I fullskjerm flyttes pillen inn i kartet
og er synlig før noe bilde er åpnet; da var `_activeMediaZone` null og tellingen ble 0, mens
kartikonene (som bruker `activeZone`) viste riktige bilder. Pilene (`nextFlowWithMedia`) bruker samme
telling og var derfor også feil. Samme kode fantes i Audna, Lygna, Mandalselva og Sygna; Tovdalselva
har en enklere pille uten antall og fullskjerm og er ikke berørt.

## Validering

- `python scripts/valider.py mandalselva/index.html` — OK.
- Kart-UX A–C — uberørt.
- Manuelt i nettleserpanelet (PC), fullskjerm, sone valgt uten å åpne bilde, filter på, slider gjennom
  alle binene med medier: tallet i pillen = antall synlige ikoner i hver bin. Sone 3: 18 bins fra 25 til 115 m³/s, alle like; bytte til Sone 4 → 4 = 4.
