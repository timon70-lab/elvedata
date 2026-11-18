# Mandalselva2 v0.065 — Sone 4 får polygon

**Dato:** 2026-11-18
**Fil:** `mandalselva2/index.html` (bare versjonsnummeret)
**Forrige versjon:** v0.064

## Hva ble endret

- **Sone 4 har nå polygon**, 4,7 km². Polygonet går fra demningen ved Manflåvann gjennom
  magasinet, opp elva til samløpet med Kosåni og videre ca. 1,6 km opp Kosåni til sonens
  sluttpunkt (58.43661, 7.54922). Dette er rundt 17–18 km og stemmer med «ca. 18 km» i
  sonebeskrivelsen.
  - Mandalselvas vestlige grein over samløpet er ikke med.
  - Sonelinja i oversikten følger den manuelle senterlinja, som går helt til øvre grense av
    Sone 4.
- **`scripts/sonepolygoner.py` har fått valget `flate`** for soner som ikke kan lages langs
  midtlinja. Midtlinja i OSM stopper ved demningen og har hull gjennom magasinet.
  - Sonen lages fra egne OSM-objekter: vannflater (relasjoner), elvelinjer som fyller hullene
    mellom vannflatene, og kutt på tvers av en elvelinje.
  - Vannet deles først, og delen som henger sammen med startpunktet beholdes. Deretter legges
    landstripa rundt, og det som stikker forbi kuttene klippes bort.
  - `--hent` henter også objektene i `flate`.
- **Oppsett for Sone 4:**
  - Vannflater: Manflåvann (11856727) og elveflatene 11857046, 11857037, 11857035, 11857018,
    11856977, 11857041 og 11857045.
  - Elvelinjer: Mandalselva 1209803304, 1209803296, 1209803297 og 1209803298, og Kosåni
    804522326.
  - Kutt: sonens sluttpunkt på Kosåni, og 290 m opp den vestlige greina fra samløpet.
- `data/raw/osm_mandalselva.json` er hentet på nytt med disse objektene. De 39 andre sonene er
  uendret, og `data/soner_otra.geojson` blir nøyaktig lik.

Andre filer i samme commit: `scripts/sonepolygoner.py`, `scripts/sonepolygoner_oppsett.json`,
`data/soner_mandalselva.geojson`, `data/raw/osm_mandalselva.json`.

## Hvorfor

Per Lasse: Sone 4 må også få polygon.

## Validering

- `python scripts/valider.py mandalselva2/index.html` — OK.
- Polygonet går fra 58.2918 til 58.4372 nord og fra 7.5113 til 7.5495 øst. Det er ett
  sammenhengende polygon.
- I nettleseren er 40 polygoner lastet. Klikk på Sone 4 åpner sonen, og polygonet stopper på
  Kosåni og ved samløpet.
