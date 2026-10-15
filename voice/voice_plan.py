"""Plan every voice clip Pip needs for a recorded (Google Chirp 3 HD) voice.

Lines that only come in a few versions are recorded whole, so they sound natural.
Lines that come in thousands of versions (numbers, names, picture words) are recorded in
pieces that join at natural pauses; the pieces are chosen so each one still has only a
limited number of versions.

Usage: python3 voice_plan.py index.html out_dir [name ...]
Writes out_dir/lines.json, out_dir/lines.csv and prints a summary.
"""
import json, re, subprocess, sys, csv, collections, pathlib, hashlib

HTML, OUT = sys.argv[1], pathlib.Path(sys.argv[2])
NAMES = sys.argv[3:]          # the child's name(s) Pip says ("Hi, Ava!")
HERE = pathlib.Path(__file__).resolve().parent
WHOLE_MAX = 150               # a group with this many versions or fewer is recorded whole
MERGE_MAX = 60                # pieces are joined while a piece has this many versions or fewer
FIX_FRAC = 0.35               # a word in this share of a group's lines is part of the fixed text

# ---------------------------------------------------------------- the lines
def corpus(n):
    raw = subprocess.check_output(['node', str(HERE / 'voice_corpus.js'), HTML, str(n)])
    return json.loads(raw)

data = corpus(4000)
lists = data['lists']
groups = collections.defaultdict(set)
for x in data['lines']:
    groups[x['group']].add(x['text'])

PAGE = open(HTML).read()
app = max(re.findall(r'<script>([\s\S]*?)</script>', PAGE), key=len)   # the app script (the biggest plain <script>)
names_file = HERE / 'names.txt'
if names_file.exists(): NAMES += [n.strip() for n in names_file.read_text().splitlines() if n.strip() and not n.startswith('#')]
def appgroup(name, texts):
    for t in texts:
        if t and t.strip(): groups['app:' + name].add(t)

# fixed lines in the app
lit = set(re.findall(r"Voice\.say\(\s*'((?:[^'\\]|\\.)*)'\s*[,)]", app)) | set(re.findall(r'Voice\.say\(\s*"((?:[^"\\]|\\.)*)"\s*[,)]', app))
appgroup('fixed', lit)
def strlist(var):
    m = re.search(r'var %s = \[([^\]]*)\]' % var, app)
    return re.findall(r"'([^']*)'", m.group(1)) if m else []
CHEER, CHEER2, OOPS = strlist('CHEER'), strlist('CHEER2'), strlist('OOPS')
appgroup('cheer', CHEER + CHEER2 + ['Three in a row!', 'Four in a row!'])
appgroup('oops', OOPS + ["Here's a hint. Tap the one that's glowing."])
appgroup('silly', strlist('SILLY') + strlist('FUN') + ['Paint brush!', 'Rainbow paint!', 'Glitter!', 'Stamps! Tap to stamp.', 'Eraser!', 'Slow!', 'Fast!', 'Super fast!'])
m = re.search(r'var ROOM_SAY = \{([\s\S]*?)\};', app)
appgroup('rooms', re.findall(r"'([^']*)'", m.group(1)))
game_names = re.findall(r"name: '([^']*)', std:", PAGE)
appgroup('game-names', [g + '!' for g in game_names])
POT = re.findall(r"\['\w+', '[^']+', (?:'#[0-9A-F]+'|null), '([^']*)'\]", app)
appgroup('potion-parts', POT)
POTIONS = re.findall(r"\{ id: '\w+', name: '([^']*)'", app)
appgroup('potions', ['Poof! ' + p for p in POTIONS] + ['You found a new potion!'])

