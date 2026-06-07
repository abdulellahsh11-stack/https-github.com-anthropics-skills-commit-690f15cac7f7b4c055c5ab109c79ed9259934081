# برومبت نظام تسجيل الدخول وإدارة الصلاحيات — منصة ضيوف

---

أنت الآن خبير هندسة برمجيات، وخبير أمن تطبيقات، ومهندس نظم Backend وFrontend، ومحلل متطلبات برمجية.
أريد منك إنشاء نظام احترافي كامل لتسجيل الدخول وإدارة الصلاحيات متعددة الأدوار، مع الالتزام بمبدأ:
**دقة قبل الجمال — تحقق قبل الاستنتاج — تفصيل قبل الاختصار — إخراج نهائي قبل الشرح.**

---

## أولاً: بيانات المشروع

قم ببناء نظام تسجيل دخول وصلاحيات متعدد الأدوار لمشروع من النوع التالي:

| الحقل | القيمة |
|---|---|
| نوع المشروع | منصة SaaS |
| اسم المشروع | منصة ضيوف |
| لغة البرمجة | TypeScript (في الجانبين Backend وFrontend) |
| إطار العمل — الواجهة الأمامية | Next.js 14 (App Router) |
| إطار العمل — الخلفية | NestJS |
| ORM | Prisma |
| قاعدة البيانات | PostgreSQL |
| أسلوب المصادقة | JWT مع Access Token وRefresh Token + Email Verification |
| التحقق الإضافي | رمز OTP عبر البريد الإلكتروني |
| إدارة الحالة (Frontend) | Zustand |
| التنسيق (Frontend) | Tailwind CSS + shadcn/ui |
| لغة الواجهة | عربية وإنجليزية (i18n) |
| اتجاه الواجهة | RTL للعربية / LTR للإنجليزية |
| بيئة تشغيل التطوير | Node.js 20+ / Docker Compose |

---

## ثانياً: الهدف العام

أنشئ نظاماً كاملاً وآمناً لإدارة المستخدمين وتسجيل الدخول والصلاحيات، بحيث يسمح بوجود عدة أدوار داخل النظام، وكل دور يمتلك صلاحيات محددة بدقة. يجب أن يكون النظام:

- قابلاً للتوسع (Scalable)
- منظماً ومقسماً إلى طبقات واضحة
- آمناً في بيئة الإنتاج
- سهل الصيانة والتطوير
- مناسباً للاستخدام الحقيقي في منصة SaaS متعددة المستأجرين (Multi-Tenant)

---

## ثالثاً: الأدوار المطلوبة

أنشئ نظام أدوار مرناً قابلاً للتعديل من قاعدة البيانات، ويتضمن افتراضياً الأدوار التالية:

### 1. Admin (المدير العام)
- يمتلك جميع الصلاحيات دون استثناء.
- يستطيع إدارة النظام كاملاً: إنشاء الأدوار، حذف المستخدمين، تعديل الصلاحيات، ومراجعة سجلات النظام.
- يستطيع تعديل أي مستخدم أو دور في النظام.
- لا يمكن حذف حساب Admin الافتراضي.

### 2. Manager (مدير المنشأة)
- يستطيع إدارة حساب التسجيل لمنشأته الخاصة فقط.
- يستطيع مراجعة وتعديل بيانات المستخدمين التابعين لمنشأته فحسب.
- لا يستطيع تعديل صلاحياته بنفسه.
- لا يستطيع الوصول إلى بيانات منشآت أخرى.

### 3. Employee (الموظف)
- يستطيع تنفيذ المهام التشغيلية المسموح بها من قِبَل Manager فقط.
- لا يملك وصولاً إلى إعدادات النظام الحساسة.
- لا يستطيع تعديل أي إعداد لحسابه إلا ما سُمح به صراحةً.

### 4. User (المستخدم العادي)
- يمتلك صلاحيات محدودة: عرض حسابه الشخصي فقط.
- يستطيع إدارة حجوزاته وتعديل بياناته الشخصية.
- يستطيع إرسال طلبات واستخدام الخدمات الأساسية للمنصة.

---

## رابعاً: الصلاحيات المطلوبة

أنشئ نظام صلاحيات منفصلاً عن الأدوار، قابلاً للإدارة من قاعدة البيانات، ولا يعتمد على قيم مكتوبة بشكل جامد (Hardcoded) داخل الكود.

### قائمة الصلاحيات

```
users.create
users.read
users.update
users.delete
roles.create
roles.read
roles.update
roles.delete
permissions.assign
dashboard.view
reports.view
reports.export
settings.update
profile.view
profile.update
audit_logs.view
bookings.create
bookings.read
bookings.update
bookings.delete
establishments.create
establishments.read
establishments.update
establishments.delete
```

### مصفوفة الصلاحيات لكل دور

