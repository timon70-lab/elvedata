# Bilde fra kartet vises rett under kartet på mobil

**Dato:** 2026-11-20
**Filer:** alle seks dashboard:

| Elv | Ny versjon |
|---|---|
| Otra | v1.091 |
| Mandalselva | v1.068 |
| Audna | v1.171 |
| Tovdalselva | v1.020 |
| Sygna | v1.050 |
| Lygna | v1.074 |

## Hva ble endret

- **Bildet får fokus.** Trykker du på et bilde i kartet på mobil, rulles siden nå slik at
  bildepanelet står rett under kartet. Det gjelder også når en sone er valgt.
  - Før ble bildet liggende bak kartet, mens soneinfo fortsatt sto på skjermen.
- **Ny funksjon `visUnderKartet(panel)`.**
  - Når en sone er valgt på smal skjerm, står kartet fast øverst (`position: sticky`). Da
    gjorde `visKartOverst()` ingenting, fordi kartet allerede sto øverst.
  - Den nye funksjonen ruller til panelet og trekker fra kartets høyde.
  - Når kartet ikke står fast, brukes `visKartOverst()` som før.
- **Rullingen er uten animasjon, og justeres igjen når bildet er lastet.**
  - Når bildet lastes og panelet blir høyere, flytter nettleserens scroll anchoring siden.
    Det avbrøt en myk rulling.
  - Justeringen skjer bare innen 4 sekunder etter trykket.
- PC og fullskjerm er uendret.

## Hvorfor

Per Lasse: «når jeg klikker på et bilde i kartet på mobil åpner bildet under kartet. sone
kortet har fremdeles fokus under kartet. bildet bør få fokus slik at jeg slipper og scrolle
for å få det frem.»

## Validering

- `python scripts/valider.py` — OK for alle seks.
- Mobil 375 px med valgt sone og rullet ned i soneinfo, i Otra, Tovdalselva og Audna:
  - Bildepanelet starter 8 px under kartet (kartet slutter på 342 px, panelet starter på
    350 px).
  - Det gjelder også bilder fra en annen sone og bilder som ikke var lastet før.
- PC: bildepanelet åpnes som før.
