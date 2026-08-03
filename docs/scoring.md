# Scoringsmetodikk

Hvordan sonescoren 0–100 beregnes, og hvorfor den er bygget slik.

Referanseimplementasjon: `computeScores()` og `scaleScore()` i hver elvs `index.html`.
Denne beskrivelsen skal til enhver tid stemme med koden — endres den ene, må den andre
følge etter.

---

## Problemet som skal løses

Spørsmålet scoren forsøker å svare på er: *gitt denne vannføringen, i denne
sesongperioden, hvilke soner har historisk levert best fiske?*

Den naive tilnærmingen — å telle fangster per sone ved gjeldende vannføring — bryter
sammen på tre måter:

1. **Ujevn observasjonsmengde.** En sone kan ha 40 fangster fordi den er god, eller
   fordi vannføringen tilfeldigvis lå der i mange dager. Rå tellinger måler like mye
   været som fisken.
2. **Tynne bins.** Ved uvanlige vannføringer finnes det kanskje tre observerte dager.
   En enkelt heldig dag gir da en rate som ser spektakulær ut, men ikke betyr noe.
3. **Ekstremverdier.** Én rekorddag med 30 fangster ville dominert en lineær skala og
   presset alle andre soner ned mot null.

De tre stegene under adresserer nøyaktig disse tre problemene, i rekkefølge.

---

## Steg 1 — Glatting mot nabobins

Fangstdata deles i vannføringsbins (binstørrelsen varierer per elv, se tabellen nederst).
I stedet for kun å bruke bin-en brukeren har valgt, slås den sammen med bin-en over og
under, med trekantvekting:

```
vekt senterbin  wC = 2
vekt nabobins   wN = 1

poolDays = 2·dager(senter) + 1·dager(under) + 1·dager(over)
effDays  = poolDays / 2
smRate   = (2·fangst(senter) + 1·fangst(under) + 1·fangst(over)) / poolDays
```

Nabobins telles kun med dersom de faktisk har observerte dager. Har ingen av de tre
bin-ene data, returnerer funksjonen `null` og sonen vises uten score i stedet for å
gjette.

**Hvorfor:** vannføring er en kontinuerlig størrelse, og grensen mellom 15 og 20 m³/s er
vilkårlig. Fisket ved 19 m³/s ligner mer på 21 enn binstrukturen antyder. Glattingen
låner statistisk styrke fra naboene uten å viske ut den reelle vannføringsavhengigheten.

`effDays` er poolDays skalert tilbake til «ekte dager»-nivå, slik at vektene ikke blåser
opp datamengden kunstig i neste steg.

---

## Steg 2 — Empirisk Bayes-krymping

Den glattede raten trekkes mot sonens egen gjennomsnittsrate over *alle* vannføringer i
det valgte år- og månedsvinduet:

```
prior  = totale fangster i sonen i vinduet / totale observerte dager i vinduet
shrunk = (smRate · effDays + C · prior) / (effDays + C)
```

`C` (`shrinkC` i konfigurasjonen, standard **15**) tolkes som antall pseudo-dager
priorinformasjon.

**Hvorfor:** dette er den viktigste mekanismen mot falske toppscorer. Effekten avhenger
av hvor mye data som finnes:

- Har en sone **3 effektive dager** ved denne vannføringen, veier prioren 15/18 ≈ 83 %.
  Sonen får omtrent sin normale rate, uansett hvor heldig de tre dagene var.
- Har den **100 effektive dager**, veier prioren 15/115 ≈ 13 %. Da får den faktiske
  observasjonen ved denne vannføringen dominere, slik den skal.

Krympingen skrur altså seg selv opp og ned etter datagrunnlaget. Valget av C = 15 er en
skjønnsmessig avveining: høyt nok til å dempe bins med under ti dager, lavt nok til at
soner med solid datagrunnlag ikke jevnes ut mot middelmådighet.

---

## Steg 3 — To-segments skala

Både den krympede raten og det rå fangstvolumet skaleres til 0–100 gjennom `scaleScore`:

```
x ≤ P90:   score = knee · x / P90                    (lineær)
x > P90:   score = knee + (100−knee) · ln(x/P90) / ln(maks/P90)   (logaritmisk)
```

`knee` er standard **80**.

**Hvorfor:** 90-persentilen brukes som referansepunkt i stedet for absolutt maksimum,
fordi maksimum ofte er en enkelthendelse. Under P90 — der de aller fleste observasjoner
ligger — er skalaen lineær og lett å tolke. Over P90 komprimeres den logaritmisk, slik at
eksepsjonelle dager fortsatt gir høyere score enn gode dager, men uten å ta over hele
skalaen.

