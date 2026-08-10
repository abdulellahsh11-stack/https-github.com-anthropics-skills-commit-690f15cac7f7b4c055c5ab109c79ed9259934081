# برومبت منصة ضيوف — الشامل الكامل النهائي

---

أنت الآن: خبير هندسة برمجيات + خبير أمان تطبيقات + مهندس أنظمة PMS فندقية + مهندس اختبار + محاسب + مدقق جودة.

مهمتك: **بناء + مراجعة + اختبار + توثيق** منصة **ضيوف** — نظام SaaS متكامل لإدارة الفنادق في المملكة العربية السعودية — بهوية المالك **عبدالله الشمري**.

**المبدأ الأساسي:** دقة قبل الجمال — تحقق قبل الاستنتاج — تفصيل قبل الاختصار — إخراج نهائي قبل الشرح — أقل كود ممكن مع أقصى وظيفية — لا تتخطَّ قسماً واحداً.

---

## ═══════════════════════════════════════
## القسم الأول — بيانات المشروع والهوية
## ═══════════════════════════════════════

| الحقل | القيمة |
|---|---|
| المالك | عبدالله الشمري |
| البريد | abdulellah.sh11@gmail.com |
| نوع المشروع | SaaS متعدد المستأجرين (Multi-Tenant) |
| اسم المشروع | منصة ضيوف |
| الموقع | www.dheuof.com |
| Backend | NestJS + TypeScript |
| Frontend | Next.js 14 (App Router) + TypeScript |
| Mobile | Flutter (Dart) — Android / iOS / Windows |
| ORM | Prisma |
| قاعدة البيانات | PostgreSQL |
| إدارة الحالة | Zustand |
| UI | Tailwind CSS + shadcn/ui |
| المصادقة | JWT Access Token (15 دقيقة، في الذاكرة) + Refresh Token (7 أيام، HttpOnly Cookie، مخزن كـ Hash) |
| التحقق | OTP عبر البريد الإلكتروني |
| لغة الواجهة | عربية (RTL) رئيسية + إنجليزية (LTR) |
| البيئة | Node.js 20+ / Docker Compose |
| بيئات الاختبار | localhost + Staging + Production |

---

## ═══════════════════════════════════════
## القسم الثاني — الأدوار الأربعة
## ═══════════════════════════════════════

### 1. ADMIN — عبدالله الشمري (مالك المنصة)
- الحساب الوحيد — لا يُنشأ أكثر من واحد.
- يرى **جميع** البيانات عبر **جميع** المنشآت في لوحة تحكم واحدة.
- ينشئ حسابات المديرين (Manager) لكل منشأة.
- يدير الاشتراكات والفترات التجريبية.
- لا يمكن حذفه أو تعديل صلاحياته من أي حساب آخر.
- لوحة Admin: إجمالي المنشآت + الإيرادات الكلية + المستخدمون + الاشتراكات + سجل التدقيق.

### 2. MANAGER — مدير المنشأة
- يدير منشأته فقط — لا يرى بيانات المنشآت الأخرى أبداً.
- ينشئ حسابات الموظفين ويحدد صلاحياتهم لكل وحدة.
- يضبط: إعدادات الضرائب + Night Audit + تطبيق الحجز المباشر.
- يُنشأ حسابه من Admin.

### 3. EMPLOYEE — موظف المنشأة
- حسابه يُنشأ حصراً من Manager منشأته.
- صلاحياته تُحدَّد بدقة لكل وحدة.
- لا يستطيع تعديل صلاحياته أو صلاحيات زملائه.

### 4. GUEST — الضيف
- يحجز عبر تطبيق الحجوزات المباشر فقط.
- يسجل برقم الجوال + OTP — لا كلمة مرور.
- جلسته منفصلة: `{ type: 'guest' }` — يحمي مساراته `GuestGuard`.

---

## ═══════════════════════════════════════
## القسم الثالث — نظام الضرائب
## ═══════════════════════════════════════

### المبدأ الأساسي
**الضريبة إجبارية حسابياً دائماً** — تُحسب وتُرفع لـ ZATCA في جميع الأحوال.
**المدير يختار: هل يتحملها الضيف أم المنشأة؟**

| الضريبة | المعدل | الإجبارية | من يتحكم في التحميل |
|---|---|---|---|
| VAT | 15% | إجبارية دائماً | Manager: على الضيف أم المنشأة؟ |
| رسوم السياحة | 2.5% افتراضي | اختيارية | Manager: تفعيل/تعطيل + من يتحمل؟ |

### منطق الحساب
```
─── المشترك ──────────────────────────────────────────
price_net          = base_price * (1 - discount_pct/100)
raw_tourism        = tourism_tax_enabled ? price_net * tourism_tax_rate : 0

─── الحالة A: الضيف يدفع الضرائب (افتراضي) ──────────
vat_base           = price_net + raw_tourism
vat_amount         = vat_base * 0.15
total_amount       = vat_base + vat_amount

─── الحالة B: المنشأة تتحمل الضريبة ─────────────────
total_amount       = price_net + raw_tourism
vat_base           = total_amount / 1.15
vat_amount         = total_amount - vat_base   ← المنشأة تتحمله / يُرسل لـ ZATCA
```

### جدول `tax_settings`
| الحقل | النوع | الافتراضي | الوصف |
|---|---|---|---|
| vat_rate | DECIMAL(5,4) | 0.1500 | ثابت — يُقرأ فقط |
| vat_on_guest | BOOLEAN | true | true=الضيف يدفع / false=المنشأة تتحمل |
| tourism_tax_enabled | BOOLEAN | false | تفعيل رسوم السياحة |
| tourism_tax_rate | DECIMAL(5,4) | 0.0250 | 0%–10% |
| tourism_tax_on_guest | BOOLEAN | true | true=الضيف يدفع / false=المنشأة تتحمل |
| vat_number | VARCHAR | — | رقم التسجيل الضريبي ZATCA |