| الصلاحية | Admin | Manager | Employee | User |
|---|:---:|:---:|:---:|:---:|
| users.create | ✅ | ✅ | ❌ | ❌ |
| users.read | ✅ | ✅ (منشأته فقط) | ❌ | ❌ |
| users.update | ✅ | ✅ (منشأته فقط) | ❌ | ❌ |
| users.delete | ✅ | ❌ | ❌ | ❌ |
| roles.create | ✅ | ❌ | ❌ | ❌ |
| roles.read | ✅ | ✅ | ❌ | ❌ |
| roles.update | ✅ | ❌ | ❌ | ❌ |
| roles.delete | ✅ | ❌ | ❌ | ❌ |
| permissions.assign | ✅ | ❌ | ❌ | ❌ |
| dashboard.view | ✅ | ✅ | ✅ | ❌ |
| reports.view | ✅ | ✅ | ❌ | ❌ |
| reports.export | ✅ | ✅ | ❌ | ❌ |
| settings.update | ✅ | ✅ (منشأته فقط) | ❌ | ❌ |
| profile.view | ✅ | ✅ | ✅ | ✅ |
| profile.update | ✅ | ✅ | ✅ | ✅ |
| audit_logs.view | ✅ | ❌ | ❌ | ❌ |
| bookings.create | ✅ | ✅ | ✅ | ✅ |
| bookings.read | ✅ | ✅ | ✅ | ✅ (حجوزاته فقط) |
| bookings.update | ✅ | ✅ | ✅ | ✅ (حجوزاته فقط) |
| bookings.delete | ✅ | ✅ | ❌ | ❌ |
| establishments.create | ✅ | ❌ | ❌ | ❌ |
| establishments.read | ✅ | ✅ (منشأته فقط) | ✅ (منشأته فقط) | ❌ |
| establishments.update | ✅ | ✅ (منشأته فقط) | ❌ | ❌ |
| establishments.delete | ✅ | ❌ | ❌ | ❌ |

> **ملاحظة:** هذه المصفوفة قابلة للتعديل الكامل من لوحة التحكم دون تعديل الكود.

---

## خامساً: مكونات النظام الأساسية

### 1. صفحة تسجيل الدخول
- حقل: البريد الإلكتروني أو اسم المستخدم
- حقل: كلمة المرور (مع زر إظهار/إخفاء)
- خيار: تذكرني (Remember Me)
- رابط: نسيت كلمة المرور؟
- رسائل خطأ عامة وآمنة (لا تكشف سبب الفشل بدقة)
- حماية CSRF
- Rate Limiting على مستوى IP

### 2. صفحة إنشاء حساب
- حقل: الاسم الكامل
- حقل: البريد الإلكتروني
- حقل: رقم الهاتف (بصيغة دولية)
- حقل: اسم المنشأة
- حقل: كلمة المرور
- حقل: تأكيد كلمة المرور
- خانة: الموافقة على الشروط والأحكام
- التحقق الفوري من صحة البيانات (Real-time Validation)
- إرسال بريد تحقق فور التسجيل

### 3. نظام التحقق من الهوية
- إرسال رمز OTP إلى البريد الإلكتروني فور التسجيل
- مدة صلاحية رمز التحقق: 15 دقيقة
- منع وصول الحسابات غير المُفعَّلة إلى أي مسار محمي
- صفحة مخصصة لإدخال رمز التحقق
- إمكانية إعادة إرسال الرمز مع تأخير زمني (Cooldown: 60 ثانية)

### 4. استعادة كلمة المرور
- إدخال البريد الإلكتروني المسجَّل
- إرسال رابط إعادة التعيين عبر البريد (صالح لمدة 30 دقيقة)
- الرابط يُستخدَم مرة واحدة فقط (Single-Use Token)
- بعد التعيين: إلغاء جميع جلسات المستخدم الحالية
- منع تكرار كلمة المرور الأخيرة

### 5. إدارة الجلسات
- JWT: Access Token (مدة: 15 دقيقة) + Refresh Token (مدة: 7 أيام)
- تخزين Refresh Token في قاعدة البيانات مع دعم الإلغاء
- تخزين Access Token في الذاكرة (In-Memory) في الـ Client
- تخزين Refresh Token في HttpOnly Cookie
- دعم تسجيل الخروج الكامل من جميع الأجهزة

### 6. لوحة إدارة المستخدمين
- جدول بيانات مع بحث وتصفية وفرز
- إضافة مستخدم جديد
- تعديل بيانات المستخدم
- تعيين/تغيير دور المستخدم
- تعطيل الحساب مؤقتاً
- الحذف الناعم (Soft Delete) مع إمكانية الاسترجاع
- عرض حالة الحساب: نشط / غير مُفعَّل / معطَّل / محذوف

### 7. لوحة إدارة الأدوار
- إنشاء دور جديد بالاسم والوصف
- ربط مجموعة صلاحيات بكل دور
- تعديل صلاحيات الدور في الوقت الفعلي
- منع حذف الأدوار الأساسية (Admin, Manager, Employee, User)
- عرض عدد المستخدمين المرتبطين بكل دور

### 8. لوحة إدارة الصلاحيات
- عرض الصلاحيات مصنَّفةً حسب الوحدات (Users, Roles, Bookings, إلخ)
- ربط الصلاحيات بالأدوار عبر واجهة بصرية (Drag & Drop أو Checkboxes)
- منع إزالة صلاحية حرجة من Admin

### 9. حماية المسارات
- `AuthGuard`: التحقق من وجود Access Token صالح
- `RolesGuard`: التحقق من دور المستخدم
- `PermissionsGuard`: التحقق من الصلاحية الفعلية المطلوبة
- `OwnershipGuard`: التحقق من أن المورد يعود للمستخدم نفسه أو لمنشأته
- تطبيق Guards بشكل تراكمي (Composable)

### 10. سجل التدقيق (Audit Log)
تسجيل العمليات التالية تلقائياً:
- تسجيل الدخول الناجح وفشله
- تسجيل الخروج
- إنشاء حساب جديد
- تغيير كلمة المرور
- تعديل الصلاحيات
- حذف مستخدم
- تغيير إعدادات النظام
- تعيين دور لمستخدم
- تفعيل/تعطيل حساب

---

## سادساً: قاعدة البيانات

### تصميم الجداول (PostgreSQL + Prisma)

---

