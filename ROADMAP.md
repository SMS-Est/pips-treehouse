# Pip's Treehouse — Roadmap

## Next up: natural voice for Pip (not started — Nick to review)

**Problem:** Pip uses the device's built-in voice, which sounds robotic on both iPad and Android.

### Option 1 — Better built-in voice (free, try first, ~5 min)
- **iPad:** Settings → Accessibility → Spoken Content → Voices → English → download an
  "Enhanced" or "Premium" voice (e.g. Ava, Zoe, Evan). Then in the app: Grown-ups → Pip's voice.
- **Android:** Settings → Text-to-speech → Google engine → install a higher-quality English voice.
- Clear improvement, but still a computer voice. Not every premium voice is guaranteed to show up
  for web apps — check the voice list in Grown-ups after downloading.

### Option 2 — Recorded natural AI voice bundled in the app (recommended)
Generate every line Pip says once with a natural voice service, store the audio files in this repo,
and let the app cache them on the device like the rest of the app.

- **Why:** realistic voice, identical on iPad and Android, **still works offline in the car**,
  no ongoing cost, and it unlocks real phonics sounds ("buh", "ah") that robotic voices can't say.
- **Services:** ElevenLabs (most natural, character-style voices) · OpenAI TTS or Google Cloud TTS
  (cheaper, still natural). Confirm current pricing before choosing.
- **Measured size (Oct 13):** as written today, Pip can say ~15,000 distinct sentences (mostly
  math praise like "47 is bigger than 23!") ≈ 150 MB — too big. Plan is to rework speech into
  reusable pieces (numbers, words, short phrases): **~2,000 clips, ~25 MB, ~70k characters**.
  One-time generation cost: roughly free to ~$20 depending on the service.

**Nick's steps (browser-only, works from the Chromebook):**
1. Create an account with the chosen voice service and pick a voice.
2. Add its API key as a GitHub repository secret (Settings → Secrets and variables → Actions).
3. Click **Run workflow** on the GitHub Action Claude writes. It records all clips, commits them,
   and Netlify redeploys.

**Clip list (done Oct 14):** `voice/lines.csv` — about 8,500 clips, ~181,000 characters (inside Google's
free 1 million characters a month for Chirp 3: HD, so $0), about 4 hours of audio, ~45 MB on the
iPad. Every line the games can say is covered. Rebuild with `python3 voice/voice_plan.py index.html voice`.

**Claude's build:**
- Rework spoken text into reusable pieces; list every clip the games can need.
- Generation script + GitHub Action (re-run with one click when games or words change).
- Audio player that plays clips in order with the existing pauses and highlights, and falls back
  to the device voice for anything missing.
- Add true letter sounds to Letter Sounds / Ghost Letters once recordings exist.

**Trade-offs:** math sentences stitched from pieces sound slightly less smooth than whole
sentences; first install downloads ~25 MB on Wi-Fi; new words need the Action re-run.

### Option 3 — Live cloud voice (not recommended)
Needs internet (breaks car play), costs money per use, and needs a server to hide the API key.

---

## Ideas backlog
- Record Mom & Dad cheers ("Great job!") from the Grown-ups page, played on right answers.
- Pip says her name in praise (best after the recorded-voice upgrade).
- More seasonal rooms: Valentine's Day (February), spring/Easter (March–April).
- Player profiles so another child can have their own progress and levels.
- Weekly progress summary to Nick's phone (could use the existing Apps Script setup), and/or
  sync progress across devices.

## Done
- v1.0–1.1: 12 games (reading + math), adaptive levels, stickers, grown-ups progress page,
  installable offline web app on Netlify.
- v1.2: Halloween Hollow (4 games), pauses between spoken choices with highlighting.
- v1.3: Celebrations (sparkles, flying stars, streaks, confetti, sticker presents).
- v1.4: Daily Adventure, Pip's Shop, Trace Letters / Trace Numbers, Story Time.
- v1.5: Pip's Arcade — game tokens from level-ups and the daily chest; Balloon Pop,
  Sticker Match, Color Pip's World (with Art Gallery). Second-grade levels labeled accurately.
- v1.5.1: Fixed how Pip says letter names (cat/bat/leg), full speech audit.
- v1.6: Three new rooms (10 games). Pip's Bakery: Cookie Jar with Foxy the cookie thief
  (silly walks, robber sack, take-away / give-back / "how many did Foxy eat?"), Pizza Shop,
  Cupcake Shop, Mixing Bowl. Art Studio: Color by Number, Color by Letter, Dot-to-Dot, plus
  Paint Studio in the Arcade (brushes, rainbow, glitter, stamps; saves to the Art Gallery).
  Space Station: Rocket Launch, Alien Beam-Up, Star Spell.
- v1.7: Seven themed Arcade games: Rocket Ride, Alien Pop-Up (space), Cake Stacker (bakery),
  Spin Art (art), Broom Ride, Pumpkin Carver, Potion Lab (Halloween, seasonal). Arcade sorted
  into sections; each themed room has doors to its bonus games.
- v1.8: Bug Garden room. Ladybug Spots (count spots, add both wings, how many more), Caterpillar
  ABCs (next letter, missing small letter, put letters in ABC order), Butterfly Match (same
  letter, big/small, b-d-p-q, first sounds), Bee & Flowers (numbers to 20, one more / one less).
  Bug Arcade games: Frog Snack, Firefly Night, Butterfly Painter (mirror painting, saves to the
  Art Gallery).
- v1.9: Winter Wonderland room (shows Nov 8 – end of February; Grown-ups can switch it on or off).
  Jingle Bell Syllables (clapping syllables), Snowball Toss (letters and sight words), Cocoa Count
  (ten-frames: make 10, teen numbers), Light the Tree (number order, counting by tens). Winter
  Arcade games: Snowman Maker, Snowflake Cutter, Tree Lights (memory), Santa's Sleigh.
- v1.10: Sticker book grew from 30 to 210 stickers on 14 themed pages (Pets and Farm, Under the
  Sea, In the Garden, Wild Animals, Outer Space, Yummy Food, Things That Go, Magic and Fairy Tales,
  Toys and Games, Music Time, Halloween, Winter Wonderland). Page arrows, dots and swipe; locked
  stickers show as shadows. Stars earned after the first 30 were full don't count, so each new
  sticker still comes in a present.

## More game ideas (later)
- More Foxy: Foxy steals pizza toppings or cupcake sprinkles in other Bakery games.
- Space: Moon Shapes (find shapes on the moon), Planet Sight Words.
- Art: Pattern Painter.
- Bugs: Ant Line (skip counting by 2s, 5s, 10s), Spider Web Sight Words, Bug Hotel sorting.

## More Arcade ideas (later)
- Catch the Apples: slide a basket to catch fruit while Pip counts out loud.
- Pizza Toss, Cookie Decorator, Snowball Fun (winter room).
