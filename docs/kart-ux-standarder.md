# Kart-UX-standarder (gjelder ALLE dashboard, uansett elv)

## A) Smooth slider — fast bredde på verdi-etiketten
`.ctrl-val` (verditeksten ved siden av hver slider — vannføring/år/måned) må ha `min-width: 88px`.
Uten dette endrer etiketten bredde når intervallet skifter («5–10 m³/s» → «145–150 m³/s»), slik at
selve slideren endrer bredde midt i et drag og oppleves å «hoppe». Fast bredde løser det uansett
hvor lang tekst elvens flow-range gir.

## B) Behold kartposisjon når en fokusert sone mister fokus
I `selectZone()`s «lukk sone»-gren (klikk samme sone igjen) skal `map.fitBounds(allCoords, {...})`
fjernes helt. Kartet skal beholde posisjon/zoom fra da sonen hadde fokus.

## C) Ikke scroll siden ved hver slider-endring
`showZoneInfo(zone, scrollTo = true)` med `if (scrollTo) panel.scrollIntoView(...)` — ikke ubetinget.
`update()` kaller `showZoneInfo(activeZone, false)` ved hver slider-endring (vannføring/år/måned).
