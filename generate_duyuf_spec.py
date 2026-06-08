"""
منصة ضيوف — مواصفات النظام الكاملة PDF
"""
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import HRFlowable

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_R = '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf'
FONT_B = '/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
pdfmetrics.registerFont(TTFont('Ar',  FONT_R))
pdfmetrics.registerFont(TTFont('ArB', FONT_B))

# ── Arabic helper ──────────────────────────────────────────────────────────────
def a(t):
    return get_display(arabic_reshaper.reshape(str(t)))

# ── Colours ────────────────────────────────────────────────────────────────────
C = dict(
    bg      = colors.HexColor('#0F1117'),
    surface = colors.HexColor('#1A1D27'),
    card    = colors.HexColor('#22263A'),
    border  = colors.HexColor('#2E3452'),
    accent  = colors.HexColor('#6366F1'),
    gold    = colors.HexColor('#F59E0B'),
    green   = colors.HexColor('#10B981'),
    red     = colors.HexColor('#EF4444'),
    blue    = colors.HexColor('#3B82F6'),
    orange  = colors.HexColor('#F97316'),
    teal    = colors.HexColor('#14B8A6'),
    white   = colors.HexColor('#F1F5F9'),
    muted   = colors.HexColor('#64748B'),
    text    = colors.HexColor('#E2E8F0'),
)

W, H = A4

# ── Styles ─────────────────────────────────────────────────────────────────────
# NOTE: wordWrap='RTL' is intentionally NOT set — get_display() already
# produces visual-order text; ReportLab's RTL wrap would double-reverse it.
def S(name, font='Ar', size=10, color=C['text'], align=TA_RIGHT,
      leading=None, spBefore=0, spAfter=4, bold=False):
    return ParagraphStyle(
        name,
        fontName='ArB' if bold else font,
        fontSize=size,
        textColor=color,
        alignment=align,
        leading=leading or size * 1.6,
        spaceBefore=spBefore,
        spaceAfter=spAfter,
        rightIndent=0,
        leftIndent=0,
    )

sTitle   = S('title',   size=28, color=C['gold'],   align=TA_CENTER, bold=True, leading=42)
sH1      = S('h1',      size=18, color=C['accent'],  bold=True, spBefore=14, spAfter=6)
sH2      = S('h2',      size=14, color=C['green'],   bold=True, spBefore=10, spAfter=4)
sH3      = S('h3',      size=11, color=C['gold'],    bold=True, spBefore=6,  spAfter=3)
sBody    = S('body',    size=9,  color=C['text'],    spAfter=3)
sBullet  = S('bullet',  size=9,  color=C['text'],    spAfter=2)
sCenter  = S('center',  size=10, color=C['muted'],   align=TA_CENTER)
sSmall   = S('small',   size=8,  color=C['muted'],   spAfter=2)

def hr():
    return HRFlowable(width='100%', thickness=1,
                      color=C['border'], spaceAfter=8, spaceBefore=4)

def sp(h=6):
    return Spacer(1, h)

def p(text, style=None):
    return Paragraph(a(text), style or sBody)

def h1(text): return p(text, sH1)
def h2(text): return p(text, sH2)
def h3(text): return p(text, sH3)

def bullet(text, color=None):
    st = ParagraphStyle('blt', parent=sBullet,
                        textColor=color or C['text'])
    return Paragraph(a('• ' + text), st)

# ── Table helper ────────────────────────────────────────────────────────────────
# ar_table is the SINGLE place that calls a() on cell text.
# Do NOT pre-process data with a() before passing here — double processing
# (reshape + get_display called twice) produces garbled Arabic.
def ar_table(data, col_widths, hbg=None, fs=8):
    rows = []
    for i, row in enumerate(data):
        cells = []
        for cell in row:
            fn  = 'ArB' if i == 0 else 'Ar'
            fsz = (fs + 1) if i == 0 else fs
            tc  = C['white'] if i == 0 else C['text']
            cells.append(Paragraph(
                a(str(cell)),
                ParagraphStyle('x', fontName=fn, fontSize=fsz,
                               textColor=tc, alignment=TA_RIGHT,
                               leading=fsz * 1.5)
            ))
        rows.append(cells)

    ts = TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  hbg or C['accent']),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C['card'], C['surface']]),
        ('GRID',          (0, 0), (-1, -1),  0.4, C['border']),
        ('TOPPADDING',    (0, 0), (-1, -1),  5),
        ('BOTTOMPADDING', (0, 0), (-1, -1),  5),
        ('LEFTPADDING',   (0, 0), (-1, -1),  6),
        ('RIGHTPADDING',  (0, 0), (-1, -1),  6),
        ('VALIGN',        (0, 0), (-1, -1),  'MIDDLE'),
    ])
    return Table(rows, colWidths=col_widths, style=ts, repeatRows=1)

# ── Page background ─────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C['bg'])
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(C['muted'])
    canvas.setFont('Ar', 7)
    canvas.drawCentredString(
        W / 2, 1.2 * cm,
        a(f'منصة ضيوف — وثيقة المواصفات الفنية — صفحة {doc.page}')
    )
    canvas.restoreState()

