# The Shape of Speed: Formula 1, 1950–2026

A one-page editorial timeline of six turning points in the shape of Formula 1 cars, plus a small gallery of the cars in between. It is an editorially selected set of milestones, not an official or exhaustive taxonomy of every season or chassis.

**Status:** live on GitHub Pages at https://git.marcuschiu.com/f1-car-generations/ (public repository: https://github.com/TheRealMarcusChiu/f1-car-generations). The GitHub Pages HTTPS-enforcement setting is enabled.

## Layout

```
index.html              the page (static HTML, no JavaScript)
styles.css              layout, palette, type, responsive and reduced-motion rules
assets/images/          11 local photographs from Wikimedia Commons
data/sources.json       the six cited Formula 1 articles (id, title, claim, caveat, URL)
data/images.json        per-image record: file, model, photo context, alt, creator, license, Commons page
research/source-matrix.md   source/claim/caveat matrix, verified 2026-10-19
research/image-audit.md     image checks, model year vs photo context, the excluded Lotus 72
tests/test_site.py      no-dependency verifier (Python standard library only)
```

## Run the tests

From the project root:

```sh
python3 -m unittest discover -s tests -v
```

The tests check the data/citation/asset contract: six milestones with unique IDs and valid source IDs and visible citation links; exactly 11 images, all present locally with alt text, creator, license and Commons page; relative local `<img>` paths only; visible figure credits; wording guards against unsupported technical claims; and the responsive, focus and reduced-motion CSS rules.

### Verification log (2026-10-19)

Latest independent verification (current):

- **Tests** — `Ran 16 tests … OK`.
- **Images** — all 11 local JPEGs decode and match the dimensions recorded in `data/images.json`.
- **Browser check** — all 11 images load; no horizontal overflow at desktop width or at 360px mobile width.
- **GitHub Pages** — Pages API reports status `built`, serves the canonical custom-domain URL https://git.marcuschiu.com/f1-car-generations/, and reports `https_enforced: true`. A direct HTTP request to http://git.marcuschiu.com/f1-car-generations/ also returned 200 (no redirect observed), so HTTP-to-HTTPS redirection is not claimed.

Earlier runs (historical, superseded by the above):

- **Red** — test written before any production file existed: `Ran 5 tests … FAILED (errors=7)` (the five data tests, plus setup errors for the page and style classes; all `FileNotFoundError`).
- **Green** — same test after initial implementation: `Ran 15 tests … OK` (the suite size at that time).
- **Mutation check** — on a throwaway copy, adding a remote image URL, dropping "representative", calling the 2026 rules "upcoming", adding 1962/2009 technical claims, and duplicating a milestone ID made 6 tests fail.

## Serve locally

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```

Opening `index.html` directly from disk also works. Fonts (Newsreader, JetBrains Mono) load from Google Fonts and fall back to local serif/monospace fonts offline. All photographs are local.

## Image credits and licensing

Every image is a Wikimedia Commons 1280px thumbnail; no further edits (downloaded as served, not cropped or re-encoded). Each figure caption credits the photographer, links the license and links the Commons file page; `data/images.json` holds the same records. Photos under CC BY-SA keep their share-alike terms, so any adaptation must use the same license. The RB18 photo is CC0 and is credited anyway.

## Sources

All milestone claims come from six official Formula 1 (formula1.com) articles, listed in `data/sources.json` and `research/source-matrix.md`. This project is not affiliated with Formula 1, the FIA or any team.
