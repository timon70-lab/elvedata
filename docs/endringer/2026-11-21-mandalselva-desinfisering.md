# Mandalselva — desinfeksjonsposter

**Dato:** 2026-11-21
**Fil:** `data/desinfisering.json` (bare data, `mandalselva/index.html` er uendret og har
fortsatt v1.068)

## Hva ble endret

- **Fire desinfeksjonsposter for Mandalselva**, fra munningen og oppover:

  | Post | Koordinater |
  |---|---|
  | Sandnes Camping | 58.043210, 7.495671 |
  | Hauge | 58.134032, 7.539281 |
  | Mandalselva Villakssenter | 58.245333, 7.513411 |
  | Adventure Norway | 58.354959, 7.527093 |

- **I kartet:** postene vises som egne punkter på nær zoom.
- **Knappen «Desinfisering»** finner nærmeste post.
- **Soneinfo:** hver sone med koordinater får raden «Desinfisering» med nærmeste post, avstand,
  «Kjør dit» og «Vis på kart».

## Hvorfor

Per Lasse ga postene med koordinater 2026-11-21.

## Validering

- Lokalt i Mandalselva-kartet: `DESINF` har 4 poster, og Hauge-posten vises på zoom 14.
- Riktig nærmeste post i soneinfo:
  - Sone 1 → Sandnes Camping (1,7 km).
  - Hauge A → Hauge (0,4 km).
  - Strædethylen → Mandalselva Villakssenter (4,1 km).
- Soner uten koordinater (f.eks. Haugefossen, Sandnes fiskeri, Åsefoss) har ikke fått raden,
  som før.
