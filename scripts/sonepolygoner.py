#!/usr/bin/env python3
"""
sonepolygoner.py — lager sonepolygoner langs elveflaten.

Leser vannflaten og midtlinja fra OpenStreetMap (data/raw/osm_<elv>.json),
start/slutt-punktene fra ZONE_COORDS i <elv>/index.html og oppsettet i
scripts/sonepolygoner_oppsett.json, og skriver data/soner_<elv>.geojson.
Dashbordet henter fila i runtime, så HTML-en blir ikke større.

Slik regnes sonene ut:
  * Korridoren = vannflaten + bredde_land meter inn på land.
  * Hver sonegrense er et kutt vinkelrett på midtlinja der sonepunktet
    treffer, ikke en rett strek mellom to punkter. Sonene følger svingene.
  * En hovedsone går fra sin start til neste hovedsones start; den øverste
    går til sin egen slutt. Ingen hull eller overlapp mellom hovedsoner.
  * egne_grenser = true i oppsettet (Mandalselva): hver sone går fra sin egen
    start til sin egen slutt. Strekninger uten sone blir stående som hull.
  * kutt_i_vann = true: kuttene måles fra bredd til bredd i vannflaten og
    forlenges inn på land, så de ikke krysser et nes og treffer elva igjen.
  * flate = {vann, linjer, kutt} for en sone: sonen lages fra egne OSM-objekter
    i stedet for midtlinja (Mandalselva Sone 4 over demningen, der midtlinja
    mangler gjennom magasinet). vann = relasjoner, linjer = elveveier som fyller
    hull mellom vannflatene, kutt = [{vei, punkt}] der punkt er [lat, lon],
    "start" eller "slutt". Sonen er biten som henger sammen med startpunktet.
  * En delsone (forelder satt) går fra sin egen start til sin egen slutt, og
    klippes ut av hovedsonen: den er en egen sone med eget kort.
    behold_hel = true på hovedsonen lar den beholde hele strekningen, med
    delsonene tegnet oppå (Audna: gamle Sone5 = dagens 5A + 5B).
  * side = vest/øst deler strekningen langs midtlinja.
  * kun_side = liste av {side, fra, til}: på delstrekningen fra–til hører bare
    den ene bredden til sonen (fiske fra én side). fra/til er [lat, lon] eller
    "start"/"slutt" for sonens egne grenser.
  * utelat_øy_med_kanal = OSM-id til en vei i øyas ring. Øya, sidekanalen
    bak den (sett fra midtlinja) og landstripa langs kanalen tas ut av sonene.
    Kanalåpningene lukkes med korteste linje fra øyspissene til bredden.

Bruk:
    python scripts/sonepolygoner.py otra           # lag polygonene
    python scripts/sonepolygoner.py otra --hent    # hent OSM på nytt først
    python scripts/sonepolygoner.py otra --ut soner_otra2.geojson   # annet filnavn i data/

Data fra OpenStreetMap er under ODbL (© OpenStreetMap contributors).
"""

import json, math, os, sys, time, urllib.parse, urllib.request

from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon, mapping
from shapely.ops import linemerge, polygonize, split, substring, unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from beregn_km import ROOT, les_zone_coords, projeksjon

OPPSETT = os.path.join(ROOT, 'scripts', 'sonepolygoner_oppsett.json')
OVERPASS = 'https://overpass-api.de/api/interpreter'
BRUKERAGENT = 'elvesona.no sonekart (ikke-kommersiell, kontakt via elvesona.no)'

TANGENT_M = 60        # tangenten ved et kutt glattes over ± denne lengden
FORENKLE_M = 3        # Douglas-Peucker-toleranse før lagring
DESIMALER = 5         # ~1 m

# Settes av behandle() når oppsettet har kutt_i_vann = true: (vannflate med øyene
# fylt inn, forlengelse inn på land i meter). Se kutt().
KUTT_I_VANN = None


# ---------------------------------------------------------------- OSM

