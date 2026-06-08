# برومبت منصة ضيوف — النسخة الكاملة المحدثة

---

أنت الآن خبير هندسة برمجيات، وخبير أمن تطبيقات، ومهندس نظم Backend وFrontend متخصص في أنظمة إدارة الفنادق (PMS).
أريد منك إنشاء نظام **منصة ضيوف** — نظام SaaS متكامل لإدارة الفنادق والمنشآت الفندقية في المملكة العربية السعودية.

**المبدأ الأساسي:** دقة قبل الجمال — تحقق قبل الاستنتاج — تفصيل قبل الاختصار — إخراج نهائي قبل الشرح — أقل كود ممكن مع أقصى وظيفية.

---

## أولاً: بيانات المشروع

| الحقل | القيمة |
|---|---|
| نوع المشروع | SaaS متعدد المستأجرين (Multi-Tenant) |
| اسم المشروع | منصة ضيوف |
| الموقع | www.dheuof.com |
| البريد | info@dheuof.com |
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

---

## ثانياً: الأدوار الأربعة

### 1. ADMIN — أنا المالك (مالك المنصة)
- الحساب الوحيد من هذا النوع — لا يُنشأ أكثر من واحد.
- يرى **جميع** البيانات عبر **جميع** المنشآت في لوحة تحكم واحدة.
- ينشئ حسابات المديرين (Manager) لكل منشأة.
- يدير الاشتراكات والفترات التجريبية.
- لا يمكن حذفه أو تعديل صلاحياته من أي حساب آخر.
- لا ينتمي لأي منشأة — يرى الكل.
- لوحة Admin تعرض: إجمالي المنشآت + الإيرادات الكلية + المستخدمون + الاشتراكات + سجل التدقيق الكامل.

### 2. MANAGER — مدير المنشأة
- يدير منشأته الخاصة فقط (فندق / شقق فندقية / منتجع...).
- **ينشئ حسابات الموظفين** داخل منشأته.
- **يحدد صلاحيات كل موظف** لكل وحدة بشكل منفصل (Toggle per module).
- يضبط: إعدادات الضرائب + تطبيق الحجز المباشر + Night Audit + أوقات الدخول/الخروج.
- لا يرى بيانات المنشآت الأخرى أبداً.
- يُنشأ حسابه من Admin.

### 3. EMPLOYEE — موظف المنشأة
- **حسابه يُنشأ حصراً من قِبل Manager منشأته.**
- صلاحياته تُحدَّد بدقة لكل وحدة (حجوزات، كاشير، تدبير منزلي...).
- لا يستطيع تعديل صلاحياته أو صلاحيات زملائه.
- يعمل فقط على المهام المسموحة صراحةً.
- لا يرى بيانات Manager أو Admin.
- يمكن تعطيل حسابه بواسطة Manager في أي وقت.

### 4. GUEST — الضيف (النزيل / العميل)
- مستخدم خارجي يحجز عبر **تطبيق الحجوزات المباشر** فقط.
- يسجل دخوله برقم الجوال + OTP — لا كلمة مرور.
- يستطيع: بحث + حجز + تتبع + إلغاء + تقييم.
- لا يرى أي شاشة إدارية.
- جلسته منفصلة تماماً: `{ type: 'guest' }` في الـ JWT.
- يحمي مساراته `GuestGuard`.

---

## ثالثاً: نظام الضرائب (مُحدَّث)

### أنواع الضرائب

| الضريبة | المعدل | النوع | من يتحكم فيها |
|---|---|---|---|
| ضريبة القيمة المضافة (VAT) | 15% | إجبارية — ثابتة بالنظام السعودي | النظام تلقائياً |
| رسوم السياحة | 2.5% (افتراضي) | **اختيارية** — يفعّلها/يعطّلها المدير | Manager من إعدادات المنشأة |

### منطق حساب الأسعار

```
base_price          = سعر الغرفة × عدد الليالي
discount_amount     = base_price × discount_rate  (إن وُجد خصم)
price_net           = base_price - discount_amount

tourism_tax_amount  = tourism_tax_enabled ? (price_net × tourism_tax_rate) : 0
vat_base            = price_net + tourism_tax_amount
vat_amount          = vat_base × 0.15
total_amount        = vat_base + vat_amount
```

### تفصيل الفاتورة (يظهر في كل حجز وفاتورة ZATCA)

```
سعر الغرفة (قبل الخصم):     X ر.س
الخصم (-X%):                - X ر.س   [يظهر فقط إن وُجد خصم]
السعر الصافي:                X ر.س
رسوم السياحة (2.5%):         X ر.س    [يظهر فقط إن كانت مفعّلة]
المجموع قبل الضريبة:          X ر.س
ضريبة القيمة المضافة (15%):  X ر.س
الإجمالي:                    X ر.س
```

### إعدادات الضرائب (Manager — منشأته فقط)

| الإعداد | النوع | الافتراضي | القيود |
|---|---|---|---|
| `tourism_tax_enabled` | BOOLEAN | false | Toggle — يفعّله Manager |
| `tourism_tax_rate` | DECIMAL | 0.0250 (2.5%) | قابل للتعديل: 0% – 10% |
| `vat_rate` | DECIMAL | 0.1500 (15%) | **ثابت** — غير قابل للتعديل |
| `vat_number` | VARCHAR | — | رقم التسجيل الضريبي في ZATCA |

### صلاحيات الضرائب الجديدة

```
tax_settings.view    → Admin + Manager
tax_settings.update  → Admin (الكل) + Manager (منشأته فقط)
```

### API الضرائب

| المسار | الطريقة | الوظيفة | الصلاحية |
|---|---|---|---|
| `/settings/tax` | GET | عرض إعدادات الضرائب | `tax_settings.view` |
| `/settings/tax` | PATCH | تحديث إعدادات (تفعيل/تعطيل السياحة) | `tax_settings.update` |
| `/bookings/:id/tax-breakdown` | GET | تفصيل الضرائب لحجز محدد | `bookings.read` |

