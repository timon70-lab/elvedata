# Oversiktskart v1.057 — 💬-lenka åpner i ny fane

**Dato:** 2026-10-05
**Fil:** `index.html`
**Forrige versjon:** v1.056

## Hva ble endret

- 💬-lenka i headeren har fått tilbake `target="_blank" rel="noopener"`, slik at
  tilbakemeldingssiden åpnes i ny fane.

Andre filer i samme commit: ingen.

## Hvorfor

I v1.056 fjernet jeg `target="_blank"` fordi siden er intern og har sin egen
«← Tilbake til oversiktskartet»-lenke. Per Lasse vil at den skal oppføre seg som
elvesidene, som åpnes i ny fane (`index.html:490`, `:504`, `:594`). Da beholder
man kartet med sonevalg og slidere urørt mens man skriver tilbakemeldingen, noe
som er den egentlige grunnen til at elvesidene gjør det samme.

Elvesidene bruker bare `target="_blank"`. Her er `rel="noopener"` beholdt, slik
lenka hadde det før v1.056. Det endrer ingen oppførsel — moderne nettlesere
setter noopener av seg selv på `target="_blank"` — men er eksplisitt.

## Validering

- `python scripts/valider.py index.html` — OK, alle seks sjekker.
- Kart-UX A–C: ikke berørt, endringen er to attributter i headeren.

## Oppfølging

- Tilbakemeldingssidens «← Tilbake til oversiktskartet»-lenke gir nå et ekstra
  kartvindu når siden er åpnet i ny fane, i stedet for å gå tilbake. Den er
  harmløs, men kunne vært skjult når `window.opener` er satt. Ikke gjort nå.
- `staging/index.html` peker fortsatt til Google Forms (fra v1.056).
