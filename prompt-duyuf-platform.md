# برومبت منصة ضيوف — النسخة الكاملة النهائية

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
- يضبط: **إعدادات الضرائب (من يتحمل الضريبة)** + تطبيق الحجز المباشر + Night Audit + أوقات الدخول/الخروج.
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

## ثالثاً: نظام الضرائب

### مبدأ أساسي

**الضريبة إجبارية حسابياً دائماً** — تُحسب وتُرفع لـ ZATCA في جميع الأحوال.
**لكن المدير يختار: هل يتحملها الضيف أم المنشأة؟**

- `على الضيف (افتراضي)`: الضريبة تُضاف فوق السعر الصافي → الإجمالي أعلى.
- `تتحملها المنشأة`: الضريبة تُستخرج من داخل السعر → الإجمالي للضيف لا يتغير، والمنشأة تتحمل الفرق.

### أنواع الضرائب

| الضريبة | المعدل | الإجبارية | من يتحكم في التحميل |
|---|---|---|---|
| ضريبة القيمة المضافة (VAT) | 15% | **إجبارية دائماً** — تُحسب وتُرفع لـ ZATCA | Manager: على الضيف أم المنشأة؟ |
| رسوم السياحة | 2.5% (افتراضي) | **اختيارية** — يفعّلها المدير | Manager: تفعيل/تعطيل + على الضيف أم المنشأة؟ |

### منطق حساب الأسعار

```
─── المشترك في الحالتين ───────────────────────────────────────
base_price         = سعر الغرفة × عدد الليالي
discount_amount    = base_price × discount_rate
price_net          = base_price - discount_amount
tourism_tax_amount = tourism_tax_enabled ? (price_net × tourism_tax_rate) : 0

─── الحالة A: المنشأة تمرّر الضريبة للضيف (افتراضي) ──────────
vat_base           = price_net + tourism_tax_amount
vat_amount         = vat_base × 0.15
total_amount       = vat_base + vat_amount             ← الضيف يدفع هذا

─── الحالة B: المنشأة تتحمل الضريبة ───────────────────────────
total_amount       = price_net + tourism_tax_amount    ← الضيف يدفع هذا فقط
vat_base           = total_amount / 1.15               ← تُستخرج داخلياً لـ ZATCA
vat_amount         = total_amount - vat_base           ← المنشأة تتحمله
```

> **قاعدة التحقق:** في كلتا الحالتين `vat_amount` يُرسل لـ ZATCA — لا فرق في الالتزام الضريبي، الفرق فقط في من يدفع.

### تفصيل الفاتورة

```
─── الحالة A: على الضيف ─────────────────────────────────────
سعر الغرفة (قبل الخصم):         X ر.س
الخصم (-X%):                    - X ر.س    [يظهر فقط إن وُجد]
السعر الصافي:                    X ر.س
رسوم السياحة (2.5%):             X ر.س    [يظهر فقط إن فُعّلت]
المجموع قبل الضريبة:              X ر.س
ضريبة القيمة المضافة (15%):      X ر.س
الإجمالي:                        X ر.س

─── الحالة B: المنشأة تتحمل ──────────────────────────────────
سعر الغرفة (قبل الخصم):         X ر.س
الخصم (-X%):                    - X ر.س    [يظهر فقط إن وُجد]
السعر الصافي:                    X ر.س
رسوم السياحة (2.5%):             X ر.س    [يظهر فقط إن فُعّلت]
الإجمالي (شامل الضريبة):         X ر.س
ضريبة القيمة المضافة مشمولة:     X ر.س    [سطر إعلامي فقط]
```

### إعدادات الضرائب (Manager — منشأته فقط)

| الإعداد | النوع | الافتراضي | الوصف |
|---|---|---|---|
| `vat_rate` | DECIMAL(5,4) | 0.1500 | **ثابت** — غير قابل للتعديل |
| `vat_on_guest` | BOOLEAN | true | true = الضيف يدفع VAT / false = المنشأة تتحمله |
| `tourism_tax_enabled` | BOOLEAN | false | تفعيل رسوم السياحة |
| `tourism_tax_rate` | DECIMAL(5,4) | 0.0250 | قابل للتعديل: 0% – 10% |
| `tourism_tax_on_guest` | BOOLEAN | true | true = الضيف يدفع / false = المنشأة تتحمله (فقط إن مفعّلة) |
| `vat_number` | VARCHAR | — | رقم التسجيل الضريبي في ZATCA |