---

## رابعاً: قاعدة البيانات (PostgreSQL + Prisma)

### جدول `users`

| الحقل | النوع | الغرض |
|---|---|---|
| id | UUID PK | معرف المستخدم |
| name | VARCHAR(100) | الاسم الكامل |
| email | VARCHAR UNIQUE | البريد الإلكتروني |
| phone | VARCHAR? | رقم الجوال |
| password_hash | VARCHAR | bcrypt rounds=12 |
| country | VARCHAR? | رمز الدولة ISO |
| city | VARCHAR? | المدينة |
| establishment_id | FK → establishments? | null للـ Admin |
| role_type | ENUM | ADMIN / MANAGER / EMPLOYEE |
| is_email_verified | BOOLEAN DEFAULT false | هل البريد مفعّل؟ |
| is_active | BOOLEAN DEFAULT true | حالة الحساب |
| is_deleted | BOOLEAN DEFAULT false | Soft Delete |
| deleted_at | TIMESTAMP? | تاريخ الحذف الناعم |
| failed_login_count | INT DEFAULT 0 | محاولات الدخول الفاشلة |
| locked_until | TIMESTAMP? | وقت إلغاء القفل |
| last_login_at | TIMESTAMP? | آخر دخول |
| created_at | TIMESTAMP DEFAULT NOW() | — |
| updated_at | TIMESTAMP AUTO | — |

### جدول `establishments`

| الحقل | النوع | الغرض |
|---|---|---|
| id | UUID PK | معرف المنشأة |
| serial_number | INT UNIQUE AUTO | رقم تسلسلي: 1، 2، 3... (للتجديد) |
| name | VARCHAR(200) | اسم المنشأة |
| slug | VARCHAR UNIQUE | للرابط: dheuof.com/book/{slug} |
| type | ENUM | HOTEL / APARTMENT / RESORT / CHALET |
| owner_id | FK → users | Manager المسؤول |
| country | VARCHAR DEFAULT 'SA' | رمز الدولة |
| city | VARCHAR? | المدينة |
| district | VARCHAR? | الحي |
| phone | VARCHAR? | هاتف المنشأة |
| subscription_status | ENUM | TRIAL / ACTIVE / EXPIRED / SUSPENDED |
| trial_ends_at | TIMESTAMP | تاريخ انتهاء التجربة (60 يوم من التسجيل) |
| subscription_ends_at | TIMESTAMP? | تاريخ انتهاء الاشتراك |
| is_active | BOOLEAN DEFAULT true | — |
| is_deleted | BOOLEAN DEFAULT false | Soft Delete |
| created_at | TIMESTAMP DEFAULT NOW() | — |

### جدول `tax_settings` (جديد)

| الحقل | النوع | الغرض |
|---|---|---|
| id | UUID PK | — |
| establishment_id | FK → establishments UNIQUE | منشأة واحدة = سجل ضرائب واحد |
| vat_rate | DECIMAL(5,4) DEFAULT 0.1500 | ضريبة القيمة المضافة (ثابتة 15%) |
| vat_number | VARCHAR? | رقم التسجيل الضريبي في ZATCA |
| tourism_tax_enabled | BOOLEAN DEFAULT false | تفعيل رسوم السياحة |
| tourism_tax_rate | DECIMAL(5,4) DEFAULT 0.0250 | معدل رسوم السياحة (2.5% افتراضي) |
| updated_by | FK → users? | آخر من عدّل الإعدادات |
| updated_at | TIMESTAMP AUTO | — |

### جدول `roles` و `permissions`

| الحقل | النوع | الغرض |
|---|---|---|
| roles.id / name / is_system | UUID / VARCHAR / BOOL | is_system يمنع الحذف |
| permissions.id / name / module | UUID / VARCHAR / VARCHAR | الصلاحيات مصنّفة بالوحدة |
| role_permissions | role_id + permission_id PK | ربط الأدوار بالصلاحيات |
| user_roles | user_id + role_id PK | ربط المستخدمين بالأدوار |
| user_permissions | user_id + permission_id | صلاحيات مخصصة إضافية |

### جدول `refresh_tokens` و Security Tokens

| الجدول | الحقول الرئيسية | الغرض |
|---|---|---|
| refresh_tokens | token_hash UNIQUE + expires_at + is_revoked | Refresh Token كـ Hash — لا نص صريح |
| password_reset_tokens | token_hash + is_used + expires_at | Single-Use — 30 دقيقة |
| email_verification_tokens | otp_hash + expires_at + is_used | OTP — 15 دقيقة |
| login_attempts | email + ip_address + is_success + attempted_at | تتبع محاولات الدخول |
| audit_logs | user_id + action + entity_type + old_value + new_value | سجل كل العمليات |

### جدول `room_types` و `rooms`

| الحقل | النوع | الغرض |
|---|---|---|
| room_types.id | UUID PK | معرف النوع |
| room_types.name | VARCHAR | اسم النوع (غرفة عادية، جناح...) |
| room_types.base_price | DECIMAL | السعر الأساسي للليلة |
| room_types.max_occupancy | INT | الحد الأقصى للأشخاص |
| room_types.amenities | VARCHAR[] | المرافق |
| rooms.id | UUID PK | معرف الغرفة |
| rooms.room_number | VARCHAR | رقم الغرفة |
| rooms.floor | INT? | الطابق |
| rooms.status | ENUM | AVAILABLE / OCCUPIED / DIRTY / MAINTENANCE / OUT_OF_ORDER |

### جدول `guests`

