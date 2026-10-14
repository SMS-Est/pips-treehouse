# Pip's recorded voice: the clip list

`lines.csv` / `lines.json` list every clip Pip needs so her voice can be recorded once
(Google Cloud Text-to-Speech, Chirp 3: HD) and play offline on the iPad.

- Lines that only come in a few versions are recorded **whole** so they sound natural
  ("Find the smallest number.", "Snowman Maker! Pick a hat…").
- Lines that come in thousands of versions are recorded in **pieces** that join at natural
  pauses: "Kitty wants | 5 pineapples | and 2 tomatoes!", "98 | is bigger than | 72!".
- The app will say a line by joining the fewest clips that cover it. The planner checks
  every line the games can produce (plus a fresh random sample) against the list.

Rebuild the list after changing what Pip says:

    python3 voice/voice_plan.py index.html voice

Files: `voice_corpus.js` collects the game lines, `voice_plan.py` picks the clips and writes
`lines.json`, `lines.csv`, `summary.json` and `pieces_by_group.txt` (how lines get split).
Put the child's name in `names.txt` (one per line) so "Hi, ___!" gets recorded too.
