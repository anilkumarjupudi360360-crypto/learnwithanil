/**
 * Learn with Anil — passes and payments (Google Apps Script; its data lives in the private "Learn with Anil – Passes" spreadsheet).
 *
 * Passes
 *  - PYQ Pass (₹45): EVERYTHING on the website for 12 months from the day of payment (Anil, 26 Oct 2026: "one ₹45 =
 *    everything"): every previous paper of every exam (including exams added later), every mock test series
 *    (Mission Khaki SI and Constable, Mission CGL, Bahubali, and later series) and the study books. Stored with exam = 'all'.
 *  - Free trial: the same access as the PYQ Pass for 3 days, once per phone number, starting the first time a registered
 *    student's phone and email reach this script (right after they register on the site). Stored in the 'trials' tab.
 *  - Mock packs are no longer sold on their own (they were ₹150 / ₹99 / ₹149, combo ₹199, until 26 Oct 2026; nobody bought
 *    one). Old 'mock' rows in the passes tab still work; a 'buy' for a mock or combo now opens the ₹45 PYQ Pass checkout.
 *  - Free mocks (FREE_MOCKS): open to every registered student, no pass needed; each opening is logged in the 'free' tab.
 *
 * What it does
 *  - buy:     creates an Instamojo payment request for a pass (price fixed here, never taken from the browser)
 *             and returns Instamojo's checkout link; or, when Cashfree is switched on, a Cashfree order and its payment
 *             session, which the website opens with Cashfree's checkout script.
 *  - verify:  after Instamojo or Cashfree sends the student back to learnwithanil.in, asks that gateway whether the payment
 *             request or order was paid and, if so, records the pass.
 *  - webhook: Instamojo (form-encoded, signed with the private salt) and Cashfree (JSON, checked by asking Cashfree) also
 *             call this script when a payment succeeds, so a pass is recorded even if the student closes the page.
 *  - passes:  which passes (and free trial) a registered phone number has; starts the free trial the first time.
 *  - mock:    the key of a released mock (its encrypted file is on the website), for a valid PYQ Pass or mock pass (or a free
 *             mock). Also 'bk-<book id>' (key of an encrypted study book) and 'bb-code' (the Bahubali access code) for any
 *             exam, PYQ Pass only. These keys live in the 'keys' tab like the mock keys.
 *  - ref:     a registered student's personal invite code (made the first time) and how many friends joined / bought.
 *  - refjoin: a new student registered through a friend's link (?ref=<code>): records it and gives the friend free days.
 *             See "invite friends, earn free days" below.
 *  - glogin:  log in with Google (a 12-month session on that device; see "student accounts").
 *
 * Settings are NOT in this file. They live under Project Settings → Script properties:
 *   SHEET_ID                                       the ID of the "Learn with Anil – Passes" spreadsheet (the only sheet this script opens)
 *   INSTAMOJO_CLIENT_ID, INSTAMOJO_CLIENT_SECRET   (Instamojo dashboard → API & Plugins; "API v2")
 *   INSTAMOJO_SALT                                 (Instamojo private salt, used to check webhooks)
 *   INSTAMOJO_API (optional)                       defaults to https://api.instamojo.com
 *   PAY_GATEWAY                                    'cashfree' sends every new checkout to Cashfree; anything else (or not set) keeps Instamojo
 *   CASHFREE_APP_ID, CASHFREE_SECRET               (Cashfree dashboard → Developers → API Keys; the production keys)
 *   CASHFREE_ENV (optional)                        'sandbox' to try Cashfree with its test keys; defaults to production
 *
 * Cashfree (Anil, 4 Nov 2026): Instamojo's free plan takes 5% + ₹3 (+ GST) of every ₹45 pass, about ₹6.20. New checkouts move to
 * Cashfree once PAY_GATEWAY = cashfree and its two keys are set. Payments already made on Instamojo keep working (verify, webhook
 * and "Link my payment" with a MOJO id); Cashfree orders have ids like LWA261104K7Q2ZX (LWA + date + 6 characters), which is also
 * the "Order ID" on the student's Cashfree receipt.
 */

const SITE = 'https://learnwithanil.in/';
const PYQ = {price: 45, months: 12, purpose: 'PYQ Pass - All Exams (1 yr)'};   // Instamojo allows 30 characters
const TRIAL_DAYS = 0;   // free trial switched off (Anil, 23 Oct 2026: every PYQ needs the paid pass). Was 3.
const MOCKS = {   // exam id: that exam's mock series (old price and checkout name, last day an old mock pass is valid or months
                  // from payment, and the prefix every mock id of that pack starts with). Since 26 Oct 2026 the ₹45 PYQ Pass opens
                  // every pack; add a new series here (e.g. 'upsc-epfo') when its Mock 1 is ready.
  'ts-police-si': {price: 150, name: 'Mission Khaki TS SI Mocks', until: '2026-11-30', prefix: 'mk-si-'},
  'ssc-cgl': {price: 149, name: 'Mission CGL SSC Mocks', months: 12, prefix: 'mk-cgl-'},   // Anil, 24 Oct 2026: ₹149
  'ts-police-constable': {price: 99, name: 'Mission Khaki TS PC Mocks', until: '2026-12-21', prefix: 'mk-pc-'},   // Anil, 25 Oct 2026: ₹99
};
// SI + Constable in one payment (Anil, 25 Oct 2026): recorded as a mock pass for each exam, each valid till its own exam
const COMBO = {price: 199,   // no longer sold (26 Oct 2026); kept so old combo rows still read
                name: 'Mission Khaki SI+PC Mocks', exams: ['ts-police-si', 'ts-police-constable']};
const FREE_MOCKS = {'mk-pc-1': true, 'mk-si-1': true, 'bk-g2mk-1': true};   // free for every registered student (Anil: Constable Mock 1, 25 Oct 2026; SI Mock 1, 28 Oct 2026; Bahubali Prelims (APPSC Group-II) Mock 1, 8 Nov 2026)
// Mock keys live in the 'keys' tab of this spreadsheet: mock_id | key (base64) | file | opens (yyyy-mm-dd, IST).
const MAX_DEVICES = 3;   // one phone number's passes work on at most this many phones/computers

// ---------------------------------------------------------------------------------------------------------------
function doGet() { return out({ok: true, service: 'Learn with Anil passes'}); }

