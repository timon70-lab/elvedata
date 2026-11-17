# Admin — tokenmerket sjekker at GitHub godtar tokenet

**Dato:** 2026-11-17
**Fil:** `admin/index.html` (har ingen versjonslinje)

## Hva ble endret

- «GitHub-token»-merket øverst sjekker nå tokenet mot GitHub (`GET /repos/timon70-lab/elvedata`)
  ved sidelasting og hver gang et token lagres. Merket viser én av disse tilstandene:
  - `…` mens sjekken pågår
  - `✓` når GitHub godtar tokenet
  - `✗ ugyldig` ved 401 (tokenet er utløpt, slettet eller feil)
  - `✗ ingen tilgang` ved andre feilkoder
  - `✗` når det ikke finnes noe token
  - `?` når GitHub ikke svarer
- Når merket er rødt eller gult, åpner et klikk Innstillinger. Forklaringen står i tooltip.

Andre filer i samme commit: ingen.

## Hvorfor

Per Lasse fikk «HTTP 401 ved henting av data/nyheter.json» i Edge, men ikke i Firefox. Hver
nettleser har sitt eget token i localStorage, og Edge hadde et gammelt token. Merket viste likevel
✓, fordi det bare sjekket at et token fantes.

## Validering

- `python scripts/valider.py admin/index.html` — OK.
- Testet i nettleser med ugyldig token (`✗ ugyldig`) og uten token (`✗`). Tilstanden `✓` er ikke
  testet, fordi ingen gyldig token er tilgjengelig for Claude.
- Utløpsdato kan ikke vises: GitHub eksponerer ikke `github-authentication-token-expiration` for
  nettlesere (CORS). `permissions.push` gjelder brukeren og ikke tokenet, så manglende
  skrivetilgang oppdages først ved lagring.
