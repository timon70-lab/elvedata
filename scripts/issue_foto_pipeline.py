# -*- coding: utf-8 -*-
"""
Issue-basert foto-pipeline for Elvedata.

I stedet for å laste opp originalbilder til en innboks-mappe (som blir
liggende i git-historikken for alltid, ~7 MB per bilde), oppretter du en
GitHub Issue med bildene limt/dratt inn i tekstfeltet. GitHub lagrer da
bildene i sin egen vedleggslagring (user-attachments) - IKKE i selve
repoet, og teller derfor ikke mot 1 GB-grensen.

Denne pipelinen:
  1. Leser issue-tittel for å finne hvilken elv (audna/mandalselva/lygna
     som substreng, case-insensitive).
  2. Finner alle bilde-URL-er i issue-teksten (markdown ![]()-syntaks).
  3. Laster ned hvert bilde midlertidig, kjører dem gjennom NØYAKTIG samme
     logikk som innboks-pipelinen (EXIF, sonetilordning, NVE-vannføring,
     komprimering til 1600px/q80).
  4. Skriver kun de komprimerte bildene til bilder/<elv>/ og oppdaterer
     data/photos_<elv>.json - selve GitHub-vedleggene forblir utenfor git.
  5. Kommenterer på issuen med et sammendrag og lukker den.

Miljøvariabler (satt av workflow): GITHUB_TOKEN, GITHUB_REPOSITORY,
ISSUE_NUMBER, ISSUE_TITLE, ISSUE_BODY.
"""
import tempfile
import re

# -*- coding: utf-8 -*-
"""
Foto-pipeline for Elvedata — flerelvs (Audna, Mandalselva, Lygna).
Kjøres av GitHub Actions ved push til bilder/innboks/<elv>/.

For hvert bilde i en elvs innboks:
  1. Les EXIF (GPS + tid). Ugyldig/manglende GPS -> bilder/innboks/manuell/.
  2. Tilordne nærmeste sone fra elvens sonegrenser (Audna: Sone5/5A/5B-datoregel).
  3. Hent vannføring fra elvens NVE-stasjon (timesverdi nærmest tidspunktet).
  4. Komprimer (maks 1600 px, JPEG q80, EXIF strippes) -> bilder/<elv>/.
  5. Appender til data/photos_<elv>.json og sletter originalen.

Miljøvariabel: NVE_API_KEY (GitHub Secrets).
"""
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests
from PIL import Image, ImageOps
from PIL.ExifTags import GPSTAGS, TAGS

MANUAL_DIR = "bilder/innboks/manuell"
MAX_WIDTH = 1600
JPEG_QUALITY = 80
LOCAL_TZ = ZoneInfo("Europe/Oslo")


def audna_date_rule(zone_segments, local_dt):
    """Audna: bilder t.o.m. 2021 -> Sone5 (udelt); f.o.m. 2022 -> 5A/5B (aldri Sone5)."""
    year = local_dt.year if local_dt else datetime.now(LOCAL_TZ).year
    if year <= 2021:
        return {z: s for z, s in zone_segments.items() if z not in ("Sone 5A", "Sone 5B")}
    return {z: s for z, s in zone_segments.items() if z != "Sone5"}