function doPost(e) {
  try {
    if (e && e.parameter && e.parameter.mac) return webhook(formParams_(e));   // Instamojo → form-encoded, signed
    const b = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (b && b.data && b.data.order && /WEBHOOK/.test(String(b.type || ''))) return cfWebhook_(b);   // Cashfree → JSON (notify_url)
    const exam = String(b.exam || '');
    if (!/^[a-z0-9-]{2,40}$/.test(exam)) return out({ok: false, error: 'Unknown exam.'});
    // Student accounts (Anil, 2 Nov 2026: "student logins ... no need to login again and again ... like JioHotstar").
    // A student signs in once with Google, adds a phone number once, and stays logged in on that device for 12 months.
    // Requests carrying a session are answered for the account's phone (and its Google email); older phone + email requests still work.
    if (b.action === 'glogin') return out(glogin(b));
    let S = null;
    if (b.session) {
      S = session_(String(b.session));
      if (!S) return out({ok: false, relogin: true, error: 'Please log in again.'});
      if (S.phone) b.phone = S.phone;
      b.email = S.email; b.acct = S;
    }
    switch (b.action) {
      case 'setphone': return out(S ? setPhone(b, S, exam) : {ok: false, relogin: true, error: 'Please log in again.'});
      case 'me': return out(S ? me(S, exam, String(b.session)) : {ok: false, relogin: true, error: 'Please log in again.'});
      case 'logout': return out(S ? logout(S, String(b.session), String(b.target || '')) : {ok: true});
      case 'claim': return out(claim(b, exam));
      case 'buy': return out(buy(b, exam));
      case 'verify': return out(verify(b, exam));
      case 'passes': return out(passesFor(phoneOf(b.phone), exam, b.device, b.email, true, S));
      case 'mock': return out(mock(b, exam));
      case 'grievance': return out(grievance(b, exam));
      case 'ref': return out(refInfo(b));
      case 'refjoin': return out(refJoin(b));
      default: return out({ok: false, error: 'Unknown action.'});
    }
  } catch (err) {
    log_('error', String(err && err.stack || err));
    return out({ok: false, error: 'Something went wrong. Please try again in a minute.'});
  }
}

// ---------- grievance redressal cell (learnwithanil.in/help.html): every complaint gets a ticket in the 'grievances' tab ----------
// Consumer Protection (E-Commerce) Rules 2020: acknowledge within 48 hours, redress within one month.
const GRIEV_HEAD = ['time', 'ticket', 'name', 'phone', 'email', 'exam', 'category', 'payment_id', 'message', 'status', 'reply'];
const GRIEV_CATS = ['Payment or PYQ Pass', 'Mock test pack', 'A question or answer', 'Website not working', 'Refund', 'Other'];
function cell_(s) { s = String(s || '').trim(); return /^[=+\-@]/.test(s) ? "'" + s : s; }   // never let text act as a sheet formula
function grievance(b, exam) {
  const phone = phoneOf(b.phone), name = String(b.name || '').trim().slice(0, 80), email = String(b.email || '').trim().slice(0, 100);
  const msg = String(b.message || '').trim().slice(0, 2000), cat = GRIEV_CATS.indexOf(String(b.category)) >= 0 ? String(b.category) : 'Other';
  if (!name || !phone) return {ok: false, error: 'Please give your name and a valid 10-digit mobile number.'};
  if (msg.length < 10) return {ok: false, error: 'Please describe the problem in a sentence or two.'};
  const sh = sheet('grievances', GRIEV_HEAD);
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const v = sh.getDataRange().getValues(), today = today_();
    let n = 0, mine = 0;
    for (let i = 1; i < v.length; i++) if (v[i][0] && ymd_(new Date(v[i][0])) === today) { n++; if (String(v[i][3]) === phone) mine++; }
    if (mine >= 5) return {ok: false, error: 'You have already sent 5 complaints today. We will reply to them soon.'};
    if (n >= 300) return {ok: false, error: 'Too many complaints today. Please WhatsApp +91 94947 92739.'};
    const ticket = 'LWA-' + today.replace(/-/g, '').slice(2) + '-' + String(n + 1).padStart(3, '0');
    sh.appendRow([new Date(), ticket, cell_(name), phone, cell_(email), exam, cat, cell_(String(b.payment_id || '').slice(0, 60)), cell_(msg), 'new', '']);
    return {ok: true, ticket: ticket};
  } finally { lock.releaseLock(); }
}

function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function phoneOf(p) { const d = String(p || '').replace(/\D/g, '').slice(-10); return /^[6-9]\d{9}$/.test(d) ? d : ''; }
function prop(k) { return PropertiesService.getScriptProperties().getProperty(k) || ''; }
function book_() { return SpreadsheetApp.openById(prop('SHEET_ID')); }
function sheet(name, header) {
  const ss = book_();
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(header); sh.setFrozenRows(1); }
  return sh;
}
function log_(kind, text) { sheet('log', ['time', 'kind', 'text']).appendRow([new Date(), kind, String(text).slice(0, 4000)]); }
function ymd_(d) { return Utilities.formatDate(d, 'Asia/Kolkata', 'yyyy-MM-dd'); }
function today_() { return ymd_(new Date()); }
function day_(v) { return v instanceof Date ? ymd_(v) : String(v || ''); }
function inMonths_(n) { const d = new Date(); d.setMonth(d.getMonth() + n); return ymd_(d); }
function inDays_(n) { const d = new Date(); d.setDate(d.getDate() + n); return ymd_(d); }
function untilFor(kind, exam) { return kind === 'mock' ? (MOCKS[exam].until || inMonths_(MOCKS[exam].months || 12)) : inMonths_(PYQ.months); }

// ---------- Instamojo API v2 ----------
function api_() { return (prop('INSTAMOJO_API') || 'https://api.instamojo.com').replace(/\/+$/, ''); }
function token_() {
  const c = CacheService.getScriptCache(), hit = c.get('im_token');
  if (hit) return hit;
  const r = UrlFetchApp.fetch(api_() + '/oauth2/token/', {method: 'post', muteHttpExceptions: true,
    payload: {grant_type: 'client_credentials', client_id: prop('INSTAMOJO_CLIENT_ID'), client_secret: prop('INSTAMOJO_CLIENT_SECRET')}});
  const j = JSON.parse(r.getContentText() || '{}');
  if (!j.access_token) throw new Error('Instamojo token: ' + r.getResponseCode() + ' ' + r.getContentText().slice(0, 300));
  c.put('im_token', j.access_token, Math.max(60, (j.expires_in || 3600) - 120));
  return j.access_token;
}
function im_(method, path, payload) {
  const opt = {method: method, muteHttpExceptions: true, headers: {Authorization: 'Bearer ' + token_()}};
  if (payload) opt.payload = payload;
  const r = UrlFetchApp.fetch(api_() + path, opt);
  const t = r.getContentText() || '{}';
  if (r.getResponseCode() >= 300) throw new Error('Instamojo ' + path + ': ' + r.getResponseCode() + ' ' + t.slice(0, 300));
  return JSON.parse(t);
}

