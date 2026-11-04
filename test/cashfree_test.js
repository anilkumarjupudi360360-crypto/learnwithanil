// Runs the payments script (tools/payments/Code.gs) in Node against fake Google services, a fake Instamojo and a fake Cashfree,
// to check the Cashfree checkout (4 Nov 2026) before a new version is deployed:   node test/cashfree_test.js
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const SRC = fs.readFileSync(path.join(__dirname, '..', 'tools', 'payments', 'Code.gs'), 'utf8');

function makeEnv(extraProps) {
  const sheets = {};
  const book = {getName: () => 'Passes', getSheetByName: n => sheets[n] || null, insertSheet: n => (sheets[n] = makeSheet())};
  function makeSheet() {
    const rows = [];
    return {rows, appendRow: r => rows.push(r.slice()), setFrozenRows: () => {},
      getDataRange: () => ({getValues: () => rows.map(r => r.slice())}),
      getRange: (r, c) => ({setValue: v => { rows[r - 1][c - 1] = v; }, setValues: v => { v[0].forEach((x, k) => { rows[r - 1][c - 1 + k] = x; }); }})};
  }
  const props = Object.assign({SHEET_ID: 'x', INSTAMOJO_CLIENT_ID: 'id', INSTAMOJO_CLIENT_SECRET: 'sec', INSTAMOJO_SALT: 'salt'}, extraProps || {});
  const im = {requests: {}, payments: {}, n: 0};
  const cf = {orders: {}, payments: {}, calls: [], failPayments: false};
  const ymd = d => new Date(d.getTime() + 5.5 * 3600e3).toISOString().slice(0, 10);
  const res = (code, body) => ({getResponseCode: () => code, getContentText: () => JSON.stringify(body)});
  const env = {
    SpreadsheetApp: {openById: () => book},
    PropertiesService: {getScriptProperties: () => ({getProperty: k => props[k] || null})},
    LockService: {getScriptLock: () => ({waitLock: () => {}, releaseLock: () => {}})},
    CacheService: {getScriptCache: () => ({get: () => 'tok', put: () => {}})},
    ContentService: {createTextOutput: t => ({t, setMimeType() { return this; }}), MimeType: {JSON: 'json'}},
    ScriptApp: {getService: () => ({getUrl: () => 'https://script.google.com/macros/s/TEST/exec'})},
    Logger: {log: () => {}},
    Utilities: {
      formatDate: d => ymd(d), getUuid: () => crypto.randomUUID(),
      computeDigest: (a, t) => Array.from(crypto.createHash('sha256').update(t).digest()), DigestAlgorithm: {SHA_256: 'sha256'},
      computeHmacSignature: (alg, msg, key) => Array.from(crypto.createHmac('sha1', key).update(msg, 'utf8').digest()),
      MacAlgorithm: {HMAC_SHA_1: 'sha1'}, Charset: {UTF_8: 'utf8'},
    },
    UrlFetchApp: {fetch: (url, opt) => {
      const m = url.match(/^https:\/\/(api|sandbox)\.cashfree\.com\/pg(\/.*)$/);
      if (m) {
        cf.calls.push({base: m[1], path: m[2], method: opt.method, headers: opt.headers, body: opt.payload ? JSON.parse(opt.payload) : null});
        if (opt.headers['x-client-id'] !== 'CFID' || opt.headers['x-client-secret'] !== 'CFSEC') return res(401, {message: 'authentication Failed'});
        let p = m[2], q;
        if (p === '/orders' && opt.method === 'post') {
          const b = JSON.parse(opt.payload);
          if (cf.orders[b.order_id]) return res(409, {message: 'order already exists'});
          cf.orders[b.order_id] = {order_id: b.order_id, order_amount: b.order_amount, order_status: 'ACTIVE'};
          return res(200, Object.assign({payment_session_id: 'session_' + b.order_id, cf_order_id: 1}, cf.orders[b.order_id]));
        }
        if ((q = p.match(/^\/orders\/([^/]+)\/payments$/))) {
          if (cf.failPayments) return res(500, {message: 'try later'});
          return res(200, cf.payments[decodeURIComponent(q[1])] || []);
        }
        if ((q = p.match(/^\/orders\/([^/]+)$/))) {
          const o = cf.orders[decodeURIComponent(q[1])];
          return o ? res(200, o) : res(404, {message: 'order not found'});
        }
        return res(404, {});
      }
      const u = url.replace('https://api.instamojo.com', '');
      let body = {};
      if (u === '/v2/payment_requests/' && opt.method === 'post') {
        const id = 'req' + (++im.n); im.requests[id] = {id, status: 'Pending', amount: opt.payload.amount};
        body = {id, longurl: 'https://imojo.test/' + id};
      } else if (u.startsWith('/v2/payment_requests/')) body = im.requests[decodeURIComponent(u.split('/')[3])];
      else if (u.startsWith('/v2/payments/')) body = im.payments[decodeURIComponent(u.split('/')[3])];
      return res(200, body);
    }},
  };
  const names = Object.keys(env);
  const fn = new Function(...names, SRC + '\nreturn {doPost};');
  const api = fn(...names.map(n => env[n]));
  const call = b => JSON.parse(api.doPost({postData: {contents: JSON.stringify(b)}, parameter: {}}).t);
  const cfHook = (type, order_id, extra) => JSON.parse(api.doPost({parameter: {}, postData: {type: 'application/json',
    contents: JSON.stringify({type, event_time: '2026-11-04T10:00:00+05:30', data: Object.assign({order: {order_id, order_amount: 45}, payment: {cf_payment_id: '999', payment_status: 'SUCCESS'}}, extra || {})})}}).t);
  const pay = id => { cf.orders[id].order_status = 'PAID'; cf.payments[id] = [{cf_payment_id: 5114915573, payment_status: 'SUCCESS', payment_amount: 45}]; };
  const passes = () => (sheets.passes ? sheets.passes.rows.slice(1) : []);
  return {api, call, cfHook, pay, passes, sheets, im, cf, props};
}