# lines the app builds from pieces (what each piece can be is listed here)
L = lists['letters']
nums = lambda a, b: [str(i) for i in range(a, b + 1)]
many = lambda n, one, more: one if n == '1' or n == 1 else more
stickers = lists['stickers']
st_say = lists['stickerSays']
st_mid = [x if re.match(r'[A-Z]', n) else x[0].lower() + x[1:] for x, n in zip(st_say, stickers)]
appgroup('counting', nums(0, 100))
appgroup('count-cheer', [str(i) + '!' for i in range(5, 101, 5)] + [str(i) + ' layers!' for i in range(5, 61, 5)] + [str(i) + ' in a row!' for i in range(3, 31, 3)] + [str(i) + ' presents!' for i in range(5, 61, 5)])
appgroup('greet', ['Hi there! Pick a room.'] + ['Hi, %s! Pick a room.' % n for n in NAMES] + ["Hi! I'm Pip. Let's play and learn. Pick a room!"] + ["Hi %s! I'm Pip. Let's play and learn. Pick a room!" % n for n in NAMES])
appgroup('stickers', st_say + ['T rex' if s == 'T. rex' else s for s in stickers])
appgroup('sticker-new', [s + ' It’s in your sticker book.' for s in st_say] + ['You filled a whole page!'])
appgroup('sticker-book', ['You found every sticker!'] + ['%d of %d stickers. %d more %s for the next one!' % (h, len(stickers), nd, 'star' if nd == 1 else 'stars') for h in range(0, len(stickers)) for nd in range(1, 9)])
appgroup('sticker-pages', [t + '!' for t in lists['stickerPages']] + ['You filled this page!', 'Keep earning stars to find this one!', 'Wow! Your sticker book has %d new pages!' % (len(lists['stickerPages']) - 2)])
appgroup('sticker-page-count', ['%d of 15 stickers.' % n for n in range(0, 15)])
appgroup('sticker-next', ['%d more %s to find this one!' % (n, 'star' if n == 1 else 'stars') for n in range(1, 9)])
appgroup('letter-taps', [l + '.' for l in L]); appgroup('find-letter', ['Find the letter ' + l + '.' for l in L]); appgroup('after-letter', ['What comes after ' + l + '?' for l in L]); appgroup('start-letter', ['Start with ' + l + '.' for l in L])
appgroup('spell-hint', ['Listen: ' + w + '. What letter comes next?' for w in lists['spellWords']])
appgroup('colors', [c.capitalize() + '.' for c in lists['colors']])
appgroup('bucket-1', ['Hmm, let’s count again. We need %d.' % t for t in range(1, 21)]); appgroup('bucket-2', ['You have %d. We need %d. %s' % (h, t, 'Put in %d more.' % (t - h) if t > h else 'Take out %d.' % (h - t)) for t in range(1, 21) for h in range(0, 26) if h != t])
EATERS = ['Bear', 'Bunny', 'Piggy', 'Kitty', 'Puppy', 'Panda', 'Froggy', 'Koala']
tops = lists['tops']
pz = [['Hmm, let’s count all the toppings. We need 10.']]
pz.append(['You have %d. We need 10. %s' % (h, 'Add %d more.' % (10 - h) if h < 10 else 'Take off %d.' % (h - 10)) for h in range(0, 16) if h != 10])
pz.append(['Oops! %s did not ask for %s. Tap them to take them off.' % (e, t[1]) for e in EATERS for t in tops])
pz.append(['Hmm, let’s count again. %s wants %d %s.' % (e, n, many(n, *t)) for e in EATERS for n in range(1, 11) for t in tops])
pz.append(['You have %d %s. %s wants %d. %s' % (h, many(h, *t), e, n, 'Add %d more.' % (n - h) if n > h else 'Take off %d.' % (h - n)) for e in EATERS for t in tops for n in range(1, 11) for h in range(0, 13) if h != n])
for k, part in enumerate(pz): appgroup('pizza-fix-%d' % k, part)
appgroup('dots-start', ['Start at %d.' % n for n in (1, 2, 5, 10)]); appgroup('dots-fix', ['Oops! What comes after %d?' % n for n in range(1, 100)])
appgroup('tree-find', ['Find %d.' % n for n in range(1, 101)]); appgroup('tree-start', ['Start with %d.' % n for n in range(1, 101)]); appgroup('tree-tens', ['What comes after %d? Count by tens.' % n for n in range(10, 100, 10)]); appgroup('tree-after', ['What comes after %d?' % n for n in range(1, 20)] + ['Find the smallest number.', 'Find the smallest number left.'])
titles = ['Perfect round!', 'Great job!', 'Good practice!', 'Good try!']
ends = ['%s You got %d %s!' % (t, n, 'star' if n == 1 else 'stars') for t in titles for n in range(0, 6)]
ends += [' Look at your picture! It’s in the Art Gallery.', ' Look at your picture!', ' You moved up a level!', ' And you won a game token! Play a bonus game now, or save it for later.',
         ' Now go open your treasure chest!', ' On to the next stop of your adventure!', ' And you earned a new sticker! Tap the present to open it.']
