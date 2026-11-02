// Invite friends, earn free days (payments script 'ref' / 'refjoin' and the reward on a friend's first purchase):   node test/referral_test.js
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const SRC = fs.readFileSync(path.join(__dirname, '..', 'tools', 'payments', 'Code.gs'), 'utf8');
const ymd = d => new Date(d.getTime() + 5.5 * 3600e3).toISOString().slice(0, 10);
const plus = n => { const t = new Date(ymd(new Date()) + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + n); return t.toISOString().slice(0, 10); };
function makeEnv() {
  const sheets = {};
  const book = {getName: () => 'x', getSheetByName: n => sheets[n] || null, insertSheet: n => (sheets[n] = makeSheet())};
  function makeSheet() {
    const rows = [];
    return {rows, appendRow: r => rows.push(r.slice()), setFrozenRows: () => {},
      getDataRange: () => ({getValues: () => rows.map(r => r.slice())}),
      getRange: (r, c) => ({setValue: v => { rows[r - 1][c - 1] = v; }, setValues: vs => { vs[0].forEach((v, k) => { rows[r - 1][c - 1 + k] = v; }); }})};
  }
  const props = {SHEET_ID: 'x', INSTAMOJO_CLIENT_ID: 'id', INSTAMOJO_CLIENT_SECRET: 'sec', INSTAMOJO_SALT: 'salt', GOOGLE_CLIENT_ID: 'gid.apps'};
  const im = {payments: {}, requests: {}}, tokens = {};
  const env = {
    SpreadsheetApp: {openById: () => book},
    PropertiesService: {getScriptProperties: () => ({getProperty: k => props[k] || null})},
    LockService: {getScriptLock: () => ({waitLock: () => {}, releaseLock: () => {}})},
    CacheService: {getScriptCache: () => ({get: () => 'tok', put: () => {}})},
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
      const u = url.replace('https://api.instamojo.com', ''), id = decodeURIComponent(u.split('/')[3] || '');
      const body = u.startsWith('/v2/payments/') ? (im.payments[id] || {}) : u.startsWith('/v2/payment_requests/') ? (im.requests[id] || {}) : {access_token: 'tok', expires_in: 3600};
      return {getResponseCode: () => 200, getContentText: () => JSON.stringify(body)};
    }},
  };
  const names = Object.keys(env);
  const api = new Function(...names, SRC + '\nreturn {doPost};')(...names.map(n => env[n]));
  const call = b => JSON.parse(api.doPost({postData: {contents: JSON.stringify(Object.assign({exam: 'appsc-group-2'}, b))}, parameter: {}}).t);
  const gtok = (email, name) => { const k = 'cred-' + email + Math.random(); tokens[k] = {aud: 'gid.apps', iss: 'https://accounts.google.com', email, email_verified: 'true', name, sub: 's-' + email, exp: String(Math.floor(Date.now() / 1000) + 600)}; return k; };
  // a friend pays: a payment request row + Instamojo says it is completed, then the student comes back (verify)
  const pay = (phone, email, rid, pid) => {
    E0(sheets).requests.rows.push([new Date(), rid, phone, 'all', 'pyq', 45, 'Friend', email, 'created']);
    im.requests[rid] = {status: 'Completed', amount: '45.00'}; im.payments[pid] = {status: true, payment_request: 'https://x/' + rid + '/'};
    return call({action: 'verify', request: rid, payment: pid, device: 'dev-' + phone});
  };
  return {call, sheets, im, gtok, pay};
}
function E0(sheets) { if (!sheets.requests) sheets.requests = {rows: [['time']]}; return sheets; }
let fails = 0;
const ok = (c, m) => { if (!c) { fails++; console.log('FAIL', m); } else console.log('ok  ', m); };
const A = {phone: '9000000001', email: 'anil.student@gmail.com'};

