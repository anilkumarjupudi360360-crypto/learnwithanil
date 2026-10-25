// Runs the payments script (tools/payments/Code.gs) in Node against fake Google services and a fake Instamojo,
// to check the pass logic before a new version is deployed:   node test/code_gs_test.js
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const SRC = fs.readFileSync(path.join(__dirname, '..', 'tools', 'payments', 'Code.gs'), 'utf8');

function makeEnv() {
  const sheets = {};
  const book = {
    getName: () => 'Learn with Anil – Passes (private)',
    getSheetByName: n => sheets[n] || null,
    insertSheet: n => (sheets[n] = makeSheet()),
  };
  function makeSheet() {
    const rows = [];
    return {
      rows,
      appendRow: r => rows.push(r.slice()),
      setFrozenRows: () => {},
      getDataRange: () => ({getValues: () => rows.map(r => r.slice())}),
      getRange: (r, c) => ({setValue: v => { rows[r - 1][c - 1] = v; }}),
    };
  }
  const props = {SHEET_ID: 'x', INSTAMOJO_CLIENT_ID: 'id', INSTAMOJO_CLIENT_SECRET: 'sec', INSTAMOJO_SALT: 'salt'};
  const im = {requests: {}, payments: {}, n: 0};
  const ymd = d => new Date(d.getTime() + 5.5 * 3600e3).toISOString().slice(0, 10);
  const env = {
    SpreadsheetApp: {openById: () => book},
    PropertiesService: {getScriptProperties: () => ({getProperty: k => props[k] || null})},
    LockService: {getScriptLock: () => ({waitLock: () => {}, releaseLock: () => {}})},
    CacheService: {getScriptCache: () => ({get: () => 'tok', put: () => {}})},
    ContentService: {createTextOutput: t => ({t, setMimeType() { return this; }}), MimeType: {JSON: 'json'}},
    ScriptApp: {getService: () => ({getUrl: () => 'https://script.test/exec'})},
    Logger: {log: () => {}},
    Utilities: {
      formatDate: d => ymd(d),
      computeHmacSignature: (alg, msg, key) => Array.from(crypto.createHmac('sha1', key).update(msg, 'utf8').digest()),
      MacAlgorithm: {HMAC_SHA_1: 'sha1'}, Charset: {UTF_8: 'utf8'},
    },
    UrlFetchApp: {fetch: (url, opt) => {
      const u = url.replace('https://api.instamojo.com', '');
      let body = {};
      if (u === '/v2/payment_requests/' && opt.method === 'post') {
        const id = 'req' + (++im.n); im.requests[id] = {id, status: 'Pending', amount: opt.payload.amount, purpose: opt.payload.purpose};
        body = {id, longurl: 'https://imojo.test/' + id};
      } else if (u.startsWith('/v2/payment_requests/')) body = im.requests[decodeURIComponent(u.split('/')[3])];
      else if (u.startsWith('/v2/payments/')) body = im.payments[decodeURIComponent(u.split('/')[3])];
      return {getResponseCode: () => 200, getContentText: () => JSON.stringify(body)};
    }},
  };
  const names = Object.keys(env);
  const fn = new Function(...names, SRC + '\nreturn {doPost, passesFor, today_};');
  const api = fn(...names.map(n => env[n]));
  const call = b => JSON.parse(api.doPost({postData: {contents: JSON.stringify(b)}, parameter: {}}).t);
  const hook = p => {   // a signed Instamojo webhook
    const keys = Object.keys(p).sort((a, b) => a.toLowerCase() < b.toLowerCase() ? -1 : 1);
    const mac = crypto.createHmac('sha1', 'salt').update(keys.map(k => p[k]).join('|'), 'utf8').digest('hex');
    return JSON.parse(api.doPost({parameter: Object.assign({}, p, {mac}), postData: {type: 'text/plain', contents: ''}}).t);
  };
  return {api, call, hook, sheets, im};
}

let fails = 0;
const ok = (c, m) => { if (!c) { fails++; console.log('FAIL', m); } else console.log('ok  ', m); };
const S = {name: 'Ravi', phone: '9876543210', email: 'ravi@example.com', device: 'd1'};

