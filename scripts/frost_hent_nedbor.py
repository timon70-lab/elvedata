#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Henter observert dognnedbor 2016-2025 for de fire uregulerte elvene.

Kjores manuelt (workflow_dispatch). Skriver en CSV per elv til
data/logg/nedbor_obs_<elv>.csv.

Bakgrunn: dette er fasiten kalibreringen mangler. Loggen fra nve_cache
lagrer bare hva som ble VARSLET; her henter vi hva som faktisk falt, ti
sesonger bakover, slik at sammenhengen nedbor -> vannforingsrespons kan
regnes ut med en gang framfor a vente pa nye hendelser.

Metode:
  * Element sum(precipitation_amount P1D), timeOffset PT6H.
    Dognet lopper fra 06 UTC dagen for til 06 UTC pa datoen. Vannforingen
    MA aggregeres til samme vindu nar seriene kobles - ikke til midnatt.
  * Primaerstasjon brukes nar den har godkjent verdi. Reservestasjon fyller
    hullene. Kolonnen 'kilde' sier hvilken som ble brukt, slik at et hull
    fylt av en stasjon 25 km unna kan vektes ned eller lukes ut senere.
  * Kvalitetskode 0-2 godtas. Hoyere koder er mistenkelige, korrigerte
    eller forkastede verdier og slippes ikke gjennom.
  * Hele sesonger som er ubrukelige er svartelistet under FORKAST.