appgroup('round-end', [e.strip() for e in ends])
shop = re.findall(r"\{ id: '[a-z]-\w+', cat: '\w+', name: '([^']*)', price: (\d+)", app)
appgroup('shop-welcome', ['Welcome to Pip’s Shop! You have %d stars to spend.' % n for n in range(0, 301)])
appgroup('shop-have', ['%s! You have this one.' % nm for nm, p in shop]); appgroup('shop-cost', ['%s! It costs %s stars.' % (nm, p) for nm, p in shop]); appgroup('shop-got', ['You got the %s!' % nm.lower() for nm, p in shop])
adv = ['You finished today’s adventure! Come back tomorrow for a new one.', 'You did all three stops! Tap the treasure chest!', 'Today’s adventure has three stops and a treasure chest. Tap the first stop!', 'On to stop 2!', 'On to stop 3!']
adv += ['Treasure! You found 5 bonus stars, a game token, and a stamp for today!', 'Treasure! You found 5 bonus stars and a stamp for today!', 'Great job today. Pip is getting sleepy!']
adv += ['And a new sticker: ' + m for m in st_mid]
appgroup('adventure', adv)
arc = ['Welcome to Pip’s Arcade! You have %d game %s. Pick a game!' % (n, 'token' if n == 1 else 'tokens') for n in range(1, 31)] + ['Welcome to Pip’s Arcade! Move up a level or open the treasure chest to earn a game token.']
appgroup('arcade', arc)
mt = ['Time’s up!', 'You did it!', 'Beautiful!', 'Great flying!', 'Yummy!', 'Swirly!', 'What a ride!', 'Happy Halloween!', 'Magic!', 'Burp! So full!', 'Goodnight, fireflies!', 'A beautiful butterfly!', 'What a snowman!', 'Snowflake magic!', 'What a memory!', 'Merry Christmas!', 'Great playing!']
appgroup('mini-gallery', ['Your picture is in the Art Gallery.', 'Your painting is in the Art Gallery.', 'Your spin art is in the Art Gallery.', 'Your jack-o’-lantern is in the Art Gallery.', 'Your butterfly is in the Art Gallery.', 'Your snowman is in the Art Gallery.', 'Your snowflake is in the Art Gallery.', 'New best score!', 'Tallest cake yet!', 'Most fireflies yet!', 'Longest pattern yet!', 'Most presents yet!', 'New best!'])
appgroup('mini-titles', mt)
for k, f in enumerate([lambda n: 'You scored %d!' % n, lambda n: 'You grabbed %d points of candy!' % n, lambda n: 'The frog ate %d points of bugs!' % n,
                       lambda n: 'You caught %d %s!' % (n, 'firefly' if n == 1 else 'fireflies'), lambda n: 'You remembered %d %s in a row!' % (n, 'light' if n == 1 else 'lights'),
                       lambda n: 'Santa delivered %d %s!' % (n, 'present' if n == 1 else 'presents')]):
    appgroup('mini-end-%d' % k, [f(n) for n in range(0, 151)])
appgroup('mini-end-pairs', ['You found all the pairs in %d tries!' % n for n in range(6, 61)]); appgroup('mini-end-cake', ['Your cake is %d layers tall!' % n for n in range(1, 61)]); appgroup('mini-end-potions', ['You found %d of 12 potions.' % n for n in range(1, 13)])

# ---------------------------------------------------------------- pieces
TOK = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9’'\-]*[A-Za-z0-9])?|[.,!?;:]")
def units(t):
    """words with any punctuation that follows them ("olives!", "Hi,")"""
    out = []
    for tok in TOK.findall(t):
        if tok in '.,!?;:' and out: out[-1] += tok
        elif tok not in '.,!?;:': out.append(tok)
    return out
def key(u):
    w = u.replace('’', "'")
    core = re.sub(r'[.,!?;:]+$', '', w)
    return w if len(core) == 1 else w.lower()
