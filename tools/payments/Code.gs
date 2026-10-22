/** @OnlyCurrentDoc */
/**
 * Learn with Anil — passes and payments (Google Apps Script, bound to the "Learn with Anil – Passes" spreadsheet).
 *
 * What it does
 *  - buy:     creates an Instamojo payment request for a pass (price fixed here, never taken from the browser)
 *             and returns Instamojo's checkout link.
 *  - verify:  after Instamojo sends the student back to learnwithanil.in, asks Instamojo whether that payment
 *             request was paid and, if so, records the pass.
 *  - webhook: Instamojo also calls this script when a payment succeeds (checked with the private salt), so a pass
 *             is recorded even if the student closes the page.
 *  - passes:  which passes a registered phone number has for an exam.
 *  - mock:    the key of a released Mission Khaki mock (its encrypted file is on the website), only for a valid mock pass.
 *
 * Secrets are NOT in this file. Anil adds them himself under Project Settings → Script properties:
 *   INSTAMOJO_CLIENT_ID, INSTAMOJO_CLIENT_SECRET   (Instamojo dashboard → API & Plugins; "API v2")
 *   INSTAMOJO_SALT                                 (Instamojo private salt, used to check webhooks)
 *   INSTAMOJO_API (optional)                       defaults to https://api.instamojo.com
 */

const SITE = 'https://learnwithanil.in/';
const PYQ_PRICE = 45;
const EXAMS = {   // exam id: name, last day a pass is valid (null = 12 months), mock pack price (null = not on sale)
  'appsc-group-2':        {name: 'APPSC Group 2', until: null, mock: null},
  'appsc-group-1':        {name: 'APPSC Group 1', until: '2027-01-25', mock: null},
  'upsc-capf':            {name: 'UPSC CAPF AC', until: null, mock: null},
  'ts-police-si':         {name: 'TS Police SI', until: '2026-11-30', mock: {price: 150, name: 'Mission Khaki TS SI Mocks'}},
  'ts-police-constable':  {name: 'TS Police Constable', until: '2026-12-21', mock: null},
  'tgpsc-hmwssb-manager': {name: 'TGPSC HMWSSB Manager', until: null, mock: null},
};
// Mock keys live in the 'keys' tab of this spreadsheet: mock_id | key (base64) | file | opens (yyyy-mm-dd, IST).
const MAX_DEVICES = 3;   // one pass, at most this many phones/computers

// ---------------------------------------------------------------------------------------------------------------
function doGet() { return out({ok: true, service: 'Learn with Anil passes'}); }

function doPost(e) {
  try {
    if (e && e.parameter && e.parameter.mac) return webhook(e.parameter);   // Instamojo → form-encoded, signed
    const b = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const exam = String(b.exam || '');
    if (!EXAMS[exam]) return out({ok: false, error: 'Unknown exam.'});
    switch (b.action) {
      case 'buy': return out(buy(b, exam));
      case 'verify': return out(verify(b, exam));
      case 'passes': return out(passesFor(phoneOf(b.phone), exam, b.device, b.email));
      case 'mock': return out(mock(b, exam));
      default: return out({ok: false, error: 'Unknown action.'});
    }
  } catch (err) {
    log_('error', String(err && err.stack || err));
    return out({ok: false, error: 'Something went wrong. Please try again in a minute.'});
  }
}