### صلاحيات الضرائب

```
tax_settings.view    → Admin + Manager
tax_settings.update  → Admin (الكل) + Manager (منشأته فقط)
```

### API الضرائب

| المسار | الطريقة | الوظيفة | الصلاحية |
|---|---|---|---|
| `/settings/tax` | GET | عرض إعدادات الضرائب | `tax_settings.view` |
| `/settings/tax` | PATCH | تحديث (من يتحمل VAT/السياحة، تفعيل/تعطيل) | `tax_settings.update` |
| `/bookings/:id/tax-breakdown` | GET | تفصيل الضرائب لحجز محدد | `bookings.read` |
| `/reports/tax` | GET | تقرير الضرائب المحصّلة (VAT + سياحة) | `reports.view` |

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
| trial_ends_at | TIMESTAMP | تاريخ انتهاء التجربة (60 يوم) |
| subscription_ends_at | TIMESTAMP? | تاريخ انتهاء الاشتراك |
| is_active | BOOLEAN DEFAULT true | — |
| is_deleted | BOOLEAN DEFAULT false | Soft Delete |
| created_at | TIMESTAMP DEFAULT NOW() | — |

### جدول `tax_settings`

| الحقل | النوع | الغرض |
|---|---|---|
| id | UUID PK | — |
| establishment_id | FK → establishments UNIQUE | منشأة واحدة = سجل ضرائب واحد |
| vat_rate | DECIMAL(5,4) DEFAULT 0.1500 | ثابت 15% — يُقرأ فقط |
| **vat_on_guest** | BOOLEAN DEFAULT true | true = الضيف يدفع VAT / false = المنشأة تتحمله |
| vat_number | VARCHAR? | رقم التسجيل الضريبي في ZATCA |
| tourism_tax_enabled | BOOLEAN DEFAULT false | تفعيل رسوم السياحة |
| tourism_tax_rate | DECIMAL(5,4) DEFAULT 0.0250 | معدل رسوم السياحة |
| **tourism_tax_on_guest** | BOOLEAN DEFAULT true | true = الضيف يدفع / false = المنشأة تتحمل (إن فُعّلت) |
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

### جدول `direct_bookings`

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
| tourism_tax_enabled | BOOLEAN | هل رسوم السياحة مفعّلة لهذا الحجز؟ |
| tourism_tax_on_guest | BOOLEAN | هل الضيف يتحملها؟ |
| tourism_tax_rate | DECIMAL DEFAULT 0 | المعدل المطبَّق وقت الحجز |
| tourism_tax_amount | DECIMAL DEFAULT 0 | مبلغ رسوم السياحة |
| vat_rate | DECIMAL DEFAULT 0.15 | معدل VAT وقت الحجز |
| vat_on_guest | BOOLEAN DEFAULT true | هل الضيف يتحمل VAT؟ |
| vat_amount | DECIMAL | مبلغ ضريبة القيمة المضافة |
| total_amount | DECIMAL | الإجمالي الذي يدفعه الضيف فعلياً |
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
| night_audit_logs | establishment_id + audit_date + status + total_revenue + total_vat + total_tourism_tax + total_vat_absorbed + total_tourism_absorbed + unsettled_count | سجل الإغلاق اليومي |
| payment_devices | establishment_id + device_name + device_type (POS/MADA/CASH_DRAWER) + is_active | أجهزة الدفع |
| payments | booking_id + device_id? + method + amount + status + settled_in_audit_id | المدفوعات |
| zatca_invoices | booking_id + invoice_number + invoice_type (SIMPLIFIED/CREDIT) + xml_signed + qr_tlv_base64 + qr_image_base64 + zatca_status + vat_amount + tourism_tax_amount + vat_absorbed | فواتير ZATCA |
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
| tax_settings.view | ✅ | ✅ | ❌ | ❌ |
| tax_settings.update | ✅ | ✅ منشأته | ❌ | ❌ |
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
- حساب السعر تلقائياً مع تطبيق **جميع الضرائب** حسب إعدادات المنشأة
- خصومات تلقائية (تُطبَّق على السعر الصافي قبل الضرائب):
  - **خصم الحجز المباشر** (افتراضي 5%)
  - **خصم الحجز المبكر** (افتراضي 10% قبل 30 يوم)
  - **خصم الإقامة الطويلة** (افتراضي 15% من 7 ليالٍ)
  - **كودات خصم مخصصة** من Manager