### جدول `users`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف المستخدم | DEFAULT gen_random_uuid() |
| name | VARCHAR(100) | ✅ | — | الاسم الكامل | NOT NULL |
| email | VARCHAR(255) | ✅ | UNIQUE INDEX | البريد الإلكتروني | NOT NULL, UNIQUE |
| phone | VARCHAR(20) | ❌ | — | رقم الهاتف | — |
| username | VARCHAR(50) | ❌ | UNIQUE INDEX | اسم المستخدم | UNIQUE |
| password_hash | VARCHAR(255) | ✅ | — | كلمة المرور المشفرة | NOT NULL |
| establishment_id | UUID | ❌ | FK → establishments | ارتباط بالمنشأة | ON DELETE SET NULL |
| is_email_verified | BOOLEAN | ✅ | — | هل البريد مُفعَّل؟ | DEFAULT false |
| is_active | BOOLEAN | ✅ | — | هل الحساب نشط؟ | DEFAULT true |
| is_deleted | BOOLEAN | ✅ | — | حذف ناعم | DEFAULT false |
| deleted_at | TIMESTAMP | ❌ | — | تاريخ الحذف الناعم | NULL |
| last_login_at | TIMESTAMP | ❌ | — | آخر تسجيل دخول | — |
| failed_login_count | INT | ✅ | — | عدد محاولات الدخول الفاشلة | DEFAULT 0 |
| locked_until | TIMESTAMP | ❌ | — | مدة قفل الحساب | NULL |
| subscription_type | ENUM | ✅ | — | نوع الاشتراك | trial / basic / pro / enterprise |
| trial_ends_at | TIMESTAMP | ❌ | — | تاريخ انتهاء التجربة المجانية | — |
| subscription_ends_at | TIMESTAMP | ❌ | — | تاريخ انتهاء الاشتراك | — |
| created_at | TIMESTAMP | ✅ | — | تاريخ الإنشاء | DEFAULT NOW() |
| updated_at | TIMESTAMP | ✅ | — | تاريخ آخر تعديل | AUTO UPDATE |

---

### جدول `establishments`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف المنشأة | DEFAULT gen_random_uuid() |
| name | VARCHAR(200) | ✅ | — | اسم المنشأة | NOT NULL |
| owner_id | UUID | ✅ | FK → users | مالك المنشأة | NOT NULL |
| is_active | BOOLEAN | ✅ | — | حالة المنشأة | DEFAULT true |
| created_at | TIMESTAMP | ✅ | — | تاريخ الإنشاء | DEFAULT NOW() |
| updated_at | TIMESTAMP | ✅ | — | تاريخ آخر تعديل | AUTO UPDATE |

---

### جدول `roles`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف الدور | DEFAULT gen_random_uuid() |
| name | VARCHAR(50) | ✅ | UNIQUE | اسم الدور | NOT NULL, UNIQUE |
| description | TEXT | ❌ | — | وصف الدور | — |
| is_system | BOOLEAN | ✅ | — | هل هو دور نظام محمي؟ | DEFAULT false |
| created_at | TIMESTAMP | ✅ | — | تاريخ الإنشاء | DEFAULT NOW() |

---

### جدول `permissions`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف الصلاحية | DEFAULT gen_random_uuid() |
| name | VARCHAR(100) | ✅ | UNIQUE | اسم الصلاحية (users.create) | NOT NULL, UNIQUE |
| module | VARCHAR(50) | ✅ | INDEX | الوحدة التابعة لها (users) | NOT NULL |
| description | TEXT | ❌ | — | وصف الصلاحية | — |
| created_at | TIMESTAMP | ✅ | — | تاريخ الإنشاء | DEFAULT NOW() |

---

### جدول `role_permissions`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| role_id | UUID | ✅ | FK → roles | ارتباط بالدور | ON DELETE CASCADE |
| permission_id | UUID | ✅ | FK → permissions | ارتباط بالصلاحية | ON DELETE CASCADE |
| — | — | — | PK (role_id, permission_id) | مفتاح مركب | UNIQUE |

---

### جدول `user_roles`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| user_id | UUID | ✅ | FK → users | ارتباط بالمستخدم | ON DELETE CASCADE |
| role_id | UUID | ✅ | FK → roles | ارتباط بالدور | ON DELETE CASCADE |
| assigned_by | UUID | ❌ | FK → users | من قام بالتعيين | — |
| assigned_at | TIMESTAMP | ✅ | — | تاريخ التعيين | DEFAULT NOW() |
| — | — | — | PK (user_id, role_id) | مفتاح مركب | UNIQUE |

---

### جدول `user_permissions` (صلاحيات مخصصة اختيارية)

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| user_id | UUID | ✅ | FK → users | ارتباط بالمستخدم | ON DELETE CASCADE |
| permission_id | UUID | ✅ | FK → permissions | صلاحية مباشرة | ON DELETE CASCADE |
| granted_by | UUID | ✅ | FK → users | من منح الصلاحية | NOT NULL |
| granted_at | TIMESTAMP | ✅ | — | تاريخ المنح | DEFAULT NOW() |

---

### جدول `password_reset_tokens`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف الرمز | DEFAULT gen_random_uuid() |
| user_id | UUID | ✅ | FK → users | ارتباط بالمستخدم | ON DELETE CASCADE |
| token_hash | VARCHAR(255) | ✅ | INDEX | هاش الرمز | NOT NULL |
| expires_at | TIMESTAMP | ✅ | — | تاريخ انتهاء الصلاحية | NOT NULL |
| is_used | BOOLEAN | ✅ | — | هل استُخدم؟ | DEFAULT false |
| created_at | TIMESTAMP | ✅ | — | تاريخ الإنشاء | DEFAULT NOW() |

---

### جدول `email_verification_tokens`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف رمز التحقق | DEFAULT gen_random_uuid() |
| user_id | UUID | ✅ | FK → users | ارتباط بالمستخدم | ON DELETE CASCADE |
| otp_hash | VARCHAR(255) | ✅ | — | هاش رمز OTP | NOT NULL |
| expires_at | TIMESTAMP | ✅ | — | تاريخ انتهاء الصلاحية | NOT NULL |
| is_used | BOOLEAN | ✅ | — | هل استُخدم؟ | DEFAULT false |
| created_at | TIMESTAMP | ✅ | — | تاريخ الإنشاء | DEFAULT NOW() |

