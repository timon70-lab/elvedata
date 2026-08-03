# Utviklerkonvensjoner

Regler for hvordan endringer lages, valideres og publiseres. Disse er ikke stilpreferanser
— de er reaksjoner på faktiske feil som har oppstått.

---

## Versjonering

Filnavn ved levering:

```
{elv}_dynamisk_oversikt_{iterasjon}.html
```

Aldri `index.html` lokalt. Filen gis navnet `index.html` først ved opplasting til riktig
mappe i repoet. Dette hindrer at to ulike versjoner forveksles.

Versjonsnummeret vises i footeren:

```
v{major}.{iterasjon, 3 siffer}
```

`major` er **1** for elver som er koblet til oversiktskartet, **0** for frittstående
dashboard under utvikling.

**Én leveranse per fil per runde.** Alle endringer samles i én ny versjon i stedet for å
levere flere mellomversjoner. Iterasjonsnummeret økes med nøyaktig én per levert fil.

---

## Valideringssekvens

Skal kjøres **før hver eneste leveranse**, uten unntak.

**1. Hent fersk fil fra repoet**

```bash
curl -s "https://raw.githubusercontent.com/timon70-lab/elvedata/main/{elv}/index.html" \
     -o {elv}.html
```

Aldri jobb videre på en lokal kopi fra en tidligere runde. Filen kan ha endret seg.

**2. Sjekk for git-konfliktmarkører**

```bash
grep -c "<<<<<<<\|=======\|>>>>>>>" {elv}.html
```

Dette har skjedd i publiserte filer på Audna, Mandalselva og Sygna. Finner du markører:
varsle, identifiser riktig side (som regel den sist leverte versjonen), fjern markørene og
lever en ren fil.

> Merk: kommentarseparatorer med `====` gir falske treff. Bruk `----` i stedet.

**3. Trekk ut og syntakssjekk alle script-blokker**

```python
scripts = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', content, re.S)
```

Kjør `node --check` på hver blokk. Dette fanger opp de fleste feilene.

**4. Verifiser div-balanse**

```python
assert content.count('<div') == content.count('</div>')
```

**5. Sammenlign deklarasjoner på toppnivå**

Sett opp alle `const`/`let`/`var`/`function`-navn i original og patchet fil. Listen
«Removed» skal være tom. Dette fanger opp den vanligste alvorlige feilen: at en
tekstutskifting ved et uhell sletter en funksjonsdefinisjon.

**6. Sikre entydige tekstutskiftinger**

```python
assert content.count(OLD) == 1
```

Før hver `str.replace()`. Uten dette kan en endring treffe feil sted, eller flere steder.

For Python-filer: `ast.parse()` i stedet for `node --check`.

---

## Testflyt

1. **Staging først** for oversiktskartet: `staging/index.html` har `noindex`, en synlig
   oransje STAGING-stripe og deaktivert GoatCounter, men bruker ekte data.
2. **Sygna først** for endringer som skal rulles ut på alle elver. Er den godkjent der,
   gjøres samme endring på de øvrige fire.

---

## Kart-UX-standarder

Obligatorisk for alle dashboard, også fremtidige elver. Hver av disse løser en konkret
irritasjon som ble rapportert i bruk.

**A — fast bredde på slider-etiketten**

```css
.ctrl-val { min-width: 88px; }
```

Uten dette endrer etiketten bredde når intervallteksten skifter (f.eks. «5–10 m³/s» →
«145–150 m³/s»), noe som får slideren til å endre bredde midt i et drag. Det oppleves som
at slideren hopper.

**B — behold kartposisjon når en sone lukkes**

I `selectZone()` sin «lukk sone»-gren skal `map.fitBounds(allCoords, ...)` være fjernet
helt. Uten dette zoomer kartet ut til hele elva hver gang man lukker en sone.

**C — ikke scroll siden ved hver slider-endring**

`showZoneInfo(zone, scrollTo = true)` må ha `scrollTo`-parameteren, og `update()` må kalle
`showZoneInfo(activeZone, false)`. Uten dette hopper siden til infopanelet hver gang
brukeren drar i en slider.

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

**Idélogging:** melding som starter med `ide:` skal logges som mulig fremtidig endring, ikke
implementeres.

**Ny elv:** utløses av `Ny elv – {navn} – {regulert/uregulert}`. Se
[ny-elv-sjekkliste.md](ny-elv-sjekkliste.md).

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