let fails = 0;
const ok = (c, m) => { if (!c) { fails++; console.log('FAIL', m); } else console.log('ok  ', m); };
const S = {name: 'Ravi Kumar', phone: '9876543210', email: 'ravi@example.com', device: 'd1'};
const CFKEYS = {PAY_GATEWAY: 'cashfree', CASHFREE_APP_ID: 'CFID', CASHFREE_SECRET: 'CFSEC'};
const buy = (E, who) => E.call(Object.assign({action: 'buy', exam: 'ts-police-si', kind: 'pyq', back: 'https://learnwithanil.in/ts-police-si/'}, who || S));

// 1. Until PAY_GATEWAY = cashfree (and both keys are set), checkouts stay on Instamojo
{
  const E = makeEnv({CASHFREE_APP_ID: 'CFID', CASHFREE_SECRET: 'CFSEC'});
  const r = buy(E);
  ok(r.ok && r.url === 'https://imojo.test/req1' && !r.session, 'without PAY_GATEWAY: Instamojo checkout link, as before');
  ok(E.cf.calls.length === 0, 'without PAY_GATEWAY: Cashfree is not called');
  const E2 = makeEnv({PAY_GATEWAY: 'cashfree', CASHFREE_APP_ID: 'CFID'});
  ok(buy(E2).url === 'https://imojo.test/req1', 'PAY_GATEWAY set but the secret missing: still Instamojo');
}

// 2. Cashfree checkout: order made with the right price, return and notify URLs, headers and customer
{
  const E = makeEnv(CFKEYS);
  const r = buy(E);
  ok(r.ok && r.gateway === 'cashfree' && r.mode === 'production' && /^LWA\d{6}[0-9A-F]{6}$/.test(r.order) && r.session === 'session_' + r.order, 'buy gives a Cashfree session and an LWA order id');
  const c = E.cf.calls[0];
  ok(c.base === 'api' && c.method === 'post' && c.headers['x-api-version'] === '2026-01-01', 'production API, version 2026-01-01');
  ok(c.body.order_amount === 45 && c.body.order_currency === 'INR', 'price ₹45 fixed by the script');
  ok(c.body.order_meta.return_url === 'https://learnwithanil.in/ts-police-si/?cf_order=' + r.order, 'student comes back to the same page with ?cf_order=');
  ok(c.body.order_meta.notify_url === 'https://script.google.com/macros/s/TEST/exec', 'Cashfree notifies this script');
  ok(c.body.customer_details.customer_id === 'lwa9876543210' && c.body.customer_details.customer_phone === '9876543210' &&
     c.body.customer_details.customer_email === 'ravi@example.com' && c.body.customer_details.customer_name === 'Ravi Kumar', 'customer details');
  const rq = E.sheets.requests.rows[1];
  ok(rq[1] === r.order && rq[2] === '9876543210' && rq[3] === 'all' && rq[4] === 'pyq' && rq[5] === 45 && rq[8] === 'created', 'request row recorded');
  const r2 = buy(E, Object.assign({}, S, {name: 'రవి', back: 'https://evil.example/'}));
  const c2 = E.cf.calls[E.cf.calls.length - 1];
  ok(!('customer_name' in c2.body.customer_details), 'a Telugu name is left out (optional for Cashfree)');
  ok(c2.body.order_meta.return_url === 'https://learnwithanil.in/?cf_order=' + r2.order, 'a return address outside the site goes to the home page');
  ok(r2.order !== r.order, 'every checkout gets a new order id');
  const E3 = makeEnv(Object.assign({CASHFREE_ENV: 'sandbox'}, CFKEYS));
  ok(buy(E3).mode === 'sandbox' && E3.cf.calls[0].base === 'sandbox', 'CASHFREE_ENV = sandbox uses the sandbox');
  const E4 = makeEnv({PAY_GATEWAY: 'cashfree', CASHFREE_APP_ID: 'CFID', CASHFREE_SECRET: 'WRONG'});
  const r4 = buy(E4);
  ok(!r4.ok && /try again/i.test(r4.error) && E4.sheets.log.rows.some(x => /Cashfree \/orders: 401/.test(x[2])), 'wrong keys: a polite error, the reason in the log tab');
}

