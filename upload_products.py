#!/usr/bin/env python3
"""
Homestauz - Telegram kanaldan mahsulotlarni Supabasega yuklash
Ishlatish: python3 upload_products.py
"""

import requests
import json
import time
import sys

BOT_TOKEN    = "8782087228:AAFZQAHvPJ-TWwFzu_rPW0evcguhF-HeqLE"
CHANNEL_ID   = -1001899414591
SUPABASE_URL = "https://yaprjjishzefecbztdtn.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhcHJqamlzaHplZmVjYnp0ZHRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk1MDgwMTMsImV4cCI6MjA5NTA4NDAxM30"
    ".f4-fsuVLhZXSLYVLjPSLqLYoGZecPrDPI2s84SlXf_g"
)
BUCKET = "poduct-images"
TG     = f"https://api.telegram.org/bot{BOT_TOKEN}"
SB_HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}


def tg(method, **params):
    r = requests.get(f"{TG}/{method}", params=params, timeout=30)
    return r.json()


def get_file_url(file_id):
    d = tg("getFile", file_id=file_id)
    if d.get("ok"):
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{d['result']['file_path']}"
    return None


def upload_image(img_bytes, filename):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}"
    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "image/jpeg",
        "x-upsert":      "true",
    }
    r = requests.post(url, data=img_bytes, headers=headers, timeout=60)
    if r.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
    print(f"  [xato] storage: {r.status_code} {r.text[:200]}")
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
    print("=" * 48)
    print("  Homestauz — Mahsulot yuklash")
    print("=" * 48)

    # Bot tekshirish
    me = tg("getMe")
    if not me.get("ok"):
        print("[xato] Bot token noto'g'ri!")
        sys.exit(1)
    print(f"  Bot: @{me['result']['username']}")

    # Kanaldan postlar olish
    print("  Kanaldan postlar olinmoqda...")
    updates = tg("getUpdates", limit=100, allowed_updates=json.dumps(["channel_post"]))
    if not updates.get("ok"):
        print(f"  [xato] {updates}")
        sys.exit(1)

    posts = []
    last_id = 0
    for upd in updates.get("result", []):
        last_id = max(last_id, upd["update_id"])
        cp = upd.get("channel_post", {})
        if cp.get("photo") and cp.get("chat", {}).get("id") == CHANNEL_ID:
            posts.append(cp)

    # Offset yangilash (qayta yuklamaslik)
    if last_id:
        tg("getUpdates", offset=last_id + 1, limit=1)

    if not posts:
        print("  Yangi rasm topilmadi.")
        print("  (Bot kanalda admin ekanini va yangi post borligini tekshiring)")
        sys.exit(0)

    print(f"  {len(posts)} ta yangi post topildi\n")

    ok = 0
    for i, post in enumerate(posts, 1):
        # Bitta (eng yaxshi) rasmni olish
        photo   = max(post["photo"], key=lambda p: p.get("file_size", 0))
        caption = post.get("caption", "").strip()
        name    = caption if caption else f"Mahsulot {i}"

        print(f"  [{i}/{len(posts)}] {name}")

        file_url = get_file_url(photo["file_id"])
        if not file_url:
            print("    → fayl URL topilmadi, o'tkazildi")
            continue

        r = requests.get(file_url, timeout=60)
        if r.status_code != 200:
            print(f"    → rasm yuklanmadi ({r.status_code})")
            continue

        ts       = int(time.time())
        safe     = "".join(c if c.isalnum() or c in "-_" else "_" for c in name[:40])
        filename = f"{ts}_{safe}.jpg"

        image_url = upload_image(r.content, filename)
        if not image_url:
            print("    → storage xatosi")
            continue

        if add_product(name, image_url):
            print(f"    → qo'shildi! (narx=1, soni=1 — saytdan tahrirlang)")
            ok += 1
        else:
            print("    → bazaga yozib bo'lmadi")

    print(f"\n  Natija: {ok}/{len(posts)} ta mahsulot yuklandi")
    print("  Narx va sonini https://homestauz.vercel.app/ dan tahrirlang")


if __name__ == "__main__":
    main()
