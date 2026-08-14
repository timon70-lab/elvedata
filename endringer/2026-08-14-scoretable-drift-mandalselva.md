# 2026-08-14 — Oversiktskartets scoreTable for Mandalselva regenerert

**Type:** feilretting
**Leveranse:** `index.html` (oversiktskart, v1.043)

## Hva ble endret

Mandalselvas `scoreTable` i oversiktskartet er regenerert fra dashboardets egen kode.
De øvrige elvenes tabeller er verifisert og latt urørt.

Observert symptom: oversiktskartet viste 43 for Mandalselva ved 15,7 m³/s, mens
elvedashboardet viste 60 for samme vannføring og samme vindu.

## Hvorfor

Oversiktskartets score er **statisk forhåndsberegnet** og bakt inn i `index.html`,
mens dashboardet regner ut sin score i nettleseren fra sine egne datablokker og
`config.json`. De to kildene kan drifte fra hverandre uten at noe krasjer.

To ting hadde endret seg siden tabellen ble bakt:

1. **`config.json` ble endret til `rateWeight: 1, volWeight: 0` for Mandalselva.**
   Tabellen var beregnet med standardvektingen 0,8 / 0,2.
2. **Septemberdata kom inn i datagrunnlaget** da sesongslutt for Sone 4 og dens
   nordlige undersoner ble rettet til 15. september. Bin 15 består nå av 8 dager,
   hvorav 7 er fra september 2022 — dager som ikke fantes da tabellen ble laget.

Avviksmønsteret bekrefter dette: bins i midtsjiktet (50–75 m³/s), som er datarike
og septemberuavhengige, stemte på 0–1 poeng. De høye bins driftet mest, opptil
**30 poeng ved bin 140**, fordi september er høyvannsmåneden og bidrar mest der.

**Metode for regenerering:** dashboardets eget script kjøres i Node med stubbet
DOM og Leaflet, `update()` kalles per bin, og verdien leses ut av `totalScoreBox`.
Ingen reimplementering av scoringen — dashboardet er sin egen fasit. Metoden ble
validert ved at Audna, Lygna og Otra reproduserte sine lagrede tabeller **eksakt**,
som også beviser at kun Mandalselva hadde driftet.

## Berørte dokumentasjonsavsnitt

| Fil | Avsnitt | Hva må skrives om |
|---|---|---|
| docs/arkitektur.md | ## Byggetid kontra kjøretid | scoreTable er byggetid, dashboardscore er kjøretid — kjent driftkilde |
| docs/scoring.md | ## Kjente svakheter | Statisk scoreTable kan drifte fra config.json og fra oppdaterte datablokker |
| docs/datamodell.md | ## Filoversikt | `config.json`-endringer forplanter seg ikke til oversiktskartet |

## Validering

`node --check` OK, div-balanse 19/19, ingen konfliktmarkører. Regenerert tabell for
bin 15 gir 60, identisk med det dashboardet viser live. Audna, Lygna og Otra sine
tabeller verifisert bit-for-bit uendret i den leverte fila.

## Åpne punkter

- **Sygna kunne ikke verifiseres med denne metoden.** Sygnas dashboard har ingen
  `totalScoreBox` og beregner ingen elvenivåscore. Kartets Sygna-tabell må derfor
  ha en annen opprinnelse, og er latt urørt. Bør undersøkes.
- **Mandalselvas kartoppføring har `seasonEnd: '08-31'`**, mens datagrunnlaget nå
  inneholder september. Ikke endret, siden feltet styrer åpen/stengt-visningen og
  riktig sesongslutt for 2026 ikke er bekreftet.
- Grunnproblemet er ikke løst, bare symptomet. Så lenge tabellen er statisk vil
  den drifte igjen ved neste `config.json`-endring eller datablokkoppdatering.
  Varig løsning er en GitHub Action som regenererer tabellene ved push til
  `*/index.html` eller `data/config.json`, med samme Node-metode som er brukt her.
