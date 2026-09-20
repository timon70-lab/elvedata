---
description: Avslutt en leveranserunde for én elv — valider, bump versjon, endringsnotat, commit
argument-hint: <elv>
---
Avslutt leveranserunde for: $ARGUMENTS

1. `git status` og `git diff` — bekreft at alle endringer for denne elva er med, og kun disse.
2. Bump versjonsnummeret i filen +1 minor (major uendret, med mindre dette er go-live Per Lasse har bedt om).
3. Kjør `python scripts/valider.py <fil>` — stopp og rapporter hvis noe feiler.
4. Sjekk at kart-UX-standardene A–C fortsatt er på plass.
5. Skriv endringsnotat i `docs/endringer/` etter `MAL.md`.
6. Commit: `<elv> v<major>.<minor>: <kort beskrivelse>`. Ikke push før Per Lasse sier det.
