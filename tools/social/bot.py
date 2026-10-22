#!/usr/bin/env python3
"""Learn with Anil social bot: posts to the Telegram channel and to Instagram, every day, India time.

    08:00  morning question  a real previous-year question card (rotating exams), answer on the site
    13:00  meme 1            current affairs, made each morning by the Claude meme maker
    18:00  evening question
    21:00  meme 2            aspirant life

It runs on GitHub Actions (.github/workflows/social.yml). Each run looks at the clock and does what is due,
so a late or missed run is caught up by the next one. Memes are first sent to Anil on Telegram with a Stop
button; they post on time unless he taps Stop.

State lives on the `social` branch, checked out at ./state (or $STATE_DIR):
    used-questions.json              question ids already posted (never repeated)
    cards/<date>-<am|pm>.jpg / .json question cards, made up to a day ahead
    memes/<date>/<1|2>.jpg / .json   memes queued by the meme maker
    memes/history.jsonl              every meme posted (the meme maker reads it to avoid repeats)
    log/<date>.json                  what went out where, with the Instagram links (the WhatsApp status task reads it)
    control.json                     Telegram update offset, meme previews, stopped memes
    secrets/ig.token                 the refreshed Instagram token, encrypted with STATE_KEY

Commands:
    bot.py run [--wait]      do what is due now (--wait: if a post is due within 15 minutes, wait for it)
    bot.py fetch             download queued memes that only have a Canva link (runs when the meme maker pushes)
    bot.py needs-render      print true if question cards for today / tomorrow are missing
    bot.py render            make the missing question cards
    bot.py check             check the Telegram and Instagram settings and say which accounts they reach
    bot.py whoami            list the Telegram chats that have messaged the bot (to find TG_ADMIN_CHAT)
    bot.py demo --out DIR    make one sample card per exam, without posting or remembering anything

Settings (GitHub secrets): TG_BOT_TOKEN and IG_TOKEN (long-lived Instagram token) are needed. Optional:
TG_CHANNEL (default @learn_with_anil06), TG_ADMIN_CHAT (default: the channel owner), IG_USER_ID, STATE_KEY
(key for the stored refreshed token; default derived from IG_TOKEN).
DRY_RUN=1 renders and logs but does not post.
"""
import argparse, asyncio, base64, datetime as dt, hashlib, json, os, random, subprocess, sys, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

IST = ZoneInfo('Asia/Kolkata')
SITE = 'https://learnwithanil.in'
STATE = os.path.abspath(os.environ.get('STATE_DIR') or os.path.join(ROOT, 'state'))
REPO = os.environ.get('GITHUB_REPOSITORY', 'anilkumarjupudi360360-crypto/learnwithanil')
BRANCH = 'social'
DRY = os.environ.get('DRY_RUN') == '1'
IG_VER = os.environ.get('IG_API_VERSION', 'v24.0')
if not os.environ.get('TG_CHANNEL'):            # an unset GitHub secret arrives as an empty string
    os.environ['TG_CHANNEL'] = '@learn_with_anil06'   # the public channel

# slot: when it is due, until when a late post is still worth making (India time)
SLOTS = [
    dict(key='q-am', kind='question', half='am', at=(8, 0), until=(12, 0), label='morning question'),
    dict(key='meme-1', kind='meme', n=1, at=(13, 0), until=(17, 0), label='meme 1'),
    dict(key='q-pm', kind='question', half='pm', at=(18, 0), until=(21, 0), label='evening question'),
    dict(key='meme-2', kind='meme', n=2, at=(21, 0), until=(23, 30), label='meme 2'),
]
PREVIEW_MIN = 30          # a meme posts only if Anil has had its preview for at least this many minutes
KEEP_DAYS = 21            # images older than this are removed from the branch (Instagram has its own copy)

