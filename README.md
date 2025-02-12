# WebSocket Chat

Bu loyiha **Django + WebSocket** asosida qurilgan real vaqt chat tizimidir. Foydalanuvchilar xabar yuborishi, fayllarni ulashishi va xavfsiz muloqot qilishi mumkin.

## 🚀 Xususiyatlar

- **Real vaqt chat** – WebSocket orqali xabar almashish.
- **Fayllarni yuklash** – Rasm, video, audio va hujjatlarni yuklash imkoniyati.
- **Shifrlash** – Fayllar foydalanuvchining paroli orqali shifrlanadi.
- **Online status** – Redis yordamida foydalanuvchilarning online/offline holati kuzatiladi.
- **Xabarning yetkazilganligi** – Xabar yetib borgan yoki bormaganligi tekshiriladi.
- **REST API** – Frontend bilan integratsiya qilish uchun API qo‘llab-quvvatlanadi.

## 🛠 O‘rnatish

### 1. Loyihani yuklab olish
```bash
git clone https://github.com/rozievich/chatbot.git
cd chatbot
```

### 2. Virtual muhit yaratish va kutubxonalarni o‘rnatish
```bash
python -m venv venv
source venv/bin/activate  # Windows uchun: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Redis serverini ishga tushirish
Loyiha Redis-dan foydalanadi, shuning uchun uni ishga tushirish kerak:
```bash
redis-server
```

### 4. Ma'lumotlar bazasini yaratish
```bash
python manage.py migrate
python manage.py createsuperuser  # Superuser yaratish
```

### 5. Serverni ishga tushirish
```bash
python manage.py runserver
```

## 🔌 API Endpoints

| Endpoint               | Metod | Tavsif |
|------------------------|-------|--------|
| `/ws/chat/`           | WebSocket | Chatga ulanish |
| `/api/messages/`      | GET    | Barcha xabarlarni olish |
| `/api/messages/send/` | POST   | Xabar yuborish |
| `/api/files/upload/`  | POST   | Fayl yuklash |
| `/api/users/online/`  | GET    | Online foydalanuvchilar |

## 🔐 Xavfsizlik

- **Shifrlash**: Barcha yuklangan fayllar foydalanuvchining paroli asosida shifrlanadi.
- **Secret Key ishlatilmaydi**: Har bir foydalanuvchi o‘z parolini shifrlash kaliti sifatida ishlatadi.
- **Server hack bo‘lsa ham ma’lumotlar ochiq qolmaydi.**

## 📌 Kelajakdagi rejalari

- Frontend integratsiyasi
- Gruppaviy chat qo‘shish
- Chat statistikasi va monitoring

## 🤝 Hissa qo‘shish
Pull requestlar va takliflarga ochiqmiz! 😊

## 📜 Litsenziya
MIT License

---

Agar loyiha yoqsa, ⭐ berishni unutmang! 😎🔥
