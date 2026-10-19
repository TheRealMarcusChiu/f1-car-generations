# Image audit

Audit date: 2026-10-19. The persistent, normalized source and credit records for every shipped image (file, Commons title and page, creator, license name and HTTPS license URL, model, photo context, alt text) are in `data/images.json`. The 12 candidate records were first gathered in a temporary research manifest outside the project; that manifest was ephemeral and is not shipped or relied on here.

## Method

- Eleven photo file pages were requested directly and checked for HTTP 200, file title, creator, license link and description; a contact sheet of the candidates was inspected visually.
- For each retained file the Wikimedia-generated 1280px-wide thumbnail was downloaded with `curl` into `assets/images/`. Files are saved byte-for-byte as served: **Wikimedia Commons 1280px thumbnail; no further edits** (no crop, resize, re-encode or colour change).
- All 11 downloads succeeded (each is a 1280px-wide baseline JPEG). No asset was substituted, generated or hotlinked.
- Credits, license names/links and Commons page links are recorded in `data/images.json` and shown in every figure caption. CC BY-SA files keep their share-alike terms: anyone adapting those images must release the adaptation under the same license.

## Model year vs photo context

A car’s model year is not the year the photo was taken. Almost all of these are later photos of historic cars at festivals, shows or museums, and the captions keep the two apart:

| Local file | Model | Photo context (from Commons) | Creator | License |
|---|---|---|---|---|
| `1950-alfa-romeo-158.jpg` | Alfa Romeo 158/9 | Later display at the Silverstone Festival, **not** an in-period 1950 race photo | David Merrett | CC BY 4.0 |
| `lotus-79.jpg` | Lotus 79 (Ronnie Peterson’s) | Goodwood Festival of Speed, 2014 | Nic Redhead | CC BY-SA 2.0 |
| `mercedes-w05-hybrid.jpg` | Mercedes F1 W05 Hybrid | On display at the 2015 Malaysian GP (photo/event year 2015) | Morio | CC BY-SA 4.0 |
| `2022-red-bull-rb18.jpg` | Red Bull RB18 | Static display; location/date not stated, so none is given | Calreyn88 | CC0 (still credited) |
| `2026-alpine-a526.jpg` | Alpine A526 (Franco Colapinto) | Free Practice, 2026 Australian GP (in-period) | Yu Chu Chin | CC BY-SA 4.0 |
| `1959-cooper-t51.jpg` | 1959 Cooper T51 | David Brabham demonstration, Goodwood Festival of Speed, 2009 | Bahnfrend | CC BY-SA 4.0 |
| `lotus-25.jpg` | Lotus 25 (Jim Clark’s) | Museum photo, Donington Grand Prix Collection | John Chapman (Pyrope) | CC BY-SA 3.0 |
| `1988-mclaren-mp4-4.jpg` | 1988 McLaren-Honda MP4/4 | On display, Goodwood Festival of Speed, 2009 | Bahnfrend | CC BY-SA 4.0 |
| `1992-williams-fw14b.jpg` | 1992 Williams-Renault FW14B | 1992 car show, NEC Birmingham; the file title names Nigel Mansell | Martin Pettitt | CC BY 2.0 |
| `2004-ferrari-schumacher.jpg` | Ferrari, 2004 (Michael Schumacher) | United States GP, Indianapolis, 2004 (in-period) | Rick Dikeman | CC BY-SA 3.0 |
| `2009-brawn-bgp-001.jpg` | 2009 Brawn BGP 001 | On display, Goodwood Festival of Speed, 2009 | Bahnfrend | CC BY-SA 4.0 |

Commons descriptions sometimes include win counts or other superlatives (e.g. the Alfa 158 record). None of those statistics are copied into the site text.

## Excluded

- **`File:Lotus 72 at Formula 1 Exhibition, London 01.jpg`** (Hullian111, CC BY-SA 4.0). Reason: on the contact sheet it is visibly much darker than the retained shortlist. Its long exhibition-plaque description also carries claims (including a 1962 monocoque story) that the verified sources do not support. Not downloaded.