def hent_osm(elv, oppsett):
    o = oppsett['osm']
    veier, rel = list(o['midtlinje']), list(o['vann'])
    for s in oppsett.get('soner', {}).values():
        fl = s.get('flate')
        if fl:
            veier += fl.get('linjer', []) + [k['vei'] for k in fl.get('kutt', [])]
            rel += fl.get('vann', [])
    q = '[out:json][timeout:120];(way(id:%s);relation(id:%s););out geom;' % (
        ','.join(map(str, sorted(set(veier)))), ','.join(map(str, sorted(set(rel)))))
    data = urllib.parse.urlencode({'data': q}).encode()
    for forsok in range(5):
        try:
            req = urllib.request.Request(OVERPASS, data=data, headers={'User-Agent': BRUKERAGENT})
            with urllib.request.urlopen(req, timeout=180) as r:
                svar = json.loads(r.read().decode('utf-8'))
            break
        except Exception as e:
            print('Overpass feilet (%s), prøver igjen ...' % e)
            time.sleep(20 * (forsok + 1))
    else:
        sys.exit('Overpass svarte ikke. Prøv igjen senere.')
    sti = os.path.join(ROOT, 'data', 'raw', 'osm_%s.json' % elv)
    with open(sti, 'w', encoding='utf-8') as fh:
        json.dump(svar, fh, ensure_ascii=False, separators=(',', ':'))
    print('Lagret', os.path.relpath(sti, ROOT))


def les_osm(elv, oppsett, xy):
    sti = os.path.join(ROOT, 'data', 'raw', 'osm_%s.json' % elv)
    if not os.path.exists(sti):
        sys.exit('Mangler %s - kjør med --hent først.' % os.path.relpath(sti, ROOT))
    with open(sti, encoding='utf-8') as fh:
        elementer = json.load(fh)['elements']

    def linje(geom):
        return LineString([xy(p['lon'], p['lat']) for p in geom])

    # Midtlinja: veiene i oppsettet, satt sammen. OSM tegner waterway=river
    # i strømretningen; vi snur den så målet går fra munningen og oppover.
    veier = [linje(e['geometry']) for e in elementer
             if e['type'] == 'way' and e['id'] in oppsett['osm']['midtlinje']]
    midt = linemerge(veier)
    if midt.geom_type != 'LineString':
        sys.exit('Midtlinja henger ikke sammen (%d deler).' % len(midt.geoms))
    midt = LineString(list(midt.coords)[::-1])

    # Vannflaten: ytre ringer minus indre (øyer).
    ytre, indre, indre_id = [], [], []
    for e in elementer:
        if e['type'] != 'relation' or e['id'] not in oppsett['osm']['vann']:
            continue
        for m in e['members']:
            if m['type'] == 'way' and 'geometry' in m:
                if m['role'] == 'inner':
                    indre.append(linje(m['geometry']))
                    indre_id.append(m['ref'])
                else:
                    ytre.append(linje(m['geometry']))
    vann = unary_union(list(polygonize(ytre)))
    øyer = list(polygonize(indre))
    if øyer:
        vann = vann.difference(unary_union(øyer))
    # Øy per OSM-vei, så oppsettet kan peke på en øy med id-en til en av veiene i ringen.
    øy_for_vei = {}
    for vid, v in zip(indre_id, indre):
        for ø in øyer:
            if v.distance(ø.exterior) < 0.5 and v.within(ø.exterior.buffer(0.5)):
                øy_for_vei[vid] = ø
    return midt, vann, øy_for_vei


# ---------------------------------------------------------------- geometri