# questions rotate through every live exam, two a day
ROTATION = ['appsc-group-2', 'ts-police-si', 'appsc-group-1', 'ts-police-constable', 'upsc-capf']
TAGS = {
    'appsc-group-2': '#APPSC #APPSCGroup2 #Group2 #APGroup2 #APPSCExams',
    'appsc-group-1': '#APPSC #APPSCGroup1 #Group1 #APGroup1 #APPSCExams',
    'ts-police-si': '#TSPolice #TSSI #TGPRB #TSLPRB #TelanganaPolice #PoliceSI',
    'ts-police-constable': '#TSPolice #TSConstable #TGPRB #TSLPRB #TelanganaPolice #PoliceConstable',
    'upsc-capf': '#UPSC #CAPF #CAPFAC #UPSCCAPF #AssistantCommandant',
}
L2 = {
    'te': dict(font='Te', name='Telugu', line='సమాధానం, వివరణ తెలుగులో కూడా ఉన్నాయి.', comment='మీ సమాధానం (1/2/3/4) కామెంట్ చేయండి!'),
    'hi': dict(font='Hi', name='Hindi', line='उत्तर और व्याख्या हिंदी में भी उपलब्ध है।', comment='अपना उत्तर (1/2/3/4) कमेंट करें!'),
}


# ---------------------------------------------------------------- small helpers

def now_ist():
    fake = os.environ.get('NOW')   # for testing: NOW=2026-10-23T13:05
    return dt.datetime.fromisoformat(fake).replace(tzinfo=IST) if fake else dt.datetime.now(IST)


def at(day, hm):
    return dt.datetime(day.year, day.month, day.day, hm[0], hm[1], tzinfo=IST)


def sp(*parts):
    return os.path.join(STATE, *parts)


def jload(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def jsave(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def log(msg):
    print(f'[{now_ist():%H:%M:%S}] {msg}', flush=True)


def git(*args, check=True):
    return subprocess.run(['git', '-C', STATE, *args], check=check, capture_output=True, text=True)


def publish_state(msg):
    """Commit and push the state branch, so that new images get a public URL Instagram can fetch."""
    if not os.path.isdir(sp('.git')) or DRY:
        return
    git('add', '-A')
    if git('diff', '--cached', '--quiet', check=False).returncode == 0:
        return
    git('commit', '-q', '-m', msg)
    for i in range(4):
        r = git('push', '-q', 'origin', f'HEAD:{BRANCH}', check=False)
        if r.returncode == 0:
            return
        log(f'push failed ({r.stderr.strip()[:200]}), rebasing')
        git('pull', '-q', '--rebase', 'origin', BRANCH, check=False)
        time.sleep(3 * (i + 1))
    raise RuntimeError('could not push the social branch')


def raw_url(rel):
    return f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/{rel}'


def wait_until_public(url, tries=12):
    import requests
    for _ in range(tries):
        try:
            if requests.head(url, timeout=20).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(5)
    return False


# ---------------------------------------------------------------- Telegram

class Telegram:
    def __init__(self, token):
        self.base = f'https://api.telegram.org/bot{token}/'

    def call(self, method, files=None, **params):
        import requests
        for k, v in list(params.items()):
            if isinstance(v, (dict, list)):
                params[k] = json.dumps(v, ensure_ascii=False)
        r = requests.post(self.base + method, data=params, files=files, timeout=90)
        j = r.json()
        if not j.get('ok'):
            raise RuntimeError(f'Telegram {method}: {j.get("description")}')
        return j['result']

    def photo(self, chat, path, caption, buttons=None):
        kw = dict(chat_id=chat, caption=caption[:1024])
        if buttons:
            kw['reply_markup'] = {'inline_keyboard': buttons}
        with open(path, 'rb') as f:
            return self.call('sendPhoto', files={'photo': f}, **kw)

    def text(self, chat, text):
        return self.call('sendMessage', chat_id=chat, text=text[:4000], disable_web_page_preview=True)


def admin_chat(tg, ctl):
    """Anil's private chat with the bot: TG_ADMIN_CHAT, or else the owner of the channel (he must have pressed Start)."""
    if os.environ.get('TG_ADMIN_CHAT'):
        return str(os.environ['TG_ADMIN_CHAT'])
    if ctl.get('admin_chat'):
        return str(ctl['admin_chat'])
    if not tg:
        return ''
    try:
        for m in tg.call('getChatAdministrators', chat_id=os.environ['TG_CHANNEL']):
            if m.get('status') == 'creator' and not m['user'].get('is_bot'):
                ctl['admin_chat'] = m['user']['id']
                return str(m['user']['id'])
    except Exception as e:
        log(f'(could not look up the channel owner: {e})')
    return ''


def channel_link(msg):
    ch = msg.get('chat', {})
    if ch.get('username'):
        return f'https://t.me/{ch["username"]}/{msg["message_id"]}'
    cid = str(ch.get('id', ''))
    return f'https://t.me/c/{cid[4:]}/{msg["message_id"]}' if cid.startswith('-100') else ''


# ---------------------------------------------------------------- Instagram

def _fernet():
    key = os.environ.get('STATE_KEY') or os.environ.get('IG_TOKEN', '')   # the original token is secret too
    if not key:
        return None
    from cryptography.fernet import Fernet
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(('lwa-state-key:' + key).encode()).digest()))