- تسلسل عرض الأسعار (يتكيف حسب `vat_on_guest` و `tourism_tax_on_guest`):
  ```
  ─── الحالة A: المنشأة تمرّر الضرائب للضيف ─────────
  سعر الغرفة الأصلي:   X ر.س
  الخصم:               - X ر.س
  السعر الصافي:         X ر.س
  رسوم السياحة:        + X ر.س  [إن وُجدت وعلى الضيف]
  VAT 15%:             + X ر.س  [إن على الضيف]
  الإجمالي:             X ر.س

  ─── الحالة B: المنشأة تتحمل الضرائب ───────────────
  سعر الغرفة الأصلي:   X ر.س
  الخصم:               - X ر.س
  السعر الصافي:         X ر.س
  الإجمالي (شامل الضريبة): X ر.س
  ضريبة مشمولة:        X ر.س  [سطر إعلامي]
  ```
- الدفع: Moyasar (MADA + Visa + Apple Pay)
- تأكيد الحجز: QR Code + SMS + Email
- تتبع الحجز برقم الجوال — بدون تسجيل دخول
- إلغاء مع احتساب الاسترداد حسب سياسة المنشأة
- تقييم بعد الخروج (5 معايير × 5 نجوم)

**إعدادات Manager لتطبيق الحجز:**
- تحديد من يتحمل VAT (الضيف أم المنشأة)
- تفعيل/تعطيل رسوم السياحة + تحديد من يتحملها
- معدل رسوم السياحة (0–10%)
- نسب الخصومات الثلاثة
- سياسة الإلغاء + الحد الأدنى للإقامة
- طرق الدفع المقبولة

### 2. Night Audit

**الخصائص:**
- وقت التشغيل اختياري — Manager يضبطه (افتراضي 23:59)
- Cron ديناميكي: يُعاد ضبطه تلقائياً عند تغيير الوقت
- تشغيل يدوي متاح لـ Manager
- **شرط التشغيل:** لا يعمل إذا كانت هناك مدفوعات معلّقة
- تحديث حالة الحجوزات: DUE_OUT → No-Show أو تمديد
- تثبيت الإيرادات ومنع تعديلها
- توليد تقرير PDF يشمل:
  - إجمالي الإيرادات (ما دفعه الضيوف فعلياً)
  - إجمالي VAT المحصّل
  - إجمالي رسوم السياحة المحصّلة
  - **إجمالي الضرائب التي تحملتها المنشأة** (إن وُجدت)
  - تفصيل أجهزة الدفع

### 3. ZATCA — الفاتورة الإلكترونية

**الخصائص:**
- إصدار فاتورة مبسّطة تلقائياً عند Check-out
- **بنود الفاتورة تشمل دائماً (بغض النظر عمّن يتحمل):**
  - السعر الصافي للغرفة
  - رسوم السياحة (سطر منفصل إن كانت مفعّلة)
  - مبلغ VAT (15% على القاعدة الضريبية)
  - الإجمالي
  - ملاحظة إن كانت الضريبة مشمولة في السعر
- QR Code بمعيار TLV الرسمي من ZATCA (5 حقول):
  1. اسم البائع
  2. رقم التسجيل الضريبي
  3. تاريخ ووقت الفاتورة
  4. إجمالي الفاتورة (القاعدة الضريبية الكاملة)
  5. مبلغ VAT
- XML موقّع وفق UBL 2.1
- إرسال للـ ZATCA API (Sandbox → Production)
- فاتورة دائن (Credit Note) عند الاسترداد

### 4. التقارير و KPI

**المؤشرات الحية:**
- معدل الإشغال (Occupancy Rate)
- متوسط سعر الغرفة (ADR)
- الإيراد لكل غرفة متاحة (RevPAR)
- إجمالي الإيرادات اليومية
- إجمالي VAT المحصّل (مدفوع من الضيف + مُتحمَّل من المنشأة)
- إجمالي رسوم السياحة