// 3. verify: nothing before payment; the pass after; a repeat (and the webhook) records nothing more
{
  const E = makeEnv(CFKEYS);
  const r = buy(E);
  ok(!E.call({action: 'verify', exam: 'ts-police-si', request: r.order, device: 'd1'}).ok && E.passes().length === 0, 'verify before paying: no pass');
  E.pay(r.order);
  const v = E.call({action: 'verify', exam: 'ts-police-si', request: r.order, device: 'd1'});
  const p = E.passes();
  ok(v.ok && p.length === 1, 'verify after paying: pass recorded');
  ok(p[0][1] === '9876543210' && p[0][2] === 'all' && p[0][3] === 'pyq' && p[0][5] === 'CF5114915573' && p[0][6] === r.order && p[0][7] === 45 && p[0][8] === 'verify', 'pass row: phone, all exams, Cashfree payment id, order id, ₹45');
  ok(E.sheets.requests.rows[1][8] === 'paid', 'request marked paid');
  E.call({action: 'verify', exam: 'ts-police-si', request: r.order, device: 'd1'});
  ok(E.cfHook('PAYMENT_SUCCESS_WEBHOOK', r.order).ok && E.passes().length === 1, 'second verify and the webhook add nothing');
  ok(E.call({action: 'verify', exam: 'appsc-group-1', request: r.order}).ok, 'the pass works from any exam page');
}

// 4. webhook alone records the pass (student closed the page), but only if Cashfree itself says PAID
{
  const E = makeEnv(CFKEYS);
  const r = buy(E);
  E.cfHook('PAYMENT_SUCCESS_WEBHOOK', r.order);
  ok(E.passes().length === 0, 'a SUCCESS webhook for an unpaid order (forged) records nothing');
  E.cfHook('PAYMENT_FAILED_WEBHOOK', r.order, {payment: {payment_status: 'FAILED', payment_message: 'UPI timed out'}});
  ok(E.passes().length === 0 && E.sheets.log.rows.some(x => x[1] === 'cf-payment-failed'), 'a failed payment is only logged');
  E.pay(r.order);
  E.cfHook('PAYMENT_SUCCESS_WEBHOOK', r.order);
  ok(E.passes().length === 1 && E.passes()[0][8] === 'cf-webhook', 'webhook after payment: pass recorded');
  E.cfHook('PAYMENT_SUCCESS_WEBHOOK', 'LWA261104ZZZZZZ');
  ok(E.passes().length === 1 && E.sheets.log.rows.some(x => x[1] === 'cf-webhook-unknown'), 'unknown order: logged, nothing recorded');
  E.cf.orders[r.order].order_status = 'ACTIVE';
}

// 5. Cashfree's payments list unreachable for the first check: no second pass when the next check does read it
{
  const E = makeEnv(CFKEYS);
  const r = buy(E);
  E.pay(r.order); E.cf.failPayments = true;
  E.cfHook('PAYMENT_SUCCESS_WEBHOOK', r.order);
  ok(E.passes().length === 1 && E.passes()[0][5] === 'cf-' + r.order, 'payment id unreadable: recorded under the order id');
  E.cf.failPayments = false;
  E.call({action: 'verify', exam: 'ts-police-si', request: r.order});
  ok(E.passes().length === 1, 'the later verify with the real payment id adds nothing');
}

