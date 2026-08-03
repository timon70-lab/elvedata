# Admin-brukerveiledning

Praktisk veiledning for `admin/index.html`. Skrevet med mobilbruk i tankene, siden det er
der mesteparten av redigeringen skjer.

---

## Førstegangsoppsett: GitHub-token

Uten token kan du se skjemaene, men ikke lagre noe. Tokenet lagres **lokalt i nettleseren
din** — PC og mobil trenger hvert sitt.

**Opprette token:**

1. Gå til **`github.com/settings/tokens?type=beta`** i mobilnettleseren
   (ikke GitHub-appen — den støtter ikke opprettelse av fine-grained tokens)
2. **Generate new token**
3. Fyll ut:
   - **Token name:** f.eks. `elvedata-admin-mobil`
   - **Resource owner:** `timon70-lab`
   - **Expiration:** velg selv, f.eks. 90 dager
   - **Repository access:** «Only select repositories» → **elvedata**
   - **Permissions** → **Repository permissions** → **Contents** → **Read and write**
4. **Generate token** nederst
5. **Kopier verdien med en gang** — den vises kun denne ene gangen

**Legge inn i admin:**

1. Åpne `admin/index.html`
2. Åpne seksjonen **🔑 Nøkler og tilgang**
3. Lim inn i GitHub-token-feltet → **Lagre**

Feltet viser deretter «Token er lagret ✓». Skal du bytte, lim bare inn et nytt.

---

## 📰 Nyheter

Ligger øverst på siden, med to faner.

### Legge inn en nyhet

1. **Kilde** — velg fra nedtrekket. Elv og tilgangstype fylles automatisk, men kan
   overstyres.
2. **Overskrift** — dette er teksten som ruller i banneret. Hold den kort; lange
   overskrifter tar lang tid å rulle forbi.
3. **Lenke** — direkte til artikkelen eller innlegget, ikke til forsiden av kilden.
4. **Vis fra dato** — forhåndsutfylt med dagens dato. Nyheten blir aktiv med en gang hvis
   du lar den stå.
5. **Vis til dato** — valgfritt. La stå tom for «vis til jeg sletter den».
6. **➕ Legg til nyhet**

Nyheten dukker opp i banneret innen ca. 10 minutter (GitHub Pages-cache).

### Redigere en nyhet

Trykk **Rediger** på raden. Skjemaet fylles ut, overskriften endres til «Rediger nyhet»,
og knappen blir **💾 Oppdater nyhet**. ID-en beholdes — det opprettes ingen duplikat.

**Avbryt** i den blå linjen går ut av redigeringsmodus uten å lagre.

### Status-merker

| Merke | Betyr |
|---|---|
| **AKTIV** | Vises i banneret nå |
| **KOMMENDE** | Vis fra-dato ligger frem i tid |
| **UTLØPT** | Vis til-dato er passert |

Banneret viser nyheter sortert med **nyeste først**. Listen i admin viser eldste først, for
å gi bedre oversikt.

### 🔗 Kilder

Registrer kildene dine én gang, så slipper du å taste tilgangstype for hver nyhet.

- **Navn** — f.eks. «Laksefiskere i Mandalselva»
- **Type** — Side / Åpen Facebook-gruppe / Lukket Facebook-gruppe
- **Elv**
- **URL** — grunnlenken til kilden

**Slik finner du ut om en Facebook-gruppe er åpen:** gå inn på gruppen og se rett under
navnet. Står det «Offentlig gruppe» med globe-ikon, er den åpen. Står det «Privat gruppe»,
er den lukket — da vil lesere uten medlemskap møte en vegg.

**Slik kopierer du gruppelenken på mobil:** trykk de tre prikkene (⋯) → **Share** →
**Copy link**. Enkelte menyer mangler «Kopier lenke» direkte; da er Share riktig vei.

Sletter du en kilde, beholder eksisterende nyheter sin elv og tilgangstype uendret.

---

## 🎬 Media

To faner: **Video** og **Bilde**.

**Video:** lim inn YouTube-lenke, velg elv og sone, legg til beskrivelse. Sletting fjerner
kun oppføringen — videoen på YouTube må fjernes separat.

**Bilde:** for bilder uten GPS, eller når automatisk sonetilordning bommer. Bildet
komprimeres til maks 1600 px og EXIF fjernes automatisk. Sletting fjerner både oppføringen
**og** selve bildefilen fra repoet.

**Koordinater fra Google Maps:** høyreklikk i kartet (langt trykk på mobil) og trykk på
tallene for å kopiere.

**📋 Registrert innhold** nederst viser alt registrert per elv og sone, med filter på
video/bilde.

---

## ⚖️ Scoringsparametre

Sjelden brukt. Justerer `rateWeight`, `volWeight`, `shrinkC` og `knee` per elv, og skriver
til `data/config.json`.

> ⚠️ **Endringene slår ikke gjennom på oversiktskartet.** Score-tabellene der er
> forhåndsberegnede. Endrer du parametre, vil elve-dashbordene og oversiktskartet vise
> ulike tall inntil oversiktskartet bygges på nytt.

Se [scoring.md](scoring.md) for hva parametrene faktisk gjør før du endrer dem.

---

## Laste opp nye dashboard-filer fra mobil

1. Last ned filen fra chatten → havner i Filer / Nedlastinger
2. Gå til repoet på **github.com** i mobilnettleseren (ikke appen)
3. Naviger til riktig mappe, f.eks. `mandalselva/`
4. **Add file** → **Upload files**
5. Velg filen fra Filer / Nedlastinger
6. **Endre filnavnet til `index.html`** før du committer — dette kan gjøres direkte i
   GitHubs opplastingsdialog
7. Skriv commit-melding → **Commit changes**

---

## Sikkerhet

Admin-siden ligger åpent på GitHub Pages og har `noindex`. Andre som finner URL-en kan se
skjemaene og lese data — men ikke endre noe, siden skriving krever ditt personlige token.

**Det som faktisk må beskyttes er tokenet, ikke lenken:**

- Lim aldri inn tokenet på en delt eller fremmed enhet
- Del aldri skjermbilde der token-feltet er utfylt
- Bruk alltid fine-grained token begrenset til `elvedata` med kun `Contents: read/write`
