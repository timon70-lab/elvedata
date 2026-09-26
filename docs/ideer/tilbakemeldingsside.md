# Idé: egen tilbakemeldingsside

Status: runde 1 (kjerne: Worker, side, admin) implementert 2026-09-26, ikke satt i drift eller lenket.
Punkt 4 (inngangspunkter) og 👍/👎 gjenstår. Driftsdokumentasjon: `docs/datakilder-og-infrastruktur.md`.
Loggført som idé 2026-09-26.
Beslutninger tatt: lagring i privat repo, Cloudflare Worker som mellomledd.

## Kontekst
I dag er tilbakemelding en 💬-lenke til Google Forms, kun på oversiktskartet (`index.html:96`,
`staging/index.html:89`). Nyhet N-006 i `data/nyheter.json` peker til et *annet* skjema
(`forms.gle/erbD…` mot `forms.gle/JbZt…`). Ingen av de seks dashboardene har noen lenke. Siden
juli har det kommet én tilbakemelding. Problemet er altså både **friksjon** (man forlater nettstedet
for å fylle ut et Google-skjema) og **synlighet** (lenken finnes bare ett sted).

Målet er en egen side på `elvesona.no/tilbakemelding/` som lagrer svarene som JSON og kan leses
i adminpanelet, i tillegg til flere og lettere inngangspunkter.

## Arkitektur

```
Bruker ──► elvesona.no/tilbakemelding/  (statisk skjema, GitHub Pages)
              │  POST JSON (fetch)
              ▼
        Cloudflare Worker  (gratis; holder hemmelig token)
          · validerer felt, lengdegrenser, honeypot, rate-limit per IP
          · leser tilbakemeldinger.json → legger til post → PUT (retry ved 409)
              ▼
        Privat repo  timon70-lab/elvesona-tilbakemeldinger
              tilbakemeldinger.json
              ▲
        admin/index.html  «Tilbakemeldinger»-seksjon (leser/merker med eksisterende PAT)
```

**Hvorfor dette:** Adminpanelet skriver med PAT-en din fra localStorage, men en offentlig side
kan ikke ha en token i HTML (absolutt regel 1). Workeren er det eneste som holder tokenen, og
repoet er privat, så e-post og fritekst fra brukerne blir ikke offentlig.

### 1. Privat repo + token
- Nytt privat repo `elvesona-tilbakemeldinger` med `tilbakemeldinger.json` = `[]`.
- Fine-grained PAT **kun** for dette repoet, contents: read/write. Lagres som Worker-secret
  (`wrangler secret put GH_TOKEN`), aldri i elvedata.
- Adminpanelets eksisterende PAT utvides til også å gjelde det private repoet (eller et eget token-felt).

### 2. Cloudflare Worker (`worker/tilbakemelding.js` i elvedata, uten hemmeligheter)
- `POST /` tar imot `{type, elv, sone, melding, epost?, side, versjon, website(honeypot)}`.
- CORS er låst til `https://elvesona.no` (og `localhost` ved test).
- Avviser ved fylt honeypot, `melding` < 5 eller > 2000 tegn, eller mer enn 5 innsendinger per IP per time
  (Cloudflare KV eller `caches`-basert teller).
- Legger til `id` (`T-<tidsstempel>`), `mottatt` (ISO UTC) og `status: "ny"`, og skriver deretter til repoet med
  GET sha → PUT. Ved 409 prøver den igjen opptil 3 ganger (samme mønster som push-retry i
  `issue_foto_pipeline.yml`).
- Samme kall som adminpanelets `ghGet`/`ghPut` rundt `admin/index.html:1423–1440`, med
  base64 av UTF-8 (æøå).

### 3. Siden `tilbakemelding/index.html`
- Samme stil og footer-versjonsmønster som øvrige sider (starter på `v0.001`), med GoatCounter-event ved innsending.
- Felt:
  - Type som piller: 💡 Idé · 🐞 Feil · 🎣 Fangst/sone stemte ikke · 💬 Annet
  - Elv (valgfri, forhåndsutfylt fra `?elv=`)
  - Sone (valgfri, fra `?sone=`)
  - Melding
  - E-post (valgfri, «hvis du vil ha svar»)
- Etter innsending vises en takkemelding på siden, uten at brukeren sendes videre. Er Workeren nede, vises en fallback-lenke til e-post.

### 4. Flere og lettere inngangspunkter (engasjement)
- **Alle seks dashboard:** en synlig «Gi tilbakemelding»-knapp som lenker til `/tilbakemelding/?elv={elv}`.
  Det gir én runde per elv med versjonsbump, `valider.py` og commit (jf. `/runde`).
- **Kontekstuell hurtigrespons i dashboard:** under topp 3-sonene, «Stemte dette? 👍 / 👎». Et 👎-klikk
  åpner siden med `elv` og `sone` ferdig utfylt og typen «Fangst/sone stemte ikke». Det er lavest mulig terskel
  og gir samtidig kalibreringsdata.
- **Statistikksiden og sesongsidene:** samme lenke i footer.
- **Oversiktskartet:** 💬-lenken peker nå til `/tilbakemelding/` i stedet for Google Forms. *Endringen
  gjøres kun med din eksplisitte godkjenning (regel 3). Godkjenning av denne planen regnes som det.*
- Nyhet N-006 oppdateres til å lenke til den nye siden (via admin eller JSON).

### 5. Admin
- Ny seksjon «💬 Tilbakemeldinger» i `admin/index.html`:
  - viser listen, nyeste først, med et merke for antall `ny`
  - filtrerer på type og elv
  - kan sette status til `lest`/`ferdig`, som skrives tilbake med PUT
- Gjenbruker eksisterende `getToken()` og GitHub-hjelpefunksjoner.

## Rekkefølge
1. Privat repo, PAT og Worker (deploy med `wrangler`). Test med `curl`.
2. `tilbakemelding/index.html` + adminseksjonen.
3. Lenker fra dashboardene, én elv per commit. Deretter statistikksidene.
4. Oversiktskartet og N-006 til slutt, når alt fungerer.
5. Oppdater `docs/datakilder-og-infrastruktur.md` (Worker, privat repo, PAT) og `docs/faq.md`.

## Verifisering
- `curl -X POST` mot Workeren: gyldig post havner i `tilbakemeldinger.json`. Honeypot, for lang tekst og
  gal Origin avvises.
- Fem parallelle innsendinger gir fem poster uten tap (tester 409-retry).
- Siden testes i nettleserpanelet (lokalt og på elvesona.no): innsending, forhåndsutfylling via `?elv=&sone=`
  og feilvisning når Workeren er nede.
- `python scripts/valider.py` på hver endret HTML-fil før commit.
- Adminpanelet: listen vises, og statusendring blir lagret.
- Kontroller at det ikke finnes noen token i noen committet fil (`git grep -i github_pat`).
