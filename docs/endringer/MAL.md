# Mal for endringsnotat

Ett notat per leveranserunde, altså per elv per versjonsbump. Notatet skrives i steg 5 av
`/runde`, før commit, og committes sammen med selve endringen.

**Filnavn:** `{yyyy-mm-dd}-{elv}-v{major}.{minor}.md` — f.eks. `2026-09-20-sygna-v1.044.md`.
Dato først gjør at mappa sorterer kronologisk; elv og versjon gjør notatet entydig.

Denne fila (`MAL.md`) er malen selv og er ikke et endringsnotat.

Kopier alt under streken og fyll ut. Slett punkter som ikke er relevante — et tomt avsnitt
er verre enn ingen avsnitt.

---

# {Elv} v{major}.{minor} — {kort beskrivelse}

**Dato:** {yyyy-mm-dd}
**Fil:** `{elv}/index.html`
**Forrige versjon:** v{major}.{minor-1}

## Hva ble endret

- {Endring 1 — hva som faktisk står annerledes i fila, ikke hva som var intensjonen.}
- {Endring 2.}

Andre filer i samme commit: {`data/...`, `scripts/...` — eller «ingen».}

## Hvorfor

{Hva utløste runden: rapportert irritasjon i bruk, feil i data, punkt fra backlogen,
eller ønske fra Per Lasse. Én til tre setninger. Dette er den delen som er verdt noe om
seks måneder — hva som ble gjort kan leses ut av diffen, hvorfor kan det ikke.}

## Validering

- `python scripts/valider.py {elv}/index.html` — {OK / hva som måtte fikses underveis}
- Kart-UX A–C (`docs/kart-ux-standarder.md`) — {bekreftet på plass / berørt av denne runden: ...}
- {Manuell test som ikke dekkes av valideringen: hvilke slidere/soner/paneler ble prøvd.}

## Oppfølging

- {Ny teknisk gjeld denne runden innfører — legg samme punkt i `docs/status-og-backlog.md`.}
- {Gjeld eller backlog-punkt runden lukker — fjern det fra `status-og-backlog.md`.}
- {Endring som bør rulles ut på de øvrige elvene senere. Testes på Sygna først, jf.
  `docs/utviklerkonvensjoner.md`.}
