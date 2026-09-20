# Statistikk v0.036 — Sygna-sesongen rettet til 15. juli–15. september

**Dato:** 2026-09-20
**Fil:** `statistikk/index.html`
**Forrige versjon:** v0.035

## Hva ble endret

Hele Sygna-seksjonen er regnet om fra 93-døgnsvinduet 15.06–15.09 til det
korrekte 63-døgnsvinduet 15.07–15.09:

- Sesongtekst, diagrammets aria-label og «Om tallene» oppdatert til 15. juli og
  63 døgn.
- KPI-er: median 0,4 → 0,3 m³/s, maks 8,9 → 2,0 m³/s, sjøørretvekt 5,8 → 5,3 kg.
- Diagrammet regenerert: alle 22 søyler for 2016–2026 med nye verdier.
- Sammenligningstabellen: snitt 16–25 for laks 45 → 42, laks totalvekt 96,0 →
  86,5 kg, laks snittvekt 2,22 → 2,19 kg, sjøørret 65 → 59, sjøørret totalvekt
  63,7 → 59,5 kg, sjøørret snittvekt 0,94 → 0,97 kg, median vannføring
  2,3 → 2,8 m³/s. 2025-kolonnen: median 1,0 → 1,5 m³/s.
- Bildetekst: toppår sjøørret 2019 164 → 160, laks 2017 125 → 124.
- Analyseteksten: svakeste tidligere medianer var 2022 (0,6) og 2025 (1,0), er nå
  2022 (0,7) og 2018 (1,1). Historisk sjøørret-snittvekt 0,94 → 0,97 kg.

Tre feil som ikke hadde med sesongvinduet å gjøre ble rettet i samme omgang:

- **Sjøørretvekten inkluderte fisk utenfor vinduet.** 2026 har ni sjøørret, men to
  ble tatt 5. og 9. juni. Antallet «7» utelot dem, mens vekten «5,8 kg» summerte
  alle ni (5,25 + 0,3 + 0,3). Sidens egen snittvekt på 0,75 kg svarte til 5,25 kg
  og avslørte avviket.
- **Diagrammets søyler og y-akse brukte ulik skala.** Gridlinjene ga 0,59 px per
  fisk, søylene 0,72. 2019-søylen på 164 sjøørret ble derfor tegnet helt opp til
  «200»-linja. Søylene bruker nå samme skala som aksen.
- **Maksvannføringen var feil forklart.** Teksten knyttet 8,9 m³/s til «nedbørs-
  intervallet i begynnelsen av september». Toppen lå i realiteten mellom 15. og
  30. juni. I det korrigerte vinduet er maks 2,0 m³/s, og den kom på siste
  sesongdag 15. september.

Andre filer i samme commit: ingen.

## Hvorfor

Sesongen sto oppgitt som 15. juni–15. september på statistikksiden, mens
`data/sesong.json` og Sygna-dashboardet sa 15. juli–15. september. Per Lasse
bekreftet 2026-09-20 at 15. juli er riktig. To sider på samme nettsted oppga
ulik sesong for samme elv, og sammenligningsvinduet var 30 døgn for langt.

## Validering

- `python scripts/valider.py statistikk/index.html` — OK, alle seks sjekker.
- Beregningsmetoden ble først verifisert mot det gamle vinduet: den reproduserte
  sidens eksisterende tall eksakt for 2025 og for snitt 16–25. Først da ble den
  brukt på det nye vinduet.
- Diagrammet dekodet tilbake fra SVG-geometri: alle 22 søyler gir riktig verdi
  mot gridlinjeskalaen.
- Visuelt kontrollert i nettleser: 160-søylen ligger rett over 150-linja, KPI-er,
  tabell og bildetekst stemmer med beregningene.
- Kart-UX A–C: ikke relevant for statistikksiden.

## Oppfølging

- **`data/statistikk.json` er ikke rettet.** Sygnas 2026-oppføring har fortsatt
  `dager: 93`, `start: "15.06"`, `slutt: "15.09"`. Den mater «Annen statistikk»-
  figurene. For 2026 gir det ingen synlig feil, siden laksefangsten er null og
  raten blir 0 uansett vindu — men grunnlaget er feil og vil slå ut neste sesong.
  Skriptet som genererer fila ligger ikke i repoet, så den må regenereres av
  den som eier pipelinen.
- Sesongkilden bør sjekkes for de øvrige elvene også: statistikksidens
  sesongvinduer er hardkodet i HTML, ikke lest fra `data/sesong.json`, så samme
  type avvik kan finnes andre steder. Audna, Lygna, Mandalselva, Otra og
  Tovdalselva stemte mot `sesong.json` ved kontroll 2026-09-20, men koblingen er
  manuell og kan skli igjen.
