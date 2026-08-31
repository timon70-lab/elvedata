#!/usr/bin/env python3
"""
beregn_km.py — lineaerreferanse for bilde- og videoregistre.

Regner ut hvor langt opp i elva hvert bilde ligger, maalt i meter langs
senterlinja fra munningen, og skriver resultatet som feltet "km" i
data/photos_<elv>.json og data/videoer_<elv>.json.

km brukes KUN til sortering (og eventuelt visning). Markoerposisjoner i
kartet leser fortsatt lat/lon direkte og paavirkes ikke.

Bruk:
    python3 scripts/beregn_km.py              # alle elver med senterlinje
    python3 scripts/beregn_km.py otra         # bare én elv
    python3 scripts/beregn_km.py --dry-run    # regn ut og rapporter, ikke skriv

Elver uten data/senterlinje_<elv>.geojson hoppes over. Poster uten
koordinater faar km = null.
"""

import json, math, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELVER = ['audna', 'lygna', 'mandalselva', 'otra', 'sygna', 'tovdalselva']

# Hvor langt utenfor sonens eget km-intervall et bilde faar projisere seg.
# Fanger opp at sonepunktene er satt paa bredden og at bilder kan vaere tatt
# rett utenfor sonegrensa, uten aa aapne for at et bilde snapper til feil
# arm av en meander flere kilometer unna.
SONE_MARGIN_M = 400


# ---------------------------------------------------------------- geometri

def projeksjon(lat0, lon0):
    """Lokal plan projeksjon. Feilen over 20 km er faa meter - godt nok
    naar resultatet bare skal brukes til rekkefoelge."""
    k = 111320.0 * math.cos(math.radians(lat0))
    return lambda lon, lat: ((lon - lon0) * k, (lat - lat0) * 110540.0)


def kumulativ(pts):
    """Meter fra start til hvert knekkpunkt."""
    cum = [0.0]
    for i in range(len(pts) - 1):
        cum.append(cum[-1] + math.dist(pts[i], pts[i + 1]))
    return cum


def projiser(p, pts, cum, lo=None, hi=None):
    """Nærmeste punkt paa linja. Returnerer (km_i_meter, avstand_i_meter).
    lo/hi avgrenser soeket til et km-intervall (sonebegrensning)."""
    best_d, best_km = float('inf'), 0.0
    for i in range(len(pts) - 1):
        if lo is not None and (cum[i + 1] < lo or cum[i] > hi):
            continue
        a, b = pts[i], pts[i + 1]
        vx, vy = b[0] - a[0], b[1] - a[1]
        L2 = vx * vx + vy * vy
        if L2 == 0:
            continue
        t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2
        t = max(0.0, min(1.0, t))
        qx, qy = a[0] + t * vx, a[1] + t * vy
        d = math.dist(p, (qx, qy))
        if d < best_d:
            best_d, best_km = d, cum[i] + t * math.sqrt(L2)
    if best_d == float('inf'):          # tomt intervall - proev hele linja
        return projiser(p, pts, cum)
    return best_km, best_d


# ---------------------------------------------------------------- innlesing

def les_senterlinje(elv):
    sti = os.path.join(ROOT, 'data', f'senterlinje_{elv}.geojson')
    if not os.path.exists(sti):
        return None
    with open(sti, encoding='utf-8') as fh:
        gj = json.load(fh)
    linjer = [f for f in gj.get('features', [])
              if f.get('geometry', {}).get('type') == 'LineString']
    if len(linjer) != 1:
        raise SystemExit(f'{elv}: forventet én LineString, fant {len(linjer)}')
    return linjer[0]['geometry']['coordinates']


def les_zone_coords(elv):
    """Hentes fra dashbordet slik at kilden alltid er den samme som kartet
    bruker. Feiler den, faller vi tilbake til projeksjon mot hele linja."""
    sti = os.path.join(ROOT, elv, 'index.html')
    if not os.path.exists(sti):
        return {}
    with open(sti, encoding='utf-8') as fh:
        html = fh.read()
    m = re.search(r'^const ZONE_COORDS = (\{.*?\});$', html, re.M)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------- kjoering

def behandle(elv, dry_run=False):
    coords = les_senterlinje(elv)
    if coords is None:
        print(f'{elv}: ingen senterlinje - hoppet over')
        return

    lat0 = sum(c[1] for c in coords) / len(coords)
    lon0 = sum(c[0] for c in coords) / len(coords)
    pr = projeksjon(lat0, lon0)
    pts = [pr(c[0], c[1]) for c in coords]
    cum = kumulativ(pts)
    total = cum[-1]

    print(f'\n=== {elv} ===')
    print(f'senterlinje: {len(coords)} punkter, {total/1000:.2f} km')

    # km-intervall per sone
    zc = les_zone_coords(elv)
    soner = {}
    for navn, c in zc.items():
        try:
            ks, _ = projiser(pr(c['s'][1], c['s'][0]), pts, cum)
            ke, _ = projiser(pr(c['e'][1], c['e'][0]), pts, cum)
        except (KeyError, TypeError, IndexError):
            continue
        soner[navn] = (min(ks, ke) - SONE_MARGIN_M, max(ks, ke) + SONE_MARGIN_M)

    if soner:
        print('sonens km-intervaller (kontroller at de stiger):')
        for navn, (lo, hi) in sorted(soner.items(), key=lambda kv: kv[1][0]):
            print(f'  {navn:24s} {max(lo,0)/1000:6.2f} - {hi/1000:6.2f} km')
    else:
        print('ADVARSEL: fant ingen ZONE_COORDS - projiserer mot hele linja')

    for fil, merkelapp in ((f'data/photos_{elv}.json', 'bilder'),
                           (f'data/videoer_{elv}.json', 'video')):
        sti = os.path.join(ROOT, fil)
        if not os.path.exists(sti):
            print(f'{merkelapp}: {fil} finnes ikke - hoppet over')
            continue
        with open(sti, encoding='utf-8') as fh:
            poster = json.load(fh)

        uten_koord = endret = 0
        avvik = []
        for p in poster:
            lat, lon = p.get('lat'), p.get('lon')
            if lat is None or lon is None:
                if p.get('km') is not None:
                    endret += 1
                p['km'] = None
                uten_koord += 1
                continue
            lo_hi = soner.get(p.get('zone'))
            km_m, d = projiser(pr(lon, lat), pts, cum,
                               *(lo_hi if lo_hi else (None, None)))
            ny = round(km_m / 1000.0, 2)
            if p.get('km') != ny:
                endret += 1
            p['km'] = ny
            avvik.append(d)

        if avvik:
            avvik.sort()
            print(f'{merkelapp}: {len(poster)} poster, {endret} endret, '
                  f'{uten_koord} uten koordinater | avstand til linja: '
                  f'median {avvik[len(avvik)//2]:.0f} m, maks {avvik[-1]:.0f} m')
        if not dry_run:
            with open(sti, 'w', encoding='utf-8') as fh:
                json.dump(poster, fh, ensure_ascii=False, indent=1)
                fh.write('\n')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    dry = '--dry-run' in sys.argv
    for elv in (args or ELVER):
        if elv not in ELVER:
            raise SystemExit(f'ukjent elv: {elv}')
        behandle(elv, dry)
    if dry:
        print('\n(--dry-run: ingen filer skrevet)')


if __name__ == '__main__':
    main()
