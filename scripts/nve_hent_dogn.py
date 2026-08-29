#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Henter timesvannforing 2016-2025 fra NVE og aggregerer til dognverdier.

Kjores manuelt (workflow_dispatch). Skriver en CSV per elv til
data/logg/vannforing_dogn_<elv>.csv.

Hele poenget er dognvinduet. Nedborfilene fra Frost bruker timeOffset PT6H,
altsa 06 UTC til 06 UTC. Vannforingen ma aggregeres til NOYAKTIG samme
vindu, ellers er seriene forskjovet seks timer - og siden det vi skal maale
er responstid fra nedbor til vannforingsokning, ville den forskyvningen
odelagt malingen.

Et dogn merket 2019-07-04 dekker derfor 2019-07-03T06:00Z til
2019-07-04T06:00Z, som er samme konvensjon som nedborfilene.

Perioden er 1. mai til 31. august. Mai er med selv om ingen elv fisker da:
den gir en forhistorie a male feltets fuktighet mot, som er den faktoren vi
mistenker forklarer hvorfor 45 mm ga 0,06 m3/s i Lygna etter torken i 2026.

Timesverdiene lagres ikke - de aggregeres underveis. Kolonnen 'timer' sier
hvor mange av de 24 som faktisk hadde verdi, slik at et tynt dogn kan
vektes ned framfor a se like solid ut som et komplett.

Krever NVE_API_KEY.
Bruker kun standardbiblioteket.
"""
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://hydapi.nve.no/api/v1/Observations'
BRUKERAGENT = 'elvesona.no vannforingsuthenting (github.com/timon70-lab/elvedata)'

PARAMETER = 1001          # vannforing
OPPLOSNING = 60           # minutter, altsa timesverdier
DOGNSTART = 6             # UTC - ma matche timeOffset PT6H i nedborfilene

AAR = list(range(2016, 2026))
FRA = (5, 1)              # 1. mai
TIL = (8, 31)             # 31. august, inklusiv

ELVER = {
    'audna':       ('23.8.0',  'Gaupefossen'),
    'lygna':       ('24.9.0',  'Tingvatn (Lygne)'),
    'sygna':       ('22.22.0', 'Sogne'),
    'tovdalselva': ('20.3.0',  'Flakksvann'),
}


def hent(stasjon, fra, til):
    """Timesobservasjoner i intervallet. Returnerer liste av (datetime, verdi)."""
    nokkel = os.environ.get('NVE_API_KEY', '').strip()
    if not nokkel:
        print('FEIL: NVE_API_KEY er ikke satt.', file=sys.stderr)
        sys.exit(1)
    params = {
        'StationId': stasjon,
        'Parameter': PARAMETER,
        'ResolutionTime': OPPLOSNING,
        'ReferenceTime': fra + '/' + til,
    }
    url = BASE + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'X-API-Key': nokkel, 'Accept': 'application/json', 'User-Agent': BRUKERAGENT})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        kropp = e.read().decode('utf-8', 'replace')[:200].replace('\n', ' ')
        print('    HTTP %d for %s %s: %s' % (e.code, stasjon, fra[:10], kropp), file=sys.stderr)
        return None
    except Exception as e:
        print('    feil for %s %s: %s' % (stasjon, fra[:10], e), file=sys.stderr)
        return None

    ut = []
    for serie in d.get('data', []):
        for o in serie.get('observations', []):
            v = o.get('value')
            if v is None:
                continue
            t = o.get('time', '')
            try:
                ts = datetime.datetime.fromisoformat(t.replace('Z', '+00:00'))
            except ValueError:
                continue
            ut.append((ts.astimezone(datetime.timezone.utc), float(v)))
    return ut


def dognmerke(ts):
    """Hvilken dato hoerer en timesverdi til, gitt 06-06-vinduet?

    Verdier fra 06:00 og utover tilhorer NESTE dato, fordi dognet merket
    med en dato slutter kl. 06 pa den datoen.
    """
    d = ts.date()
    return d + datetime.timedelta(days=1) if ts.hour >= DOGNSTART else d


def main():
    os.makedirs('data/logg', exist_ok=True)
    sammendrag = []

    for elv, (stasjon, navn) in ELVER.items():
        print('\n=== %s  %s (%s)' % (elv, navn, stasjon), flush=True)
        bøtter = {}
        feilaar = []

        for aar in AAR:
            # Start seks timer for perioden, slik at forste dogn blir komplett
            start = datetime.datetime(aar, FRA[0], FRA[1], DOGNSTART,
                                      tzinfo=datetime.timezone.utc) - datetime.timedelta(days=1)
            slutt = datetime.datetime(aar, TIL[0], TIL[1], DOGNSTART,
                                      tzinfo=datetime.timezone.utc) + datetime.timedelta(hours=1)
            obs = hent(stasjon,
                       start.strftime('%Y-%m-%dT%H:00'),
                       slutt.strftime('%Y-%m-%dT%H:00'))
            time.sleep(0.5)
            if obs is None:
                feilaar.append(aar)
                continue
            for ts, v in obs:
                bøtter.setdefault(dognmerke(ts), []).append(v)
            print('  %d: %d timesverdier' % (aar, len(obs)), flush=True)

        rader = []
        n_hele = n_tynne = n_mangler = 0
        for aar in AAR:
            dag = datetime.date(aar, *FRA)
            sist = datetime.date(aar, *TIL)
            while dag <= sist:
                v = bøtter.get(dag)
                if not v:
                    rader.append([dag.isoformat(), '', '', '', '0'])
                    n_mangler += 1
                else:
                    rader.append([dag.isoformat(),
                                  '%.3f' % (sum(v) / len(v)),
                                  '%.3f' % min(v), '%.3f' % max(v), str(len(v))])
                    if len(v) >= 24:
                        n_hele += 1
                    else:
                        n_tynne += 1
                dag += datetime.timedelta(days=1)

        sti = 'data/logg/vannforing_dogn_%s.csv' % elv
        with open(sti, 'w', encoding='utf-8') as f:
            f.write('# Dognverdier for vannforing, %s. Stasjon %s (%s), parameter %d.\n'
                    % (elv, stasjon, navn, PARAMETER))
            f.write('# Aggregert fra timesverdier. Dognet gaar fra %02d UTC dagen for\n'
                    % DOGNSTART)
            f.write('# til %02d UTC paa datoen - samme vindu som nedborfilene (PT6H).\n'
                    % DOGNSTART)
            f.write('# timer = antall timesverdier bak dognet, maks 24.\n')
            f.write('# Kilde: NVE HydAPI.\n')
            f.write('dato;vf_snitt;vf_min;vf_maks;timer\n')
            for r in rader:
                f.write(';'.join(r) + '\n')

        tot = len(rader)
        print('  -> %s: %d dogn, %d komplette, %d delvise, %d mangler'
              % (sti, tot, n_hele, n_tynne, n_mangler))
        if feilaar:
            print('  ADVARSEL: oppslag feilet for %s' % feilaar)
        sammendrag.append((elv, tot, n_hele, n_tynne, n_mangler, feilaar))

    print('\n%-13s %6s %10s %9s %9s' % ('elv', 'dogn', 'komplette', 'delvise', 'mangler'))
    for elv, tot, h, t, m, f in sammendrag:
        print('%-13s %6d %10d %9d %9d%s'
              % (elv, tot, h, t, m, '  FEIL: %s' % f if f else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
