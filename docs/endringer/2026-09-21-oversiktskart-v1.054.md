# Oversiktskart v1.054 — luft mellom ytterelvene og skjermkanten

**Dato:** 2026-09-21
**Fil:** `index.html` (roten)
**Forrige versjon:** v1.053

## Hva ble endret

- `settUtsnitt()` bruker nå `paddingTopLeft`/`paddingBottomRight` i stedet for én
  symmetrisk `padding`. Polstringen regnes ut fra markørgeometrien: halve markøren
  (20 px, senterforankret) + overhenget på hver side (vannføringsetiketten 12 px mot
  venstre, reguleringssymbolet 8 px mot høyre og opp, fangstetiketten 18 px ned) +
  ønsket luft (14 px på smal skjerm, 30 px ellers).
- Kartet opprettes med `zoomSnap: 0.25` (`zoomDelta` eksplisitt 1). Uten dette måtte
  utsnittet falle et helt zoomnivå når polstringen økte, og alt ble halvparten så stort.
- Versjonslinjen i footeren: v1.053 → v1.054.

Andre filer i samme commit: ingen.

## Hvorfor

Per Lasse rapporterte fra Android at Lygna i vest og Tovdalselva i øst lå nesten utenfor
skjermen. Årsaken er at `fitBounds` polstrer rundt selve koordinatpunktet, ikke rundt
markøren: med 20 px polstring på smal skjerm ble halve markøren (også 20 px) stående
akkurat i kanten, og vannføringsetiketten som henger ut til venstre ble klippet.

## Validering

- `python scripts/valider.py index.html` — OK
- Målt i browserpanelet mot lokal `python -m http.server`:
  375 px bredde → zoom 8.5, 32 px klaring til venstre / 30 px til høyre.
  412 px bredde → zoom 8.75, 26 px / 30 px.
  Desktop → zoom 9 som før (`maxZoom` styrer), markørene sentrert.
- Elvene uten dashbord (Kvina, Sireåna, Bjerkreimselva, Nidelva, Storelva) ligger
  fortsatt bevisst utenfor utsnittet og nås ved å panorere.

## Oppfølging

- `zoomSnap: 0.25` gjør at hjulzoom på PC nå lander på kvarte nivåer og at flisene kan
  bli marginalt uskarpe mellom hele nivåer. +/- knappene hopper fortsatt et helt nivå.
