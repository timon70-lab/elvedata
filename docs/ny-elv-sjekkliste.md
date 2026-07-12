# Ny elv – sjekkliste for Elvedata

> **Trigger:** Denne prosessen startes **kun i chat** med en melding på formen
> `Ny elv – {navn} – {regulert/uregulert}`
>
> Skal **ikke** trigges i Cowork — se begrunnelse under punkt 4.

---

## 1. Datagrunnlag som må være på plass før bygging starter

### Kritisk – bygging kan ikke starte uten disse

- [ ] **Fangstlogg 2016–2025**
  CSV med `Dato;Vekt;Fisk;Redskap;Sone` — eller Inatur-eksport med `Aar/Vald_Sone/Oppdrett`-format (som Mandalselva/Otra).
- [ ] **Komplett daglig vannføringsserie 2016–2025**
  Ikke bare fangstdager — kreves for DAYS_DATA/fangstrate-beregning. Sjekk eksplisitt om filen faktisk er daglig (Otra kom ferdig som ~daglig serie; Audna/Lygna-filene er semikolon-separerte rådata som må sjekkes for hull).
- [ ] **NVE-stasjon** (ID + navn)
  Verifiser at stasjonen faktisk dekker fiskestrekningen — ikke bare nærmeste stasjon oppstrøms/nedstrøms uten reell relevans.
- [ ] **Kvoteregler for gjeldende sesong**
  Døgnkvote, sesongkvote, gjenutsetting/65cm-regler. **Sjekk eksplisitt om kvoteformatet avviker fra antall-basert** (Otra har f.eks. kg-basert sesongkvote i stedet for antall laks) — scoringslogikken må tåle dette, anta ikke samme format som forrige elv.
- [ ] **Sesongdatoer**
  Bekreftet fra Inatur/elveeierlag — varierer per elv og evt. per sone. Ikke antatt fra andre elver.

### Nødvendig, men kan komme litt senere i prosessen

- [ ] **Soneliste med koordinater** (StartLat/Lon, SluttLat/Lon per sone → `elvesoner.xlsx`)
  Dashboardet kan bygges med foreløpige koordinater/markører og oppdateres når soner er ferdig kartlagt.
- [ ] **Inatur riverId** for laksebørsen (fra GraphQL-kallet på `laksebors.inatur.no/bors/{id}`)
  Nødvendig for `fangst_pipeline.yml`-integrasjon, men dashboardet kan leveres med statisk historisk data først og kobles på live-børs etterpå.
- [ ] **Inatur-sider per sone/vald** (kortUrl + beskrivelse til `ZONE_INFO`)

---

## 2. Info Per Lasse må skaffe manuelt

Dette er ting Claude ikke kan løse fra data alene:

- [ ] Kontakt med elveeierlag/Inatur for å bekrefte sesongdatoer og evt. sone-spesifikke regler
- [ ] Finne Inatur riverId (krever åpning av devtools/nettverksfanen på riktig laksebørs-side)
- [ ] Avklare **regulert/uregulert-status** — avgjør fiskemelding-metode (se punkt 3)
- [ ] Fysisk/visuell bekreftelse av sonegrenser — spesielt nær kjente problemgrenser (jf. Audna Sone 2/3)
- [ ] Eventuell 21°C-regel eller andre spesialregler som ikke fremgår av kvoteoversikten
- [ ] Endelig godkjenning av kvoter for sesongen — kan endres sent (jf. Mandalselva, bekreftet endelig først 2026-07-07)

---

## 3. Metodevalg som avhenger av regulert/uregulert

**Uregulert** (som Audna/Lygna):
Fiskemelding basert på nedbørrespons (MET-varsel → vannstandsstigning). Responstid må kartlegges per elv gjennom korrelasjonsstudie mot fangstdata:
- Audna: samme dag (r=0.68, Laudal-Kleiven SN41175)
- Lygna: 1–2 døgns forsinkelse pga. innsjøbuffer (Lygne) (r=0.62 ved lag 2 dager)

**Regulert** (som Mandalselva):
Nedbørmetoden gjelder **ikke**. Fiskemelding = sesong-/oppgangsprofil fra fangstloggen + dagens vannføring (svak persistens, 1–2 dager) + temperaturvakt hvis elva har 21°C-regel.