def tangent(midt, m):
    a = midt.interpolate(max(0.0, m - TANGENT_M))
    b = midt.interpolate(min(midt.length, m + TANGENT_M))
    dx, dy = b.x - a.x, b.y - a.y
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def kutt(midt, korridor, m, forleng=None):
    """Linjestykket på tvers av korridoren gjennom midtlinja ved mål m.
    Bare delen som henger sammen med midtlinja tas med, så kuttet ikke
    treffer elva igjen i neste sving."""
    p = midt.interpolate(m)
    tx, ty = tangent(midt, m)
    nx, ny = -ty, tx
    L = 2000.0
    lang = LineString([(p.x - nx * L, p.y - ny * L), (p.x + nx * L, p.y + ny * L)])
    if KUTT_I_VANN:
        # Mål kuttet fra bredd til bredd i vannflaten (øyene fylt inn) og forleng det
        # inn på land. I trange svinger smelter landstripene sammen, og da ville et
        # kutt i korridoren fortsette over neset og treffe elva en gang til.
        flate, ekstra = KUTT_I_VANN
        if forleng is not None:
            ekstra = forleng
        biter = lang.intersection(flate)
        biter = list(getattr(biter, 'geoms', [biter]))
        bit = min((b for b in biter if b.length > 0), key=lambda g: g.distance(p))
        (x0, y0), (x1, y1) = bit.coords[0], bit.coords[-1]
        d = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / d, (y1 - y0) / d
        return LineString([(x0 - ux * ekstra, y0 - uy * ekstra), (x1 + ux * ekstra, y1 + uy * ekstra)])
    biter = lang.intersection(korridor)
    biter = list(getattr(biter, 'geoms', [biter]))
    bit = min(biter, key=lambda g: g.distance(p))
    # Strekk litt utover kanten så split() får et rent snitt.
    (x0, y0), (x1, y1) = bit.coords[0], bit.coords[-1]
    d = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    return LineString([(x0 - ux * 5, y0 - uy * 5), (x1 + ux * 5, y1 + uy * 5)])


def kanal_bak_øy(midt, vann, øy):
    """Vannet på baksiden av en øy sett fra midtlinja, dvs. sidekanalen rundt
    øya. Hver kanalåpning lukkes med den korteste linja fra øyas øvre og nedre
    spiss over til bredden på baksiden (bort fra midtlinja)."""
    spisser = sorted(øy.exterior.coords, key=lambda c: midt.project(Point(c)))
    c = øy.centroid
    munninger = []
    for t in (Point(spisser[0]), Point(spisser[-1])):
        q = midt.interpolate(midt.project(t))
        vx, vy = t.x - q.x, t.y - q.y
        bak = [Point(p) for p in vann.exterior.coords
               if (p[0] - q.x) * vx + (p[1] - q.y) * vy > 0]
        b = min(bak, key=lambda p: p.distance(t))
        # Linja må starte inne på øya og slutte inne på land (begge utenfor
        # vannflaten) for at split() skal dele.
        d = t.distance(c) or 1.0
        inne = (t.x + (c.x - t.x) / d * 3, t.y + (c.y - t.y) / d * 3)
        L = b.distance(t) or 1.0
        land = (b.x + (b.x - t.x) / L * 3, b.y + (b.y - t.y) / L * 3)
        munninger.append(LineString([inne, (t.x, t.y), (b.x, b.y), land]))
        print('    kanalåpning lukket med %.0f m linje' % L)
    # Begge linjene på én gang: én linje alene fra øya til land deler ikke flata.
    biter = list(split(vann, MultiLineString(munninger)).geoms)
    hoved = max(biter, key=lambda b: b.area)
    return unary_union([b for b in biter if b is not hoved and b.distance(øy) < 1])


def lag_korridor(midt, vann, bredde, unntak):
    """Vannflaten + bredde meter land. unntak = flater (øy med kanal) som
    verken skal være vann eller land i sonen."""
    if not unntak:
        return vann.buffer(bredde, join_style='round')
    ut = unary_union(unntak)
    hovedvann = vann.difference(ut)
    land = hovedvann.buffer(bredde, join_style='round').difference(ut.buffer(bredde))
    return unary_union([hovedvann, land])