def _fingerprint(tok):
    return hashlib.sha256(('lwa-fingerprint:' + tok).encode()).hexdigest()[:16]


def ig_token():
    """The newest Instagram token: the refreshed one on the state branch, unless the IG_TOKEN secret has changed since."""
    env = os.environ.get('IG_TOKEN', '').strip()
    stored, f = jload(sp('secrets', 'ig.token'), None), _fernet()
    if stored and f and stored.get('secret') == _fingerprint(env):
        try:
            return f.decrypt(stored['token'].encode()).decode()
        except Exception:
            log('stored Instagram token could not be decrypted; using the IG_TOKEN secret')
    return env


def save_ig_token(token):
    f = _fernet()
    if not f:
        return
    env = os.environ.get('IG_TOKEN', '').strip()
    jsave(sp('secrets', 'ig.token'), dict(secret=_fingerprint(env),
                                          token=f.encrypt(token.encode()).decode(), saved=now_ist().isoformat()))


class Instagram:
    def __init__(self, token, user_id=''):
        self.token, self.uid = token, user_id

    def call(self, method, path, **params):
        import requests
        params['access_token'] = self.token
        url = f'https://graph.instagram.com/{IG_VER}/{path}'
        r = requests.request(method, url, params=params if method == 'GET' else None,
                             data=params if method != 'GET' else None, timeout=90)
        j = r.json()
        if 'error' in j:
            e = j['error']
            raise RuntimeError(f'Instagram {path}: {e.get("message")} (code {e.get("code")})')
        return j

    def me(self):
        j = self.call('GET', 'me', fields='user_id,username')
        self.uid = self.uid or j.get('user_id') or j.get('id')
        return j

    def post_image(self, image_url, caption):
        if not self.uid:
            self.me()
        c = self.call('POST', f'{self.uid}/media', image_url=image_url, caption=caption[:2200])['id']
        for _ in range(24):
            st = self.call('GET', c, fields='status_code').get('status_code')
            if st == 'FINISHED':
                break
            if st in ('ERROR', 'EXPIRED'):
                raise RuntimeError(f'Instagram could not process the image ({st})')
            time.sleep(5)
        m = self.call('POST', f'{self.uid}/media_publish', creation_id=c)['id']
        link = ''
        try:
            link = self.call('GET', m, fields='permalink').get('permalink', '')
        except RuntimeError as e:
            log(f'no permalink: {e}')
        return dict(id=m, permalink=link)


def refresh_ig(ctl):
    """Long-lived Instagram tokens last 60 days; refresh once a week so it never runs out."""
    today = now_ist().date()
    fp = _fingerprint(os.environ.get('IG_TOKEN', ''))
    if ctl.get('ig_secret_fp') != fp:                 # a new IG_TOKEN secret: Instagram refuses to refresh tokens < 24 h old
        ctl['ig_secret_fp'], ctl['ig_secret_seen'], ctl['ig_refreshed'] = fp, today.isoformat(), today.isoformat()
        return
    last = ctl.get('ig_refreshed')
    if last and (today - dt.date.fromisoformat(last)).days < 7:
        return
    tok = ig_token()
    if not tok or not _fernet():
        return
    import requests
    j = requests.get('https://graph.instagram.com/refresh_access_token',
                     params=dict(grant_type='ig_refresh_token', access_token=tok), timeout=60).json()
    if 'access_token' in j:
        save_ig_token(j['access_token'])
        ctl['ig_refreshed'] = now_ist().date().isoformat()
        log(f'Instagram token refreshed, valid for {int(j.get("expires_in", 0)) // 86400} days')
    else:
        raise RuntimeError(f'Instagram token refresh failed: {j.get("error", j)}')


# ---------------------------------------------------------------- question cards

def exam_for(day, half):
    k = day.toordinal() * 2 + (0 if half == 'am' else 1)
    return ROTATION[k % len(ROTATION)], k // len(ROTATION)


def card_name(day, half):
    return f'cards/{day.isoformat()}-{half}'