// ---------- Cashfree Payments (PG API, version 2026-01-01) ----------
const CF_VERSION = '2026-01-01';
function cfOn_() { return prop('PAY_GATEWAY').toLowerCase() === 'cashfree' && !!prop('CASHFREE_APP_ID') && !!prop('CASHFREE_SECRET'); }
function cfMode_() { return prop('CASHFREE_ENV').toLowerCase() === 'sandbox' ? 'sandbox' : 'production'; }
function cfApi_() { return cfMode_() === 'sandbox' ? 'https://sandbox.cashfree.com/pg' : 'https://api.cashfree.com/pg'; }
function cf_(method, path, payload) {
  const opt = {method: method, muteHttpExceptions: true, contentType: 'application/json',
    headers: {'x-client-id': prop('CASHFREE_APP_ID'), 'x-client-secret': prop('CASHFREE_SECRET'), 'x-api-version': CF_VERSION}};
  if (payload) opt.payload = JSON.stringify(payload);
  const r = UrlFetchApp.fetch(cfApi_() + path, opt);
  const t = r.getContentText() || '{}';
  if (r.getResponseCode() >= 300) throw new Error('Cashfree ' + path + ': ' + r.getResponseCode() + ' ' + t.slice(0, 300));
  return JSON.parse(t);
}
function isCfOrder_(id) { return /^LWA[0-9A-Z]{8,30}$/.test(String(id || '')); }
function cfOrderId_() {   // LWA + yymmdd + 6 characters, e.g. LWA261104K7Q2ZX: short enough for a student to read out from the receipt
  return 'LWA' + today_().replace(/-/g, '').slice(2) + Utilities.getUuid().replace(/-/g, '').toUpperCase().slice(0, 6);
}
function cfPaymentId_(id) {   // Cashfree's id of the successful payment on order `id` ('' if it can't be read right now)
  try {
    const ps = cf_('get', '/orders/' + encodeURIComponent(id) + '/payments');
    const s = (Array.isArray(ps) ? ps : []).filter(p => String(p.payment_status) === 'SUCCESS')[0];
    return s ? 'CF' + String(s.cf_payment_id) : '';
  } catch (e) { log_('cashfree-payments-error', String(e)); return ''; }
}