# ══════════════════════════════════════════════════════════════════════════════
# CONTENT
# ══════════════════════════════════════════════════════════════════════════════
def build():
    out = '/home/user/https-github.com-anthropics-skills-commit-690f15cac7f7b4c055c5ab109c79ed9259934081/duyuf-platform-spec.pdf'
    doc = SimpleDocTemplate(out, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    M = W - 4 * cm   # usable width

    # ══════════════════════════════════
    # صفحة الغلاف
    # ══════════════════════════════════
    story += [sp(60)]
    story.append(Paragraph(a('منصة ضيوف'), sTitle))
    story.append(sp(8))
    story.append(Paragraph(a('وثيقة المواصفات الفنية الشاملة'),
        S('sub', size=16, color=C['teal'], align=TA_CENTER, bold=True)))
    story.append(sp(6))
    story.append(Paragraph(a('نظام PMS + SaaS + تطبيق حجز مباشر'),
        S('sub2', size=12, color=C['muted'], align=TA_CENTER)))
    story.append(sp(20))

    cover_data = [
        ('الموقع',            'www.dheuof.com'),
        ('البريد الإلكتروني', 'info@dheuof.com'),
        ('Backend',           'NestJS + TypeScript'),
        ('Frontend',          'Next.js 14 App Router'),
        ('قاعدة البيانات',    'PostgreSQL + Prisma ORM'),
        ('التطبيق',           'Flutter (Android / iOS / Windows)'),
        ('المصادقة',          'JWT + OTP + HttpOnly Cookie'),
        ('الاشتراك',          'SaaS - فترة تجربة 60 يوم'),
        ('الإصدار',           'v1.0 - وثيقة ما قبل البناء'),
    ]
    story.append(ar_table(
        [('الخاصية', 'القيمة')] + cover_data,
        [M * 0.4, M * 0.6], hbg=C['accent'], fs=9
    ))
    story.append(PageBreak())

    # ══════════════════════════════════
    # فهرس المحتويات
    # ══════════════════════════════════
    story.append(h1('فهرس المحتويات'))
    story.append(hr())
    toc = [
        ('1',  'نظرة معمارية عامة'),
        ('2',  'الأدوار والمسؤوليات'),
        ('3',  'لوحات التحكم لكل دور'),
        ('4',  'مصفوفة الصلاحيات الكاملة'),
        ('5',  'تصميم قاعدة البيانات'),
        ('6',  'واجهات API - الفهرس الكامل'),
        ('7',  'وحدات PMS'),
        ('8',  'تطبيق الحجز المباشر'),
        ('9',  'ZATCA والفاتورة الإلكترونية'),
        ('10', 'Night Audit'),
        ('11', 'لوحة التقارير و KPI'),
        ('12', 'متطلبات الأمان'),
        ('13', 'الدول والمناطق'),
        ('14', 'هيكل المشروع'),
        ('15', 'متغيرات البيئة'),
        ('16', 'ترتيب التنفيذ'),
        ('17', 'قائمة مراجعة ما قبل الإطلاق'),
    ]
    for num, title in toc:
        story.append(Paragraph(
            a(f'{num}.  {title}'),
            S('toc', size=10, color=C['text'], spAfter=5)
        ))
    story.append(PageBreak())

    # ══════════════════════════════════
    # 1. نظرة معمارية
    # ══════════════════════════════════
    story.append(h1('1. نظرة معمارية عامة'))
    story.append(hr())
    story.append(p('منصة ضيوف نظام SaaS متكامل لإدارة الفنادق والمنشآت الفندقية. '
                   'تجمع بين نظام إدارة الفنادق PMS وتطبيق حجز مباشر للعملاء '
                   'بدون عمولات لمنصات الحجز الخارجية.'))
    story.append(sp(4))

    arch_data = [
        ('الطبقة',       'التقنية',                          'الوظيفة'),
        ('Frontend Web', 'Next.js 14 + TypeScript',          'لوحة تحكم + تطبيق حجز عام'),
        ('Mobile App',   'Flutter (Dart)',                   'تطبيق موظفين + تطبيق حجوزات'),
        ('Backend API',  'NestJS + TypeScript',              'منطق الأعمال + API'),
        ('قاعدة البيانات','PostgreSQL + Prisma',             'تخزين البيانات'),
        ('المصادقة',     'JWT + OTP + bcrypt',               'الأمان والجلسات'),
        ('البريد',       'Zoho Mail (info@dheuof.com)',      'التحقق والإشعارات'),
        ('الدفع',        'Moyasar / HyperPay',               'MADA + Visa + Apple Pay'),
        ('ZATCA',        'UBL 2.1 + TLV QR',                'الفاتورة الإلكترونية'),
        ('SMS',          'Unifonic / Taqnyat',               'OTP + تأكيدات'),
    ]
    story.append(ar_table(arch_data, [M * 0.25, M * 0.35, M * 0.40], hbg=C['accent']))
    story.append(PageBreak())

    # ══════════════════════════════════
    # 2. الأدوار
    # ══════════════════════════════════
    story.append(h1('2. الأدوار والمسؤوليات'))
    story.append(hr())

    roles = [
        ('ADMIN - أنا المالك', C['red'], [
            'يمتلك جميع الصلاحيات على المنصة كاملاً',
            'ينشئ حسابات المنشآت (Manager لكل منشأة)',
            'يرى إحصائيات جميع المنشآت في لوحة واحدة',
            'يدير الاشتراكات والفترات التجريبية',
            'لا يمكن حذفه أو تعديل صلاحياته من أي حساب آخر',
            'لا ينتمي لأي منشأة - يرى الكل',
        ]),
        ('MANAGER - مدير المنشأة', C['orange'], [
            'يدير منشأته الخاصة فقط (فندق، شقق، منتجع...)',
            'ينشئ حسابات الموظفين داخل منشأته',
            'يحدد صلاحيات كل موظف لكل وحدة بشكل منفصل',
            'يضبط إعدادات تطبيق الحجز المباشر',
            'يضبط أوقات الدخول/الخروج و Night Audit',
            'لا يرى بيانات المنشآت الأخرى',
        ]),
        ('EMPLOYEE - موظف المنشأة', C['blue'], [
            'حسابه ينشأ من قِبل Manager منشأته فقط',
            'صلاحياته تحدد بدقة لكل وحدة (حجوزات، كاشير، تدبير...)',
            'لا يستطيع تعديل صلاحياته أو صلاحيات زملائه',
            'يعمل فقط على المهام المسموحة صراحةً',
            'لا يرى بيانات Manager أو Admin',
            'يمكن تعطيل حسابه بواسطة Manager',
        ]),
        ('GUEST - الضيف / النزيل', C['green'], [
            'مستخدم خارجي يحجز عبر تطبيق الحجوزات المباشر',
            'يسجل دخوله برقم الجوال + OTP فقط',
            'يستطيع: بحث + حجز + تتبع + إلغاء + تقييم',
            'لا يرى أي شاشة إدارية',
            'جلسته منفصلة تماماً عن جلسات الموظفين',
            'Token خاص: type = guest',
        ]),
    ]

    for (title, color, items) in roles:
        story.append(KeepTogether([
            Paragraph(a(title),
                S('rt', size=12, color=color, bold=True, spBefore=8, spAfter=4)),
            *[bullet(item) for item in items],
            sp(4),
        ]))

    story.append(PageBreak())

    # ══════════════════════════════════
    # 3. لوحات التحكم لكل دور
    # ══════════════════════════════════
    story.append(h1('3. لوحة تحكم Admin - أنا المالك'))
    story.append(hr())
    story.append(p('Admin هو مالك المنصة الوحيد. لوحة التحكم الخاصة به تعرض بيانات إجمالية '
                   'لجميع المنشآت المسجلة في المنصة - لا ينتمي لأي منشأة ويرى الكل.'))
    story.append(sp(4))
    admin_dash = [
        ('إجمالي المنشآت',      'عدد كل المنشآت + المشتركة + التجريبية + المعلقة'),
        ('إجمالي الإيرادات',    'مجموع الإيرادات من جميع المنشآت'),
        ('المستخدمون',          'إجمالي المديرين + الموظفين في المنصة'),
        ('إدارة المنشآت',       'عرض + تفعيل + تعليق + حذف أي منشأة'),
        ('إدارة الاشتراكات',    'تجديد + تعليق + سجل الدفع لكل منشأة'),
        ('سجل التدقيق الكامل',  'جميع العمليات الحساسة في المنصة كاملاً'),
        ('إعدادات المنصة',      'الصلاحيات الافتراضية + إدارة البنية التحتية'),
    ]
    story.append(ar_table(
        [('البطاقة / القسم', 'المحتوى')] + admin_dash,
        [M * 0.30, M * 0.70], hbg=C['red'], fs=8
    ))
    story.append(sp(10))

    story.append(h1('لوحة تحكم Manager - مدير المنشأة'))
    story.append(hr())
    story.append(p('Manager يدير منشأته الخاصة فقط. '
                   'ينشئ حسابات موظفيه ويحدد صلاحية كل موظف لكل وحدة بشكل منفصل.'))
    story.append(sp(4))
    manager_dash = [
        ('الغرف',       'إجمالي + مشغولة + شاغرة + صيانة'),
        ('الحجوزات',    'وصول + مغادرة + مقيم اليوم'),
        ('الإيرادات',   'اليوم + الأسبوع + الشهر'),
        ('الموظفون',    'إنشاء حساب + تعيين صلاحيات + تفعيل/تعطيل'),
        ('Night Audit', 'إعدادات الوقت + أجهزة الدفع + آخر تشغيل'),
        ('تطبيق الحجز', 'إعدادات + كودات الخصم + تقرير الوفر من العمولات'),
        ('التقارير',    'KPI + Occupancy + Revenue + Guests + Forecast'),
    ]
    story.append(ar_table(
        [('البطاقة / القسم', 'المحتوى')] + manager_dash,
        [M * 0.30, M * 0.70], hbg=C['orange'], fs=8
    ))
    story.append(sp(10))

    story.append(h1('لوحة تحكم Employee - موظف المنشأة'))
    story.append(hr())
    story.append(p('الموظف ينشأ حسابه حصراً من قِبل Manager منشأته. '
                   'كل قسم يظهر فقط إن كانت الصلاحية المقابلة ممنوحة له.'))
    story.append(sp(4))
    emp_dash = [
        ('الحجوزات',        'تظهر إن كانت صلاحية bookings.read ممنوحة'),
        ('Check-in/out',    'تظهر إن كانت صلاحية bookings.check_in ممنوحة'),
        ('Housekeeping',    'مهامه المعينة له - متاح دائماً للموظف'),
        ('الكاشير / ZATCA', 'تظهر إن كانت صلاحية invoices.view ممنوحة'),
        ('الضيوف',          'تظهر إن كانت صلاحية guests.read ممنوحة'),
        ('الملف الشخصي',    'متاح دائماً - لا يعدل إلا بواسطة صاحبه'),
        ('لا يرى',          'بيانات Manager / Admin / إعدادات المنشأة'),
    ]
    story.append(ar_table(
        [('القسم', 'شرط الوصول')] + emp_dash,
        [M * 0.30, M * 0.70], hbg=C['blue'], fs=8
    ))
    story.append(sp(6))

    story.append(h2('كيفية إنشاء حساب موظف'))
    emp_create = [
        ('1', 'Manager يفتح إعدادات ثم الموظفون'),
        ('2', 'يضغط إضافة موظف جديد ويدخل: الاسم + البريد + رقم الجوال'),
        ('3', 'يحدد الصلاحيات لكل وحدة بشكل منفصل (Toggle لكل صلاحية)'),
        ('4', 'يرسل بريد إلكتروني للموظف برابط تفعيل + كلمة مرور مؤقتة'),
        ('5', 'الموظف يفعل حسابه ويغير كلمة المرور عند أول دخول'),
        ('6', 'يمكن Manager تعطيل الحساب أو تعديل الصلاحيات في أي وقت'),
    ]
    story.append(ar_table(
        [('الخطوة', 'الإجراء')] + emp_create,
        [M * 0.12, M * 0.88], hbg=C['blue'], fs=8
    ))
    story.append(PageBreak())

    # ══════════════════════════════════
    # 4. مصفوفة الصلاحيات
    # ══════════════════════════════════
    story.append(h1('4. مصفوفة الصلاحيات الكاملة'))
    story.append(hr())
    story.append(p('جميع الصلاحيات مخزنة في قاعدة البيانات وقابلة للتعديل من لوحة التحكم بدون تعديل الكود.'))
    story.append(sp(4))

    perm_data = [
        ('الصلاحية',                           'الوحدة',        'Admin', 'Manager',    'Employee',       'Guest'),
        ('users.create/read/update/delete',    'المستخدمون',    'كل',   'منشأته',     'لا',             'لا'),
        ('roles.create/read/update/delete',    'الأدوار',       'كل',   'لموظفيه',    'لا',             'لا'),
        ('permissions.assign',                 'الصلاحيات',     'كل',   'لموظفيه',    'لا',             'لا'),
        ('dashboard.view / analytics',         'اللوحة',        'كل',   'نعم',        'محدود',          'لا'),
        ('reports.view / export',              'التقارير',      'كل',   'نعم',        'لا',             'لا'),
        ('settings.view / update',             'الإعدادات',     'كل',   'منشأته',     'لا',             'لا'),
        ('bookings.create/read/update',        'الحجوزات',      'كل',   'نعم',        'حسب الإعداد',    'لا'),
        ('bookings.check_in / check_out',      'الحجوزات',      'كل',   'نعم',        'حسب الإعداد',    'لا'),
        ('rooms.create/read/update',           'الغرف',         'كل',   'نعم',        'rooms.read',     'لا'),
        ('guests.create/read/update',          'الضيوف',        'كل',   'نعم',        'حسب الإعداد',    'لا'),
        ('guests.blacklist / vip_upgrade',     'الضيوف',        'كل',   'نعم',        'لا',             'لا'),
        ('night_audit.run / settings',         'Night Audit',   'كل',   'نعم',        'لا',             'لا'),
        ('invoices.create/view/export',        'ZATCA',         'كل',   'نعم',        'view فقط',       'لا'),
        ('housekeeping.*',                     'التدبير',       'كل',   'نعم',        'نعم',            'لا'),
        ('booking_app.settings/promotions',    'تطبيق الحجز',   'كل',   'نعم',        'لا',             'لا'),
        ('reviews.view / reply',               'التقييمات',     'كل',   'نعم',        'view فقط',       'لا'),
        ('payment_devices.manage',             'أجهزة الدفع',   'كل',   'نعم',        'لا',             'لا'),
        ('audit_logs.view / export',           'سجل التدقيق',   'كل',   'نعم',        'لا',             'لا'),
        ('profile.view / update',              'الملف الشخصي',  'كل',   'نعم',        'نعم',            'نعم'),
    ]
    story.append(ar_table(perm_data,
        [M * 0.30, M * 0.16, M * 0.12, M * 0.135, M * 0.145, M * 0.10],
        hbg=C['accent'], fs=7))
    story.append(PageBreak())

    # ══════════════════════════════════
    # 5. قاعدة البيانات
    # ══════════════════════════════════
    story.append(h1('5. تصميم قاعدة البيانات'))
    story.append(hr())

    tables_info = [
        ('users', C['blue'], [
            ('id',                      'UUID PK',                  'معرف المستخدم'),
            ('name',                    'VARCHAR(100)',              'الاسم الكامل'),
            ('email',                   'VARCHAR UNIQUE',            'البريد الإلكتروني'),
            ('phone',                   'VARCHAR?',                  'رقم الجوال'),
            ('password_hash',           'VARCHAR',                   'كلمة المرور مشفرة bcrypt'),
            ('country / city',          'VARCHAR?',                  'الدولة والمدينة'),
            ('establishment_id',        'FK - establishments?',      'null للـ Admin'),
            ('role_type',               'ENUM',                      'ADMIN / MANAGER / EMPLOYEE'),
            ('is_email_verified',       'BOOLEAN',                   'هل البريد مفعل؟'),
            ('is_active / is_deleted',  'BOOLEAN',                   'الحالة + Soft Delete'),
            ('failed_login_count',      'INT',                       'محاولات الدخول الفاشلة'),
            ('locked_until',            'TIMESTAMP?',                'وقت إلغاء القفل'),
        ]),
        ('establishments', C['green'], [
            ('id',                      'UUID PK',                   'معرف المنشأة'),
            ('serial_number',           'INT UNIQUE',                'رقم تسلسلي: 1، 2، 3...'),
            ('name',                    'VARCHAR',                   'اسم المنشأة'),
            ('slug',                    'VARCHAR UNIQUE',             'للرابط: /book/slug'),
            ('owner_id',                'FK - users',                'مدير المنشأة'),
            ('country / city / district','VARCHAR?',                 'الموقع الجغرافي'),
            ('subscription_status',     'ENUM',                      'TRIAL / ACTIVE / EXPIRED / SUSPENDED'),
            ('trial_ends_at',           'TIMESTAMP',                 'تاريخ انتهاء التجربة 60 يوم'),
            ('subscription_ends_at',    'TIMESTAMP?',                'تاريخ انتهاء الاشتراك'),
        ]),
        ('roles + permissions', C['accent'], [
            ('roles.id / name / is_system',           'UUID / VARCHAR / BOOL',   'الأدوار - is_system يمنع الحذف'),
            ('permissions.id / name / module',        'UUID / VARCHAR / VARCHAR', 'الصلاحيات مصنفة بالوحدة'),
            ('role_permissions',                      'role_id + permission_id', 'ربط الأدوار بالصلاحيات'),
            ('user_roles',                            'user_id + role_id PK',    'ربط المستخدمين بالأدوار'),
            ('user_permissions',                      'user_id + permission_id', 'صلاحيات مخصصة إضافية'),
        ]),
        ('tokens + security', C['orange'], [
            ('refresh_tokens',            'token_hash UNIQUE + expires_at', 'Refresh Token كـ Hash فقط'),
            ('password_reset_tokens',     'token_hash + is_used',           'Single-Use - 30 دقيقة'),
            ('email_verification_tokens', 'otp_hash + expires_at',          'OTP - 15 دقيقة'),
            ('login_attempts',            'email + ip_address + is_success', 'تتبع محاولات الدخول'),
            ('audit_logs',                'action + old_value + new_value',  'سجل كل العمليات الحساسة'),
        ]),
        ('direct_bookings', C['teal'], [
            ('booking_ref',                 'VARCHAR UNIQUE',     'DB-2025-00001'),
            ('establishment_id',            'FK',                 'المنشأة'),
            ('room_type_id / room_id',      'FK / FK?',           'النوع + الغرفة عند الوصول'),
            ('guest_name/phone/email',      'VARCHAR',            'بيانات العميل'),
            ('guest_country / guest_city',  'VARCHAR?',           'الدولة والمدينة'),
            ('check_in_date / check_out_date', 'TIMESTAMP',       'تواريخ الإقامة'),
            ('nights / adults / children',  'INT',                'تفاصيل الإقامة'),
            ('base_price / discount / final_price', 'DECIMAL',    'التسعير'),
            ('vat_amount / total_with_vat', 'DECIMAL',            'الضريبة والإجمالي'),
            ('status',                      'ENUM',               'PENDING / CONFIRMED / CHECKED_IN / CHECKED_OUT'),
            ('payment_status / paid_amount','ENUM / DECIMAL',     'حالة الدفع'),
        ]),
        ('pms tables', C['gold'], [
            ('room_types',          'id + name + base_price + max_occupancy',    'أنواع الغرف'),
            ('rooms',               'id + room_number + floor + status',         'الغرف الفعلية + RoomStatus'),
            ('guests',              'id + full_name + phone + country + vip_level', 'ملفات الضيوف'),
            ('booking_reviews',     'overall/cleanliness/service/location/value', 'تقييمات بعد الخروج'),
            ('night_audit_settings','scheduled_time + default_check_in',         'إعدادات Night Audit'),
            ('night_audit_logs',    'audit_date + status + total_revenue',        'سجل الإغلاق اليومي'),
            ('payment_devices',     'device_name + device_type + daily_total',   'أجهزة الدفع'),
            ('payments',            'booking_id + method + status + settled',     'المدفوعات'),
            ('zatca_invoices',      'invoice_number + qr_tlv_base64 + status',   'الفواتير الإلكترونية'),
            ('housekeeping_tasks',  'room_id + task_type + priority + status',   'مهام التدبير'),
            ('booking_app_settings','direct_discount + cancellation_policy',     'إعدادات تطبيق الحجز'),
            ('promotions',          'code UNIQUE + discount_type + valid_from',  'كودات الخصم'),
            ('subscriptions',       'serial_number + plan + starts_at + ends_at','سجل الاشتراكات'),
        ]),
    ]

    for (tname, tcolor, fields) in tables_info:
        story.append(KeepTogether([
            Paragraph(a('جدول: ' + tname),
                S('th', size=11, color=tcolor, bold=True, spBefore=8, spAfter=3)),
            ar_table(
                [('الحقل / المفتاح', 'النوع', 'الغرض')] + fields,
                [M * 0.30, M * 0.32, M * 0.38], hbg=tcolor, fs=7
            ),
            sp(4),
        ]))

    story.append(PageBreak())

    # ══════════════════════════════════
    # 6. API
    # ══════════════════════════════════
    story.append(h1('6. واجهات API - الفهرس الكامل'))
    story.append(hr())

    api_sections = [
        ('المصادقة', C['accent'], [
            ('POST',   '/auth/register',              'تسجيل منشأة جديدة + بدء تجربة 60 يوم',   'عام'),
            ('POST',   '/auth/login',                 'تسجيل الدخول + إصدار Tokens',             'عام'),
            ('POST',   '/auth/logout',                'تسجيل الخروج + إلغاء Refresh Token',      'مسجل'),
            ('POST',   '/auth/refresh-token',         'تجديد Access Token',                       'Cookie'),
            ('POST',   '/auth/forgot-password',       'إرسال رابط إعادة التعيين',                'عام'),
            ('POST',   '/auth/reset-password',        'تعيين كلمة مرور جديدة',                   'Token'),
            ('POST',   '/auth/verify-email',          'تفعيل البريد بـ OTP',                      'عام'),
            ('GET',    '/auth/me',                    'بيانات المستخدم + أدواره + صلاحياته',      'مسجل'),
        ]),
        ('المستخدمون والمنشآت', C['blue'], [
            ('GET',    '/users',                      'قائمة المستخدمين مع بحث وتصفية',          'users.read'),
            ('POST',   '/users',                      'إنشاء موظف جديد',                         'users.create'),
            ('PATCH',  '/users/:id',                  'تعديل بيانات مستخدم',                     'users.update'),
            ('DELETE', '/users/:id',                  'حذف ناعم Soft Delete',                    'users.delete'),
            ('PATCH',  '/users/:id/activate',         'تفعيل الحساب',                            'users.activate'),
            ('POST',   '/users/:id/assign-role',      'تعيين دور لمستخدم',                       'permissions.assign'),
            ('GET',    '/establishments',             'كل المنشآت (Admin فقط)',                  'Admin'),
            ('POST',   '/subscriptions/renew',        'تجديد الاشتراك برقم المنشأة',             'settings.update'),
        ]),
        ('الأدوار والصلاحيات', C['teal'], [
            ('GET',    '/roles',                      'قائمة الأدوار',                           'roles.read'),
            ('POST',   '/roles',                      'إنشاء دور جديد',                         'roles.create'),
            ('PATCH',  '/roles/:id',                  'تعديل الدور',                             'roles.update'),
            ('DELETE', '/roles/:id',                  'حذف دور غير نظامي',                      'roles.delete'),
            ('GET',    '/permissions',                'قائمة الصلاحيات',                         'permissions.read'),
            ('POST',   '/roles/:id/permissions',      'ربط صلاحيات بدور',                       'permissions.assign'),
            ('DELETE', '/roles/:id/permissions/:pid', 'إزالة صلاحية من دور',                    'permissions.assign'),
        ]),
        ('PMS - الغرف والضيوف والحجوزات', C['green'], [
            ('GET',    '/rooms/availability',         'فحص التوفر ?checkIn&checkOut',            'rooms.read'),
            ('POST',   '/rooms',                      'إضافة غرفة جديدة',                       'rooms.create'),
            ('PATCH',  '/rooms/:id/status',           'تغيير حالة الغرفة',                      'rooms.change_status'),
            ('GET',    '/guests',                     'قائمة الضيوف مع بحث',                    'guests.read'),
            ('POST',   '/guests',                     'تسجيل ضيف جديد',                         'guests.create'),
            ('GET',    '/guests/:id/history',         'سجل إقامات ضيف',                         'guests.read'),
            ('PATCH',  '/guests/:id/blacklist',       'إضافة لقائمة الحظر',                     'guests.blacklist'),
            ('GET',    '/bookings',                   'قائمة الحجوزات',                          'bookings.read'),
            ('POST',   '/bookings',                   'إنشاء حجز جديد',                         'bookings.create'),
            ('POST',   '/bookings/:id/check-in',      'تسجيل الدخول الفعلي',                    'bookings.check_in'),
            ('POST',   '/bookings/:id/check-out',     'تسجيل الخروج + فاتورة ZATCA',            'bookings.check_out'),
            ('POST',   '/bookings/:id/review',        'تسجيل تقييم بعد الخروج',                 'bookings.update'),
        ]),
        ('Night Audit + ZATCA + Housekeeping', C['orange'], [
            ('GET',    '/night-audit/settings',          'عرض إعدادات Night Audit',             'night_audit.view'),
            ('PATCH',  '/night-audit/settings',          'تعديل الإعدادات (Manager فقط)',        'night_audit.settings'),
            ('POST',   '/night-audit/run',               'تشغيل Night Audit يدوياً',            'night_audit.run'),
            ('GET',    '/night-audit/:date/report',      'تقرير يوم محدد PDF',                   'night_audit.view'),
            ('POST',   '/zatca/invoices/:id/generate',   'إصدار فاتورة ZATCA',                   'invoices.create'),
            ('GET',    '/zatca/invoices/:id/qr',         'صورة QR للفاتورة',                     'invoices.view'),
            ('POST',   '/zatca/verify-qr',               'التحقق من QR (عام - بدون JWT)',        'عام'),
            ('GET',    '/housekeeping',                  'لوحة مهام التدبير',                    'housekeeping.view'),
            ('POST',   '/housekeeping',                  'إنشاء مهمة تدبير',                     'housekeeping.create'),
        ]),
        ('تطبيق الحجز المباشر', C['gold'], [
            ('GET',    '/book/:slug',                    'صفحة المنشأة العامة',                  'عام - بدون JWT'),
            ('GET',    '/book/:slug/search',             'البحث عن غرف متاحة',                  'عام'),
            ('POST',   '/book/:slug/check-promo',        'التحقق من كود خصم',                   'عام'),
            ('POST',   '/book/:slug/create',             'إنشاء حجز مباشر',                     'عام'),
            ('POST',   '/book/:slug/payment',            'بدء عملية الدفع (Moyasar)',            'عام'),
            ('GET',    '/book/my-booking',               'تتبع الحجز برقم الهاتف',              'عام'),
            ('POST',   '/book/my-booking/cancel',        'إلغاء الحجز',                         'عام'),
            ('PATCH',  '/booking-app/settings',          'إعدادات تطبيق الحجز (Manager)',        'booking_app.settings'),
            ('POST',   '/booking-app/promotions',        'إنشاء كود خصم جديد',                  'booking_app.promotions'),
            ('GET',    '/booking-app/savings-report',    'تقرير الوفر من العمولات',              'booking_app.view'),
        ]),
        ('التقارير و KPI', C['teal'], [
            ('GET',    '/reports/kpis',                  'مؤشرات KPI الحية',                    'dashboard.analytics'),
            ('GET',    '/reports/occupancy',             'تقرير الإشغال يومي/شهري',             'reports.view'),
            ('GET',    '/reports/revenue',               'تقرير الإيرادات بالمصدر',             'reports.view'),
            ('GET',    '/reports/guests',                'تقرير الضيوف بالدول والمناطق',        'reports.view'),
            ('GET',    '/reports/reviews',               'تقرير التقييمات',                      'reports.view'),
            ('GET',    '/reports/forecast',              'توقعات الإشغال ?days=7/14/30',        'reports.view'),
            ('GET',    '/reports/savings',               'الوفر من العمولات vs OTA',             'reports.view'),
            ('GET',    '/audit-logs',                    'سجل التدقيق',                          'audit_logs.view'),
        ]),
    ]

    for (section_title, section_color, endpoints) in api_sections:
        story.append(h2(section_title))
        story.append(ar_table(
            [('الطريقة', 'المسار', 'الوظيفة', 'الصلاحية')] + endpoints,
            [M * 0.10, M * 0.28, M * 0.40, M * 0.22],
            hbg=section_color, fs=7
        ))
        story.append(sp(6))

    story.append(PageBreak())

    # ══════════════════════════════════
    # 7. وحدات PMS
    # ══════════════════════════════════
    story.append(h1('7. وحدات النظام PMS'))
    story.append(hr())

    modules = [
        ('تطبيق الحجز المباشر', C['green'], [
            'رابط مباشر للعملاء: dheuof.com/book/{slug}',
            'بحث عن غرف + اختيار التواريخ + عدد النزلاء',
            'حساب السعر تلقائياً مع الخصومات',
            'خصم الحجز المباشر (افتراضي 5%) - يوفر عمولات OTA 15-25%',
            'خصم الحجز المبكر (افتراضي 10% عند الحجز قبل 30 يوم)',
            'خصم الإقامة الطويلة (افتراضي 15% من 7 ليالٍ)',
            'كودات خصم مخصصة من المدير (Promotions)',
            'الدفع عبر Moyasar: MADA + Visa + Apple Pay',
            'تأكيد الحجز بـ QR Code + SMS + Email',
            'تتبع الحجز برقم الجوال بدون تسجيل دخول',
            'إلغاء مع احتساب الاسترداد حسب السياسة',
            'تقييم بعد الخروج (5 معايير × 5 نجوم)',
        ]),
        ('Night Audit', C['orange'], [
            'وقت تشغيل اختياري - يضبطه المدير (افتراضي 23:59)',
            'تشغيل تلقائي بـ Cron ديناميكي أو يدوي',
            'يمنع التشغيل إذا كانت هناك مدفوعات معلقة',
            'يحدث حالة الحجوزات: DUE_OUT - تمديد أو No-Show',
            'يثبت إيرادات اليوم ويمنع تعديلها',
            'يولد تقرير PDF',
            'ربط أجهزة الدفع: POS + MADA + Visa + CASH_DRAWER',
            'تعديل وقت الدخول/الخروج الافتراضي: Manager فقط',
        ]),
        ('ZATCA - الفاتورة الإلكترونية', C['red'], [
            'إصدار فاتورة مبسطة تلقائياً عند Check-out',
            'QR Code بمعيار TLV الرسمي من ZATCA',
            'QR قابل للقراءة بأي جهاز + التحقق من صحة الفاتورة',
            'ضريبة القيمة المضافة 15% محسوبة تلقائياً',
            'XML موقع وفق UBL 2.1',
            'إرسال للـ ZATCA API (Sandbox أو Production)',
            'صفحة Scanner بالكاميرا للتحقق من QR',
            'فاتورة دائن (Credit Note) عند الاسترداد',
        ]),
        ('التقارير و KPI', C['teal'], [
            'KPI حية: الإشغال + ADR + RevPAR + الإيرادات',
            'تقرير الإشغال: يومي / أسبوعي / شهري',
            'تقرير الإيرادات: حسب المصدر + نوع الغرفة + طريقة الدفع',
            'تقرير الضيوف: توزيع الدول والمناطق (Shamoos)',
            'تقرير التقييمات: Radar Chart لـ 5 معايير',
            'توقعات الإشغال: 7 / 14 / 30 يوم',
            'تقرير الوفر من العمولات vs OTA',
            'تصدير كل تقرير: PDF أو Excel',
        ]),
        ('Housekeeping', C['blue'], [
            'مهمة تنظيف تنشأ تلقائياً عند كل Check-out',
            'حالة الغرفة تتغير تلقائياً: DIRTY - CLEAN',
            'لوحة Kanban: PENDING - IN_PROGRESS - DONE',
            'أنواع المهام: CLEANING / INSPECTION / MAINTENANCE / TURNDOWN',
            'أولوية: LOW / MEDIUM / HIGH / URGENT',
            'تعيين المهمة لموظف محدد',
        ]),
        ('Channel Manager', C['accent'], [
            'مزامنة التوفر مع: Booking.com + Airbnb + Expedia + Agoda',
            'تحديث التوفر تلقائياً عند كل حجز أو إلغاء',
            'استقبال حجوزات من OTA عبر Webhook',
            'سجل نجاح/فشل كل عملية مزامنة',
            'Retry Queue للعمليات الفاشلة',
        ]),
    ]

    for (mod_title, mod_color, items) in modules:
        story.append(KeepTogether([
            Paragraph(a(mod_title),
                S('mt', size=12, color=mod_color, bold=True, spBefore=8, spAfter=3)),
            *[bullet(item) for item in items],
            sp(4),
        ]))

    story.append(PageBreak())

    # ══════════════════════════════════
    # 8. متطلبات الأمان
    # ══════════════════════════════════
    story.append(h1('8. متطلبات الأمان'))
    story.append(hr())

    sec_data = [
        ('كلمات المرور',  'bcrypt rounds=12 أو argon2id - لا تخزين كنص صريح'),
        ('JWT',           'Access Token 15 دقيقة في الذاكرة + Refresh Token 7 أيام في DB كـ Hash'),
        ('Cookie',        'HttpOnly + Secure + SameSite=Strict + Path=/auth/refresh'),
        ('Rate Limiting', '5 محاولات / 15 دقيقة لكل IP على مسارات Auth'),
        ('قفل الحساب',    '30 دقيقة بعد 5 محاولات فاشلة متتالية'),
        ('رسالة الخطأ',   'بيانات الدخول غير صحيحة - لا يكشف سبب الفشل'),
        ('SQL Injection', 'Prisma Parameterized Queries فقط - لا Raw SQL'),
        ('XSS',           'DOMPurify (Frontend) + sanitize-html (Backend)'),
        ('CSRF',          'Double Submit Cookie Pattern أو SameSite=Strict'),
        ('Input Validation','class-validator + class-transformer على كل DTO'),
        ('Security Headers','Helmet.js في NestJS'),
        ('CORS',          'Whitelist صريح - لا * في Production'),
        ('Escalation',    'لا مستخدم يرفع صلاحياته بنفسه - OwnershipGuard'),
        ('Admin Protection','لا يمكن حذف أو تعديل حساب Admin من أي حساب آخر'),
        ('Row Isolation', 'Manager يرى منشأته فقط - EstablishmentContextInterceptor'),
        ('Guest Isolation','GuestGuard - مسارات Guest لا تقبل Staff tokens'),
        ('الأسرار',       'جميع المفاتيح في .env - لا في الكود - .env في .gitignore'),
        ('Audit Logs',    'كل عملية حساسة تسجل تلقائياً بـ AuditLogInterceptor'),
        ('Soft Delete',   'جميع الجداول الرئيسية تدعم is_deleted + deleted_at'),
        ('ZATCA Keys',    'شهادة + مفتاح ZATCA في .env فقط - لا في قاعدة البيانات'),
    ]
    story.append(ar_table(
        [('المتطلب', 'التفاصيل')] + sec_data,
        [M * 0.25, M * 0.75], hbg=C['red'], fs=8
    ))
    story.append(PageBreak())

    # ══════════════════════════════════
    # 9. الدول والمناطق
    # ══════════════════════════════════
    story.append(h1('9. الدول والمناطق'))
    story.append(hr())
    story.append(p('مكون CountryRegionSelect.tsx مشترك يستخدم في:'))
    for loc in ['نموذج تسجيل حساب المنشأة', 'نموذج إنشاء حجز مباشر',
                'ملف الضيف', 'إعدادات المنشأة', 'تقرير الضيوف (Shamoos)']:
        story.append(bullet(loc))
    story.append(sp(6))

    regions_data = [
        ('عند اختيار السعودية',    'قائمة منسدلة بالمناطق الـ 13'),
        ('عند اختيار دولة أخرى',  'حقل نصي حر لإدخال المدينة'),
        ('الحقول المضافة للجداول', 'country (ISO code) + city (نص)'),
        ('استخدام في التقارير',    'تقرير الضيوف: by_country + by_city'),
        ('استخدام في Shamoos',     'تمييز السعوديين عن غير السعوديين تلقائياً'),
    ]
    story.append(ar_table(
        [('السلوك', 'التفاصيل')] + regions_data,
        [M * 0.35, M * 0.65], hbg=C['teal'], fs=8
    ))

    story.append(sp(8))
    story.append(h2('المناطق السعودية الـ 13'))
    regions = [
        'الرياض', 'مكة المكرمة', 'المدينة المنورة', 'القصيم',
        'المنطقة الشرقية', 'عسير', 'تبوك', 'حائل',
        'الحدود الشمالية', 'جازان', 'نجران', 'الباحة', 'الجوف',
    ]
    story.append(ar_table([regions[:7]],  [M / 7] * 7, hbg=C['teal'], fs=8))
    story.append(sp(3))
    story.append(ar_table([regions[7:]], [M / 7] * 7, hbg=C['teal'], fs=8))
    story.append(PageBreak())

    # ══════════════════════════════════
    # 10. هيكل المشروع
    # ══════════════════════════════════
    story.append(h1('10. هيكل المشروع'))
    story.append(hr())

    struct_data = [
        ('Backend - NestJS', [
            'src/auth/                   --- المصادقة + strategies + DTOs',
            'src/users/                  --- إدارة المستخدمين',
            'src/establishments/         --- المنشآت',
            'src/subscriptions/          --- الاشتراكات والتجديد',
            'src/roles/ + permissions/   --- الأدوار والصلاحيات',
            'src/rooms/ + room-types/    --- الغرف وأنواعها',
            'src/guests/                 --- ملفات الضيوف',
            'src/bookings/               --- الحجوزات (Staff)',
            'src/booking-app/            --- تطبيق الحجز المباشر',
            'src/night-audit/            --- Night Audit',
            'src/zatca/                  --- ZATCA + QR',
            'src/housekeeping/           --- التدبير الفندقي',
            'src/reports/                --- التقارير و KPI',
            'src/audit-logs/             --- سجل التدقيق',
            'src/common/guards/          --- JwtAuth + Roles + Permissions + Subscription + Ownership + Guest',
            'src/common/interceptors/    --- AuditLog + EstablishmentContext',
            'src/common/data/            --- locations.ts (ثابت - لا DB)',
            'src/mail/ + sms/            --- البريد والرسائل',
            'prisma/schema.prisma + seed.ts',
        ]),
        ('Frontend - Next.js 14', [
            'app/(auth)/                 --- login + register + verify + forgot + reset',
            'app/(dashboard)/            --- لوحة التحكم الكاملة',
            'app/(dashboard)/bookings/   --- check-in + check-out + review',
            'app/(dashboard)/night-audit/ --- إعدادات + تشغيل + سجل',
            'app/(dashboard)/zatca/scanner --- قارئ QR',
            'app/(dashboard)/reports/    --- تقارير + مخططات',
            'app/(dashboard)/booking-app/ --- إعدادات تطبيق الحجز',
            'app/book/[slug]/            --- صفحات الحجز العامة (Public)',
            'app/guest/                  --- ملف الضيف (OTP Login)',
            'app/401/ + 403/             --- صفحات الخطأ',
            'components/CountryRegionSelect --- مكون الدول والمناطق المشترك',
            'store/auth.store.ts         --- Zustand للجلسة',
        ]),
    ]
    for (section, items) in struct_data:
        story.append(h2(section))
        for item in items:
            story.append(Paragraph(
                item,
                ParagraphStyle('code2', fontName='Courier', fontSize=7.5,
                               textColor=C['teal'], alignment=TA_LEFT,
                               leading=12, spaceAfter=2)
            ))
        story.append(sp(6))

    story.append(PageBreak())

    # ══════════════════════════════════
    # 11. متغيرات البيئة
    # ══════════════════════════════════
    story.append(h1('11. متغيرات البيئة (.env.example)'))
    story.append(hr())

    env_groups = [
        ('التطبيق', [
            'NODE_ENV=development',
            'PORT=3001',
            'APP_URL=http://localhost:3001',
            'FRONTEND_URL=http://localhost:3000',
        ]),
        ('قاعدة البيانات', [
            'DATABASE_URL=postgresql://USER:PASS@localhost:5432/duyuf_db',
        ]),
        ('JWT', [
            'JWT_ACCESS_SECRET=REPLACE_MIN_64_CHARS',
            'JWT_ACCESS_EXPIRES_IN=15m',
            'JWT_REFRESH_SECRET=REPLACE_DIFFERENT_MIN_64_CHARS',
            'JWT_REFRESH_EXPIRES_IN=7d',
        ]),
        ('الأمان', [
            'BCRYPT_SALT_ROUNDS=12',
            'THROTTLE_TTL=900',
            'THROTTLE_LIMIT=5',
            'ACCOUNT_LOCK_MINUTES=30',
            'TRIAL_DAYS=60',
            'ADMIN_DEFAULT_PASSWORD=REPLACE_STRONG_PASS',
        ]),
        ('البريد', [
            'MAIL_HOST=smtp.zoho.sa',
            'MAIL_PORT=587',
            'MAIL_USER=info@dheuof.com',
            'MAIL_PASSWORD=REPLACE',
        ]),
        ('الدفع', [
            'PAYMENT_GATEWAY=moyasar',
            'MOYASAR_API_KEY=REPLACE',
            'MOYASAR_WEBHOOK_SECRET=REPLACE',
        ]),
        ('ZATCA', [
            'ZATCA_ENV=sandbox',
            'ZATCA_VAT_NUMBER=REPLACE',
            'ZATCA_CERTIFICATE=REPLACE',
            'ZATCA_PRIVATE_KEY=REPLACE',
        ]),
        ('SMS', [
            'SMS_PROVIDER=unifonic',
            'SMS_API_KEY=REPLACE',
        ]),
    ]

    for (gname, gvars) in env_groups:
        story.append(h3(gname))
        for var in gvars:
            story.append(Paragraph(
                var,
                ParagraphStyle('env', fontName='Courier', fontSize=8,
                               textColor=C['teal'], alignment=TA_LEFT,
                               leading=12, spaceAfter=2, leftIndent=10)
            ))
        story.append(sp(4))

    story.append(PageBreak())

    # ══════════════════════════════════
    # 12. ترتيب التنفيذ
    # ══════════════════════════════════
    story.append(h1('12. ترتيب التنفيذ المقترح'))
    story.append(hr())

    impl_data = [
        ('1',  'البنية الأساسية',       'إعداد NestJS + Next.js + Prisma + Docker + Auth + Guards'),
        ('2',  'نظام المصادقة',         'Register + Login + OTP + JWT + Refresh Token + Rate Limiting'),
        ('3',  'الأدوار والصلاحيات',    'Seed الأدوار والصلاحيات + RBAC Guards + لوحة الإدارة'),
        ('4',  'الاشتراكات',            'Serial Number تلقائي + Trial 60 يوم + Subscription Guard'),
        ('5',  'بيانات الدول والمناطق', 'locations.ts + CountryRegionSelect مكون مشترك'),
        ('6',  'الغرف والضيوف',         'RoomTypes + Rooms + Guests + Room Map'),
        ('7',  'الحجوزات (للموظفين)',   'Bookings + Check-in + Check-out + Review + Housekeeping Auto'),
        ('8',  'Night Audit',           'Settings + PaymentDevices + Cron ديناميكي + تقرير PDF'),
        ('9',  'ZATCA',                 'TLV Builder + QR Generator + QR Scanner + ZATCA API'),
        ('10', 'تطبيق الحجز المباشر',   'Public Pages + Pricing Engine + Promotions + Payment + تأكيد'),
        ('11', 'التقارير و KPI',        'Dashboard KPIs + 6 تقارير + تصدير PDF/Excel + Recharts'),
        ('12', 'Channel Manager',       'مزامنة OTA + Webhook استقبال حجوزات خارجية'),
        ('13', 'Shamoos + Revenue Mgmt','تقرير شهري + تسعير ديناميكي حسب الإشغال'),
        ('14', 'Open API + Webhooks',   'API Keys + Rate Limit + Webhook events'),
    ]
    story.append(ar_table(
        [('الخطوة', 'المرحلة', 'المحتوى')] + impl_data,
        [M * 0.08, M * 0.25, M * 0.67], hbg=C['accent'], fs=8
    ))
    story.append(PageBreak())

    # ══════════════════════════════════
    # 13. قائمة مراجعة ما قبل الإطلاق
    # ══════════════════════════════════
    story.append(h1('13. قائمة مراجعة ما قبل الإطلاق'))
    story.append(hr())

    checklist = [
        ('الأمان', C['red'], [
            'NODE_ENV=production في بيئة الإنتاج',
            'HTTPS + SSL Certificate فعال',
            'تغيير كلمة مرور Admin الافتراضية فور أول تشغيل',
            'CORS بالنطاقات الصحيحة فقط (لا *)',
            '.env لا يوجد في Git',
            'Refresh Token Rotation عند كل تجديد',
            'Rate Limiting فعال على مسارات Auth',
            'Swagger Docs محظور في Production',
        ]),
        ('قاعدة البيانات', C['blue'], [
            'Prisma Migrations نفذت بنجاح في Production',
            'Seed Data: أدوار + صلاحيات + Admin افتراضي',
            'Database Connection Pooling (PgBouncer)',
            'Backup تلقائي يومي لقاعدة البيانات',
        ]),
        ('الوظائف', C['green'], [
            'اختبار Night Audit في Staging أولاً',
            'اختبار ZATCA في Sandbox قبل Production',
            'اختبار بوابة الدفع Moyasar (Test - Production)',
            'اختبار إرسال SMS + البريد الإلكتروني',
            'اختبار QR Scanner على Android + iOS',
            'اختبار جميع سيناريوهات الصلاحيات',
        ]),
        ('المراقبة', C['orange'], [
            'Monitoring + Error Tracking (Sentry)',
            'Logging موجه لخدمة مركزية',
            'npm audit - لا ثغرات في الـ dependencies',
            'Performance Test: PageSpeed > 90 على الجوال',
        ]),
    ]

    for (cat, cat_color, items) in checklist:
        story.append(KeepTogether([
            Paragraph(a(cat),
                S('cl', size=11, color=cat_color, bold=True, spBefore=6, spAfter=3)),
            *[Paragraph(a('- ' + item),
                ParagraphStyle('ci', fontName='Ar', fontSize=9,
                               textColor=C['text'], alignment=TA_RIGHT,
                               leading=14, spaceAfter=3))
              for item in items],
            sp(4),
        ]))

    # ══════════════════════════════════
    # صفحة الختام
    # ══════════════════════════════════
    story.append(PageBreak())
    story.append(sp(80))
    story.append(Paragraph(a('منصة ضيوف'), sTitle))
    story.append(sp(8))
    story.append(Paragraph(a('وثيقة المواصفات الفنية - نهاية الوثيقة'),
        S('end', size=12, color=C['muted'], align=TA_CENTER)))
    story.append(sp(6))
    story.append(Paragraph(a('www.dheuof.com  |  info@dheuof.com'),
        S('end2', size=10, color=C['teal'], align=TA_CENTER)))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f'PDF saved: {out}')
    return out


if __name__ == '__main__':
    build()
