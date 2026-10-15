# Pip's Treehouse (v1.11.0)

Kindergarten reading, spelling and math games. Pip reads every question out loud.

## Files (all go in the repo root)
- `index.html` — the whole app
- `manifest.webmanifest` — makes it installable from Safari's Share > Add to Home Screen
- `sw.js` — offline support (saves every file on the device; opens from that copy)
- `fonts/` — the two fonts, bundled so nothing loads from the internet
- `icons/` — home-screen icons
- `netlify.toml` — Netlify settings (no build step; publishes the repo root)

## Deploy
Netlify > Add new site > Import an existing project > GitHub > pick this repo.
Leave the build command empty and the publish directory as `.`

## On the iPad
Open the Netlify URL in Safari > Share > Add to Home Screen. Open it from the new icon
once while on Wi-Fi; after that it works with no internet. Progress is saved on that
iPad (in the home-screen app). After a new deploy, open it once on Wi-Fi, close it,
and open it again to get the update.
