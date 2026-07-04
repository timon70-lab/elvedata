# -*- coding: utf-8 -*-
"""
Foto-pipeline for Elvedata (Audna).
Kjøres av GitHub Actions ved push til bilder/innboks/audna/.

For hvert bilde i innboksen:
  1. Les EXIF (GPS-posisjon + tidspunkt). Uten GPS -> flyttes til bilder/innboks/manuell/.
  2. Tilordne nærmeste sone fra koordinatene (med Sone5/5A/5B-datoregel).
  3. Hent vannføring fra NVE HydAPI (timesverdi nærmest bildets tidspunkt).
  4. Komprimer/nedskaler (maks 1600 px bredde, JPEG q80, EXIF strippes) -> bilder/audna/.
  5. Legg til oppføring i data/photos_audna.json og slett originalen.

Miljøvariabel: NVE_API_KEY (fra GitHub Secrets).
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

# ── Konfigurasjon ──────────────────────────────────────────────────────────
INBOX_DIR = "bilder/innboks/audna"
MANUAL_DIR = "bilder/innboks/manuell"
OUT_DIR = "bilder/audna"
JSON_PATH = "data/photos_audna.json"
STATION_ID = "23.8.0"  # Gaupefossen
MAX_WIDTH = 1600
JPEG_QUALITY = 80
ID_PREFIX = "A"
LOCAL_TZ = ZoneInfo("Europe/Oslo")

# Audna sonegrenser (start/slutt-punkt per sone, fra elvesoner.xlsx)
ZONE_SEGMENTS = {
    "Sone1":   ((58.05198, 7.27773), (58.10616, 7.34156)),
    "Sone2":   ((58.10460, 7.32402), (58.12497, 7.33835)),
    "Sone3":   ((58.11864, 7.34185), (58.12488, 7.33926)),
    "Sone4":   ((58.12488, 7.33926), (58.12555, 7.33911)),
    "Sone5":   ((58.12644, 7.34040), (58.21173, 7.33608)),
    "Sone 5A": ((58.12663, 7.33986), (58.15179, 7.36636)),
    "Sone 5B": ((58.15189, 7.36660), (58.21173, 7.33608)),
    "Sone6":   ((58.21189, 7.33640), (58.22503, 7.33559)),
    "Sone7":   ((58.22583, 7.33559), (58.24200, 7.34598)),
    "Sone8":   ((58.24221, 7.34617), (58.32363, 7.36626)),
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


def assign_zone(lat, lon, local_dt):
    """Nærmeste sone. Datoregel: <=2021 -> Sone5 (udelt); >=2022 -> 5A/5B (aldri Sone5)."""
    year = local_dt.year if local_dt else datetime.now(LOCAL_TZ).year
    if year <= 2021:
        candidates = {z: s for z, s in ZONE_SEGMENTS.items() if z not in ("Sone 5A", "Sone 5B")}
    else:
        candidates = {z: s for z, s in ZONE_SEGMENTS.items() if z != "Sone5"}
    best_zone, best_d = None, float("inf")
    for zone, (a, b) in candidates.items():
        d = _dist_point_segment_m((lat, lon), a, b)
        if d < best_d:
            best_zone, best_d = zone, d
    if best_zone is None:
        return None, None  # kaller må håndtere (flyttes til manuell)
    return best_zone, round(best_d)


# ── NVE-vannføring ─────────────────────────────────────────────────────────
def fetch_vannforing(local_dt):
    """Timesverdi nærmest bildets tidspunkt. Returnerer None ved feil."""
    api_key = os.environ.get("NVE_API_KEY", "")
    if not api_key or not local_dt:
        return None
    day = local_dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    url = (
        "https://hydapi.nve.no/api/v1/Observations"
        f"?StationId={STATION_ID}&Parameter=1001&ResolutionTime=60"
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


# ── Hovedløp ───────────────────────────────────────────────────────────────
def main():
    if not os.path.isdir(INBOX_DIR):
        print("Ingen innboks-mappe, ingenting å gjøre.")
        return

    files = sorted(
        f for f in os.listdir(INBOX_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    if not files:
        print("Ingen nye bilder i innboksen.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(MANUAL_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)

    photos = []
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, encoding="utf-8") as f:
            photos = json.load(f)

    next_num = 1 + max(
        (int(p["id"].split("-")[1]) for p in photos if p.get("id", "").startswith(ID_PREFIX + "-")),
        default=0,
    )

    for name in files:
        src = os.path.join(INBOX_DIR, name)
        print(f"Behandler {name} ...")

        try:
            lat, lon, local_dt = read_exif(src)
        except Exception as e:
            print(f"  EXIF-lesing feilet ({e}) -> flyttes til manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue

        if lat is None or lon is None:
            print("  Mangler gyldig GPS -> flyttes til manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue

        zone, dist_m = assign_zone(lat, lon, local_dt)
        if zone is None:
            print("  Sonetilordning feilet -> flyttes til manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue
        print(f"  Sone: {zone} (avstand {dist_m} m)")

        vannforing = fetch_vannforing(local_dt)
        print(f"  Vannføring: {vannforing if vannforing is not None else 'ukjent'}")

        # Komprimer og lagre
        dt = local_dt or datetime.now(LOCAL_TZ)
        base = f"{zone.replace(' ', '')}_{dt.strftime('%Y%m%d_%H%M')}"
        out_name = base + ".jpg"
        n = 2
        while os.path.exists(os.path.join(OUT_DIR, out_name)):
            out_name = f"{base}_{n}.jpg"
            n += 1

        try:
            img = Image.open(src)
            img = ImageOps.exif_transpose(img)
            if img.width > MAX_WIDTH:
                h = round(img.height * MAX_WIDTH / img.width)
                img = img.resize((MAX_WIDTH, h), Image.LANCZOS)
            img.convert("RGB").save(
                os.path.join(OUT_DIR, out_name), "JPEG", quality=JPEG_QUALITY, optimize=True
            )
        except Exception as e:
            print(f"  Bildeprosessering feilet ({e}) -> flyttes til manuell-mappe.")
            shutil.move(src, os.path.join(MANUAL_DIR, name))
            continue

        photos.append({
            "id": f"{ID_PREFIX}-{next_num:03d}",
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

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=1)
    print(f"Oppdatert {JSON_PATH} ({len(photos)} bilder totalt).")


if __name__ == "__main__":
    sys.exit(main())
