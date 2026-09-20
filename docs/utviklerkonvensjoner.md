# Utviklerkonvensjoner

Regler for hvordan endringer lages, valideres og publiseres. Disse er ikke stilpreferanser
— de er reaksjoner på faktiske feil som har oppstått.

---

## Versjonering

Dashboardet for hver elv redigeres direkte som `{elv}/index.html` i repoet.

Tidligere ble hver runde levert som en nummerert kopi, `{elv}_dynamisk_oversikt_{iterasjon}.html`,
for å hindre at to versjoner ble forvekslet. Det er ikke lenger nødvendig — git-historikken
holder versjonene fra hverandre. Nummererte kopier skal ikke lages.

Versjonsnummeret vises i footeren:

```
v{major}.{iterasjon, 3 siffer}
```

`major` er **1** for elver som er koblet til oversiktskartet, **0** for frittstående
dashboard under utvikling. Det finnes nøyaktig ett treff på `v{major}.{minor}` per fil —
se «Repo-kart» i [CLAUDE.md](../CLAUDE.md) for plassering og gjeldende versjon per elv.

**Én leveranse per fil per runde.** Alle endringer samles i én ny versjon i stedet for å
levere flere mellomversjoner. Iterasjonsnummeret økes med nøyaktig én per levert fil, og
nullstilles aldri: ved go-live går Tovdalselva fra v0.006 til v1.007, ikke v1.000.

---

## Valideringssekvens

Skal kjøres **før hver eneste commit**, uten unntak:

```bash
python scripts/valider.py {elv}/index.html
```

Skriptet tar flere filer på én gang. `--mot REF` sammenligner deklarasjoner mot en annen
git-referanse enn `HEAD`, `--uten-jsdom` hopper over røyktesten. Feiler noe, avslutter det
med `RESULTAT: FEIL — ikke commit` og kode 1. Da committer du ikke.

Sjekkene, og hvorfor hver enkelt finnes:

**1. Git-konfliktmarkører.** Dette har faktisk stått i publiserte filer på Audna,
Mandalselva og Sygna. Finner skriptet markører: identifiser riktig side (som regel den sist
leverte versjonen), fjern markørene og kjør på nytt. Mønsteret krever sju tegn på
linjestart fulgt av mellomrom eller linjeslutt, så separatorer som `----` og `====` i
kommentarer gir ikke falske treff.

**2. `node --check` på hvert inline `<script>`.** Blokker med `src=`, og `type` satt til
`application/json`, `application/ld+json` eller `text/template`, hoppes over. Fanger de
fleste syntaksfeilene.

**3. Div-balanse.** `<div` mot `</div>` over hele fila. Merk at tellingen også får med
`<div`-strenger inne i JS-maler — står de ubalansert der, slår sjekken ut selv om HTML-en
er riktig.

**4. HTML-nesting.** Stakkbasert sjekk som gir linjenummer for tagger som lukkes uten
åpning, eller som aldri lukkes. `<script>` og `<style>` strippes først.

**5. Toppnivå-deklarasjoner mot git.** Alle `let`/`const`/`var`/`function`/`class`-navn på
klammedybde 0 sammenlignes med samme fil i `HEAD`. «Borte»-listen skal være tom. Dette
fanger den vanligste alvorlige feilen: at en tekstutskifting ved et uhell sletter en
funksjonsdefinisjon. Nye navn rapporteres som `info`. For en fil som ikke finnes i
referansen — en ny elv — hoppes sjekken over.

**6. jsdom-røyktest** (`scripts/jsdom_smoke.js`). Hoppes over med `info` hvis jsdom ikke er
installert (`npm i -D jsdom`). Da er den sjekken reelt ikke kjørt.

For Python-filer finnes ingen tilsvarende automatikk — bruk `ast.parse()`.

---

## Patching

Ikke jobb videre på en lokal kopi fra en tidligere runde, og ikke bygg fra hukommelse.
`git pull` ved øktstart, og les gjeldende fil i repoet før endring.

Ved tekstutskifting i Python — `rep()`-mønsteret:

```python
assert content.count(OLD) == 1
```

Før hver `str.replace()`. Uten dette kan en endring treffe feil sted, eller flere steder.
Valideringen fanger en erstatning som sletter en deklarasjon, men ikke en som landet
syntaktisk riktig på feil sted.

Ved jsdom-feilsøking: bruk `w.eval('...')` for å nå variabler i page-scope — direkte
`w.fn()` feiler.

---

## Testflyt

1. **Staging først** for oversiktskartet: `staging/index.html` har `noindex`, en synlig
   oransje STAGING-stripe og deaktivert GoatCounter, men bruker ekte data.
2. **Sygna først** for endringer som skal rulles ut på alle elver. Er den godkjent der,
   gjøres samme endring på de øvrige fem.

---

## Kart-UX-standarder

Obligatorisk for alle dashboard, også fremtidige elver. Hver av dem løser en konkret
irritasjon som ble rapportert i bruk:

- **A** — fast bredde på slider-etiketten (`.ctrl-val { min-width: 88px; }`)
- **B** — behold kartposisjon når en fokusert sone lukkes
- **C** — ikke scroll siden ved hver slider-endring

Nøyaktig kode og full begrunnelse: [kart-ux-standarder.md](kart-ux-standarder.md). Den fila
er fasit — reglene sto tidligere i sin helhet begge steder, og skal vedlikeholdes ett sted.

---

## Mediepanel-standard

Navigeringsknappene for bilde og video ligger i **egen rad** under panelheaderen, ikke
inne i headeren:

```css
.photo-nav-row { display:flex; justify-content:center; align-items:center;
                 gap:18px; padding:8px 14px; background:#f0fff4;
                 border-bottom:2px solid #c6f6d5; }
.pg-nav-btn { border:2px solid #9ae6b4; font-weight:700; font-size:1.35rem;
              min-height:44px; padding:6px 20px; border-radius:8px; }
```

`min-height: 44px` er berøringsmålet — mindre enn det er vanskelig å treffe på mobil.

---

## Prosessregler

**UI-endringer:** lag alltid en mockup for godkjenning før koden skrives.

**Leveranserunde:** alle endringer for én elv samles i én commit, med meldingen
`{elv} v{major}.{minor}: kort beskrivelse`. Endringsnotat skrives i `docs/endringer/` etter
[MAL.md](endringer/MAL.md). Hele runden er beskrevet i `/runde`. Push og PR kun når Per
Lasse ber om det.

**Idélogging:** melding som starter med `ide:` skal logges som mulig fremtidig endring, ikke
implementeres — liten idé i backlogen i [status-og-backlog.md](status-og-backlog.md),
større idé som egen fil i `docs/ideer/`. Se `/ide`.

**Ny elv:** utløses av `Ny elv – {navn} – {regulert/uregulert}`. Se
[ny-elv-sjekkliste.md](ny-elv-sjekkliste.md) og `/ny-elv`.

**Oversiktskartet oppdateres aldri med en ny elv** uten at det er eksplisitt bedt om. Nye
elver bygges som frittstående dashboard først.

---

## Ytelseshensyn

Bildene er i dag rundt 550 kB hver, i full 1600 px bredde, også når de vises i et panel på
under 400 px. Mandalselva forhåndslaster nabobildene i galleriet, slik at navigering føles
umiddelbar.

Ikke implementert, men vurdert: egne mindre panelbilder, lavere JPEG-kvalitet, og WebP. Alle
tre krever endring i foto-pipelinen og vil kun gjelde nye bilder — eksisterende bilder må
reprosesseres i en egen jobb.