// 6. an underpaid order never opens a pass
{
  const E = makeEnv(CFKEYS);
  const r = buy(E);
  E.pay(r.order); E.cf.orders[r.order].order_amount = 1;
  ok(!E.call({action: 'verify', exam: 'ts-police-si', request: r.order}).ok && E.passes().length === 0, 'order paid for ₹1 instead of ₹45: no pass');
}

// 7. "Link my payment" with the LWA order id from the receipt
{
  const E = makeEnv(CFKEYS);
  const r = buy(E);
  E.pay(r.order);
  E.call({action: 'verify', exam: 'ts-police-si', request: r.order});
  const other = {phone: '9123456780', email: 'other@example.com', device: 'd2'};
  const c = E.call(Object.assign({action: 'claim', exam: 'ts-police-si', payment: r.order.toLowerCase()}, other));
  ok(c.ok && /linked/i.test(c.note) && E.passes().length === 2 && E.passes()[1][1] === '9123456780' && E.passes()[1][5] === 'CF5114915573', 'order id (any case) links the paid pass to another number');
  const c2 = E.call(Object.assign({action: 'claim', exam: 'ts-police-si', payment: r.order}, {phone: '9000000001', email: 'x@example.com'}));
  ok(!c2.ok && /another number/.test(c2.error), 'the same order cannot be linked to a third number');
  const bad = E.call(Object.assign({action: 'claim', exam: 'ts-police-si', payment: 'hello'}, other));
  ok(!bad.ok && /MOJO or LWA/.test(bad.error), 'a wrong id asks for MOJO or LWA');
  // paid, but neither verify nor the webhook reached the script
  const r2 = buy(E, {name: 'Sita', phone: '9988776655', email: 'sita@example.com'});
  E.pay(r2.order);
  const c3 = E.call({action: 'claim', exam: 'ts-police-si', payment: r2.order, phone: '9988776655', email: 'sita@example.com'});
  const last = E.passes()[E.passes().length - 1];
  ok(c3.ok && last[1] === '9988776655' && last[6] === r2.order && last[8] === 'claim (cashfree)', 'missed webhook: the order id checks Cashfree and records the pass');
  const r3 = buy(E);
  ok(!E.call({action: 'claim', exam: 'ts-police-si', payment: r3.order, phone: '9988776655', email: 'sita@example.com'}).ok, 'an unpaid order id links nothing');
  // as with Instamojo, a payment linked by its receipt id before the webhook arrived is not recorded a second time by the late webhook
  const r4 = buy(E, {name: 'Lakshmi', phone: '9555544444', email: 'l@example.com'});
  E.pay(r4.order);
  E.call({action: 'claim', exam: 'ts-police-si', payment: r4.order, phone: '9111122222', email: 'l@example.com'});
  const n4 = E.passes().length;
  E.cfHook('PAYMENT_SUCCESS_WEBHOOK', r4.order);
  ok(E.passes().length === n4, 'a late webhook after the receipt id was linked adds nothing (same as Instamojo)');
}

// 8. Instamojo payments made before the switch still work after it
{
  const E = makeEnv({});
  const r = buy(E);
  const id = r.url.split('/').pop();
  const E2 = E; Object.assign(E2.props, CFKEYS);   // the same spreadsheet, now with Cashfree switched on
  E2.im.requests[id].status = 'Completed'; E2.im.payments.MOJO123ABCD99 = {status: true, payment_request: 'https://x/' + id + '/', amount: '45.00'};
  const v = E2.call({action: 'verify', exam: 'ts-police-si', request: id, payment: 'MOJO123ABCD99'});
  ok(v.ok && E2.passes().length === 1 && E2.passes()[0][5] === 'MOJO123ABCD99', 'Instamojo verify still records the pass');
  const c = E2.call({action: 'claim', exam: 'ts-police-si', payment: 'MOJO123ABCD99', phone: '9123456780', email: 'o@example.com'});
  ok(c.ok && E2.passes().length === 2, 'Instamojo MOJO id still links a payment');
  ok(buy(E2).session, 'and new checkouts now go to Cashfree');
}

console.log(fails ? fails + ' FAILED' : 'all passed');
process.exit(fails ? 1 : 0);