def strekning(midt, korridor, m0, m1):
    """Den delen av korridoren som ligger mellom kuttene ved m0 og m1."""
    if KUTT_I_VANN:
        return strekning_i_vann(midt, korridor, m0, m1)
    biter = [korridor]
    for m in (m0, m1):
        if 0 < m < midt.length:
            k = kutt(midt, korridor, m)
            nye = []
            for b in biter:
                nye.extend(split(b, k).geoms if b.intersects(k) else [b])
            biter = nye
    lo, hi = min(m0, m1), max(m0, m1)
    # En bit hører til strekningen hvis et punkt i den ligger mellom kuttene langs
    # midtlinja, eller hvis mesteparten av midtlinja gjennom biten ligger mellom
    # kuttene. Det siste trengs for uregelmessige biter (øyer, lange kutt), der
    # punktet havner utenfor.
    midtbit = substring(midt, lo, hi)
    grense = min(20.0, (hi - lo) / 4)

    def med(b):
        if lo <= midt.project(b.representative_point()) <= hi:
            return True
        inne = b.intersection(midtbit).length
        return inne > grense and inne > 0.5 * b.intersection(midt).length
    valgt = [b for b in biter if med(b)]
    return unary_union(valgt)


def _mellom_kutt(midt, flate, m0, m1):
    """Bitene av flata mellom kuttene ved m0 og m1 (samme utvalg som strekning())."""
    biter = [flate]
    for m in (m0, m1):
        if 0 < m < midt.length:
            k = kutt(midt, flate, m)
            nye = []
            for b in biter:
                nye.extend(split(b, k).geoms if b.intersects(k) else [b])
            biter = nye
    lo, hi = min(m0, m1), max(m0, m1)
    midtbit = substring(midt, lo, hi)
    grense = min(20.0, (hi - lo) / 4)

    def med(b):
        if lo <= midt.project(b.representative_point()) <= hi:
            return True
        inne = b.intersection(midtbit).length
        return inne > grense and inne > 0.5 * b.intersection(midt).length
    return [b for b in biter if med(b)]


def strekning_i_vann(midt, korridor, m0, m1):
    """Som strekning(), men vannflaten deles først og landstripa legges rundt
    vannbiten etterpå. Da kan ikke landstripa fra en nabostrekning i en trang sving
    henge sammen med sonen."""
    fylt, ekstra = KUTT_I_VANN
    bredde = (ekstra - 5) / 2
    vannbit = unary_union(_mellom_kutt(midt, fylt, m0, m1))
    if vannbit.is_empty:
        return vannbit
    lokal = vannbit.buffer(bredde, join_style='round').intersection(korridor)
    # Klipp bort landstripa som stikker forbi kuttene. Kuttet forlenges godt forbi
    # landstripa: lokal er bare denne vannbiten med strimmel, så det treffer ikke naboer.
    biter = [lokal]
    for m in (m0, m1):
        if 0 < m < midt.length:
            k = kutt(midt, korridor, m, forleng=3 * bredde + 50)
            nye = []
            for b in biter:
                nye.extend(split(b, k).geoms if b.intersects(k) else [b])
            biter = nye
    return unary_union([b for b in biter if b.intersection(vannbit).area > 1.0])