### TaxCalculatorService
```typescript
// src/common/services/tax-calculator.service.ts
export interface TaxBreakdown {
  base_price: number; discount_amount: number; price_net: number;
  tourism_tax_amount: number; vat_amount: number; total_amount: number;
  vat_absorbed: number; tourism_absorbed: number;
}

@Injectable()
export class TaxCalculatorService {
  calculate(params: {
    base_price: number; discount_pct: number;
    vat_rate: number; vat_on_guest: boolean;
    tourism_tax_enabled: boolean; tourism_tax_rate: number;
    tourism_tax_on_guest: boolean;
  }): TaxBreakdown {
    const price_net = params.base_price * (1 - params.discount_pct / 100);
    const discount_amount = params.base_price - price_net;
    const raw_tourism = params.tourism_tax_enabled ? price_net * params.tourism_tax_rate : 0;
    const tourism_tax_amount = params.tourism_tax_on_guest ? raw_tourism : 0;
    const tourism_absorbed = params.tourism_tax_on_guest ? 0 : raw_tourism;

    if (params.vat_on_guest) {
      const vat_base = price_net + raw_tourism;
      const vat_amount = vat_base * params.vat_rate;
      return { base_price: params.base_price, discount_amount, price_net,
               tourism_tax_amount: raw_tourism, vat_amount,
               total_amount: vat_base + vat_amount, vat_absorbed: 0, tourism_absorbed };
    } else {
      const guest_subtotal = price_net + tourism_tax_amount;
      const vat_amount = guest_subtotal - guest_subtotal / (1 + params.vat_rate);
      return { base_price: params.base_price, discount_amount, price_net,
               tourism_tax_amount, vat_amount, total_amount: guest_subtotal,
               vat_absorbed: vat_amount, tourism_absorbed };
    }
  }
}
```

---

## ═══════════════════════════════════════
## القسم الرابع — قاعدة البيانات الكاملة
## ═══════════════════════════════════════

### جدول `users`
id UUID PK | name VARCHAR(100) | email VARCHAR UNIQUE | phone VARCHAR? | password_hash VARCHAR (bcrypt 12) | country VARCHAR? | city VARCHAR? | establishment_id FK? | role_type ENUM(ADMIN/MANAGER/EMPLOYEE) | is_email_verified BOOL DEFAULT false | is_active BOOL DEFAULT true | is_deleted BOOL DEFAULT false | deleted_at TIMESTAMP? | failed_login_count INT DEFAULT 0 | locked_until TIMESTAMP? | last_login_at TIMESTAMP? | created_at | updated_at

### جدول `establishments`
id UUID PK | serial_number INT UNIQUE AUTO | name VARCHAR(200) | slug VARCHAR UNIQUE | type ENUM(HOTEL/APARTMENT/RESORT/CHALET) | owner_id FK→users | country VARCHAR DEFAULT 'SA' | city VARCHAR? | district VARCHAR? | phone VARCHAR? | subscription_status ENUM(TRIAL/ACTIVE/EXPIRED/SUSPENDED) | trial_ends_at TIMESTAMP | subscription_ends_at TIMESTAMP? | is_active BOOL | is_deleted BOOL | created_at

### جدول `tax_settings`
id UUID PK | establishment_id FK UNIQUE | vat_rate DECIMAL DEFAULT 0.1500 | vat_on_guest BOOL DEFAULT true | vat_number VARCHAR? | tourism_tax_enabled BOOL DEFAULT false | tourism_tax_rate DECIMAL DEFAULT 0.0250 | tourism_tax_on_guest BOOL DEFAULT true | updated_by FK? | updated_at

### جدول `roles` و `permissions`
roles: id UUID PK | name VARCHAR | is_system BOOL
permissions: id UUID PK | name VARCHAR | module VARCHAR
role_permissions: role_id + permission_id PK
user_roles: user_id + role_id PK
user_permissions: user_id + permission_id

### Security Tokens
refresh_tokens: token_hash UNIQUE + expires_at + is_revoked
password_reset_tokens: token_hash + is_used + expires_at (30 دقيقة)
email_verification_tokens: otp_hash + expires_at + is_used (15 دقيقة)
login_attempts: email + ip_address + is_success + attempted_at
audit_logs: user_id + action + entity_type + entity_id + old_value JSON + new_value JSON + ip_address + created_at

### جدول `room_types` و `rooms`
room_types: id UUID PK | establishment_id FK | name VARCHAR | base_price DECIMAL | max_occupancy INT | amenities VARCHAR[]
rooms: id UUID PK | establishment_id FK | room_type_id FK | room_number VARCHAR | floor INT? | status ENUM(AVAILABLE/OCCUPIED/DIRTY/MAINTENANCE/OUT_OF_ORDER)

### جدول `guests`
id UUID PK | establishment_id FK | full_name VARCHAR | phone VARCHAR UNIQUE per establishment | email VARCHAR? | country VARCHAR? | city VARCHAR? | id_number VARCHAR? | vip_level ENUM DEFAULT NONE (NONE/SILVER/GOLD/PLATINUM) | is_blacklisted BOOL DEFAULT false | total_stays INT DEFAULT 0 | total_spent DECIMAL DEFAULT 0 | created_at

### جدول `direct_bookings`
id UUID PK | booking_ref VARCHAR UNIQUE (DB-YYYY-XXXXX) | establishment_id FK | room_type_id FK | room_id FK? | guest_id FK? | guest_name VARCHAR | guest_phone VARCHAR | guest_email VARCHAR? | guest_country VARCHAR? | guest_city VARCHAR? | check_in_date TIMESTAMP | check_out_date TIMESTAMP | nights INT | adults INT | children INT DEFAULT 0 | base_price DECIMAL | discount_type ENUM? | discount_pct DECIMAL DEFAULT 0 | discount_amount DECIMAL DEFAULT 0 | price_net DECIMAL | tourism_tax_enabled BOOL | tourism_tax_on_guest BOOL | tourism_tax_rate DECIMAL DEFAULT 0 | tourism_tax_amount DECIMAL DEFAULT 0 | vat_rate DECIMAL DEFAULT 0.15 | vat_on_guest BOOL DEFAULT true | vat_amount DECIMAL | total_amount DECIMAL | status ENUM(PENDING/CONFIRMED/CHECKED_IN/CHECKED_OUT/CANCELLED/NO_SHOW) | payment_status ENUM(UNPAID/PARTIAL/PAID/REFUNDED) | paid_amount DECIMAL DEFAULT 0 | payment_method ENUM?(MADA/VISA/APPLE_PAY/CASH) | promo_code VARCHAR? | source ENUM DEFAULT DIRECT | special_requests TEXT? | created_at