**التقارير:**
- تقرير الإشغال: يومي / أسبوعي / شهري
- تقرير الإيرادات: حسب المصدر + نوع الغرفة + طريقة الدفع
- **تقرير الضرائب:** VAT + سياحة + مُتحمَّل من المنشأة + إجمالي أي فترة
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

### 6. Channel Manager

- مزامنة التوفر مع: Booking.com + Airbnb + Expedia + Agoda
- تحديث التوفر تلقائياً عند كل حجز أو إلغاء
- استقبال حجوزات OTA عبر Webhook
- Retry Queue للعمليات الفاشلة

---

## سابعاً: متطلبات الأمان

| المتطلب | التفاصيل |
|---|---|
| كلمات المرور | bcrypt rounds=12 — لا تخزين كنص صريح |
| JWT | Access Token 15 دقيقة (في الذاكرة) + Refresh Token 7 أيام (في DB كـ Hash) |
| Cookie | HttpOnly + Secure + SameSite=Strict + Path=/auth/refresh |
| Rate Limiting | 5 محاولات / 15 دقيقة لكل IP على مسارات Auth |
| قفل الحساب | 30 دقيقة بعد 5 محاولات فاشلة متتالية |
| رسالة الخطأ | "بيانات الدخول غير صحيحة" — لا يكشف سبب الفشل |
| SQL Injection | Prisma Parameterized Queries دائماً |
| XSS | DOMPurify (Frontend) + sanitize-html (Backend) |
| CSRF | Double Submit Cookie أو SameSite=Strict |
| Input Validation | class-validator + class-transformer على كل DTO |
| Security Headers | Helmet.js في NestJS |
| CORS | Whitelist صريح — لا * في Production |
| Escalation | OwnershipGuard — لا مستخدم يرفع صلاحياته بنفسه |
| Admin Protection | لا يمكن حذف أو تعديل Admin من أي حساب آخر |
| Row Isolation | EstablishmentContextInterceptor — Manager يرى منشأته فقط |
| Guest Isolation | GuestGuard — مسارات Guest لا تقبل Staff tokens |
| Tax Integrity | vat_rate ثابت في الكود — لا يُعدَّل من الواجهة / Manager يتحكم في التحميل فقط |
| Audit Logs | كل عملية حساسة تُسجَّل بـ AuditLogInterceptor |
| Soft Delete | جميع الجداول الرئيسية: is_deleted + deleted_at |
| ZATCA Keys | شهادة + مفتاح ZATCA في .env فقط |

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
| GET | /users | قائمة المستخدمين | users.read |
| POST | /users | إنشاء موظف جديد | users.create |
| PATCH | /users/:id | تعديل بيانات مستخدم | users.update |
| DELETE | /users/:id | حذف ناعم | users.delete |
| PATCH | /users/:id/activate | تفعيل الحساب | users.update |
| POST | /users/:id/assign-role | تعيين دور لمستخدم | permissions.assign |
| GET | /establishments | كل المنشآت — Admin فقط | Admin |
| POST | /subscriptions/renew | تجديد الاشتراك برقم المنشأة | settings.update |

### الإعدادات والضرائب

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /settings/tax | عرض إعدادات الضرائب | tax_settings.view |
| PATCH | /settings/tax | تحديث (vat_on_guest / tourism_tax_on_guest / tourism_tax_enabled) | tax_settings.update |
| GET | /bookings/:id/tax-breakdown | تفصيل الضرائب لحجز محدد | bookings.read |
| GET | /reports/tax | تقرير الضرائب (VAT + سياحة + مُتحمَّل من المنشأة) | reports.view |

### PMS — الغرف والضيوف والحجوزات

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /rooms/availability | فحص التوفر | rooms.read |
| POST | /rooms | إضافة غرفة | rooms.create |
| PATCH | /rooms/:id/status | تغيير حالة الغرفة | rooms.change_status |
| GET | /guests | قائمة الضيوف | guests.read |
| POST | /guests | تسجيل ضيف | guests.create |
| GET | /guests/:id/history | سجل إقامات ضيف | guests.read |
| PATCH | /guests/:id/blacklist | إضافة لقائمة الحظر | guests.blacklist |
| GET | /bookings | قائمة الحجوزات | bookings.read |
| POST | /bookings | إنشاء حجز (يُحسب الضرائب حسب إعدادات المنشأة) | bookings.create |
| POST | /bookings/:id/check-in | تسجيل الدخول الفعلي | bookings.check_in |
| POST | /bookings/:id/check-out | تسجيل الخروج + فاتورة ZATCA | bookings.check_out |
| POST | /bookings/:id/review | تسجيل تقييم | bookings.update |