Praktisk konsekvens: score 80 betyr «på nivå med de beste 10 % av observasjonene». Å
komme fra 80 til 100 krever ikke 25 % mer fangst, men en flerdobling.

---

## Sammenslåing

De to skalerte størrelsene vektes sammen:

```
score = scaleScore(shrunk, P90_RATE, MAX_RATE) · rateWeight
      + scaleScore(vol,    P90_VOL,  MAX_VOL)  · volWeight
```

`vol` er råtallet for fangster i senterbin — altså uglattet og ukrympet. Rateleddet
svarer på «hvor godt fisker det her per dag», mens volumleddet gir en viss uttelling for
soner der det faktisk tas mye fisk totalt.

Standardvekting er 0,8 rate / 0,2 volum. **Mandalselva bruker 1,0 / 0,0** — ren rate,
uten volumledd — fordi elva har svært mange små soner med ujevn størrelse, og
volumleddet der endte med å belønne store soner framfor gode soner.

---

## Fargeskala

Terskler i `scoreColor()` skaleres mot `knee`, slik at fargene følger med hvis knee
endres:

| Farge | Terskel (ved knee = 80) | Tekst |
|---|---|---|
| 🟢 Grønn | ≥ 56 | Svært godt |
| 🔵 Blå | ≥ 36 | Godt |
| 🟠 Oransje | ≥ 20 | Middels |
| 🔴 Rød | < 20 | Svakt |

---

## Justerbare parametre

`data/config.json` leses ved kjøretid og kan endres via admin-panelet uten å publisere
nye HTML-filer:

```json
{ "rateWeight": 0.8, "volWeight": 0.2, "shrinkC": 15, "knee": 80 }
```

Faller hentingen, brukes innebygget fallback med de samme standardverdiene.

**Merk:** oversiktskartets score-tabeller er forhåndsberegnede og reagerer *ikke* på
endringer i `config.json`. Justeres parametrene, vil oversiktskartet og elve-dashbordene
kunne vise ulike tall inntil oversiktskartet bygges på nytt.

---

## Konstanter per elv

`P90_*` og `MAX_*` beregnes fra elvas eget historiske datagrunnlag og bakes inn i
HTML-filen. De må beregnes på nytt dersom fangsthistorikken utvides.

| Elv | Bin | Samlebin | P90 rate | P90 volum | Vekting |
|---|---|---|---|---|---|
| Audna | 5 m³/s | 55+ | 5,30 | 173,5 | 0,8 / 0,2 |
| Lygna | 5 m³/s | 55+ | 1,58 | 63,4 | 0,8 / 0,2 |
| Mandalselva | 15 m³/s | 150+ | 0,82 | 38,0 | 1,0 / 0,0 |
| Otra | 25 m³/s | 300+ | 1,95 | — | 0,8 / 0,2 |
| Sygna | 2 m³/s | 18+ | — | — | 0,8 / 0,2 |

Audna og Lygna har i tillegg egne konstanter for «kun flue»-visningen
(`P90_RATE_FLY`, `P90_VOL_FLY` og tilsvarende maks).

Sygna scorer **laks og sjøørret samlet**, i motsetning til de øvrige elvene som kun
teller laks. Sygna er primært en sjøørretelv, og en ren lakseskår ville hatt for tynt
datagrunnlag.

---

## Kjente svakheter

Disse er erkjente og ikke løst. De bør være kjent for alle som tolker tallene.

**Ingen innsatsjustering.** Nevneren er kalenderdager, ikke fiskeinnsats. En sone med
mange solgte kort og en med få behandles likt. Fangst per kortdøgn ville vært mer
robust, men datagrunnlaget finnes ikke.

**Kvoteendringer over tid.** Strengere kvoter demper registrerte fangsttall på gode dager
uavhengig av hvor mye fisk som står i elva. Det gjør sammenligning på tvers av år skjev,
i disfavør av nyere sesonger.

**Nåtidsrelevans.** Scoren bygger på hele 2016–2025. Fangstratene har falt i alle fem
elver siden omtrent 2020 — mest markant i Mandalselva, der de grovt regnet er halvert.
Scoren beskriver derfor *historisk sonekvalitet*, og kan overvurdere dagens fisketetthet.
Mulige tiltak under vurdering: nyhetsvekting, rullerende femårsvindu, eller tydeligere
kommunikasjon av hva tallet faktisk er. Avventer 2026-data.

**Gjenutsatt fisk.** Fangstloggen skiller på gjenutsetting, men scoren gjør det ikke.

---

## Validering ved endringer

Endres scoringslogikken, skal JS-implementasjonen kryssvalideres mot en uavhengig
Python-beregning på samme datagrunnlag før publisering. Avvik skal være null, ikke
«omtrent likt» — en forskjell tyder på at ett av stegene er implementert ulikt et sted.