def load_exams(ids):
    import build as B
    import contextlib, io
    confs = {c['id']: c for c in B.exam_confs()}
    out = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for cid in ids:
            out[cid] = (confs[cid],) + B.load_exam(confs[cid])
    return B, out


def pick_question(conf, papers, qs, used, k, seed):
    pm = {p['id']: p for p in papers}
    subjects = [s[0] for s in conf['subjects'] if s[0] not in ('cur', 'eng')]
    want = subjects[k % len(subjects)]

    def ok(q, s=None, loose=False):
        if q['id'] in used or not q.get('o') or not q.get('qt') or not q.get('ot') or q.get('img'):
            return False
        if pm[q['p']]['fmt'] != 'mcq' or len(q['a']) != 1 or q['s'] in ('cur', 'eng') or (s and q['s'] != s):
            return False
        lim = 1.5 if loose else 1
        return (len(q['q']) < 240 * lim and len(q['qt']) < 280 * lim and max(map(len, q['o'])) < 60 * lim
                and max(map(len, q['ot'])) < 70 * lim and (loose or '\n' not in q['q'].strip()))

    for cand in ([q for q in qs if ok(q, want)], [q for q in qs if ok(q)], [q for q in qs if ok(q, loose=True)]):
        if cand:
            return random.Random(seed).choice(sorted(cand, key=lambda q: q['id']))
    return None


def card_item(B, conf, papers, q, day, half):
    p = {p['id']: p for p in papers}[q['p']]
    subj = {s[0]: s[1] for s in conf['subjects']}
    l2 = L2[conf['l2']['code']]
    url = f'{SITE}{conf["pb"]}q/{q["id"]}.html'
    exam = conf['seo'].replace('TS Police Constable', 'TS Constable')
    return dict(day=day.isoformat(), daylabel=day.strftime('%a %d %b'), exam_short=exam, exam_id=conf['id'],
                kicker='Morning question' if half == 'am' else 'Evening question',
                paper=B.paper_kw(conf, p).replace(conf['seo'] + ' ', ''), n=q['n'], subject=subj[q['s']],
                q=q['q'], o=q['o'], qt=q['qt'], ot=q['ot'], id=q['id'], url=url, short=url.replace('https://', ''),
                qr=url + f'?utm_source=qotd&utm_medium=social&utm_campaign={day.isoformat()}-{half}',
                l2font=l2['font'], l2code=conf['l2']['code'], l2name=l2['name'], fs=54, fo=38, ft=38)


def captions(it):
    l2 = L2[it['l2code']]
    when = 'Morning' if it['kicker'].startswith('Morning') else 'Evening'
    head = (f"{it['exam_short']}: {when} question ({it['daylabel']})\n"
            f"From the {it['exam_short']} {it['paper']} question paper, Q{it['n']} · {it['subject']}\n\n"
            f"Comment your answer (1/2/3/4) before you check!\n{l2['comment']}\n\n")
    tags = f"{TAGS.get(it['exam_id'], '')} #PYQ #PreviousYearQuestions #LearnWithAnil"
    ig = (head + f"✅ Answer + explanation in English & {it['l2name']}: {it['short']}\n"
          f"(scan the QR code on the card, or tap the link in our bio)\n{l2['line']}\n\n"
          f"Free previous papers & mock tests: learnwithanil.in\n\n{tags}")
    tg = (head + f"✅ Answer + explanation: {it['url']}\n{l2['line']}\n\n"
          f"Free previous papers & mock tests: {SITE}\n{tags}")
    return ig, tg


def render_cards(items, outdir):
    import qotd_cards as Q
    os.makedirs(outdir, exist_ok=True)
    asyncio.run(Q.render(items, outdir))


def needs_render():
    if not (os.environ.get('TG_BOT_TOKEN') or os.environ.get('IG_TOKEN')):
        return []
    now = now_ist()
    todo = []
    for day in (now.date(), now.date() + dt.timedelta(days=1)):
        for s in SLOTS:
            if s['kind'] == 'question' and now < at(day, s['until']) and not os.path.exists(sp(card_name(day, s['half']) + '.jpg')):
                todo.append((day, s['half']))
    return todo


