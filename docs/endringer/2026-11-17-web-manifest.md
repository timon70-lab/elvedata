# Alle sider — web-manifest, Elvesona kan installeres som app

**Dato:** 2026-11-17
**Filer:** alle 18 sider med favicon

## Hva ble endret

- Nytt `manifest.webmanifest` i roten: navn «Elvesona», `start_url: "/"` (oversiktskartet),
  `scope: "/"`, `display: "standalone"` (uten adresselinje), marineblå bakgrunns- og temafarge
  `#0f2d4a`.
- Nye maskable-ikoner `icon-maskable-192.png` og `icon-maskable-512.png`. Merket er mindre her,
  slik at Android kan klippe ikonet til sirkel eller annen form med marineblått helt ut i
  kanten. `icon-192.png` og `icon-512.png` er med som `any`-ikoner.
- Hver side har fått `<link rel="manifest">` rett under `apple-touch-icon`-linja.
- Versjonen er bumpet +1 på hver side med versjonslinje:
  - oversiktskartet v1.060
  - Audna v1.167, Lygna v1.070, Mandalselva v1.063, Otra v1.082, Sygna v1.046, Tovdalselva v1.015
  - otra2 v0.081
  - statistikk v0.038; sesongsidene for Audna, Lygna, Otra og Tovdalselva v1.004,
    Mandalselva og Sygna v1.003
  - tilbakemelding v1.006
  - vilkår v0.003

Andre filer i samme commit: `CLAUDE.md` (avsnittet Logo og favicon).

## Hvorfor

På Android ble app-ikonet vist som en liten firkant inne i en hvit sirkel, fordi siden bare var
en snarvei. Per Lasse ville at det marineblå skulle fylle hele sirkelen. Han valgte ett felles
manifest der appen åpner oversiktskartet, og godtok at appen vises uten adresselinje.

## Validering

- `python scripts/valider.py` — OK på alle 18 sider.
- Lokal server: manifestet svarer 200 og er gyldig JSON. `/`, `/otra/`,
  `/statistikk/otra2026.html` og `/vilkar/` peker alle på `/manifest.webmanifest`, og alle fire
  ikoner svarer 200 med riktig størrelse.
- Maskable-ikonet: ingen piksler fra merket ligger utenfor sikker sone. Det ytterste punktet
  ligger 37,4 % av bredden fra midten, og grensen er 40 %.
- Ikke testet på telefon før push.

## Oppfølging

- På Android: fjern den gamle snarveien, åpne elvesona.no i Chrome og velg «⋮ → Installer app».
