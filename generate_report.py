#!/usr/bin/env python3
"""
يقرأ ملف summary.json الناتج عن k6 ويولّد تقرير PDF عربي RTL.
الاستخدام:
  python generate_report.py [summary.json] [تقرير_الأداء.pdf]
"""

import json
import sys
import os
from datetime import datetime
from jinja2 import Template

# ─── قراءة النتائج ────────────────────────────────────────────────────────────

def load_results(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ─── استخراج الفحوصات من الشجرة التكرارية ────────────────────────────────────

def extract_checks(group, checks=None):
    if checks is None:
        checks = []
    for c in group.get('checks', []):
        passes = c.get('passes', 0)
        fails  = c.get('fails',  0)
        total  = passes + fails
        checks.append({
            'name':   c.get('name', '—'),
            'passes': passes,
            'fails':  fails,
            'rate':   round(passes / total * 100, 1) if total else 0,
        })
    for g in group.get('groups', []):
        extract_checks(g, checks)
    return checks

# ─── توليد التوصيات ──────────────────────────────────────────────────────────

def recommendations(p95, p99, err_rate, rps):
    recs = []
    if p95 <= 1000:
        recs.append("✅ وقت الاستجابة P95 ممتاز (أقل من ثانية) — الخوادم تعمل بكفاءة عالية.")
    elif p95 <= 2000:
        recs.append("🟡 وقت الاستجابة P95 مقبول — راجع استعلامات قاعدة البيانات البطيئة.")
    else:
        recs.append("🔴 وقت الاستجابة P95 مرتفع — فعّل الـ Caching وراجع أداء الخادم فوراً.")

    if p99 > 5000:
        recs.append("⚠️ P99 يتجاوز 5 ثوانٍ — قد يعاني بعض المستخدمين من تجربة سيئة في أوقات الذروة.")

    if err_rate <= 1:
        recs.append("✅ معدل الأخطاء ضمن الحدود المثالية (< 1%).")
    elif err_rate <= 5:
        recs.append("🟡 معدل الأخطاء مرتفع قليلاً — راجع سجلات الخادم ومعالجة الاستثناءات.")
    else:
        recs.append("🔴 معدل الأخطاء مرتفع جداً — المنصة غير مستقرة تحت الحمل الحالي.")

    if rps >= 50:
        recs.append("✅ الإنتاجية جيدة — المنصة تستطيع تحمّل حجم طلبات مناسب.")
    else:
        recs.append("⚠️ الإنتاجية منخفضة — النظر في التوسع الأفقي (Horizontal Scaling).")

    recs.append("📈 يُنصح بتكرار الاختبار بعد كل نشر (Deployment) جديد.")
    recs.append("🔍 فعّل المراقبة المستمرة عبر Grafana Dashboards في بيئة الإنتاج.")
    recs.append("📦 استخدم CDN لتحسين سرعة تحميل الأصول الثابتة (الصور، CSS، JS).")
    return recs

# ─── قالب HTML عربي RTL ──────────────────────────────────────────────────────

TEMPLATE = """\
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    font-family: 'Tajawal', 'Arial Unicode MS', 'Tahoma', sans-serif;
    direction: rtl;
    background: #f4f6f9;
    color: #2c3e50;
    font-size: 14px;
    line-height: 1.7;
  }

  /* ── غلاف ── */
  .cover {
    background: linear-gradient(135deg, #1a2f50 0%, #2471a3 100%);
    color: white;
    padding: 55px 50px 45px;
    text-align: center;
  }
  .cover .logo { font-size: 48px; margin-bottom: 12px; }
  .cover h1   { font-size: 34px; font-weight: 800; margin-bottom: 8px; }
  .cover .sub { font-size: 18px; opacity: .88; }
  .cover .meta {
    margin-top: 24px;
    display: flex;
    justify-content: center;
    gap: 40px;
    font-size: 13px;
    opacity: .72;
  }

  /* ── حاوية ── */
  .wrap { max-width: 920px; margin: 0 auto; padding: 28px 20px 40px; }

  /* ── بطاقة الحكم الكلي ── */
  .verdict {
    border-radius: 10px;
    padding: 22px 28px;
    text-align: center;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 24px;
    border: 3px solid;
  }
  .verdict.pass { background:#d4edda; border-color:#28a745; color:#155724; }
  .verdict.fail { background:#f8d7da; border-color:#dc3545; color:#721c24; }

  /* ── بطاقة عامة ── */
  .card {
    background: white;
    border-radius: 10px;
    padding: 26px;
    margin-bottom: 22px;
    box-shadow: 0 2px 10px rgba(0,0,0,.07);
  }
  .card h2 {
    font-size: 19px;
    font-weight: 700;
    color: #1a2f50;
    border-bottom: 3px solid #2471a3;
    padding-bottom: 10px;
    margin-bottom: 20px;
  }

  /* ── شبكة الأرقام ── */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }
  .kpi {
    background: #eaf2fb;
    border-radius: 8px;
    padding: 18px 12px;
    text-align: center;
  }
  .kpi .lbl { font-size: 12px; color: #666; margin-bottom: 8px; }
  .kpi .val { font-size: 28px; font-weight: 800; color: #1a2f50; }
  .kpi .unt { font-size: 11px; color: #999; margin-top: 4px; }

  /* ── جداول ── */
  table { width:100%; border-collapse:collapse; }
  th {
    background: #1a2f50;
    color: white;
    padding: 11px 14px;
    text-align: right;
    font-size: 13px;
  }
  td {
    padding: 10px 14px;
    border-bottom: 1px solid #edf0f3;
    font-size: 13px;
    text-align: right;
  }
  tr:nth-child(even) td { background: #f8fafc; }
  .pass { color:#27ae60; font-weight:700; }
  .fail { color:#e74c3c; font-weight:700; }
  .warn { color:#f39c12; font-weight:700; }

  /* ── توصيات ── */
  .recs li {
    padding: 8px 0;
    border-bottom: 1px dashed #e0e0e0;
    font-size: 13.5px;
  }
  .recs li:last-child { border-bottom: none; }

  /* ── تذييل ── */
  .footer {
    text-align: center;
    color: #aaa;
    font-size: 11.5px;
    padding: 20px;
  }

  @media print {
    body { background: white; }
    .wrap { padding: 0; }
  }
</style>
</head>
<body>

<!-- ═══ غلاف ═══════════════════════════════════════════════════════ -->
<div class="cover">
  <div class="logo">🏨</div>
  <h1>تقرير اختبار الأداء</h1>
  <div class="sub">منصة الضيوف — تقييم شامل للأداء والاستجابة تحت الضغط</div>
  <div class="meta">
    <span>📅 {{ date }}</span>
    <span>⏱️ مدة الاختبار: {{ duration }}</span>
    <span>👥 أقصى مستخدمين افتراضيين: {{ max_vus }}</span>
  </div>
</div>

<div class="wrap">

  <!-- ═══ الحكم الكلي ══════════════════════════════════════════════ -->
  <div class="verdict {{ 'pass' if overall_pass else 'fail' }}">
    {% if overall_pass %}
      ✅ الاختبار نجح — المنصة مستقرة وجاهزة للإنتاج
    {% else %}
      ❌ الاختبار فشل — يلزم معالجة مشكلات الأداء قبل الإطلاق
    {% endif %}
  </div>

  <!-- ═══ ملخص سريع ════════════════════════════════════════════════ -->
  <div class="card">
    <h2>📊 ملخص سريع</h2>
    <div class="kpi-grid">
      <div class="kpi">
        <div class="lbl">إجمالي الطلبات</div>
        <div class="val">{{ total_reqs }}</div>
        <div class="unt">طلب HTTP</div>
      </div>
      <div class="kpi">
        <div class="lbl">معدل الأخطاء</div>
        <div class="val">{{ err_pct }}%</div>
        <div class="unt">من إجمالي الطلبات</div>
      </div>
      <div class="kpi">
        <div class="lbl">الإنتاجية</div>
        <div class="val">{{ rps }}</div>
        <div class="unt">طلب / ثانية</div>
      </div>
      <div class="kpi">
        <div class="lbl">متوسط وقت الاستجابة</div>
        <div class="val">{{ avg_ms }}</div>
        <div class="unt">مللي ثانية</div>
      </div>
      <div class="kpi">
        <div class="lbl">P95 وقت الاستجابة</div>
        <div class="val">{{ p95_ms }}</div>
        <div class="unt">مللي ثانية</div>
      </div>
      <div class="kpi">
        <div class="lbl">P99 وقت الاستجابة</div>
        <div class="val">{{ p99_ms }}</div>
        <div class="unt">مللي ثانية</div>
      </div>
    </div>
  </div>

  <!-- ═══ مقاييس الأداء التفصيلية ══════════════════════════════════ -->
  <div class="card">
    <h2>⚡ مقاييس وقت الاستجابة</h2>
    <table>
      <tr>
        <th>المقياس</th>
        <th>القيمة الفعلية</th>
        <th>الحد المقبول</th>
        <th>الحالة</th>
      </tr>
      {% for r in metrics_rows %}
      <tr>
        <td>{{ r.name }}</td>
        <td>{{ r.value }}</td>
        <td>{{ r.limit }}</td>
        <td class="{{ r.css }}">{{ r.status }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <!-- ═══ نتائج الفحوصات ════════════════════════════════════════════ -->
  <div class="card">
    <h2>✔️ نتائج الفحوصات التفصيلية</h2>
    <table>
      <tr>
        <th>اسم الفحص</th>
        <th>ناجح</th>
        <th>فاشل</th>
        <th>نسبة النجاح</th>
      </tr>
      {% for c in checks %}
      <tr>
        <td>{{ c.name }}</td>
        <td class="pass">{{ c.passes }}</td>
        <td class="{{ 'fail' if c.fails > 0 else 'pass' }}">{{ c.fails }}</td>
        <td class="{{ 'pass' if c.rate >= 99 else ('warn' if c.rate >= 90 else 'fail') }}">
          {{ c.rate }}%
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <!-- ═══ التوصيات ══════════════════════════════════════════════════ -->
  <div class="card">
    <h2>💡 التوصيات والخطوات التالية</h2>
    <ul class="recs" style="list-style:none; padding:0;">
      {% for rec in recs %}
      <li>{{ rec }}</li>
      {% endfor %}
    </ul>
  </div>

</div><!-- /wrap -->

<div class="footer">
  تم إنشاء هذا التقرير تلقائياً بواسطة منظومة اختبار الأداء &mdash; {{ date }}
</div>

</body>
</html>
"""

# ─── الدالة الرئيسية ─────────────────────────────────────────────────────────

def generate(results_path: str, output_path: str = 'تقرير_الأداء.pdf'):
    data    = load_results(results_path)
    metrics = data.get('metrics', {})

    dur   = metrics.get('http_req_duration', {}).get('values', {})
    reqs  = metrics.get('http_reqs',         {}).get('values', {})
    fail  = metrics.get('http_req_failed',   {}).get('values', {})
    vus   = metrics.get('vus_max',           {}).get('values', {})
    iters = metrics.get('iteration_duration',{}).get('values', {})

    total_reqs = int(reqs.get('count', 0))
    err_rate   = fail.get('rate', 0) * 100
    rps        = round(reqs.get('rate', 0), 2)
    avg_ms     = round(dur.get('avg',  0))
    p95_ms     = round(dur.get('p(95)', 0))
    p99_ms     = round(dur.get('p(99)', 0))
    min_ms     = round(dur.get('min',   0))
    max_ms     = round(dur.get('max',   0))
    med_ms     = round(dur.get('med',   0))
    max_vus    = int(vus.get('max', 0))

    duration_s = round(iters.get('count', 0) * avg_ms / 1000) if avg_ms else 0
    duration_str = f"{duration_s // 60} د {duration_s % 60} ث" if duration_s else "—"

    overall_pass = p95_ms <= 2000 and err_rate <= 5

    def row(name, val_str, limit_str, pass_bool):
        return {
            'name':   name,
            'value':  val_str,
            'limit':  limit_str,
            'status': '✅ ناجح' if pass_bool else '❌ فشل',
            'css':    'pass'    if pass_bool else 'fail',
        }

    metrics_rows = [
        row('أدنى وقت استجابة',    f'{min_ms} ms', '—',          True),
        row('متوسط وقت الاستجابة', f'{avg_ms} ms', '< 1000 ms',  avg_ms <= 1000),
        row('الوسيط (P50)',         f'{med_ms} ms', '< 800 ms',   med_ms <= 800),
        row('P95 وقت الاستجابة',   f'{p95_ms} ms', '< 2000 ms',  p95_ms <= 2000),
        row('P99 وقت الاستجابة',   f'{p99_ms} ms', '< 5000 ms',  p99_ms <= 5000),
        row('أقصى وقت استجابة',    f'{max_ms} ms', '—',          True),
        row('معدل الأخطاء',        f'{err_rate:.2f}%', '< 5%',   err_rate <= 5),
        row('الإنتاجية (RPS)',      f'{rps} req/s',    '> 10 req/s', rps >= 10),
    ]

    checks = extract_checks(data.get('root_group', {}))
    if not checks:
        checks = [{'name': 'لا توجد فحوصات مسجلة', 'passes': 0, 'fails': 0, 'rate': 0}]

    recs = recommendations(p95_ms, p99_ms, err_rate, rps)

    html = Template(TEMPLATE).render(
        date         = datetime.now().strftime('%Y/%m/%d  %H:%M'),
        duration     = duration_str,
        max_vus      = max_vus,
        total_reqs   = total_reqs,
        err_pct      = f'{err_rate:.2f}',
        rps          = rps,
        avg_ms       = avg_ms,
        p95_ms       = p95_ms,
        p99_ms       = p99_ms,
        overall_pass = overall_pass,
        metrics_rows = metrics_rows,
        checks       = checks,
        recs         = recs,
    )

    # ── محاولة إنشاء PDF ──────────────────────────────────────────────
    try:
        import weasyprint
        weasyprint.HTML(string=html).write_pdf(output_path)
        print(f'\n✅ تم إنشاء التقرير: {output_path}')
    except ImportError:
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'\n⚠️  weasyprint غير مثبّت — تم حفظ HTML بدلاً من PDF: {html_path}')
        print('    لتثبيت weasyprint:  pip install weasyprint')
        print('    ثم شغّل الأمر مجدداً لتوليد PDF.')

# ─── نقطة الدخول ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'summary.json'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'تقرير_الأداء.pdf'

    if not os.path.exists(src):
        print(f'❌ الملف غير موجود: {src}')
        print('   شغّل أولاً: k6 run --summary-export=summary.json k6-test.js')
        sys.exit(1)

    generate(src, dst)
