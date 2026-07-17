#!/usr/bin/env python3
"""
bulk_unpack.py — pakker ut release-zip(er) til foto-pipelinens innbokser.

Bruk: python scripts/bulk_unpack.py <mappe-med-zip-filer>

Forventet zip-struktur: én undermappe per elv i roten av zip-en:
    audna/IMG_001.jpg
    mandalselva/IMG_002.jpg
    ...
Gyldige elvenavn (små bokstaver): audna, lygna, mandalselva, otra, sygna.
Hvis zip-en har ett enkelt omslagsnivå (typisk Windows «Send til komprimert
mappe»), hoppes det over automatisk. Ukjente mapper og løse filer i roten
listes som advarsler og hoppes over.
"""
import os
import sys
import shutil
import zipfile
import tempfile

RIVERS = ["audna", "lygna", "mandalselva", "otra", "sygna"]
IMG_EXT = (".jpg", ".jpeg", ".png")
INBOX = "bilder/innboks"


def find_river_root(root):
    """Returner mappen som inneholder elve-undermappene (hopp over omslag)."""
    for _ in range(3):
        entries = [e for e in os.listdir(root) if not e.startswith((".", "__MACOSX"))]
        dirs = [e for e in entries if os.path.isdir(os.path.join(root, e))]
        if any(d.lower() in RIVERS for d in dirs):
            return root
        if len(dirs) == 1 and not any(
            e.lower().endswith(IMG_EXT) for e in entries
        ):
            root = os.path.join(root, dirs[0])
            continue
        return root
    return root


def main():
    if len(sys.argv) != 2:
        sys.exit("Bruk: bulk_unpack.py <mappe-med-zip-filer>")
    src_dir = sys.argv[1]
    zips = [f for f in os.listdir(src_dir) if f.lower().endswith(".zip")]
    if not zips:
        sys.exit(f"Ingen zip-filer funnet i {src_dir}")

    total = {}
    advarsler = []

    for zname in sorted(zips):
        zpath = os.path.join(src_dir, zname)
        print(f"=== Pakker ut {zname} ===")
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(zpath) as zf:
                zf.extractall(tmp)
            root = find_river_root(tmp)

            for entry in sorted(os.listdir(root)):
                if entry.startswith((".", "__MACOSX")):
                    continue
                full = os.path.join(root, entry)
                if os.path.isdir(full):
                    key = entry.lower()
                    if key not in RIVERS:
                        advarsler.append(f"Ukjent mappe hoppet over: {entry}/")
                        continue
                    dest = os.path.join(INBOX, key)
                    os.makedirs(dest, exist_ok=True)
                    for fn in sorted(os.listdir(full)):
                        if not fn.lower().endswith(IMG_EXT):
                            advarsler.append(f"Ikke-bildefil hoppet over: {entry}/{fn}")
                            continue
                        out = os.path.join(dest, fn)
                        n = 2
                        base, ext = os.path.splitext(fn)
                        while os.path.exists(out):
                            out = os.path.join(dest, f"{base}_{n}{ext}")
                            n += 1
                        shutil.copy2(os.path.join(full, fn), out)
                        total[key] = total.get(key, 0) + 1
                else:
                    advarsler.append(f"Løs fil i roten hoppet over: {entry}")

    print("\n=== Utpakking ferdig ===")
    for k in RIVERS:
        if k in total:
            print(f"  {k}: {total[k]} bilde(r) til {INBOX}/{k}/")
    for a in advarsler:
        print(f"  ADVARSEL: {a}")
    if not total:
        sys.exit("Ingen bilder havnet i noen innboks - sjekk zip-strukturen "
                 "(undermapper må hete audna/lygna/mandalselva/otra/sygna).")


if __name__ == "__main__":
    main()
