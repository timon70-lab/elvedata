#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Logger varslet nedbor sammen med observert vannforing.

Kjores som et steg i nve_cache.yml, rett etter at MET- og NVE-filene er hentet.
Bruker de allerede nedlastede cache-filene - ingen egne API-kall.

Formalet er a bygge et datagrunnlag for a kalibrere tersklene i fiskemeldingen:
varslet nedbor er ferskvare som overskrives hver time, mens vannforingen kan
hentes igjen i ettertid. Uten denne loggen finnes det ingen fasit a sammenligne
varselet mot.

Skriver en rad per elv per kjoring til data/logg/nedbor_vf_<aar>.csv.
Nedborbotter er IKKE kumulative - mm_0_24 + mm_24_48 + mm_48_72 gir totalen.

Summeringen folger noyaktig samme algoritme som fiskemeldingen i dashbordene:
next_1_hours foretrekkes, next_6_hours brukes kun der timeoppløsning mangler,
og da hoppes det 6 timer fram for a unnga dobbelttelling.
"""
import csv
import datetime
import json
import os
import sys

ELVER = [
    # (navn, nedborfil, vannforingsfil)
    ('audna',       'data/nedbor.json',             'data/vannforing.json'),
    ('lygna',       'data/nedbor_lygna.json',       'data/vannforing_lygna.json'),
    ('sygna',       'data/nedbor_sygna.json',       'data/vannforing_sygna.json'),
    ('tovdalselva', 'data/nedbor_tovdalselva.json', 'data/vannforing_tovdalselva.json'),
]

LOGGKATALOG = 'data/logg'
KOLONNER = ['tid_utc', 'elv', 'mm_0_24', 'mm_24_48', 'mm_48_72', 'vf_naa', 'varsel_fra']


def nedbor_botter(sti, naa):
    """Summerer varslet nedbor i tre ikke-overlappende dognbotter fra naa."""
    with open(sti, encoding='utf-8') as f:
        j = json.load(f)
    ts = j['properties']['timeseries']
    oppdatert = j['properties'].get('meta', {}).get('updated_at', '')

    grenser = [naa + datetime.timedelta(hours=h) for h in (24, 48, 72)]
    botter = [0.0, 0.0, 0.0]
    truffet = False

    i = 0
    while i < len(ts):
        t = datetime.datetime.fromisoformat(ts[i]['time'].replace('Z', '+00:00'))
        if t >= grenser[2]:
            break
        d = ts[i]['data']
        mm, span = None, 1
        if 'next_1_hours' in d:
            mm = d['next_1_hours']['details'].get('precipitation_amount')
            span = 1
        elif 'next_6_hours' in d:
            mm = d['next_6_hours']['details'].get('precipitation_amount')
            span = 6
        # Samme slingringsmonn som dashbordet: ta med punktet inntil en time bak.
        if mm is not None and t >= naa - datetime.timedelta(hours=1):
            truffet = True
            if t < grenser[0]:
                botter[0] += mm
            elif t < grenser[1]:
                botter[1] += mm
            else:
                botter[2] += mm
        i += span

    if not truffet:
        raise ValueError('ingen varselpunkter innenfor 72 t')
    return [round(b, 2) for b in botter], oppdatert


def siste_vannforing(sti):
    """Siste observasjon som ikke er null."""
    with open(sti, encoding='utf-8') as f:
        j = json.load(f)
    obs = [o for o in j['data'][0]['observations'] if o.get('value') is not None]
    if not obs:
        raise ValueError('ingen observasjoner med verdi')
    return round(float(obs[-1]['value']), 2)


def main():
    naa = datetime.datetime.now(datetime.timezone.utc).replace(
        minute=0, second=0, microsecond=0)
    tid = naa.strftime('%Y-%m-%dT%H:00Z')

    os.makedirs(LOGGKATALOG, exist_ok=True)
    sti = os.path.join(LOGGKATALOG, 'nedbor_vf_%d.csv' % naa.year)
    ny_fil = not os.path.exists(sti)

    # Ikke skriv samme timestamp to ganger (workflowen kan kjores manuelt).
    if not ny_fil:
        with open(sti, encoding='utf-8') as f:
            if any(rad.startswith(tid + ';') for rad in f):
                print('Rader for %s finnes allerede - hopper over.' % tid)
                return 0

    rader, feil = [], []
    for navn, nedborfil, vannforingsfil in ELVER:
        try:
            botter, oppdatert = nedbor_botter(nedborfil, naa)
            vf = siste_vannforing(vannforingsfil)
            rader.append([tid, navn] + botter + [vf, oppdatert])
        except Exception as e:
            feil.append('%s: %s' % (navn, e))

    if not rader:
        print('Ingen elver kunne logges: ' + ' | '.join(feil), file=sys.stderr)
        return 0  # aldri velt hele workflowen paa dette

    with open(sti, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=';', lineterminator='\n')
        if ny_fil:
            w.writerow(KOLONNER)
        w.writerows(rader)

    print('Logget %d elver til %s (%s)' % (len(rader), sti, tid))
    for r in rader:
        print('  %-12s 0-24t %5.1f mm | 24-48t %5.1f mm | 48-72t %5.1f mm | vf %6.1f'
              % (r[1], r[2], r[3], r[4], r[5]))
    for f_ in feil:
        print('  HOPPET OVER ' + f_)
    return 0


if __name__ == '__main__':
    sys.exit(main())