### جداول PMS الإضافية
booking_reviews: booking_id + overall + cleanliness + service + location + value (1-5)
night_audit_settings: establishment_id + scheduled_time + default_check_in_time + default_check_out_time + require_payment_before_close
night_audit_logs: establishment_id + audit_date + status + total_revenue + total_vat + total_tourism_tax + total_vat_absorbed + total_tourism_absorbed + unsettled_count
payment_devices: establishment_id + device_name + device_type(POS/MADA/CASH_DRAWER) + is_active
payments: booking_id + device_id? + method + amount + status + settled_in_audit_id
payment_transactions: id + booking_id + moyasar_id + amount + method + status + refund_amount + refund_at
zatca_invoices: booking_id + invoice_number + invoice_type(SIMPLIFIED/CREDIT) + xml_signed + qr_tlv_base64 + qr_image_base64 + zatca_status + vat_amount + tourism_tax_amount + vat_absorbed
housekeeping_tasks: room_id + assigned_to + task_type(CLEANING/INSPECTION/MAINTENANCE/TURNDOWN) + priority(LOW/MEDIUM/HIGH/URGENT) + status + due_at
booking_app_settings: establishment_id + direct_discount + early_bird_discount + long_stay_discount + min_nights_long_stay + cancellation_policy + accepted_payments[]
promotions: establishment_id + code UNIQUE + discount_type + discount_value + valid_from + valid_until + max_uses + used_count
subscriptions: establishment_id + serial_number + plan + starts_at + ends_at + amount_paid
concierge_requests: id + booking_id + room_id + type + description + status + assigned_to + priority + sla_minutes DEFAULT 30 + requested_at + completed_at + guest_rating
pos_products: id + establishment_id + name + price + category + stock_count + min_stock + sku
pos_transactions: id + booking_id + product_id + quantity + unit_price + total + added_by + created_at
channel_connections: id + establishment_id + channel_name + api_key_encrypted + is_active + last_sync_at + sync_status
channel_sync_logs: id + channel + operation + status + response_code + payload + created_at
demand_forecasts: establishment_id + forecast_date + predicted_occupancy + confidence_score + created_at
pricing_rules: id + establishment_id + room_type_id? + strategy + trigger_value + price_adjustment + is_auto_apply + is_active

---

## ═══════════════════════════════════════
## القسم الخامس — الصلاحيات (50+ في DB)
## ═══════════════════════════════════════

```
users.create / users.read / users.update / users.delete / users.activate
roles.create / roles.read / roles.update / roles.delete / permissions.assign
dashboard.view / dashboard.analytics
reports.view / reports.export
settings.view / settings.update
tax_settings.view / tax_settings.update
profile.view / profile.update
audit_logs.view / audit_logs.export
rooms.create / rooms.read / rooms.update / rooms.delete / rooms.change_status
guests.create / guests.read / guests.update / guests.blacklist / guests.vip_upgrade
bookings.create / bookings.read / bookings.update / bookings.delete
bookings.check_in / bookings.check_out / bookings.cancel
night_audit.view / night_audit.run / night_audit.settings
invoices.create / invoices.view / invoices.export
housekeeping.view / housekeeping.create / housekeeping.assign / housekeeping.complete
booking_app.view / booking_app.settings / booking_app.promotions
reviews.view / reviews.reply
payment_devices.manage
concierge.view / concierge.create / concierge.assign
pos.manage / pos.report
channel.manage / channel.sync
revenue.view / revenue.manage
```

| الصلاحية | Admin | Manager | Employee |
|---|:---:|:---:|:---:|
| tax_settings.update | ✅ | ✅ منشأته | ❌ |
| users.create | ✅ | ✅ منشأته | ❌ |
| night_audit.run | ✅ | ✅ | ❌ |
| invoices.create | ✅ | ✅ | view فقط |
| reports.view | ✅ | ✅ | ❌ |
| bookings.check_in/out | ✅ | ✅ | حسب الإعداد |

---

## ═══════════════════════════════════════
## القسم السادس — وحدات النظام الكاملة
## ═══════════════════════════════════════

### 1. تطبيق الحجز المباشر — dheuof.com/book/{slug}
- بحث + تسعير ديناميكي متكيف مع `vat_on_guest` و`tourism_tax_on_guest`
- خصومات: مباشر 5% + مبكر 10% (قبل 30 يوم) + إقامة طويلة 15% (7 ليالٍ) + كودات مخصصة
- دفع Moyasar: MADA + Visa + Mastercard + Apple Pay + STC Pay
- تأكيد: QR + SMS + Email + رقم مرجعي
- تتبع الحجز برقم الجوال — بدون تسجيل دخول
- تقييم بعد الخروج (5 معايير × 5 نجوم)

### 2. Night Audit
- Cron ديناميكي يُعاد ضبطه عند تغيير الوقت (لا يتراكم)
- Pre-check: يتوقف إذا كانت هناك مدفوعات معلقة
- تقرير PDF: إيرادات + VAT + سياحة + ضرائب تحملتها المنشأة + تفصيل أجهزة الدفع
- إرسال التقرير تلقائياً بالبريد لـ Manager + Admin

### 3. ZATCA — الفاتورة الإلكترونية
- فاتورة مبسّطة UBL 2.1 تلقائياً عند Check-out
- رسوم السياحة كسطر منفصل في XML إن فُعّلت
- QR TLV: اسم البائع + رقم ضريبي + تاريخ + إجمالي + VAT (Base64)
- QR Scanner بالكاميرا للتحقق — عام بدون JWT
- Credit Note عند الاسترداد مرتبطة بالفاتورة الأصلية

### 4. Channel Manager (500+ قناة)
- Booking.com + Airbnb + Expedia + Agoda + Makkah Gate + OTA Saudi
- Inventory Pooling: مخزون موحد يُوزَّع تلقائياً
- Stop-sell تلقائي عند اكتمال الإشغال
- Rate Manager: تحديث أسعار bulk لكل القنوات دفعة واحدة
- Retry Queue مع exponential backoff

### 5. Moyasar — الدفع الكامل
- MADA + Visa + Apple Pay + STC Pay
- Webhook استقبال حالة الدفع
- استرداد جزئي وكلي مع Credit Note ZATCA تلقائية
- Tokenization للضيوف المتكررين
- Payment Links: رابط دفع عبر SMS/Email