| الحقل | النوع | الغرض |
|---|---|---|
| id | UUID PK | معرف الضيف |
| establishment_id | FK | المنشأة |
| full_name | VARCHAR | الاسم الكامل |
| phone | VARCHAR UNIQUE per establishment | رقم الجوال (تسجيل الدخول) |
| email | VARCHAR? | البريد |
| country | VARCHAR? | الدولة |
| city | VARCHAR? | المدينة |
| id_number | VARCHAR? | رقم الهوية / الجواز |
| vip_level | ENUM DEFAULT NONE | NONE / SILVER / GOLD / PLATINUM |
| is_blacklisted | BOOLEAN DEFAULT false | قائمة الحظر |
| total_stays | INT DEFAULT 0 | عدد الإقامات |
| total_spent | DECIMAL DEFAULT 0 | إجمالي الإنفاق |
| created_at | TIMESTAMP | — |

### جدول `direct_bookings` (مع الضرائب)

| الحقل | النوع | الغرض |
|---|---|---|
| id | UUID PK | — |
| booking_ref | VARCHAR UNIQUE | DB-2025-XXXXX |
| establishment_id | FK | المنشأة |
| room_type_id | FK → room_types | نوع الغرفة |
| room_id | FK → rooms? | الغرفة الفعلية (عند الوصول) |
| guest_id | FK → guests? | ملف الضيف |
| guest_name | VARCHAR | اسم الضيف |
| guest_phone | VARCHAR | الجوال |
| guest_email | VARCHAR? | البريد |
| guest_country | VARCHAR? | الدولة |
| guest_city | VARCHAR? | المدينة |
| check_in_date | TIMESTAMP | تاريخ الدخول |
| check_out_date | TIMESTAMP | تاريخ الخروج |
| nights | INT | عدد الليالي |
| adults | INT | البالغون |
| children | INT DEFAULT 0 | الأطفال |
| base_price | DECIMAL | السعر الأساسي (قبل الخصم) |
| discount_type | ENUM? | DIRECT / EARLY_BIRD / LONG_STAY / PROMO |
| discount_pct | DECIMAL DEFAULT 0 | نسبة الخصم |
| discount_amount | DECIMAL DEFAULT 0 | مبلغ الخصم |
| price_net | DECIMAL | السعر الصافي (بعد الخصم) |
| **tourism_tax_enabled** | BOOLEAN | هل رسوم السياحة مفعّلة لهذا الحجز؟ |
| **tourism_tax_rate** | DECIMAL DEFAULT 0 | المعدل المطبَّق وقت الحجز |
| **tourism_tax_amount** | DECIMAL DEFAULT 0 | مبلغ رسوم السياحة |
| **vat_rate** | DECIMAL DEFAULT 0.15 | معدل VAT المطبَّق وقت الحجز |
| **vat_amount** | DECIMAL | مبلغ ضريبة القيمة المضافة |
| **total_amount** | DECIMAL | الإجمالي الكلي شاملاً جميع الضرائب |
| status | ENUM | PENDING / CONFIRMED / CHECKED_IN / CHECKED_OUT / CANCELLED / NO_SHOW |
| payment_status | ENUM | UNPAID / PARTIAL / PAID / REFUNDED |
| paid_amount | DECIMAL DEFAULT 0 | المبلغ المدفوع |
| payment_method | ENUM? | MADA / VISA / APPLE_PAY / CASH |
| promo_code | VARCHAR? | كود الخصم المستخدم |
| source | ENUM DEFAULT DIRECT | DIRECT / OTA_BOOKING / OTA_EXPEDIA / OTA_AIRBNB |
| special_requests | TEXT? | طلبات خاصة |
| created_at | TIMESTAMP | — |

### جداول PMS الإضافية

| الجدول | الحقول الأساسية | الغرض |
|---|---|---|
| booking_reviews | booking_id + overall + cleanliness + service + location + value (1-5) | تقييمات بعد الخروج |
| night_audit_settings | establishment_id + scheduled_time + default_check_in_time + default_check_out_time + require_payment_before_close | إعدادات Night Audit |
| night_audit_logs | establishment_id + audit_date + status + total_revenue + total_vat + total_tourism_tax + unsettled_count | سجل الإغلاق اليومي |
| payment_devices | establishment_id + device_name + device_type (POS/MADA/CASH_DRAWER) + is_active | أجهزة الدفع |
| payments | booking_id + device_id? + method + amount + status + settled_in_audit_id | المدفوعات |
| zatca_invoices | booking_id + invoice_number + invoice_type (SIMPLIFIED/CREDIT) + xml_signed + qr_tlv_base64 + qr_image_base64 + zatca_status + vat_amount + tourism_tax_amount | فواتير ZATCA |
| housekeeping_tasks | room_id + assigned_to + task_type + priority + status + due_at | مهام التدبير المنزلي |
| booking_app_settings | establishment_id + direct_discount + early_bird_discount + long_stay_discount + min_nights_long_stay + cancellation_policy + accepted_payments[] | إعدادات تطبيق الحجز |
| promotions | establishment_id + code UNIQUE + discount_type + discount_value + valid_from + valid_until + max_uses + used_count | كودات الخصم |
| subscriptions | establishment_id + serial_number + plan + starts_at + ends_at + amount_paid | سجل الاشتراكات |

---

## خامساً: قائمة الصلاحيات الكاملة (مخزنة في DB)

```
# المستخدمون
users.create / users.read / users.update / users.delete / users.activate

# الأدوار والصلاحيات
roles.create / roles.read / roles.update / roles.delete
permissions.assign

# اللوحة والتقارير
dashboard.view / dashboard.analytics
reports.view / reports.export

# الإعدادات والضرائب
settings.view / settings.update
tax_settings.view / tax_settings.update

# الملف الشخصي
profile.view / profile.update

# سجل التدقيق
audit_logs.view / audit_logs.export

# الغرف
rooms.create / rooms.read / rooms.update / rooms.delete / rooms.change_status

# الضيوف
guests.create / guests.read / guests.update / guests.blacklist / guests.vip_upgrade

# الحجوزات
bookings.create / bookings.read / bookings.update / bookings.delete
bookings.check_in / bookings.check_out / bookings.cancel

# Night Audit
night_audit.view / night_audit.run / night_audit.settings

# الفواتير (ZATCA)
invoices.create / invoices.view / invoices.export

# التدبير المنزلي
housekeeping.view / housekeeping.create / housekeeping.assign / housekeeping.complete

# تطبيق الحجز المباشر
booking_app.view / booking_app.settings / booking_app.promotions

# التقييمات
reviews.view / reviews.reply

# أجهزة الدفع
payment_devices.manage
```

