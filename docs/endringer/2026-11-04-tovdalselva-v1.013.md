# Tovdalselva v1.013 — fullskjermkart og vannføringspille med antall og piler

**Dato:** 2026-11-04
**Fil:** `tovdalselva/index.html`
**Forrige versjon:** v1.012

## Hva ble endret

- **Fullskjermkart:** «⛶ Fullskjerm»-knapp i kartheaderen. Kartpanelet er pakket i `#mapFs`; ved
  inngang flyttes vannføringsraden (`#flowCtrlRow`), pillen, bildepanelet og bildevisningen inn i
  fullskjerm, og tilbake ved «✕ Avslutt fullskjerm» / Esc. CSS og JS (`_enterMapFs`, `_teardownMapFs`,
  `toggleMapFullscreen`, `_onMapFsChange` m.fl.) er hentet uendret fra Lygna v1.068.
- **Vannføringspillen:** byttet fra enkel av/på-knapp («💧 Kun 20–25 m³/s») til samme pille som de
  andre elvene: antall bilder/videoer i valgt sone og bin, og ‹ ›-piler som hopper til nærmeste bin med
  medier. `flowBinOf`, `flowBinLabel`, `mediaCountInBin`, `nextFlowWithMedia`, `stepFlow` og
  `_syncFlowChip` er hentet fra Lygna, tilpasset Tovdalselvas bins (5 m³/s, samlebin 85+).
- `updateMap()`, `_rebuildZoneMedia()` og `openZoneMedia()` oppdaterer pillen via `_syncFlowChip()`.
- «Kun laks»-pillen og resten av Tovdalselvas egne funksjoner er uendret.
- Versjon v1.012 → v1.013.

Andre filer i samme commit: `docs/status-og-backlog.md` (versjonslinja).

## Hvorfor

Per Lasse spurte hva Tovdalselva manglet i kartløsningen sammenlignet med de andre elvene. Svaret var
fullskjermkartet og den utvidede vannføringspillen — begge finnes i Audna, Lygna, Mandalselva, Otra og
Sygna. Han ba om å få dem inn.

## Validering

- `python scripts/valider.py tovdalselva/index.html` — OK.
- Kart-UX A–C — uberørt.
- Manuelt i nettleserpanelet (PC):
  - Klikk på «⛶ Fullskjerm» åpner fullskjerm med slider og pille øverst til venstre, «Avslutt
    fullskjerm» øverst til høyre.
  - Sone 2, 65–70 m³/s (0 bilder): klikk på ‹ hopper til 5–10 m³/s, pillen viser (10) = 10 ikoner.
  - Sone 4 og 5: (10) / (4) / (4) i binene 5, 40, 60 m³/s = antall ikoner; Sone 3 i samlebin 85+:
    (10) = 10 ikoner.
  - «Avslutt fullskjerm» flytter slider og pille tilbake på plass.
  - Bildepanelet i vanlig visning: pillen med piler og antall vises i panelheaderen.
- Ikke testet på mobil (smal skjerm bruker `@media (max-width: 520px)`-reglene fra Lygna).
