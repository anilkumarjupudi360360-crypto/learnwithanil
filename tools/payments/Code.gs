/**
 * Learn with Anil — passes and payments (Google Apps Script; its data lives in the private "Learn with Anil – Passes" spreadsheet).
 *
 * Passes
 *  - PYQ Pass (₹45): every previous paper on the whole website, all exams (including exams added later), for 12 months
 *    from the day of payment. Stored with exam = 'all'.
 *  - Free trial: the same access as the PYQ Pass for 3 days, once per phone number, starting the first time a registered
 *    student's phone and email reach this script (right after they register on the site). Stored in the 'trials' tab.
 *  - Mock packs (Mission Khaki ₹150 and Mission Khaki – Constable ₹99, valid till that exam; Mission CGL ₹149, 12 months):
 *    one exam's mock tests only (the PYQ Pass is separate). The SI + Constable combo (₹199) records one mock pass for each.
 *  - Free mocks (FREE_MOCKS): open to every registered student, no pass needed; each opening is logged in the 'free' tab.
 *
 * What it does
 *  - buy:     creates an Instamojo payment request for a pass (price fixed here, never taken from the browser)
 *             and returns Instamojo's checkout link.
 *  - verify:  after Instamojo sends the student back to learnwithanil.in, asks Instamojo whether that payment
 *             request was paid and, if so, records the pass.
 *  - webhook: Instamojo also calls this script when a payment succeeds (checked with the private salt), so a pass
 *             is recorded even if the student closes the page.
 *  - passes:  which passes (and free trial) a registered phone number has; starts the free trial the first time.
 *  - mock:    the key of a released mock (its encrypted file is on the website), only for a valid mock pass (or a free mock).
 *
 * Settings are NOT in this file. They live under Project Settings → Script properties:
 *   SHEET_ID                                       the ID of the "Learn with Anil – Passes" spreadsheet (the only sheet this script opens)
 *   INSTAMOJO_CLIENT_ID, INSTAMOJO_CLIENT_SECRET   (Instamojo dashboard → API & Plugins; "API v2")
 *   INSTAMOJO_SALT                                 (Instamojo private salt, used to check webhooks)
 *   INSTAMOJO_API (optional)                       defaults to https://api.instamojo.com
 */

const SITE = 'https://learnwithanil.in/';
const PYQ = {price: 45, months: 12, purpose: 'PYQ Pass - All Exams (1 yr)'};   // Instamojo allows 30 characters
const TRIAL_DAYS = 0;   // free trial switched off (Anil, 23 Oct 2026: every PYQ needs the paid pass). Was 3.
const MOCKS = {   // exam id: mock pack on sale (price, name shown at checkout, last day the pass is valid or months from payment,
                  // and the prefix every mock id of that pack starts with: a pass for one pack never opens another pack's mocks)
  'ts-police-si': {price: 150, name: 'Mission Khaki TS SI Mocks', until: '2026-11-30', prefix: 'mk-si-'},
  'ssc-cgl': {price: 149, name: 'Mission CGL SSC Mocks', months: 12, prefix: 'mk-cgl-'},   // Anil, 24 Oct 2026: ₹149
  'ts-police-constable': {price: 99, name: 'Mission Khaki TS PC Mocks', until: '2026-12-21', prefix: 'mk-pc-'},   // Anil, 25 Oct 2026: ₹99
};
// SI + Constable in one payment (Anil, 25 Oct 2026): recorded as a mock pass for each exam, each valid till its own exam
const COMBO = {price: 199, name: 'Mission Khaki SI+PC Mocks', exams: ['ts-police-si', 'ts-police-constable']};
const FREE_MOCKS = {'mk-pc-1': true};   // free for every registered student (Anil, 25 Oct 2026: Constable Mock 1)
// Mock keys live in the 'keys' tab of this spreadsheet: mock_id | key (base64) | file | opens (yyyy-mm-dd, IST).
const MAX_DEVICES = 3;   // one phone number's passes work on at most this many phones/computers

// ---------------------------------------------------------------------------------------------------------------
function doGet() { return out({ok: true, service: 'Learn with Anil passes'}); }