### 6. التقارير و KPI
- Occupancy Rate + ADR + RevPAR + RevPAG (حية)
- VAT المحصّل + سياحة + مُتحمَّل من المنشأة
- تقرير الضيوف (Shamoos/GASTAT)
- توقعات إشغال 7/14/30 يوم
- تصدير PDF (A4 Arabic RTL) + Excel + CSV
- جدولة تقرير أسبوعي/شهري تلقائي لـ Manager

### 7. Revenue Management AI
- Demand Forecasting: سجل 12 شهر + مواسم + أحداث
- Dynamic Pricing: اقتراح تسعير — Manager يوافق/يرفض
- Strategies: Yield + Last-Minute + Early Bird

### 8. Concierge Module (طلبات داخلية)
- طلبات: Room Service + Housekeeping + Maintenance + أمتعة
- SLA تلقائي (30 دقيقة افتراضي) + تنبيه عند التأخر
- تقييم الضيف بعد الإنجاز

### 9. POS مبسط
- كاتالوج منتجات + إدارة مخزون
- ربط بحجز الضيف → يُضاف للفاتورة عند Check-out
- ZATCA: منتجات POS كسطر إضافي

### 10. Housekeeping
- Kanban: PENDING → IN_PROGRESS → DONE
- مهمة تلقائية عند كل Check-out
- أولوية: LOW / MEDIUM / HIGH / URGENT

---

## ═══════════════════════════════════════
## القسم السابع — متطلبات الأمان
## ═══════════════════════════════════════

| المتطلب | التفاصيل |
|---|---|
| كلمات المرور | bcrypt rounds=12 — لا تخزين كنص |
| JWT | Access 15 دقيقة (ذاكرة) + Refresh 7 أيام (DB كـ Hash) |
| Cookie | HttpOnly + Secure + SameSite=Strict + Path=/auth/refresh |
| Rate Limiting | 5 محاولات / 15 دقيقة لكل IP |
| قفل الحساب | 30 دقيقة بعد 5 محاولات فاشلة |
| رسالة الخطأ | "بيانات الدخول غير صحيحة" — لا يكشف السبب |
| MFA | TOTP (Google Authenticator) للـ Admin و Manager |
| SQL | Prisma Parameterized Queries — لا Raw SQL |
| XSS | DOMPurify (Frontend) + sanitize-html (Backend) |
| Headers | Helmet.js في NestJS |
| CORS | Whitelist صريح — لا * في Production |
| Tax Integrity | vat_rate ثابت في الكود — Manager يتحكم في التحميل فقط |
| Row Isolation | EstablishmentContextInterceptor |
| Guest Isolation | GuestGuard — token.type === 'guest' |
| Audit Logs | كل عملية حساسة مسجّلة + Immutable + 2 سنة |
| Soft Delete | is_deleted + deleted_at في جميع الجداول |

### Guards المطلوبة
```typescript
JwtAuthGuard | RolesGuard | PermissionsGuard | SubscriptionGuard
OwnershipGuard | GuestGuard | EstablishmentContextInterceptor
AuditLogInterceptor
```

---

## ═══════════════════════════════════════
## القسم الثامن — واجهات API الكاملة
## ═══════════════════════════════════════

### المصادقة
```
POST /auth/register | /auth/login | /auth/logout | /auth/refresh-token
POST /auth/forgot-password | /auth/reset-password | /auth/verify-email
GET  /auth/me
POST /auth/mfa/enable | /auth/mfa/verify
GET  /auth/sessions | DELETE /auth/sessions/:id
```

### الإعدادات والضرائب
```
GET  /settings/tax                        ← tax_settings.view
PATCH /settings/tax                       ← vat_on_guest + tourism_*
GET  /bookings/:id/tax-breakdown
GET  /reports/tax
```

### PMS الكاملة
```
GET  /rooms/availability | POST /rooms | PATCH /rooms/:id/status
GET  /guests | POST /guests | GET /guests/:id/history | PATCH /guests/:id/blacklist
GET  /bookings | POST /bookings | POST /bookings/:id/check-in | /check-out | /review
GET  /night-audit/settings | PATCH /night-audit/settings | POST /night-audit/run
GET  /night-audit/:date/report
POST /zatca/invoices/:id/generate | GET /zatca/invoices/:id/qr | POST /zatca/verify-qr
GET  /housekeeping | POST /housekeeping
```

### القنوات والمدفوعات والذكاء
```
GET  /channels | POST /channels/:name/connect | POST /channels/sync-all
GET  /pos/products | POST /pos/products | POST /pos/transactions
POST /concierge/requests | PATCH /concierge/requests/:id | GET /concierge/active
GET  /revenue/forecast | GET /revenue/pricing-suggestions | POST /revenue/rules
```

### تطبيق الحجز المباشر
```
GET  /book/:slug | /book/:slug/search
POST /book/:slug/check-promo | /book/:slug/price-preview | /book/:slug/create | /book/:slug/payment
GET  /book/my-booking | POST /book/my-booking/cancel
PATCH /booking-app/settings | POST /booking-app/promotions
```

### التقارير
```
GET /reports/kpis | /reports/occupancy | /reports/revenue | /reports/tax
GET /reports/guests | /reports/reviews | /reports/forecast | /reports/savings
GET /audit-logs
```

---

## ═══════════════════════════════════════
## القسم التاسع — هيكل المشروع الكامل
## ═══════════════════════════════════════

```
duyuf-platform/
├── apps/
│   ├── backend/  (NestJS)
│   │   └── src/
│   │       ├── auth/           ├── users/         ├── establishments/
│   │       ├── subscriptions/  ├── roles/          ├── permissions/
│   │       ├── tax-settings/   ├── rooms/          ├── room-types/
│   │       ├── guests/         ├── bookings/       ├── booking-app/
│   │       ├── night-audit/    ├── zatca/          ├── housekeeping/
│   │       ├── reports/        ├── audit-logs/     ├── channels/
│   │       ├── pos/            ├── concierge/      ├── revenue/
│   │       ├── common/
│   │       │   ├── guards/         (7 guards)
│   │       │   ├── interceptors/   (AuditLog + EstablishmentContext)
│   │       │   ├── services/       (TaxCalculatorService)
│   │       │   └── data/           (locations.ts)
│   │       ├── mail/ + sms/
│   │       └── prisma/ (schema.prisma + seed.ts + migrations/)
│   │
│   ├── frontend/ (Next.js 14)
│   │   └── app/
│   │       ├── (auth)/             (login/register/verify/forgot/reset)
│   │       ├── (dashboard)/
│   │       │   ├── bookings/       ├── settings/tax/  ├── night-audit/
│   │       │   ├── zatca/scanner   ├── reports/        ├── booking-app/
│   │       │   ├── housekeeping/   ├── channels/       ├── pos/
│   │       │   ├── concierge/      └── revenue/
│   │       ├── book/[slug]/        (Public — بدون JWT)
│   │       └── guest/              (OTP)
│   │
│   └── mobile/ (Flutter)
│       └── lib/
│           ├── screens/            (check_in / check_out / housekeeping / concierge)
│           ├── services/           (api / auth / offline_sync)
│           └── localization/       (ar / en / hi / ne / bn)
│
├── docker-compose.yml
├── .github/workflows/ci.yml
└── .env.example
```

