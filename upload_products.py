#!/usr/bin/env python3
"""
Homestauz - Telegram kanaldan mahsulotlarni Supabasega yuklash
Ishlatish: python3 upload_products.py
"""

import requests
import json
import time
import sys
import os
from io import BytesIO

# ── Sozlamalar ────────────────────────────────────────────────
BOT_TOKEN    = "8782087228:AAFZQAHvPJ-TWwFzu_rPW0evcguhF-HeqLE"
CHANNEL_ID   = -1001899414591        # private kanal
SUPABASE_URL = "https://yaprjjishzefecbztdtn.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhcHJqamlzaHplZmVjYnp0ZHRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk1MDgwMTMsImV4cCI6MjA5NTA4NDAxM30"
    ".f4-fsuVLhZXSLYVLjPSLqLYoGZecPrDPI2s84SlXf_g"
)
BUCKET       = "poduct-images"
TG           = f"https://api.telegram.org/bot{BOT_TOKEN}"
SB_HEADERS   = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}
# ─────────────────────────────────────────────────────────────


def tg(method, **params):
    r = requests.get(f"{TG}/{method}", params=params, timeout=30)
    return r.json()


def get_file_url(file_id):
    d = tg("getFile", file_id=file_id)
    if d.get("ok"):
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{d['result']['file_path']}"
    return None


def best_photo(photos):
    """Eng katta o'lchamli rasmni qaytaradi."""
    return max(photos, key=lambda p: p.get("file_size", 0))


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


def add_product(name, qty, price, cost, image_url):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/products",
        json={"name": name, "qty": qty, "price": price, "cost": cost, "image_url": image_url},
        headers=SB_HEADERS,
        timeout=20,
    )
    return r.status_code in (200, 201)


def ask(prompt, default=None, cast=str):
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    if not val and default is not None:
        return default
    try:
        return cast(val)
    except ValueError:
        print("  Noto'g'ri qiymat, qayta kiriting.")
        return ask(prompt, default, cast)


def process_post(post, idx, total):
    photos = post.get("photo")
    if not photos:
        return

    caption = post.get("caption", "").strip()
    print(f"\n{'─'*48}")
    print(f"  Rasm {idx}/{total}")
    if caption:
        print(f"  Caption: {caption}")

    # Rasmni yuklab olish
    file_url = get_file_url(best_photo(photos)["file_id"])
    if not file_url:
        print("  [xato] fayl URLi topilmadi, o'tkazildi")
        return

    r = requests.get(file_url, timeout=60)
    if r.status_code != 200:
        print(f"  [xato] rasm yuklanmadi ({r.status_code})")
        return

    img_bytes = r.content
    print(f"  Rasm hajmi: {len(img_bytes)//1024} KB")

    # Ma'lumot kiritish
    default_name = caption if caption else None
    name = ask("Mahsulot nomi", default=default_name)
    if not name:
        print("  Nom kiritilmadi — o'tkazildi")
        return

    qty   = ask("Miqdori (dona)", default=0,  cast=int)
    price = ask("Sotuv narxi (so'm)", default=0, cast=int)
    cost  = ask("Xarid narxi (so'm)", default=0, cast=int)

    # Supabasega yuklash
    ts       = int(time.time())
    safe     = "".join(c if c.isalnum() or c in "-_" else "_" for c in name[:30])
    filename = f"{ts}_{safe}.jpg"

    print("  Rasm yuklanmoqda...", end="", flush=True)
    image_url = upload_image(img_bytes, filename)
    if not image_url:
        print(" XATO")
        return
    print(" OK")

    print("  Bazaga qo'shilmoqda...", end="", flush=True)
    if add_product(name, qty, price, cost, image_url):
        print(f" OK  →  '{name}' qo'shildi!")
    else:
        print(" XATO — bazaga yozib bo'lmadi")


