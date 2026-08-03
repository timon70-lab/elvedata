# Elvesona

Fiskeintelligens for lakseelver i Agder — vannføring, fangsthistorikk og sonescore.

**Live:** [elvesona.no](https://elvesona.no)
**Facebook:** gruppa *Elvesona* (åpen)

> Tjenesten heter **Elvesona** utad. Repoet, GitHub Pages-stien og filnavn bruker fortsatt
> `elvedata` av historiske grunner — begge navn viser til det samme.

Elvesona kobler historisk fangststatistikk (2016–2025) mot vannføringen på fangstdagen, og
regner ut hvilke soner som historisk har fisket best under forhold som dagens. Fem elver:
**Audna, Lygna, Mandalselva, Otra og Sygna**.

Privat, ikke-kommersielt hobbyprosjekt. Gratis, uten reklame og uten tilknytning til
elveeierlagene.

---

## Dokumentasjon

### For utviklere

| Dokument | Innhold |
|---|---|
| [Arkitektur](docs/arkitektur.md) | Hvordan delene henger sammen, datakilder, byggetid vs. kjøretid |
| [Scoringsmetodikk](docs/scoring.md) | Hvordan sonescoren 0–100 beregnes, og hvorfor |
| [Datamodell](docs/datamodell.md) | Filreferanse, formater og CSV-fallgruver |
| [Automatisering](docs/automatisering.md) | Workflows, cron, tokens og **utløpsdatoer** |
| [Utviklerkonvensjoner](docs/utviklerkonvensjoner.md) | Versjonering, valideringssekvens, UX-standarder |
| [Elvereferanse](docs/elver.md) | Stasjoner, konstanter, sesonger og kvoter per elv |
| [Driftshåndbok](docs/driftshandbok.md) | Feilsøking når noe ikke virker |
| [Ny elv-sjekkliste](docs/ny-elv-sjekkliste.md) | Fremgangsmåte for å legge til en elv |

### For brukere

| Dokument | Innhold |
|---|---|
| [Om tallene](docs/om-tallene.md) | Hva poengsummen betyr — og ikke betyr |
| [Ofte stilte spørsmål](docs/faq.md) | FAQ |
| [Admin-brukerveiledning](docs/admin-brukerveiledning.md) | Nyheter, media, token-oppsett |

---

## Struktur

```
index.html              Oversiktskart med nyhetsbanner
audna/  lygna/  …       Ett dashboard per elv
admin/                  Redigeringspanel (krever personlig token)
staging/                Testversjon av oversiktskartet
data/                   Mellomlagret JSON fra NVE, MET og Inatur
bilder/                 Sonebilder
scripts/                Python-pipelines
.github/workflows/      Planlagte jobber
docs/                   Denne dokumentasjonen
```

---

## Teknologi

Statisk nettside på GitHub Pages — ingen server, ingen database, ingen byggesteg. Hvert
dashboard er én selvstendig HTML-fil med innebygget JavaScript og Leaflet-kart.
Automatisering skjer via GitHub Actions, med cron-job.org som ekstern trigger.

Datakilder: **NVE HydAPI** (vannføring), **Meteorologisk institutt** (nedbørsvarsel),
**Inatur** (fangster), **OpenStreetMap** (kart).

Besøksstatistikk med GoatCounter — cookieløst, uten sporing av enkeltbesøkende.

---

## ⚠️ Viktige datoer

- **11. juli 2027** — cron-tokenet `elvedata-cron` utløper. Etter dette stopper
  automatisk oppdatering av vannføring og fangster, uten synlig feilmelding.
  Se [Automatisering](docs/automatisering.md).

---

© 2026 Per Lasse Brønstad
