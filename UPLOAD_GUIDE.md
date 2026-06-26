# Mahsulot yuklash skripti — qo'llanma

`upload_products.py` — siz bergan rasmga qarab Telegram kanaldan tovarni topadi,
uning **yaxshi sifatli rasmini** va **nomini** olib Supabasega yuklaydi
(narx=1, soni=1 — keyin saytdan tahrirlaysiz).

## 1. O'rnatish (bir martalik)

```bash
pip install -r requirements.txt
```

## 2. Telegram API kaliti (bir martalik)

1. https://my.telegram.org ga kiring (telefon raqamingiz bilan).
2. **API development tools** → yangi ilova yarating.
3. `api_id` va `api_hash` ni oling.
4. `tg_config.example.json` dan nusxa olib `tg_config.json` yarating va
   qiymatlarni yozing:

```json
{
  "api_id": 1234567,
  "api_hash": "0123456789abcdef..."
}
```

> `tg_config.json` va `*.session` fayllari maxfiy — ular `.gitignore` da,
> hech qachon GitHub'ga yuklanmaydi.

## 3. Ishlatish

```bash
python3 upload_products.py rasm.jpg
```

- **Birinchi marta**: Telegram telefon raqami + kod so'raydi (login). Keyin
  `homestauz.session` keshlanadi — qayta so'ramaydi.
- Skript kanalni indekslaydi (birinchi marta sekinroq, keyin tez).
- Rasmga eng o'xshash postni topadi:
  - Aniq topsa → avtomatik yuklaydi.
  - Noaniq bo'lsa → eng yaqin 3 nomzodni ko'rsatib tanlatadi.
- Topilgan tovar Supabasega tushadi.

## 4. Tekshirish

https://homestauz.vercel.app/ ni oching — yangi mahsulot (to'g'ri nom + sifatli
rasm, narx=1, soni=1) ko'rinadi. Narx va sonini saytdan tahrirlang.

## Eslatma

Bu skript faqat **sizning kompyuteringizda** ishlaydi (bulut serveri
Telegram/Supabasega ulanolmaydi).