def cmd_render():
    todo = needs_render()
    if not todo:
        log('all question cards are ready'); return
    used = set(jload(sp('used-questions.json'), []))
    B, ex = load_exams({exam_for(d, h)[0] for d, h in todo})
    items = []
    for day, half in todo:
        cid, k = exam_for(day, half)
        conf, papers, qs = ex[cid]
        q = pick_question(conf, papers, qs, used, k, f'{day}-{half}')
        if not q:
            log(f'no unused question left for {cid}'); continue
        used.add(q['id'])
        it = card_item(B, conf, papers, q, day, half)
        it['file'] = os.path.basename(card_name(day, half)) + '.jpg'
        items.append(it)
    render_cards(items, sp('cards'))
    for it in items:
        ig, tg = captions(it)
        meta = {k: it[k] for k in ('day', 'kicker', 'exam_id', 'exam_short', 'paper', 'n', 'subject', 'id', 'url', 'file')}
        meta.update(caption_ig=ig, caption_tg=tg, q=it['q'])
        jsave(sp('cards', it['file'][:-4] + '.json'), meta)
        log(f'card {it["file"]}: {it["exam_short"]} {it["id"]}')
    jsave(sp('used-questions.json'), sorted(used))
    publish_state(f'Question cards for {", ".join(sorted({d.isoformat() for d, _ in todo}))}')


# ---------------------------------------------------------------- memes

def meme_paths(day, n):
    base = sp('memes', day.isoformat(), str(n))
    return base + '.jpg', base + '.json'


def ensure_meme_image(day, n):
    """The meme maker normally commits the JPEG; if it could only leave Canva's download link, fetch it here."""
    img, meta_p = meme_paths(day, n)
    meta = jload(meta_p, None)
    if os.path.exists(img) or not meta:
        return meta if os.path.exists(img) else None
    for name in ('png', 'jpeg'):
        alt = img[:-3] + name
        if os.path.exists(alt):
            _to_jpeg(alt, img); return meta
    if meta.get('export_url'):
        import requests, tempfile
        r = requests.get(meta['export_url'], timeout=120)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(r.content)
        _to_jpeg(t.name, img)
        os.remove(t.name)
        return meta
    return None