---

### جدول `refresh_tokens`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف الـ Token | DEFAULT gen_random_uuid() |
| user_id | UUID | ✅ | FK → users | ارتباط بالمستخدم | ON DELETE CASCADE |
| token_hash | VARCHAR(255) | ✅ | UNIQUE INDEX | هاش الـ Refresh Token | NOT NULL, UNIQUE |
| device_info | TEXT | ❌ | — | معلومات الجهاز | — |
| ip_address | INET | ❌ | — | عنوان IP | — |
| expires_at | TIMESTAMP | ✅ | — | تاريخ انتهاء الصلاحية | NOT NULL |
| is_revoked | BOOLEAN | ✅ | — | هل أُلغي؟ | DEFAULT false |
| created_at | TIMESTAMP | ✅ | — | تاريخ الإنشاء | DEFAULT NOW() |

---

### جدول `login_attempts`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف المحاولة | DEFAULT gen_random_uuid() |
| email | VARCHAR(255) | ✅ | INDEX | البريد المُستخدم | NOT NULL |
| ip_address | INET | ✅ | INDEX | عنوان IP | NOT NULL |
| is_success | BOOLEAN | ✅ | — | هل نجحت المحاولة؟ | NOT NULL |
| user_agent | TEXT | ❌ | — | بيانات المتصفح | — |
| attempted_at | TIMESTAMP | ✅ | INDEX | وقت المحاولة | DEFAULT NOW() |

---

### جدول `audit_logs`

| اسم الحقل | النوع | إجباري | مفتاح | الغرض | القيود |
|---|---|:---:|---|---|---|
| id | UUID | ✅ | PK | معرف السجل | DEFAULT gen_random_uuid() |
| user_id | UUID | ❌ | FK → users | المستخدم المنفِّذ | ON DELETE SET NULL |
| action | VARCHAR(100) | ✅ | INDEX | نوع العملية | NOT NULL |
| entity_type | VARCHAR(50) | ❌ | INDEX | نوع الكيان (user/role/...) | — |
| entity_id | UUID | ❌ | — | معرف الكيان المتأثر | — |
| old_value | JSONB | ❌ | — | القيمة قبل التعديل | — |
| new_value | JSONB | ❌ | — | القيمة بعد التعديل | — |
| ip_address | INET | ❌ | — | عنوان IP | — |
| user_agent | TEXT | ❌ | — | بيانات المتصفح | — |
| created_at | TIMESTAMP | ✅ | INDEX | وقت تنفيذ العملية | DEFAULT NOW() |

---

## سابعاً: متطلبات الأمان

طبّق جميع الممارسات التالية دون استثناء:

### تشفير كلمات المرور
- استخدم `bcrypt` بـ salt rounds = 12 كحد أدنى أو `argon2id`.
- لا تخزن أي كلمة مرور كنص صريح في أي مكان.
- لا تُرسل كلمة المرور الحالية عند تعديل الملف الشخصي.

### حماية تسجيل الدخول
- Rate Limiting: 5 محاولات لكل IP في 15 دقيقة.
- قفل الحساب تلقائياً بعد 5 محاولات فاشلة متتالية لمدة 30 دقيقة.
- رسالة الخطأ موحَّدة: "بيانات الدخول غير صحيحة" (بدون تحديد ما إذا كان البريد أو كلمة المرور هو الخطأ).
- تسجيل كل محاولة دخول في `login_attempts`.

### حماية API
- SQL Injection: استخدم Prisma Parameterized Queries دائماً، لا Raw Queries.
- XSS: تنظيف المدخلات بـ `DOMPurify` في Frontend، وـ `class-sanitizer` أو `sanitize-html` في Backend.
- CSRF: استخدم Double Submit Cookie Pattern أو SameSite=Strict للـ Cookies.
- Input Validation: استخدم `class-validator` + `class-transformer` في NestJS لكل DTO.
- استخدم `helmet` في NestJS لتعيين Security Headers.
- استخدم `cors` مع whitelist صريحة للنطاقات المسموح بها.

### إعداد Cookies
```
HttpOnly: true
Secure: true (في بيئة الإنتاج)
SameSite: Strict
Path: /auth/refresh
MaxAge: 7 days
```

### مبدأ أقل الصلاحيات
- لا تُرسل بيانات لا يحتاجها الـ Client (مثل password_hash).
- لا تسمح للمستخدم بتعديل دوره بنفسه.
- لا تسمح لأي Employee بتعديل أو حذف Manager.
- تحقق من الصلاحية الفعلية في كل Request، لا فقط من الدور.
- استخدم OwnershipGuard للتحقق من أن المستخدم يعدّل موارده هو فقط.

### المتغيرات البيئية
- احفظ جميع الأسرار في `.env` ولا تُدمجها داخل الكود.
- أضف `.env` إلى `.gitignore`.
- أنشئ `.env.example` بمفاتيح فارغة كمرجع.

---

## ثامناً: منطق الصلاحيات

### شروط السماح بالوصول (بالترتيب)

1. **المستخدم مسجَّل الدخول** — Access Token صالح وغير منتهي.
2. **الحساب مُفعَّل** — `is_email_verified = true` و`is_active = true` و`is_deleted = false`.
3. **الاشتراك ساري** — إما:
   - في فترة التجربة المجانية (60 يوماً تتناقص يومياً)، أو
   - يمتلك اشتراكاً نشطاً لم تنتهِ صلاحيته.