### Night Audit + ZATCA + Housekeeping

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /night-audit/settings | عرض إعدادات Night Audit | night_audit.view |
| PATCH | /night-audit/settings | تعديل الإعدادات | night_audit.settings |
| POST | /night-audit/run | تشغيل يدوي | night_audit.run |
| GET | /night-audit/:date/report | تقرير يوم محدد PDF | night_audit.view |
| POST | /zatca/invoices/:id/generate | إصدار فاتورة ZATCA | invoices.create |
| GET | /zatca/invoices/:id/qr | صورة QR للفاتورة | invoices.view |
| POST | /zatca/verify-qr | التحقق من QR — عام | عام |
| GET | /housekeeping | لوحة مهام التدبير | housekeeping.view |
| POST | /housekeeping | إنشاء مهمة | housekeeping.create |

### تطبيق الحجز المباشر

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /book/:slug | صفحة المنشأة العامة | عام |
| GET | /book/:slug/search | بحث + عرض السعر حسب إعدادات الضرائب | عام |
| POST | /book/:slug/check-promo | التحقق من كود خصم | عام |
| POST | /book/:slug/price-preview | معاينة السعر التفصيلي (يتكيف مع vat_on_guest) | عام |
| POST | /book/:slug/create | إنشاء حجز مباشر | عام |
| POST | /book/:slug/payment | بدء عملية الدفع Moyasar | عام |
| GET | /book/my-booking | تتبع الحجز برقم الهاتف | عام |
| POST | /book/my-booking/cancel | إلغاء الحجز | عام |
| PATCH | /booking-app/settings | إعدادات تطبيق الحجز | booking_app.settings |
| POST | /booking-app/promotions | إنشاء كود خصم | booking_app.promotions |

### التقارير و KPI

| الطريقة | المسار | الوظيفة | الصلاحية |
|---|---|---|---|
| GET | /reports/kpis | مؤشرات KPI الحية | dashboard.analytics |
| GET | /reports/occupancy | تقرير الإشغال | reports.view |
| GET | /reports/revenue | تقرير الإيرادات | reports.view |
| GET | /reports/tax | تقرير VAT + سياحة + مُتحمَّل | reports.view |
| GET | /reports/guests | تقرير الضيوف | reports.view |
| GET | /reports/reviews | تقرير التقييمات | reports.view |
| GET | /reports/forecast | توقعات الإشغال | reports.view |
| GET | /audit-logs | سجل التدقيق | audit_logs.view |

---

## عاشراً: الدول والمناطق

مكوّن مشترك `CountryRegionSelect.tsx`:
- عند اختيار المملكة: قائمة منسدلة بالمناطق الـ 13
- عند اختيار دولة أخرى: حقل نصي حر
- **المناطق الـ 13:** الرياض / مكة المكرمة / المدينة المنورة / القصيم / المنطقة الشرقية / عسير / تبوك / حائل / الحدود الشمالية / جازان / نجران / الباحة / الجوف
- مخزنة ثابتة في `src/common/data/locations.ts` — لا DB

---

## حادي عشر: نظام الاشتراكات

- **فترة تجربة مجانية:** 60 يوماً تبدأ تلقائياً عند التسجيل
- **رقم تسلسلي:** يُولَّد تلقائياً لكل منشأة
- **التجديد:** برقم المنشأة التسلسلي — Admin يجدّد
- **حالات:** TRIAL / ACTIVE / EXPIRED / SUSPENDED
- `SubscriptionGuard` يمنع الوصول عند الانتهاء
- تحذيرات تلقائية قبل 7 أيام و3 أيام

---

## ثاني عشر: هيكل المشروع