def egen_flate(elv, spek, zc_sone, bredde, xy):
    """Sone laget fra egne OSM-objekter (se «flate» i docstringen øverst)."""
    sti = os.path.join(ROOT, 'data', 'raw', 'osm_%s.json' % elv)
    with open(sti, encoding='utf-8') as fh:
        el = json.load(fh)['elements']
    linje = lambda geom: LineString([xy(p['lon'], p['lat']) for p in geom])
    veier = {e['id']: linje(e['geometry']) for e in el if e['type'] == 'way'}
    flater = []
    for e in el:
        if e['type'] != 'relation' or e['id'] not in spek.get('vann', []):
            continue
        ytre = [linje(m['geometry']) for m in e['members']
                if m['type'] == 'way' and 'geometry' in m and m['role'] != 'inner']
        indre = [linje(m['geometry']) for m in e['members']
                 if m['type'] == 'way' and 'geometry' in m and m['role'] == 'inner']
        f = unary_union(list(polygonize(ytre)))
        if indre:
            f = f.difference(unary_union(list(polygonize(indre))))
        flater.append(f)
    mangler = set(spek.get('vann', [])) - {e['id'] for e in el if e['type'] == 'relation'}
    mangler |= set(spek.get('linjer', [])) - set(veier)
    if mangler:
        sys.exit('Mangler OSM-objekter %s - kjør med --hent.' % sorted(mangler))
    linjer = unary_union([veier[v] for v in spek.get('linjer', [])])
    grunn = unary_union(flater + [linjer.buffer(spek.get('linjebredde', 8) / 2)])
    # Vannet deles først, så landstripa ikke kan henge sammen over et nes eller et
    # samløp. Deretter legges landstripa rundt vannet som ble igjen, og det som
    # stikker forbi kuttene klippes bort med lange kutt.
    snitt_kort, snitt_lang = [], []
    for k in spek.get('kutt', []):
        pk = k['punkt']
        pk = zc_sone['s'] if pk == 'start' else zc_sone['e'] if pk == 'slutt' else pk
        vei = veier[k['vei']]
        m = vei.project(Point(xy(pk[1], pk[0])))
        p = vei.interpolate(m)
        tx, ty = tangent(vei, m)
        nx, ny = -ty, tx
        lang = LineString([(p.x - nx * 2000, p.y - ny * 2000), (p.x + nx * 2000, p.y + ny * 2000)])
        biter = list(getattr(lang.intersection(grunn), 'geoms', [lang.intersection(grunn)]))
        bit = min((b for b in biter if b.length > 0), key=lambda g: g.distance(p))
        (x0, y0), (x1, y1) = bit.coords[0], bit.coords[-1]
        d = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / d, (y1 - y0) / d
        lag = lambda e: LineString([(x0 - ux * e, y0 - uy * e), (x1 + ux * e, y1 + uy * e)])
        snitt_kort.append(lag(3))
        snitt_lang.append(lag(3 * bredde + 50))
        print('    kutt ved vei %s: %.0f m over vannet' % (k['vei'], bit.length))
    start = Point(xy(zc_sone['s'][1], zc_sone['s'][0]))
    deler = [grunn]
    for s in snitt_kort:
        deler = [d for b in deler for d in (split(b, s).geoms if b.intersects(s) else [b])]
    vann = min(deler, key=lambda g: g.distance(start))
    deler = [vann.buffer(bredde, join_style='round')]
    for s in snitt_lang:
        deler = [d for b in deler for d in (split(b, s).geoms if b.intersects(s) else [b])]
    return unary_union([d for d in deler if d.intersection(vann).area > 1.0])


def side(midt, flate, hvilken):
    """vest/øst-halvdelen av flata, delt langs midtlinja (forlenget i endene)."""
    c = list(midt.coords)
    (ax, ay), (bx, by) = c[0], c[1]
    (yx, yy), (zx, zy) = c[-2], c[-1]
    fram = LineString([(ax - (bx - ax) * 50, ay - (by - ay) * 50)] + c +
                      [(zx + (zx - yx) * 50, zy + (zy - yy) * 50)])
    biter = list(split(flate, fram).geoms)

    # Hver bit sammenlignes med nærmeste punkt på midtlinja: vest = venstre side
    # sett oppover elva (midtlinja går fra munningen og oppover). Det virker også
    # der elva renner mot øst eller vest.
    def er_vest(b):
        p = b.representative_point()
        m = midt.project(p)
        q = midt.interpolate(m)
        tx, ty = tangent(midt, m)
        return tx * (p.y - q.y) - ty * (p.x - q.x) > 0
    valgt = [b for b in biter if er_vest(b) == (hvilken == 'vest')]
    return unary_union(valgt)


def som_lonlat(geom, inv):
    geom = geom.simplify(FORENKLE_M, preserve_topology=True)
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    polys = [p for p in polys if p.area > 50]          # dropp smuler < 50 m²

    def ring(r):
        return [[round(v, DESIMALER) for v in inv(x, y)] for x, y in r.coords]

    koord = [[ring(p.exterior)] + [ring(i) for i in p.interiors] for p in polys]
    if len(koord) == 1:
        return {'type': 'Polygon', 'coordinates': koord[0]}
    return {'type': 'MultiPolygon', 'coordinates': koord}


# ---------------------------------------------------------------- kjøring

