# Rydding etter kartoppgraderingen

**Dato:** 2026-11-21
**Filer:** `mandalselva2/`, `audna2/`, `tovdalselva2/`, `sygna2/` og `lygna2/` (slettet),
`sitemap.xml`, `data/videoer_lygna.json` (ny), `CLAUDE.md`, `docs/status-og-backlog.md` og
`docs/ny-elv-sjekkliste.md`

## Hva ble endret

- **De fem testklonene er slettet:** mandalselva2, audna2, tovdalselva2, sygna2 og lygna2.
  - Alle fem er live som `{elv}/index.html`, og ingen sider lenket til dem.
  - De ligger fortsatt i git-historikken.
  - `otra2` står igjen.
- **`sitemap.xml`:** Tovdalselva manglet og er lagt til. `lastmod` er satt til 2026-11-21 for de
  seks elvesidene.
- **`data/videoer_lygna.json` (`[]`):** Lygna har ingen video, og kartet fikk 404 på fila ved
  hver lasting.
- **`robots.txt` er uendret:** klonene som manglet der, er slettet.
- **`CLAUDE.md`:**
  - Esri-unntaket lister bare de seks elvene og `otra2`, pluss en testklone mens den finnes.
  - De fem kloneavsnittene er erstattet av ett avsnitt om det nye kartet med særtrekkene per
    elv, og en oppskrift for å lage en ny testklone.
- **`docs/status-og-backlog.md`:** versjonene er oppdatert, det nye kartet står under aktive
  funksjoner, og backloggen viser hva som gjenstår.
  - Gjenstår: grensesjekk, desinfeksjonsposter, parkering og kortsalg for de fem andre elvene,
    og redigering av steder i admin.
- **`docs/ny-elv-sjekkliste.md`:** nytt punkt 5b om det nye kartet. Det dekker malfil,
  sonepolygoner, datafiler, Esri-nøkkel, vilkårslenke, testklone, sitemap og test.

## Hvorfor

Per Lasse: «slett de 5 klonene + punkt 1-5». Punktene kom fra en gjennomgang av hva som
gjensto etter kartoppgraderingene.

## Validering

- I nettleseren lastes Lygna med 19 polygoner, og alle datafiler svarer 200, også
  `videoer_lygna.json`.
- `/audna2/` svarer 404.
- `sitemap.xml` er gyldig XML med alle seks elvene.

## Kjente mangler / oppfølging

- Det er ikke målt om det dukker opp tomme fliser ved panorering og zoom i de fem siste kartene.
- Data fra Per Lasse: sonegrenser, desinfeksjonsposter, parkering, kortsalg og strekninger med
  fiske fra én side.