NUMWORD = re.compile(r'^\d+[.,!?;:]*$')
LETTERS = set(L)

clips = {}            # key -> text
clip_src = collections.defaultdict(set)
def add_clip(text, src):
    k = ' '.join(key(u) for u in units(text))
    if not k: return
    clips.setdefault(k, ' '.join(units(text)))
    clip_src[k].add(src)

ALWAYS_WHOLE = {'story:read', 'story:prompt', 'story:praise', 'read:praise', 'read:prompt', 'app:fixed', 'app:rooms', 'app:game-names', 'app:potions', 'app:potion-parts', 'app:silly', 'app:cheer', 'app:oops', 'app:greet', 'app:round-end', 'app:adventure', 'app:mini-titles', 'app:colors'}
plan_kind = {}
for g, texts in sorted(groups.items()):
    if g in ALWAYS_WHOLE or len(texts) <= WHOLE_MAX:
        plan_kind[g] = 'whole'
        for t in texts: add_clip(t, g)
        continue
    plan_kind[g] = 'pieces'
    rows = [units(t) for t in texts]
    df = collections.Counter()
    for r in rows:
        for u in set(key(x) for x in r): df[u] += 1
    n = len(rows)
    def fixed(u):
        k = key(u); core = re.sub(r'[.,!?;:]+$', '', k)
        if NUMWORD.match(k) or core in LETTERS or core.upper() in LETTERS and len(core) == 1: return False
        return df[k] >= FIX_FRAC * n
    # segments: (signature, text)
    segs = []
    for r in rows:
        s = []
        for u in r:
            if fixed(u):
                if s and s[-1][2]: s[-1] = (s[-1][0] + ' ' + key(u), s[-1][1] + ' ' + u, True)
                else: s.append((key(u), u, True))
            else:
                p = re.search(r'[.,!?;:]+$', u)
                s.append(('{}' + (p.group(0) if p else ''), u, False))
        segs.append(s)
    # join neighbouring pieces while the joined piece still has few versions
    while True:
        cand = collections.defaultdict(set); occ = collections.Counter()
        for s in segs:
            for i in range(len(s) - 1):
                if '{}' in s[i][0] and re.search(r'[.!?]$', s[i][1]): continue   # don't run a number or word on into the next sentence
                sig = s[i][0] + ' ' + s[i + 1][0]
                cand[sig].add(s[i][1] + ' ' + s[i + 1][1]); occ[sig] += 1
        ok = [(occ[sig] / len(v), sig) for sig, v in cand.items() if len(v) <= MERGE_MAX]
        if not ok: break
        ok.sort(reverse=True)
        best = ok[0][1]
        for s in segs:
            i = 0
            while i < len(s) - 1:
                if s[i][0] + ' ' + s[i + 1][0] == best and not ('{}' in s[i][0] and re.search(r'[.!?]$', s[i][1])):
                    s[i:i + 2] = [(best, s[i][1] + ' ' + s[i + 1][1], False)]
                i += 1
    for s in segs:
        for sig, text, _ in s: add_clip(text, g)

# ---------------------------------------------------------------- check: can every line be said with the clips?
maxlen = max(len(k.split(' ')) for k in clips)
def cover(t):
    """fewest clips that say the line (a word with no clip costs a lot); the app will do the same"""
    us = [key(u) for u in units(t)]
    n = len(us); INF = 10 ** 9
    best = [INF] * (n + 1); back = [None] * (n + 1); best[n] = 0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, min(n, i + maxlen) + 1):
            if ' '.join(us[i:j]) in clips and best[j] + 1 < best[i]: best[i] = best[j] + 1; back[i] = (j, True)
        if best[i + 1] + 1000 < best[i]: best[i] = best[i + 1] + 1000; back[i] = (i + 1, False)
    i, pieces, miss = 0, 0, []
    while i < n:
        j, ok = back[i]
        if ok: pieces += 1
        else: miss.append(us[i])
        i = j
    return pieces, miss
