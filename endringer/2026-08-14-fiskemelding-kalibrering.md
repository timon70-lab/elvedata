# 2026-08-14 — Fiskemeldingen kalibrert mot ti sesonger (Tovdalselva)

**Type:** analyse
**Leveranse:** `tovdalselva_dynamisk_oversikt_3.html` (v0.003), videreført i v0.004

## Hva ble endret

Fiskemeldingen i Tovdalselva er ikke lenger ren nedbørrespons. Den kombinerer
nedbørvarsel med **live vannføring** og gir ulik melding etter hvor våt elva er.

- Ny konstant `FM_LOW_FLOW = 10` (m³/s)
- Logikken flyttet ut i `renderFiskemelding()`, kalt fra både `fetchNVE()` og
  `fetchNedbor()`. Rekkefølge er likegyldig; funksjonen returnerer tidlig til
  nedbørdata finnes, og faller tilbake på «dagens nivå» uten tallverdi hvis NVE feiler.

## Hvorfor

Datagrunnlag: 980 sesongdøgn 2016–2025. Nedbør fra MET Hynnekleiv (SN38730) via
Frost, vannføring fra NVE Flakksvann 20.3.0.

**Forsinkelsen er kortere enn først antatt.** Beste enkeltlag er dag 0 (r = 0,401),
ikke dag 1. Beste prediktor er to-døgns sum, i dag + i går (r = 0,498). Første
tekstversjon lovet «1–2 døgn senere» basert på hydrologisk resonnement om
innsjøbuffer — innsjøene demper amplituden, men forsinker mindre enn antatt.
Rettet til «samme døgn og dagen etter».

**Terskelen på 10 m³/s.** Etter minst 10 mm nedbør er median stigning ved t+2
rundt 40 % når elva står over 10 m³/s (88 hendelser), mot rundt 12 % under
(18 hendelser). Kontrasten er stabil enten skillet settes på 8, 10, 12 eller 15,
og viskes ut rundt 20. 10 ble valgt fordi det ligger midt i det stabile området
og gir flest hendelser på oversiden.

**Månedsregel ble vurdert og forkastet.** Analyse av kun 2025 viste r = 0,096 for
juni–juli mot 0,633 for august–september, og pekte mot en sesongbasert regel. Over
ti sesonger holder dette ikke: juni er faktisk den sterkeste måneden (r = 0,633),
juli den svakeste (0,378), august 0,458, september 0,646. 2025 var en tørr sommer,
ikke et systematisk mønster. **Ikke gjeninnfør månedsregel uten nytt grunnlag.**

## Berørte dokumentasjonsavsnitt

| Fil | Avsnitt | Hva må skrives om |
|---|---|---|
| docs/ (ny fil) | `fiskemelding.md` | Finnes ikke i dag. Bør dekke metode per elv, kalibreringsgrunnlag og terskler |
| docs/arkitektur.md | ## Hvor dataene kommer fra | Frost API som historisk kilde, i tillegg til Locationforecast |
| docs/automatisering.md | ### nve_cache.yml | MET-punkt for Tovdalselva er Hynnekleiv, valgt for å matche kalibreringsstasjonen |
| docs/ny-elv-sjekkliste.md | ## 3. Metodevalg | Responstid skal måles, ikke antas |

## Validering

`node --check` OK, div-balanse 107/107, tre kall til `renderFiskemelding()`
(definisjon + to kallsteder). Korrelasjoner beregnet på 980 døgn med både nedbør-
og vannføringsdata; nedbørserien har to manglende døgn på ti år.

## Åpne punkter

- Hynnekleiv dekker hovedgreina, ikke Uldalsgreina, som bidrar med rundt halvparten
  av vannet inn i Herefossfjorden og er regulert via Hanefoss. Sannsynlig
  hovedårsak til at korrelasjonen stopper på 0,50. Mulig forbedring: hent en
  Frost-stasjon til i Uldalsgreina (Ogge- eller Vegusdal-området) og test om en
  vektet sum av to punkter slår Hynnekleiv alene. Krever ny historisk analyse
  før et varselpunkt nummer to eventuelt legges inn.
- Terskelverdien gjelder kun Tovdalselva. De øvrige elvene har ikke fått
  tilsvarende kalibrering — Audna og Lygna kjører fortsatt ren nedbørrespons
  uten vannføringsbetingelse.
- Koordinaten 58,6020 / 8,4181 er bygdesenteret Hynnekleiv, ikke selve målerens
  posisjon. Innenfor METs varselgrid på ca. 1 km, men eksakt posisjon kan hentes
  fra Frost `/sources?ids=SN38730`.
