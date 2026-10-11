# Oversiktskart v1.058 — QR-kode for deling av elvesona.no

**Dato:** 2026-10-11
**Fil:** `index.html`
**Forrige versjon:** v1.057

## Hva ble endret

- Ny QR-knapp oppe til venstre i headeren (44 px hvit flis), speilvendt mot 💬-tilbakemeldingsknappen.
  Koden peker til `https://elvesona.no`.
- Trykk på flisen åpner en stor visning: hvit QR-flate (maks 440 px, 88 % av bredden på mobil) på mørk
  bakgrunn med teksten «Skann for å åpne elvesona.no». Lukkes ved trykk hvor som helst, ✕ eller Esc.
- QR-koden er en statisk inline-SVG (`<symbol id="qr-elvesona">`) generert med `segno`
  (versjon 2, feilkorreksjon Q, 2 moduler stille sone) og gjenbrukt via `<use>` i både flisen og
  den store visningen. Ingen bibliotek eller nettverkskall.
- `tellHendelse('qr-aapnet', …)` registrerer hvor mange som åpner den store visningen (GoatCounter,
  samme mønster som øvrige hendelser).
- `header` har fått 56 px sidepadding (var 20) slik at undertittelen ikke havner under flisen på smale skjermer.
- Versjon v1.057 → v1.058.

Andre filer i samme commit: `docs/status-og-backlog.md`.

## Hvorfor

Ønske fra Per Lasse: en enklere måte å dele siden på enn å skrive adressen — fiskere kan skanne QR-koden
fra en annens skjerm eller utskrift. Flisen er for liten til å skanne pålitelig, derfor forstørrelsen.
Ren adresse (uten `?ref=qr`) er valgt for enklest og mest robust kode. Staging er utdatert (v1.035) og
er ikke endret.

## Validering

- `python scripts/valider.py index.html` — OK.
- Matrisen i den innbakte SVG-en er rundtur-verifisert mot `segno`-matrisen (identisk).
- Manuelt i Browser-panelet: flis på plass (desktop og 360 px), stor visning åpner/lukkes via klikk og Esc,
  ingen overlapp med tittel/undertittel/💬. Faktisk skanning med mobilkamera er ikke testet.

## Oppfølging

- Test skanning med mobilkamera (både flisen og den store visningen) etter publisering.
- Legg koden ev. også i `staging/index.html` når den synkroniseres med hovedsiden.