fresh = corpus(1500)  # a new random sample the plan has not seen
fresh_groups = collections.defaultdict(set)
for x in fresh['lines']: fresh_groups[x['group']].add(x['text'])
all_groups = dict(groups)
missing = collections.Counter(); miss_lines = []; total = 0; covered = 0; piece_hist = collections.Counter()
for g, texts in list(all_groups.items()) + [('fresh:' + g, t) for g, t in fresh_groups.items()]:
    for t in texts:
        total += 1
        p, miss = cover(t)
        if miss:
            for mm in miss: missing[(g.split(':', 1)[-1] if g.startswith('fresh') else g, mm)] += 1
            if len(miss_lines) < 30: miss_lines.append(t)
        else: covered += 1; piece_hist[min(p, 6)] += 1

# ---------------------------------------------------------------- write
OUT.mkdir(parents=True, exist_ok=True)
def kind(k):
    srcs = clip_src[k]
    if any(s.startswith('app:') for s in srcs) and not any(not s.startswith('app:') for s in srcs): return 'app'
    return 'game'
rows = []
for i, (k, text) in enumerate(sorted(clips.items(), key=lambda kv: (sorted(clip_src[kv[0]])[0], kv[1].lower()))):
    srcs = sorted(clip_src[k])
    rows.append({'id': 'v' + hashlib.sha1(k.encode()).hexdigest()[:10], 'text': text, 'chars': len(text), 'used_by': ' '.join(srcs[:4]) + (' +%d more' % (len(srcs) - 4) if len(srcs) > 4 else '')})
json.dump({'note': 'Every clip Pip needs. text is what the voice says; id is the audio file name (it stays the same as long as the text does).', 'clips': [{'id': r['id'], 'text': r['text']} for r in rows]}, open(OUT / 'lines.json', 'w'), ensure_ascii=False, indent=0)
with open(OUT / 'lines.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'text', 'characters', 'used by'])
    for r in rows: w.writerow([r['id'], r['text'], r['chars'], r['used_by']])
chars = sum(r['chars'] for r in rows)
secs = chars / 13.0 + 0.25 * len(rows)
whole = sum(1 for g in plan_kind if plan_kind[g] == 'whole'); pieces = len(plan_kind) - whole
summary = {
    'clips': len(rows), 'characters': chars, 'audio_minutes': round(secs / 60, 1),
    'download_mb_24kbps_mp3': round(secs * 3000 / 1e6, 1), 'google_cost_usd': round(max(0, chars - 1_000_000) * 30 / 1e6, 2), 'groups_whole': whole, 'groups_in_pieces': pieces,
    'lines_checked': total, 'lines_fully_covered': covered, 'pieces_per_line': dict(sorted(piece_hist.items())),
    'missing_examples': [[g, m, c] for (g, m), c in missing.most_common(25)], 'missing_lines': miss_lines,
    'biggest_piece_groups': sorted([(g, len(groups[g])) for g in plan_kind if plan_kind[g] == 'pieces'], key=lambda x: -x[1])[:15],
}
json.dump(summary, open(OUT / 'summary.json', 'w'), indent=1)
print(json.dumps(summary, indent=1))

if True:  # how each group's lines get split into clips (for checking by eye)
    def split(t):
        us = units(t); ks = [key(u) for u in us]; n = len(ks); INF = 10 ** 9
        best = [INF] * (n + 1); back = [None] * (n + 1); best[n] = 0
        for i in range(n - 1, -1, -1):
            for j in range(i + 1, min(n, i + maxlen) + 1):
                if ' '.join(ks[i:j]) in clips and best[j] + 1 < best[i]: best[i] = best[j] + 1; back[i] = j
        out, i = [], 0
        while i < n and back[i]: out.append(' '.join(us[i:back[i]])); i = back[i]
        return out
    per = collections.defaultdict(list)
    for g, texts in groups.items():
        for t in texts: per[g].append(len(split(t)))
    stats = sorted(((sum(v) / len(v), g, len(v)) for g, v in per.items()), reverse=True)
    with open(OUT / 'pieces_by_group.txt', 'w') as f:
        for avg, g, n in stats:
            ex = sorted(groups[g], key=lambda t: -len(split(t)))[:2]
            f.write('%.2f  %-22s %5d lines   e.g. %s\n' % (avg, g, n, '  ||  '.join(' | '.join(split(t)) for t in ex)))
