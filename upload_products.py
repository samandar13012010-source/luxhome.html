#!/usr/bin/env python3
"""
Homestauz - Mahsulot rasmini Supabasega yuklash
Ishlatish: python3 upload_products.py <rasm_fayli> "<mahsulot_nomi>"
Misol:      python3 upload_products.py sofa.jpg "Divan Milano"
"""

import requests
import sys
import time
import os

SUPABASE_URL = "https://yaprjjishzefecbztdtn.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhcHJqamlzaHplZmVjYnp0ZHRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk1MDgwMTMsImV4cCI6MjA5NTA4NDAxM30"
    ".f4-fsuVLhZXSLYVLjPSLqLYoGZecPrDPI2s84SlXf_g"
)
BUCKET = "poduct-images"
HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}


def upload_image(img_bytes, filename):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}"
    r = requests.post(url, data=img_bytes, timeout=60, headers={
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "image/jpeg",
        "x-upsert":      "true",
    })
    if r.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
    print(f"Storage xatosi: {r.status_code} — {r.text[:300]}")
    return None


def add_product(name, image_url):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/products",
        json={"name": name, "qty": 1, "price": 1, "cost": 1, "image_url": image_url},
        headers=HEADERS,
        timeout=20,
    )
    return r.status_code in (200, 201)


def main():
    if len(sys.argv) < 3:
        print("Ishlatish: python3 upload_products.py <rasm_fayli> \"<nom>\"")
        print("Misol:     python3 upload_products.py sofa.jpg \"Divan Milano\"")
        sys.exit(1)

    image_path = sys.argv[1]
    name       = sys.argv[2].strip()

    if not os.path.isfile(image_path):
        print(f"Fayl topilmadi: {image_path}")
        sys.exit(1)

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    ts       = int(time.time())
    safe     = "".join(c if c.isalnum() or c in "-_" else "_" for c in name[:40])
    filename = f"{ts}_{safe}.jpg"

    print(f"Yuklanmoqda: {name}...", end="", flush=True)

    image_url = upload_image(img_bytes, filename)
    if not image_url:
        sys.exit(1)

    if add_product(name, image_url):
        print(f" OK!\n'{name}' qo'shildi. Narx/sonni saytdan tahrirlang.")
    else:
        print(" Bazaga yozib bo'lmadi!")
        sys.exit(1)


if __name__ == "__main__":
    main()
