# BYD Salon

BYD avtosaloni uchun veb-sayt: model katalogi, avtomobil sahifalari, kredit kalkulyatori, test-drayv va murojaat arizalari, admin panel va REST API.

**Stek:** Python 3.12+, Django 5.2, Django REST Framework, SQLite / PostgreSQL, vanilla JS + CSS (build bosqichisiz).

## Imkoniyatlar

- **Katalog** — kuzov turi, dvigatel (EV / DM-i gibrid), narx oralig'i, qidiruv bo'yicha filtr; saralash va sahifalash.
- **Avtomobil sahifasi** — texnik xususiyatlar jadvali, galereya, rang tanlash, o'xshash modellar.
- **Kredit kalkulyatori** — annuitet bo'yicha oylik to'lov (USD va so'm), natija bilan birga ariza yuborish.
- **Arizalar** — test-drayv (sana/vaqt tanlash) va murojaatlar (konsultatsiya, kredit, trade-in, servis). O'zbek telefon raqami normallashtiriladi (`+998XXXXXXXXX`), spamdan honeypot himoyasi bor.
- **Telegram xabarnoma** — yangi ariza tushganda menejerlarga xabar (ixtiyoriy).
- **Admin panel** — modellar, ranglar, galereya, arizalar holati (Yangi → Jarayonda → Yakunlangan), salon ma'lumotlari (telefon, manzil, USD kursi, kredit foizi).
- **REST API** — mobil ilova yoki boshqa frontend uchun.
- Rasm yuklanmagan modellar uchun kuzov turiga mos SVG siluet avtomatik chiziladi.

## Ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py seed_cars        # 8 ta demo model
python manage.py createsuperuser
python manage.py runserver
```

- Sayt: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/

Testlar: `python manage.py test apps`

## Loyiha tuzilishi

```
config/            sozlamalar, asosiy URL'lar
apps/core/         bosh sahifa, "Biz haqimizda", SalonInfo (singleton), template filtrlar
apps/cars/         BodyType, Car, CarColor, CarImage; katalog va batafsil sahifa; seed_cars buyrug'i
apps/leads/        TestDriveRequest, ContactRequest; formalar, Telegram signallari
apps/api/          DRF serializer va viewset'lar
templates/         Django shablonlari (partials/ — qayta ishlatiladigan bloklar)
static/            main.css, main.js
```

## API

| Metod | URL | Tavsif |
|---|---|---|
| GET | `/api/cars/` | Katalog. Filtrlar: `body`, `powertrain`, `price_min`, `price_max`, `q` |
| GET | `/api/cars/<slug>/` | Model: barcha xususiyatlar, ranglar, galereya |
| GET | `/api/body-types/` | Kuzov turlari |
| POST | `/api/test-drive/` | Test-drayv arizasi (soatiga 10 ta / IP) |

```bash
curl -X POST http://127.0.0.1:8000/api/test-drive/ \
  -H "Content-Type: application/json" \
  -d '{"car": "byd-seal", "full_name": "Aziz", "phone": "90 123 45 67",
       "preferred_date": "2026-11-10", "time_slot": "evening"}'
```

## Telegram xabarnoma

1. [@BotFather](https://t.me/BotFather) orqali bot yarating va tokenni oling.
2. Botni menejerlar guruhiga qo'shing va guruh `chat_id` sini aniqlang.
3. `.env` ga `TELEGRAM_BOT_TOKEN` va `TELEGRAM_CHAT_ID` ni yozing.

## Production

- `.env`: `DJANGO_DEBUG=False`, kuchli `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`.
- PostgreSQL uchun `psycopg[binary]` o'rnating va `POSTGRES_*` o'zgaruvchilarini to'ldiring.
- `python manage.py collectstatic`, so'ng `gunicorn config.wsgi` + Nginx (`/static/` va `/media/` ni Nginx beradi).

## Eslatma

`seed_cars` dagi narxlar namunaviy, xususiyatlar esa ochiq manbalardagi taxminiy qiymatlar. "Biz haqimizda" sahifasidagi raqamlar, kafolat shartlari va kontaktlar ham namuna — ishga tushirishdan oldin salonning haqiqiy ma'lumotlari bilan almashtiring.