function cfBuy_(b, phone, amount, purpose, passExam, kind, back) {
  const id = cfOrderId_(), name = String(b.name || '').trim(), email = String(b.email || '').trim();
  const cust = {customer_id: 'lwa' + phone, customer_phone: phone};
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) && email.length <= 100) cust.customer_email = email;
  if (/^[A-Za-z][A-Za-z .'-]{2,99}$/.test(name)) cust.customer_name = name;   // optional; a name in Telugu or Hindi is simply left out
  const o = cf_('post', '/orders', {order_id: id, order_amount: amount, order_currency: 'INR', customer_details: cust,
    order_meta: {return_url: back + (back.indexOf('?') < 0 ? '?' : '&') + 'cf_order=' + id, notify_url: ScriptApp.getService().getUrl()},
    order_note: purpose});
  if (!o.payment_session_id) throw new Error('Cashfree order ' + id + ': no payment_session_id');
  sheet('requests', REQ_HEAD).appendRow([new Date(), id, phone, passExam, kind, amount, String(b.name || ''), String(b.email || ''), 'created']);
  return {ok: true, gateway: 'cashfree', mode: cfMode_(), session: o.payment_session_id, order: id};
}

// Asks Cashfree itself whether order `id` was paid in full and, if so, records the pass. Returns true when paid.
function cfConfirmPaid_(req, id, source) {
  const o = cf_('get', '/orders/' + encodeURIComponent(id));
  if (String(o.order_status || '') !== 'PAID' || Number(o.order_amount) < Number(req.amount || PYQ.price)) return false;
  req.request = id;
  grant_(req, cfPaymentId_(id) || ('cf-' + id), o.order_amount, source);
  return true;
}

// Cashfree calls this script (notify_url) when a payment on an order succeeds or fails. Apps Script cannot read the request headers,
// so Cashfree's signature can't be checked here: the message itself is never trusted, and the order is looked up on Cashfree with the
// secret key before anything is recorded (the same check as "verify").
function cfWebhook_(body) {
  const id = String(body.data.order.order_id || '');
  const req = isCfOrder_(id) ? requestRow_(id) : null;
  if (!req) { log_('cf-webhook-unknown', String(body.type) + ' ' + id); return out({ok: true}); }
  let paid = false;
  try { paid = cfConfirmPaid_(req, id, 'cf-webhook'); } catch (e) { log_('cf-webhook-error', String(e && e.stack || e)); }
  if (!paid && /FAIL|DROP/.test(String(body.type))) log_('cf-payment-failed', id + ' ' + JSON.stringify(((body.data.payment || {}).payment_message) || ''));
  return out({ok: true});
}

// ---------- actions ----------
const REQ_HEAD = ['time', 'request_id', 'phone', 'exam', 'kind', 'amount', 'name', 'email', 'status'];

function buy(b, exam) {
  const kind = 'pyq';   // Anil, 26 Oct 2026: one ₹45 PYQ Pass for everything; a 'mock' or 'combo' buy from an old page opens it too
  const phone = phoneOf(b.phone);
  if (!phone) return {ok: false, error: b.acct ? 'Please add your mobile number first (My Account).' : 'Please register with a valid 10-digit mobile number first.'};
  const amount = kind === 'mock' ? MOCKS[exam].price : kind === 'combo' ? COMBO.price : PYQ.price;
  const purpose = (kind === 'mock' ? MOCKS[exam].name : kind === 'combo' ? COMBO.name : PYQ.purpose).slice(0, 30);
  const passExam = kind === 'mock' ? exam : kind === 'combo' ? 'combo' : 'all';
  let back = String(b.back || '');
  if (back.indexOf(SITE) !== 0 || back.length > 180) back = SITE;
  if (cfOn_()) return cfBuy_(b, phone, amount, purpose, passExam, kind, back);
  if (!prop('INSTAMOJO_CLIENT_ID') || !prop('INSTAMOJO_CLIENT_SECRET')) return {ok: false, error: 'Online payment opens in a few hours. Please try again later today.'};
  const pr = im_('post', '/v2/payment_requests/', {
    purpose: purpose, amount: String(amount), buyer_name: String(b.name || '').slice(0, 100),
    email: String(b.email || '').slice(0, 100), phone: phone, redirect_url: back,
    webhook: ScriptApp.getService().getUrl(), send_email: 'false', send_sms: 'false', allow_repeated_payments: 'false'});
  sheet('requests', REQ_HEAD).appendRow([new Date(), pr.id, phone, passExam, kind, amount, String(b.name || ''), String(b.email || ''), 'created']);
  return {ok: true, url: pr.longurl};
}

function requestRow_(id) {
  const sh = sheet('requests', REQ_HEAD);
  const v = sh.getDataRange().getValues();
  for (let i = v.length - 1; i >= 1; i--) if (String(v[i][1]) === String(id)) return {sh: sh, row: i + 1, phone: String(v[i][2]), exam: String(v[i][3]), kind: String(v[i][4]), amount: v[i][5], email: String(v[i][7] || '')};
  return null;
}

function grant_(req, paymentId, amount, source) {
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  let fresh = false;   // a new paid PYQ Pass was recorded just now (not a repeat of the webhook / verify)
  try {
    const sh = sheet('passes', PASS_HEAD);
    const v = sh.getDataRange().getValues();
    // a combo is one payment recorded as a mock pass for each of its exams (the amount goes on the first row)
    const rows = req.kind === 'combo' ? COMBO.exams.map(ex => [ex, 'mock']) : [[req.exam, req.kind]];
    const cfReq = isCfOrder_(req.request);   // a Cashfree order is paid once: a second webhook or verify for it is a repeat, whatever payment id it read
    rows.forEach(([ex, kind], k) => {
      for (let i = 1; i < v.length; i++) if (String(v[i][2]) === ex && ((paymentId && String(v[i][5]) === String(paymentId)) ||
          (cfReq && String(v[i][6]) === String(req.request) && String(v[i][1]) === req.phone && String(v[i][8]).indexOf('claim') !== 0))) return;   // already recorded
      const amt = k ? 0 : (amount || req.amount);
      sh.appendRow([new Date(), req.phone, ex, kind, untilFor(kind, ex), paymentId || '', req.request || '', amt,
                    req.kind === 'combo' ? source + ' (combo)' : source, req.email.toLowerCase()]);
      if (kind === 'pyq' && Number(amt) > 0) fresh = true;
    });
    if (req.sh) req.sh.getRange(req.row, 9).setValue('paid');
  } finally { lock.releaseLock(); }
  if (fresh) { try { refBought_(req.phone, paymentId); } catch (e) { log_('referral-error', String(e && e.stack || e)); } }
}

// Asks Instamojo itself whether payment request `id` was paid and, if so, records the pass. Returns true when paid.
function confirmPaid_(req, id, pid, source) {
  const pr = im_('get', '/v2/payment_requests/' + encodeURIComponent(id) + '/');
  if (String(pr.status || '').toLowerCase() !== 'completed') return false;
  if (pid) {   // make sure that payment really belongs to this request and was credited
    const p = im_('get', '/v2/payments/' + encodeURIComponent(pid) + '/');
    if (!p.status || String(p.payment_request || '').indexOf(id) < 0) pid = '';
  }
  req.request = id;
  grant_(req, pid || ('req-' + id), pr.amount, source);
  return true;
}

function verify(b, exam) {
  const id = String(b.request || '');
  const req = requestRow_(id);
  if (!req || !(req.exam === exam || req.exam === 'all' || (req.kind === 'combo' && COMBO.exams.indexOf(exam) >= 0))) return {ok: false, error: 'Payment not found.'};
  const paid = isCfOrder_(id) ? cfConfirmPaid_(req, id, 'verify') : confirmPaid_(req, id, String(b.payment || ''), 'verify');
  if (!paid) return {ok: false, error: 'The payment is not complete yet. If money was taken, it will show here within a few minutes.'};
  return passesFor(req.phone, exam, b.device, req.email, false);
}

// Instamojo's webhook fields, decoded from the raw body as UTF-8 (so Telugu or Hindi buyer names keep their exact
// characters for the signature check); falls back to Apps Script's own decoding.
function formParams_(e) {
  const raw = e.postData && e.postData.contents;
  if (!raw || String(e.postData.type || '').indexOf('application/x-www-form-urlencoded') < 0) return e.parameter;
  try {
    const dec = s => decodeURIComponent(s.replace(/\+/g, ' '));
    const p = {};
    raw.split('&').forEach(kv => {
      if (!kv) return;
      const i = kv.indexOf('=');
      p[dec(i < 0 ? kv : kv.slice(0, i))] = i < 0 ? '' : dec(kv.slice(i + 1));
    });
    return p.mac ? p : e.parameter;
  } catch (err) { return e.parameter; }
}

function webhook(p) {
  const salt = prop('INSTAMOJO_SALT');
  const id = String(p.payment_request_id || '');
  const keys = Object.keys(p).filter(k => k !== 'mac').sort((a, b) => a.toLowerCase() < b.toLowerCase() ? -1 : 1);
  const msg = keys.map(k => p[k]).join('|');
  const mac = Utilities.computeHmacSignature(Utilities.MacAlgorithm.HMAC_SHA_1, msg, salt, Utilities.Charset.UTF_8)
    .map(x => ('0' + (x & 0xff).toString(16)).slice(-2)).join('');
  if (!salt || mac !== String(p.mac)) {
    // Never trust an unsigned message, but don't lose a real payment either: ask Instamojo directly.
    const req = requestRow_(id);
    const paid = !!req && confirmPaid_(req, id, String(p.payment_id || ''), 'webhook-checked');
    log_('webhook-bad-mac', JSON.stringify({payment_id: p.payment_id, request: id, paid_per_instamojo: paid}));
    return out({ok: paid});
  }
  if (String(p.status).toLowerCase() === 'credit') {
    const req = requestRow_(id);
    if (req) { req.request = id; grant_(req, p.payment_id, p.amount, 'webhook'); }
    else log_('webhook-unknown-request', id);
  }
  return out({ok: true});
}

const PASS_HEAD = ['time', 'phone', 'exam', 'kind', 'until', 'payment_id', 'request_id', 'amount', 'source', 'email'];
const TRIAL_HEAD = ['time', 'phone', 'email', 'until'];

function trialFor_(phone, email, start) {   // the phone's free-trial end date; starts it the first time if asked
  const sh = sheet('trials', TRIAL_HEAD);
  const v = sh.getDataRange().getValues();
  for (let i = 1; i < v.length; i++) if (String(v[i][1]) === phone) return day_(v[i][3]);
  if (!start) return '';
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const w = sh.getDataRange().getValues();
    for (let i = 1; i < w.length; i++) if (String(w[i][1]) === phone) return day_(w[i][3]);
    const until = inDays_(TRIAL_DAYS);
    sh.appendRow([new Date(), phone, email, until]);
    return until;
  } finally { lock.releaseLock(); }
}