4. **المستخدم يمتلك دوراً واحداً على الأقل**.
5. **الدور يمتلك الصلاحية المطلوبة** — التحقق من `role_permissions`.
6. **في حالة تعدد الأدوار**: يحصل المستخدم على مجموع صلاحيات جميع أدواره (Union).
7. **الصلاحية المخصصة** (`user_permissions`): تُضاف فوق صلاحيات الأدوار (اختيارية).

### قواعد منع تعارض الصلاحيات الحرجة
- لا يمكن لأي مستخدم منح لنفسه صلاحية أعلى من صلاحياته الحالية.
- لا يمكن تعديل أو حذف حساب Admin الافتراضي.
- لا يمكن إزالة دور Admin من المستخدم الوحيد الذي يمتلكه في النظام.

---

## تاسعاً: واجهات API المطلوبة

### Authentication APIs

---

#### `POST /auth/register`
- **الوظيفة**: تسجيل مستخدم جديد وإرسال رمز تحقق للبريد.
- **الصلاحية**: عامة (لا تتطلب مصادقة).
- **المدخلات (Body)**:
```json
{
  "name": "أحمد محمد",
  "email": "ahmed@example.com",
  "phone": "+966501234567",
  "establishment_name": "فندق النخيل",
  "password": "P@ssw0rd123!",
  "password_confirm": "P@ssw0rd123!",
  "terms_accepted": true
}
```
- **المخرجات (201)**:
```json
{
  "success": true,
  "message": "تم إنشاء الحساب. يرجى التحقق من بريدك الإلكتروني.",
  "data": { "user_id": "uuid", "email": "ahmed@example.com" }
}
```
- **أخطاء محتملة**: 400 (بيانات غير صالحة)، 409 (البريد مستخدم مسبقاً).

---

#### `POST /auth/login`
- **الوظيفة**: تسجيل الدخول وإصدار Access Token وRefresh Token.
- **الصلاحية**: عامة.
- **المدخلات (Body)**:
```json
{
  "email": "ahmed@example.com",
  "password": "P@ssw0rd123!",
  "remember_me": true
}
```
- **المخرجات (200)**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "user": {
      "id": "uuid",
      "name": "أحمد محمد",
      "email": "ahmed@example.com",
      "roles": ["manager"],
      "permissions": ["users.read", "bookings.create"]
    }
  }
}
```
- **Refresh Token**: يُحفظ في HttpOnly Cookie تلقائياً.
- **أخطاء محتملة**: 401 (بيانات غير صحيحة)، 403 (حساب غير مُفعَّل أو مقفل)، 429 (تجاوز حد المحاولات).

---

#### `POST /auth/logout`
- **الوظيفة**: تسجيل الخروج وإلغاء Refresh Token.
- **الصلاحية**: مسجَّل الدخول.
- **المدخلات**: Cookie (refresh_token).
- **المخرجات (200)**:
```json
{ "success": true, "message": "تم تسجيل الخروج بنجاح." }
```

---

#### `POST /auth/refresh-token`
- **الوظيفة**: تجديد Access Token باستخدام Refresh Token.
- **الصلاحية**: Refresh Token صالح في الـ Cookie.
- **المخرجات (200)**:
```json
{
  "success": true,
  "data": { "access_token": "eyJ..." }
}
```
- **أخطاء محتملة**: 401 (Token منتهٍ أو ملغى).

---

#### `POST /auth/forgot-password`
- **الوظيفة**: إرسال رابط إعادة تعيين كلمة المرور.
- **الصلاحية**: عامة.
- **المدخلات (Body)**:
```json
{ "email": "ahmed@example.com" }
```
- **المخرجات (200)**:
```json
{ "success": true, "message": "إذا كان البريد مسجَّلاً، ستصلك تعليمات إعادة التعيين." }
```
> **ملاحظة أمنية**: الرسالة موحَّدة بغض النظر عن وجود البريد في النظام.

---

#### `POST /auth/reset-password`
- **الوظيفة**: تعيين كلمة مرور جديدة باستخدام رمز إعادة التعيين.
- **المدخلات (Body)**:
```json
{
  "token": "reset-token-string",
  "password": "NewP@ssw0rd!",
  "password_confirm": "NewP@ssw0rd!"
}
```
- **المخرجات (200)**:
```json
{ "success": true, "message": "تم تغيير كلمة المرور بنجاح. يرجى تسجيل الدخول." }
```
- **أخطاء محتملة**: 400 (رمز غير صالح أو منتهٍ).

---

#### `POST /auth/verify-email`
- **الوظيفة**: التحقق من البريد الإلكتروني باستخدام رمز OTP.
- **المدخلات (Body)**:
```json
{ "user_id": "uuid", "otp": "123456" }
```
- **المخرجات (200)**:
```json
{ "success": true, "message": "تم تفعيل حسابك بنجاح." }
```

---

#### `GET /auth/me`
- **الوظيفة**: جلب بيانات المستخدم الحالي مع أدواره وصلاحياته.
- **الصلاحية**: مسجَّل الدخول.
- **المخرجات (200)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "أحمد محمد",
    "email": "ahmed@example.com",
    "roles": ["manager"],
    "permissions": ["users.read", "bookings.create", "profile.update"],
    "subscription": {
      "type": "trial",
      "days_remaining": 45
    }
  }
}
```

---

### Users APIs

| المسار | الطريقة | الصلاحية المطلوبة | الوظيفة |
|---|---|---|---|
| `/users` | GET | `users.read` | قائمة المستخدمين مع بحث وتصفية |
| `/users/:id` | GET | `users.read` | تفاصيل مستخدم واحد |
| `/users` | POST | `users.create` | إنشاء مستخدم جديد |
| `/users/:id` | PATCH | `users.update` | تعديل بيانات مستخدم |
| `/users/:id` | DELETE | `users.delete` | حذف ناعم للمستخدم |
| `/users/:id/activate` | PATCH | `users.update` | تفعيل الحساب |
| `/users/:id/deactivate` | PATCH | `users.update` | تعطيل الحساب |

