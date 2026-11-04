// Student accounts in the payments script (Google sign-in, sessions, devices, linking a payment):   node test/accounts_test.js
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const SRC = fs.readFileSync(path.join(__dirname, '..', 'tools', 'payments', 'Code.gs'), 'utf8');
function makeEnv() {
  const sheets = {};
  const book = {getName: () => 'x', getSheetByName: n => sheets[n] || null, insertSheet: n => (sheets[n] = makeSheet())};
  function makeSheet() {
    const rows = [];
    return {rows, appendRow: r => rows.push(r.slice()), setFrozenRows: () => {},
      getDataRange: () => ({getValues: () => rows.map(r => r.slice())}),
      getRange: (r, c, nr, nc) => ({setValue: v => { rows[r - 1][c - 1] = v; }, setValues: vs => { vs[0].forEach((v, k) => { rows[r - 1][c - 1 + k] = v; }); }})};
  }
  const props = {SHEET_ID: 'x', INSTAMOJO_CLIENT_ID: 'id', INSTAMOJO_CLIENT_SECRET: 'sec', INSTAMOJO_SALT: 'salt', GOOGLE_CLIENT_ID: 'gid.apps'};
  const im = {payments: {}}, tokens = {}, cache = new Map(), mail = {quota: 100, sent: [], fail: false};
  const ymd = d => new Date(d.getTime() + 5.5 * 3600e3).toISOString().slice(0, 10);
  const env = {
    SpreadsheetApp: {openById: () => book},
    PropertiesService: {getScriptProperties: () => ({getProperty: k => props[k] || null})},
    LockService: {getScriptLock: () => ({waitLock: () => {}, releaseLock: () => {}})},
    CacheService: {getScriptCache: () => ({get: k => k === 'im_token' ? 'tok' : (cache.has(k) ? cache.get(k) : null), put: (k, v) => { cache.set(k, v); }, remove: k => { cache.delete(k); }})},
    MailApp: {getRemainingDailyQuota: () => mail.quota, sendEmail: o => { if (mail.fail) throw new Error('Invalid email: ' + o.to); mail.sent.push(o); }},
    ContentService: {createTextOutput: t => ({t, setMimeType() { return this; }}), MimeType: {JSON: 'json'}},
    ScriptApp: {getService: () => ({getUrl: () => 'https://script.test/exec'})},
    Logger: {log: () => {}},
    Utilities: {formatDate: d => ymd(d), getUuid: () => crypto.randomUUID(),
      computeDigest: (alg, t) => Array.from(crypto.createHash('sha256').update(t, 'utf8').digest()).map(b => b > 127 ? b - 256 : b),
      DigestAlgorithm: {SHA_256: 'sha256'}, computeHmacSignature: () => [], MacAlgorithm: {}, Charset: {}},
    UrlFetchApp: {fetch: (url) => {
      if (url.startsWith('https://oauth2.googleapis.com/tokeninfo')) {
        const t = tokens[decodeURIComponent(url.split('id_token=')[1])];
        return {getResponseCode: () => t ? 200 : 400, getContentText: () => JSON.stringify(t || {error: 'invalid'})};
      }
      const u = url.replace('https://api.instamojo.com', '');
      const body = u.startsWith('/v2/payments/') ? (im.payments[decodeURIComponent(u.split('/')[3])] || {}) : {access_token: 'tok', expires_in: 3600};
      return {getResponseCode: () => 200, getContentText: () => JSON.stringify(body)};
    }},
  };
  const names = Object.keys(env);
  const api = new Function(...names, SRC + '\nreturn {doPost};')(...names.map(n => env[n]));
  const call = b => JSON.parse(api.doPost({postData: {contents: JSON.stringify(Object.assign({exam: 'appsc-group-2'}, b))}, parameter: {}}).t);
  const gtok = (email, name) => { const k = 'cred-' + email + Math.random(); tokens[k] = {aud: 'gid.apps', iss: 'https://accounts.google.com', email, email_verified: 'true', name, sub: 's-' + email, exp: String(Math.floor(Date.now() / 1000) + 600)}; return k; };
  const codeOf = o => (o.subject.match(/^(\d{6}) /) || [])[1];
  return {call, sheets, im, gtok, mail, cache, codeOf};
}
let fails = 0;
const ok = (c, m) => { if (!c) { fails++; console.log('FAIL', m); } else console.log('ok  ', m); };
const passRow = (phone, email, pid) => [new Date(), phone, 'all', 'pyq', '2027-10-30', pid, 'req', 45, 'webhook', email];