### مصفوفة الصلاحيات الرئيسية

| الصلاحية | Admin | Manager | Employee | Guest |
|---|:---:|:---:|:---:|:---:|
| users.create/read/update/delete | ✅ | ✅ منشأته | ❌ | ❌ |
| permissions.assign | ✅ | ✅ لموظفيه | ❌ | ❌ |
| dashboard.view | ✅ | ✅ | ✅ محدود | ❌ |
| reports.view/export | ✅ | ✅ | ❌ | ❌ |
| **tax_settings.view** | ✅ | ✅ | ❌ | ❌ |
| **tax_settings.update** | ✅ | ✅ منشأته | ❌ | ❌ |
| settings.update | ✅ | ✅ منشأته | ❌ | ❌ |
| rooms.create/update/delete | ✅ | ✅ | ❌ | ❌ |
| rooms.read | ✅ | ✅ | ✅ | ❌ |
| guests.create/read | ✅ | ✅ | حسب الإعداد | ❌ |
| guests.blacklist/vip_upgrade | ✅ | ✅ | ❌ | ❌ |
| bookings.create/read/update | ✅ | ✅ | حسب الإعداد | ❌ |
| bookings.check_in/check_out | ✅ | ✅ | حسب الإعداد | ❌ |
| night_audit.run/settings | ✅ | ✅ | ❌ | ❌ |
| invoices.create/view/export | ✅ | ✅ | view فقط | ❌ |
| housekeeping.* | ✅ | ✅ | ✅ | ❌ |
| booking_app.settings/promotions | ✅ | ✅ | ❌ | ❌ |
| payment_devices.manage | ✅ | ✅ | ❌ | ❌ |
| audit_logs.view/export | ✅ | ✅ | ❌ | ❌ |
| profile.view/update | ✅ | ✅ | ✅ | ✅ |

---

## سادساً: وحدات النظام PMS

### 1. تطبيق الحجز المباشر (Direct Booking App)

رابط عام للعملاء: `dheuof.com/book/{establishment_slug}`

**الخصائص:**
- بحث عن غرف بالتاريخ وعدد الأشخاص
- حساب السعر تلقائياً مع تطبيق **جميع الضرائب**:
  - VAT 15% إجباري
  - رسوم السياحة 2.5% إن فعّلها Manager
- خصومات تلقائية (تُطبَّق على السعر الصافي قبل الضرائب):
  - **خصم الحجز المباشر** (افتراضي 5%) — لتجاوز عمولات OTA 15-25%
  - **خصم الحجز المبكر** (افتراضي 10% عند الحجز قبل 30 يوم)
  - **خصم الإقامة الطويلة** (افتراضي 15% من 7 ليالٍ)
  - **كودات خصم مخصصة** من Manager
- تسلسل عرض الأسعار لعميل الحجز:
  ```
  سعر الغرفة الأصلي: X ر.س
  الخصم: - X ر.س
  السعر الصافي: X ر.س
  رسوم السياحة: + X ر.س  [إن وُجدت]
  VAT 15%: + X ر.س
  الإجمالي: X ر.س
  ```
- الدفع: Moyasar (MADA + Visa + Apple Pay)
- تأكيد الحجز: QR Code + SMS + Email
- تتبع الحجز برقم الجوال — بدون تسجيل دخول
- إلغاء مع احتساب الاسترداد حسب سياسة المنشأة
- تقييم بعد الخروج (5 معايير × 5 نجوم)
- عرض توفير العميل مقارنةً بـ OTA

**إعدادات Manager لتطبيق الحجز:**
- تفعيل/تعطيل رسوم السياحة
- معدل رسوم السياحة (0–10%)
- نسب الخصومات الثلاثة
- سياسة الإلغاء
- الحد الأدنى للإقامة
- طرق الدفع المقبولة

### 2. Night Audit

**الخصائص:**
- وقت التشغيل اختياري — Manager يضبطه (افتراضي 23:59)
- Cron ديناميكي: يُعاد ضبطه تلقائياً عند تغيير الوقت
- تشغيل يدوي متاح لـ Manager
- **شرط التشغيل:** لا يعمل إذا كانت هناك مدفوعات معلّقة
- تحديث حالة الحجوزات: DUE_OUT → No-Show أو تمديد
- تثبيت الإيرادات (تشمل: السعر الصافي + رسوم السياحة + VAT) ومنع تعديلها
- توليد تقرير PDF يشمل:
  - إجمالي الإيرادات
  - إجمالي VAT المحصّل
  - **إجمالي رسوم السياحة المحصّلة** (إن كانت مفعّلة)
  - تفصيل أجهزة الدفع
- ربط أجهزة الدفع: POS + MADA + Visa + CASH_DRAWER
- تعديل وقت الدخول/الخروج الافتراضي: **Manager فقط**

### 3. ZATCA — الفاتورة الإلكترونية (مُحدَّثة بالضرائب)

**الخصائص:**
- إصدار فاتورة مبسّطة تلقائياً عند Check-out
- **بنود الفاتورة تشمل:**
  - السعر الصافي للغرفة
  - رسوم السياحة (سطر منفصل إن كانت مفعّلة)
  - مبلغ VAT (15% على القاعدة الضريبية = صافي + سياحة)
  - الإجمالي الكلي