def _to_jpeg(src, dst):
    from PIL import Image
    im = Image.open(src).convert('RGB')
    w, h = im.size
    if w / h < 0.8 or w / h > 1.91:      # Instagram accepts 4:5 to 1.91:1; pad anything taller onto 4:5, in the edge colour
        nw = max(w, int(h * 0.8))
        edge = [im.getpixel((x, y)) for x in (0, w - 1) for y in range(0, h, max(1, h // 40))]
        fill = tuple(sum(c[i] for c in edge) // len(edge) for i in range(3))
        bg = Image.new('RGB', (nw, int(nw / 0.8)), fill)
        bg.paste(im, ((nw - w) // 2, (int(nw / 0.8) - h) // 2))
        im = bg
    im.save(dst, 'JPEG', quality=90, optimize=True)
    if os.path.abspath(src) != os.path.abspath(dst) and src.startswith(STATE):
        os.remove(src)


def cmd_fetch():
    """Download queued memes that only have Canva's (short-lived) download link. Needs no tokens."""
    day = now_ist().date()
    for d in (day, day + dt.timedelta(days=1)):
        for n in (1, 2):
            try:
                if ensure_meme_image(d, n):
                    log(f'meme {d} {n}: image ready')
            except Exception as e:
                log(f'! meme {d} {n}: could not fetch the image: {e}')
    publish_state(f'Meme images for {day}')


def meme_caption(meta, platform):
    cap = meta.get('caption_tg' if platform == 'tg' else 'caption_ig') or meta.get('caption') or ''
    return cap.strip()


# ---------------------------------------------------------------- the run

def process_updates(tg, ctl):
    """Stop / Undo taps on meme previews, and a /status reply."""
    admin = admin_chat(tg, ctl)
    ups = tg.call('getUpdates', offset=ctl.get('tg_offset', 0) + 1, timeout=0, allowed_updates=['callback_query', 'message'])
    for u in ups:
        ctl['tg_offset'] = u['update_id']
        cb = u.get('callback_query')
        if cb and str(cb['from']['id']) == admin and ':' in cb.get('data', ''):
            act, key = cb['data'].split(':', 1)
            stopped = set(ctl.get('stopped', []))
            (stopped.add if act == 'stop' else stopped.discard)(key)
            ctl['stopped'] = sorted(stopped)
            msg = cb.get('message', {})
            label = '⛔ Stopped. This meme will not be posted.' if act == 'stop' else '✅ Back on. It will post on time.'
            btn = [[{'text': '↩️ Undo, post it' if act == 'stop' else '⛔ Stop this meme', 'callback_data': ('undo:' if act == 'stop' else 'stop:') + key}]]
            for call in (lambda: tg.call('answerCallbackQuery', callback_query_id=cb['id'], text=label),
                         lambda: tg.call('editMessageCaption', chat_id=msg['chat']['id'], message_id=msg['message_id'],
                                         caption=(label + '\n\n' + (msg.get('caption') or '').split('\n\n', 1)[-1])[:1024], reply_markup={'inline_keyboard': btn})):
                try:
                    call()
                except Exception as e:
                    log(f'(telegram: {e})')
            log(f'{act} {key}')
        m = u.get('message')
        if m and str(m['chat']['id']) == admin and (m.get('text') or '').strip().lower() in ('/status', 'status'):
            day = now_ist().date()
            lg = jload(sp('log', f'{day}.json'), {})
            lines = [f"{s['label']}: " + ('posted' if lg.get(s['key'], {}).get('telegram') or lg.get(s['key'], {}).get('instagram')
                                           else lg.get(s['key'], {}).get('skipped', 'waiting')) for s in SLOTS]
            tg.text(admin, f'Today ({day:%d %b}):\n' + '\n'.join(lines))


def send_previews(tg, ctl, day):
    admin = admin_chat(tg, ctl)
    if not admin:
        return
    prev = ctl.setdefault('previews', {})
    for s in SLOTS:
        if s['kind'] != 'meme':
            continue
        key = f'{day}:{s["n"]}'
        if key in prev or now_ist() >= at(day, s['until']):
            continue
        meta = ensure_meme_image(day, s['n'])
        if not meta:
            continue
        img = meme_paths(day, s['n'])[0]
        t = f'{s["at"][0] % 12 or 12}:{s["at"][1]:02d} {"PM" if s["at"][0] >= 12 else "AM"}'
        text = (f'🕐 Meme {s["n"]} for today posts at {t} on Instagram and Telegram.\n'
                f'Tap Stop if you don\'t want it (the bot checks every 30 minutes).\n\n'
                f'{meta.get("title", "")}\n\nCaption:\n{meme_caption(meta, "ig")}')
        if DRY:
            log(f'[dry] preview {key}'); prev[key] = now_ist().isoformat(); continue
        tg.photo(admin, img, text, [[{'text': '⛔ Stop this meme', 'callback_data': f'stop:{key}'}]])
        prev[key] = now_ist().isoformat()
        log(f'preview sent for meme {key}')


def post_slot(s, day, lg, ctl, tg, ig):
    entry = lg.setdefault(s['key'], {})
    if s['kind'] == 'question':
        base = card_name(day, s['half'])
        meta = jload(sp(base + '.json'), None)
        if not meta or not os.path.exists(sp(base + '.jpg')):
            raise RuntimeError(f'no card for the {s["label"]}')
        rel, cap_ig, cap_tg = base + '.jpg', meta['caption_ig'], meta['caption_tg']
        buttons = [[{'text': '✅ See the answer & explanation', 'url': meta['url'] + f'?utm_source=telegram&utm_medium=social&utm_campaign={day}'}]]
        entry.update(title=f'{meta["exam_short"]} {s["label"]}', url=meta['url'], question=meta['id'])
    else:
        key = f'{day}:{s["n"]}'
        if key in ctl.get('stopped', []):
            entry['skipped'] = 'stopped by Anil'; return
        sent = ctl.get('previews', {}).get(key)
        if not sent:
            return                                    # no preview yet: wait for the next run
        if now_ist() - dt.datetime.fromisoformat(sent) < dt.timedelta(minutes=PREVIEW_MIN):
            return
        meta = ensure_meme_image(day, s['n'])
        if not meta:
            return
        img, _ = meme_paths(day, s['n'])
        rel = os.path.relpath(img, STATE).replace(os.sep, '/')
        cap_ig, cap_tg, buttons = meme_caption(meta, 'ig'), meme_caption(meta, 'tg'), None
        entry.update(title=meta.get('title', s['label']), kind=meta.get('kind', ''))

    path = sp(rel)
    if tg and os.environ.get('TG_CHANNEL') and 'telegram' not in entry:
        if DRY:
            log(f'[dry] telegram {s["key"]}'); entry['telegram'] = {'dry': True}
        else:
            try:
                m = tg.photo(os.environ['TG_CHANNEL'], path, cap_tg, buttons)
                entry['telegram'] = dict(message_id=m['message_id'], link=channel_link(m), at=now_ist().isoformat())
                log(f'telegram: {s["key"]} posted {entry["telegram"]["link"]}')
            except Exception as e:
                alert_once(tg, entry, 'telegram', f'Telegram post failed for the {s["label"]}: {e}')
    if ig and 'instagram' not in entry:
        if DRY:
            log(f'[dry] instagram {s["key"]}'); entry['instagram'] = {'dry': True}
        else:
            try:
                publish_state(f'{day} {s["key"]} image')
                url = raw_url(rel)
                if not wait_until_public(url):
                    raise RuntimeError(f'image not public yet: {url}')
                r = ig.post_image(url, cap_ig)
                entry['instagram'] = dict(r, at=now_ist().isoformat())
                log(f'instagram: {s["key"]} posted {r["permalink"]}')
            except Exception as e:
                alert_once(tg, entry, 'instagram', f'Instagram post failed for the {s["label"]}: {e}')
    if s['kind'] == 'meme' and ('telegram' in entry or 'instagram' in entry) and not entry.get('history'):
        with open(sp('memes', 'history.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(date=day.isoformat(), n=s['n'], kind=meta.get('kind', ''), title=meta.get('title', ''),
                                    topic=meta.get('topic', '')), ensure_ascii=False) + '\n')
        entry['history'] = True


CTL = {}


def alert_once(tg, entry, platform, msg):
    log('! ' + msg)
    errs = entry.setdefault('errors', {})
    if platform in errs:
        return
    errs[platform] = msg[:300]
    admin = admin_chat(tg, CTL) if tg else ''
    if tg and admin and not DRY:
        try:
            tg.text(admin, '⚠️ ' + msg + '\nThe bot will try again on its next run.')
        except Exception as e:
            log(f'(alert failed: {e})')


def prune():
    cutoff = now_ist().date() - dt.timedelta(days=KEEP_DAYS)
    for folder in ('cards', 'memes'):
        root = sp(folder)
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            for fn in files:
                if fn.endswith(('.jpg', '.png', '.jpeg')):
                    try:
                        d = dt.date.fromisoformat((os.path.basename(dirpath) if folder == 'memes' else fn)[:10])
                    except ValueError:
                        continue
                    if d < cutoff:
                        os.remove(os.path.join(dirpath, fn))


def cmd_run(wait):
    tok_tg, tok_ig = os.environ.get('TG_BOT_TOKEN'), ig_token()
    if not tok_tg and not tok_ig:
        log('Telegram and Instagram are not set up yet (no TG_BOT_TOKEN / IG_TOKEN secrets); nothing to do')
        return
    tg = Telegram(tok_tg) if tok_tg else None
    ig = Instagram(tok_ig, os.environ.get('IG_USER_ID', '')) if tok_ig else None
    ctl = jload(sp('control.json'), {})
    CTL.clear(); CTL.update(ctl); ctl = CTL
    now = now_ist()
    day = now.date()

    if wait:   # started a few minutes early by the timed schedule: wait for the slot
        nxt = [at(day, s['at']) for s in SLOTS if dt.timedelta(0) < at(day, s['at']) - now <= dt.timedelta(minutes=15)]
        if nxt:
            secs = (min(nxt) - now).total_seconds()
            log(f'waiting {int(secs)} s for {min(nxt):%H:%M}')
            if tg:
                send_previews(tg, ctl, day)
            time.sleep(max(0, secs) + 2)

    if tg:
        try:
            process_updates(tg, ctl)
            send_previews(tg, ctl, day)
        except Exception as e:
            log(f'! telegram updates: {e}')

    lg = jload(sp('log', f'{day}.json'), {})
    for s in SLOTS:
        e = lg.get(s['key'], {})
        done = e.get('skipped') or (('telegram' in e or not tg) and ('instagram' in e or not ig))
        if done or not (at(day, s['at']) <= now_ist() < at(day, s['until'])):
            continue
        try:
            post_slot(s, day, lg, ctl, tg, ig)
        except Exception as ex:
            alert_once(tg, lg.setdefault(s['key'], {}), 'slot', f'{s["label"]}: {ex}')
        jsave(sp('log', f'{day}.json'), lg)
        jsave(sp('control.json'), ctl)

    if ig:
        try:
            refresh_ig(ctl)
        except Exception as e:
            if ctl.get('refresh_alerted') != day.isoformat():
                ctl['refresh_alerted'] = day.isoformat()
                if tg and admin_chat(tg, ctl):
                    tg.text(admin_chat(tg, ctl), f'⚠️ {e}. Instagram posts stop when the token expires; ask Claude to renew it.')
            log(f'! {e}')
    prune()
    jsave(sp('control.json'), ctl)
    if lg:
        jsave(sp('log', f'{day}.json'), lg)
    publish_state(f'Run {now:%Y-%m-%d %H:%M} IST')


def cmd_check():
    ok = True
    if os.environ.get('TG_BOT_TOKEN'):
        tg = Telegram(os.environ['TG_BOT_TOKEN'])
        me = tg.call('getMe')
        print(f'Telegram bot: @{me["username"]}')
        if not os.environ.get('TG_ADMIN_CHAT'):
            os.environ['TG_ADMIN_CHAT'] = admin_chat(tg, {}) or ''
        for name in ('TG_CHANNEL', 'TG_ADMIN_CHAT'):
            v = os.environ.get(name)
            if not v:
                print(f'  {name}: not set'); ok = False; continue
            try:
                c = tg.call('getChat', chat_id=v)
                print(f'  {name}: {c.get("title") or c.get("first_name")} ({c.get("type")}, @{c.get("username", "-")}, id {c["id"]})')
                if c.get('type') == 'channel':
                    mem = tg.call('getChatMember', chat_id=v, user_id=me['id'])
                    print(f'    bot is {mem["status"]}' + ('' if mem.get('can_post_messages') or mem['status'] == 'creator' else '  ← needs "Post messages" admin right'))
            except Exception as e:
                print(f'  {name}: {e}'); ok = False
    else:
        print('Telegram: TG_BOT_TOKEN not set'); ok = False
    tok = ig_token()
    if tok:
        try:
            print(f'Instagram: @{Instagram(tok).me().get("username")}')
        except Exception as e:
            print(f'Instagram: {e}'); ok = False
    else:
        print('Instagram: IG_TOKEN not set'); ok = False
    print('STATE_KEY: ' + ('set' if os.environ.get('STATE_KEY') else 'not set (using the IG_TOKEN secret as the key)'))
    return ok


def cmd_whoami():
    tg = Telegram(os.environ['TG_BOT_TOKEN'])
    seen = {}
    for u in tg.call('getUpdates', timeout=0):
        for k in ('message', 'channel_post', 'my_chat_member'):
            c = (u.get(k) or {}).get('chat')
            if c:
                seen[c['id']] = f'{c.get("type")}: {c.get("title") or c.get("first_name", "")} @{c.get("username", "-")}'
    for cid, d in seen.items():
        print(cid, d)
    if not seen:
        print('No chats yet: send /start to the bot from your Telegram, then run this again.')


def cmd_demo(out):
    B, ex = load_exams(ROTATION)
    day = now_ist().date()
    items = []
    for i, cid in enumerate(ROTATION):
        conf, papers, qs = ex[cid]
        q = pick_question(conf, papers, qs, set(jload(sp('used-questions.json'), [])), i, f'demo-{cid}')
        it = card_item(B, conf, papers, q, day, 'am' if i % 2 == 0 else 'pm')
        it['file'] = f'{cid}.jpg'
        items.append(it)
    render_cards(items, out)
    for it in items:
        ig, tg = captions(it)
        with open(os.path.join(out, it['file'][:-4] + '.txt'), 'w', encoding='utf-8') as f:
            f.write('INSTAGRAM\n' + ig + '\n\nTELEGRAM\n' + tg + '\n')
    print(f'{len(items)} sample cards in {out}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['run', 'fetch', 'needs-render', 'render', 'check', 'whoami', 'demo'])
    ap.add_argument('--wait', action='store_true')
    ap.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'needs-render':
        print('true' if needs_render() else 'false')
    elif a.cmd == 'render':
        cmd_render()
    elif a.cmd == 'fetch':
        cmd_fetch()
    elif a.cmd == 'run':
        cmd_run(a.wait)
    elif a.cmd == 'check':
        sys.exit(0 if cmd_check() else 1)
    elif a.cmd == 'whoami':
        cmd_whoami()
    elif a.cmd == 'demo':
        cmd_demo(a.out)


if __name__ == '__main__':
    main()