---

### Roles APIs

| المسار | الطريقة | الصلاحية المطلوبة | الوظيفة |
|---|---|---|---|
| `/roles` | GET | `roles.read` | قائمة الأدوار |
| `/roles/:id` | GET | `roles.read` | تفاصيل دور واحد |
| `/roles` | POST | `roles.create` | إنشاء دور جديد |
| `/roles/:id` | PATCH | `roles.update` | تعديل الدور |
| `/roles/:id` | DELETE | `roles.delete` | حذف الدور (غير النظامي) |

---

### Permissions APIs

| المسار | الطريقة | الصلاحية المطلوبة | الوظيفة |
|---|---|---|---|
| `/permissions` | GET | `permissions.assign` | قائمة الصلاحيات مصنَّفة |
| `/roles/:id/permissions` | POST | `permissions.assign` | ربط صلاحيات بدور |
| `/roles/:id/permissions/:permId` | DELETE | `permissions.assign` | إزالة صلاحية من دور |

---

### Audit Logs APIs

| المسار | الطريقة | الصلاحية المطلوبة | الوظيفة |
|---|---|---|---|
| `/audit-logs` | GET | `audit_logs.view` | قائمة سجلات التدقيق مع تصفية |
| `/audit-logs/:id` | GET | `audit_logs.view` | تفاصيل سجل واحد |

---

## عاشراً: هيكل المشروع

```
duyuf-platform/
├── apps/
│   ├── backend/                    # NestJS Application
│   │   ├── src/
│   │   │   ├── auth/
│   │   │   │   ├── auth.module.ts
│   │   │   │   ├── auth.controller.ts
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── strategies/
│   │   │   │   │   ├── jwt.strategy.ts
│   │   │   │   │   └── jwt-refresh.strategy.ts
│   │   │   │   └── dto/
│   │   │   │       ├── register.dto.ts
│   │   │   │       ├── login.dto.ts
│   │   │   │       ├── forgot-password.dto.ts
│   │   │   │       └── reset-password.dto.ts
│   │   │   ├── users/
│   │   │   │   ├── users.module.ts
│   │   │   │   ├── users.controller.ts
│   │   │   │   ├── users.service.ts
│   │   │   │   └── dto/
│   │   │   ├── roles/
│   │   │   │   ├── roles.module.ts
│   │   │   │   ├── roles.controller.ts
│   │   │   │   └── roles.service.ts
│   │   │   ├── permissions/
│   │   │   │   ├── permissions.module.ts
│   │   │   │   ├── permissions.controller.ts
│   │   │   │   └── permissions.service.ts
│   │   │   ├── audit-logs/
│   │   │   │   ├── audit-logs.module.ts
│   │   │   │   ├── audit-logs.controller.ts
│   │   │   │   └── audit-logs.service.ts
│   │   │   ├── common/
│   │   │   │   ├── guards/
│   │   │   │   │   ├── jwt-auth.guard.ts
│   │   │   │   │   ├── roles.guard.ts
│   │   │   │   │   ├── permissions.guard.ts
│   │   │   │   │   └── ownership.guard.ts
│   │   │   │   ├── decorators/
│   │   │   │   │   ├── roles.decorator.ts
│   │   │   │   │   ├── permissions.decorator.ts
│   │   │   │   │   └── current-user.decorator.ts
│   │   │   │   ├── filters/
│   │   │   │   │   └── http-exception.filter.ts
│   │   │   │   ├── interceptors/
│   │   │   │   │   └── audit-log.interceptor.ts
│   │   │   │   └── pipes/
│   │   │   │       └── validation.pipe.ts
│   │   │   ├── mail/
│   │   │   │   ├── mail.module.ts
│   │   │   │   └── mail.service.ts
│   │   │   ├── prisma/
│   │   │   │   ├── prisma.module.ts
│   │   │   │   └── prisma.service.ts
│   │   │   └── main.ts
│   │   ├── prisma/
│   │   │   ├── schema.prisma
│   │   │   └── seed.ts
│   │   ├── test/
│   │   │   ├── auth.e2e-spec.ts
│   │   │   ├── users.e2e-spec.ts
│   │   │   └── roles.e2e-spec.ts
│   │   └── .env.example
│   │
│   └── frontend/                   # Next.js 14 Application
│       ├── app/
│       │   ├── (auth)/
│       │   │   ├── login/
│       │   │   │   └── page.tsx
│       │   │   ├── register/
│       │   │   │   └── page.tsx
│       │   │   ├── verify-email/
│       │   │   │   └── page.tsx
│       │   │   ├── forgot-password/
│       │   │   │   └── page.tsx
│       │   │   └── reset-password/
│       │   │       └── page.tsx
│       │   ├── (dashboard)/
│       │   │   ├── layout.tsx
│       │   │   ├── page.tsx
│       │   │   ├── users/
│       │   │   │   └── page.tsx
│       │   │   ├── roles/
│       │   │   │   └── page.tsx
│       │   │   ├── permissions/
│       │   │   │   └── page.tsx
│       │   │   ├── audit-logs/
│       │   │   │   └── page.tsx
│       │   │   └── profile/
│       │   │       └── page.tsx
│       │   ├── 401/
│       │   │   └── page.tsx
│       │   ├── 403/
│       │   │   └── page.tsx
│       │   └── layout.tsx
│       ├── components/
│       │   ├── auth/
│       │   ├── users/
│       │   ├── roles/
│       │   └── ui/
│       ├── lib/
│       │   ├── api.ts
│       │   ├── auth.ts
│       │   └── permissions.ts
│       ├── store/
│       │   └── auth.store.ts
│       ├── middleware.ts
│       ├── messages/
│       │   ├── ar.json
│       │   └── en.json
│       └── .env.example
│
├── docker-compose.yml
└── README.md
```

