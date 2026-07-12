# -*- coding: utf-8 -*-
"""
Henter "siste fangster" for Audna, Lygna, Mandalselva og Otra fra Inaturs laksebørs
(laksebors.inatur.no/graphql) og skriver ut filtrerte, anonymiserte JSON-filer
til data/fangster_<elv>.json.

Filtrering:
  - Kun ART == "Laks" (etter avtale — sjøørret o.a. tas ikke med)
  - Kun fangster siste 72 timer (rullende, ikke kalenderdager)
  - NAVN-feltet fjernes fullstendig før noe skrives til disk (personvern —
    Inatur anonymiserer ikke selv konsekvent, så vi må gjøre det)

Feltene som beholdes per fangst: dato, sone, vekt, agn.

Dette er et UTESTET førsteutkast — det interne GraphQL-endepunktet er ikke
offentlig dokumentert av Inatur. Kjør med workflow_dispatch og sjekk loggen
før dette kobles til et fast tidsskjema.
"""
import json
import os
from datetime import datetime, timedelta, timezone

import requests

GRAPHQL_URL = "https://laksebors.inatur.no/graphql"
LOOKBACK_HOURS = 72

RIVERS = {
    "audna":       {"river_id": 621,  "out": "data/fangster_audna.json"},
    "lygna":       {"river_id": 25,   "out": "data/fangster_lygna.json"},
    "mandalselva": {"river_id": 1542, "out": "data/fangster_mandalselva.json"},
    "otra":        {"river_id": 6,    "out": "data/fangster_otra.json"},
}

QUERY = """
query CatchesQuery($riverId: Int!, $year: String!) {
  catches(riverId: $riverId, year: $year, limit: 100, offset: 0, sort: "-DATO") {
    DATO
    KG
    SONE
    Redskap
    ART
    __typename
  }
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Origin": "https://laksebors.inatur.no",
    "Referer": "https://laksebors.inatur.no/",
    "User-Agent": "Mozilla/5.0 (compatible; elvedata-fangstpipeline/1.0)",
}


def fetch_river(key, river_id):
    year = str(datetime.now().year)
    payload = {
        "operationName": "CatchesQuery",
        "query": QUERY,
        "variables": {"riverId": river_id, "year": year},
    }
    resp = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body:
        raise RuntimeError(f"GraphQL-feil: {body['errors']}")
    return body["data"]["catches"]


def process(catches):
    cutoff_ms = (datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)).timestamp() * 1000
    out = []
    for c in catches:
        if c.get("ART") != "Laks":
            continue
        try:
            dato_ms = int(c["DATO"])
        except (TypeError, ValueError):
            continue
        if dato_ms < cutoff_ms:
            continue
        dato_iso = datetime.fromtimestamp(dato_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        out.append({
            "dato": dato_iso,
            "sone": c.get("SONE"),
            "vekt": c.get("KG"),
            "agn": c.get("Redskap"),
        })
    # Nyeste først
    out.sort(key=lambda x: x["dato"], reverse=True)
    return out


def main():
    any_ok = False
    for key, cfg in RIVERS.items():
        print(f"=== {key} (riverId={cfg['river_id']}) ===")
        try:
            catches = fetch_river(key, cfg["river_id"])
            recent = process(catches)
            os.makedirs(os.path.dirname(cfg["out"]), exist_ok=True)
            with open(cfg["out"], "w", encoding="utf-8") as f:
                json.dump(recent, f, ensure_ascii=False, indent=1)
            print(f"  OK: {len(catches)} hentet totalt, {len(recent)} siste {LOOKBACK_HOURS}t (laks) -> {cfg['out']}")
            any_ok = True
        except Exception as e:
            print(f"  FEIL for {key}: {e}")
            # Ikke la én elvs feil stoppe de andre. Eksisterende fil (om noen)
            # blir stående urørt, dashbordet faller da tilbake til forrige data.

    if not any_ok:
        raise SystemExit("Ingen elver ble hentet OK — sjekk endepunkt/headere.")


if __name__ == "__main__":
    main()
