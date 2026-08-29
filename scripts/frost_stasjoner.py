#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finner kandidatstasjoner for observert nedbor i Frost, per elv.

Kjores manuelt (workflow_dispatch). Skriver en rapport til
data/logg/frost_stasjoner.md som kan leses direkte i GitHub.

Formalet er a svare pa ett sporsmal for vi bygger uthentingen:
finnes det stasjoner nar nok, med hoy nok opplosning, og med data
langt nok tilbake til at kalibrering mot vannforingsseriene 2016-2025
faktisk lar seg gjore?

Krever miljovariabelen FROST_CLIENT_ID (HTTP Basic, tomt passord).
Bruker kun standardbiblioteket.
"""
import base64
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://frost.met.no'

# Samme punkter som MET-varselet bruker i dag - altsa oppe i nedborfeltet,
# ikke ved fiskestrekningen. Regulerte elver (Mandalselva, Otra) er utelatt:
# der er sammenhengen nedbor -> vannforing brutt av magasinstyring.
ELVER = [
    ('audna',       58.27,   7.40),
    ('lygna',       58.4786, 7.2083),
    ('sygna',       58.1551, 7.8358),
    ('tovdalselva', 58.602,  8.4181),
]

ELEMENTER = [
    'sum(precipitation_amount PT1H)',
    'sum(precipitation_amount P1D)',
]

KANDIDATER = 15          # hvor mange naboer vi ser pa per elv
KREVER_FRA = '2016-01-01'  # ma dekke dette for a vaere brukbar til kalibrering


def hent(sti, params):
    url = BASE + sti + '?' + urllib.parse.urlencode(params)
    cid = os.environ.get('FROST_CLIENT_ID', '').strip()
    if not cid:
        print('FEIL: miljovariabelen FROST_CLIENT_ID er ikke satt.', file=sys.stderr)
        sys.exit(1)
    auth = base64.b64encode((cid + ':').encode()).decode()
    req = urllib.request.Request(url, headers={
        'Authorization': 'Basic ' + auth,
        'User-Agent': 'elvesona.no stasjonsoppslag (github.com/timon70-lab/elvedata)',
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        kropp = e.read().decode('utf-8', 'replace')[:400]
        if e.code in (401, 403):
            print('FEIL: Frost avviste legitimasjonen (%d). Sjekk FROST_CLIENT_ID.' % e.code,
                  file=sys.stderr)
            sys.exit(1)
        if e.code == 404:
            return None          # ingen treff er et gyldig svar
        print('HTTP %d for %s\n%s' % (e.code, sti, kropp), file=sys.stderr)
        return None


def avstand(lat1, lon1, lat2, lon2):
    """Storsirkelavstand i km."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def naboer(lat, lon):
    d = hent('/sources/v0.jsonld', {
        'types': 'SensorSystem',
        'geometry': 'nearest(POINT(%s %s))' % (lon, lat),
        'nearestmaxcount': KANDIDATER,
        'fields': 'id,name,masl,geometry,validFrom,validTo,county',
    })
    return (d or {}).get('data', []) or []


def tidsserier(kilde_ider):
    if not kilde_ider:
        return []
    d = hent('/observations/availableTimeSeries/v0.jsonld', {
        'sources': ','.join(kilde_ider),
        'elements': ','.join(ELEMENTER),
    })
    return (d or {}).get('data', []) or []


def kort(s, n=10):
    return (s or '')[:n]


def dekker_2016(fra):
    return bool(fra) and fra[:10] <= KREVER_FRA


def main():
    linjer = ['# Kandidatstasjoner for observert nedbor (Frost)', '',
              'Automatisk oppslag. Krav for a vaere brukbar til kalibrering: ',
              'nedbor som element, og data fra senest %s.' % KREVER_FRA, '']
    oppsummering = []

    for elv, lat, lon in ELVER:
        print('--- %s' % elv)
        stasjoner = naboer(lat, lon)
        if not stasjoner:
            linjer += ['## %s' % elv.capitalize(), '', 'Ingen stasjoner funnet.', '']
            oppsummering.append((elv, 0, 0))
            continue

        pos = {}
        for s in stasjoner:
            g = s.get('geometry') or {}
            c = g.get('coordinates') or [None, None]
            pos[s['id']] = dict(
                navn=s.get('name', ''),
                masl=s.get('masl'),
                km=avstand(lat, lon, c[1], c[0]) if c[0] is not None else None,
                tilTo=s.get('validTo'),
            )

        serier = tidsserier([s['id'] for s in stasjoner])
        rader = []
        for ts in serier:
            sid = (ts.get('sourceId') or '').split(':')[0]
            p = pos.get(sid)
            if not p:
                continue
            rader.append(dict(
                sid=sid, navn=p['navn'], km=p['km'], masl=p['masl'],
                elem='PT1H' if 'PT1H' in ts.get('elementId', '') else 'P1D',
                fra=kort(ts.get('validFrom')), til=kort(ts.get('validTo')) or 'aktiv',
                offset=ts.get('timeOffset', ''),
            ))

        rader.sort(key=lambda r: (r['km'] if r['km'] is not None else 9e9, r['elem']))
        brukbare = [r for r in rader if dekker_2016(r['fra']) and r['til'] == 'aktiv']
        med_time = [r for r in brukbare if r['elem'] == 'PT1H']
        oppsummering.append((elv, len(brukbare), len(med_time)))

        linjer += ['## %s' % elv.capitalize(),
                   '', 'Punkt: %.4f, %.4f' % (lat, lon), '',
                   '| Stasjon | Navn | km | moh | Opplosning | Fra | Til | Offset | Brukbar |',
                   '|---|---|---|---|---|---|---|---|---|']
        if not rader:
            linjer += ['| _ingen nedbormaling blant de %d naermeste_ | | | | | | | | |' % KANDIDATER]
        for r in rader:
            ok = 'JA' if (dekker_2016(r['fra']) and r['til'] == 'aktiv') else ''
            linjer.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                r['sid'], r['navn'],
                '%.1f' % r['km'] if r['km'] is not None else '?',
                r['masl'] if r['masl'] is not None else '?',
                r['elem'], r['fra'], r['til'], r['offset'], ok))
        linjer.append('')
        print('  %d serier, %d brukbare, %d med timesopplosning'
              % (len(rader), len(brukbare), len(med_time)))

    linjer = linjer[:4] + ['', '## Oppsummering', '',
                           '| Elv | Brukbare serier | Med timesopplosning |', '|---|---|---|'] + \
             ['| %s | %d | %d |' % (e, b, t) for e, b, t in oppsummering] + linjer[4:]

    ut = 'data/logg/frost_stasjoner.md'
    os.makedirs(os.path.dirname(ut), exist_ok=True)
    with open(ut, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linjer) + '\n')
    print('\nSkrev %s' % ut)
    return 0


if __name__ == '__main__':
    sys.exit(main())
