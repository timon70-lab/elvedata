# Idé: brukereid turlogg og fangstregistrering

Status: kun idé, ingen implementering påbegynt (loggført 2026-09-14).

## Konsept
- Én knapp «Logg tur» trykkes én gang i felt — turen er logget.
- Hentes automatisk: tidspunkt, elv (åpent dashboard), sone (aktiv sone i slider),
  vannføring (NVE-cache), geolokasjon (med tillatelse).
- Etter trykk: kun liten kvittering, ikke skjema. Kvitteringen lenker til å legge til fangst/notater senere
  («i godstolen hjemme foran peisen»).

## Brukertyper
- Felt-brukeren: ett trykk — bidrar med innsatsdata (dato, sone, vannføring, tidspunkt).
- Sofa-brukeren: legger senere til fangst, vekt, redskap, bilde — full fangstdata.

## Datalagring — brukereid kapsel
- Lagres lokalt (localStorage/IndexedDB), ikke på server. Elvesona er aldri databehandler.
- Første gang: bekreftelsesdialog som forklarer lokal lagring.
- Kapsel: id, tidspunkt, elv, sone, vannføring, fangster[], notater, eksportert(ja/nei).
  Fangster ligger inne i turen — koblingen innsats/utbytte er alltid intakt.
- «Eksporter mine turer» → JSON eller CSV. JSON-strukturen skal være portabel fra start.

## Deling og innsatsdata
- Frivillig, eksplisitt opt-in: «Bidra til innsatsstatistikk (anonymt)». Kun da sendes noe til backend.
- Mål: fangstrate = laks per stang-time per sone — nevneren som mangler i dagens scoring.
- Kobler til backlog-punkt (c) innsats- og kvotejustering.

## Begrensning
- localStorage er bundet til én nettleser/enhet; tur logget på telefon kan ikke redigeres på PC
  uten eksport/import eller frivillig skysynk. Ikke et problem i v1.
