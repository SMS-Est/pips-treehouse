// Collect every line the question generators can produce, grouped by game and kind of line.
// Usage: node voice_corpus.js index.html > corpus.json
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const sc = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const ctx = { window: {} }; vm.createContext(ctx); vm.runInContext(sc[0], ctx);
const C = ctx.window.PipContent, L = C._lists;
const out = new Map();
const add = (t, group) => { if (typeof t !== 'string' || !t.trim()) return; const k = group + '\u0001' + t; if (!out.has(k)) out.set(k, { text: t, group }); };
const N = +(process.argv[3] || 4000);
for (const g of C.GAMES) for (let lv = 1; lv <= g.levels.length; lv++) {
  const qs = [];
  if (g.genRound) { for (let n = 0; n < Math.round(N / 20); n++) qs.push(...g.genRound(lv, []).questions); }
  else for (let n = 0; n < N; n++) qs.push(g.gen(lv));
  for (const q of qs) {
    const story = g.id === 'story';
    (Array.isArray(q.say) ? q.say : [q.say]).forEach(p => add(typeof p === 'string' ? p : p.t, g.id + (story && p.read ? ':read' : ':prompt')));
    add(q.praise, g.id + ':praise'); add(q.hint, g.id + ':hint');
    (q.again || []).forEach(p => add(typeof p === 'string' ? p : p.t, g.id + ':recap'));
    (q.steps || []).forEach(st => { add(st.say, g.id + ':step'); add(st.hint, g.id + ':hint'); });
    if (q.stage && q.stage.word) add(q.stage.word + '.', 'tap-word');
    if (typeof q.word === 'string') add(q.word, 'tap-word');
    if (q.pic && q.pic.word) add(q.pic.word, 'tap-word');
    if (q.type === 'bells') add(C.cap(q.word) + '.', 'tap-word');
  }
}
const lists = {
  letters: 'abcdefghijklmnopqrstuvwxyz'.split('').map(c => C.L(c)),
  stickers: C.STICKERS.map(s => s.name),
  stickerSays: C.STICKERS.map(s => s.say),
  stickerPages: C.STICKER_PAGES.map(p => p[0]),
  spellWords: [...new Set([...L.CVC, ...L.BLEND, ...L.FOOD_SHORT, ...L.FOOD_LONG, ...L.STAR_SHORT, ...L.SPACE_LONG])],
  tops: L.TOPS.map(t => [t.one, t.more]),
  colors: Object.keys(L.PCOL)
};
console.log(JSON.stringify({ lines: [...out.values()], lists }));