// A pass needs the same phone AND email the student paid with. Returns {pyq, mock, trial, paid}: pyq = last day the
// student can use every PYQ on the site (PYQ Pass or free trial), mock = last day of this exam's mock pack.
function passesFor(phone, exam, device, email, startTrial, acct) {
  email = String(email || '').trim().toLowerCase();
  if (acct) { phone = acct.phone; email = acct.email; }
  if (!acct && (!phone || !email)) return {ok: true, passes: {}};
  if (acct && !phone && !email) return {ok: true, passes: {}};
  const v = sheet('passes', PASS_HEAD).getDataRange().getValues();
  const now = today_(), res = {};
  // logged-in account: its phone (ownership checked when the phone was linked) or its Google email; otherwise phone AND email
  const mine = (rp, re) => acct ? ((phone && rp === phone) || (email && re === email)) : (rp === phone && re === email);
  for (let i = 1; i < v.length; i++) {
    if (!mine(String(v[i][1]), String(v[i][9] || '').toLowerCase())) continue;
    const ex = String(v[i][2]), kind = String(v[i][3]), u = day_(v[i][4]);
    if (u < now) continue;
    if (kind === 'pyq' && ex === 'all') { if (!res.pyq || res.pyq < u) res.pyq = u; res.paid = true; }
    else if (kind === 'mock' && ex === exam) { if (!res.mock || res.mock < u) res.mock = u; }
  }
  // invite rewards: 'full' days extend a paid pass (everything); 'free' days (bonus) open PYQs, explanations and mocks, not downloads
  const w = sheet('rewards', REWARD_HEAD).getDataRange().getValues();
  for (let i = 1; i < w.length; i++) {
    if (!mine(String(w[i][1]), String(w[i][2] || '').toLowerCase())) continue;
    const u = day_(w[i][4]);
    if (u < now) continue;
    if (String(w[i][3]) === 'full') { if (!res.pyq || res.pyq < u) res.pyq = u; res.paid = true; }
    else if (!res.bonus || res.bonus < u) res.bonus = u;
  }
  if (res.paid && res.pyq && (!res.mock || res.mock < res.pyq)) res.mock = res.pyq;   // the PYQ Pass opens every mock series too
  if (res.bonus && (!res.mock || res.mock < res.bonus)) res.mock = res.bonus;
  const t = TRIAL_DAYS > 0 ? trialFor_(phone, email, startTrial) : '';
  if (t && t >= now) { res.trial = t; if (!res.pyq || res.pyq < t) res.pyq = t; }
  if (!acct && (res.pyq || res.mock) && device && !deviceOK_(phone, String(device))) return {ok: false, error: 'These passes are already in use on ' + MAX_DEVICES + ' devices.', passes: {}};
  return {ok: true, passes: res};
}

function deviceOK_(phone, device) {
  const sh = sheet('devices', ['time', 'phone', 'exam', 'device']);
  const v = sh.getDataRange().getValues();
  const seen = new Set();
  for (let i = 1; i < v.length; i++) if (String(v[i][1]) === phone) seen.add(String(v[i][3]));
  if (seen.has(device)) return true;
  if (seen.size >= MAX_DEVICES) return false;
  sh.appendRow([new Date(), phone, 'all', device]);
  return true;
}

function mock(b, exam) {   // the key of a sealed mock, book or the Bahubali code (the encrypted file is on the website), for a valid pass
  const id = String(b.id || '');
  const item = /^(bk-[a-z0-9-]{2,40}|bb-code)$/.test(id);   // study books and the Bahubali access code: any exam, PYQ Pass only
  if (!item && (!MOCKS[exam] || id.indexOf(MOCKS[exam].prefix) !== 0)) return {ok: false, error: 'This mock is not part of this exam\'s test series.'};
  const v = sheet('keys', ['mock_id', 'key', 'file', 'opens']).getDataRange().getValues();
  let row = null;
  for (let i = 1; i < v.length; i++) if (String(v[i][0]) === id) row = v[i];
  if (!row) return {ok: false, error: item ? 'This is not ready yet.' : 'This mock is not ready yet.'};
  const opens = day_(row[3]);
  if (opens > today_()) return {ok: false, error: 'This mock opens on ' + opens + '.'};
  if (FREE_MOCKS[id]) {   // free mock: any registered student (bk- ids too: Bahubali Prelims Mock 1 is 'bk-g2mk-1')
    const phone = phoneOf(b.phone);
    if (!phone) return {ok: false, error: 'Please register first (it is free): your name, phone and email.'};
    try { sheet('free', ['time', 'phone', 'email', 'mock']).appendRow([new Date(), phone, cell_(String(b.email || '').slice(0, 100)), id]); } catch (e) {}
    return {ok: true, id: id, key: String(row[1]), file: String(row[2]), free: true};
  }
  const ps = passesFor(phoneOf(b.phone), exam, b.device, b.email, false, b.acct || null);
  if (!ps.ok) return ps;
  // free invite days open the sealed explanations (bk-ex-<exam>) and mocks, but not the PDF downloads or the Bahubali code
  if (item ? !((ps.passes.paid && ps.passes.pyq) || (/^bk-ex-/.test(id) && ps.passes.bonus)) : !ps.passes.mock)
    return {ok: false, error: 'This needs the ₹' + PYQ.price + ' PYQ Pass (everything on the site, 12 months).', need: 'pyq'};
  return {ok: true, id: id, key: String(row[1]), file: String(row[2])};
}

// Run from the editor (Run ▶ checkSetup) to check the settings. Prints no secrets.
function checkSetup() {
  Logger.log('Spreadsheet: ' + (prop('SHEET_ID') ? book_().getName() : 'SHEET_ID MISSING'));
  ['INSTAMOJO_CLIENT_ID', 'INSTAMOJO_CLIENT_SECRET', 'INSTAMOJO_SALT'].forEach(k => Logger.log(k + ': ' + (prop(k) ? 'set' : 'MISSING')));
  ['CASHFREE_APP_ID', 'CASHFREE_SECRET'].forEach(k => Logger.log(k + ': ' + (prop(k) ? 'set' : 'not set')));
  Logger.log('New checkouts go to: ' + (cfOn_() ? 'Cashfree (' + cfMode_() + ')' : 'Instamojo') + '   (PAY_GATEWAY = ' + (prop('PAY_GATEWAY') || 'not set') + ')');
  if (cfOn_()) { try { cf_('get', '/orders/LWA000000CHECK'); Logger.log('Cashfree keys: accepted'); }
                 catch (e) { Logger.log(/: 404 /.test(String(e)) ? 'Cashfree keys: accepted' : 'Cashfree keys: ' + String(e).slice(0, 200)); } }
  Logger.log('Web app URL: ' + ScriptApp.getService().getUrl());
}

// ---------- student accounts: Google sign-in, 12-month sessions, devices, linking a payment (Anil, 2 Nov 2026) ----------
const ACC_HEAD = ['time', 'email', 'name', 'phone', 'district', 'sub', 'last_login'];
const SES_HEAD = ['time', 'token_hash', 'email', 'device', 'agent', 'expires', 'revoked', 'last_seen'];
const SESSION_MONTHS = 12;
function sha_(t) { return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, t).map(b => ('0' + (b & 255).toString(16)).slice(-2)).join(''); }
function account_(email) {
  const sh = sheet('accounts', ACC_HEAD), v = sh.getDataRange().getValues();
  for (let i = 1; i < v.length; i++) if (String(v[i][1]).toLowerCase() === email)
    return {sh: sh, row: i + 1, email: email, name: String(v[i][2] || ''), phone: String(v[i][3] || ''), district: String(v[i][4] || '')};
  return null;
}
function pub_(a) { return {email: a.email, name: a.name, phone: a.phone, district: a.district}; }
function deviceName_(ua) {
  ua = String(ua || '');
  const os = /Android/i.test(ua) ? 'Android phone' : /iPhone|iPad/i.test(ua) ? 'iPhone' : /Windows/i.test(ua) ? 'Windows computer' : /Mac OS/i.test(ua) ? 'Mac' : /Linux/i.test(ua) ? 'Linux computer' : 'Device';
  const br = /Edg\//.test(ua) ? 'Edge' : /OPR\//.test(ua) ? 'Opera' : /Chrome\//.test(ua) ? 'Chrome' : /Firefox\//.test(ua) ? 'Firefox' : /Safari\//.test(ua) ? 'Safari' : '';
  return os + (br ? ' · ' + br : '');
}

