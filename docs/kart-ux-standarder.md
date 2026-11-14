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

## D) Smooth kart — ingen tomme eller hvite felter
Flytting og zooming av kartet skal oppleves sømløst. Brukeren skal ikke se tomme eller hvite felter
som bruker lang tid på å laste. Per Lasse regner dette som en av de viktigste egenskapene ved en
topp kartløsning (fastslått 2026-11-14).

- **Bufferens utstrekning:** området som vises når hele elva med alle soner er i bildet. Det er nok —
  kartet skal ikke forhåndslaste områder utenfor dette (ikke «hele Sør-Norge»).
- Kravet gjelder alle kartlag (Kart, Topo, Flyfoto) og også ved bytte mellom dem.
- Hver kartendring (nytt kartlag, flere markører, polygoner, overlegg) vurderes mot dette, og
  flislasting og flyt prøves i nettleser før endringen regnes som ferdig.
- Går et valg ut over flyten (treg fliskilde, forstørrede fliser, tungt overlegg), skal det sies
  fra i endringsnotatet.