RIVERS = {
    "audna": {
        "inbox": "bilder/innboks/audna",
        "out": "bilder/audna",
        "json": "data/photos_audna.json",
        "station": "23.8.0",
        "id_prefix": "A",
        "date_rule": audna_date_rule,
        "zones": {"Sone 5A": [[58.12663, 7.33986], [58.15179, 7.36636]], "Sone 5B": [[58.15189, 7.3666], [58.21173, 7.33608]], "Sone1": [[58.05198, 7.27773], [58.10616, 7.34156]], "Sone2": [[58.1046, 7.32402], [58.12497, 7.33835]], "Sone3": [[58.11864, 7.34185], [58.12488, 7.33926]], "Sone4": [[58.12488, 7.33926], [58.12555, 7.33911]], "Sone5": [[58.12644, 7.3404], [58.21173, 7.33608]], "Sone6": [[58.21189, 7.3364], [58.22503, 7.33559]], "Sone7": [[58.22583, 7.33559], [58.242, 7.34598]], "Sone8": [[58.24221, 7.34617], [58.32363, 7.36626]]},
    },
    "mandalselva": {
        "inbox": "bilder/innboks/mandalselva",
        "out": "bilder/mandalselva",
        "json": "data/photos_mandalselva.json",
        "station": "22.4.0",
        "id_prefix": "M",
        "date_rule": None,
        "zones": {"Bjåhylen": [[58.26443, 7.51949], [58.27256, 7.5224]], "Bjørkenes": [[58.12563, 7.53263], [58.12878, 7.53292]], "Bringsdal A": [[58.1098, 7.53488], [58.11112, 7.53627]], "Bringsdal B": [[58.11122, 7.53637], [58.11409, 7.53641]], "Bringsdal C": [[58.11411, 7.53618], [58.11625, 7.5298]], "Fossefjellene": [[58.11845, 7.52884], [58.11994, 7.52804]], "Fossefjellene syd": [[58.11744, 7.52565], [58.1185, 7.52862]], "Furuholmen": [[58.12167, 7.52964], [58.12549, 7.53305]], "Fuskeland A": [[58.10933, 7.53458], [58.11157, 7.53383]], "Fuskeland B": [[58.11167, 7.53407], [58.11373, 7.53477]], "Fuskeland C": [[58.11375, 7.53455], [58.11425, 7.53212]], "Fuskeland D": [[58.11436, 7.532], [58.116, 7.52794]], "Fuskeland under Nødingfossen": [[58.1032, 7.53277], [58.10524, 7.5338]], "Grimefossen A": [[58.11655, 7.52844], [58.11818, 7.53012]], "Grimefossen B": [[58.11828, 7.53022], [58.12126, 7.52994]], "Hauge A": [[58.13593, 7.53885], [58.1389, 7.54186]], "Hauge B1": [[58.13902, 7.542], [58.14082, 7.54367]], "Hauge B2": [[58.14117, 7.54411], [58.14277, 7.54544]], "Hauge C": [[58.14288, 7.54558], [58.14465, 7.54796]], "Hauge D": [[58.14545, 7.54837], [58.14958, 7.55351]], "Heia": [[58.09776, 7.5324], [58.09928, 7.53348]], "Holmegård": [[58.0973, 7.53079], [58.10246, 7.53241]], "Holmesland A": [[58.13577, 7.53744], [58.13945, 7.54166]], "Holmesland B": [[58.13968, 7.54173], [58.14218, 7.54428]], "Holmesland C": [[58.1456, 7.54808], [58.14894, 7.55274]], "Holmesland P": [[58.14227, 7.54432], [58.14474, 7.54758]], "Klevelandsfossen": [[58.25034, 7.51761], [58.25436, 7.51854]], "Laksehylen": [[58.28023, 7.52474], [58.29398, 7.52741]], "Møll": [[58.09016, 7.52388], [58.09329, 7.52707]], "Nedre Holum": [[58.04857, 7.49707], [58.07799, 7.5169]], "Nedre Nøding": [[58.09947, 7.53363], [58.101, 7.53455]], "Nodehylen": [[58.27287, 7.52251], [58.28054, 7.5249]], "Smeland": [[58.12867, 7.53316], [58.13589, 7.5375]], "Sone 1": [[58.02, 7.45592], [58.0481, 7.49793]], "Sone 3": [[58.14889, 7.55298], [58.25011, 7.51745]], "Sone 4": [[58.29408, 7.52763], [58.43661, 7.54922]], "Steinshylen": [[58.25473, 7.51858], [58.26406, 7.51934]], "Stoveland": [[58.12132, 7.53011], [58.12699, 7.53454]], "Strædethylen": [[58.27918, 7.52291], [58.28334, 7.52582]], "Øvre Nøding": [[58.12842, 7.53385], [58.13221, 7.53603]]},
    },
    "lygna": {
        "inbox": "bilder/innboks/lygna",
        "out": "bilder/lygna",
        "json": "data/photos_lygna.json",
        "station": "24.9.0",
        "id_prefix": "L",
        "date_rule": None,
        "zones": {"Gysfossen til Lygne": [[58.30483, 7.21033], [58.39585, 7.22089]], "Kvåsfossen til Gysfossen": [[58.26817, 7.18861], [58.30419, 7.20943]], "Sone 1 Bjerga og Fidja": [[58.14148, 7.01938], [58.14107, 7.03934]], "Sone 10 Grøvan og Foss": [[58.18731, 7.10734], [58.19597, 7.11697]], "Sone 11 Foss øvre": [[58.19641, 7.1173], [58.21209, 7.13638]], "Sone 13 Gitlestad": [[58.21788, 7.14613], [58.22142, 7.15094]], "Sone 14 Rudjord": [[58.22181, 7.15119], [58.23157, 7.16139]], "Sone 15 Vemestad ytre": [[58.23211, 7.16125], [58.23642, 7.17249]], "Sone 16 Vemestad øvre": [[58.2368, 7.17284], [58.24428, 7.17885]], "Sone 17 Moi": [[58.24471, 7.1788], [58.25733, 7.1904]], "Sone 18 Kvås": [[58.25792, 7.19041], [58.26308, 7.19369]], "Sone 2 Årnes": [[58.13953, 7.03994], [58.14298, 7.05089]], "Sone 3 Kvavik": [[58.1435, 7.05079], [58.14539, 7.05901]], "Sone 4 Berge øvre": [[58.14558, 7.06007], [58.14238, 7.06307]], "Sone 5 Bringsjord": [[58.14184, 7.06384], [58.14381, 7.07018]], "Sone 6 Bergsaker": [[58.14411, 7.07086], [58.14776, 7.07779]], "Sone 7": [[58.14797, 7.07895], [58.14917, 7.08637]], "Sone 8 Prestegården": [[58.14944, 7.08678], [58.16698, 7.08765]], "Sone 9 Kvelland": [[58.16748, 7.08782], [58.18692, 7.10662]], "Sone12 Vegge": [[58.21253, 7.1366], [58.21737, 7.14569]]},
    },
}


