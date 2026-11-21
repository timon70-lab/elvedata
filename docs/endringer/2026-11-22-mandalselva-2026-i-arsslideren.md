# Mandalselva: sesongen 2026 med i årsslideren

**Dato:** 2026-11-22
**Filer:** `mandalselva/index.html` (v1.068 → v1.069)

## Hva ble endret

- **Årsslideren går til 2026.** Standardvalget er 2016–2026, det samme er teksten i
  rekorddag-vinduet.
  - En delt lenke uten `aar=` viser nå 2016–2026.
- **Fangsttallene for 2026 er lagt inn** i `ALL_DATA`, `FLY_DATA` og `DAYS_DATA`, laget fra
  `data/raw/mandalselva_siste_fangster_2016_2026.csv` og `MandalselvaVannforing20162026.csv`.
  - Det gjelder 1090 laks, av dem 524 på flue.
  - Vannføringen går til 2026-09-15.
  - 2016–2025 er uendret, byte for byte.
- **`FLOW_LOOKUP` er forlenget** fra 2025-09-01 til 2026-09-15. Den gir vannføring på bilder
  som mangler den.
- **Rekorder med 2026:**
  - Største laks: Hauge C 10,0 kg, Nedre Nøding 6,0 kg, Lakseøya 9,6 kg, Bjåhylen 13,0 kg og
    Hauge B1 6,0 kg.
  - Beste dag: Bringsdal A 2026-08-11 med 5 fisk. Den får nytt rekorddag-vindu.
  - Bringsdal C 2026-08-14 med 3 fisk. Den tangerer rekorden, og ved likhet vises den nyeste
    dagen, som før.
- **Ikke endret:**
  - Kalibreringskonstantene `P90_*` og `MAX_*`, slik at poengskalaen er den samme.
  - `ZONE_TOOL_RATING`.

## Hvorfor

Per Lasse: «hvorfor går ikke år intervallet lenger enn til 2025 for mandalselva? har vi ikke
data for 2026?» Svaret var «kun for mandalselva og sygna».

## Validering

- Generatoren gjenskaper de innebygde tallene for 2016–2025 nøyaktig fra rådataene. Det gjelder
  `ALL_DATA`, `FLY_DATA`, `BOOM_DAYS` og `REKORDLAKS_DATA`.
  - Unntak: `DAYS_DATA` for september 2023 (15 dager) og september 2025 (1 dag). Der lå
    vannføringen ikke lenger enn det da tallene ble laget. Verdiene er beholdt som de var.
- Poengene er like i gammel og ny fil for 1320 kombinasjoner av årsvindu innenfor 2016–2025,
  måned, flue og vannføring 0–160.
- `python scripts/valider.py mandalselva/index.html` — OK.
- I nettleseren: v1.069, slideren viser 2016–2026, og konsollen er uten feil.

## Kjente mangler / oppfølging

- Fire soner i 2026 fantes ikke i 2016–2025. Bare «Piren m.fl.» (2 laks) mangler i `ZONES`, og
  den telles ikke i poengene.
- Rangeringen av rekorddager («rang») er flettet med 2026-dager, ikke regnet om fra bunnen. Den
  opprinnelige rekkefølgen ved like tall lar seg ikke gjenskape.
- Otra, Audna, Lygna og Tovdalselva har 2026 i dataene, men mangler september.