{ // a student without a pass invites friends
  const E = makeEnv();
  E.call({action: 'passes', phone: '9999999999', email: 'z@z.com'});   // makes the tabs
  ok(!E.call({action: 'ref', phone: '123', email: A.email}).ok, 'no code without a valid phone');
  const r = E.call({action: 'ref', phone: A.phone, email: A.email});
  ok(r.ok && /^[A-HJ-NP-Z]{6}$/.test(r.code) && r.joined === 0 && r.left === 10, 'first ref call makes a 6-letter code: ' + r.code);
  ok(E.call({action: 'ref', phone: A.phone, email: 'OTHER@x.com'}).code === r.code, 'same phone, same code');
  const j = E.call({action: 'refjoin', code: r.code.toLowerCase(), phone: '9100000001', email: 'f1@gmail.com', name: 'Friend One', device: 'df1'});
  ok(j.ok && j.status === 'ok', 'a new friend registering through the link is rewarded');
  let p = E.call({action: 'passes', phone: A.phone, email: A.email}).passes;
  ok(p.bonus === plus(3) && !p.paid && p.mock === plus(3), 'sender gets 3 free days (bonus, not paid; mocks open): ' + JSON.stringify(p));
  ok(E.call({action: 'refjoin', code: r.code, phone: '9100000001', email: 'f1@gmail.com', device: 'df1'}).status === 'already', 'the same friend twice: no second reward');
  ok(E.call({action: 'refjoin', code: r.code, phone: A.phone, email: 'new@x.com', device: 'dself'}).status === 'self', 'own phone: self');
  ok(E.call({action: 'refjoin', code: r.code, phone: '9100000002', email: A.email, device: 'dself2'}).status === 'self', 'own email: self');
  ok(E.call({action: 'refjoin', code: r.code, phone: '9100000003', email: 'f3@gmail.com', device: 'df1'}).status === 'device', 'a device that already brought a referral: no reward');
  E.sheets.passes.rows.push([new Date(), '9100000004', 'all', 'pyq', '2027-10-30', 'MOJO1', 'req', 45, 'webhook', 'f4@gmail.com']);
  ok(E.call({action: 'refjoin', code: r.code, phone: '9100000004', email: 'x4@gmail.com', device: 'df4'}).status === 'known', 'a phone that already paid is not a new student');
  ok(!E.call({action: 'refjoin', code: 'ZZZZZZ', phone: '9100000005', email: 'f5@gmail.com', device: 'df5'}).ok, 'unknown code refused');
  const j2 = E.call({action: 'refjoin', code: r.code, phone: '9100000006', email: 'f6@gmail.com', device: 'df6'});
  p = E.call({action: 'passes', phone: A.phone, email: A.email}).passes;
  ok(j2.status === 'ok' && p.bonus === plus(6), 'a second friend adds 3 more days: ' + p.bonus);
  // the explanations key opens with free days; a study book does not
  E.sheets.keys = E.sheets.keys || null; E.call({action: 'mock', id: 'bk-ex-appsc-group-2', phone: A.phone, email: A.email});
  E.sheets.keys.rows.push(['bk-ex-appsc-group-2', 'KEY', 'ex.bin', '2026-01-01'], ['bk-g2-book', 'KEY2', 'b.bin', '2026-01-01']);
  ok(E.call({action: 'mock', id: 'bk-ex-appsc-group-2', phone: A.phone, email: A.email, device: 'da'}).key === 'KEY', 'free days open the explanations');
  const bk = E.call({action: 'mock', id: 'bk-g2-book', phone: A.phone, email: A.email, device: 'da'});
  ok(!bk.ok && bk.need === 'pyq', 'free days do not open a PDF/book download');
  // friend 1 buys the pass: +30 days for the sender, once
  const passRows = E.sheets.passes.rows.length;
  const v = E.pay('9100000001', 'f1@gmail.com', 'req-f1', 'MOJOF1');
  ok(v.ok && v.passes.paid, 'friend 1 bought the pass');
  p = E.call({action: 'passes', phone: A.phone, email: A.email}).passes;
  ok(p.bonus === plus(36), 'friend 1 buying adds 30 days: ' + p.bonus);
  E.pay('9100000001', 'f1@gmail.com', 'req-f1', 'MOJOF1');   // the webhook / verify again: same payment
  ok(E.call({action: 'passes', phone: A.phone, email: A.email}).passes.bonus === plus(36), 'the same payment twice: no second reward');
  ok(E.sheets.passes.rows.length === passRows + 1, 'rewards never go into the passes tab (Payments dashboard stays real)');
  E.pay('9100000002', A.email, 'req-s', 'MOJOS');   // the "self" friend buys: nothing
  ok(E.call({action: 'passes', phone: A.phone, email: A.email}).passes.bonus === plus(36), 'self referral buying: no reward');
  E.pay('9100000003', 'f3@gmail.com', 'req-d', 'MOJOD');   // the "device" friend buys: nothing
  ok(E.call({action: 'passes', phone: A.phone, email: A.email}).passes.bonus === plus(36), 'a known device buying: no reward');
  const s = E.call({action: 'ref', phone: A.phone, email: A.email});
  ok(s.joined === 2 && s.bought === 1 && s.days === 36 && s.left === 8, 'stats: ' + JSON.stringify(s));
}
{ // cap: 10 rewarded friends, then joins are recorded without days (a later purchase still counts)
  const E = makeEnv();
  const r = E.call({action: 'ref', phone: A.phone, email: A.email});
  for (let k = 0; k < 10; k++) E.call({action: 'refjoin', code: r.code, phone: '92000000' + String(k).padStart(2, '0'), email: 'c' + k + '@g.com', device: 'dc' + k});
  const c = E.call({action: 'refjoin', code: r.code, phone: '9300000000', email: 'c11@g.com', device: 'dc11'});
  ok(c.status === 'cap', '11th friend: cap');
  let p = E.call({action: 'passes', phone: A.phone, email: A.email}).passes;
  ok(p.bonus === plus(30), '10 friends = 30 free days: ' + p.bonus);
  E.pay('9300000000', 'c11@g.com', 'req-c11', 'MOJOC11');
  p = E.call({action: 'passes', phone: A.phone, email: A.email}).passes;
  ok(p.bonus === plus(60), 'a capped friend who buys still gives 30 days: ' + p.bonus);
}
{ // a sender with a paid pass: days are added to the end of it ('full': downloads too)
  const E = makeEnv();
  E.call({action: 'passes', phone: '9999999999', email: 'z@z.com'});
  E.sheets.passes.rows.push([new Date(), A.phone, 'all', 'pyq', '2027-10-30', 'MOJOA', 'req', 45, 'webhook', A.email]);
  const r = E.call({action: 'ref', phone: A.phone, email: A.email});
  E.call({action: 'refjoin', code: r.code, phone: '9400000001', email: 'p1@g.com', device: 'dp1'});
  const p = E.call({action: 'passes', phone: A.phone, email: A.email}).passes;
  ok(p.paid && p.pyq === '2027-11-02' && !p.bonus, 'paid sender: pass extended to 2027-11-02: ' + JSON.stringify(p));
}
{ // Google accounts: the sender asks with a session; a friend who logs in with Google and adds a phone is new
  const E = makeEnv();
  const s = E.call({action: 'glogin', credential: E.gtok('sender@gmail.com', 'S'), device: 'gs'});
  ok(!E.call({action: 'ref', session: s.session}).ok, 'account without a phone: add it first');
  E.call({action: 'setphone', session: s.session, phone: '9500000001', name: 'S', district: 'Guntur'});
  const r = E.call({action: 'ref', session: s.session});
  ok(r.ok && r.code, 'account with a phone gets a code');
  const f = E.call({action: 'glogin', credential: E.gtok('friend@gmail.com', 'F'), device: 'gf'});
  E.call({action: 'setphone', session: f.session, phone: '9500000002', name: 'F', district: 'Kurnool'});
  ok(E.call({action: 'refjoin', session: f.session, code: r.code, device: 'gf'}).status === 'ok', 'a brand-new Google account is a new student');
  ok(E.call({action: 'passes', session: s.session}).passes.bonus === plus(3), 'the sender sees the days through the session');
  const o = E.call({action: 'glogin', credential: E.gtok('sender@gmail.com', 'S'), device: 'gs2'});
  ok(E.call({action: 'refjoin', session: o.session, code: r.code, device: 'gs2'}).status === 'self', 'the sender on another device: self');
}
console.log(fails ? `\nREFERRAL TEST: ${fails} FAILED` : '\nREFERRAL TEST: all passed');
process.exit(fails ? 1 : 0);