function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function phoneOf(p) { const d = String(p || '').replace(/\D/g, '').slice(-10); return /^[6-9]\d{9}$/.test(d) ? d : ''; }
function prop(k) { return PropertiesService.getScriptProperties().getProperty(k) || ''; }
function sheet(name, header) {
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(header); sh.setFrozenRows(1); }
  return sh;
}
function log_(kind, text) { sheet('log', ['time', 'kind', 'text']).appendRow([new Date(), kind, String(text).slice(0, 4000)]); }
function today_() { return Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyyy-MM-dd'); }
function untilFor(exam) {
  const u = EXAMS[exam].until;
  if (u) return u;
  const d = new Date(); d.setFullYear(d.getFullYear() + 1);
  return Utilities.formatDate(d, 'Asia/Kolkata', 'yyyy-MM-dd');
}

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
function buy(b, exam) {
  const kind = b.kind === 'mock' ? 'mock' : 'pyq';
  const E = EXAMS[exam];
  if (kind === 'mock' && !E.mock) return {ok: false, error: 'This mock test pack is not on sale yet.'};
  const phone = phoneOf(b.phone);
  if (!phone) return {ok: false, error: 'Please register with a valid 10-digit mobile number first.'};
  const amount = kind === 'mock' ? E.mock.price : PYQ_PRICE;
  const purpose = (kind === 'mock' ? E.mock.name : E.name + ' PYQ Pass').slice(0, 30);   // Instamojo allows 30 characters
  let back = String(b.back || '');
  if (back.indexOf(SITE) !== 0) back = SITE;
  const pr = im_('post', '/v2/payment_requests/', {
    purpose: purpose, amount: String(amount), buyer_name: String(b.name || '').slice(0, 100),
    email: String(b.email || '').slice(0, 100), phone: phone, redirect_url: back,
    webhook: ScriptApp.getService().getUrl(), send_email: 'false', send_sms: 'false', allow_repeated_payments: 'false'});
  sheet('requests', ['time', 'request_id', 'phone', 'exam', 'kind', 'amount', 'name', 'email', 'status'])
    .appendRow([new Date(), pr.id, phone, exam, kind, amount, String(b.name || ''), String(b.email || ''), 'created']);
  return {ok: true, url: pr.longurl};
}

function requestRow_(id) {
  const sh = sheet('requests', ['time', 'request_id', 'phone', 'exam', 'kind', 'amount', 'name', 'email', 'status']);
  const v = sh.getDataRange().getValues();
  for (let i = v.length - 1; i >= 1; i--) if (String(v[i][1]) === String(id)) return {sh: sh, row: i + 1, phone: String(v[i][2]), exam: v[i][3], kind: v[i][4], amount: v[i][5], email: String(v[i][7] || '')};
  return null;
}

function grant_(req, paymentId, amount, source) {
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const sh = sheet('passes', PASS_HEAD);
    const v = sh.getDataRange().getValues();
    for (let i = 1; i < v.length; i++) if (paymentId && String(v[i][5]) === String(paymentId)) return;   // already recorded
    sh.appendRow([new Date(), req.phone, req.exam, req.kind, untilFor(req.exam), paymentId || '', req.request || '', amount || req.amount, source, req.email.toLowerCase()]);
    if (req.sh) req.sh.getRange(req.row, 9).setValue('paid');
  } finally { lock.releaseLock(); }
}

function verify(b, exam) {
  const id = String(b.request || '');
  const req = requestRow_(id);
  if (!req || req.exam !== exam) return {ok: false, error: 'Payment not found.'};
  const pr = im_('get', '/v2/payment_requests/' + encodeURIComponent(id) + '/');
  const paid = String(pr.status || '').toLowerCase() === 'completed';
  if (!paid) return {ok: false, error: 'The payment is not complete yet. If money was taken, it will show here within a few minutes.'};
  let pid = String(b.payment || '');
  if (pid) {   // make sure that payment really belongs to this request and was credited
    const p = im_('get', '/v2/payments/' + encodeURIComponent(pid) + '/');
    if (!p.status || String(p.payment_request || '').indexOf(id) < 0) pid = '';
  }
  req.request = id;
  grant_(req, pid || ('req-' + id), pr.amount, 'verify');
  return passesFor(req.phone, exam, b.device, req.email);
}

