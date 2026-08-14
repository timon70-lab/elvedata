# 2026-08-14 — Ny elv: Tovdalselva

**Type:** ny elv
**Leveranse:** `tovdalselva_dynamisk_oversikt_4.html` (v0.004), `nve_cache.yml`,
`soner.json`, `config.json`, `photos_tovdalselva.json`, `videoer_tovdalselva.json`

## Hva ble endret

Sjette elv i systemet. Bygget på Audna-malen, med Sygnas artstoggle portert inn.
Major = 0 fordi elva ikke er lenket fra oversiktskartet.

- NVE-stasjon Flakksvann 20.3.0, MET-punkt Hynnekleiv (58,6020 / 8,4181)
- Bin 5 m³/s, slider 0–85, samlebin 85+
- Sju soner: Sone 1, Sone 2, Sone 3, Sone 4 og 5, Teinefoss Fluefiske, Buhølen, Laksefoss
- Kartsentrum ved oppstart: 58,292383 / 8,188960, zoom 10

## Hvorfor

**Artsvalg — laks + sjøørret med «Kun laks»-toggle.** Sone 1 er 81 % sjøørret
(78 laks mot 337 sjøørret 2016–2025). På en ren laksescore ville sona ligget nær
null i alle bins og fremstått som død, når den i realiteten er elvas viktigste
sjøørretstrekning. Døgnkvoten dekker begge arter (1 laks / 2 sjøørret), så
Sygna-modellen passer bedre enn Audnas rene lakseskår.

**Sone 3a utelatt.** 22 laks totalt og ingen koordinater i `elvesoner.xlsx`. Uten
koordinater kan sona verken tegnes i kartet eller brukes i GPS-basert
soneidentifisering. Fangstene teller ikke med i noen sone.

**Bin-valg.** Fangstraten stiger monotont fra 0,58 laks/døgn ved 0–5 m³/s til
rundt 8–11 ved 50–85. Bin 0–80 dekker 94 % av sesongdøgnene og 93 % av laksen,
og alle bins under 85 har minst 10 dager. Samlebin 85+ får 53 dager og 252 laks.

**Sesongvinduer varierer per år og ble lest ut av fangstloggen**, ikke antatt:
2016, 2017, 2019 og 2020 gikk til 15. september, øvrige år til 31. august. Flatt
vindu ville gitt feil nevner i DAYS_DATA for fire av ti år.

**Konstantutledning ble reversert fra Audnas live-fil**, ikke gjettet. MAX-verdiene
traff eksakt (11,0 / 1356 / 6,0 / 326) og P90_RATE_ELV eksakt (21,25), som bekrefter
oppskriften: zone-nivå er persentil over (bin, sone) aggregert over hele vinduet,
elv-nivå er dagvektet persentil over (år, måned, bin)-celler.

## Berørte dokumentasjonsavsnitt

| Fil | Avsnitt | Hva må skrives om |
|---|---|---|
| docs/scoring.md | ## Konstanter per elv | Tovdalselva mangler i tabellen |
| docs/scoring.md | ## Konstanter per elv | Teksten sier Sygna er eneste elv som scorer laks + sjøørret — nå to |
| docs/datamodell.md | ## Filoversikt | `photos_tovdalselva.json`, `videoer_tovdalselva.json`, `vannforing_tovdalselva.json`, `nedbor_tovdalselva.json` |
| docs/datamodell.md | ## Soner som ekskluderes | Tovdalselva: `Sone 3a` |
| docs/automatisering.md | ### nve_cache.yml | Seks stasjoner og fire nedbørpunkter, ikke fem og tre |
| docs/ny-elv-sjekkliste.md | ## 7. Endringslogg | Nye lærdommer, se eget punkt under |

## Validering

`node --check` OK, div-balanse 107/107, ingen konfliktmarkører, ingen tapte
deklarasjoner mot malen. Tørrkjøring av datablokkene: 980 sesongdøgn, 4406 fangster,
3681 laks, bins 0–85 i 5-steg uten hull. Kart-UX-standardene A, B og C verifisert
intakte. `soner.json` og `config.json` verifisert bit-for-bit uendret for de fem
eksisterende elvene.

## Åpne punkter

- Sone 4 og 5 spenner over 14 km med mange svinger. Avstand til rett linje mellom
  start- og sluttkoordinat blir stor (T-001 lå 666 m unna), så GPS-forslaget for
  sonen er upålitelig og må overstyres manuelt.
- Laksefoss, Buhølen og Teinefoss ligger geografisk inne i Sone 4 og 5 sitt
  koordinatspenn. Fangstene er gjensidig utelukkende i loggen, så scoringen er
  trygg, men kartrenderingen trenger samme behandling som Audnas Sone5/5A/5B.
- 2024 har siste fangst 18. august. Om elva faktisk stengte tidlig det året, er
  augustnevneren for høy. Ikke bekreftet med elveeierlaget.
- Elva er ikke lagt til på oversiktskartet — skal ikke gjøres uten eksplisitt ønske.