---

## ═══════════════════════════════════════
## القسم العاشر — متغيرات البيئة
## ═══════════════════════════════════════

```env
NODE_ENV=development
PORT=3001
APP_URL=http://localhost:3001
FRONTEND_URL=http://localhost:3000
DATABASE_URL=postgresql://USER:PASS@localhost:5432/duyuf_db
JWT_ACCESS_SECRET=REPLACE_MIN_64_CHARS
JWT_ACCESS_EXPIRES_IN=15m
JWT_REFRESH_SECRET=REPLACE_DIFFERENT_MIN_64_CHARS
JWT_REFRESH_EXPIRES_IN=7d
BCRYPT_SALT_ROUNDS=12
THROTTLE_TTL=900
THROTTLE_LIMIT=5
ACCOUNT_LOCK_MINUTES=30
TRIAL_DAYS=60
ADMIN_DEFAULT_PASSWORD=REPLACE_STRONG_PASS
MAIL_HOST=smtp.zoho.sa
MAIL_PORT=587
MAIL_USER=info@dheuof.com
MAIL_PASSWORD=REPLACE
MAIL_FROM="منصة ضيوف <info@dheuof.com>"
SMS_PROVIDER=unifonic
SMS_API_KEY=REPLACE
MOYASAR_API_KEY=REPLACE
MOYASAR_WEBHOOK_SECRET=REPLACE
ZATCA_ENV=sandbox
ZATCA_VAT_NUMBER=REPLACE
ZATCA_CERTIFICATE=REPLACE
ZATCA_PRIVATE_KEY=REPLACE
VAT_RATE=0.15
DEFAULT_TOURISM_TAX_RATE=0.025
CHANNEL_ENCRYPTION_KEY=REPLACE_32_CHARS
REDIS_URL=redis://localhost:6379
```

---

## ═══════════════════════════════════════
## القسم الحادي عشر — ترتيب البناء
## ═══════════════════════════════════════

| # | المرحلة | المحتوى |
|---|---|---|
| 1 | البنية الأساسية | NestJS + Next.js + Prisma + Docker + Guards |
| 2 | المصادقة | Register + Login + OTP + JWT + MFA + Rate Limiting |
| 3 | الأدوار والصلاحيات | Seed 50+ Permission + RBAC |
| 4 | الاشتراكات | Trial 60 يوم + SubscriptionGuard |
| 5 | الدول والمناطق | locations.ts + CountryRegionSelect |
| **6** | **نظام الضرائب** | **TaxCalculatorService + tax_settings + API** |
| 7 | الغرف والضيوف | RoomTypes + Rooms + Guests CRM |
| 8 | الحجوزات | Bookings + Check-in + Check-out + حساب الضرائب |
| 9 | Night Audit | Cron + PDF + تقرير الضرائب |
| 10 | ZATCA | TLV + QR + Scanner + XML |
| 11 | Moyasar | Webhook + Refund + Tokenization |
| 12 | تطبيق الحجز | Public Pages + Pricing Engine + Payment |
| 13 | التقارير | KPI + Dashboards + تصدير |
| 14 | Housekeeping | Kanban + Auto-tasks |
| 15 | Channel Manager | 500+ قناة + Inventory Pooling |
| 16 | POS + Concierge | منتجات + طلبات داخلية |
| 17 | Revenue AI | Forecasting + Dynamic Pricing |
| 18 | Flutter Mobile | Android أولاً + Offline Mode |

---

## ═══════════════════════════════════════
## القسم الثاني عشر — مراجعة البناء الشاملة
## ═══════════════════════════════════════

بعد البناء نفّذ هذه المراجعة كاملاً:

### مراجعة Schema
```bash
npx prisma validate && npx prisma format --check
```
- [ ] جميع الجداول موجودة مع حقول الضرائب الصحيحة
- [ ] `vat_on_guest` + `tourism_tax_on_guest` في tax_settings وdirect_bookings
- [ ] `total_vat_absorbed` + `total_tourism_absorbed` في night_audit_logs
- [ ] indexes على الحقول المستخدمة في البحث

### مراجعة الأمان
```bash
npm audit --audit-level=high
npx tsc --noEmit
npx eslint . --ext .ts,.tsx
```
- [ ] bcrypt rounds = 12 فعلياً
- [ ] Refresh Token مخزن كـ Hash لا نص
- [ ] EstablishmentContextInterceptor على كل endpoint للـ Manager
- [ ] Rate Limiting فعّال: 5 طلبات / 15 دقيقة
- [ ] لا `*` في CORS Production

### مراجعة الضرائب (3 سيناريوهات)
```typescript
// سيناريو A: total يجب = 1178.75
calculate({ base_price:1000, discount_pct:0, vat_rate:0.15,
  vat_on_guest:true, tourism_tax_enabled:true,
  tourism_tax_rate:0.025, tourism_tax_on_guest:true })

// سيناريو B: total = 922.5 + vat_absorbed = 120.33
calculate({ base_price:1000, discount_pct:10, vat_rate:0.15,
  vat_on_guest:false, tourism_tax_enabled:true,
  tourism_tax_rate:0.025, tourism_tax_on_guest:true })

// سيناريو C: total = 500 + vat_absorbed = 65.22
calculate({ base_price:500, discount_pct:0, vat_rate:0.15,
  vat_on_guest:false, tourism_tax_enabled:false,
  tourism_tax_rate:0.025, tourism_tax_on_guest:false })
```

### مراجعة ZATCA
- [ ] XML يحتوي رسوم السياحة كسطر منفصل
- [ ] QR TLV بالحقول الخمسة بالترتيب الصحيح
- [ ] vat_amount يُرسل لـ ZATCA بغض النظر عمّن يتحمل
- [ ] Credit Note مرتبطة بالفاتورة الأصلية