- QR Code بمعيار TLV الرسمي من ZATCA (5 حقول مشفّرة Base64):
  1. اسم البائع
  2. رقم التسجيل الضريبي
  3. تاريخ ووقت الفاتورة
  4. إجمالي الفاتورة (شامل كل الضرائب)
  5. مبلغ VAT
- QR قابل للقراءة بأي جهاز + التحقق منه
- XML موقّع وفق UBL 2.1
- إرسال للـ ZATCA API (Sandbox → Production)
- صفحة Scanner بالكاميرا للتحقق من QR
- فاتورة دائن (Credit Note) عند الاسترداد

### 4. التقارير و KPI

**المؤشرات الحية (Real-time):**
- معدل الإشغال (Occupancy Rate)
- متوسط سعر الغرفة (ADR)
- الإيراد لكل غرفة متاحة (RevPAR)
- إجمالي الإيرادات اليومية
- **إجمالي VAT المحصّل يومياً**
- **إجمالي رسوم السياحة المحصّلة يومياً**

**التقارير:**
- تقرير الإشغال: يومي / أسبوعي / شهري
- تقرير الإيرادات: حسب المصدر + نوع الغرفة + طريقة الدفع
- **تقرير الضرائب:** VAT المحصّل + رسوم السياحة المحصّلة + الإجمالي لأي فترة
- تقرير الضيوف: توزيع الدول والمناطق (Shamoos)
- تقرير التقييمات: Radar Chart لـ 5 معايير
- توقعات الإشغال: 7 / 14 / 30 يوم
- تقرير الوفر من العمولات vs OTA
- تصدير كل تقرير: PDF أو Excel

### 5. Housekeeping (التدبير المنزلي)

- مهمة تنظيف تُنشأ تلقائياً عند كل Check-out
- حالة الغرفة تتغير: DIRTY → CLEAN
- لوحة Kanban: PENDING → IN_PROGRESS → DONE
- أنواع المهام: CLEANING / INSPECTION / MAINTENANCE / TURNDOWN
- أولوية: LOW / MEDIUM / HIGH / URGENT
- تعيين المهمة لموظف محدد

### 6. Channel Manager

- مزامنة التوفر مع: Booking.com + Airbnb + Expedia + Agoda
- تحديث التوفر تلقائياً عند كل حجز أو إلغاء
- استقبال حجوزات OTA عبر Webhook
- سجل نجاح/فشل كل عملية مزامنة
- Retry Queue للعمليات الفاشلة

---

## سابعاً: متطلبات الأمان

| المتطلب | التفاصيل |
|---|---|
| كلمات المرور | bcrypt rounds=12 أو argon2id — لا تخزين كنص صريح |
| JWT | Access Token 15 دقيقة (في الذاكرة) + Refresh Token 7 أيام (في DB كـ Hash) |
| Cookie | HttpOnly + Secure + SameSite=Strict + Path=/auth/refresh |
| Rate Limiting | 5 محاولات / 15 دقيقة لكل IP على مسارات Auth |
| قفل الحساب | 30 دقيقة بعد 5 محاولات فاشلة متتالية |
| رسالة الخطأ | "بيانات الدخول غير صحيحة" — لا يكشف سبب الفشل |
| SQL Injection | Prisma Parameterized Queries دائماً — لا Raw SQL |
| XSS | DOMPurify (Frontend) + sanitize-html (Backend) |
| CSRF | Double Submit Cookie Pattern أو SameSite=Strict |
| Input Validation | class-validator + class-transformer على كل DTO |
| Security Headers | Helmet.js في NestJS |
| CORS | Whitelist صريح — لا * في Production |
| Escalation | لا مستخدم يرفع صلاحياته بنفسه — OwnershipGuard |
| Admin Protection | لا يمكن حذف أو تعديل حساب Admin من أي حساب آخر |
| Row Isolation | Manager يرى منشأته فقط — EstablishmentContextInterceptor |
| Guest Isolation | GuestGuard — مسارات Guest لا تقبل Staff tokens |
| الأسرار | جميع المفاتيح في .env — لا في الكود |
| Audit Logs | كل عملية حساسة تُسجَّل تلقائياً بـ AuditLogInterceptor |
| Soft Delete | جميع الجداول الرئيسية: is_deleted + deleted_at |
| ZATCA Keys | شهادة + مفتاح ZATCA في .env فقط |
| Tax Integrity | معدل VAT ثابت في الكود — لا يُعدَّل من واجهة المستخدم |

---

## ثامناً: Guards المطلوبة

```typescript
JwtAuthGuard        // التحقق من Access Token
RolesGuard          // التحقق من الدور (ADMIN / MANAGER / EMPLOYEE)
PermissionsGuard    // التحقق من الصلاحية الفعلية
SubscriptionGuard   // التحقق من سريان الاشتراك أو التجربة
OwnershipGuard      // لا يعدّل المستخدم إلا ما يخصّه
GuestGuard          // مسارات الضيف — token.type === 'guest'
EstablishmentContextInterceptor  // يضبط establishment_id تلقائياً لكل request
```

---

## تاسعاً: واجهات API الكاملة

### المصادقة

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| POST | /auth/register | تسجيل منشأة جديدة + بدء تجربة 60 يوم | عام |
| POST | /auth/login | تسجيل الدخول + إصدار Tokens | عام |
| POST | /auth/logout | تسجيل الخروج + إلغاء Refresh Token | مسجّل |
| POST | /auth/refresh-token | تجديد Access Token | Cookie |
| POST | /auth/forgot-password | إرسال رابط إعادة التعيين | عام |
| POST | /auth/reset-password | تعيين كلمة مرور جديدة | Token |
| POST | /auth/verify-email | تفعيل البريد بـ OTP | عام |
| GET | /auth/me | بيانات المستخدم + أدواره + صلاحياته | مسجّل |