// 1. combo: one payment, a mock pass for SI and for Constable
{
  const E = makeEnv();
  const r = E.call(Object.assign({action: 'buy', exam: 'ts-police-constable', kind: 'combo', back: 'https://learnwithanil.in/ts-police-constable/'}, S));
  ok(r.ok && r.url, 'combo buy gives a checkout link');
  const req = Object.values(E.im.requests)[0];
  ok(req.amount === '199' && req.purpose === 'Mission Khaki SI+PC Mocks', 'combo price 199 and name');
  const rq = E.sheets.requests.rows[1];
  ok(rq[3] === 'combo' && rq[4] === 'combo', 'request row exam/kind = combo');
  req.status = 'Completed'; E.im.payments.MOJO1 = {status: true, payment_request: 'https://x/' + req.id + '/'};
  ok(E.hook({payment_id: 'MOJO1', payment_request_id: req.id, status: 'Credit', amount: '199.00', buyer: S.email}).ok, 'webhook accepted');
  const p = E.sheets.passes.rows.slice(1);
  ok(p.length === 2 && p[0][2] === 'ts-police-si' && p[1][2] === 'ts-police-constable' && p.every(x => x[3] === 'mock'), 'two mock passes recorded');
  ok(p[0][4] === '2026-11-30' && p[1][4] === '2026-12-21', 'each pass valid till its exam');
  ok(p[0][7] === '199.00' && p[1][7] === 0, 'amount on the first row only');
  E.hook({payment_id: 'MOJO1', payment_request_id: req.id, status: 'Credit', amount: '199.00', buyer: S.email});
  ok(E.sheets.passes.rows.length === 3, 'a repeated webhook adds nothing');
  const v = E.call(Object.assign({action: 'verify', exam: 'ts-police-si', request: req.id, payment: 'MOJO1'}, S));
  ok(v.ok && v.passes.mock === '2026-11-30', 'verify from the SI page shows the SI mock pass');
  const v2 = E.call(Object.assign({action: 'verify', exam: 'ts-police-constable', request: req.id, payment: 'MOJO1'}, S));
  ok(v2.ok && v2.passes.mock === '2026-12-21', 'verify from the Constable page shows the Constable mock pass');
  ok(E.sheets.passes.rows.length === 3, 'verify after the webhook adds nothing');
  const s1 = E.call(Object.assign({action: 'passes', exam: 'ssc-cgl'}, S));
  ok(s1.ok && !s1.passes.mock, 'the combo does not open other exams');
  ok(!E.call(Object.assign({action: 'buy', exam: 'ssc-cgl', kind: 'combo'}, S)).ok, 'no combo on other exams');
}
// 2. the Constable pack alone, and the existing packs unchanged
{
  const E = makeEnv();
  E.call(Object.assign({action: 'buy', exam: 'ts-police-constable', kind: 'mock'}, S));
  E.call(Object.assign({action: 'buy', exam: 'ts-police-si', kind: 'mock'}, S));
  E.call(Object.assign({action: 'buy', exam: 'ssc-cgl', kind: 'mock'}, S));
  E.call(Object.assign({action: 'buy', exam: 'ts-police-si', kind: 'pyq'}, S));
  const a = Object.values(E.im.requests).map(r => r.amount + ' ' + r.purpose);
  ok(a.join(' | ') === '99 Mission Khaki TS PC Mocks | 150 Mission Khaki TS SI Mocks | 149 Mission CGL SSC Mocks | 45 PYQ Pass - All Exams (1 yr)', 'prices: ' + a.join(' | '));
  const req = Object.values(E.im.requests)[0]; req.status = 'Completed';
  E.hook({payment_id: 'MOJO2', payment_request_id: req.id, status: 'Credit', amount: '99.00'});
  const p = E.sheets.passes.rows.slice(1);
  ok(p.length === 1 && p[0][2] === 'ts-police-constable' && p[0][4] === '2026-12-21', 'Constable pass alone');
  ok(!E.call(Object.assign({action: 'passes', exam: 'ts-police-si'}, S)).passes.mock, 'Constable pass does not open SI mocks');
}
// 3. mock keys: free Mock 1, paid mocks need a pass
{
  const E = makeEnv();
  E.api.passesFor('0', 'x');   // create nothing
  const keys = E.sheets.keys || (E.sheets.keys = null);
  const book = E.call({action: 'passes', exam: 'ts-police-constable', phone: S.phone, email: S.email});   // creates the sheets lazily
  const ks = (E.sheets.keys = E.sheets.keys || null);
  // add a keys tab
  E.call({action: 'mock', exam: 'ts-police-constable', id: 'mk-pc-1', phone: S.phone, email: S.email});   // creates the tab
  E.sheets.keys.rows.push(['mk-pc-1', 'KEY1', 'mk-pc-1-abc.bin', '2026-10-25'], ['mk-pc-2', 'KEY2', 'mk-pc-2-abc.bin', '2026-10-25'], ['mk-pc-3', 'KEY3', 'mk-pc-3-abc.bin', '2099-01-01']);
  const f = E.call({action: 'mock', exam: 'ts-police-constable', id: 'mk-pc-1', phone: S.phone, email: S.email});
  ok(f.ok && f.key === 'KEY1' && f.free, 'free Mock 1 opens without a pass');
  ok(E.sheets.free.rows.length === 2 && E.sheets.free.rows[1][3] === 'mk-pc-1', 'free opening logged');
  ok(!E.call({action: 'mock', exam: 'ts-police-constable', id: 'mk-pc-1', phone: '123'}).ok, 'free mock still needs a registered phone');
  const g = E.call({action: 'mock', exam: 'ts-police-constable', id: 'mk-pc-2', phone: S.phone, email: S.email});
  ok(!g.ok && g.need === 'mock', 'Mock 2 needs the pass');
  ok(!E.call({action: 'mock', exam: 'ts-police-constable', id: 'mk-pc-3', phone: S.phone, email: S.email}).ok, 'a mock before its opening date stays shut');
  ok(!E.call({action: 'mock', exam: 'ts-police-si', id: 'mk-pc-1', phone: S.phone, email: S.email}).ok, 'a Constable mock id is refused on the SI exam');
  E.sheets.passes.rows.push([new Date(), S.phone, 'ts-police-constable', 'mock', '2026-12-21', 'P', 'R', 99, 'webhook', S.email]);
  const h = E.call({action: 'mock', exam: 'ts-police-constable', id: 'mk-pc-2', phone: S.phone, email: S.email, device: 'd1'});
  ok(h.ok && h.key === 'KEY2', 'Mock 2 opens with the Constable pass');
}
console.log(fails ? `CODE.GS TEST FAILURES: ${fails}` : 'CODE.GS TEST: all passed');
process.exit(fails ? 1 : 0);