---

## حادي عشر: ملف Environment Variables النموذجي

### `apps/backend/.env.example`
```env
# === Application ===
NODE_ENV=development
PORT=3001
APP_URL=http://localhost:3001
FRONTEND_URL=http://localhost:3000

# === Database ===
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/duyuf_db

# === JWT ===
JWT_ACCESS_SECRET=REPLACE_WITH_STRONG_SECRET_MIN_64_CHARS
JWT_ACCESS_EXPIRES_IN=15m
JWT_REFRESH_SECRET=REPLACE_WITH_DIFFERENT_STRONG_SECRET_MIN_64_CHARS
JWT_REFRESH_EXPIRES_IN=7d

# === Bcrypt ===
BCRYPT_SALT_ROUNDS=12

# === Email ===
MAIL_HOST=smtp.example.com
MAIL_PORT=587
MAIL_SECURE=false
MAIL_USER=noreply@duyuf.com
MAIL_PASSWORD=REPLACE_WITH_MAIL_PASSWORD
MAIL_FROM="منصة ضيوف <noreply@duyuf.com>"

# === Rate Limiting ===
THROTTLE_TTL=900
THROTTLE_LIMIT=5

# === Token Expiry ===
EMAIL_VERIFY_OTP_EXPIRES_MINUTES=15
PASSWORD_RESET_EXPIRES_MINUTES=30
TRIAL_DAYS=60
```

### `apps/frontend/.env.example`
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_APP_NAME=منصة ضيوف
NEXT_PUBLIC_DEFAULT_LOCALE=ar
```

---

## ثاني عشر: آلية تشغيل المشروع محلياً

```bash
# 1. استنساخ المشروع
git clone https://github.com/your-org/duyuf-platform.git
cd duyuf-platform

# 2. تشغيل قاعدة البيانات عبر Docker
docker-compose up -d postgres

# 3. إعداد Backend
cd apps/backend
cp .env.example .env
# عدّل .env بالقيم الصحيحة
npm install
npx prisma migrate dev --name init
npx prisma db seed
npm run start:dev

# 4. إعداد Frontend (في نافذة طرفية جديدة)
cd apps/frontend
cp .env.example .env
npm install
npm run dev

# 5. الوصول إلى التطبيق
# Frontend: http://localhost:3000
# Backend API: http://localhost:3001
# Swagger Docs: http://localhost:3001/api/docs
```

### `docker-compose.yml`
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: duyuf_db
      POSTGRES_USER: duyuf_user
      POSTGRES_PASSWORD: duyuf_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## ثالث عشر: بيانات Seed الافتراضية

```typescript
// prisma/seed.ts — ملخص البيانات الأساسية

// الأدوار الأساسية (is_system = true)
const roles = ['admin', 'manager', 'employee', 'user'];

// الصلاحيات الأساسية
const permissions = [
  // Users
  { name: 'users.create', module: 'users' },
  { name: 'users.read',   module: 'users' },
  { name: 'users.update', module: 'users' },
  { name: 'users.delete', module: 'users' },
  // Roles
  { name: 'roles.create', module: 'roles' },
  { name: 'roles.read',   module: 'roles' },
  { name: 'roles.update', module: 'roles' },
  { name: 'roles.delete', module: 'roles' },
  // Permissions
  { name: 'permissions.assign', module: 'permissions' },
  // Dashboard & Reports
  { name: 'dashboard.view',  module: 'dashboard' },
  { name: 'reports.view',    module: 'reports' },
  { name: 'reports.export',  module: 'reports' },
  // Settings & Profile
  { name: 'settings.update', module: 'settings' },
  { name: 'profile.view',    module: 'profile' },
  { name: 'profile.update',  module: 'profile' },
  // Audit
  { name: 'audit_logs.view', module: 'audit' },
  // Bookings
  { name: 'bookings.create', module: 'bookings' },
  { name: 'bookings.read',   module: 'bookings' },
  { name: 'bookings.update', module: 'bookings' },
  { name: 'bookings.delete', module: 'bookings' },
  // Establishments
  { name: 'establishments.create', module: 'establishments' },
  { name: 'establishments.read',   module: 'establishments' },
  { name: 'establishments.update', module: 'establishments' },
  { name: 'establishments.delete', module: 'establishments' },
];