# ── EXIF-hjelpere ──────────────────────────────────────────────────────────
def _dms_to_deg(dms, ref):
    deg = float(dms[0]) + float(dms[1]) / 60.0 + float(dms[2]) / 3600.0
    if ref in ("S", "W"):
        deg = -deg
    return deg


def read_exif(path):
    """Returnerer (lat, lon, local_dt) — alle kan være None."""
    img = Image.open(path)
    exif = img.getexif()
    lat = lon = dt = None

    # Tidspunkt
    raw_dt = exif.get(0x9003) or exif.get(0x0132)  # DateTimeOriginal / DateTime
    if not raw_dt:
        try:
            ifd = exif.get_ifd(0x8769)  # Exif IFD
            raw_dt = ifd.get(0x9003)
        except Exception:
            pass
    if raw_dt:
        try:
            dt = datetime.strptime(str(raw_dt), "%Y:%m:%d %H:%M:%S").replace(tzinfo=LOCAL_TZ)
        except ValueError:
            dt = None

    # GPS
    try:
        gps = exif.get_ifd(0x8825)
        if gps:
            gd = {GPSTAGS.get(k, k): v for k, v in gps.items()}
            if "GPSLatitude" in gd and "GPSLongitude" in gd:
                lat = _dms_to_deg(gd["GPSLatitude"], gd.get("GPSLatitudeRef", "N"))
                lon = _dms_to_deg(gd["GPSLongitude"], gd.get("GPSLongitudeRef", "E"))
    except Exception:
        lat = lon = None

    # Pixel m.fl. kan skrive GPS-tagger med NaN/0-verdier når posisjon manglet.
    # Behandle alt som ikke er gyldige koordinater som "mangler GPS".
    import math
    if lat is not None and lon is not None:
        if (not isinstance(lat, float) or not isinstance(lon, float)
                or math.isnan(lat) or math.isnan(lon)
                or not (-90 <= lat <= 90) or not (-180 <= lon <= 180)
                or (lat == 0 and lon == 0)):
            lat = lon = None

    return lat, lon, dt


# ── Sonetilordning ─────────────────────────────────────────────────────────
def _dist_point_segment_m(p, a, b):
    """Avstand (meter, tilnærmet) fra punkt p til linjesegment a-b. Punkter er (lat, lon)."""
    import math
    lat0 = math.radians(p[0])
    mx = 111320.0 * math.cos(lat0)  # meter per grad lengdegrad
    my = 110540.0                   # meter per grad breddegrad

    def xy(q):
        return ((q[1] - p[1]) * mx, (q[0] - p[0]) * my)

    ax, ay = xy(a)
    bx, by = xy(b)
    dx, dy = bx - ax, by - ay
    seg2 = dx * dx + dy * dy
    if seg2 == 0:
        return (ax * ax + ay * ay) ** 0.5
    t = max(0.0, min(1.0, (-ax * dx - ay * dy) / seg2))
    cx, cy = ax + t * dx, ay + t * dy
    return (cx * cx + cy * cy) ** 0.5


