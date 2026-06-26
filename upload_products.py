#!/usr/bin/env python3
"""
Homestauz — rasm orqali Telegram kanaldan mahsulot topib Supabasega yuklash.

Ishlatish:
    python3 upload_products.py <reference_rasm.jpg>

Nima qiladi:
  1. Telethon orqali sizning akkauntingiz bilan ulanadi (sessiya keshlanadi).
  2. Private kanaldagi rasmli postlarni indekslaydi (perceptual hash).
  3. Berilgan rasmga eng o'xshash postni topadi.
  4. O'sha postning TO'LIQ sifatli rasmini va NOMINI (caption) oladi.
  5. Supabasega yuklaydi: narx=1, soni=1 (keyin saytdan tahrirlanadi).

Birinchi marta o'rnatish:
    pip install -r requirements.txt
    tg_config.json ga api_id / api_hash yozing (my.telegram.org dan olinadi).
"""

import sys
import os
import io
import json
import time

try:
    import requests
    import imagehash
    from PIL import Image
    from telethon.sync import TelegramClient
    from telethon.tl.types import PeerChannel
except ImportError as e:
    print(f"[xato] Kutubxona topilmadi: {e}")
    print("Avval o'rnating:  pip install -r requirements.txt")
    sys.exit(1)

# ── Sozlamalar ────────────────────────────────────────────────
CHANNEL_ID   = 1899414591           # private kanal (Telethon uchun -100 shart emas)
SUPABASE_URL = "https://yaprjjishzefecbztdtn.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhcHJqamlzaHplZmVjYnp0ZHRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk1MDgwMTMsImV4cCI6MjA5NTA4NDAxM30"
    ".f4-fsuVLhZXSLYVLjPSLqLYoGZecPrDPI2s84SlXf_g"
)
BUCKET          = "poduct-images"
SESSION_NAME    = "homestauz"               # → homestauz.session
CATALOG_FILE    = "channel_catalog.json"
CONFIG_FILE     = "tg_config.json"
PHASH_THRESHOLD = 10                          # Hamming masofa: shundan kichik = ishonchli moslik
TOP_N           = 3                           # noaniq bo'lsa nechta nomzod ko'rsatilsin

SB_HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}
# ─────────────────────────────────────────────────────────────


def load_api_config():
    """api_id / api_hash ni tg_config.json yoki muhit o'zgaruvchisidan oladi."""
    api_id  = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    if api_id and api_hash:
        return int(api_id), api_hash

    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        return int(cfg["api_id"]), cfg["api_hash"]

    print(f"[xato] {CONFIG_FILE} topilmadi.")
    print("https://my.telegram.org → 'API development tools' dan api_id va")
    print("api_hash oling va quyidagicha faylga yozing:")
    print(f'  {{"api_id": 1234567, "api_hash": "abcdef..."}}')
    sys.exit(1)


def load_catalog():
    if os.path.isfile(CATALOG_FILE):
        with open(CATALOG_FILE) as f:
            return json.load(f)
    return {"entries": [], "last_id": 0}


def save_catalog(cat):
    with open(CATALOG_FILE, "w") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1)


