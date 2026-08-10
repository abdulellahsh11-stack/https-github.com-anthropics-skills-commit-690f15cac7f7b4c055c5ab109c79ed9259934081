# منصة ضيوف (Duyuf PMS)
### نظام إدارة الفنادق المتكامل | Integrated Hotel Property Management System
**الموقع:** [dheuof.com](https://dheuof.com)

---

## نظرة عامة | Overview

**منصة ضيوف** هي نظام إدارة فندقية متكامل (PMS) مصمم للسوق السعودي، يدعم اللغة العربية بالكامل واتجاه RTL، ويتكامل مع بوابة الدفع **Moyasar** ونظام **الفواتير الإلكترونية (ZATCA)**.

**Duyuf PMS** is a full-featured hotel management system built for the Saudi market, with complete Arabic (RTL) support, Moyasar payment integration, and ZATCA e-invoicing compliance.

---

## المميزات الرئيسية | Key Features

| الميزة | الوصف |
|--------|--------|
| إدارة الحجوزات | محرك حجز متكامل مع تقويم الغرف |
| الفوترة الإلكترونية | متوافق مع ZATCA (VAT 15% + رسوم سياحة 2.5%) |
| إدارة الصلاحيات | نظام RBAC متعدد المستويات (مدير، موظف استقبال، خادمة) |
| Channel Manager | تكامل مع Booking.com و Airbnb و Expedia |
| بوابة الدفع | Moyasar (بطاقة، Apple Pay، STC Pay) |
| تقارير ومؤشرات | لوحة تحكم مع KPIs وتقارير الإيرادات |
| نقطة البيع | إدارة المطعم والمنتجعات (F&B) |
| المخزون | إدارة الغرف والأصول والصيانة |

---

## البنية التقنية | Tech Stack

```
Frontend:  HTML / CSS / JavaScript (RTL Support)
Backend:   Python (FastAPI / Django)
Database:  PostgreSQL
Cache:     Redis
Auth:      JWT + RBAC
Payments:  Moyasar API
Tax:       ZATCA e-Invoicing
Hosting:   dheuof.com
```

---

## المستودعات | Repositories

| المستودع | الوصف | النوع |
|----------|--------|-------|
| `hotelsystem` | الواجهة الأمامية (Frontend) | عام |
| `hotel-server` | الخادم الخلفي (Backend API) | خاص |
| `HotelSystem1` | نسخة Python الأساسية | خاص |
| `hotel-data-backup` | نسخ احتياطية لقاعدة البيانات | خاص |

---

## توثيق API | API Documentation

### المصادقة | Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**الاستجابة:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "name": "اسم المستخدم",
    "role": "admin | receptionist | housekeeper"
  }
}
```

---

### الحجوزات | Reservations

#### قائمة الحجوزات
```http
GET /api/v1/reservations
Authorization: Bearer {token}
Query Params:
  - status: pending | confirmed | checked_in | checked_out | cancelled
  - from_date: YYYY-MM-DD
  - to_date: YYYY-MM-DD
  - page: int (default: 1)
  - per_page: int (default: 20)
```

#### إنشاء حجز جديد
```http
POST /api/v1/reservations
Authorization: Bearer {token}
Content-Type: application/json

{
  "guest_id": "uuid",
  "room_id": "uuid",
  "check_in": "2026-08-15",
  "check_out": "2026-08-20",
  "adults": 2,
  "children": 0,
  "special_requests": "طابق عالٍ - مطل على البحر",
  "payment_method": "card | apple_pay | stc_pay"
}
```

**الاستجابة:**
```json
{
  "reservation_id": "uuid",
  "confirmation_number": "DYF-2026-001234",
  "status": "confirmed",
  "total_amount": 2500.00,
  "vat_amount": 375.00,
  "tourism_fee": 62.50,
  "grand_total": 2937.50,
  "currency": "SAR"
}
```

#### تسجيل الوصول (Check-In)
```http
PATCH /api/v1/reservations/{reservation_id}/check-in
Authorization: Bearer {token}
```

#### تسجيل المغادرة (Check-Out)
```http
PATCH /api/v1/reservations/{reservation_id}/check-out
Authorization: Bearer {token}
```

---

### الغرف | Rooms

#### قائمة الغرف المتاحة
```http
GET /api/v1/rooms/available
Authorization: Bearer {token}
Query Params:
  - from_date: YYYY-MM-DD
  - to_date: YYYY-MM-DD
  - type: single | double | suite | deluxe
  - floor: int
```

**الاستجابة:**
```json
{
  "rooms": [
    {
      "id": "uuid",
      "number": "101",
      "type": "double",
      "floor": 1,
      "status": "available",
      "price_per_night": 500.00,
      "amenities": ["wifi", "ac", "tv", "minibar"],
      "max_occupancy": 2
    }
  ],
  "total": 45,
  "available": 12
}
```

#### تحديث حالة الغرفة
```http
PATCH /api/v1/rooms/{room_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "available | occupied | maintenance | cleaning",
  "notes": "ملاحظات اختيارية"
}
```

---

### الضيوف | Guests

#### إضافة ضيف جديد
```http
POST /api/v1/guests
Authorization: Bearer {token}
Content-Type: application/json

