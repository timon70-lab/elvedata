# Oversiktskart v1.055 — nyhetsbanneret viser ikke samme nyhet to ganger

**Dato:** 2026-09-26
**Fil:** `index.html` (roten) og `staging/index.html` (v1.034 → v1.035, samme endring)
**Forrige versjon:** v1.054

## Hva ble endret

- Ny `layoutNewsTicker()`: legger inn nyhetssettet én gang, måler, og dupliserer settet
  og starter auto-scroll **bare** hvis det er bredere enn banneret. Ellers vises settet
  én gang, stillestående.
- `renderNewsTicker()` bygger HTML-en i `newsItemHtml` og kaller `layoutNewsTicker()`
  etter at banneret er gjort synlig (bredden kan ikke måles før).
- `resize`-lytter (200 ms debounce) kjører `layoutNewsTicker()` på nytt, siden ny
  skjermbredde kan endre om rulling trengs.
- Versjonslinjen i footeren: v1.054 → v1.055.

Andre filer i samme commit: `staging/index.html`.

## Hvorfor

Per Lasse så «Sesongoppsummering 2026» to ganger ved siden av hverandre på elvesona.no.
`data/nyheter.json` har bare én aktiv nyhet (N-013) — dataene var riktige. Banneret
dupliserte alltid settet for at auto-scroll skulle loope sømløst, men når innholdet er
smalere enn banneret kan det ikke rulle, og begge kopiene står synlige.

## Validering

- `python scripts/valider.py index.html staging/index.html` — OK (nye deklarasjoner:
  `layoutNewsTicker`, `newsItemHtml`, `newsResizeTimer`; ingen borte)
- I browserpanelet mot lokal `python -m http.server`: med ekte `nyheter.json` vises
  1 element og auto-scroll er av. Med 8 injiserte lange nyheter vises 16 elementer
  (duplisert) og banneret ruller.

## Oppfølging

- Ingen.
