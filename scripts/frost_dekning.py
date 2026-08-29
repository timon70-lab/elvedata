#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maler faktisk datadekning for kandidatstasjonene, sesong for sesong.

Kjores manuelt (workflow_dispatch). Skriver data/logg/frost_dekning.md.

Bakgrunn: validFrom i stasjonsoppslaget sier bare naar serien startet, ikke
hvor komplett den er. En stasjon kan ha data fra 1895 og likevel mangle halve
juli 2019. Dette skriptet henter faktiske observasjoner for sesongene
2016-2025 og teller hvor mange dogn som finnes, og hvor mange som har
godkjent kvalitet.

Element: sum(precipitation_amount P1D) med timeOffset PT6H. Dognet lopper
altsa fra 06 UTC dagen for til 06 UTC samme dag - det ma vannforingen
aggregeres til nar seriene kobles senere.

Krever FROST_CLIENT_ID (og eventuelt FROST_CLIENT_SECRET).
Bruker kun standardbiblioteket.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://frost.met.no'
BRUKERAGENT = 'elvesona.no dekningsanalyse (github.com/timon70-lab/elvedata)'
AUTH_HEADER = None

ELEMENT = 'sum(precipitation_amount P1D)'
TIDSOFFSET = 'PT6H'

# Valgt ut fra stasjonsrapporten. Primaerstasjon forst.
STASJONER = [
    ('audna',       'SN41175', 'Laudal - Kleiven',   2.4),
    ('audna',       'SN41860', 'Kvineshei - Sorhelle', 24.6),
    ('lygna',       'SN41480', 'Aseral - Kyrkjebygda', 19.4),
    ('lygna',       'SN42520', 'Risnes i Fjotland',  25.1),
    ('sygna',       'SN39150', 'Kristiansand - Somskleiva', 12.7),
    ('sygna',       'SN39040', 'Kjevik',             15.0),
    ('tovdalselva', 'SN38730', 'Hynnekleiv',          0.2),
    ('tovdalselva', 'SN38600', 'Mykland',             8.3),
]

AAR = list(range(2016, 2026))
SESONG_FRA, SESONG_TIL = (6, 1), (8, 31)     # videste sesongvindu blant elvene

# Frost sine kvalitetskoder: 0-2 regnes som brukbare, 3-5 er mistenkelige
# eller korrigerte, 6+ er forkastet. Vi teller begge deler hver for seg.
GODKJENT = {'0', '1', '2'}


def _basic(bruker, passord):
    return 'Basic ' + base64.b64encode((bruker + ':' + passord).encode()).decode()


def _oauth_token(cid, secret):
    data = urllib.parse.urlencode({
        'client_id': cid, 'client_secret': secret,
        'grant_type': 'client_credentials',
    }).encode()
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


def hent_aar(stasjon, aar):
    """Returnerer liste av (dato, mm, kvalitetskode) for sesongen."""
    fra = '%d-%02d-%02d' % (aar, SESONG_FRA[0], SESONG_FRA[1])
    til = '%d-%02d-%02d' % (aar, SESONG_TIL[0], SESONG_TIL[1])
    params = {
        'sources': stasjon,
        'elements': ELEMENT,
        'referencetime': fra + '/' + til,
        'timeoffsets': TIDSOFFSET,
        'fields': 'referenceTime,observations',
    }
    url = BASE + '/observations/v0.jsonld?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization': AUTH_HEADER,
                                               'User-Agent': BRUKERAGENT})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []                    # ingen data for perioden
        print('    HTTP %d for %s %d' % (e.code, stasjon, aar), file=sys.stderr)
        return None                      # skiller feil fra tomt
    ut = []
    for rad in d.get('data', []):
        dato = rad.get('referenceTime', '')[:10]
        for o in rad.get('observations', []):
            ut.append((dato, o.get('value'), str(o.get('qualityCode', ''))))
    return ut


def main():
    finn_auth()
    ventet = (30 + 31 + 31)              # 1. juni - 31. august
    linjer = ['# Datadekning for kandidatstasjonene', '',
              'Element: `%s`, timeOffset `%s` (dogn 06-06 UTC).' % (ELEMENT, TIDSOFFSET),
              'Sesongvindu 1. juni - 31. august, altsa %d dogn per aar.' % ventet,
              'Prosent = andel dogn med observasjon. Kvalitet = andel av disse',
              'med godkjent kvalitetskode (0-2).', '']

    oppsummering = []
    for elv, sid, navn, km in STASJONER:
        print('--- %s / %s %s' % (elv, sid, navn), flush=True)
        linjer += ['## %s - %s (%s, %.1f km)' % (elv.capitalize(), navn, sid, km), '',
                   '| Aar | Dogn | Dekning | Godkjent | Sum mm | Feil |',
                   '|---|---|---|---|---|---|']
        tot_d = tot_ok = 0
        feilaar = 0
        for aar in AAR:
            rader = hent_aar(sid, aar)
            time.sleep(0.4)                       # vaer snill mot APIet
            if rader is None:
                linjer.append('| %d | - | - | - | - | oppslag feilet |' % aar)
                feilaar += 1
                continue
            gyldige = [r for r in rader if r[1] is not None]
            ok = [r for r in gyldige if r[2] in GODKJENT]
            sum_mm = sum(r[1] for r in gyldige)
            tot_d += len(gyldige)
            tot_ok += len(ok)
            linjer.append('| %d | %d | %d %% | %d %% | %.0f | |' % (
                aar, len(gyldige), round(100 * len(gyldige) / ventet),
                round(100 * len(ok) / len(gyldige)) if gyldige else 0, sum_mm))
        snitt = round(100 * tot_d / (ventet * len(AAR)))
        kval = round(100 * tot_ok / tot_d) if tot_d else 0
        linjer += ['', '**Samlet: %d %% dekning, %d %% godkjent kvalitet.**' % (snitt, kval), '']
        oppsummering.append((elv, navn, sid, snitt, kval, feilaar))

    linjer = linjer[:6] + ['', '## Oppsummering', '',
                           '| Elv | Stasjon | Dekning | Kvalitet | Aar med feil |',
                           '|---|---|---|---|---|'] + \
        ['| %s | %s (%s) | %d %% | %d %% | %d |' % (e, n, s, d, k, f)
         for e, n, s, d, k, f in oppsummering] + [''] + linjer[6:]

    ut = 'data/logg/frost_dekning.md'
    os.makedirs(os.path.dirname(ut), exist_ok=True)
    with open(ut, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linjer) + '\n')
    print('\nSkrev %s' % ut)
    for e, n, s, d, k, f in oppsummering:
        print('  %-12s %-26s %3d %% dekning, %3d %% godkjent' % (e, n, d, k))
    return 0


if __name__ == '__main__':
    sys.exit(main())
