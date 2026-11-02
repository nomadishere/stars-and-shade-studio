# Stars & Shade Studio

Private home for the 44-card Stars & Shade learning deck by Justin's mom (Tutu).

## What's here
| Folder | What it is |
|---|---|
| `final-1080/` | **The finished deck.** All 44 cards, 1080×1920, 23.976 fps, 7.29 s seamless loops, with the FINAL music (review round r-oct31-3: 33 tracks she loved + 11 re-made with a beat). This is what gets sold and posted. |
| `masters/` | Originals kept before any edit. `027_House_05_ORIGINAL_I-EXPRESS.mp4` is the Fifth House card before Mom's Nov 1 correction to I CREATE. |
| `tools/` | Scripts used to build or change cards (see below). `027-data/` holds the measurements used for the Fifth House fix. |

## Where else things live
- **Website** (public): github.com/nomadishere/stars-and-shade. The site is served from its gh-pages branch. Web-size cards are in `deck/`, posters in `p/`.
- **Google Drive** (Justin's, shared to anyone with the link): the Oct 29 full-size render.
  - All 44: https://drive.google.com/drive/folders/1-DvXf9H5enOY5C2uzxcMHV9G_5NEBe11
  - 34 of them: https://drive.google.com/drive/folders/1guoVY9UGfPpEsO2N9_hF3R21-ZdaGdez
  - The video in those files is identical to `final-1080/`, but their music is OUTDATED. Use `final-1080/` instead.
  - To download, run `curl -sSL "https://drive.usercontent.google.com/download?id=FILE_ID&export=download&confirm=t" -o out.mp4`. To list a folder's IDs, use `gdown.download_folder(url, skip_download=True)`. Justin allowed drive.google.com and drive.usercontent.google.com in claude.ai Settings → Capabilities.
- **Claude project "Stars & Shade - Tutu astrology teaching deck"**: docs `claude/STUDIO-RUNBOOK.md`, `claude/music-handoff.md` (music history, ElevenLabs prompts and tools), `claude/deck-production-status.md` (locked design), `claude/shade-oracle.md` (Skye the AI astrologer, accounts).

## How a final card was assembled (Nov 1, 2026)
- **Video:** the Oct 29 full-size render (Drive), retimed with `-itsscale 1.001` to 24000/1001 fps (stream copy, no re-encode). The card keeps all 175 frames and its 7.29 s length.
- **Audio:** stream-copied from the website card (`deck/NNN_*.mp4` in the site repo). That audio is the final r-oct31-3 music, already cut to an exact seamless loop.
- **Exception, 027 Fifth House:** rebuilt so the motto reads I CREATE (see below), then encoded with H.264 High at crf 16, audio copied.

## Locked card design
- **Timing:** 7.29 s loop, 175 frames, 16 beats at about 131.66 BPM.
  - Title flies in about frame 11.
  - The motto flies in from above (frames 81–98) and settles (98–133).
  - Flare at 134, then the glitter dissolve (136–165).
- **Lettering:** DejaVu Sans Bold, metallic gold. All text is centered at x=540.
  - Title is 96 px (it shrinks to fit long titles). The motto is 90% of the title (86.4 px when the title is 96), with its cap top at y=1446.
  - The zinger is set in Comfortaa.
  - A soft dark shadow (blur σ≈10 px, strength 1.37) and a gold glow (rgb 133,83,38, blur σ≈14 px) sit around the words.
- **Skies:** each section shares one sky, and every card in a section has the identical sky and the same darkening behind the text. Low-res sky loops are in the site repo at `sky/*.mp4`.

## Changing words on an existing card
`tools/comp_hd.py` is the method used for 027 (I EXPRESS → I CREATE):
- **New letters:** taken from sibling cards in the same section at the same frame (C and T from 025 "I CONNECT", A from 032 "I ACHIEVE", the rest from 027 itself). They come out with identical font, gold shading, fly-in and glitter timing, then are moved to the new word's layout (Pillow RAQM layout).
- **Sky under the old word:** recovered by undoing the shadow/glow model. During the flare frames it's borrowed from a card with a shorter motto (024 "I VALUE").
- **After about frame 143:** the glitter cloud is left as it was.
- **Work files:** the script expects frames extracted to PNG (`ffmpeg -i card.mp4 NNN_%03d.png`) and the low-res sky frames. `tools/comp.py`, `glyph.py`, `fit.py` and `bg3.py` are the 540-wide versions used to measure the fly-in and the scrim. Their outputs are in `tools/027-data/`.

## Mom's corrections log
- **Nov 1, 2026:** Fifth House motto is **I CREATE**; the Sun keeps I EXPRESS. Card 027 was updated here, on the website, and in Skye's knowledge.