function glogin(b) {
  const cid = prop('GOOGLE_CLIENT_ID');
  if (!cid) return {ok: false, error: 'Google login is not switched on yet. Please register with your phone and email.'};
  const r = UrlFetchApp.fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + encodeURIComponent(String(b.credential || '')), {muteHttpExceptions: true});
  let t = {}; try { t = JSON.parse(r.getContentText()); } catch (e) {}
  if (r.getResponseCode() !== 200 || t.aud !== cid || !/^(https:\/\/)?accounts\.google\.com$/.test(String(t.iss)) || String(t.email_verified) !== 'true' || Number(t.exp) * 1000 < Date.now())
    return {ok: false, error: 'Google login did not work. Please try again.'};
  return newSession_(String(t.email).toLowerCase(), String(t.name || t.given_name || '').slice(0, 80), String(t.sub || ''), b);
}

// Log in (or create the account) for an email that has been checked, by Google or by an emailed code, on this device.
function newSession_(email, name, sub, b) {
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    let a = account_(email);
    if (!a) { sheet('accounts', ACC_HEAD).appendRow([new Date(), email, cell_(name), '', '', sub, new Date()]); a = account_(email); }
    else a.sh.getRange(a.row, 7).setValue(new Date());
    // one session per login; at most MAX_DEVICES stay active (the oldest is logged out, like a streaming app)
    const token = Utilities.getUuid().replace(/-/g, '') + Utilities.getUuid().replace(/-/g, '');
    const sh = sheet('sessions', SES_HEAD);
    sh.appendRow([new Date(), sha_(token), email, String(b.device || '').slice(0, 40), String(b.agent || '').slice(0, 160), inMonths_(SESSION_MONTHS), '', new Date()]);
    const v = sh.getDataRange().getValues(), now = today_(), live = [];
    for (let i = 1; i < v.length; i++) if (String(v[i][2]) === email && !v[i][6] && day_(v[i][5]) >= now) live.push(i + 1);
    let out = 0;
    while (live.length > MAX_DEVICES) { sh.getRange(live.shift(), 7).setValue(new Date()); out++; }
    return {ok: true, session: token, account: pub_(a), loggedOut: out};
  } finally { lock.releaseLock(); }
}

// Email-code (OTP) login was written on 4 Nov 2026 (commit 2a9c5e9324) and taken out the same morning (Anil, 4 Nov 2026:
// "let the students login previously as done yesterday"). It needed Google's "Send email as you" permission, which blocks every
// deploy until Anil allows it. To bring it back: restore the code from that commit, Run allowEmailCodes once, then deploy.

function session_(token) {
  if (!/^[0-9a-f]{64}$/.test(token)) return null;
  const h = sha_(token), sh = sheet('sessions', SES_HEAD), v = sh.getDataRange().getValues(), now = today_();
  for (let i = v.length - 1; i >= 1; i--) {
    if (String(v[i][1]) !== h) continue;
    if (v[i][6] || day_(v[i][5]) < now) return null;
    const a = account_(String(v[i][2]));
    if (!a) return null;
    const seen = v[i][7] instanceof Date ? v[i][7] : null;
    if (!seen || Date.now() - seen.getTime() > 6 * 3600 * 1000) sh.getRange(i + 1, 8).setValue(new Date());
    return {email: a.email, phone: a.phone, name: a.name, district: a.district, acc: a, srow: i + 1};
  }
  return null;
}

// Link a phone number to the account. A number that already has a PYQ Pass is linked only if that pass was bought with this
// Google email, or with the payment ID from the student's own receipt; a number linked to another account is refused.
function setPhone(b, S, exam) {
  const phone = phoneOf(b.phone);
  if (!phone) return {ok: false, error: 'Please enter a valid 10-digit mobile number.'};
  const name = String(b.name || S.name || '').trim().slice(0, 80), district = String(b.district || S.district || '').trim().slice(0, 60);
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const av = sheet('accounts', ACC_HEAD).getDataRange().getValues();
    for (let i = 1; i < av.length; i++) if (String(av[i][3]) === phone && String(av[i][1]).toLowerCase() !== S.email)
      return {ok: false, error: 'This number is already linked to another Google account. If it is yours, please write to us at learnwithanil.in/help.html.'};
    if (phone !== S.phone) {
      const v = sheet('passes', PASS_HEAD).getDataRange().getValues(), pid = String(b.payment || '').trim();
      const rows = v.slice(1).filter(r => String(r[1]) === phone);
      if (rows.length && !rows.some(r => String(r[9] || '').toLowerCase() === S.email || (pid && (String(r[5]).toUpperCase() === pid.toUpperCase() || String(r[6]).toUpperCase() === pid.toUpperCase()))))
        return {ok: false, needPayment: true, error: 'This number has a PYQ Pass bought with another email. Enter the payment ID or order ID from your payment SMS or email (it starts with MOJO or LWA) to link it.'};
    }
    const sh = S.acc.sh;
    sh.getRange(S.acc.row, 3, 1, 3).setValues([[cell_(name), phone, cell_(district)]]);
  } finally { lock.releaseLock(); }
  const a = account_(S.email);
  return {ok: true, account: pub_(a), passes: passesFor(a.phone, exam, '', a.email, false, {phone: a.phone, email: a.email}).passes};
}

function me(S, exam, token) {
  const h = sha_(token), v = sheet('sessions', SES_HEAD).getDataRange().getValues(), now = today_(), devices = [];
  for (let i = 1; i < v.length; i++) if (String(v[i][2]) === S.email && !v[i][6] && day_(v[i][5]) >= now)
    devices.push({id: String(v[i][1]).slice(0, 12), name: deviceName_(v[i][4]), since: v[i][0] instanceof Date ? ymd_(v[i][0]) : String(v[i][0]), seen: v[i][7] instanceof Date ? ymd_(v[i][7]) : '', current: String(v[i][1]) === h});
  const pv = sheet('passes', PASS_HEAD).getDataRange().getValues(), pays = [];
  for (let i = 1; i < pv.length; i++) {
    const rp = String(pv[i][1]), re = String(pv[i][9] || '').toLowerCase();
    if ((S.phone && rp === S.phone) || re === S.email) pays.push({on: pv[i][0] instanceof Date ? ymd_(pv[i][0]) : String(pv[i][0]), what: String(pv[i][3]) === 'pyq' ? 'PYQ Pass' : 'Mock pack', until: day_(pv[i][4]), id: isCfOrder_(pv[i][6]) ? String(pv[i][6]) : String(pv[i][5]), amount: pv[i][7]});
  }
  return {ok: true, account: pub_(S.acc), passes: passesFor(S.phone, exam, '', S.email, false, S).passes, devices: devices, payments: pays};
}

