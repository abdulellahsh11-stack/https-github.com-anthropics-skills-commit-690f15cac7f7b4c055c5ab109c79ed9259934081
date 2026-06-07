import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

const bookingTime  = new Trend('booking_time');
const searchTime   = new Trend('search_time');
const loginTime    = new Trend('login_time');
const errorRate    = new Rate('error_rate');
const bookingCount = new Counter('booking_success');

const BASE_URL = __ENV.BASE_URL || 'https://www.dheuof.com';

export const options = {
  stages: [
    { duration: '2m', target: 10  },  // إحماء تدريجي
    { duration: '5m', target: 50  },  // حمل عادي
    { duration: '3m', target: 100 },  // ذروة
    { duration: '2m', target: 0   },  // تهدئة
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000', 'p(99)<5000'],
    http_req_failed:   ['rate<0.05'],
    booking_time:      ['p(95)<3000'],
    search_time:       ['p(95)<1500'],
    login_time:        ['p(95)<1000'],
  },
};

export default function () {
  const headers = { 'Content-Type': 'application/json' };
  let token = '';

  // ─── 1. تسجيل الدخول ───────────────────────────────────────────────
  group('تسجيل الدخول', () => {
    const t0  = Date.now();
    const res = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({ email: 'test@guest.com', password: 'Test@1234' }),
      { headers }
    );
    loginTime.add(Date.now() - t0);

    const ok = check(res, {
      'رمز الاستجابة 200':  (r) => r.status === 200,
      'التوكن موجود':        (r) => !!r.json('token'),
    });
    errorRate.add(!ok);

    if (ok) token = res.json('token');
    sleep(1);
  });

  const authHeaders = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };

  // ─── 2. الصفحة الرئيسية ────────────────────────────────────────────
  group('الصفحة الرئيسية', () => {
    const res = http.get(`${BASE_URL}/`);
    check(res, {
      'الصفحة الرئيسية تعمل': (r) => r.status === 200,
      'وقت التحميل مقبول':    (r) => r.timings.duration < 3000,
    });
    sleep(1);
  });

  // ─── 3. البحث عن الغرف ─────────────────────────────────────────────
  group('البحث عن الغرف', () => {
    const t0  = Date.now();
    const res = http.get(
      `${BASE_URL}/api/rooms?checkin=2026-07-01&checkout=2026-07-05&guests=2`,
      { headers: authHeaders }
    );
    searchTime.add(Date.now() - t0);

    const ok = check(res, {
      'نتائج البحث 200':    (r) => r.status === 200,
      'توجد غرف متاحة':     (r) => (r.json('results') || []).length > 0,
    });
    errorRate.add(!ok);
    sleep(2);
  });

  // ─── 4. تفاصيل الغرفة ──────────────────────────────────────────────
  group('تفاصيل الغرفة', () => {
    const res = http.get(`${BASE_URL}/api/rooms/101`, { headers: authHeaders });
    check(res, {
      'تفاصيل الغرفة 200':   (r) => r.status === 200,
      'السعر موجود':          (r) => r.json('price') !== undefined,
      'الصور موجودة':         (r) => (r.json('images') || []).length > 0,
    });
    sleep(1);
  });

  // ─── 5. إنشاء الحجز ────────────────────────────────────────────────
  group('إنشاء الحجز', () => {
    const t0  = Date.now();
    const res = http.post(
      `${BASE_URL}/api/bookings`,
      JSON.stringify({
        room_id:  '101',
        checkin:  '2026-07-01',
        checkout: '2026-07-05',
        guests:   2,
        name:     'ضيف تجريبي',
        email:    'test@guest.com',
      }),
      { headers: authHeaders }
    );
    bookingTime.add(Date.now() - t0);

    const ok = check(res, {
      'الحجز نجح 201':        (r) => r.status === 201,
      'رقم الحجز موجود':      (r) => !!r.json('booking_id'),
      'رسالة التأكيد موجودة': (r) => !!r.json('confirmation'),
    });
    if (ok) bookingCount.add(1);
    errorRate.add(!ok);
    sleep(3);
  });

  // ─── 6. سجل حجوزات المستخدم ────────────────────────────────────────
  group('سجل الحجوزات', () => {
    const res = http.get(`${BASE_URL}/api/bookings/my`, { headers: authHeaders });
    check(res, {
      'سجل الحجوزات 200': (r) => r.status === 200,
    });
    sleep(1);
  });

  // ─── 7. تسجيل الخروج ───────────────────────────────────────────────
  group('تسجيل الخروج', () => {
    const res = http.post(`${BASE_URL}/api/auth/logout`, null, { headers: authHeaders });
    check(res, {
      'تسجيل الخروج نجح': (r) => r.status === 200 || r.status === 204,
    });
    sleep(1);
  });
}
