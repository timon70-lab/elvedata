# Sygna: sesongen 2026 med i årsslideren

**Dato:** 2026-11-22
**Filer:** `sygna/index.html` (v1.050 → v1.051)

## Hva ble endret

- **Årsslideren går til 2026.** Standardvalget er 2016–2026, det samme er teksten i
  rekorddag-vinduet.
  - En delt lenke uten `aar=` viser nå 2016–2026.
- **Fangsttallene for 2026 er lagt inn** i `ALL_DATA`, `FLY_DATA` og `DAYS_DATA`, laget fra
  `data/raw/Sygna_fangstlogg_2016_2026.csv` og `Sygna_vannforing_2016_2026.csv`.
  - Det gjelder 9 fisk, alle sjøørret (7 på flue).
  - `LAKS_DATA` og `LAKS_FLY_DATA` («Kun laks») får derfor ingen 2026-tall.
  - 2016–2025 er uendret, byte for byte.
- **`FLOW_LOOKUP`** har fått juni–september 2026, i tillegg til 2025.
- **Rekordene er uendret:** ingen dag eller laks i 2026 slår dem.
- **Kalibreringskonstantene `P90_*` og `MAX_*` er uendret.**

## Hvorfor

Per Lasse: «hvorfor går ikke år intervallet lenger enn til 2025 for mandalselva? har vi ikke
data for 2026?» Svaret var «kun for mandalselva og sygna».

## Validering

- Generatoren gjenskaper alle fem datasett for 2016–2025 nøyaktig fra rådataene. Den bruker
  bins på 2 m³/s fra ikke-avrundet vannføring og samler alt fra 18 og over i én bin.
- Poengene er like i gammel og ny fil for 880 kombinasjoner av årsvindu innenfor 2016–2025,
  måned, flue, «Kun laks» og vannføring 0–20.
- `python scripts/valider.py sygna/index.html` — OK.
- I nettleseren: v1.051, `#aar=2026-2026` gir 7 fangster ved 0–2 m³/s, og konsollen er uten
  feil.

## Kjente mangler / oppfølging

- Ingen.
