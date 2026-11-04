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
console.log(fails ? fails + ' FAILED' : 'ALL OK'); process.exit(fails ? 1 : 0);