def fetch_channel_posts():
    """
    Bot channel_post updatelarini oladi.
    Bot kanalda admin bo'lsa yangi postlar keladi.
    Eski postlarni olish uchun bot oldin /start qilingan bo'lishi kerak.
    """
    updates = tg("getUpdates", limit=100, allowed_updates=json.dumps(["channel_post"]))
    if not updates.get("ok"):
        return []

    posts = []
    last_id = 0
    for upd in updates.get("result", []):
        last_id = max(last_id, upd["update_id"])
        cp = upd.get("channel_post", {})
        chat_id = cp.get("chat", {}).get("id", 0)
        if cp.get("photo") and chat_id == CHANNEL_ID:
            posts.append(cp)

    # Offset yangilash (qayta yuklamaslik uchun)
    if last_id:
        tg("getUpdates", offset=last_id + 1, limit=1)

    return posts


def main():
    print("=" * 48)
    print("  Homestauz — Mahsulot yuklash vositasi")
    print("=" * 48)

    # Bot tekshirish
    me = tg("getMe")
    if not me.get("ok"):
        print("[xato] Bot token noto'g'ri!")
        sys.exit(1)
    print(f"  Bot: {me['result']['first_name']} (@{me['result']['username']})")

    # Supabase tekshirish
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/products?select=id&limit=1",
        headers=SB_HEADERS, timeout=10
    )
    if r.status_code != 200:
        print(f"[xato] Supabase ulanmadi: {r.status_code}")
        sys.exit(1)
    print("  Supabase: ulandi")

    while True:
        print("\n" + "=" * 48)
        print("  1) Kanaldan yangi postlarni yuklash")
        print("  2) Lokal rasm fayli yuklash")
        print("  3) Rasm URL dan yuklash")
        print("  0) Chiqish")
        choice = input("\n  Tanlov: ").strip()

        if choice == "0":
            print("  Xayr!")
            break

        elif choice == "1":
            print("\n  Kanaldan postlar olinmoqda...")
            posts = fetch_channel_posts()
            if not posts:
                print("  Yangi rasm topilmadi.")
                print("  (Bot kanalda admin ekanligini va yangi postlar borligini tekshiring)")
            else:
                print(f"  {len(posts)} ta yangi rasm topildi!")
                for i, post in enumerate(posts, 1):
                    process_post(post, i, len(posts))

        elif choice == "2":
            path = input("  Fayl yo'li (masalan: /home/user/sofa.jpg): ").strip()
            if not os.path.isfile(path):
                print("  Fayl topilmadi!")
                continue
            with open(path, "rb") as f:
                img_bytes = f.read()

            name  = ask("Mahsulot nomi")
            qty   = ask("Miqdori (dona)", default=0, cast=int)
            price = ask("Sotuv narxi (so'm)", default=0, cast=int)
            cost  = ask("Xarid narxi (so'm)", default=0, cast=int)

            ts       = int(time.time())
            safe     = "".join(c if c.isalnum() or c in "-_" else "_" for c in name[:30])
            filename = f"{ts}_{safe}.jpg"

            print("  Yuklanmoqda...", end="", flush=True)
            image_url = upload_image(img_bytes, filename)
            if image_url and add_product(name, qty, price, cost, image_url):
                print(f" OK  →  '{name}' qo'shildi!")
            else:
                print(" XATO")

        elif choice == "3":
            url   = input("  Rasm URL: ").strip()
            r     = requests.get(url, timeout=30)
            if r.status_code != 200:
                print("  URL dan rasm yuklab bo'lmadi!")
                continue
            img_bytes = r.content

            name  = ask("Mahsulot nomi")
            qty   = ask("Miqdori (dona)", default=0, cast=int)
            price = ask("Sotuv narxi (so'm)", default=0, cast=int)
            cost  = ask("Xarid narxi (so'm)", default=0, cast=int)

            ts       = int(time.time())
            safe     = "".join(c if c.isalnum() or c in "-_" else "_" for c in name[:30])
            filename = f"{ts}_{safe}.jpg"

            print("  Yuklanmoqda...", end="", flush=True)
            image_url = upload_image(img_bytes, filename)
            if image_url and add_product(name, qty, price, cost, image_url):
                print(f" OK  →  '{name}' qo'shildi!")
            else:
                print(" XATO")

        else:
            print("  Noto'g'ri tanlov!")


if __name__ == "__main__":
    main()
