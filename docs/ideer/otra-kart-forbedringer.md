# Idé: forbedringer av kartløsningen for Otra

Status: kun idé, ingen implementering påbegynt (loggført 2026-11-14).

Åtte forslag fra evalueringen av `otra/index.html` v1.054, gjort 2026-11-14 ved kodelesing og test i
nettleser (PC-bredde, fullskjerm og mobilbredde 375 px). Målet Per Lasse satte: den beste
kartløsningen for laksefiske som finnes på internett.

## Det som fungerer godt i dag
- Sonepolygonene følger elva og gjør sonene lesbare fra zoom 14–15.
- Vannføringsfilteret på bilder (💧-pillen) er en reell differensiator.
- Desinfeksjonspostene med «nærmeste post» og kjørerute er nyttige.
- Kart-UX A–C er overholdt.

## Funn
1. Kartet er 480 × 320 px uansett skjermbredde (`max-width: 480px`, `#map { height: 320px }`).
2. Startvisningen er zoom 10: scoremarkørene ligger oppå hverandre og polygonene er noen få piksler
   brede.
3. Eneste kartlag er standard OSM, med `maxZoom: 17`.
4. Stedene sonetekstene nevner (Vedbua, Sødalsstrømmen, Urestrømmen, Gillsteinen, Haus, Glattetre,
   Hengebrua) finnes ikke som punkter i kartet.
5. Kartet vet ikke om en sone er åpen. Sone 5B Øst er `stengt` i `data/sesong.json`, men tegnes som
   en vanlig sone med score. Grunneierdager finnes bare som fritekst i `ZONE_INFO`.
   (`updateMap()` leser ikke `SESONG`.)
6. I fullskjerm gir klikk på en sone ingen soneinfo (`zoneInfoPanel` ligger utenfor `#mapFs`), og
   år, måned, «Kun flue» og topp 3 er borte.
7. Musehjulet zoomer kartet når man ruller forbi det på siden (`scrollWheelZoom` er på).
8. «Hvor er jeg?» er ett engangsoppslag med rød prikk, og sier ikke hvilken sone man står i. Feil
   vises med `alert()`.
9. Scoremarkøren står på sonens startgrense (`L.marker(zc.s)`), og de faste etikettene dekker
   markører og polygon ved zoom 13.
10. Ingen tegnforklaring og ingen delbar lenke til sone eller vannføring.
11. «Veibeskrivelse hit» ruter til sonens grensepunkt ved elva, ikke til parkering.
12. `data/videoer_otra.json` finnes ikke, så hver sidelasting gir en 404.
13. Bildedekningen er skjev: 66 bilder, men 0 i Sone 1, 3C og 5B Øst, og 2 i Sone 2 (5,7 km).

## Forslag, prioritert

### 1. Flyfoto og Kartverket-topo som kartlag (liten innsats, størst effekt)
- Lagvelger med Kart / Topo / Flyfoto, og maks zoom hevet til 18–19.
- Kartverkets topo-lag svarte 2026-11-14 på zoom 13, 17 og 18
  (`https://cache.kartverket.no/v1/wmts/1.0.0/topo/default/webmercator/{z}/{y}/{x}.png`). Det viser
  Haus, Glattetre, Stavsøyra, Høiebekken, stier og høydekurver. Lisensen er oppgitt som CC BY 4.0.
- Flyfoto viser grusører, stryk og hengebrua på Haus.
- Esri World Imagery virket teknisk, men vilkårene må sjekkes.
- Det gamle åpne Norge i bilder-endepunktet (`opencache.statkart.no`) svarte ikke. Ikke avklart om
  dagens tjeneste krever avtale.

### 2. PC-layout med kartet som hovedflate (middels)
- Fra ca. 1000 px bredde: kartet i full høyde på den ene siden, topp 3, slidere og soneinfo i en
  kolonne ved siden av.