### المستخدمون والمنشآت

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /users | قائمة المستخدمين مع بحث وتصفية | users.read |
| POST | /users | إنشاء موظف جديد | users.create |
| PATCH | /users/:id | تعديل بيانات مستخدم | users.update |
| DELETE | /users/:id | حذف ناعم Soft Delete | users.delete |
| PATCH | /users/:id/activate | تفعيل الحساب | users.update |
| POST | /users/:id/assign-role | تعيين دور لمستخدم | permissions.assign |
| GET | /establishments | كل المنشآت — Admin فقط | Admin |
| POST | /subscriptions/renew | تجديد الاشتراك برقم المنشأة | settings.update |

### الإعدادات والضرائب

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /settings/tax | عرض إعدادات الضرائب | tax_settings.view |
| PATCH | /settings/tax | تحديث رسوم السياحة (تفعيل/تعطيل/معدل) | tax_settings.update |
| GET | /bookings/:id/tax-breakdown | تفصيل الضرائب لحجز محدد | bookings.read |
| GET | /reports/tax | تقرير الضرائب المحصّلة (VAT + سياحة) | reports.view |

### الأدوار والصلاحيات

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /roles | قائمة الأدوار | roles.read |
| POST | /roles | إنشاء دور جديد | roles.create |
| PATCH | /roles/:id | تعديل الدور | roles.update |
| DELETE | /roles/:id | حذف دور غير نظامي | roles.delete |
| GET | /permissions | قائمة الصلاحيات | permissions.read |
| POST | /roles/:id/permissions | ربط صلاحيات بدور | permissions.assign |
| DELETE | /roles/:id/permissions/:pid | إزالة صلاحية من دور | permissions.assign |

### PMS — الغرف والضيوف والحجوزات

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /rooms/availability | فحص التوفر ?checkIn&checkOut | rooms.read |
| POST | /rooms | إضافة غرفة جديدة | rooms.create |
| PATCH | /rooms/:id/status | تغيير حالة الغرفة | rooms.change_status |
| GET | /guests | قائمة الضيوف | guests.read |
| POST | /guests | تسجيل ضيف جديد | guests.create |
| GET | /guests/:id/history | سجل إقامات ضيف | guests.read |
| PATCH | /guests/:id/blacklist | إضافة لقائمة الحظر | guests.blacklist |
| GET | /bookings | قائمة الحجوزات | bookings.read |
| POST | /bookings | إنشاء حجز جديد (مع حساب الضرائب) | bookings.create |
| POST | /bookings/:id/check-in | تسجيل الدخول الفعلي | bookings.check_in |
| POST | /bookings/:id/check-out | تسجيل الخروج + فاتورة ZATCA | bookings.check_out |
| POST | /bookings/:id/review | تسجيل تقييم بعد الخروج | bookings.update |

### Night Audit + ZATCA + Housekeeping

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /night-audit/settings | عرض إعدادات Night Audit | night_audit.view |
| PATCH | /night-audit/settings | تعديل الإعدادات — Manager فقط | night_audit.settings |
| POST | /night-audit/run | تشغيل Night Audit يدوياً | night_audit.run |
| GET | /night-audit/:date/report | تقرير يوم محدد PDF | night_audit.view |
| POST | /zatca/invoices/:id/generate | إصدار فاتورة ZATCA (VAT + سياحة) | invoices.create |
| GET | /zatca/invoices/:id/qr | صورة QR للفاتورة | invoices.view |
| POST | /zatca/verify-qr | التحقق من QR — عام بدون JWT | عام |
| GET | /housekeeping | لوحة مهام التدبير | housekeeping.view |
| POST | /housekeeping | إنشاء مهمة تدبير | housekeeping.create |

### تطبيق الحجز المباشر (مع الضرائب)

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /book/:slug | صفحة المنشأة العامة | عام — بدون JWT |
| GET | /book/:slug/search | البحث + عرض السعر الكامل (صافي + ضرائب) | عام |
| POST | /book/:slug/check-promo | التحقق من كود خصم | عام |
| POST | /book/:slug/price-preview | معاينة السعر التفصيلي مع جميع الضرائب | عام |
| POST | /book/:slug/create | إنشاء حجز مباشر (يُحسب الضرائب من DB) | عام |
| POST | /book/:slug/payment | بدء عملية الدفع Moyasar | عام |
| GET | /book/my-booking | تتبع الحجز برقم الهاتف | عام |
| POST | /book/my-booking/cancel | إلغاء الحجز | عام |
| PATCH | /booking-app/settings | إعدادات تطبيق الحجز | booking_app.settings |
| POST | /booking-app/promotions | إنشاء كود خصم | booking_app.promotions |
| GET | /booking-app/savings-report | تقرير الوفر من العمولات | booking_app.view |

### التقارير و KPI

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /reports/kpis | مؤشرات KPI الحية (+ إجمالي الضرائب) | dashboard.analytics |
| GET | /reports/occupancy | تقرير الإشغال يومي/شهري | reports.view |
| GET | /reports/revenue | تقرير الإيرادات بالمصدر | reports.view |
| GET | /reports/tax | تقرير VAT + رسوم السياحة | reports.view |
| GET | /reports/guests | تقرير الضيوف بالدول والمناطق | reports.view |
| GET | /reports/reviews | تقرير التقييمات | reports.view |
| GET | /reports/forecast | توقعات الإشغال ?days=7/14/30 | reports.view |
| GET | /reports/savings | الوفر من العمولات vs OTA | reports.view |
| GET | /audit-logs | سجل التدقيق | audit_logs.view |

---

## عاشراً: الدول والمناطق

مكوّن مشترك `CountryRegionSelect.tsx` يُستخدم في:
- نموذج تسجيل المنشأة
- نموذج إنشاء حجز مباشر
- ملف الضيف
- إعدادات المنشأة
- تقرير الضيوف (Shamoos)

