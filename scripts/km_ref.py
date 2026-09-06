#!/usr/bin/env python3
"""
km_ref.py — lineaerreferanse langs en elv.

Regner ut hvor langt opp i elva et punkt ligger, maalt i meter langs
senterlinja fra munningen (data/senterlinje_<elv>.geojson).

Modulen er delt mellom scripts/beregn_km.py (etterberegning av hele
registre) og foto-pipelinene (km paa nye bilder ved opplasting), slik at
geometrien finnes ett sted og de to alltid gir samme svar.

km brukes KUN til sortering og visning. Markoerposisjoner i kartet leser
fortsatt lat/lon direkte og paavirkes ikke.
"""

import json
import math
import os

# Hvor langt utenfor sonens eget km-intervall et bilde faar projisere seg.
# Fanger opp at sonepunktene er satt paa bredden og at bilder kan vaere tatt
# rett utenfor sonegrensa, uten aa aapne for at et bilde snapper til feil
# arm av en meander flere kilometer unna.
SONE_MARGIN_M = 400


class KmRef:
    """Senterlinje med kumulativ lengde, klar til projeksjon."""

    def __init__(self, coords):
        if not coords or len(coords) < 2:
            raise ValueError('senterlinja maa ha minst to punkter')
        self.lat0 = sum(c[1] for c in coords) / len(coords)
        self.lon0 = sum(c[0] for c in coords) / len(coords)
        self._k = 111320.0 * math.cos(math.radians(self.lat0))
        self.pts = [self._xy(c[0], c[1]) for c in coords]
        self.cum = [0.0]
        for i in range(len(self.pts) - 1):
            self.cum.append(self.cum[-1] + math.dist(self.pts[i], self.pts[i + 1]))
        self.lengde_m = self.cum[-1]

    def _xy(self, lon, lat):
        """Lokal plan projeksjon. Feilen over 20 km er faa meter - godt nok
        naar resultatet bare skal brukes til rekkefoelge."""
        return ((lon - self.lon0) * self._k, (lat - self.lat0) * 110540.0)

    def projiser(self, lat, lon, lo=None, hi=None):
        """Naermeste punkt paa linja. Returnerer (km_i_meter, avstand_i_meter).
        lo/hi avgrenser soeket til et km-intervall (sonebegrensning)."""
        p = self._xy(lon, lat)
        best_d, best_km = float('inf'), 0.0
        for i in range(len(self.pts) - 1):
            if lo is not None and (self.cum[i + 1] < lo or self.cum[i] > hi):
                continue
            a, b = self.pts[i], self.pts[i + 1]
            vx, vy = b[0] - a[0], b[1] - a[1]
            L2 = vx * vx + vy * vy
            if L2 == 0:
                continue
            t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2
            t = max(0.0, min(1.0, t))
            d = math.dist(p, (a[0] + t * vx, a[1] + t * vy))
            if d < best_d:
                best_d, best_km = d, self.cum[i] + t * math.sqrt(L2)
        if best_d == float('inf'):        # tomt intervall - proev hele linja
            return self.projiser(lat, lon)
        return best_km, best_d

    def sone_intervaller(self, zones, margin=SONE_MARGIN_M):
        """km-intervall per sone. Taaler begge formatene vi bruker:
        pipelinens {navn: [[lat,lon],[lat,lon]]} og dashbordets
        {navn: {"s": [lat,lon], "e": [lat,lon]}}."""
        ut = {}
        for navn, c in (zones or {}).items():
            try:
                if isinstance(c, dict):
                    s, e = c['s'], c['e']
                else:
                    s, e = c[0], c[1]
                ks, _ = self.projiser(s[0], s[1])
                ke, _ = self.projiser(e[0], e[1])
            except (KeyError, TypeError, IndexError):
                continue
            ut[navn] = (min(ks, ke) - margin, max(ks, ke) + margin)
        return ut

    def km(self, lat, lon, zone=None, intervaller=None, desimaler=2):
        """km fra munningen, avrundet. None hvis koordinater mangler."""
        if lat is None or lon is None:
            return None
        lo_hi = (intervaller or {}).get(zone)
        km_m, _ = self.projiser(lat, lon, *(lo_hi if lo_hi else (None, None)))
        return round(km_m / 1000.0, desimaler)


def last(elv, root=None):
    """Leser data/senterlinje_<elv>.geojson. Returnerer None hvis fila ikke
    finnes, slik at elver uten senterlinje bare hopper over km-beregningen."""
    if root is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sti = os.path.join(root, 'data', f'senterlinje_{elv}.geojson')
    if not os.path.exists(sti):
        return None
    try:
        with open(sti, encoding='utf-8') as fh:
            gj = json.load(fh)
        linjer = [f for f in gj.get('features', [])
                  if f.get('geometry', {}).get('type') == 'LineString']
        if len(linjer) != 1:
            print(f'  km: {elv} har {len(linjer)} LineString(s) - forventet 1, hopper over')
            return None
        return KmRef(linjer[0]['geometry']['coordinates'])
    except Exception as e:
        print(f'  km: kunne ikke lese senterlinje for {elv} ({e}) - hopper over')
        return None