```
duyuf-platform/
├── apps/
│   ├── backend/  (NestJS)
│   │   └── src/
│   │       ├── auth/
│   │       ├── users/
│   │       ├── establishments/
│   │       ├── subscriptions/
│   │       ├── roles/
│   │       ├── permissions/
│   │       ├── tax-settings/        ← إعدادات الضرائب
│   │       ├── rooms/
│   │       ├── room-types/
│   │       ├── guests/
│   │       ├── bookings/
│   │       ├── booking-app/
│   │       ├── night-audit/
│   │       ├── zatca/
│   │       ├── housekeeping/
│   │       ├── reports/
│   │       ├── audit-logs/
│   │       ├── common/
│   │       │   ├── guards/
│   │       │   ├── interceptors/
│   │       │   ├── services/        ← TaxCalculatorService
│   │       │   └── data/            ← locations.ts
│   │       ├── mail/ + sms/
│   │       └── prisma/
│   │
│   └── frontend/ (Next.js 14)
│       └── app/
│           ├── (auth)/
│           ├── (dashboard)/
│           │   ├── bookings/
│           │   ├── settings/
│           │   │   └── tax/         ← إعدادات الضرائب
│           │   ├── night-audit/
│           │   ├── zatca/scanner
│           │   ├── reports/
│           │   └── booking-app/
│           ├── book/[slug]/
│           └── guest/
```

### `TaxCalculatorService` (خدمة مشتركة)

