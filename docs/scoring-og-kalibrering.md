# Scoring, fiskemelding og kalibrering

Hardt vunne funn — dyre å lære på nytt. Overført fra prosjektminnet 2026-09-20.

## Scoringarkitektur (alle seks elver)
- Pipeline: nabo-bin-glatting (triangulær ±5 m³/s, ±2 for Sygnas 2 m³/s-bins)
  → empirisk Bayes-krymping (shrinkC=15 for soner, shrinkC=8 på elvenivå i Audna/Lygna)
  → to-segment skala (lineær 0→P90-kne, logaritmisk kne→100 mot MAX).
- Elvenivå-score er frikoblet fra sone-snitt og bruker egne `P90_RATE_ELV`/`P90_VOL_ELV` og `shrinkCElv`.
- `P90_RATE_ELV`/`P90_VOL_ELV` kan ikke reproduseres fra embeddede data i Otra og Lygna —
  dokumenter kilden når de genereres.
- Vannføringstrend ble testet for Lygna; backtest negativ. Trend hører hjemme i fiskemeldingen,
  ikke i sonescoren.

## Fiskemelding
- Uregulerte elver (Audna, Lygna, Sygna, Tovdalselva): empirisk kalibrert forventet stigning,
  responsfaktorer utledet fra 2016–2025 MET Frost + NVE.
- Samme nedbør gir 3–5× større vannføringsrespons på våt mark enn tørr.
- Under ~1 m³/s (Lygna) faller responsfaktoren til ~1/10 av normalt — forklarer nesten null
  respons på kraftig regn ved svært lav basisvannføring.
- Responstid: Audna samme dag; Lygna 1–2 døgn (innsjøbuffer).
- Regulerte elver (Mandalselva, Otra): fiskemelding deaktivert. For regulert elv brukes
  sesong-/oppgangsprofil fra fangstlogg + dagens vannføring (svak persistens 1–2 dager)
  + temperaturvakt hvis elva har 21 °C-regel.

## Vannføringsbins
- 5 m³/s-intervaller for Audna/Lygna/Mandalselva.
- Samlebins: Audna 55+, Lygna 55+, Mandalselva 150+, Sygna 18+ (2 m³/s-bins), Otra 300+ (25 m³/s-bins).
- Slider-range: faktisk datarange i sesongvinduet; samlebin i toppen hvis høye bins har <10 dager hver.
- Kanttilfelle rå vs. avrundet float: f.eks. 74.99955 → bin 50 (ikke 75). Verifiser før embedding.
- NVE live: bruk alltid `ResolutionTime=60` (time, nær sanntid). `ResolutionTime=1440` henger ~24 t.

## Foto-GPS og sonetilordning
- Androids bildevelger fjerner GPS; GPS bevares kun med Kamera-valget direkte i GitHub-opplastingen.
- Gmail fjerner GPS; OneDrive bevarer den.
- Audna-bilder: før 2022 → Sone 5 (udelt); 2022+ → Sone 5A eller 5B; Sone 5A-klynge rundt 58.130/7.363.
- Manuell verifisering innenfor 300 m av grensene Sone 2/3 og Sone 7/8.

## Valideringsfelle
- `node --check` fanger bare syntaks, ikke manglende deklarasjoner. Etter malbaserte bygg:
  sammenlign alle toppnivå `let`/`const`/`var` mot originalen (gjøres av `scripts/valider.py`).
