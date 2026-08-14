# 2026-08-14 — Admin: Tovdalselva, CORS-feil og dobbel EXIF-rotasjon

**Type:** feilretting
**Leveranse:** `admin/index.html` (levert som `admin_index_v3.html`)

## Hva ble endret

Tre uavhengige ting i samme fil.

1. Tovdalselva lagt inn seks steder: begge elve-nedtrekkene, `STATIONS` (20.3.0),
   `RIVER_NAMES`, `ID_PREFIX` (`T`), elvelista bak «Alle elver», og de sju sonene
   med koordinatpar i `ALL_RIVER_ZONES`.
2. `SONER_URL` endret fra absolutt til relativ sti.
3. EXIF-rotasjonen i `compressImage()` fjernet.

## Hvorfor

**CORS etter domenebytte.** `SONER_URL` pekte på
`https://timon70-lab.github.io/elvedata/data/soner.json`. Etter flyttingen til
`elvesona.no` ble det kallet kryssopphav, og GitHub Pages sender ikke CORS-headere
som tillater det. `fetch` feilet, `lastSoner()` gikk i catch-grenen, og resultatet
var fritekstfelt i registreringsskjemaet og tom «Alle soner»-nedtrekk — for alle
elver, ikke bare Tovdalselva. Endret til `../data/soner.json`, som er samme opphav
uansett domene. Admin var eneste sted med hardkodet absolutt URL; dashboardene
brukte allerede relative stier.

**Dobbel rotasjon av portrettbilder.** `compressImage()` anvendte EXIF-transformasjonen
manuelt på canvas. Men nettlesere har `image-orientation: from-image` som standard
og har allerede orientert bildet når `img.onload` fyrer — `img.width`/`height`
rapporterer de orienterte målene. Transformasjonen roterte derfor en gang for mye.
Landskapsbilder har orientation 1 og traff `default:`, derfor slo feilen bare ut
på portrett (orientation 6 og 8). `swap`-logikken hadde samme feil: den byttet om
mål nettleseren allerede hadde byttet om.

Løsningen er å la nettleseren gjøre jobben alene. `orientation`-parameteren står
igjen i signaturen med kommentar om hvorfor den bevisst ikke brukes — uten den
kommentaren blir transformasjonen lagt inn igjen i god tro. Canvas-utdata har
ingen EXIF, så rotasjonen er bakt inn i pikslene. GPS leses ut før komprimering
og går ikke tapt.

Sidegevinst: `URL.revokeObjectURL()` kalles nå etter lasting. Manglet før, så hver
opplasting lekket en object-URL fram til sidelasting.

## Berørte dokumentasjonsavsnitt

| Fil | Avsnitt | Hva må skrives om |
|---|---|---|
| docs/datamodell.md | ## Foto og GPS | EXIF-orientering: nettleseren orienterer selv, ikke roter manuelt |
| docs/arkitektur.md | ## Skriving til repoet | Relative stier i admin — absolutte github.io-URL-er ryker på custom domene |
| docs/ny-elv-sjekkliste.md | ## 6. Validering | Sjekk hardkodede verdier ved kopiering fra mal |

## Validering

`node --check` OK, div-balanse 81/81, ingen konfliktmarkører. Deklarasjonsdiff
etter EXIF-fiksen: `dw`, `scale`, `swap` fjernet, `ch` lagt til — alle tre fjernede
var kun brukt i den slettede transformasjonen.

## Åpne punkter

- **Allerede opplastede portrettbilder er fortsatt feilroterte.** Rotasjonen er
  bakt inn i filene i repoet. Fiksen gjelder bare nye opplastinger. Berørte bilder
  må slettes fra admin og lastes opp på nytt; slett-knappen fjerner både oppføring
  og bildefil.
- CORS-diagnosen er ikke verifisert mot live-siden fra analysemiljøet. Feilmeldingen
  viser nå HTTP-statuskoden hvis den fortsatt slår til.