**السلوك:**
- عند اختيار المملكة العربية السعودية: قائمة منسدلة بالمناطق الـ 13
- عند اختيار دولة أخرى: حقل نصي حر
- المناطق السعودية الـ 13: الرياض / مكة المكرمة / المدينة المنورة / القصيم / المنطقة الشرقية / عسير / تبوك / حائل / الحدود الشمالية / جازان / نجران / الباحة / الجوف
- مخزنة ثابتة في `src/common/data/locations.ts` — لا DB

---

## حادي عشر: نظام الاشتراكات

- **فترة تجربة مجانية:** 60 يوماً تبدأ تلقائياً عند التسجيل
- **رقم تسلسلي:** يُولَّد تلقائياً (1، 2، 3...) لكل منشأة
- **التجديد:** برقم المنشأة التسلسلي فقط — Admin يجدّد
- **حالات الاشتراك:** TRIAL / ACTIVE / EXPIRED / SUSPENDED
- `SubscriptionGuard` يمنع الوصول عند انتهاء الاشتراك
- تحذيرات تلقائية قبل 7 أيام و3 أيام من الانتهاء

---

## ثاني عشر: هيكل المشروع

```
duyuf-platform/
├── apps/
│   ├── backend/  (NestJS)
│   │   └── src/
│   │       ├── auth/           -- المصادقة + strategies + DTOs
│   │       ├── users/          -- إدارة المستخدمين
│   │       ├── establishments/ -- المنشآت
│   │       ├── subscriptions/  -- الاشتراكات
│   │       ├── roles/          -- الأدوار
│   │       ├── permissions/    -- الصلاحيات
│   │       ├── tax-settings/   -- إعدادات الضرائب (جديد)
│   │       ├── rooms/          -- الغرف
│   │       ├── room-types/     -- أنواع الغرف
│   │       ├── guests/         -- ملفات الضيوف
│   │       ├── bookings/       -- الحجوزات (Staff)
│   │       ├── booking-app/    -- تطبيق الحجز المباشر
│   │       ├── night-audit/    -- Night Audit
│   │       ├── zatca/          -- ZATCA + QR
│   │       ├── housekeeping/   -- التدبير المنزلي
│   │       ├── reports/        -- التقارير و KPI
│   │       ├── audit-logs/     -- سجل التدقيق
│   │       ├── common/
│   │       │   ├── guards/     -- JwtAuth|Roles|Permissions|Subscription|Ownership|Guest
│   │       │   ├── interceptors/ -- AuditLog + EstablishmentContext
│   │       │   ├── services/   -- TaxCalculator (Service مشترك للضرائب)
│   │       │   └── data/       -- locations.ts (ثابت — لا DB)
│   │       ├── mail/ + sms/
│   │       └── prisma/
│   │           ├── schema.prisma
│   │           └── seed.ts
│   │
│   └── frontend/ (Next.js 14)
│       └── app/
│           ├── (auth)/         -- login|register|verify|forgot|reset
│           ├── (dashboard)/
│           │   ├── bookings/   -- + check-in + check-out + review
│           │   ├── settings/
│           │   │   └── tax/    -- إعدادات الضرائب (جديد)
│           │   ├── night-audit/
│           │   ├── zatca/scanner
│           │   ├── reports/    -- + تقرير الضرائب
│           │   └── booking-app/
│           ├── book/[slug]/    -- صفحات الحجز العامة (Public)
│           └── guest/          -- ملف الضيف (OTP)
```

### `TaxCalculatorService` (خدمة مشتركة)

```typescript
// src/common/services/tax-calculator.service.ts
@Injectable()
export class TaxCalculatorService {
  calculate(params: {
    base_price: number;
    discount_pct: number;
    tourism_tax_enabled: boolean;
    tourism_tax_rate: number;   // 0.025 افتراضي
    vat_rate: number;            // 0.15 ثابت
  }): TaxBreakdown {
    const price_net = base_price * (1 - discount_pct / 100);
    const tourism_tax_amount = tourism_tax_enabled
      ? price_net * tourism_tax_rate
      : 0;
    const vat_base = price_net + tourism_tax_amount;
    const vat_amount = vat_base * vat_rate;
    return {
      base_price,
      discount_amount: base_price - price_net,
      price_net,
      tourism_tax_amount,
      vat_amount,
      total_amount: vat_base + vat_amount,
    };
  }
}
```

---

## ثالث عشر: متغيرات البيئة (.env.example)

```env
# === Application ===
NODE_ENV=development
PORT=3001
APP_URL=http://localhost:3001
FRONTEND_URL=http://localhost:3000

# === Database ===
DATABASE_URL=postgresql://USER:PASS@localhost:5432/duyuf_db

# === JWT ===
JWT_ACCESS_SECRET=REPLACE_MIN_64_CHARS
JWT_ACCESS_EXPIRES_IN=15m
JWT_REFRESH_SECRET=REPLACE_DIFFERENT_MIN_64_CHARS
JWT_REFRESH_EXPIRES_IN=7d

# === Security ===
BCRYPT_SALT_ROUNDS=12
THROTTLE_TTL=900
THROTTLE_LIMIT=5
ACCOUNT_LOCK_MINUTES=30
TRIAL_DAYS=60
ADMIN_DEFAULT_PASSWORD=REPLACE_STRONG_PASS

# === Email (Zoho Mail) ===
MAIL_HOST=smtp.zoho.sa
MAIL_PORT=587
MAIL_USER=info@dheuof.com
MAIL_PASSWORD=REPLACE
MAIL_FROM="منصة ضيوف <info@dheuof.com>"

# === SMS ===
SMS_PROVIDER=unifonic
SMS_API_KEY=REPLACE

# === Payment ===
PAYMENT_GATEWAY=moyasar
MOYASAR_API_KEY=REPLACE
MOYASAR_WEBHOOK_SECRET=REPLACE

# === ZATCA ===
ZATCA_ENV=sandbox
ZATCA_VAT_NUMBER=REPLACE
ZATCA_CERTIFICATE=REPLACE
ZATCA_PRIVATE_KEY=REPLACE

# === Tax (System Defaults — المعدل الثابت في الكود فقط) ===
VAT_RATE=0.15
DEFAULT_TOURISM_TAX_RATE=0.025
```

