# Elvesona — instruksjoner for Claude Code

Elvesona (elvesona.no, repo `timon70-lab/elvedata`) er en gratis, ikke-kommersiell
plattform for laksefiske i Agder. Den scorer soner i seks elver — Audna, Lygna,
Mandalselva, Otra, Sygna og Tovdalselva — ut fra vannføring og fangsthistorikk.
Statisk nettsted på GitHub Pages, datainnhenting via GitHub Actions, adminpanel som
skriver via GitHub Contents API. Eneutvikler og eier: Per Lasse Brønstad.
Per Lasse jobber nesten alltid på PC — ikke anta mobil-kontekst.

Detaljer ligger i egne filer — les dem når oppgaven berører temaet:
- docs/kvoter-2026.md — kvoteregler per elv (sesong 2026)
- docs/scoring-og-kalibrering.md — scoringarkitektur, fiskemelding, flow-binning, foto-GPS
- docs/kart-ux-standarder.md — obligatoriske UX-regler for alle dashboard
- docs/datakilder-og-infrastruktur.md — API-er, stasjoner, riverId, workflows, cron, PAT-er
- docs/status-og-backlog.md — versjoner, teknisk gjeld, backlog, horisont
- docs/ny-elv-sjekkliste.md — sjekkliste for ny elv (brukes av /ny-elv)
- docs/ideer/ — loggførte idéer (brukes av /ide)

## Absolutte regler

1. **Hemmeligheter committes aldri.** NVE-API-nøkkelen finnes kun som GitHub Actions-secret
   og i lokal `.env` (gitignored). Aldri i HTML, JS, markdown eller commit-meldinger.
   Les ikke `.env`-innhold inn i svar.
2. **Fiskernavn vises aldri i dashboard.** Kolonnene `Navn`/`Fisker` i fangstloggene beholdes
   uendret i rådata — ingen data fjernes fra loggene — men de skal aldri embeddes i, eller vises i,
   dashboard, statistikkside eller oversiktskart. Kun `Art == "Laks"` inngår i fangst-pipelines.
3. **Oversiktskartet (`index.html` i roten) endres KUN på eksplisitt forespørsel** — aldri som
   del av en ny-elv-bygging. Ny elv legges ikke til kartet før Per Lasse ber om det.
4. **Ikke bygg fra hukommelse.** Les alltid gjeldende fil i repoet før endring
   (`git pull` ved øktstart).
5. **Regulerte elver (Mandalselva, Otra):** nedbørsbasert fiskemelding gjelder ikke.

## Arbeidsflyt

- Start økt: `git pull`, sjekk `git status`.
- Rediger filene direkte i repoet (ingen `{elv}_dynamisk_oversikt_{n}.html`-kopier lenger —
  git-historikken erstatter nummererte filer).
- Én runde = alle endringer for én elv samlet i én commit (tilsvarer «én fil per elv per runde»).
- Versjonsnummeret inne i filen bumpes +1 minor for hver levert runde — aldri hopp over.
- Kjør `python scripts/valider.py <fil.html>` før hver commit. Den sjekker:
  konfliktmarkører → `node --check` på alle inline-script → div-balanse → HTML-nesting →
  diff av toppnivå `let/const/var/function` mot `HEAD` → jsdom-røyktest.
  Ikke commit hvis den feiler.
- Ved patch via Python: `rep()`-mønsteret — `assert content.count(old) == 1` før `replace()`.
- jsdom: bruk `w.eval('...')` for å nå page-scope-variabler (direkte `w.fn()` feiler).
- Skriv endringsnotat i `docs/endringer/` etter malen `MAL.md`.
- Commit-melding: `{elv} v{major}.{minor}: kort beskrivelse`. Push/PR kun når Per Lasse ber om det.

## Versjonering

- Major 0 = elva er ikke på oversiktskartet. Major 1 = lenket fra oversiktskartet.
- Minor = iterasjonsteller, nullstilles ALDRI (go-live: v0.006 → v1.007, ikke v1.000).

## Implementasjonsdetaljer

- SVG-klassene `.ax`, `.axb`, `.grid` må scopes under `.rd svg` i dashboard
  (de er kun definert på statistikksiden).
- Rekorddag-data genereres fra pickle-filer, embeddes som `const REKORDDAG` over `const BOOM_DAYS`.
- `km_ref.py` håndterer både pipeline-soneformat `[[lat,lon],[lat,lon]]` og dashboard-format
  `{"s":[lat,lon],"e":[lat,lon]}`.
- `beregn_km.py`: SONE_MARGIN_M=400 m; leser ZONE_COORDS fra dashboard-HTML med tolerant parser
  (enkeltfnutt-JS for Audna, standard JSON for Otra).
- Biblioteker: Leaflet.js, Chart.js v4.4.1, jsdom (validering).
- Sesongdatoer leses fra `data/sesong.json` — ikke hardkod i ZONE_INFO.

## Analysekonvensjoner

- Audna/Lygna/Mandalselva: 5 m³/s-intervaller, og vurder alltid dato/måned OG vannføring sammen.
- «Dynamisk oversikt»-malen: banner (live NVE + kvoter), vannføringsslider, dobbel årsslider
  2016–2025, dobbel månedsslider juni–september, valgfri «Kun flue»-pille; score 0–100 per sone,
  topp 3 vises; panelheading = år · måned · vannføringsintervall.

## Triggere

- `ide: …` i en melding → loggfør som idé i `docs/ideer/` (se /ide). Ikke implementer.
- «Ny elv – {navn} – {regulert/uregulert}» → kjør /ny-elv.

## Rådata

- `data/raw/` inneholder komplette, uendrede fangstlogger og vannføringsserier 2016–2026 samt
  `elvesoner.xlsx` (sonekoordinater og priser). Formatene varierer per elv (skilletegn `;`/`,`,
  datoformat `dd.mm.yyyy`/`dd-mm-yy`/`yyyy-mm-dd`/ISO med `Z`) — sjekk header før parsing.

## Repo-kart

<!-- Fylles ut i første Claude Code-økt: hvor ligger hvert dashboard, hvor er versjonsnummeret -->