def assign_zone(lat, lon, local_dt, zone_segments, date_rule=None):
    """Nærmeste sone. date_rule kan filtrere kandidater (f.eks. Audnas Sone5/5A/5B-regel)."""
    candidates = date_rule(zone_segments, local_dt) if date_rule else dict(zone_segments)
    best_zone, best_d = None, float("inf")
    for zone, (a, b) in candidates.items():
        d = _dist_point_segment_m((lat, lon), a, b)
        if d < best_d:
            best_zone, best_d = zone, d
    if best_zone is None:
        return None, None  # kaller må håndtere (flyttes til manuell)
    return best_zone, round(best_d)


# ── NVE-vannføring ─────────────────────────────────────────────────────────
def fetch_vannforing(local_dt, station_id):
    """Timesverdi nærmest bildets tidspunkt. Returnerer None ved feil."""
    api_key = os.environ.get("NVE_API_KEY", "")
    if not api_key or not local_dt:
        return None
    day = local_dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    url = (
        "https://hydapi.nve.no/api/v1/Observations"
        f"?StationId={station_id}&Parameter=1001&ResolutionTime=60"
        f"&ReferenceTime={day}T00:00:00Z/{day}T23:59:59Z"
    )
    try:
        r = requests.get(url, headers={"X-API-Key": api_key}, timeout=30)
        r.raise_for_status()
        obs = [o for o in r.json()["data"][0]["observations"] if o["value"] is not None]
        if not obs:
            return None
        target = local_dt.astimezone(timezone.utc)
        best = min(
            obs,
            key=lambda o: abs(
                datetime.fromisoformat(o["time"].replace("Z", "+00:00")) - target
            ),
        )
        return round(best["value"], 1)
    except Exception as e:
        print(f"  NVE-oppslag feilet: {e}")
        return None


def translit(s):
    """Trygt filnavn: fjern mellomrom, erstatt æøå."""
    for a, b in [("æ","ae"),("ø","oe"),("å","aa"),("Æ","Ae"),("Ø","Oe"),("Å","Aa"),(" ",""),("/","-")]:
        s = s.replace(a, b)
    return s



# ── GitHub Issue-spesifikk logikk ───────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
ISSUE_NUMBER = os.environ.get("ISSUE_NUMBER", "")
ISSUE_TITLE = os.environ.get("ISSUE_TITLE", "")
ISSUE_BODY = os.environ.get("ISSUE_BODY", "") or ""

API_BASE = f"https://api.github.com/repos/{REPO}"
API_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def detect_river(title):
    t = title.lower()
    for key in RIVERS:
        if key in t:
            return key
    return None


def extract_image_urls(body):
    """Finn alle bilde-URL-er i issue-teksten (markdown ![]()-syntaks pluss bare lenker)."""
    md = re.findall(r'!\[[^\]]*\]\((https://[^\s)]+)\)', body)
    bare = re.findall(
        r'(https://(?:github\.com/user-attachments/assets|user-images\.githubusercontent\.com|'
        r'private-user-images\.githubusercontent\.com)/[^\s")\'<>]+)',
        body,
    )
    seen, out = set(), []
    for u in md + bare:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def download_image(url, dest):
    r = requests.get(url, headers={"User-Agent": "elvedata-issue-pipeline/1.0"}, timeout=30)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)


def post_comment(text):
    if not (GITHUB_TOKEN and REPO and ISSUE_NUMBER):
        print("Mangler issue-kontekst, kan ikke kommentere:", text)
        return
    requests.post(
        f"{API_BASE}/issues/{ISSUE_NUMBER}/comments",
        headers=API_HEADERS,
        json={"body": text},
        timeout=20,
    )


def close_issue():
    if not (GITHUB_TOKEN and REPO and ISSUE_NUMBER):
        return
    requests.patch(
        f"{API_BASE}/issues/{ISSUE_NUMBER}",
        headers=API_HEADERS,
        json={"state": "closed"},
        timeout=20,
    )