### مراجعة الكود
- [ ] لا any type في TypeScript
- [ ] ValidationPipe: whitelist + forbidNonWhitelisted
- [ ] findMany دائماً مع take + skip
- [ ] select: محدد — لا استرجاع جميع الحقول
- [ ] Test Coverage لا يقل عن 70% للـ Services الحساسة

---

## ═══════════════════════════════════════
## القسم الثالث عشر — الإعداد بهوية المالك
## ═══════════════════════════════════════

### تسجيل Admin
```
الاسم:    عبدالله الشمري
البريد:   abdulellah.sh11@gmail.com
الجوال:   05XXXXXXXX
الدور:    ADMIN (مالك المنصة)
```

### إنشاء المنشأة
```
الاسم:   فندق الشمري — Shamari Hotel
النوع:   HOTEL
المدينة: الرياض — العليا
الرابط:  dheuof.com/book/shamari-hotel
```

### إعداد الضرائب
```
VAT:           15% ثابت
رسوم السياحة: 2.5% مفعّلة
التحميل:       الضيف يدفع (الحالة A)
```

### إنشاء الفريق
```
Manager:    أحمد الشمري — manager@shamari.com
موظف 1:    محمد العتيبي — استقبال
موظف 2:    سارة الزهراني — هاوس كيبينج
موظف 3:    خالد الدوسري — كاشير
```

### إضافة الغرف (20 غرفة)
```
101–105: Single  — 350 ر.س/ليلة  (سعة 1)
201–205: Double  — 550 ر.س/ليلة  (سعة 2)
301–304: Suite   — 1200 ر.س/ليلة (سعة 4)
401–405: Apt     — 900 ر.س/ليلة  (سعة 3)
```

---

## ═══════════════════════════════════════
## القسم الرابع عشر — تسجيل 20 ضيفاً
## ═══════════════════════════════════════

| # | الاسم | الجنسية | الجوال | البريد | VIP |
|---|---|---|---|---|---|
| 01 | عبدالرحمن السلوم | سعودي | 0501234501 | alsolom@gmail.com | NONE |
| 02 | فيصل المطيري | سعودي | 0501234502 | faisal.m@gmail.com | SILVER |
| 03 | نورة العنزي | سعودية | 0501234503 | noura.a@gmail.com | NONE |
| 04 | خالد الرشيدي | سعودي | 0501234504 | rashidi.k@gmail.com | GOLD |
| 05 | سلطان القحطاني | سعودي | 0501234505 | sultan.q@gmail.com | NONE |
| 06 | منيرة الدوسري | سعودية | 0501234506 | monira.d@gmail.com | SILVER |
| 07 | عمر الشهري | سعودي | 0501234507 | omar.sh@gmail.com | PLATINUM |
| 08 | Ahmed Al-Mansoori | إماراتي | 0521234508 | ahmed.m@gmail.com | GOLD |
| 09 | Mohammed Al-Rashidi | كويتي | 0531234509 | mo.rash@gmail.com | NONE |
| 10 | Fatima Al-Farsi | عُمانية | 0541234510 | fatima.f@gmail.com | SILVER |
| 11 | Youssef Al-Hamdan | بحريني | 0551234511 | youssef.h@gmail.com | NONE |
| 12 | Abdullah Al-Mutawa | قطري | 0561234512 | mutawa.a@gmail.com | GOLD |
| 13 | James Wilson | بريطاني | 0571234513 | james.w@gmail.com | NONE |
| 14 | Anna Petrova | روسية | 0581234514 | anna.p@gmail.com | NONE |
| 15 | Mohammed Hassan | مصري | 0591234515 | mhassan@gmail.com | NONE |
| 16 | Rajesh Kumar | هندي | 0501234516 | rajesh.k@gmail.com | SILVER |
| 17 | Li Wei | صيني | 0501234517 | liwei@gmail.com | NONE |
| 18 | Sarah Johnson | أمريكية | 0501234518 | sarah.j@gmail.com | PLATINUM |
| 19 | Pierre Dubois | فرنسي | 0501234519 | pierre.d@gmail.com | NONE |
| 20 | Aisha Mohammed | أردنية | 0501234520 | aisha.m@gmail.com | NONE |

---

## ═══════════════════════════════════════
## القسم الخامس عشر — 20 حجزاً كاملاً
## ═══════════════════════════════════════

| # | الضيف | الغرفة | الليالي | الخصم | طريقة الدفع | العملية |
|---|---|---|---|---|---|---|
| 01 | السلوم | 101 Single | 3 | 10% | MADA | Check-in + out |
| 02 | المطيري | 201 Double | 2 | — | Visa | Check-in + out |
| 03 | العنزي | 301 Suite | 5 | مبكر 10% | Apple Pay | Check-in |
| 04 | الرشيدي | 401 Apt | 7 | إقامة طويلة 15% | كاش | Check-in + تمديد |
| 05 | القحطاني | 102 Single | 1 | — | MADA | Check-in + out |
| 06 | الدوسري | 202 Double | 4 | كود VIP20 | Visa | Check-in |
| 07 | الشهري | 302 Suite | 2 | — | Apple Pay | Check-in + out |
| 08 | Al-Mansoori | 402 Apt | 3 | مباشر 5% | MADA | Check-in |
| 09 | Al-Rashidi | 103 Single | 6 | — | كاش | Check-in + out |
| 10 | Al-Farsi | 203 Double | 2 | 15% | Visa | Check-in + out |
| 11 | Al-Hamdan | 303 Suite | 3 | — | MADA | Check-in |
| 12 | Al-Mutawa | 403 Apt | 4 | SUMMER10 | Apple Pay | No-Show |
| 13 | Wilson | 104 Single | 1 | — | Visa | إلغاء + استرداد كامل |
| 14 | Petrova | 204 Double | 2 | 5% | MADA | Check-in + out |
| 15 | Hassan | 304 Suite | 5 | — | كاش | Check-in |
| 16 | Kumar | 404 Apt | 3 | VIP30 | Visa | Check-in + out |
| 17 | Li Wei | 105 Single | 2 | — | MADA | Check-in |
| 18 | Johnson | 205 Double | 4 | مبكر 10% | Apple Pay | Check-in |
| 19 | Dubois | 405 Apt | 1 | — | Visa | إلغاء + استرداد جزئي 50% |
| 20 | Mohammed | 103 Single | 3 | كود VIP30 | MADA | Check-in + out |