def behandle(elv, hent=False, ut_fil=None):
    with open(OPPSETT, encoding='utf-8') as fh:
        oppsett = json.load(fh)[elv]
    if hent:
        hent_osm(elv, oppsett)

    zc = les_zone_coords(elv)
    if not zc:
        sys.exit('Fant ikke ZONE_COORDS i %s/index.html' % elv)
    alle = list(zc.values())
    lat0 = sum(z['s'][0] for z in alle) / len(alle)
    lon0 = sum(z['s'][1] for z in alle) / len(alle)
    xy = projeksjon(lat0, lon0)
    k = 111320.0 * math.cos(math.radians(lat0))
    inv = lambda x, y: (lon0 + x / k, lat0 + y / 110540.0)

    midt, vann, øy_for_vei = les_osm(elv, oppsett, xy)
    print('Midtlinje %.2f km, vannflate %.2f km²' % (midt.length / 1000, vann.area / 1e6))
    unntak = []
    for vid in oppsett.get('utelat_øy_med_kanal', []):
        øy = øy_for_vei.get(vid)
        if øy is None:
            sys.exit('Fant ingen øy med OSM-vei %s i vannflaten.' % vid)
        kanal = kanal_bak_øy(midt, vann, øy)
        print('  utelater øy (vei %s, %.0f m²) og kanal bak den (%.0f m²)' % (vid, øy.area, kanal.area))
        unntak += [øy, kanal]
    korridor = lag_korridor(midt, vann, oppsett.get('bredde_land', 40), unntak)
    global KUTT_I_VANN
    KUTT_I_VANN = None
    if oppsett.get('kutt_i_vann'):
        fylt = unary_union([Polygon(p.exterior) for p in getattr(vann, 'geoms', [vann])])
        KUTT_I_VANN = (fylt, 2 * oppsett.get('bredde_land', 40) + 5)

    spesial = oppsett.get('soner', {})

    def mål(pkt):
        p = Point(xy(pkt[1], pkt[0]))
        return midt.project(p), midt.distance(p)

    # Mål og avstand til midtlinja for hvert sonepunkt - til kontroll.
    soner = []
    for navn, z in zc.items():
        s = spesial.get(navn, {})
        ms, ds = mål(z['s'])
        me, de = mål(z['e'])
        soner.append(dict(navn=navn, ms=ms, me=me, forelder=s.get('forelder'), side=s.get('side'),
                          kun_side=s.get('kun_side', []), flate=s.get('flate'), zc=z))
        print('  %-20s %6.0f–%6.0f m  (punktene %3.0f / %3.0f m fra midtlinja)' % (navn, ms, me, ds, de))
    # Soner uten egne koordinater, som deler strekning med en annen.
    for navn, s in spesial.items():
        if 'som' in s and navn not in zc:
            mal = next(z for z in soner if z['navn'] == s['som'])
            soner.append(dict(mal, navn=navn, side=s.get('side'), kun_side=s.get('kun_side', [])))

    hoved = sorted([z for z in soner if not z['forelder']], key=lambda z: z['ms'])
    starter = sorted({round(z['ms'], 1) for z in hoved})
    flater = []
    for z in soner:
        if z.get('flate'):
            flate = egen_flate(elv, z['flate'], z['zc'], oppsett.get('bredde_land', 40), xy)
            print('  %-20s egen flate: %.0f m²' % (z['navn'], flate.area))
            flater.append((z, flate))
            continue
        if z['forelder'] or oppsett.get('egne_grenser'):
            m0, m1 = sorted((z['ms'], z['me']))
        else:
            m0 = z['ms']
            høyere = [m for m in starter if m > round(m0, 1)]
            m1 = høyere[0] if høyere else z['me']
            if m0 == min(starter):
                m0 = min(m0, 0.0)                         # nederste sone til munningen
        flate = strekning(midt, korridor, m0, m1)
        if flate.is_empty:
            print('ADVARSEL: %s ble tom' % z['navn'])
            continue
        if z['side']:
            flate = side(midt, flate, z['side'])
        # Hull er midten av øyer som landstripa ikke rakk inn til - øya hører til sonen.
        flate = unary_union([Polygon(p.exterior) for p in getattr(flate, 'geoms', [flate])])
        # Delstrekninger der det bare fiskes fra én side: ta bort den andre bredden.
        for regel in z.get('kun_side', []):
            def grense(v, standard):
                if v in (None, 'start', 'slutt'):
                    return standard
                m, d = mål(v)
                print('    %s: kun %s, grensepunkt %.0f m fra midtlinja' % (z['navn'], regel['side'], d))
                return m
            ma = grense(regel.get('fra', 'start'), m0)
            mb = grense(regel.get('til', 'slutt'), m1)
            # Klipp fra hele korridoren (et kutt akkurat i sonegrensa treffer ikke sonens egen flate).
            bit = strekning(midt, korridor, ma, mb).intersection(flate)
            feil_side = side(midt, bit, 'vest' if regel['side'] == 'øst' else 'øst')
            før = flate.area
            flate = flate.difference(feil_side.buffer(0.5))
            print('    %s: kun %s-siden på %.0f–%.0f m (%.0f m lang), fjernet %.0f m²'
                  % (z['navn'], regel['side'], min(ma, mb), max(ma, mb), abs(mb - ma), før - flate.area))
        if flate.is_empty:
            print('ADVARSEL: %s ble tom' % z['navn'])
            continue
        flater.append((z, flate))

    # Egne grenser: naboer kan overlappe litt der kuttene ikke er helt parallelle.
    # Den minste sonen beholder overlappen; den trekkes fra de større.
    if oppsett.get('egne_grenser'):
        tatt, ryddet = None, {}
        for z, flate in sorted(flater, key=lambda zf: zf[1].area):
            if tatt is not None and flate.intersects(tatt):
                før = flate.area
                flate = flate.difference(tatt.buffer(0.01))
                if før - flate.area > 50:
                    print('  %-20s overlapp med nabo fjernet: %.0f m²' % (z['navn'], før - flate.area))
            ryddet[z['navn']] = flate
            tatt = flate if tatt is None else unary_union([tatt, flate])
        flater = [(z, ryddet[z['navn']]) for z, _ in flater]

    # Delsonene er egne soner med eget kort: klipp dem ut av hovedsonen (forelderen),
    # så hovedsonen bare dekker vann som faktisk hører til den.
    features = []
    for z, flate in flater:
        if not z['forelder'] and not spesial.get(z['navn'], {}).get('behold_hel'):
            barn = [f for b, f in flater if b['forelder'] == z['navn']]
            if barn:
                før = flate.area
                flate = flate.difference(unary_union(barn).buffer(0.01))
                print('  %-20s delsoner klippet ut: %.0f m² fjernet' % (z['navn'], før - flate.area))
        props = {'sone': z['navn'], 'slag': 'del' if z['forelder'] else 'hoved'}
        if z['forelder']:
            props['forelder'] = z['forelder']
        features.append({
            'type': 'Feature',
            'properties': props,
            'geometry': som_lonlat(flate, inv),
        })
    # Hovedsoner først, så delsonene tegnes oppå.
    features.sort(key=lambda f: f['properties']['slag'] != 'hoved')

    ut = {
        'type': 'FeatureCollection',
        'kilde': 'Vannflate og midtlinje: © OpenStreetMap contributors (ODbL). '
                 'Generert av scripts/sonepolygoner.py',
        'features': features,
    }
    sti = os.path.join(ROOT, 'data', ut_fil or 'soner_%s.geojson' % elv)
    with open(sti, 'w', encoding='utf-8') as fh:
        json.dump(ut, fh, ensure_ascii=False, separators=(',', ':'))
    print('Skrev %s (%d soner, %.1f kB)' % (os.path.relpath(sti, ROOT), len(features),
                                           os.path.getsize(sti) / 1024))


def main():
    argv = sys.argv[1:]
    ut_fil = None
    if '--ut' in argv:
        i = argv.index('--ut')
        ut_fil = argv[i + 1]
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    for elv in args:
        behandle(elv, hent='--hent' in argv, ut_fil=ut_fil)


if __name__ == '__main__':
    main()