**Andre tekniske valg:**
- Slider-range: bruk faktisk datarange i sesongvinduet (min/maks bin med data). Vurder samlebin i toppen hvis høye bins har <10 dager hver (jf. Mandalselvas 150+-bin).
- Oversiktskart (`index.html`): oppdateres **kun** på eksplisitt forespørsel — aldri som del av standard ny-elv-bygging.
- Versjonsnummer: `v{major}.{minor_3siffer}`. Major=1 hvis elva er koblet til oversiktskartet, major=0 hvis ikke (f.eks. første versjon av ny elv = v0.001).

---

## 4. Arbeidsdeling: Cowork vs. Chat

### Det Cowork trygt kan gjøre
Avgrensede, verifiserbare oppgaver uten prosjektbeslutninger:
- Rense/validere CSV-filer (finne hull i vannføringsserien, håndtere komma-i-feltnavn-problemer som i Audna/Lygna-fangstloggene)
- Beregne P90-verdier, binning, collector-bins for høy vannføring
- Kjøre Python-reimplementering av scoring-logikk mot faktiske data, som uavhengig verifisering
- `node --check` og div-balanse-validering
- Generere rådata-transformasjoner (f.eks. Vald_Sone → sone-mapping)

### Det som bør holdes i chat
Krever prosjektminne/kontekst og reelle beslutninger:
- **Selve trigger-frasen** `Ny elv – {navn} – {regulert/uregulert}` — Cowork har ikke nødvendigvis tilgang til samme prosjektminne (tidligere elvers konvensjoner, kjente fallgruver, UX-standarder A/B/C under punkt 5)
- Endelig sammenstilling av dashboard-HTML fra mal
- Vurdering av hvilken fiskemelding-metode som passer (skjønnsvurdering)
- Versjonsnummerering og oversiktskart-kobling

**Anbefalt flyt:** Bruk Cowork som "forarbeider" — la den rense og validere data, beregne statistikk, og levere et strukturert datasett + rapport. Ta deretter selve beslutningen om å trigge "Ny elv"-byggingen **i chat**, med det ferdige datagrunnlaget som input. Slik unngår du at malkopiering/leveranse skjer uten full sjekkliste og UX-standarder tilgjengelig.

> Bakgrunn: Otra ble ved en feil trigget i Cowork i stedet for chat, noe som gjorde leveransen rotete.

---

## 5. Kart-UX-standarder (gjelder alle dashboard, uansett elv)

**A) Smooth slider — fast bredde på verdi-etiketten**
`.ctrl-val`-klassen (verditeksten ved siden av hver slider — vannføring/år/måned) må ha `min-width: 88px`. Uten dette endrer etikett-teksten bredde når intervallet skifter (f.eks. «5–10 m³/s» → «145–150 m³/s»), som får slideren til å oscillere under drag.

**B) Behold kartposisjon når en fokusert sone mister fokus**
I `selectZone()`s «lukk sone»-gren skal `map.fitBounds(allCoords, {...})` fjernes helt. Uten dette zoomer kartet automatisk ut til hele elva hver gang en sone lukkes.

**C) Ikke scroll siden ved hver slider-endring**
`showZoneInfo(zone, scrollTo=true)` skal bruke `if (scrollTo) panel.scrollIntoView(...)`. `update()`s kall ved slider-endring må sende `showZoneInfo(activeZone, false)`.

---

## 6. Validering før levering (uansett elv)

1. `node --check` for JS-syntaks
2. Div open/close-balansesjekk
3. Sammenlign alle topp-nivå `let`/`const`/`var`-deklarasjoner mot malen via regex — verifiser at alt som brukes er deklarert (`node --check` fanger kun syntaks, ikke manglende deklarasjoner — kritisk lærdom fra Mandalselva v3-krasjet)

---

## 7. Endringslogg for denne sjekklisten

| Dato | Endring |
|---|---|
| 2026-07-13 | Første versjon — kombinerer opprinnelig huskeliste med lærdom fra Otra-implementeringen (kvoteformat-variasjon, Cowork/chat-arbeidsdeling, trigger-frase-presisering) |