{ // new student: Google, phone, no pass
  const E = makeEnv();
  ok(!E.call({action: 'glogin', credential: 'bad'}).ok, 'a bad Google token is refused');
  const r = E.call({action: 'glogin', credential: E.gtok('ravi@gmail.com', 'Ravi K'), device: 'd1', agent: 'Mozilla (Linux; Android 14) Chrome/130'});
  ok(r.ok && /^[0-9a-f]{64}$/.test(r.session) && r.account.email === 'ravi@gmail.com' && !r.account.phone, 'Google login gives a 12-month session and an account without a phone');
  const p = E.call({action: 'setphone', session: r.session, phone: '98765 43210', name: 'Ravi K', district: 'Guntur'});
  ok(p.ok && p.account.phone === '9876543210' && p.account.district === 'Guntur', 'phone and district linked');
  const m = E.call({action: 'me', session: r.session});
  ok(m.ok && m.devices.length === 1 && m.devices[0].current && m.devices[0].name === 'Android phone · Chrome', 'me lists this device');
  ok(!E.call({action: 'passes', session: 'f'.repeat(64)}).ok, 'an unknown session must log in again');
  const r2 = E.call({action: 'glogin', credential: E.gtok('ravi@gmail.com', 'Ravi K'), device: 'd2'});
  ok(r2.account.phone === '9876543210', 'second device: the account already has its phone');
}
{ // existing pass bought with phone + another email: needs the payment ID; same email links straight away
  const E = makeEnv();
  E.call({action: 'glogin', credential: E.gtok('x@gmail.com', 'X')});   // creates the tabs
  E.sheets.passes = E.sheets.passes || null;
  const r = E.call({action: 'glogin', credential: E.gtok('sai@gmail.com', 'Sai'), device: 'd1'});
  E.call({action: 'passes', phone: '9000000001', email: 'a@b.com'});   // make sure the passes tab exists
  E.sheets.passes.rows.push(passRow('9000000001', 'other@gmail.com', 'MOJO6b02405Q38493789'));
  const n = E.call({action: 'setphone', session: r.session, phone: '9000000001'});
  ok(!n.ok && n.needPayment, 'a number with a pass bought by another email asks for the payment ID');
  const y = E.call({action: 'setphone', session: r.session, phone: '9000000001', payment: 'MOJO6b02405Q38493789'});
  ok(y.ok && y.passes.paid && y.passes.pyq === '2027-10-30', 'with the payment ID the number and its pass are linked');
  ok(E.call({action: 'passes', session: r.session, device: 'dz'}).passes.paid, 'passes by session work');
  const k = E.call({action: 'mock', session: r.session, id: 'bk-ex-appsc-group-2'});
  ok(k.ok === false && /not ready/.test(k.error), 'book keys go through the account (no key row here, so "not ready")');
  const o = E.call({action: 'glogin', credential: E.gtok('thief@gmail.com', 'T')});
  ok(!E.call({action: 'setphone', session: o.session, phone: '9000000001', payment: 'MOJO6b02405Q38493789'}).ok, 'a number already linked to another account is refused');
  const s2 = E.call({action: 'glogin', credential: E.gtok('paid@gmail.com', 'P')});
  E.sheets.passes.rows.push(passRow('9000000002', 'paid@gmail.com', 'MOJO2'));
  ok(E.call({action: 'setphone', session: s2.session, phone: '9000000002'}).passes.paid, 'same Google email as the payment: linked without the ID');
  const s3 = E.call({action: 'glogin', credential: E.gtok('paid2@gmail.com', 'P2')});
  E.sheets.passes.rows.push(passRow('9111111111', 'paid2@gmail.com', 'MOJO3'));
  ok(E.call({action: 'me', session: s3.session}).passes.paid, 'a pass bought with the Google email shows even before a phone is added');
}
{ // devices: at most 3; logging out a device
  const E = makeEnv();
  const ss = [1, 2, 3, 4].map(i => E.call({action: 'glogin', credential: E.gtok('d@gmail.com', 'D'), device: 'd' + i}).session);
  ok(!E.call({action: 'me', session: ss[0]}).ok && E.call({action: 'me', session: ss[3]}).ok, 'a 4th login logs out the oldest device');
  const m = E.call({action: 'me', session: ss[3]});
  ok(m.devices.length === 3, 'three devices listed');
  const other = m.devices.find(d => !d.current);
  E.call({action: 'logout', session: ss[3], target: other.id});
  ok(E.call({action: 'me', session: ss[3]}).devices.length === 2, 'logging out another device');
  E.call({action: 'logout', session: ss[3]});
  ok(!E.call({action: 'me', session: ss[3]}).ok, 'logging out this device');
}
{ // claim by payment ID (phone + email students too)
  const E = makeEnv();
  E.call({action: 'passes', phone: '9000000001', email: 'a@b.com'});
  E.sheets.passes.rows.push(passRow('9393939393', 'friend@gmail.com', 'MOJO6b01G05Q80872432'));
  ok(!E.call({action: 'claim', phone: '9959346357', email: 'stud@gmail.com', payment: 'abc'}).ok, 'a wrong payment ID format is refused');
  const c = E.call({action: 'claim', phone: '9959346357', email: 'stud@gmail.com', payment: 'mojo6b01g05q80872432', device: 'd1'});
  ok(c.ok && c.passes.paid, 'a payment made with another number is linked to this number');
  ok(!E.call({action: 'claim', phone: '9888888888', email: 'z@gmail.com', payment: 'MOJO6b01G05Q80872432'}).ok, 'the same payment cannot be linked to a third number');
  E.im.payments.MOJO9X9X9X9X9X = {status: true, amount: '45.00', payment_request: 'https://x/req1/'};
  ok(E.call({action: 'claim', phone: '9777777777', email: 'w@gmail.com', payment: 'MOJO9X9X9X9X9X'}).passes.paid, 'a payment the webhook missed is checked with Instamojo and recorded');
  ok(!E.call({action: 'claim', phone: '9777777770', email: 'w@gmail.com', payment: 'MOJO1111111111'}).ok, 'an unknown payment is refused');
}
{ // old phone + email requests still work as before
  const E = makeEnv();
  E.call({action: 'passes', phone: '9000000001', email: 'a@b.com'});
  E.sheets.passes.rows.push(passRow('9000000005', 'e@gmail.com', 'MOJO5'));
  ok(E.call({action: 'passes', phone: '9000000005', email: 'e@gmail.com', device: 'd1'}).passes.paid, 'phone + email still opens the pass');
  ok(!E.call({action: 'passes', phone: '9000000005', email: 'other@gmail.com', device: 'd1'}).passes.paid, 'phone with another email does not');
}
{ // email code login for students without Google (Anil, 4 Nov 2026: "OTP login for first timers")
  const E = makeEnv();
  ok(!E.call({action: 'otpsend', email: 'not-an-email'}).ok, 'a wrong email address is refused');
  const s = E.call({action: 'otpsend', email: ' Ravi.K@Gmail.com '});
  ok(s.ok && E.mail.sent.length === 1 && E.mail.sent[0].to === 'ravi.k@gmail.com' && E.mail.sent[0].name === 'Learn with Anil', 'a code is emailed to the student');
  const code = E.codeOf(E.mail.sent[0]);
  ok(/^\d{6}$/.test(code) && E.mail.sent[0].body.includes(code) && E.mail.sent[0].htmlBody.includes(code), 'the email holds the 6-digit code');
  ok(![...E.cache.values()].some(v => v.includes(code)), 'only a hash of the code is kept');
  const again = E.call({action: 'otpsend', email: 'ravi.k@gmail.com'});
  ok(!again.ok && again.wait > 0 && E.mail.sent.length === 1, 'a second code within 45 seconds is refused');
  const wrong = code === '000000' ? '111111' : '000000';
  const w = E.call({action: 'otpverify', email: 'ravi.k@gmail.com', code: wrong});
  ok(!w.ok && !w.expired && !w.session, 'a wrong code does not log in');
  ok(!E.call({action: 'otpverify', email: 'other@gmail.com', code}).ok, 'the code works only for its own email');
  const v = E.call({action: 'otpverify', email: 'RAVI.K@gmail.com', code: code.slice(0, 3) + ' ' + code.slice(3), name: 'Ravi  K', device: 'd1', agent: 'Mozilla (Linux; Android 14) Chrome/130'});
  ok(v.ok && /^[0-9a-f]{64}$/.test(v.session) && v.account.email === 'ravi.k@gmail.com' && v.account.name === 'Ravi K', 'the right code logs in with a 12-month session');
  const acc = E.sheets.accounts.rows.find(r => r[1] === 'ravi.k@gmail.com');
  ok(acc && acc[5] === 'email-otp', 'the account is marked as an email-code account');
  ok(!E.call({action: 'otpverify', email: 'ravi.k@gmail.com', code}).ok, 'a used code does not work again');
  const p = E.call({action: 'setphone', session: v.session, phone: '9876543210', name: 'Ravi K', district: 'Guntur'});
  ok(p.ok && p.account.phone === '9876543210', 'the phone is linked to the email-code account');
  ok(E.call({action: 'me', session: v.session}).devices.length === 1, 'My Account works for an email-code login');
  // too many wrong tries end the code
  E.cache.clear();
  E.call({action: 'otpsend', email: 'sai@gmail.com'});
  const c2 = E.codeOf(E.mail.sent[E.mail.sent.length - 1]), bad = c2 === '123456' ? '654321' : '123456';
  let last = null; for (let i = 0; i < 5; i++) last = E.call({action: 'otpverify', email: 'sai@gmail.com', code: bad});
  ok(last.expired && !E.call({action: 'otpverify', email: 'sai@gmail.com', code: c2}).ok, 'five wrong tries end the code');
  // an expired code
  E.call({action: 'otpsend', email: 'old@gmail.com'});
  const c3 = E.codeOf(E.mail.sent[E.mail.sent.length - 1]), key = [...E.cache.keys()].find(k => !k.endsWith('-n') && JSON.parse(E.cache.get(k)).h && !JSON.parse(E.cache.get(k)).tries && k !== 'im_token' && E.cache.get(k).includes('exp'));
  for (const k of E.cache.keys()) { const o = JSON.parse(E.cache.get(k)); if (o && o.exp) { o.exp = Date.now() - 1000; E.cache.set(k, JSON.stringify(o)); } }
  ok(key && E.call({action: 'otpverify', email: 'old@gmail.com', code: c3}).expired, 'a code older than 10 minutes has expired');
  // five codes per email, then wait
  E.cache.clear();
  let n = 0; for (let i = 0; i < 7; i++) { for (const k of E.cache.keys()) if (k.endsWith('-n')) { const o = JSON.parse(E.cache.get(k)); o.t = 0; E.cache.set(k, JSON.stringify(o)); } if (E.call({action: 'otpsend', email: 'many@gmail.com'}).ok) n++; }
  ok(n === 5, 'at most five codes per email in six hours');
  // the day's emails used up, or the address bounces
  E.mail.quota = 2;
  const q = E.call({action: 'otpsend', email: 'late@gmail.com'});
  ok(!q.ok && q.skip, 'when the daily emails run out the site is told to register without a code');
  E.mail.quota = 50; E.mail.fail = true;
  const f = E.call({action: 'otpsend', email: 'bounce@nowhere.zz'});
  ok(!f.ok && !f.skip && /Could not send/.test(f.error), 'a send error is reported');
  // an existing Google account logs in with an email code too (same account)
  const E2 = makeEnv();
  const g = E2.call({action: 'glogin', credential: E2.gtok('lak@gmail.com', 'Lakshmi')});
  E2.call({action: 'setphone', session: g.session, phone: '9000000009', name: 'Lakshmi', district: 'Nellore'});
  E2.call({action: 'otpsend', email: 'lak@gmail.com'});
  const v2 = E2.call({action: 'otpverify', email: 'lak@gmail.com', code: E2.codeOf(E2.mail.sent[0]), name: 'L'});
  ok(v2.ok && v2.account.phone === '9000000009' && v2.account.name === 'Lakshmi' && E2.sheets.accounts.rows.length === 2, 'an email code opens the same account as Google login');
}
console.log(fails ? fails + ' FAILED' : 'ALL OK'); process.exit(fails ? 1 : 0);