{
  "name_ar": "عبدالله محمد",
  "name_en": "Abdullah Mohammed",
  "id_type": "national_id | passport | iqama",
  "id_number": "1234567890",
  "nationality": "SA",
  "phone": "+966501234567",
  "email": "guest@example.com",
  "date_of_birth": "1990-01-01"
}
```

---

### الفواتير والمدفوعات | Invoices & Payments

#### إنشاء فاتورة إلكترونية (ZATCA)
```http
POST /api/v1/invoices
Authorization: Bearer {token}
Content-Type: application/json

{
  "reservation_id": "uuid",
  "items": [
    {
      "description": "إقامة - 5 ليالٍ",
      "quantity": 5,
      "unit_price": 500.00,
      "vat_rate": 0.15
    },
    {
      "description": "رسوم سياحة",
      "quantity": 5,
      "unit_price": 12.50,
      "vat_rate": 0.00
    }
  ]
}
```

**الاستجابة:**
```json
{
  "invoice_id": "uuid",
  "invoice_number": "INV-2026-001234",
  "zatca_uuid": "8ade4726-...",
  "qr_code": "base64_encoded_qr",
  "subtotal": 2500.00,
  "vat_amount": 375.00,
  "tourism_fee": 62.50,
  "total": 2937.50,
  "status": "issued",
  "zatca_status": "reported | cleared"
}
```

#### معالجة الدفع عبر Moyasar
```http
POST /api/v1/payments/moyasar
Authorization: Bearer {token}
Content-Type: application/json

{
  "invoice_id": "uuid",
  "amount": 293750,
  "currency": "SAR",
  "source": {
    "type": "creditcard | applepay | stcpay",
    "token": "moyasar_payment_token"
  },
  "callback_url": "https://dheuof.com/payments/callback"
}
```

---

### التقارير | Reports

#### تقرير الإيرادات
```http
GET /api/v1/reports/revenue
Authorization: Bearer {token}
Query Params:
  - period: daily | weekly | monthly | yearly
  - from_date: YYYY-MM-DD
  - to_date: YYYY-MM-DD
```

**الاستجابة:**
```json
{
  "period": "monthly",
  "total_revenue": 125000.00,
  "total_vat": 18750.00,
  "total_bookings": 87,
  "occupancy_rate": 0.78,
  "average_daily_rate": 520.00,
  "revpar": 405.60,
  "breakdown": {
    "rooms": 100000.00,
    "restaurant": 15000.00,
    "services": 10000.00
  }
}
```

---

## نظام الصلاحيات | RBAC Permissions

| الصلاحية | مدير | استقبال | خادمة |
|----------|------|---------|-------|
| عرض الحجوزات | ✅ | ✅ | ❌ |
| إنشاء/تعديل حجز | ✅ | ✅ | ❌ |
| إلغاء حجز | ✅ | ❌ | ❌ |
| تسجيل وصول/مغادرة | ✅ | ✅ | ❌ |
| إدارة الغرف | ✅ | ✅ | ✅ |
| إصدار فواتير | ✅ | ✅ | ❌ |
| التقارير المالية | ✅ | ❌ | ❌ |
| إدارة المستخدمين | ✅ | ❌ | ❌ |

---

## اختبار الأداء | Performance Testing

اختبارات الأداء تستخدم **k6** لمحاكاة أعداد المستخدمين المتزامنين على `dheuof.com`.

```bash
# تشغيل اختبار الأداء
k6 run load-test.js

# أهداف الأداء
VUs (مستخدمون متزامنون): 100
المدة: 5 دقائق
معدل الطلبات: < 500ms p95
معدل الأخطاء: < 1%
```

---

## التثبيت والإعداد | Setup

### المتطلبات
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (للواجهة الأمامية)

### متغيرات البيئة
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/duyuf
REDIS_URL=redis://localhost:6379
MOYASAR_API_KEY=your_moyasar_key
ZATCA_CERT=your_zatca_certificate
JWT_SECRET=your_jwt_secret
HOTEL_NAME=اسم الفندق
HOTEL_VAT_NUMBER=رقم_ضريبي
```

### التشغيل
```bash
# Backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
npm install
npm run dev
```

---

## الإصدارات | Changelog

| الإصدار | التاريخ | التغييرات |
|---------|---------|----------|
| v1.0.0 | مايو 2026 | الإطلاق الأولي |
| v1.1.0 | يونيو 2026 | إضافة Channel Manager |
| v1.2.0 | أغسطس 2026 | تحسينات الأداء + اختبارات k6 |

---

## التراخيص | License

© 2026 منصة ضيوف — جميع الحقوق محفوظة  
تطوير: [abdulellahsh11-stack](https://github.com/abdulellahsh11-stack)