function logout(S, token, target) {   // target = a device id from 'me' (first 12 characters of its session hash); none = this device
  const h = target ? '' : sha_(token), sh = sheet('sessions', SES_HEAD), v = sh.getDataRange().getValues();
  for (let i = 1; i < v.length; i++) {
    const rh = String(v[i][1]);
    if (String(v[i][2]) === S.email && !v[i][6] && (target ? rh.slice(0, 12) === target : rh === h)) sh.getRange(i + 1, 7).setValue(new Date());
  }
  return {ok: true};
}

// "Paid already but it still shows locked?": link a payment by its Instamojo payment ID (MOJO…) or Cashfree order ID (LWA…), both on the
// student's own receipt. Works for a logged-in account or a phone + email registration. One payment can be linked to one more number only once.
function claim(b, exam) {
  const pid = String(b.payment || '').trim().toUpperCase();
  const cf = isCfOrder_(pid);
  if (!cf && !/^MOJO[0-9A-Z]{8,30}$/.test(pid)) return {ok: false, error: 'Please enter the payment ID or order ID exactly as in your payment SMS or email (it starts with MOJO or LWA).'};
  const phone = phoneOf(b.phone), email = String(b.email || '').trim().toLowerCase();
  if (!phone) return {ok: false, error: b.acct ? 'Please add your mobile number first.' : 'Please register with your phone number first.'};
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const sh = sheet('passes', PASS_HEAD), v = sh.getDataRange().getValues();
    const rows = v.slice(1).filter(r => String(cf ? r[6] : r[5]).toUpperCase() === pid);
    if (rows.some(r => String(r[1]) === phone)) return Object.assign(passesFor(phone, exam, b.device, email, false, b.acct || null), {note: 'This payment is already linked to your number.'});
    if (rows.filter(r => String(r[8]).indexOf('claim') === 0).length) return {ok: false, error: 'This payment is already linked to another number. Please write to us at learnwithanil.in/help.html.'};
    let src = rows[0];
    if (!src && cf) {   // not recorded yet (webhook missed): ask Cashfree directly
      let o = {}; try { o = cf_('get', '/orders/' + encodeURIComponent(pid)); } catch (e) { o = {}; }
      if (String(o.order_status) !== 'PAID' || Number(o.order_amount) < PYQ.price) return {ok: false, error: 'We could not find this payment. Please check the ID, or write to us at learnwithanil.in/help.html with a screenshot.'};
      sh.appendRow([new Date(), phone, 'all', 'pyq', inMonths_(PYQ.months), cfPaymentId_(pid) || ('cf-' + pid), pid, o.order_amount, 'claim (cashfree)', email]);
    } else if (!src) {   // not recorded yet (webhook missed): ask Instamojo directly
      let p = {}; try { p = im_('get', '/v2/payments/' + encodeURIComponent(pid) + '/'); } catch (e) { p = {}; }
      if (!p || p.status !== true || Number(p.amount) < PYQ.price) return {ok: false, error: 'We could not find this payment. Please check the ID, or write to us at learnwithanil.in/help.html with a screenshot.'};
      sh.appendRow([new Date(), phone, 'all', 'pyq', inMonths_(PYQ.months), pid, String(p.payment_request || ''), p.amount, 'claim (instamojo)', email]);
    } else {
      if (String(src[3]) !== 'pyq' || day_(src[4]) < today_()) return {ok: false, error: 'This payment is not an active PYQ Pass.'};
      sh.appendRow([new Date(), phone, String(src[2]), 'pyq', day_(src[4]), String(src[5]), String(src[6]), 0, 'claim (from ' + String(src[1]).slice(-4) + ')', email]);
    }
    log_('claim', pid + ' -> ' + phone);
  } finally { lock.releaseLock(); }
  return Object.assign(passesFor(phone, exam, b.device, email, false, b.acct || null), {note: 'Payment linked. Your PYQ Pass is active.'});
}

// ---------- invite friends, earn free days (Anil, 3 Nov 2026: "can we make this sharing compulsory?" → a reward instead) ----------
// Every registered student gets a personal link (learnwithanil.in/...?ref=<code>). When a NEW student registers through it, the
// sender gets REF.joinDays free days (for at most REF.joinMax friends); when that friend first buys the PYQ Pass, the sender gets
// REF.buyDays more. A sender whose paid pass is active gets the days added to its end ('full' rows in the 'rewards' tab: everything,
// downloads too); otherwise they are free days ('free' rows: every PYQ with explanations, practice and mocks, but not the PDF
// downloads, study books or the Bahubali code, which could be kept for ever). Rewards live in their own tab so the passes tab (and
// the Payments dashboard built from it) keeps only real payments.
// Not rewarded (neither the joining nor a later purchase): the sender's own phone or email ('self'); a phone, email or device already
// known to the site ('known' / 'device'); a friend already referred once. After REF.joinMax rewarded friends a new one is 'cap': no
// joining days, but their first purchase still counts. Each referral is recorded in the 'referrals' tab, rewarded or not, so Anil can see them.
const REF = {joinDays: 3, joinMax: 10, buyDays: 30};
const REFCODE_HEAD = ['time', 'code', 'phone', 'email'];
const REFERRAL_HEAD = ['time', 'code', 'ref_phone', 'ref_email', 'friend_phone', 'friend_email', 'friend_name', 'device', 'status',
                       'join_days', 'bought', 'buy_days', 'payment_id'];
const REWARD_HEAD = ['time', 'phone', 'email', 'kind', 'until', 'days', 'reason', 'code', 'friend_phone'];
const REF_LETTERS = 'ABCDEFGHJKLMNPQRSTUVWXYZ';   // letters only (no I or O), so the sheet never reads a code as a number or date

function newRefCode_() {
  const u = Utilities.getUuid().replace(/-/g, '') + Utilities.getUuid().replace(/-/g, '');
  let s = '';
  for (let k = 0; k < 6; k++) s += REF_LETTERS[parseInt(u.substr(k * 4, 4), 16) % REF_LETTERS.length];
  return s;
}
function addDays_(d, n) { const t = new Date(String(d) + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + n); return t.toISOString().slice(0, 10); }