- Soneinfo flyttes inn i fullskjerm som sidepanel, sammen med alle sliderne.
- Zoom med Ctrl + hjul, så siden kan rulles forbi kartet.

### 3. «Kan jeg fiske her i dag?» på kartet (middels)
- Soner som er stengt, har grunneierdag eller er utenfor sesong, skraveres grått med årsak i tooltip.
- Grunneierdagene struktureres i `data/sesong.json`, for eksempel `stengteDager` per sone,
  redigerbart i admin.
- Fluesonen i 3A og strekninger med landfiske forbudt tegnes som egne linjer.
- Retter også 5B Øst (funn 5).

### 4. Fiskeplasser, parkering og kortsalg som punkter (middels, mest dataarbeid)
- Ny `data/steder_otra.json` med type, navn, posisjon og kort tekst, vedlikeholdt i admin.
- «Veibeskrivelse» går til nærmeste parkering i stedet for sonegrensa.
- Laxefiskelagets fiskekart (PDF på lakseelver.no) skal ifølge søketreff ha parkering, landfiske
  forbudt og salgssteder i tegnforklaringen. PDF-en er ikke åpnet og må sjekkes.

### 5. Posisjon som sier hvilken sone du står i (liten–middels)
- Løpende blå prikk med nøyaktighetssirkel i stedet for engangsoppslag.
- Punkt-i-polygon mot `data/soner_otra.geojson` gir «Du står i Sone 4A · score 92 · 300 kr ·
  Kjøp kort».
- Varsel når man står i en sone som er stengt i dag (krever forslag 3).

### 6. Lesbar oversikt på lav zoom (liten–middels)
- Under zoom 13: tykk, scorefarget linje per sone langs senterlinja i stedet for polygoner.
- Scoremarkøren flyttes til midten av sonen, og sluttmarkørene fjernes.
- Etiketter bare for valgt sone eller ved hover, pluss en liten tegnforklaring.
- Høyere kart, så startvisningen havner på zoom 11–12.

### 7. Delbare lenker (liten)
- Sone, vannføring, år og måned i URL-en, for eksempel `#sone=4A&vf=100`.
- Nyttig for deling i Facebook-grupper og for synlighet i søk.

### 8. Offline-kart (stor, senere)
- Lavt prioritert for bynære Otra, mer aktuelt for Sygna og Tovdalselva.

## Rekkefølge
Forslag 1 kan leveres som én runde alene. Forslag 2 og 6 hører sammen, og 3 bør komme før 5.

## Forbehold
- Sammenligningen med andre laksekart er ikke systematisk. Søkene bekreftet bare at TroutRoutes har
  adkomstpunkter, vannføringsmålere i kartet og offline-kart, altså det forslag 4 og 8 dekker.
- Fangstloggen for Otra har ingen kolonne for fiskeplass, så fangsttetthet per høl kan ikke lages av
  dagens data.
- Polygonene har 40 m landstripe med vilje (`bredde_land` i `scripts/sonepolygoner_oppsett.json`).
  Den blir synlig mot flyfoto, så grensene bør merkes som veiledende.

## Kilder
- Geonorge: Topografisk norgeskart WMTS/cache —
  https://register.geonorge.no/varsler/navn/ff1e976f-0d4f-4578-bb9b-9603e1514e8c
- data.norge.no: Statens kartverk, datatjeneste —
  https://data.norge.no/en/data-services/e3454491-066a-3276-a482-f63069728021
- data.norge.no: Norge i bilder —
  https://data.norge.no/en/data-services/12bd8b27-ec3a-3f2a-8b80-572539773205
- lakseelver.no: Otra Laxefiskelag Fiskekart 2023 (PDF) —
  https://lakseelver.no/sites/default/files/Otra%20Laxefiskelag%20Fiskekart%202023.pdf
- TroutRoutes i App Store — https://apps.apple.com/us/app/troutroutes-fly-fishing-app/id1423989574