function webhook(p) {
  const salt = prop('INSTAMOJO_SALT');
  const keys = Object.keys(p).filter(k => k !== 'mac').sort((a, b) => a.toLowerCase() < b.toLowerCase() ? -1 : 1);
  const msg = keys.map(k => p[k]).join('|');
  const mac = Utilities.computeHmacSignature(Utilities.MacAlgorithm.HMAC_SHA_1, msg, salt)
    .map(x => ('0' + (x & 0xff).toString(16)).slice(-2)).join('');
  if (!salt || mac !== String(p.mac)) { log_('webhook-bad-mac', JSON.stringify({payment_id: p.payment_id, request: p.payment_request_id})); return out({ok: false}); }
  if (String(p.status).toLowerCase() === 'credit') {
    const req = requestRow_(p.payment_request_id);
    if (req) { req.request = p.payment_request_id; grant_(req, p.payment_id, p.amount, 'webhook'); }
    else log_('webhook-unknown-request', p.payment_request_id);
  }
  return out({ok: true});
}

const PASS_HEAD = ['time', 'phone', 'exam', 'kind', 'until', 'payment_id', 'request_id', 'amount', 'source', 'email'];

function passesFor(phone, exam, device, email) {   // a pass needs the same phone AND email the student paid with
  email = String(email || '').trim().toLowerCase();
  if (!phone || !email) return {ok: true, passes: {}};
  const v = sheet('passes', PASS_HEAD).getDataRange().getValues();
  const res = {}, now = today_();
  for (let i = 1; i < v.length; i++) {
    if (String(v[i][1]) !== phone || v[i][2] !== exam) continue;
    if (String(v[i][9] || '').toLowerCase() !== email) continue;
    const u = v[i][4] instanceof Date ? Utilities.formatDate(v[i][4], 'Asia/Kolkata', 'yyyy-MM-dd') : String(v[i][4]);
    if (u < now) continue;
    const k = v[i][3];
    if (!res[k] || res[k] < u) res[k] = u;
  }
  if (Object.keys(res).length && device && !deviceOK_(phone, exam, String(device))) return {ok: false, error: 'This pass is already in use on ' + MAX_DEVICES + ' devices.', passes: {}};
  return {ok: true, passes: res};
}

function deviceOK_(phone, exam, device) {
  const sh = sheet('devices', ['time', 'phone', 'exam', 'device']);
  const v = sh.getDataRange().getValues();
  const seen = new Set();
  for (let i = 1; i < v.length; i++) if (String(v[i][1]) === phone && v[i][2] === exam) seen.add(String(v[i][3]));
  if (seen.has(device)) return true;
  if (seen.size >= MAX_DEVICES) return false;
  sh.appendRow([new Date(), phone, exam, device]);
  return true;
}

function mock(b, exam) {   // the key of a sealed mock (the encrypted file is on the website), only for a valid mock pass
  const id = String(b.id || '');
  const v = sheet('keys', ['mock_id', 'key', 'file', 'opens']).getDataRange().getValues();
  let row = null;
  for (let i = 1; i < v.length; i++) if (String(v[i][0]) === id) row = v[i];
  if (!row) return {ok: false, error: 'This mock is not ready yet.'};
  const opens = row[3] instanceof Date ? Utilities.formatDate(row[3], 'Asia/Kolkata', 'yyyy-MM-dd') : String(row[3]);
  if (opens > today_()) return {ok: false, error: 'This mock opens on ' + opens + '.'};
  const ps = passesFor(phoneOf(b.phone), exam, b.device, b.email);
  if (!ps.ok) return ps;
  if (!ps.passes.mock) return {ok: false, error: 'This mock needs the mock test pass.', need: 'mock'};
  return {ok: true, id: id, key: String(row[1]), file: String(row[2])};
}

// Run once from the editor (Run ▶ checkSetup) to approve the script and check the settings. Prints no secrets.
function checkSetup() {
  const ss = SpreadsheetApp.getActive();
  Logger.log('Spreadsheet: ' + (ss ? ss.getName() : 'NOT BOUND'));
  ['INSTAMOJO_CLIENT_ID', 'INSTAMOJO_CLIENT_SECRET', 'INSTAMOJO_SALT'].forEach(k => Logger.log(k + ': ' + (prop(k) ? 'set' : 'MISSING')));
  Logger.log('Web app URL: ' + ScriptApp.getService().getUrl());
}
