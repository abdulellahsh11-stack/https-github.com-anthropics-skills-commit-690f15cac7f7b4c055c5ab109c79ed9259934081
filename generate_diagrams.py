"""
Duyuf Platform — Architecture Diagrams PDF
Arabic text fix: FontProperties applied only to Arabic strings;
English strings use the default DejaVu font.
Color fix: alpha passed as separate parameter, never concatenated onto hex strings.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
import matplotlib.colors as mcolors
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Spacer, Image,
                                Paragraph, Table, TableStyle, HRFlowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import io

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_R = '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf'
FONT_B = '/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
pdfmetrics.registerFont(TTFont('Ar',  FONT_R))
pdfmetrics.registerFont(TTFont('ArB', FONT_B))
FP  = FontProperties(fname=FONT_R)
FPB = FontProperties(fname=FONT_B)

# ── Arabic helpers ─────────────────────────────────────────────────────────────
def a(t):
    """Reshape + bidi for matplotlib Arabic text."""
    return get_display(arabic_reshaper.reshape(str(t)))

def rl(t):
    """Reshape + bidi for ReportLab."""
    return get_display(arabic_reshaper.reshape(str(t)))

# ── Colour palette (pure 6-char hex, no alpha embedded) ───────────────────────
C = dict(
    bg='#0F1117', surface='#1A1D27', card='#22263A', border='#2E3452',
    admin='#EF4444', manager='#F97316', employee='#3B82F6', user='#22C55E',
    accent='#6366F1', gold='#F59E0B', teal='#14B8A6', pink='#EC4899',
    text='#F1F5F9', muted='#94A3B8', green='#10B981', red='#EF4444',
    white='#FFFFFF', purple='#7C3AED', sky='#0EA5E9',
)

# ── Low-level helpers ──────────────────────────────────────────────────────────
def _rgba(hex_color, alpha):
    r, g, b = mcolors.to_rgb(hex_color)
    return (r, g, b, alpha)

def fig_axes(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(C['bg'])
    ax.set_facecolor(C['bg'])
    ax.axis('off')
    return fig, ax

def to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf

def box(ax, x, y, w, h, fc, ec, lw=1.5, r=0.25, z=3, fa=0.25, ea=1.0):
    """Draw a rounded rectangle. fa=face alpha, ea=edge alpha."""
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.03,rounding_size={r}",
                       facecolor=_rgba(fc, fa),
                       edgecolor=_rgba(ec, ea),
                       linewidth=lw, zorder=z)
    ax.add_patch(p)

def solid_box(ax, x, y, w, h, fc, lw=0, r=0.0, z=3):
    """Solid (no alpha) box, e.g. for headers."""
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.03,rounding_size={r}",
                       facecolor=fc, edgecolor=fc,
                       linewidth=lw, zorder=z)
    ax.add_patch(p)

def at(ax, x, y, s, fp=None, size=9, color=C['white'],
       ha='center', va='center', z=4, bold=False):
    """Text helper. fp=None → default font (DejaVu, for English)."""
    kw = dict(ha=ha, va=va, fontsize=size, color=color, zorder=z)
    if fp:
        kw['fontproperties'] = fp
    elif bold:
        kw['fontweight'] = 'bold'
    ax.text(x, y, s, **kw)

def ar_text(ax, x, y, s, size=9, bold=False, color=C['white'],
            ha='center', va='center', z=4):
    """Arabic text, always uses Noto Arabic font."""
    ax.text(x, y, a(s), ha=ha, va=va, fontsize=size, color=color,
            fontproperties=FPB if bold else FP, zorder=z)

def arrow(ax, x1, y1, x2, y2, color=C['muted'], lw=1.8):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw), zorder=2)


# ══════════════════════════════════════════════════════════════════════════════
# D1 — System Architecture
# ══════════════════════════════════════════════════════════════════════════════
def d1():
    fig, ax = fig_axes(18, 12)
    ax.set_xlim(0, 18); ax.set_ylim(0, 12)

    ar_text(ax, 9, 11.6, 'معمارية النظام — منصة ضيوف', 16, True, C['gold'])

    def zone(x, y, w, h, color, ar_lbl, en_lbl):
        box(ax, x, y, w, h, color, color, lw=1.5, r=0.5, z=1, fa=0.08, ea=0.9)
        ar_text(ax, x+0.8, y+h-0.32, ar_lbl, 9, True, color, ha='left', z=2)
        at(ax, x+w-0.5, y+h-0.32, en_lbl, size=8.5, color=color, ha='right', z=2)

    zone(0.3, 8.0, 17.4, 3.5, C['teal'],    'طبقة العميل',   'Client Layer')
    zone(0.3, 4.5, 17.4, 3.1, C['accent'],  'طبقة البوابة',  'API Gateway')
    zone(0.3, 0.8, 17.4, 3.3, C['manager'], 'طبقة البيانات', 'Data Layer')

    def comp(x, y, w, h, color, ar_lbl, en_lbl):
        box(ax, x, y, w, h, color, C['white'], lw=1.2, r=0.2, fa=0.3, ea=0.6)
        ar_text(ax, x+w/2, y+h/2+0.15, ar_lbl, 8.5, True)
        at(ax,    x+w/2, y+h/2-0.15, en_lbl, size=7.5, color=C['muted'])

    # Client
    comp(0.6,  8.5, 3.0, 1.8, C['employee'], 'متصفح ويب',    'Next.js 14')
    comp(4.1,  8.5, 3.0, 1.8, C['teal'],     'تطبيق جوال',   'PWA / Mobile')
    comp(7.6,  8.5, 3.0, 1.8, C['accent'],   'لوحة الادارة', 'Admin Panel')
    comp(11.1, 8.5, 2.8, 1.8, C['pink'],     'خارجي',        'Third-Party')
    comp(14.3, 8.5, 3.0, 1.8, C['gold'],     'توثيق',        'Swagger /docs')

    # Gateway
    comp(0.6,  4.9, 3.0, 1.5, C['accent'],  'بوابة API',    'NestJS + Helmet')
    comp(4.1,  4.9, 2.8, 1.5, C['gold'],    'تحديد المعدل', 'ThrottlerGuard')
    comp(7.3,  4.9, 2.8, 1.5, C['pink'],    'مصادقة',       'JWT AuthGuard')
    comp(10.5, 4.9, 3.0, 1.5, C['manager'], 'صلاحيات',      'PermissionsGuard')
    comp(13.9, 4.9, 3.4, 1.5, C['green'],   'CORS',         'Whitelist Only')

    # Services
    svcs = [
        (0.4,  'خدمة المصادقة',   'AuthService',    C['admin']),
        (2.9,  'خدمة المستخدمين', 'UsersService',   C['manager']),
        (5.4,  'خدمة الادوار',    'RolesService',   C['employee']),
        (7.9,  'خدمة الصلاحيات',  'PermsService',   C['accent']),
        (10.4, 'سجل التدقيق',     'AuditService',   C['teal']),
        (12.9, 'خدمة البريد',     'MailService',    C['pink']),
        (15.4, 'خدمة الحجوزات',  'BookingService', C['gold']),
    ]
    for sx, sar, sen, sc in svcs:
        comp(sx, 2.9, 2.2, 1.3, sc, sar, sen)

    # Data
    comp(0.6,  1.1, 3.2, 1.6, C['sky'],     'قاعدة البيانات', 'PostgreSQL 16')
    comp(4.3,  1.1, 2.8, 1.6, C['red'],     'كاش / جلسات',   'Redis')
    comp(7.5,  1.1, 2.8, 1.6, C['purple'],  'طبقة البيانات',  'Prisma ORM')
    comp(10.7, 1.1, 2.8, 1.6, C['green'],   'البريد',         'SMTP/Nodemailer')
    comp(13.9, 1.1, 3.0, 1.6, C['manager'], 'حاويات',         'Docker Compose')

    for cx in [2.1, 5.6, 9.1, 12.5, 15.8]:
        arrow(ax, min(cx, 15.7), 8.5, min(cx, 15.7), 6.4, C['teal'])
    for cx in [2.1, 5.0, 8.7, 12.0, 15.6]:
        arrow(ax, min(cx, 15.6), 4.9, min(cx, 15.6), 4.2, C['accent'])

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# D2 — Database ERD
# ══════════════════════════════════════════════════════════════════════════════
def d2():
    fig, ax = fig_axes(20, 15)
    ax.set_xlim(0, 20); ax.set_ylim(0, 15)
    ar_text(ax, 10, 14.6, 'مخطط قاعدة البيانات — ERD', 16, True, C['gold'])

    RH = 0.40

    def tbl(x, y, title, fields, color, w=3.8):
        hdr = 0.55
        rows_h = len(fields) * RH + 0.1
        solid_box(ax, x, y-hdr, w, hdr, color, z=3)
        at(ax, x+w/2, y-hdr/2, title, size=9.5, bold=True, z=4)
        box(ax, x, y-hdr-rows_h, w, rows_h, C['card'], color,
            lw=1.5, r=0.0, fa=1.0, ea=1.0)
        for i, (fn, ft, key) in enumerate(fields):
            fy = y - hdr - (i+0.5)*RH - 0.05
            kc = C['gold'] if key == 'PK' else C['teal'] if key == 'FK' else C['muted']
            at(ax, x+0.12, fy, key or '--',
               size=6.5, color=kc, ha='left', bold=True, z=4)
            at(ax, x+0.55, fy, fn, size=7.5, color=C['text'], ha='left', z=4)
            at(ax, x+w-0.1, fy, ft, size=7, color=C['muted'], ha='right', z=4)

    def rel(x1, y1, x2, y2, lbl='', col=C['muted']):
        ax.plot([x1,x2],[y1,y2], color=col, lw=1.1, linestyle='--', alpha=0.6, zorder=1)
        if lbl:
            ax.text((x1+x2)/2+0.08,(y1+y2)/2+0.1, lbl, fontsize=7, color=col)

    tbl(0.3,13.5,'users',[
        ('id','UUID','PK'),('name','VARCHAR',''),('email','VARCHAR',''),
        ('username','VARCHAR',''),('password_hash','VARCHAR',''),
        ('establishment_id','UUID','FK'),('is_email_verified','BOOL',''),
        ('is_active','BOOL',''),('is_deleted','BOOL',''),
        ('subscription_type','ENUM',''),('trial_ends_at','TIMESTAMP',''),
        ('failed_login_count','INT',''),('locked_until','TIMESTAMP',''),
        ('created_at','TIMESTAMP',''),
    ], C['employee'], w=4.1)

    tbl(5.2,13.5,'roles',[
        ('id','UUID','PK'),('name','VARCHAR',''),
        ('description','TEXT',''),('is_system','BOOL',''),
        ('created_at','TIMESTAMP',''),
    ], C['manager'], w=3.6)

    tbl(9.5,13.5,'permissions',[
        ('id','UUID','PK'),('name','VARCHAR',''),
        ('module','VARCHAR',''),('description','TEXT',''),
        ('created_at','TIMESTAMP',''),
    ], C['accent'], w=3.8)

    tbl(13.9,13.5,'user_roles',[
        ('user_id','UUID','FK'),('role_id','UUID','FK'),
        ('assigned_by','UUID','FK'),('assigned_at','TIMESTAMP',''),
    ], C['pink'], w=3.6)

    tbl(13.9,10.8,'role_permissions',[
        ('role_id','UUID','FK'),('permission_id','UUID','FK'),
    ], C['teal'], w=3.6)

    tbl(0.3,7.6,'establishments',[
        ('id','UUID','PK'),('name','VARCHAR',''),
        ('owner_id','UUID','FK'),('is_active','BOOL',''),
        ('created_at','TIMESTAMP',''),
    ], C['gold'], w=4.1)

    tbl(5.2,7.6,'audit_logs',[
        ('id','UUID','PK'),('user_id','UUID','FK'),
        ('action','VARCHAR',''),('entity_type','VARCHAR',''),
        ('entity_id','UUID',''),('old_value','JSONB',''),
        ('new_value','JSONB',''),('ip_address','INET',''),
        ('created_at','TIMESTAMP',''),
    ], C['red'], w=4.1)

    tbl(9.8,7.6,'refresh_tokens',[
        ('id','UUID','PK'),('user_id','UUID','FK'),
        ('token_hash','VARCHAR',''),('expires_at','TIMESTAMP',''),
        ('is_revoked','BOOL',''),('ip_address','INET',''),
        ('created_at','TIMESTAMP',''),
    ], C['teal'], w=3.8)

    tbl(14.0,7.6,'password_reset_tokens',[
        ('id','UUID','PK'),('user_id','UUID','FK'),
        ('token_hash','VARCHAR',''),('expires_at','TIMESTAMP',''),
        ('is_used','BOOL',''),('created_at','TIMESTAMP',''),
    ], C['manager'], w=3.6)

    tbl(0.3,3.3,'email_verification_tokens',[
        ('id','UUID','PK'),('user_id','UUID','FK'),
        ('otp_hash','VARCHAR',''),('expires_at','TIMESTAMP',''),
        ('is_used','BOOL',''),('created_at','TIMESTAMP',''),
    ], C['pink'], w=4.1)

    tbl(5.2,3.3,'login_attempts',[
        ('id','UUID','PK'),('email','VARCHAR',''),
        ('ip_address','INET',''),('is_success','BOOL',''),
        ('attempted_at','TIMESTAMP',''),
    ], C['muted'], w=4.1)

    # relationships
    rel(4.4,12.0, 5.2,11.8, '1:N', C['pink'])
    rel(8.8,12.0, 13.9,11.5,'1:N', C['manager'])
    rel(8.8,11.0, 13.9,10.5,'N:N', C['teal'])
    rel(4.4,8.0,  5.2,7.1,  '1:N', C['red'])
    rel(2.3,8.0,  2.3,3.3,  '1:N', C['pink'])
    rel(2.3,8.5,  9.8,7.1,  '1:N', C['teal'])
    rel(2.3,9.5, 14.0,7.1,  '1:N', C['manager'])

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# D3 — Auth Flow
# ══════════════════════════════════════════════════════════════════════════════
def d3():
    fig, ax = fig_axes(18, 24)
    ax.set_xlim(0, 18); ax.set_ylim(0, 24)
    ar_text(ax, 9, 23.5, 'تدفق المصادقة — Authentication Flow', 15, True, C['gold'])

    def step(x, y, w, h, ar_lbl, en_lbl, color, diamond=False):
        if diamond:
            cx, cy = x+w/2, y+h/2
            poly = plt.Polygon([(cx,y+h),(x+w,cy),(cx,y),(x,cy)],
                               facecolor=_rgba(color, 0.35),
                               edgecolor=color, lw=1.8, zorder=3)
            ax.add_patch(poly)
        else:
            box(ax, x, y, w, h, color, color, lw=1.8, r=0.2, fa=0.25, ea=1.0)
        if ar_lbl:
            ar_text(ax, x+w/2, y+h/2+(0.13 if en_lbl else 0), ar_lbl, 8.5, True)
        if en_lbl:
            at(ax, x+w/2, y+h/2-0.15, en_lbl, size=7.5, color=color)

    def arr(x1,y1,x2,y2, ar_lbl='', color=C['muted']):
        arrow(ax, x1, y1, x2, y2, color)
        if ar_lbl:
            ar_text(ax,(x1+x2)/2+0.15,(y1+y2)/2+0.1, ar_lbl, 7.5, color=color)

    # ── Register ──
    c1 = 0.4
    ar_text(ax, c1+1.7, 22.7, 'تسجيل حساب جديد', 11, True, C['teal'])
    step(c1,21.7,3.4,0.8, 'المستخدم يملأ النموذج',  '',             C['card'])
    arr(c1+1.7,21.7,c1+1.7,21.1)
    step(c1,20.3,3.4,0.75,'التحقق من المدخلات',     'class-validator',C['accent'])
    arr(c1+1.7,20.3,c1+1.7,19.6)
    step(c1,18.7,3.4,0.8, 'هل البريد مكرر؟',        '',             C['card'],True)
    arr(c1+1.7,18.7,c1+1.7,18.1, 'لا', C['green'])
    at(ax,c1+3.55,19.1,'409 Conflict',size=8,color=C['red'],ha='left',bold=True)
    step(c1,17.3,3.4,0.75,'تشفير كلمة المرور',      'bcrypt rounds=12',C['green'])
    arr(c1+1.7,17.3,c1+1.7,16.7)
    step(c1,15.9,3.4,0.75,'حفظ المستخدم',           'PostgreSQL',    C['card'])
    arr(c1+1.7,15.9,c1+1.7,15.3)
    step(c1,14.5,3.4,0.75,'ارسال OTP للبريد',       'Nodemailer',    C['pink'])
    arr(c1+1.7,14.5,c1+1.7,13.9)
    step(c1,13.1,3.4,0.75,'استجابة 201 Created',    '',             C['green'])

    # ── Login ──
    c2 = 7.0
    ar_text(ax, c2+1.7, 22.7, 'تسجيل الدخول', 11, True, C['manager'])
    step(c2,21.7,3.4,0.8, 'بريد + كلمة مرور',       '',             C['card'])
    arr(c2+1.7,21.7,c2+1.7,21.1)
    step(c2,20.3,3.4,0.75,'Rate Limit',              '5 req / 15 min',C['gold'])
    arr(c2+1.7,20.3,c2+1.7,19.6)
    step(c2,18.7,3.4,0.8, 'الحساب مقفل؟',           '',             C['card'],True)
    arr(c2+1.7,18.7,c2+1.7,18.1, 'لا', C['green'])
    at(ax,c2+3.55,19.1,'403 Locked',size=8,color=C['red'],ha='left',bold=True)
    step(c2,17.3,3.4,0.75,'مقارنة كلمة المرور',      'bcrypt.compare()',C['accent'])
    arr(c2+1.7,17.3,c2+1.7,16.7)
    step(c2,15.9,3.4,0.8, 'البيانات صحيحة؟',         '',             C['card'],True)
    arr(c2+1.7,15.9,c2+1.7,15.3, 'نعم', C['green'])
    at(ax,c2+3.55,16.3,'401 + زيادة العداد',size=8,color=C['red'],ha='left')
    step(c2,14.5,3.4,0.75,'اصدار JWT',              'Access+Refresh', C['green'])
    arr(c2+1.7,14.5,c2+1.7,13.9)
    step(c2,13.1,3.4,0.75,'Refresh في HttpOnly Cookie','SameSite=Strict',C['teal'])
    arr(c2+1.7,13.1,c2+1.7,12.5)
    step(c2,11.7,3.4,0.75,'تسجيل في Audit Log',     '',             C['card'])
    arr(c2+1.7,11.7,c2+1.7,11.1)
    step(c2,10.3,3.4,0.75,'استجابة 200 + Access Token','',           C['green'])

    # ── Token Refresh ──
    c3 = 13.6
    ar_text(ax, c3+1.7, 22.7, 'تجديد التوكن', 11, True, C['accent'])
    step(c3,21.7,3.4,0.8, 'Refresh Token من Cookie','',              C['card'])
    arr(c3+1.7,21.7,c3+1.7,21.1)
    step(c3,19.9,3.4,0.8, 'Token صالح؟',            '',             C['card'],True)
    arr(c3+1.7,19.9,c3+1.7,19.3, 'نعم', C['green'])
    at(ax,c3-0.6,20.3,'401',size=8,color=C['red'],ha='right',bold=True)
    step(c3,18.1,3.4,0.8, 'موجود في DB؟',           '',             C['card'],True)
    arr(c3+1.7,18.1,c3+1.7,17.5, 'نعم', C['green'])
    step(c3,16.7,3.4,0.75,'الغاء القديم + اصدار جديد','Rotation',   C['accent'])
    arr(c3+1.7,16.7,c3+1.7,16.1)
    step(c3,15.3,3.4,0.75,'Access Token جديد 15 دقيقة','',          C['green'])
    arr(c3+1.7,15.3,c3+1.7,14.7)
    step(c3,13.5,3.4,0.75,'استجابة 200 OK',          '',            C['green'])

    # ── Password Reset ──
    ar_text(ax, 6.5, 8.8, 'استعادة كلمة المرور', 11, True, C['pink'])
    step(0.4,7.8,10.0,0.75,'المستخدم يرسل بريده الالكتروني','',     C['card'])
    arr(5.4,7.8,5.4,7.2)
    step(0.4,6.4,10.0,0.75,'ارسال رابط اعادة التعيين (30 دقيقة — استخدام واحد)','',C['pink'])
    arr(5.4,6.4,5.4,5.8)
    step(0.4,5.0,10.0,0.75,'التحقق من Token + تعيين كلمة مرور جديدة','',C['accent'])
    arr(5.4,5.0,5.4,4.4)
    step(0.4,3.6,10.0,0.75,'الغاء جميع جلسات المستخدم','revoke all refresh_tokens',C['red'])
    arr(5.4,3.6,5.4,3.0)
    step(0.4,2.2,10.0,0.75,'200 OK — يرجى تسجيل الدخول','',         C['green'])

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# D4 — Roles & Permissions Matrix
# ══════════════════════════════════════════════════════════════════════════════
def d4():
    fig, ax = fig_axes(20, 17)
    ax.set_xlim(0, 20); ax.set_ylim(0, 17)
    ar_text(ax, 10, 16.5, 'مصفوفة الأدوار والصلاحيات', 15, True, C['gold'])

    ROLES   = [('Admin',C['admin']),('Manager',C['manager']),
               ('Employee',C['employee']),('User',C['user'])]
    MOD_COL = dict(users=C['employee'],roles=C['manager'],permissions=C['accent'],
                   dashboard=C['teal'],reports=C['pink'],settings=C['gold'],
                   profile=C['green'],audit_logs=C['red'],
                   bookings=C['purple'],establishments=C['sky'])
    MATRIX  = [
        ('users.create',            (1,1,0,0)),
        ('users.read',              (1,1,0,0)),
        ('users.update',            (1,1,0,0)),
        ('users.delete',            (1,0,0,0)),
        ('roles.create',            (1,0,0,0)),
        ('roles.read',              (1,1,0,0)),
        ('roles.update',            (1,0,0,0)),
        ('roles.delete',            (1,0,0,0)),
        ('permissions.assign',      (1,0,0,0)),
        ('dashboard.view',          (1,1,1,0)),
        ('reports.view',            (1,1,0,0)),
        ('reports.export',          (1,1,0,0)),
        ('settings.update',         (1,1,0,0)),
        ('profile.view',            (1,1,1,1)),
        ('profile.update',          (1,1,1,1)),
        ('audit_logs.view',         (1,0,0,0)),
        ('bookings.create',         (1,1,1,1)),
        ('bookings.read',           (1,1,1,1)),
        ('bookings.update',         (1,1,1,1)),
        ('bookings.delete',         (1,1,0,0)),
        ('establishments.create',   (1,0,0,0)),
        ('establishments.read',     (1,1,1,0)),
        ('establishments.update',   (1,1,0,0)),
        ('establishments.delete',   (1,0,0,0)),
    ]

    PW, RW, RH = 4.5, 3.6, 0.55
    CX = [0.2, PW+0.4, PW+0.4+RW, PW+0.4+2*RW, PW+0.4+3*RW]
    START_Y = 15.8

    # role headers
    for i,(rn,rc) in enumerate(ROLES):
        rx = CX[i+1]
        solid_box(ax, rx, START_Y-0.55, RW-0.1, 0.55, rc, z=3)
        at(ax, rx+(RW-0.1)/2, START_Y-0.275, rn, size=10, bold=True, z=4)

    at(ax, 0.3, START_Y-0.275, 'Module', size=8, bold=True,
       color=C['muted'], ha='left', z=4)
    at(ax, PW*0.5, START_Y-0.275, 'Permission', size=8, bold=True,
       color=C['muted'], ha='center', z=4)

    prev_mod = None
    ry = START_Y - 0.62

    for idx,(pname,vals) in enumerate(MATRIX):
        mod = next((m for m in MOD_COL if pname.startswith(m)), 'other')
        mc  = MOD_COL.get(mod, C['muted'])
        bg  = C['card'] if idx % 2 == 0 else C['surface']
        # row bg
        box(ax,0.2,ry-RH+0.05,19.6,RH-0.1, bg, C['border'],
            lw=0.4,r=0.0,fa=1.0,ea=0.5,z=1)
        # module badge
        if mod != prev_mod:
            box(ax,0.25,ry-RH+0.1,1.9,RH-0.2,mc,mc,lw=0.8,r=0.1,fa=0.2,ea=1.0,z=2)
            at(ax,1.2,ry-RH/2,mod,size=7,bold=True,color=mc,ha='center',z=3)
            prev_mod = mod
        # perm name
        at(ax,2.4,ry-RH/2,pname,size=8.5,color=C['text'],ha='left',z=3)
        # cells
        for i,v in enumerate(vals):
            rx = CX[i+1]
            fc, sym, sc = (C['green'],'YES',C['green']) if v else (C['red'],'NO',C['red'])
            box(ax,rx+0.1,ry-RH+0.07,RW-0.2,RH-0.14,fc,C['border'],
                lw=0.4,r=0.0,fa=0.2 if v else 0.15,ea=0.4,z=2)
            at(ax,rx+RW/2,ry-RH/2,sym,size=8.5,bold=True,color=sc,z=3)
        ry -= RH

    # legend
    box(ax,0.2,0.2,5.5,0.75,C['card'],C['border'],r=0.2,fa=1.0,ea=1.0,lw=1.0)
    at(ax,0.8,0.58,'YES',size=9,bold=True,color=C['green'],z=3)
    ar_text(ax,2.2,0.58,'يمتلك الصلاحية',8,color=C['text'])
    at(ax,3.3,0.58,' NO',size=9,bold=True,color=C['red'],z=3)
    ar_text(ax,4.5,0.58,'لا يمتلكها',8,color=C['text'])

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# D5 — API Endpoints
# ══════════════════════════════════════════════════════════════════════════════
def d5():
    fig, ax = fig_axes(20, 16)
    ax.set_xlim(0, 20); ax.set_ylim(0, 16)
    ar_text(ax, 10, 15.5, 'خريطة واجهات API — منصة ضيوف', 15, True, C['gold'])

    MC = {'GET':C['green'],'POST':C['employee'],'PATCH':C['manager'],'DELETE':C['red']}

    GROUPS = [
        dict(ar='المصادقة',    path='/auth',        col=C['accent'],
             x=0.3,  y=14.8, w=6.1, ep=[
            ('POST', '/auth/register',         'تسجيل مستخدم جديد'),
            ('POST', '/auth/login',             'تسجيل الدخول'),
            ('POST', '/auth/logout',            'تسجيل الخروج'),
            ('POST', '/auth/refresh-token',     'تجديد التوكن'),
            ('POST', '/auth/forgot-password',   'نسيت كلمة المرور'),
            ('POST', '/auth/reset-password',    'اعادة تعيين كلمة المرور'),
            ('POST', '/auth/verify-email',      'التحقق من البريد'),
            ('GET',  '/auth/me',                'بيانات المستخدم الحالي'),
        ]),
        dict(ar='المستخدمون', path='/users',       col=C['employee'],
             x=7.0,  y=14.8, w=6.1, ep=[
            ('GET',   '/users',                'قائمة المستخدمين'),
            ('GET',   '/users/:id',            'تفاصيل مستخدم'),
            ('POST',  '/users',                'انشاء مستخدم'),
            ('PATCH', '/users/:id',            'تعديل البيانات'),
            ('DELETE','/users/:id',            'حذف ناعم'),
            ('PATCH', '/users/:id/activate',   'تفعيل الحساب'),
            ('PATCH', '/users/:id/deactivate', 'تعطيل الحساب'),
        ]),
        dict(ar='الادوار',     path='/roles',       col=C['manager'],
             x=13.7, y=14.8, w=6.0, ep=[
            ('GET',   '/roles',     'قائمة الادوار'),
            ('GET',   '/roles/:id', 'تفاصيل دور'),
            ('POST',  '/roles',     'انشاء دور'),
            ('PATCH', '/roles/:id', 'تعديل دور'),
            ('DELETE','/roles/:id', 'حذف دور'),
        ]),
        dict(ar='الصلاحيات',   path='/permissions', col=C['pink'],
             x=0.3,  y=7.6,  w=6.5, ep=[
            ('GET',   '/permissions',                   'قائمة الصلاحيات'),
            ('POST',  '/roles/:id/permissions',         'ربط صلاحيات بدور'),
            ('DELETE','/roles/:id/permissions/:permId', 'ازالة صلاحية من دور'),
        ]),
        dict(ar='سجل التدقيق', path='/audit-logs',  col=C['red'],
             x=7.3,  y=7.6,  w=5.8, ep=[
            ('GET','/audit-logs',     'قائمة السجلات'),
            ('GET','/audit-logs/:id', 'تفاصيل سجل'),
        ]),
        dict(ar='الملف الشخصي',path='/profile',     col=C['teal'],
             x=13.7, y=7.6,  w=6.0, ep=[
            ('GET',  '/profile',           'عرض الملف الشخصي'),
            ('PATCH','/profile',           'تعديل الملف الشخصي'),
            ('PATCH','/profile/password',  'تغيير كلمة المرور'),
        ]),
    ]

    RH = 0.60
    for g in GROUPS:
        gx,gy,gw,gc = g['x'],g['y'],g['w'],g['col']
        n = len(g['ep'])
        gh = 0.58 + n*RH + 0.12
        solid_box(ax, gx, gy-0.55, gw, 0.55, gc, r=0.2, z=3)
        ar_text(ax, gx+1.5, gy-0.275, g['ar'], 9.5, True)
        at(ax, gx+gw-0.3, gy-0.275, g['path'], size=9, color=C['white'],
           ha='right', bold=True, z=4)
        box(ax, gx, gy-gh, gw, gh-0.55, C['card'], gc,
            lw=1.5, r=0.0, fa=1.0, ea=1.0)
        for i,(method,path,desc_ar) in enumerate(g['ep']):
            ey = gy - 0.62 - i*RH - RH/2
            mc = MC.get(method, C['muted'])
            box(ax, gx+0.12, ey-0.19, 1.15, 0.38, mc, mc,
                lw=1.0, r=0.12, fa=0.2, ea=1.0, z=3)
            at(ax, gx+0.695, ey, method, size=7.5, bold=True, color=mc, z=4)
            at(ax, gx+1.4, ey+0.1, path, size=7.5, color=C['text'], ha='left', z=3)
            ar_text(ax, gx+gw/2+1.0, ey-0.14, desc_ar, 7.5, color=C['muted'])

    # Guards
    GUARDS = [
        ('AuthGuard',        'التحقق من JWT',              C['accent']),
        ('RolesGuard',       'التحقق من الدور',             C['manager']),
        ('PermissionsGuard', 'التحقق من الصلاحية الفعلية', C['employee']),
        ('OwnershipGuard',   'التحقق من ملكية المورد',      C['teal']),
        ('ThrottlerGuard',   'تحديد معدل الطلبات',          C['gold']),
    ]
    ar_text(ax, 10, 2.8, 'طبقات الحماية المطبقة على كل طلب', 10, True, C['gold'])
    gsx = 0.5
    for gn, gd, gc in GUARDS:
        box(ax, gsx, 1.3, 3.6, 1.2, gc, gc, lw=1.3, r=0.2, fa=0.15, ea=1.0)
        at(ax, gsx+1.8, 2.0, gn, size=8.5, bold=True, color=gc, z=3)
        ar_text(ax, gsx+1.8, 1.7, gd, 7.5, color=C['muted'])
        if gsx < 17:
            arrow(ax, gsx+3.6, 1.9, gsx+3.85, 1.9, gc)
        gsx += 3.8

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# D6 — Frontend Structure
# ══════════════════════════════════════════════════════════════════════════════
def d6():
    fig, ax = fig_axes(20, 14)
    ax.set_xlim(0, 20); ax.set_ylim(0, 14)
    ar_text(ax, 10, 13.5, 'هيكل الواجهة الامامية — Next.js 14', 15, True, C['gold'])

    def grp(x, y, w, h, ar_lbl, color):
        box(ax, x, y, w, h, color, color, lw=1.5, r=0.4, fa=0.08, ea=0.9, z=1)
        solid_box(ax, x, y+h-0.55, w, 0.55, color, r=0.3, z=2)
        ar_text(ax, x+w/2, y+h-0.275, ar_lbl, 10, True, z=3)

    def pg(x, y, w, h, route, ar_lbl, color):
        box(ax, x, y, w, h, color, color, lw=1.5, r=0.2, fa=0.25, ea=1.0)
        ar_text(ax, x+w/2, y+h/2+0.13, ar_lbl, 8.5, True)
        at(ax,    x+w/2, y+h/2-0.14, route, size=7.5, color=color)

    grp(0.3,  7.5, 9.0, 5.5, 'صفحات المصادقة  (auth)',    C['accent'])
    pg(0.5,  10.7, 4.0, 1.1, '/login',           'تسجيل الدخول',               C['accent'])
    pg(5.0,  10.7, 4.0, 1.1, '/register',        'انشاء حساب',                 C['accent'])
    pg(0.5,   9.3, 4.0, 1.1, '/verify-email',    'التحقق من البريد',            C['teal'])
    pg(5.0,   9.3, 4.0, 1.1, '/forgot-password', 'نسيت كلمة المرور',           C['pink'])
    pg(0.5,   7.9, 4.0, 1.1, '/reset-password',  'اعادة تعيين كلمة المرور',    C['pink'])

    grp(10.0, 7.5, 9.7, 5.5, 'لوحة التحكم  (dashboard)',   C['manager'])
    pg(10.2, 10.7, 4.5, 1.1, '/',             'الرئيسية',            C['manager'])
    pg(15.0, 10.7, 4.5, 1.1, '/users',        'ادارة المستخدمين',    C['employee'])
    pg(10.2,  9.3, 4.5, 1.1, '/roles',        'ادارة الادوار',       C['manager'])
    pg(15.0,  9.3, 4.5, 1.1, '/permissions',  'ادارة الصلاحيات',     C['accent'])
    pg(10.2,  7.9, 4.5, 1.1, '/audit-logs',   'سجل العمليات',        C['red'])
    pg(15.0,  7.9, 4.5, 1.1, '/profile',      'الملف الشخصي',        C['teal'])

    grp(0.3,  4.8, 9.0, 2.4, 'صفحات الاخطاء',               C['red'])
    pg(0.5,   5.1, 4.0, 1.8, '401 Unauthorized', 'غير مصرح',      C['red'])
    pg(5.0,   5.1, 4.0, 1.8, '403 Forbidden',    'ممنوع الوصول',  C['red'])

    grp(10.0, 4.8, 9.7, 2.4, 'Middleware & Guards',          C['gold'])
    mw = [
        ('middleware.ts',    'حماية مسارات Next.js',  C['gold']),
        ('AuthGuard',        'JWT التحقق من التوكن',   C['accent']),
        ('PermissionsGuard', 'التحقق من الصلاحية',     C['employee']),
        ('i18n Middleware',  'اللغة + RTL / LTR',      C['teal']),
    ]
    for i,(mn,md,mc) in enumerate(mw):
        ix = 10.2 + (i%2)*4.9
        iy = 5.7  - (i//2)*0.85
        box(ax, ix, iy, 4.5, 0.75, mc, mc, lw=1.2, r=0.15, fa=0.2, ea=1.0)
        at(ax,  ix+2.25, iy+0.48, mn, size=8.5, bold=True, color=mc, z=3)
        ar_text(ax, ix+2.25, iy+0.22, md, 7.5, color=C['muted'])

    grp(0.3, 1.5, 19.4, 3.0, 'الطبقة المشتركة — Shared Layer', C['teal'])
    sh = [
        ('Zustand Store',   'ادارة حالة المصادقة',   C['accent']),
        ('API Client',      'Axios + Interceptors',  C['manager']),
        ('usePermission()', 'Permission Hook',       C['employee']),
        ('i18n ar / en',    'ترجمة الواجهة',          C['teal']),
        ('shadcn/ui',       'مكونات الواجهة',          C['pink']),
    ]
    sx = 0.6
    for sn, sd, sc in sh:
        box(ax, sx, 2.0, 3.6, 1.3, sc, sc, lw=1.3, r=0.2, fa=0.18, ea=1.0)
        at(ax,  sx+1.8, 2.72, sn, size=8.5, bold=True, color=sc, z=3)
        ar_text(ax, sx+1.8, 2.38, sd, 7.5, color=C['muted'])
        sx += 3.8

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# D7 — Security Layers
# ══════════════════════════════════════════════════════════════════════════════
def d7():
    fig, ax = fig_axes(18, 14)
    ax.set_xlim(0, 18); ax.set_ylim(0, 14)
    ar_text(ax, 9, 13.5, 'طبقات الامان — Security Architecture', 15, True, C['gold'])

    LAYERS = [
        (6.5, C['red'],      'HTTPS / TLS 1.3',    'النقل المشفر'),
        (5.3, C['manager'],  'CORS + Helmet',       'حماية ترويسات HTTP'),
        (4.2, C['accent'],   'Rate Limiting',       'تحديد معدل الطلبات'),
        (3.2, C['employee'], 'JWT AuthGuard',       'التحقق من الهوية'),
        (2.3, C['teal'],     'PermissionsGuard',    'التحقق من الصلاحية'),
        (1.5, C['green'],    'Input Validation',    'التحقق من المدخلات'),
        (0.8, C['gold'],     'Business Logic',      'منطق الاعمال'),
    ]
    cx, cy = 7.0, 6.5
    for r, ec, en, ar_lbl in LAYERS:
        circ = plt.Circle((cx,cy), r, facecolor=_rgba(ec, 0.12),
                          edgecolor=ec, linewidth=2.0, zorder=2)
        ax.add_patch(circ)
        angle = np.pi * 0.22
        tx = cx + r*np.cos(angle)*0.72
        ty = cy + r*np.sin(angle)*0.9
        at(ax,  tx, ty+0.18, en, size=7.5, bold=True, color=ec, z=5)
        ar_text(ax, tx, ty-0.08, ar_lbl, 7.5, color=C['muted'], z=5)

    core = plt.Circle((cx,cy), 0.6, facecolor=C['gold'],
                      edgecolor=C['white'], linewidth=2, zorder=6)
    ax.add_patch(core)
    at(ax, cx, cy, 'DB', size=9, bold=True, color=C['bg'], z=7)

    ar_text(ax, 14.5, 13.0, 'قائمة المراجعة الامنية', 11, True, C['gold'])
    CHECKS = [
        'تشفير كلمات المرور bcrypt (rounds=12)',
        'JWT Access (15 دقيقة) + Refresh (7 ايام)',
        'HttpOnly + Secure + SameSite=Strict Cookies',
        'Rate Limiting: 5 محاولات / 15 دقيقة',
        'قفل الحساب بعد 5 محاولات فاشلة',
        'رسالة خطا موحدة عند فشل الدخول',
        'Prisma Parameterized Queries',
        'Input Validation بـ class-validator',
        'XSS Protection + Sanitization',
        'CSRF Protection — SameSite Strict',
        'Soft Delete — لا حذف نهائي للمستخدمين',
        'Audit Log لكل عملية حساسة',
        'CORS Whitelist — لا * في الانتاج',
        'اسرار النظام في ملف .env فقط',
        'منع المستخدم من رفع صلاحياته بنفسه',
        'Refresh Token Rotation',
    ]
    for i, chk in enumerate(CHECKS):
        iy = 12.4 - i*0.74
        at(ax, 10.4, iy, '[OK]', size=8, bold=True, color=C['green'], ha='left', z=3)
        ar_text(ax, 11.2, iy, chk, 8.0, color=C['text'], ha='left', z=3)

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# D8 — Subscription Flow
# ══════════════════════════════════════════════════════════════════════════════
def d8():
    fig, ax = fig_axes(18, 11)
    ax.set_xlim(0, 18); ax.set_ylim(0, 11)
    ar_text(ax, 9, 10.5, 'نظام الاشتراكات والتجربة المجانية', 15, True, C['gold'])

    def bx(x, y, w, h, ar_lbl, en_lbl, color):
        box(ax, x, y, w, h, color, color, lw=2.0, r=0.25, fa=0.22, ea=1.0)
        ar_text(ax, x+w/2, y+h/2+(0.14 if en_lbl else 0), ar_lbl, 9.5, True)
        if en_lbl:
            at(ax, x+w/2, y+h/2-0.2, en_lbl, size=8, color=color)

    def arr2(x1,y1,x2,y2, ar_lbl='', color=C['muted']):
        arrow(ax, x1, y1, x2, y2, color)
        if ar_lbl:
            ar_text(ax,(x1+x2)/2+0.15,(y1+y2)/2+0.12, ar_lbl, 7.5, color=color)

    # subscription types
    for i,(ar_lbl,en_lbl,col) in enumerate([
        ('تجربة مجانية','60 يوم',C['teal']),
        ('Basic','شهري / سنوي',C['employee']),
        ('Pro','شهري / سنوي',C['accent']),
        ('Enterprise','مخصص',C['gold']),
    ]):
        bx(0.4+i*4.4, 8.5, 3.9, 1.5, ar_lbl, en_lbl, col)

    # state machine
    ar_text(ax, 9, 7.9, 'دورة حياة الحساب', 10, True, C['gold'])
    for i,(ar_lbl,col) in enumerate([
        ('مسجل — غير مفعل',   C['muted']),
        ('تجربة مجانية نشطة', C['teal']),
        ('مشترك نشط',          C['green']),
        ('منتهي الاشتراك',     C['red']),
    ]):
        bx(0.4+i*4.4, 6.2, 3.9, 1.3, ar_lbl, '', col)

    arr2(4.3, 6.85, 4.8, 6.85, 'تفعيل البريد', C['teal'])
    arr2(8.7, 6.85, 9.2, 6.85, 'دفع / ترقية',  C['green'])
    arr2(13.1,6.85,13.6, 6.85, 'انتهاء',       C['red'])
    ax.annotate('', xy=(9.2,7.5), xytext=(13.5,7.5),
                arrowprops=dict(arrowstyle='->',color=C['green'],lw=1.8), zorder=2)
    ar_text(ax, 11.4, 7.7, 'تجديد', 8, color=C['green'])

    # permission check strip
    box(ax, 0.3,2.8,17.4,2.5,C['card'],C['teal'],lw=2.0,r=0.3,fa=1.0,ea=1.0)
    ar_text(ax, 9, 4.9, 'منطق التحقق من الاشتراك — يُطبَّق على كل طلب محمي',
            9.5, True, C['teal'])
    steps = [
        'هل الحساب مفعل؟',
        'هل الاشتراك ساري او التجربة لم تنتهِ؟',
        'احسب الايام = trial_ends_at - الآن',
        'اذا انتهى: 402 Payment Required',
        'عرض عداد الايام في لوحة التحكم',
    ]
    sx = 0.6
    for i, s in enumerate(steps):
        box(ax, sx, 3.1, 3.3, 1.3, C['accent'], C['accent'],
            lw=1.0, r=0.2, fa=0.15, ea=1.0)
        at(ax, sx+1.65, 3.85, f'{i+1}.', size=9, bold=True, color=C['accent'], z=3)
        ar_text(ax, sx+1.65, 3.52, s, 7.5, color=C['text'])
        sx += 3.45

    # trial countdown
    box(ax, 0.3,0.4,17.4,1.9,C['surface'],C['gold'],lw=2.0,r=0.3,fa=1.0,ea=1.0)
    ar_text(ax, 9, 1.85, 'مثال: عداد التجربة المجانية — 60 يوم', 9, True, C['gold'])
    for i in range(6):
        d = 60 - i*12
        rc = C['green'] if d/60 > 0.5 else (C['gold'] if d/60 > 0.25 else C['red'])
        bx2 = 0.6 + i*2.9
        box(ax, bx2, 0.55, 2.6, 0.9, rc, rc, lw=1.2, r=0.15, fa=0.2, ea=1.0)
        at(ax, bx2+1.3, 1.0, str(d), size=11, bold=True, color=rc, z=3)
        ar_text(ax, bx2+1.3, 0.72, 'يوم متبقي', 7.5, color=C['muted'])

    return to_png(fig)


# ══════════════════════════════════════════════════════════════════════════════
# BUILD PDF
# ══════════════════════════════════════════════════════════════════════════════
def build_pdf(out_path):
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title='منصة ضيوف — المخططات الهندسية',
        author='منصة ضيوف',
    )
    BG = rl_colors.HexColor('#0F1117')

    def sty(name, size, bold=False, col='#F1F5F9', align=TA_CENTER):
        return ParagraphStyle(
            name, fontName='ArB' if bold else 'Ar',
            fontSize=size, textColor=rl_colors.HexColor(col),
            alignment=align, leading=size*1.5, backColor=BG,
        )

    TIT  = sty('T', 22, True, '#F59E0B')
    H1   = sty('H1',14, True, '#6366F1')
    H2   = sty('H2',10, False,'#94A3B8')
    BODY = sty('B',  9, False,'#CBD5E1', TA_RIGHT)

    story = []

    def section(ar_lbl):
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(rl(ar_lbl), H1))
        story.append(HRFlowable(width='100%', thickness=1.5,
                                color=rl_colors.HexColor('#6366F1'), spaceAfter=4))
        story.append(Spacer(1, 0.2*cm))

    def add_img(buf, w_cm=17, h_ratio=0.67, cap=''):
        story.append(Image(buf, width=w_cm*cm, height=w_cm*cm*h_ratio))
        if cap:
            story.append(Paragraph(rl(cap), H2))
        story.append(Spacer(1, 0.4*cm))

    # Cover
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(rl('منصة ضيوف'), TIT))
    story.append(Paragraph(rl('المخططات الهندسية الاحترافية'), H1))
    story.append(Paragraph(rl('نظام تسجيل الدخول وادارة الصلاحيات متعددة الادوار'), H2))
    story.append(HRFlowable(width='100%',thickness=2,
                            color=rl_colors.HexColor('#F59E0B'),spaceAfter=8))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(rl(
        'يحتوي هذا الملف على ثمانية مخططات هندسية شاملة تغطي جميع جوانب النظام: '
        'معمارية البنية التحتية، قاعدة البيانات، تدفقات المصادقة، '
        'مصفوفة الصلاحيات، خريطة API، هيكل الواجهة الامامية، '
        'طبقات الامان، ونظام الاشتراكات.'), BODY))
    story.append(Spacer(1, 0.5*cm))

    INFO = [
        [rl('TypeScript'),                               rl('لغة البرمجة')],
        [rl('NestJS + Prisma ORM'),                      rl('Backend')],
        [rl('Next.js 14  (App Router)'),                 rl('Frontend')],
        [rl('PostgreSQL 16'),                            rl('قاعدة البيانات')],
        [rl('JWT — Access 15 دقيقة + Refresh 7 ايام'),  rl('المصادقة')],
        [rl('RTL (عربية)  /  LTR (انجليزية)'),           rl('اتجاه الواجهة')],
        [rl('Admin / Manager / Employee / User'),        rl('الادوار')],
        [rl('24 صلاحية قابلة للادارة من قاعدة البيانات'), rl('الصلاحيات')],
    ]
    tbl = Table(INFO, colWidths=[11*cm, 6*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), rl_colors.HexColor('#1A1D27')),
        ('TEXTCOLOR',     (0,0),(-1,-1), rl_colors.HexColor('#F1F5F9')),
        ('FONTNAME',      (0,0),(-1,-1), 'Ar'),
        ('FONTSIZE',      (0,0),(-1,-1), 9),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),
         [rl_colors.HexColor('#1A1D27'), rl_colors.HexColor('#22263A')]),
        ('GRID',          (0,0),(-1,-1), 0.5, rl_colors.HexColor('#2E3452')),
        ('ALIGN',         (0,0),(0,-1),'LEFT'),
        ('ALIGN',         (1,0),(1,-1),'RIGHT'),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
        ('RIGHTPADDING',  (0,0),(-1,-1), 10),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 1.0*cm))

    DIAGRAMS = [
        ('1. معمارية النظام الكاملة', d1, 17, 0.62,
         'طبقات Client / API Gateway / Data مع جميع المكونات والخدمات'),
        ('2. مخطط قاعدة البيانات  (ERD)', d2, 17, 0.70,
         '10 جداول رئيسية مع جميع العلاقات والمفاتيح الاساسية والخارجية'),
        ('3. تدفق المصادقة', d3, 15, 0.95,
         'تسجيل الدخول / انشاء حساب / تجديد التوكن / استعادة كلمة المرور'),
        ('4. مصفوفة الادوار والصلاحيات', d4, 17, 0.75,
         'صلاحيات كل دور — قابلة للتعديل الكامل من لوحة التحكم'),
        ('5. خريطة واجهات API', d5, 17, 0.72,
         'جميع نقاط النهاية مع طريقة الطلب والصلاحية المطلوبة وطبقات الحماية'),
        ('6. هيكل الواجهة الامامية', d6, 17, 0.62,
         'صفحات Next.js 14 — المصادقة / لوحة التحكم / الاخطاء / الطبقة المشتركة'),
        ('7. طبقات الامان', d7, 16, 0.70,
         'الطبقات الامنية المتداخلة وقائمة المراجعة الامنية (16 نقطة)'),
        ('8. نظام الاشتراكات والتجربة المجانية', d8, 17, 0.55,
         'دورة حياة الحساب — Trial 60 يوم + انواع الاشتراكات + منطق التحقق'),
    ]

    for i,(title, fn, w, hr, cap) in enumerate(DIAGRAMS, 1):
        print(f'  [{i}/8] {title}')
        section(title)
        add_img(fn(), w, hr, cap)

    print('  Building PDF ...')
    doc.build(story)
    print(f'  Done -> {out_path}')


if __name__ == '__main__':
    OUT = ('/home/user/https-github.com-anthropics-skills-commit-'
           '690f15cac7f7b4c055c5ab109c79ed9259934081/'
           'duyuf-platform-diagrams.pdf')
    build_pdf(OUT)
