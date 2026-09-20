---
description: Start bygging av dashboard for en ny elv (navn + regulert/uregulert)
argument-hint: <navn> <regulert|uregulert>
---
Ny elv: $ARGUMENTS

1. Les `docs/ny-elv-sjekkliste.md`, `docs/kart-ux-standarder.md` og `docs/scoring-og-kalibrering.md`.
2. Gå gjennom del 1 av sjekklisten og list opp hva som mangler av data. Spør Per Lasse om det som
   mangler før du bygger noe. Ikke gjett stasjon, riverId, sesongdatoer eller kvoter.
3. Velg metode ut fra regulert/uregulert (del 2).
4. Bygg dashboardet med utgangspunkt i nærmeste eksisterende elv av samme type (les filen fra repoet).
   Versjon v0.001. Ikke rør oversiktskartet (`index.html`).
5. Kjør `python scripts/valider.py` på den nye filen, skriv endringsnotat i `docs/endringer/`,
   og vis diff før commit.