def process_one_photo(local_path, name, cfg, photos):
    """Kjør ett nedlastet bilde gjennom samme logikk som innboks-pipelinen.
       Returnerer en menneskelesbar statuslinje til issue-kommentaren."""
    try:
        lat, lon, local_dt = read_exif(local_path)
    except Exception as e:
        return f"❌ {name}: EXIF-lesing feilet ({e})"

    if lat is None or lon is None:
        return f"⚠️ {name}: mangler gyldig GPS - ikke lagt til (ta bildet med Kamera-valget direkte i opplastingen, ikke fra galleri)"

    zone, dist_m = assign_zone(lat, lon, local_dt, cfg["zones"], cfg["date_rule"])
    if zone is None:
        return f"⚠️ {name}: klarte ikke tilordne sone"

    vannforing = fetch_vannforing(local_dt, cfg["station"])

    pfx = cfg["id_prefix"]
    next_num = 1 + max(
        (int(p["id"].split("-")[1]) for p in photos if p.get("id", "").startswith(pfx + "-")),
        default=0,
    )
    dt = local_dt or datetime.now(LOCAL_TZ)
    base = f"{translit(zone)}_{dt.strftime('%Y%m%d_%H%M')}"
    out_name = base + ".jpg"
    n = 2
    while os.path.exists(os.path.join(cfg["out"], out_name)):
        out_name = f"{base}_{n}.jpg"
        n += 1

    try:
        img = Image.open(local_path)
        img = ImageOps.exif_transpose(img)
        if img.width > MAX_WIDTH:
            h = round(img.height * MAX_WIDTH / img.width)
            img = img.resize((MAX_WIDTH, h), Image.LANCZOS)
        img.convert("RGB").save(
            os.path.join(cfg["out"], out_name), "JPEG", quality=JPEG_QUALITY, optimize=True
        )
    except Exception as e:
        return f"❌ {name}: bildeprosessering feilet ({e})"

    photos.append({
        "id": f"{pfx}-{next_num:03d}",
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "file": out_name,
        "caption": zone,
        "zone": zone,
        "dateISO": dt.strftime("%Y-%m-%d"),
        "timeUTC": dt.astimezone(timezone.utc).strftime("%H:%M"),
        "locId": zone,
        "vannforing": vannforing,
        "autoSone": True,
        "soneAvstandM": dist_m,
    })
    vf = f"{vannforing} m³/s" if vannforing is not None else "vannføring ukjent"
    return f"✅ {name} → {zone} ({vf})"


def main():
    river_key = detect_river(ISSUE_TITLE)
    if river_key is None:
        post_comment(
            "Fant ikke noe elvenavn i tittelen (audna, mandalselva eller lygna). "
            "Rediger tittelen slik at den inneholder elvenavnet, og lag issuen på nytt."
        )
        print("Ingen elv funnet i tittelen - avbryter uten å lukke issuen.")
        return

    cfg = RIVERS[river_key]
    urls = extract_image_urls(ISSUE_BODY)
    if not urls:
        post_comment(
            "Fant ingen bilder i issuen. Dra-og-slipp eller lim inn bildene direkte i "
            "tekstfeltet (ikke som lenke til en annen tjeneste), og prøv igjen."
        )
        print("Ingen bilde-URL-er funnet - avbryter uten å lukke issuen.")
        return

    photos = []
    if os.path.exists(cfg["json"]):
        with open(cfg["json"], encoding="utf-8") as f:
            photos = json.load(f)

    os.makedirs(cfg["out"], exist_ok=True)
    os.makedirs(os.path.dirname(cfg["json"]), exist_ok=True)

    lines = [f"**{river_key.capitalize()}** — {len(urls)} bilde(r) funnet i issuen:\n"]
    with tempfile.TemporaryDirectory() as tmp:
        for i, url in enumerate(urls, start=1):
            local = os.path.join(tmp, f"img_{i}.jpg")
            name = f"Bilde {i}"
            try:
                download_image(url, local)
            except Exception as e:
                lines.append(f"❌ {name}: nedlasting feilet ({e})")
                continue
            lines.append(process_one_photo(local, name, cfg, photos))

    with open(cfg["json"], "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=1)

    summary = "\n".join(lines) + f"\n\n_Totalt {len(photos)} bilder i {river_key} nå._"
    print(summary)
    post_comment(summary)
    close_issue()


if __name__ == "__main__":
    main()