---

## رابع عشر: ترتيب التنفيذ المقترح

| الخطوة | المرحلة | المحتوى |
|---|---|---|
| 1 | البنية الأساسية | NestJS + Next.js + Prisma + Docker + Auth + Guards |
| 2 | نظام المصادقة | Register + Login + OTP + JWT + Refresh Token + Rate Limiting |
| 3 | الأدوار والصلاحيات | Seed الأدوار والصلاحيات + RBAC Guards + لوحة الإدارة |
| 4 | الاشتراكات | Serial Number تلقائي + Trial 60 يوم + Subscription Guard |
| 5 | بيانات الدول والمناطق | locations.ts + CountryRegionSelect |
| 6 | **نظام الضرائب** | TaxCalculatorService + tax_settings Table + API + واجهة Manager |
| 7 | الغرف والضيوف | RoomTypes + Rooms + Guests + Room Map |
| 8 | الحجوزات (Staff) | Bookings + Check-in + Check-out + Review + حساب الضرائب |
| 9 | Night Audit | Settings + PaymentDevices + Cron ديناميكي + تقرير PDF (+ الضرائب) |
| 10 | ZATCA | TLV Builder + QR Generator + QR Scanner + ZATCA API (+ رسوم السياحة) |
| 11 | تطبيق الحجز المباشر | Public Pages + Pricing Engine (+ الضرائب) + Promotions + Payment |
| 12 | التقارير و KPI | Dashboard KPIs + تقرير الضرائب + 6 تقارير + تصدير PDF/Excel |
| 13 | Housekeeping | Kanban + Auto-create on Checkout |
| 14 | Channel Manager | مزامنة OTA + Webhook |
| 15 | Shamoos + Revenue Management | تقرير شهري + تسعير ديناميكي |

---

## خامس عشر: قائمة مراجعة ما قبل الإطلاق

### الأمان
- [ ] NODE_ENV=production في بيئة الإنتاج
- [ ] HTTPS + SSL Certificate فعّال
- [ ] تغيير كلمة مرور Admin الافتراضية فور أول تشغيل
- [ ] CORS بالنطاقات الصحيحة فقط
- [ ] .env لا يوجد في Git
- [ ] Refresh Token Rotation عند كل تجديد
- [ ] Rate Limiting فعّال على مسارات Auth
- [ ] Swagger Docs محظور في Production

### الضرائب (جديد)
- [ ] التحقق من أن VAT_RATE=0.15 ثابت لا يمكن تغييره من الواجهة
- [ ] اختبار حساب الضرائب: حجز بدون سياحة / بسياحة / بخصم + سياحة
- [ ] التحقق من عرض الضرائب بشكل صحيح في صفحة الحجز المباشر
- [ ] التحقق من أن فاتورة ZATCA تشمل رسوم السياحة كسطر منفصل
- [ ] اختبار تقرير الضرائب لفترة مخصصة
- [ ] اختبار Night Audit: إجمالي رسوم السياحة محسوب بشكل صحيح

### قاعدة البيانات
- [ ] Prisma Migrations نُفّذت بنجاح في Production
- [ ] Seed Data: أدوار + صلاحيات + Admin + tax_settings افتراضية
- [ ] Database Connection Pooling (PgBouncer)
- [ ] Backup تلقائي يومي

### الوظائف
- [ ] اختبار Night Audit في Staging أولاً
- [ ] اختبار ZATCA في Sandbox قبل Production
- [ ] اختبار بوابة الدفع Moyasar
- [ ] اختبار إرسال SMS + البريد الإلكتروني
- [ ] اختبار QR Scanner على Android + iOS
- [ ] اختبار جميع سيناريوهات الصلاحيات

---

## سادس عشر: بروتوكول التحقق الداخلي

| السؤال | الإجابة |
|---|---|
| هل VAT ثابت 15% ولا يمكن تغييره؟ | ✅ ثابت في الكود + TaxCalculatorService |
| هل رسوم السياحة اختيارية لكل منشأة؟ | ✅ Manager يفعّلها/يعطّلها من الإعدادات |
| هل الضرائب محسوبة بشكل صحيح في ZATCA؟ | ✅ رسوم السياحة سطر منفصل في XML |
| هل نظام تسجيل الدخول آمن؟ | ✅ bcrypt + Rate Limiting + قفل الحساب |
| هل الأدوار منفصلة عن الصلاحيات؟ | ✅ جداول منفصلة + DB-driven |
| هل تم منع التصعيد غير المشروع؟ | ✅ OwnershipGuard + EstablishmentContext |
| هل Admin يرى جميع البيانات؟ | ✅ لوحة Admin: إجمالي كل المنشآت |
| هل الموظفون يُنشأون من Manager فقط؟ | ✅ مقيّد بـ EstablishmentContextInterceptor |
| هل تطبيق الحجز يعرض الضرائب بوضوح؟ | ✅ تفصيل كامل: صافي + سياحة + VAT + إجمالي |
| هل Night Audit يحسب الضرائب؟ | ✅ تقرير يشمل VAT + رسوم السياحة |
| هل الكود قابل للصيانة والتوسع؟ | ✅ طبقات واضحة + TaxCalculatorService مشترك |

---

**أخرج النسخة النهائية المنظمة الكاملة القابلة للتنفيذ مباشرة، مع الكود الكامل لكل مكون، مصقولاً ومرتباً بالترتيب الموضح في هذا البرومبت. ابدأ بـ TaxCalculatorService ثم tax_settings Migration ثم ربط الضريبة بكل وحدة.**
