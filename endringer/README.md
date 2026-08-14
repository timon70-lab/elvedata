# Endringsdokumenter

Ett dokument per leveranserunde. Skrives mens endringen er fersk, og fungerer som
kilde når den kanoniske dokumentasjonen i `docs/` konsolideres.

## Slik brukes mappa

1. Hver leveranse får en fil: `ÅÅÅÅ-MM-DD-kort-navn.md`, basert på `MAL.md`
2. Filen lastes opp sammen med selve leveransen — ikke etterpå
3. Ved konsolidering leses feltet **Berørte dokumentasjonsavsnitt** i alle
   udokumenterte filer, `docs/` oppdateres, og filene flyttes til `arkiv/`

## Når konsolideres

Konsolidering utløses av én av to hendelser — ikke av «når det passer»:

- **Før en ny elv bygges.** Sjekklista i `docs/ny-elv-sjekkliste.md` må være
  oppdatert før den brukes, ellers gjentas gamle feil.
- **Når det ligger ti udokumenterte filer her.** Over det blir konsolideringen
  stor nok til at den utsettes igjen.

## Status

| Udokumenterte filer | Sist konsolidert |
|---|---|
| 3 | aldri |