function doPost(e) {
  try {
    if (e && e.parameter && e.parameter.mac) return webhook(formParams_(e));   // Instamojo → form-encoded, signed
    const b = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const exam = String(b.exam || '');
    if (!/^[a-z0-9-]{2,40}$/.test(exam)) return out({ok: false, error: 'Unknown exam.'});
    switch (b.action) {
      case 'buy': return out(buy(b, exam));
      case 'verify': return out(verify(b, exam));
      case 'passes': return out(passesFor(phoneOf(b.phone), exam, b.device, b.email, true));
      case 'mock': return out(mock(b, exam));
      case 'grievance': return out(grievance(b, exam));
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

// ---------- actions ----------
const REQ_HEAD = ['time', 'request_id', 'phone', 'exam', 'kind', 'amount', 'name', 'email', 'status'];

function buy(b, exam) {
  const kind = b.kind === 'mock' ? 'mock' : b.kind === 'combo' ? 'combo' : 'pyq';
  if (kind === 'mock' && !MOCKS[exam]) return {ok: false, error: 'This mock test pack is not on sale yet.'};
  if (kind === 'combo' && COMBO.exams.indexOf(exam) < 0) return {ok: false, error: 'This combo is not on sale for this exam.'};
  const phone = phoneOf(b.phone);
  if (!phone) return {ok: false, error: 'Please register with a valid 10-digit mobile number first.'};
  if (!prop('INSTAMOJO_CLIENT_ID') || !prop('INSTAMOJO_CLIENT_SECRET')) return {ok: false, error: 'Online payment opens in a few hours. Please try again later today.'};
  const amount = kind === 'mock' ? MOCKS[exam].price : kind === 'combo' ? COMBO.price : PYQ.price;
  const purpose = (kind === 'mock' ? MOCKS[exam].name : kind === 'combo' ? COMBO.name : PYQ.purpose).slice(0, 30);
  const passExam = kind === 'mock' ? exam : kind === 'combo' ? 'combo' : 'all';
  let back = String(b.back || '');
  if (back.indexOf(SITE) !== 0) back = SITE;
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
  try {
    const sh = sheet('passes', PASS_HEAD);
    const v = sh.getDataRange().getValues();
    // a combo is one payment recorded as a mock pass for each of its exams (the amount goes on the first row)
    const rows = req.kind === 'combo' ? COMBO.exams.map(ex => [ex, 'mock']) : [[req.exam, req.kind]];
    rows.forEach(([ex, kind], k) => {
      for (let i = 1; i < v.length; i++) if (paymentId && String(v[i][5]) === String(paymentId) && String(v[i][2]) === ex) return;   // already recorded
      sh.appendRow([new Date(), req.phone, ex, kind, untilFor(kind, ex), paymentId || '', req.request || '', k ? 0 : (amount || req.amount),
                    req.kind === 'combo' ? source + ' (combo)' : source, req.email.toLowerCase()]);
    });
    if (req.sh) req.sh.getRange(req.row, 9).setValue('paid');
  } finally { lock.releaseLock(); }
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
  if (!confirmPaid_(req, id, String(b.payment || ''), 'verify')) return {ok: false, error: 'The payment is not complete yet. If money was taken, it will show here within a few minutes.'};
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
function passesFor(phone, exam, device, email, startTrial) {
  email = String(email || '').trim().toLowerCase();
  if (!phone || !email) return {ok: true, passes: {}};
  const v = sheet('passes', PASS_HEAD).getDataRange().getValues();
  const now = today_(), res = {};
  for (let i = 1; i < v.length; i++) {
    if (String(v[i][1]) !== phone || String(v[i][9] || '').toLowerCase() !== email) continue;
    const ex = String(v[i][2]), kind = String(v[i][3]), u = day_(v[i][4]);
    if (u < now) continue;
    if (kind === 'pyq' && ex === 'all') { if (!res.pyq || res.pyq < u) res.pyq = u; res.paid = true; }
    else if (kind === 'mock' && ex === exam) { if (!res.mock || res.mock < u) res.mock = u; }
  }
  const t = TRIAL_DAYS > 0 ? trialFor_(phone, email, startTrial) : '';
  if (t && t >= now) { res.trial = t; if (!res.pyq || res.pyq < t) res.pyq = t; }
  if ((res.pyq || res.mock) && device && !deviceOK_(phone, String(device))) return {ok: false, error: 'These passes are already in use on ' + MAX_DEVICES + ' devices.', passes: {}};
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

function mock(b, exam) {   // the key of a sealed mock (the encrypted file is on the website), only for a valid mock pass
  const id = String(b.id || '');
  if (!MOCKS[exam] || id.indexOf(MOCKS[exam].prefix) !== 0) return {ok: false, error: 'This mock is not part of this exam\'s test series.'};
  const v = sheet('keys', ['mock_id', 'key', 'file', 'opens']).getDataRange().getValues();
  let row = null;
  for (let i = 1; i < v.length; i++) if (String(v[i][0]) === id) row = v[i];
  if (!row) return {ok: false, error: 'This mock is not ready yet.'};
  const opens = day_(row[3]);
  if (opens > today_()) return {ok: false, error: 'This mock opens on ' + opens + '.'};
  if (FREE_MOCKS[id]) {   // free mock: any registered student
    const phone = phoneOf(b.phone);
    if (!phone) return {ok: false, error: 'Please register first (it is free): your name, phone and email.'};
    try { sheet('free', ['time', 'phone', 'email', 'mock']).appendRow([new Date(), phone, cell_(String(b.email || '').slice(0, 100)), id]); } catch (e) {}
    return {ok: true, id: id, key: String(row[1]), file: String(row[2]), free: true};
  }
  const ps = passesFor(phoneOf(b.phone), exam, b.device, b.email, false);
  if (!ps.ok) return ps;
  if (!ps.passes.mock) return {ok: false, error: 'This mock needs the ' + (MOCKS[exam] ? MOCKS[exam].name : 'mock test') + ' pass.', need: 'mock'};
  return {ok: true, id: id, key: String(row[1]), file: String(row[2])};
}

// Run from the editor (Run ▶ checkSetup) to check the settings. Prints no secrets.
function checkSetup() {
  Logger.log('Spreadsheet: ' + (prop('SHEET_ID') ? book_().getName() : 'SHEET_ID MISSING'));
  ['INSTAMOJO_CLIENT_ID', 'INSTAMOJO_CLIENT_SECRET', 'INSTAMOJO_SALT'].forEach(k => Logger.log(k + ': ' + (prop(k) ? 'set' : 'MISSING')));
  Logger.log('Web app URL: ' + ScriptApp.getService().getUrl());
}
