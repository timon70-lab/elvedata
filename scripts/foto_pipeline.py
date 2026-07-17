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
    "otra": {
        "inbox": "bilder/innboks/otra",
        "out": "bilder/otra",
        "json": "data/photos_otra.json",
        "station": "21.11.0",
        "id_prefix": "O",
        "date_rule": None,
        "zones": {"Sone 1": [[58.142762, 8.013436], [58.164603, 7.988782]], "Sone 2": [[58.164787, 7.988607], [58.208332, 7.930266]], "Sone 3A": [[58.208123, 7.929707], [58.226027, 7.937619]], "Sone 3B Hageodden": [[58.209974, 7.926544], [58.211917, 7.9308]], "Sone 3C Mosby": [[58.223008, 7.934099], [58.226191, 7.935972]], "Sone 4A": [[58.226213, 7.937501], [58.243502, 7.947615]], "Sone 4B Ravn\u00e5s": [[58.235168, 7.931351], [58.240403, 7.93666]], "Sone 4C Holmane": [[58.24119, 7.938655], [58.24238, 7.942274]], "Sone 5A Bl\u00e5": [[58.24365, 7.947759], [58.251304, 7.954163]], "Sone 5B R\u00f8d": [[58.251312, 7.954414], [58.253048, 7.954224]]},
    },
    "sygna": {
        "inbox": "bilder/innboks/sygna",
        "out": "bilder/sygna",
        "json": "data/photos_sygna.json",
        "station": "22.22.0",
        "id_prefix": "S",
        "date_rule": None,
        "zones": {"Alle \u00e5pne soner": [[58.076907, 7.816012], [58.218747, 7.759384]]},
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
_NVE_DAY_CACHE = {}

def fetch_vannforing(local_dt, station_id):
    """Timesverdi nærmest bildets tidspunkt. Returnerer None ved feil.
    Dagens observasjoner caches per (stasjon, dag) - viktig ved bulk-kjøringer."""
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
        cache_key = (station_id, day)
        if cache_key in _NVE_DAY_CACHE:
            obs = _NVE_DAY_CACHE[cache_key]
        else:
            r = requests.get(url, headers={"X-API-Key": api_key}, timeout=30)
            r.raise_for_status()
            obs = [o for o in r.json()["data"][0]["observations"] if o["value"] is not None]
            _NVE_DAY_CACHE[cache_key] = obs
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


# ── Hovedløp ───────────────────────────────────────────────────────────────
def translit(s):
    """Trygt filnavn: fjern mellomrom, erstatt æøå."""
    for a, b in [("æ","ae"),("ø","oe"),("å","aa"),("Æ","Ae"),("Ø","Oe"),("Å","Aa"),(" ",""),("/","-")]:
        s = s.replace(a, b)
    return s


def process_river(key, cfg):
    inbox = cfg["inbox"]
    if not os.path.isdir(inbox):
        return
    files = sorted(f for f in os.listdir(inbox)
                   if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if not files:
        return

    print(f"=== {key}: {len(files)} bilde(r) i innboksen ===")
    os.makedirs(cfg["out"], exist_ok=True)
    os.makedirs(MANUAL_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(cfg["json"]), exist_ok=True)

    photos = []
    if os.path.exists(cfg["json"]):
        with open(cfg["json"], encoding="utf-8") as f:
            photos = json.load(f)

    pfx = cfg["id_prefix"]
    next_num = 1 + max(
        (int(p["id"].split("-")[1]) for p in photos if p.get("id", "").startswith(pfx + "-")),
        default=0,
    )

    for name in files:
        src = os.path.join(inbox, name)
        print(f"Behandler {name} ...")

        try:
            lat, lon, local_dt = read_exif(src)
        except Exception as e:
            print(f"  EXIF-lesing feilet ({e}) -> manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue

        if lat is None or lon is None:
            print("  Mangler gyldig GPS -> manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue

        zone, dist_m = assign_zone(lat, lon, local_dt, cfg["zones"], cfg["date_rule"])
        if zone is None:
            print("  Sonetilordning feilet -> manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue
        print(f"  Sone: {zone} (avstand {dist_m} m)")

        vannforing = fetch_vannforing(local_dt, cfg["station"])
        print(f"  Vannføring: {vannforing if vannforing is not None else 'ukjent'}")

        dt = local_dt or datetime.now(LOCAL_TZ)
        base = f"{translit(zone)}_{dt.strftime('%Y%m%d_%H%M')}"
        out_name = base + ".jpg"
        n = 2
        while os.path.exists(os.path.join(cfg["out"], out_name)):
            out_name = f"{base}_{n}.jpg"
            n += 1

        try:
            img = Image.open(src)
            img = ImageOps.exif_transpose(img)
            if img.width > MAX_WIDTH:
                h = round(img.height * MAX_WIDTH / img.width)
                img = img.resize((MAX_WIDTH, h), Image.LANCZOS)
            img.convert("RGB").save(
                os.path.join(cfg["out"], out_name), "JPEG", quality=JPEG_QUALITY, optimize=True
            )
        except Exception as e:
            print(f"  Bildeprosessering feilet ({e}) -> manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue

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
        next_num += 1
        os.remove(src)
        print(f"  -> {out_name} lagret, original slettet.")

    with open(cfg["json"], "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=1)
    print(f"Oppdatert {cfg['json']} ({len(photos)} bilder totalt).")


def main():
    for key, cfg in RIVERS.items():
        process_river(key, cfg)


if __name__ == "__main__":
    sys.exit(main())