def phash_of_bytes(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return str(imagehash.phash(img))


def build_catalog(client, channel):
    """
    Kanaldagi rasmli postlarni indekslaydi. Faqat oxirgi indekslangandan keyingi
    YANGI postlar yuklanadi — keyingi safar tez ishlaydi.
    """
    cat = load_catalog()
    known_ids = {e["id"] for e in cat["entries"]}
    last_id   = cat.get("last_id", 0)

    print(f"  Katalog: {len(cat['entries'])} ta mavjud, yangilarini qidirmoqda...")
    new_count = 0
    max_id    = last_id

    # min_id=last_id → faqat yangi (kattaroq id) postlar
    for msg in client.iter_messages(channel, min_id=last_id):
        if msg.id <= last_id or msg.id in known_ids:
            continue
        if not msg.photo:
            continue
        try:
            # Hashlash uchun kichik thumbnail kifoya (tez)
            buf = io.BytesIO()
            client.download_media(msg, file=buf, thumb=-1)  # eng kichik thumb
            buf.seek(0)
            ph = phash_of_bytes(buf.read())
        except Exception as ex:
            print(f"    [o'tkazildi] post {msg.id}: {ex}")
            continue

        caption = (msg.message or "").strip()
        cat["entries"].append({"id": msg.id, "caption": caption, "phash": ph})
        known_ids.add(msg.id)
        max_id = max(max_id, msg.id)
        new_count += 1
        if new_count % 25 == 0:
            print(f"    ...{new_count} ta yangi post indekslandi")

    cat["last_id"] = max_id
    save_catalog(cat)
    print(f"  Katalog tayyor: +{new_count} yangi, jami {len(cat['entries'])} ta.")
    return cat


def match(ref_path, catalog):
    """Reference rasmga eng yaqin postlarni (Hamming masofa) qaytaradi."""
    with open(ref_path, "rb") as f:
        ref_ph = imagehash.hex_to_hash(phash_of_bytes(f.read()))

    scored = []
    for e in catalog["entries"]:
        try:
            d = ref_ph - imagehash.hex_to_hash(e["phash"])
        except Exception:
            continue
        scored.append((d, e))
    scored.sort(key=lambda x: x[0])
    return scored


def choose(scored):
    """Eng yaqin moslikni tanlaydi; noaniq bo'lsa foydalanuvchidan so'raydi."""
    if not scored:
        print("[xato] Katalog bo'sh — kanalda rasmli post yo'qmi?")
        return None

    best_d, best_e = scored[0]
    if best_d <= PHASH_THRESHOLD:
        nom = best_e["caption"] or "(nomsiz)"
        print(f"  Topildi (masofa={best_d}): \"{nom}\"")
        return best_e

    # Noaniq — eng yaqin nomzodlarni ko'rsatamiz
    print(f"\n  Aniq moslik topilmadi (eng yaqin masofa={best_d}). Nomzodlar:")
    top = scored[:TOP_N]
    for i, (d, e) in enumerate(top, 1):
        nom = e["caption"] or "(nomsiz)"
        print(f"    {i}) masofa={d:<3} — {nom}")
    print("    0) Bekor qilish")
    while True:
        sel = input("  Qaysi biri to'g'ri? [0-{}]: ".format(len(top))).strip()
        if sel == "0":
            return None
        if sel.isdigit() and 1 <= int(sel) <= len(top):
            return top[int(sel) - 1][1]
        print("  Noto'g'ri tanlov.")


def download_best(client, channel, msg_id):
    """Postning eng katta (to'liq sifatli) rasmini bytes sifatida qaytaradi."""
    msg = client.get_messages(channel, ids=msg_id)
    buf = io.BytesIO()
    client.download_media(msg, file=buf)   # thumb berilmasa — eng katta o'lcham
    return buf.getvalue()


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
    print(f"  [xato] storage: {r.status_code} — {r.text[:200]}")
    return None


def add_product(name, image_url):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/products",
        json={"name": name, "qty": 1, "price": 1, "cost": 1, "image_url": image_url},
        headers=SB_HEADERS,
        timeout=20,
    )
    return r.status_code in (200, 201)


def main():
    if len(sys.argv) < 2:
        print("Ishlatish: python3 upload_products.py <reference_rasm.jpg>")
        sys.exit(1)

    ref_path = sys.argv[1]
    if not os.path.isfile(ref_path):
        print(f"[xato] Rasm topilmadi: {ref_path}")
        sys.exit(1)

    api_id, api_hash = load_api_config()

    print("=" * 50)
    print("  Homestauz — kanaldan mahsulot topish")
    print("=" * 50)

    with TelegramClient(SESSION_NAME, api_id, api_hash) as client:
        channel = client.get_entity(PeerChannel(CHANNEL_ID))
        print(f"  Kanal: {getattr(channel, 'title', CHANNEL_ID)}")

        catalog = build_catalog(client, channel)

        print("\n  Reference rasm tahlil qilinmoqda...")
        scored = match(ref_path, catalog)
        chosen = choose(scored)
        if not chosen:
            print("  Bekor qilindi.")
            return

        name = chosen["caption"].strip()
        if not name:
            name = input("  Bu post nomsiz. Mahsulot nomini kiriting: ").strip()
            if not name:
                print("  Nom kiritilmadi — bekor qilindi.")
                return

        print("  Sifatli rasm yuklab olinmoqda...", end="", flush=True)
        img_bytes = download_best(client, channel, chosen["id"])
        print(f" {len(img_bytes)//1024} KB")

    # Supabasega yuklash
    ts       = int(time.time())
    safe     = "".join(c if c.isalnum() or c in "-_" else "_" for c in name[:40])
    filename = f"{ts}_{safe}.jpg"

    print("  Supabasega yuklanmoqda...", end="", flush=True)
    image_url = upload_image(img_bytes, filename)
    if not image_url:
        print(" XATO")
        sys.exit(1)

    if add_product(name, image_url):
        print(" OK")
        print(f"\n  ✓ '{name}' qo'shildi (narx=1, soni=1).")
        print("  Narx va sonini https://homestauz.vercel.app/ dan tahrirlang.")
    else:
        print(" XATO — bazaga yozib bo'lmadi.")
        sys.exit(1)


if __name__ == "__main__":
    main()
