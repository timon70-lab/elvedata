# P-knappen under zoomnivået i fullskjerm

**Dato:** 2026-11-26
**Filer:** alle seks dashboard:

| Elv | Ny versjon |
|---|---|
| Otra | v1.092 |
| Mandalselva | v1.070 |
| Audna | v1.172 |
| Tovdalselva | v1.021 |
| Sygna | v1.052 |
| Lygna | v1.075 |

## Hva ble endret

- **P-knappen (parkering av/på) står under zoomnivået i fullskjerm**, rett under «z 11» i samme
  kolonne som +/−.
  - Før sto den til høyre for +/−. Der lå den under kontrollboksen med vannføringsslideren, som
    starter like ved siden av zoomknappene. På mobil var den halvt dekket, på PC helt dekket.
- Ny CSS-regel: `#mapFs.fs-on .p-tog { left:-2px; top:calc(100% + 27px); }`.
- Utenfor fullskjerm står knappen som før, til høyre for +/−.

## Hvorfor

Per Lasse: «på mobil overlapper vannføringsslider med parkering enable/disable knappen i
fullskjerm visning.»

## Validering

- `python scripts/valider.py` — OK for alle seks.
- Fullskjerm på mobil (375 px) i alle seks kart:
  - Knappen står på 5,94–39,128 px, under «z 11» (73–90 px).
  - Den overlapper verken kontrollboksen eller zoomnivået, og et trykk midt på treffer knappen.
  - I de fem elvene uten parkering er knappen skjult. Der ble den tvunget fram for å teste
    plasseringen.
- Fullskjerm på PC (1024 px) i Otra: ingen overlapp, og knappen kan trykkes.
- Utenfor fullskjerm står knappen som før: 4 px til høyre for +/−.

## Kjente mangler / oppfølging

- Ingen.