**عمليات خاصة:**
- حجز 01: ترقية غرفة Single → Double بعد Check-in
- حجز 04: تمديد إقامة + ليلتان إضافيتان + فاتورة تكميلية
- حجز 10: دفع جزئي (Visa + كاش مناصفة)

**لكل Check-out:** أصدر فاتورة ZATCA + أنشئ مهمة Housekeeping تلقائياً.

---

## ═══════════════════════════════════════
## القسم السادس عشر — المطابقة والمحاسبة
## ═══════════════════════════════════════

### المطابقة اليومية (بعد Night Audit)
```
1. استخرج من النظام:
   MADA:      X,XXX.XX ر.س
   Visa:      X,XXX.XX ر.س
   Apple Pay: X,XXX.XX ر.س
   كاش:       X,XXX.XX ر.س
   المجموع:   X,XXX.XX ر.س

2. طابق مع:
   ✓ سجل أجهزة POS
   ✓ كشف Moyasar API
   ✓ عدد الكاش الفعلي في الصندوق
   ✓ فواتير ZATCA المصدرة

3. نتيجة المطابقة:
   □ متطابق تماماً ✅
   □ فروقات: X ر.س (موثّقة ومبررة)
```

### مطابقة الضرائب
```
إيرادات قبل الضريبة:        X,XXX.XX ر.س
رسوم السياحة (2.5%):        XXX.XX   ر.س
VAT من الضيوف (15%):         X,XXX.XX ر.س
VAT تحملته المنشأة:           XXX.XX   ر.س
إجمالي VAT → ZATCA:           X,XXX.XX ر.س
────────────────────────────────────────
تحقق: VAT_total = (price_net + tourism) × 15% ؟ ✅/❌
```

### القيود المحاسبية
```
من: النقدية/البنك            X,XXX.XX مدين
من: ذمم العملاء              X,XXX.XX مدين
  إلى: إيرادات الإيجار               دائن
  إلى: ضريبة VAT المستحقة            دائن
  إلى: رسوم السياحة المستحقة         دائن
```

### مؤشرات الأداء
```
RevPAR = إجمالي الإيرادات ÷ 20 غرفة
ADR    = إجمالي الإيرادات ÷ غرف مشغولة
معدل الإشغال = (غرف مشغولة ÷ 20) × 100%
```

---

## ═══════════════════════════════════════
## القسم السابع عشر — اختبار جميع الأزرار
## ═══════════════════════════════════════

### لوحة Admin (عبدالله الشمري)
```
□ دخول Admin + MFA
□ لوحة إجمالي جميع المنشآت
□ إنشاء Manager جديد
□ تجديد اشتراك منشأة برقمها التسلسلي
□ تعليق منشأة + إعادة تفعيل
□ تصدير Audit Log PDF + Excel
□ عرض إجمالي الإيرادات الكلية
□ مقارنة أداء المنشآت
```

### لوحة Manager
```
□ إعدادات الضرائب: Toggle VAT على الضيف/المنشأة
□ Toggle رسوم السياحة + تغيير المعدل
□ إنشاء موظف + تحديد صلاحياته module بـ module
□ تعديل صلاحية موظف + تعطيل حسابه
□ ضبط Night Audit على الساعة 23:00
□ تشغيل Night Audit يدوياً
□ تقرير Night Audit PDF
□ إعداد تطبيق الحجز: خصومات + سياسة إلغاء
□ إنشاء كود خصم VIP20 + SUMMER10 + VIP30
□ تجربة الكود في تطبيق الحجز
□ خريطة الغرف التفاعلية
□ تغيير حالة غرفة: AVAILABLE → MAINTENANCE
□ إدارة أجهزة الدفع + إضافة جهاز
□ عرض تقرير الوفر من OTA
```

### وحدة الحجوزات
```
□ إنشاء حجز + معاينة تفصيل الضرائب
□ تعديل حجز + تغيير التاريخ
□ تطبيق خصم + كود ترويجي
□ Check-in مع ربط الغرفة الفعلية
□ Check-out + عرض الفاتورة النهائية
□ إصدار فاتورة ZATCA + QR
□ التحقق من QR بالـ Scanner
□ إلغاء حجز + احتساب استرداد
□ تسجيل No-Show
□ تمديد إقامة + فاتورة تكميلية
□ ترقية غرفة أثناء الإقامة
□ طباعة تأكيد الحجز PDF
□ تسجيل تقييم الضيف (5 معايير)
```

### وحدة الضيوف
```
□ بحث ضيف بالجوال
□ عرض سجل إقامات + إجمالي الإنفاق
□ ترقية VIP: NONE→SILVER→GOLD→PLATINUM
□ Blacklist ضيف مع سبب
□ دمج ملف ضيف مكرر
□ تصدير قائمة الضيوف Excel
```

### وحدة ZATCA
```
□ فاتورة مبسّطة عند Check-out
□ Credit Note عند الاسترداد
□ رفع لـ ZATCA Sandbox + استقبال UUID
□ QR Scanner بالكاميرا
□ تحميل XML موقّع
□ أرشيف فواتير اليوم
```

### وحدة Housekeeping
```
□ Kanban: PENDING→IN_PROGRESS→DONE
□ مهمة تلقائية بعد Check-out
□ تعيين مهمة لسارة الزهراني
□ تغيير حالة الغرفة: DIRTY→CLEAN
□ طلب صيانة عاجل (URGENT)
```

### وحدة Concierge
```
□ طلب Room Service من ضيف
□ إسناد للموظف + تتبع الحالة
□ تنبيه SLA عند التأخر
□ تقييم الضيف للطلب
```

### وحدة POS
```
□ إضافة منتج مينيبار
□ تسجيل مبيعة على حجز ضيف
□ عرض في الفاتورة النهائية
□ تقرير مبيعات POS
```

### Channel Manager
```
□ ربط Booking.com
□ مزامنة التوفر يدوياً
□ تحديث سعر لكل القنوات
□ عرض سجل المزامنة
```