// مستخدم Admin افتراضي
// البريد: admin@duyuf.com
// كلمة المرور: تُعيَّن من متغير بيئي ADMIN_DEFAULT_PASSWORD
// يجب تغييرها فور أول تسجيل دخول
```

---

## رابع عشر: الاختبارات المطلوبة

### سيناريوهات الاختبار الشاملة

```
✅ تسجيل حساب جديد بنجاح
✅ تسجيل حساب بمدخلات ناقصة — يجب أن يُرجع 400
✅ تسجيل حساب ببريد مكرر — يجب أن يُرجع 409
✅ تسجيل الدخول الصحيح وإصدار Token
✅ تسجيل دخول بكلمة مرور خاطئة — يجب أن يُرجع 401 برسالة عامة
✅ تسجيل دخول قبل تفعيل البريد — يجب أن يُرجع 403
✅ قفل الحساب بعد 5 محاولات فاشلة
✅ تجديد Access Token بـ Refresh Token صالح
✅ رفض Refresh Token منتهٍ أو ملغى
✅ استعادة كلمة المرور — إرسال رابط وتعيين كلمة مرور جديدة
✅ رفض رابط إعادة التعيين بعد استخدامه مرة واحدة
✅ منع User العادي من دخول /users — يجب أن يُرجع 403
✅ السماح لـ Manager بعرض مستخدمي منشأته فقط
✅ منع Manager من تعديل حساب Admin
✅ منع Employee من حذف أي مستخدم
✅ التحقق من أن صلاحية users.delete مطلوبة لحذف مستخدم
✅ اختبار Audit Log: تسجيل عملية تغيير كلمة المرور
✅ اختبار انتهاء صلاحية Trial بعد 60 يوماً
✅ منع الوصول لمستخدم انتهت تجربته المجانية
```

---

## خامس عشر: ملاحظات أمنية قبل النشر

```
⚠️  تأكد من أن NODE_ENV=production في بيئة الإنتاج.
⚠️  غيّر كلمة مرور Admin الافتراضية فور أول تشغيل.
⚠️  تأكد من تفعيل HTTPS وSSL Certificate قبل النشر.
⚠️  تحقق من إعداد CORS بقائمة نطاقات صريحة (لا تستخدم * في الإنتاج).
⚠️  راجع إعدادات Helmet Security Headers.
⚠️  تأكد من تشغيل Prisma Migrations في بيئة الإنتاج بشكل آمن.
⚠️  لا تُدرج ملفات .env أو أي أسرار في مستودع Git.
⚠️  فعّل تسجيل Audit Logs في الإنتاج ووجّهها إلى خدمة مراقبة.
⚠️  راجع Refresh Token Rotation: أُلغِ القديم وأنشئ الجديد في كل تجديد.
⚠️  تأكد من تفعيل Rate Limiting على جميع مسارات Auth.
⚠️  استخدم Database Connection Pooling (PgBouncer) في الإنتاج.
⚠️  احذف Swagger Docs أو قيّد وصوله في بيئة الإنتاج.
⚠️  فعّل Monitoring وError Tracking (مثل Sentry).
```

---

## سادس عشر: قائمة مراجعة Checklist قبل الإطلاق

```
□ تم اختبار جميع مسارات API في بيئة Staging.
□ تم التحقق من صحة جميع Validations.
□ تم تشغيل جميع الاختبارات الآلية وهي تمر بنجاح.
□ تم تغيير كلمة مرور Admin الافتراضية.
□ تم تعيين قيم .env الصحيحة في بيئة الإنتاج.
□ تم تفعيل HTTPS.
□ تم إعداد CORS بالنطاقات الصحيحة فقط.
□ تم التحقق من Security Headers (باستخدام securityheaders.com).
□ تم اختبار Rate Limiting.
□ تم التحقق من أن Refresh Tokens تُلغى عند تسجيل الخروج.
□ تم اختبار Soft Delete واسترجاع البيانات.
□ تم التحقق من Audit Logs تُسجَّل بشكل صحيح.
□ تم اختبار فترة التجربة المجانية (60 يوماً).
□ تم اختبار واجهة RTL و LTR.
□ تم اختبار الواجهة على الجوال.
□ تم مراجعة الأذونات: لا يوجد مسار غير محمي.
□ تم توثيق جميع الـ API endpoints في Swagger.
□ تم إعداد Backup تلقائي لقاعدة البيانات.
□ تم ضبط Logging وError Monitoring.
□ تم مراجعة Dependencies للتحقق من عدم وجود ثغرات (npm audit).
```

---

## سابع عشر: تحسينات مستقبلية مقترحة

```
🔮 تسجيل الدخول الاجتماعي: Google OAuth / Apple Sign-In.
🔮 المصادقة الثنائية (2FA) عبر TOTP (Google Authenticator).
🔮 نظام الاشتراكات والفوترة: Stripe / HyperPay.
🔮 Multi-Tenancy الكامل: عزل بيانات كل منشأة في Schema منفصل.
🔮 نظام الإشعارات: WebSocket / Push Notifications.
🔮 تصدير سجلات Audit Logs بصيغة CSV/PDF.
🔮 لوحة تحليلات ومؤشرات KPI لكل منشأة.
🔮 نظام API Keys للتكامل مع أنظمة خارجية.
🔮 دعم Passwordless Login (Magic Links).
🔮 تشفير البيانات الحساسة في قاعدة البيانات (Encryption at Rest).
```

---

## ثامن عشر: بروتوكول التحقق الداخلي

قبل إخراج النسخة النهائية، تحقق من جميع النقاط التالية:

| السؤال | الإجابة |
|---|---|
| هل نظام تسجيل الدخول آمن؟ | ✅ bcrypt + Rate Limiting + قفل الحساب |
| هل الأدوار منفصلة عن الصلاحيات؟ | ✅ جداول منفصلة وقابلة للإدارة |
| هل يمكن تعديل الصلاحيات دون تعديل الكود؟ | ✅ من لوحة التحكم مباشرة |
| هل تم منع التصعيد غير المشروع؟ | ✅ لا يمكن لأي مستخدم رفع صلاحياته بنفسه |
| هل تم حماية المسارات الحساسة؟ | ✅ AuthGuard + PermissionsGuard على كل مسار |
| هل تم تسجيل العمليات الحساسة؟ | ✅ AuditLog Interceptor تلقائي |
| هل يوجد تحقق من المدخلات؟ | ✅ class-validator على كل DTO |
| هل تم استخدام تشفير مناسب؟ | ✅ bcrypt (rounds=12) أو argon2id |
| هل الكود قابل للصيانة؟ | ✅ طبقات واضحة + هيكل منظم |
| هل يمكن تشغيل النظام فعلياً؟ | ✅ Docker Compose + Seed + تعليمات واضحة |

---

**أخرج النسخة النهائية المنظمة الكاملة القابلة للتنفيذ مباشرة، مع الكود الكامل لكل مكون، مصقولاً ومرتباً بالترتيب الموضح في هذا البرومبت.**