Krever FROST_CLIENT_ID (og eventuelt FROST_CLIENT_SECRET).
Bruker kun standardbiblioteket.
"""
import base64
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://frost.met.no'
BRUKERAGENT = 'elvesona.no nedboruthenting (github.com/timon70-lab/elvedata)'
AUTH_HEADER = None
VALGT = None

ELEMENT = 'sum(precipitation_amount P1D)'
TIDSOFFSET = 'PT6H'
GODKJENT = {'0', '1', '2'}

AAR = list(range(2016, 2026))
SESONG_FRA = (6, 1)
SESONG_TIL = (8, 31)          # inklusiv; sluttdato i APIet er eksklusiv

# (primaer, reserve). Rekkefolgen er valgt ut fra dekningsrapporten.
ELVER = {
    'audna':       [('SN41175', 'Laudal - Kleiven', 2.4),
                    ('SN41860', 'Kvineshei - Sorhelle', 24.6)],
    'lygna':       [('SN41480', 'Aseral - Kyrkjebygda', 19.4),
                    ('SN42520', 'Risnes i Fjotland', 25.1)],
    'sygna':       [('SN39150', 'Kristiansand - Somskleiva', 12.7),
                    ('SN39040', 'Kjevik', 15.0)],
    'tovdalselva': [('SN38730', 'Hynnekleiv', 0.2),
                    ('SN38600', 'Mykland', 8.3)],
}

# Sesonger som ikke skal brukes fra en gitt stasjon, uansett kvalitetskode.
# Kjevik 2017 hadde 31 dogn og 3 % godkjent - apenbart instrumentfeil.
FORKAST = {('SN39040', 2017)}

VARIANTER = [
    ('med timeoffsets og fields', dict(timeoffsets=True,  fields=True)),
    ('uten fields',               dict(timeoffsets=True,  fields=False)),
    ('uten timeoffsets',          dict(timeoffsets=False, fields=True)),
    ('bare det nodvendige',       dict(timeoffsets=False, fields=False)),
]


# ---------------------------------------------------------------- auth
def _basic(bruker, passord):
    return 'Basic ' + base64.b64encode((bruker + ':' + passord).encode()).decode()


def _oauth_token(cid, secret):
    data = urllib.parse.urlencode({
        'client_id': cid, 'client_secret': secret,
        'grant_type': 'client_credentials'}).encode()
    req = urllib.request.Request(BASE + '/auth/accessToken', data=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': BRUKERAGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))['access_token']


def _prov(header):
    url = BASE + '/sources/v0.jsonld?' + urllib.parse.urlencode({'ids': 'SN18700'})
    req = urllib.request.Request(url, headers={'Authorization': header,
                                               'User-Agent': BRUKERAGENT})
    try:
        with urllib.request.urlopen(req, timeout=30):
            return True
    except urllib.error.HTTPError as e:
        return e.code not in (401, 403)


def finn_auth():
    global AUTH_HEADER
    cid = os.environ.get('FROST_CLIENT_ID', '').strip()
    secret = os.environ.get('FROST_CLIENT_SECRET', '').strip()
    if not cid:
        print('FEIL: FROST_CLIENT_ID er ikke satt.', file=sys.stderr)
        sys.exit(1)
    print('FROST_CLIENT_ID: %d tegn, starter "%s"' % (len(cid), cid[:4]))
    forsok = [('klient-ID, tomt passord', lambda: _basic(cid, ''))]
    if secret:
        forsok.append(('klient-ID + hemmelighet', lambda: _basic(cid, secret)))
        forsok.append(('OAuth2 client_credentials', lambda: 'Bearer ' + _oauth_token(cid, secret)))
    for navn, lag in forsok:
        try:
            h = lag()
        except Exception as e:
            print('  %-26s feilet: %s' % (navn, e))
            continue
        if _prov(h):
            print('  %-26s VIRKER' % navn)
            AUTH_HEADER = h
            return
        print('  %-26s avvist' % navn)
    print('\nFEIL: ingen av metodene ga tilgang.', file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- kall
def _params(stasjon, fra, til, spec):
    p = {'sources': stasjon, 'elements': ELEMENT, 'referencetime': fra + '/' + til}
    if spec['timeoffsets']:
        p['timeoffsets'] = TIDSOFFSET
    if spec['fields']:
        p['fields'] = 'referenceTime,observations'
    return p


def _kall(params):
    url = BASE + '/observations/v0.jsonld?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization': AUTH_HEADER,
                                               'User-Agent': BRUKERAGENT})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode('utf-8')), ''
    except urllib.error.HTTPError as e:
        kropp = e.read().decode('utf-8', 'replace')
        try:
            grunn = json.loads(kropp).get('error', {}).get('reason', '')
        except Exception:
            grunn = kropp[:200].replace('\n', ' ')
        return None, 'HTTP %d: %s' % (e.code, grunn)
    except Exception as e:
        return None, str(e)


def finn_variant():
    global VALGT
    print('Tester sporringsvarianter mot SN38730 (2024):')
    for navn, spec in VARIANTER:
        d, feil = _kall(_params('SN38730', '2024-06-01', '2024-09-01', spec))
        if d is not None and d.get('data'):
            print('  %-28s VIRKER' % navn)
            VALGT = spec
            return
        print('  %-28s %s' % (navn, feil or 'tomt svar'))
    print('\nFEIL: ingen sporringsvariant ga data.', file=sys.stderr)
    sys.exit(1)


def hent_sesong(stasjon, aar):
    """{dato: mm} for godkjente verdier. None ved feil, {} ved ingen data."""
    if (stasjon, aar) in FORKAST:
        return {}
    fra = '%d-%02d-%02d' % (aar, SESONG_FRA[0], SESONG_FRA[1])
    # Sluttdato i APIet er EKSKLUSIV - legg til en dag for a faa med 31. august
    slutt = datetime.date(aar, SESONG_TIL[0], SESONG_TIL[1]) + datetime.timedelta(days=1)
    d, feil = _kall(_params(stasjon, fra, slutt.isoformat(), VALGT))
    if d is None:
        if feil.startswith('HTTP 404'):
            return {}
        print('    %s %d: %s' % (stasjon, aar, feil), file=sys.stderr)
        return None
    ut = {}
    for rad in d.get('data', []):
        dato = rad.get('referenceTime', '')[:10]
        for o in rad.get('observations', []):
            v, q = o.get('value'), str(o.get('qualityCode', ''))
            if v is not None and q in GODKJENT:
                ut[dato] = float(v)
    return ut


def main():
    finn_auth()
    finn_variant()
    os.makedirs('data/logg', exist_ok=True)
    sammendrag = []

    for elv, stasjoner in ELVER.items():
        (p_id, p_navn, p_km), (r_id, r_navn, r_km) = stasjoner
        print('\n=== %s  primaer %s, reserve %s' % (elv, p_id, r_id), flush=True)
        rader = []
        n_p = n_r = n_mangler = 0

        for aar in AAR:
            prim = hent_sesong(p_id, aar)
            time.sleep(0.4)
            res = hent_sesong(r_id, aar)
            time.sleep(0.4)
            if prim is None:
                prim = {}
            if res is None:
                res = {}

            dag = datetime.date(aar, *SESONG_FRA)
            sist = datetime.date(aar, *SESONG_TIL)
            while dag <= sist:
                d = dag.isoformat()
                if d in prim:
                    rader.append([d, '%.1f' % prim[d], p_id])
                    n_p += 1
                elif d in res:
                    rader.append([d, '%.1f' % res[d], r_id])
                    n_r += 1
                else:
                    rader.append([d, '', ''])
                    n_mangler += 1
                dag += datetime.timedelta(days=1)
            print('  %d: primaer %d, reserve %d' % (aar, len(prim), len(res)), flush=True)

        sti = 'data/logg/nedbor_obs_%s.csv' % elv
        with open(sti, 'w', encoding='utf-8') as f:
            f.write('# Observert dognnedbor, %s. Element %s, timeOffset %s.\n'
                    % (elv, ELEMENT, TIDSOFFSET))
            f.write('# Dognet gaar fra 06 UTC dagen for til 06 UTC paa datoen.\n')
            f.write('# Primaer %s (%s, %.1f km), reserve %s (%s, %.1f km).\n'
                    % (p_id, p_navn, p_km, r_id, r_navn, r_km))
            f.write('# Kun kvalitetskode 0-2. Tom mm betyr ingen godkjent maaling.\n')
            f.write('# Kilde: Meteorologisk institutt (CC BY 4.0).\n')
            f.write('dato;mm;kilde\n')
            for r in rader:
                f.write(';'.join(r) + '\n')

        tot = len(rader)
        print('  -> %s: %d dogn, %d fra primaer, %d fra reserve, %d mangler'
              % (sti, tot, n_p, n_r, n_mangler))
        sammendrag.append((elv, tot, n_p, n_r, n_mangler))

    print('\n%-13s %6s %8s %8s %8s %8s' % ('elv', 'dogn', 'primaer', 'reserve', 'mangler', 'dekning'))
    for elv, tot, a, b, m in sammendrag:
        print('%-13s %6d %8d %8d %8d %7d %%' % (elv, tot, a, b, m, round(100 * (tot - m) / tot)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