```typescript
// src/common/services/tax-calculator.service.ts
export interface TaxBreakdown {
  base_price: number;
  discount_amount: number;
  price_net: number;
  tourism_tax_amount: number;   // دائماً يُحسب — صفر إن معطّلة
  vat_amount: number;           // دائماً يُحسب — لـ ZATCA
  total_amount: number;         // ما يدفعه الضيف فعلياً
  vat_absorbed: number;         // ما تتحمله المنشأة من VAT (للتقارير)
  tourism_absorbed: number;     // ما تتحمله المنشأة من السياحة (للتقارير)
}

@Injectable()
export class TaxCalculatorService {
  calculate(params: {
    base_price: number;
    discount_pct: number;
    vat_rate: number;              // 0.15 ثابت
    vat_on_guest: boolean;         // true = الضيف يدفع / false = المنشأة تتحمل
    tourism_tax_enabled: boolean;
    tourism_tax_rate: number;      // 0.025 افتراضي
    tourism_tax_on_guest: boolean; // true = الضيف يدفع / false = المنشأة تتحمل
  }): TaxBreakdown {
    const { base_price, discount_pct, vat_rate,
            vat_on_guest, tourism_tax_enabled,
            tourism_tax_rate, tourism_tax_on_guest } = params;

    const price_net = base_price * (1 - discount_pct / 100);
    const discount_amount = base_price - price_net;

    // رسوم السياحة (إن فُعّلت)
    const raw_tourism = tourism_tax_enabled ? price_net * tourism_tax_rate : 0;
    const tourism_tax_amount = tourism_tax_on_guest ? raw_tourism : 0; // ما يدفعه الضيف
    const tourism_absorbed   = tourism_tax_on_guest ? 0 : raw_tourism; // ما تتحمله المنشأة

    // حساب VAT
    if (vat_on_guest) {
      // الضيف يدفع VAT فوق السعر
      const vat_base   = price_net + raw_tourism;
      const vat_amount = vat_base * vat_rate;
      return {
        base_price, discount_amount, price_net,
        tourism_tax_amount: raw_tourism,
        vat_amount,
        total_amount: vat_base + vat_amount,
        vat_absorbed: 0,
        tourism_absorbed,
      };
    } else {
      // المنشأة تتحمل VAT — يُستخرج من داخل السعر
      const guest_subtotal = price_net + tourism_tax_amount; // ما يدفعه الضيف
      const vat_base       = guest_subtotal / (1 + vat_rate);
      const vat_amount     = guest_subtotal - vat_base;
      return {
        base_price, discount_amount, price_net,
        tourism_tax_amount,
        vat_amount,
        total_amount: guest_subtotal,
        vat_absorbed: vat_amount,
        tourism_absorbed,
      };
    }
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

# === Tax (معدلات ثابتة — لا تتغير من الواجهة) ===
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
| **6** | **نظام الضرائب** | **TaxCalculatorService + tax_settings Migration + API + واجهة Manager** |
| 7 | الغرف والضيوف | RoomTypes + Rooms + Guests + Room Map |
| 8 | الحجوزات (Staff) | Bookings + Check-in + Check-out + Review + حساب الضرائب |
| 9 | Night Audit | Settings + PaymentDevices + Cron ديناميكي + تقرير PDF |
| 10 | ZATCA | TLV Builder + QR Generator + QR Scanner + ZATCA API |
| 11 | تطبيق الحجز المباشر | Public Pages + Pricing Engine + Promotions + Payment |
| 12 | التقارير و KPI | Dashboard KPIs + تقرير الضرائب + 6 تقارير + تصدير PDF/Excel |
| 13 | Housekeeping | Kanban + Auto-create on Checkout |
| 14 | Channel Manager | مزامنة OTA + Webhook |
| 15 | Shamoos + Revenue Management | تقرير شهري + تسعير ديناميكي |

---

## خامس عشر: قائمة مراجعة ما قبل الإطلاق

### الأمان
- [ ] NODE_ENV=production
- [ ] HTTPS + SSL Certificate
- [ ] تغيير كلمة مرور Admin الافتراضية فور أول تشغيل
- [ ] CORS بالنطاقات الصحيحة فقط
- [ ] .env لا يوجد في Git
- [ ] Refresh Token Rotation فعّال
- [ ] Rate Limiting فعّال
- [ ] Swagger Docs محظور في Production

### الضرائب
- [ ] التحقق من أن VAT_RATE=0.15 ثابت — لا يُعدَّل من الواجهة
- [ ] اختبار الحالة A: الضيف يدفع VAT + سياحة
- [ ] اختبار الحالة B: المنشأة تتحمل VAT — الإجمالي للضيف لا يشمل VAT
- [ ] اختبار الحالة C: الضيف يدفع VAT + المنشأة تتحمل السياحة
- [ ] التحقق من أن ZATCA تتضمن vat_amount الصحيح في جميع الحالات
- [ ] اختبار Night Audit: عمود total_vat_absorbed محسوب بشكل صحيح
- [ ] اختبار تقرير الضرائب: الضرائب المُتحمَّلة من المنشأة تظهر منفصلة

### قاعدة البيانات
- [ ] Prisma Migrations نُفّذت في Production
- [ ] Seed: أدوار + صلاحيات + Admin + tax_settings افتراضية لكل منشأة
- [ ] Database Connection Pooling
- [ ] Backup تلقائي يومي

### الوظائف
- [ ] اختبار Night Audit في Staging
- [ ] اختبار ZATCA في Sandbox
- [ ] اختبار بوابة الدفع Moyasar
- [ ] اختبار SMS + البريد الإلكتروني
- [ ] اختبار QR Scanner على Android + iOS

---

## سادس عشر: بروتوكول التحقق الداخلي

| السؤال | الإجابة |
|---|---|
| هل VAT ثابت 15% لا يتغير؟ | ✅ ثابت في TaxCalculatorService — vat_rate لا تُعدَّل من الواجهة |
| هل المدير يتحكم في من يتحمل VAT؟ | ✅ vat_on_guest toggle في tax_settings |
| هل رسوم السياحة اختيارية؟ | ✅ tourism_tax_enabled + tourism_tax_on_guest |
| هل ZATCA تحصل على vat_amount الصحيح؟ | ✅ دائماً — بغض النظر عمّن يتحمل |
| هل الفاتورة تعكس الواقع الصحيح؟ | ✅ تتكيف مع الحالتين A/B |
| هل نظام تسجيل الدخول آمن؟ | ✅ bcrypt + Rate Limiting + قفل الحساب |
| هل الأدوار منفصلة عن الصلاحيات؟ | ✅ جداول منفصلة + DB-driven |
| هل Admin يرى جميع البيانات؟ | ✅ لوحة Admin: إجمالي كل المنشآت |
| هل الموظفون يُنشأون من Manager فقط؟ | ✅ EstablishmentContextInterceptor |
| هل تطبيق الحجز يعرض الضرائب بوضوح؟ | ✅ يتكيف مع إعدادات المنشأة |
| هل Night Audit يحسب الضرائب المُتحمَّلة؟ | ✅ total_vat_absorbed + total_tourism_absorbed |

---

**أخرج النسخة النهائية المنظمة الكاملة القابلة للتنفيذ مباشرة، مع الكود الكامل لكل مكون، مصقولاً ومرتباً بالترتيب الموضح. ابدأ بـ TaxCalculatorService ثم tax_settings Migration ثم ربط الضريبة بكل وحدة.**