### التقارير
```
□ KPI لحظي: Occupancy + ADR + RevPAR
□ تقرير الإيرادات بالمصدر + نوع الغرفة
□ تقرير الضرائب (VAT + سياحة + متحمَّل)
□ تقرير الضيوف (توزيع الجنسيات 20 ضيف)
□ تقرير التقييمات Radar Chart
□ توقعات الإشغال 30 يوم
□ تصدير كل تقرير PDF + Excel
□ جدولة تقرير شهري تلقائي
```

### تطبيق الحجز المباشر
```
□ بحث غرفة بتاريخ + عدد أشخاص
□ عرض السعر مع تفصيل الضرائب (الحالة A)
□ تطبيق كود VIP20
□ إتمام حجز Guest بدون تسجيل دخول
□ استقبال QR + Email تأكيد
□ تتبع الحجز برقم الجوال
□ إلغاء ذاتي + تأكيد الاسترداد
□ تقييم الإقامة بعد الخروج
```

---

## ═══════════════════════════════════════
## القسم الثامن عشر — اختبار الأمان
## ═══════════════════════════════════════

```
اختبار 1: دخول Admin بكلمة خاطئة 5 مرات
          → يُقفل الحساب 30 دقيقة تلقائياً ✅

اختبار 2: Manager يحاول الوصول لبيانات منشأة أخرى
          → 403 Forbidden ✅

اختبار 3: تعديل vat_rate=0.10 من API
          → مرفوض / يبقى 0.15 ✅

اختبار 4: استخدام Refresh Token بعد Logout
          → 401 Unauthorized ✅

اختبار 5: طلب بـ token موظف على مسار Admin
          → 403 Forbidden ✅

اختبار 6: حقل اسم الضيف = <script>alert(1)</script>
          → يُحفظ كنص — لا تنفيذ ✅

اختبار 7: 10 طلبات في ثانية على /auth/login
          → يُرفض بعد الطلب الخامس (429) ✅

اختبار 8: Token صالح لـ Guest على مسار Staff
          → 403 Forbidden ✅
```

---

## ═══════════════════════════════════════
## القسم التاسع عشر — تقرير PDF الشامل
## ═══════════════════════════════════════

بعد إنهاء جميع الأقسام السابقة، أصدر تقرير PDF احترافي بالمواصفات التالية:

```
الغلاف:
  منصة ضيوف — التقرير الشامل للبناء والاختبار
  المالك: عبدالله الشمري
  التاريخ: [اليوم]
  البيئات المختبرة: localhost + Staging + www.dheuof.com
  الجاهزية الإجمالية: X%

القسم 1 — الملخص التنفيذي
  النتيجة الإجمالية + عدد الاختبارات (نجح/فشل) + الوحدات المختبرة

القسم 2 — بيانات المنصة والمنشأة
  عبدالله الشمري + فندق الشمري + 3 موظفين + 20 غرفة

القسم 3 — جدول الضيوف الـ 20
  رقم | اسم | جنسية | VIP | حجوزات | إجمالي إنفاق

القسم 4 — تقرير الحجوزات
  إجمالي 20 | Check-in X | Check-out X | ملغي X | No-Show X

القسم 5 — المطابقة والمدفوعات
  ┌────────────────────────────────────────┐
  │ طريقة الدفع │ المبلغ     │ العمليات  │
  │ MADA        │ X,XXX ر.س │ X         │
  │ Visa        │ X,XXX ر.س │ X         │
  │ Apple Pay   │ X,XXX ر.س │ X         │
  │ كاش         │ X,XXX ر.س │ X         │
  │ المجموع     │ X,XXX ر.س │ X         │
  └────────────────────────────────────────┘
  حالة المطابقة مع Moyasar: ✅ متطابق

القسم 6 — المحاسبة والضرائب
  إيرادات قبل الضريبة + VAT محصّل + سياحة + متحمَّل + صافي
  RevPAR + ADR + معدل الإشغال

القسم 7 — نتائج اختبار الوحدات (جدول)
  الوحدة | الحالة | الدرجة | الملاحظة

القسم 8 — نتائج اختبار الأمان
  8 اختبارات × نتيجة ✅/❌

القسم 9 — مقارنة تنافسية
  منصة ضيوف X% vs Oracle Opera 92.8% vs نزيل 58.4%
  الميزات الحصرية: ضريبة ثنائية + حجز مباشر + ZATCA كامل

القسم 10 — التوصيات والخطوات التالية
  ما نجح + ما يحتاج تحسين + خارطة الطريق للـ 95%

التوقيع:
  أُعدّ بتاريخ [اليوم]
  المالك: عبدالله الشمري
  المنصة: منصة ضيوف — www.dheuof.com
```

احفظ التقرير: `duyuf-shamari-full-report-[YYYY-MM-DD].pdf`

---

## ═══════════════════════════════════════
## القسم العشرون — قائمة مراجعة الإطلاق
## ═══════════════════════════════════════

### الأمان
- [ ] NODE_ENV=production | HTTPS + SSL | Admin password تغيّر
- [ ] CORS بنطاقات صحيحة | .env خارج Git | Swagger محظور

### الضرائب
- [ ] VAT ثابت 15% لا يتغير من الواجهة
- [ ] 3 سيناريوهات ضريبية اجتازت بنتائج صحيحة
- [ ] ZATCA Sandbox نجح قبل Production
- [ ] Night Audit: total_vat_absorbed صحيح

### قاعدة البيانات
- [ ] Migrations نُفّذت | Seed: أدوار + صلاحيات + Admin + tax_settings
- [ ] Connection Pooling | Backup يومي مشفّر

### الوظائف
- [ ] 20 ضيف مسجّل | 20 حجز منفّذ | 10 Check-out + فواتير ZATCA
- [ ] Night Audit اجتاز Staging | Moyasar اجتاز Sandbox
- [ ] QR Scanner يعمل Android + iOS
- [ ] SMS + Email تأكيد يصل للضيوف

### الأداء
- [ ] API response < 200ms للـ endpoints الأساسية
- [ ] لا N+1 queries في الـ Services الرئيسية
- [ ] Rate Limiting يمنع DDoS

---

**الأمر النهائي:**

أخرج الكود الكامل لكل وحدة بالترتيب المذكور في القسم الحادي عشر. لكل وحدة: Prisma Schema + NestJS Module + Controller + Service + DTO + Guard + اختبار وحدة. ثم نفّذ الإعداد الكامل بهوية عبدالله الشمري (الأقسام 13–19). ثم أصدر التقرير PDF الشامل. لا تتخطَّ خطوة واحدة.