function refStats_(code) {
  const v = sheet('referrals', REFERRAL_HEAD).getDataRange().getValues();
  let joined = 0, bought = 0, days = 0, rewarded = 0;
  for (let i = 1; i < v.length; i++) {
    if (String(v[i][1]) !== code || !/^(ok|cap)$/.test(String(v[i][8]))) continue;   // new students only (not self / known / device)
    joined++;
    if (Number(v[i][9]) > 0) rewarded++;
    if (v[i][10]) bought++;
    days += (Number(v[i][9]) || 0) + (Number(v[i][11]) || 0);
  }
  return {joined: joined, bought: bought, days: days, left: Math.max(0, REF.joinMax - rewarded),
          joinDays: REF.joinDays, joinMax: REF.joinMax, buyDays: REF.buyDays};
}

// The student's own code (one per phone number; made the first time) and how their invites are doing.
function refInfo(b) {
  const phone = phoneOf(b.phone), email = String(b.email || '').trim().toLowerCase();
  if (!phone || !email) return {ok: false, error: b.acct ? 'Please add your mobile number first (My Account).' : 'Please register first (it is free).'};
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  let code = '';
  try {
    const sh = sheet('refcodes', REFCODE_HEAD), v = sh.getDataRange().getValues();
    for (let i = 1; i < v.length; i++) if (String(v[i][2]) === phone) { code = String(v[i][1]); break; }
    if (!code) {
      const have = new Set(v.slice(1).map(r => String(r[1])));
      do code = newRefCode_(); while (have.has(code));
      sh.appendRow([new Date(), code, phone, email]);
    }
  } finally { lock.releaseLock(); }
  return Object.assign({ok: true, code: code}, refStats_(code));
}

// Was this phone, email or device on the site before this registration? Then it is not a new student brought by the link.
function refKnown_(phone, email, device, referrals) {
  const has = (tab, head, test) => sheet(tab, head).getDataRange().getValues().slice(1).some(test);
  if (device && referrals.slice(1).some(r => String(r[7]) === device)) return 'device';
  if (device && has('devices', ['time', 'phone', 'exam', 'device'], r => String(r[3]) === device)) return 'device';
  if (device && has('sessions', SES_HEAD, r => String(r[3]) === device && String(r[2]).toLowerCase() !== email)) return 'device';
  if (has('passes', PASS_HEAD, r => String(r[1]) === phone || (email && String(r[9] || '').toLowerCase() === email))) return 'known';
  if (has('requests', REQ_HEAD, r => String(r[2]) === phone)) return 'known';
  if (has('refcodes', REFCODE_HEAD, r => String(r[2]) === phone)) return 'known';
  if (has('free', ['time', 'phone', 'email', 'mock'], r => String(r[1]) === phone)) return 'known';
  if (has('trials', TRIAL_HEAD, r => String(r[1]) === phone)) return 'known';
  const old = Date.now() - 2 * 86400000;   // a Google account made just now for this registration is fine; an older one is not new
  if (has('accounts', ACC_HEAD, r => (String(r[3]) === phone && String(r[1]).toLowerCase() !== email) ||
                                     (email && String(r[1]).toLowerCase() === email && r[0] instanceof Date && r[0].getTime() < old))) return 'known';
  return '';
}

// Free days for the sender of a link: added to the end of an active paid pass, else counted from today (or from the end of
// free days they already have).
function refReward_(owner, days, reason, code, friend) {
  const now = today_(), p = sheet('passes', PASS_HEAD).getDataRange().getValues(), w = sheet('rewards', REWARD_HEAD).getDataRange().getValues();
  const mine = (rp, re) => rp === owner.phone || (owner.email && re === owner.email);
  let paid = '', free = '';
  for (let i = 1; i < p.length; i++) if (mine(String(p[i][1]), String(p[i][9] || '').toLowerCase()) && String(p[i][3]) === 'pyq') { const u = day_(p[i][4]); if (u > paid) paid = u; }
  for (let i = 1; i < w.length; i++) if (mine(String(w[i][1]), String(w[i][2] || '').toLowerCase())) {
    const u = day_(w[i][4]);
    if (String(w[i][3]) === 'full') { if (u > paid) paid = u; } else if (u > free) free = u;
  }
  const full = paid >= now, until = full ? addDays_(paid, days) : addDays_(free >= now ? free : now, days);
  sheet('rewards', REWARD_HEAD).appendRow([new Date(), owner.phone, owner.email, full ? 'full' : 'free', until, days, reason, code, friend]);
}

// A new student registered with a friend's link. Records the referral (rewarded or not) and gives the friend their days.
function refJoin(b) {
  const code = String(b.code || '').trim().toUpperCase(), phone = phoneOf(b.phone), email = String(b.email || '').trim().toLowerCase();
  const device = String(b.device || '').slice(0, 40), name = String(b.name || '').trim().slice(0, 80);
  if (!/^[A-Z]{6}$/.test(code) || !phone) return {ok: false, error: 'Invalid invite.'};
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    let owner = null;
    const cv = sheet('refcodes', REFCODE_HEAD).getDataRange().getValues();
    for (let i = 1; i < cv.length; i++) if (String(cv[i][1]) === code) owner = {phone: String(cv[i][2]), email: String(cv[i][3] || '').toLowerCase()};
    if (!owner) return {ok: false, error: 'Invalid invite.'};
    const rsh = sheet('referrals', REFERRAL_HEAD), rv = rsh.getDataRange().getValues();
    if (rv.slice(1).some(r => String(r[4]) === phone)) return {ok: true, status: 'already'};
    let status = owner.phone === phone || (email && owner.email === email) ? 'self' : refKnown_(phone, email, device, rv);
    if (!status) status = rv.slice(1).filter(r => String(r[1]) === code && Number(r[9]) > 0).length >= REF.joinMax ? 'cap' : 'ok';
    const days = status === 'ok' ? REF.joinDays : 0;
    rsh.appendRow([new Date(), code, owner.phone, owner.email, phone, email, cell_(name), device, status, days, '', '', '']);
    if (days) refReward_(owner, days, 'friend registered', code, phone);
    return {ok: true, status: status};
  } finally { lock.releaseLock(); }
}

// A referred friend (status ok or cap) bought the PYQ Pass for the first time: the sender gets REF.buyDays.
function refBought_(phone, pid) {
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const sh = sheet('referrals', REFERRAL_HEAD), v = sh.getDataRange().getValues();
    for (let i = 1; i < v.length; i++) {
      if (String(v[i][4]) !== String(phone)) continue;
      if (!/^(ok|cap)$/.test(String(v[i][8])) || v[i][10]) return;   // only a new student brought by the link, and only their first purchase
      sh.getRange(i + 1, 11, 1, 3).setValues([[new Date(), REF.buyDays, String(pid || '')]]);
      refReward_({phone: String(v[i][2]), email: String(v[i][3] || '').toLowerCase()}, REF.buyDays, 'friend bought the PYQ Pass', String(v[i][1]), String(phone));
      return;
    }
  } finally { lock.releaseLock(); }
}
