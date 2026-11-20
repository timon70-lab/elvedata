# Feltpunkter — markere punkter direkte i elvekartene

**Dato:** 2026-11-20
**Filer:** `felles/registrering.js` (ny), `admin/index.html` og alle seks dashboard:

| Elv | Ny versjon |
|---|---|
| Otra | v1.090 |
| Mandalselva | v1.067 |
| Audna | v1.170 |
| Tovdalselva | v1.019 |
| Sygna | v1.049 |
| Lygna | v1.073 |

## Hva ble endret

- **Ny fil `felles/registrering.js`.** Den gir knappen «➕ Marker punkt» oppe til høyre i
  elvekartet. Et punkt kan markeres på tre måter:
  - **📍 GPS:** følger posisjonen i opptil 20 s og bruker den beste målingen. Nøyaktigheten
    lagres.
  - **✓ Marker her:** bruker krysset midt i kartet.
  - **Langt trykk** (mobil) eller **høyreklikk** (PC) der punktet skal være.
- **Skjemaet** har type (sonegrense/skilt, parkering, desinfisering, kortsalg, annet), sone og
  kommentar. Sonen foreslås ut fra polygonet punktet ligger i.
- **Lagring:** punktene skrives til `punkter.json` i det private repoet
  `elvesona-tilbakemeldinger` med GitHub-tokenet fra adminpanelet. Fila lages ved første punkt.
  - Uten nett legges punktet i kø i nettleseren og sendes når nettet er tilbake.
  - Registrerte punkter vises som prikker i kartet: oransje = lagret, grå = i kø, grønn =
    behandlet.
- **Bare for Per Lasse.** Hvert dashboard har en liten laster i `<head>` som henter
  `felles/registrering.js` bare når admin-tokenet ligger i nettleseren. Vanlige brukere laster
  ikke fila, og siden er uendret for dem.
- **Adminpanelet** har ny seksjon «📍 Feltpunkter». Den har lista med filter, lenke som åpner
  elvekartet zoomet inn på punktet (`#punkt=lat,lon`), kopiering av koordinater, statusen
  «behandlet» og sletting.

Andre filer i samme runde:
- `CLAUDE.md`: `felles/registrering.js` er lagt inn i repo-kartet.
- `docs/admin-brukerveiledning.md`: ny seksjon «📍 Feltpunkter».

## Hvorfor

Per Lasse vil kunne verifisere sonegrenser ved å markere grenseskilt direkte i kartet når han
er ved elva, i stedet for å finne koordinatene for hånd etterpå. Det samme gjelder parkering,
desinfeksjonsstasjoner og annet.

## Validering

- `python scripts/valider.py` — OK for alle seks dashboard og `admin/index.html`.
- Testet lokalt med et falskt testtoken og simulerte GitHub-svar. Ingenting ble sendt til det
  ekte repoet.
  - Uten token lastes verken knappen eller fila.
  - Med token vises knappen, markeringsmodus, kryss, GPS (simulert) og langt trykk.
  - Sonen foreslås riktig («Alle åpne soner» i Sygna).
  - Når GitHub avviser, havner punktet i kø med beskjed. Når det virker, opprettes
    `punkter.json`, og køen tømmes.
  - `#punkt=58.165,7.088` zoomer Lygna-kartet inn på punktet.
  - Adminlista viser punktene, og statusendring lagres.
  - Mobil 375 px: ingen vannrett rulling, og markeringslinja dekker ikke krysset.

## Kjente mangler / oppfølging

- **Første ekte lagring er ikke testet.** Tokenet må ha skrivetilgang (Contents: read/write) til
  `elvesona-tilbakemeldinger`. Ifølge adminpanelet har det det allerede.
- **Tokenet må legges inn på telefonen** via adminpanelet før knappen vises der.
- Bilder av skilt er ikke med ennå.
- Punktene gjøres om til ekte data for hånd: si for eksempel «legg inn feltpunktene for
  Tovdalselva».
