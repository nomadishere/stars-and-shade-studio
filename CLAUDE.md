# Stars & Shade Studio (private)

This repo is the permanent home of the Stars & Shade deck: the full-size final cards, the masters, and every tool used to build or change them. Justin's rule: nothing is ever "lost with the old workspace" again.

## Rules for every session
- Anything you make or change for the deck (a card, a song, a script, a source file) gets committed here before you finish. Not only in /tmp.
- Change only what Justin or his mom asked for. Don't make variations or re-render other cards.
- The public website lives in nomadishere/stars-and-shade (web-size copies in deck/ and p/). If a card changes here, update the web copy there too: downscale to 540×960, lanczos, 975 kbps 2-pass H.264 Main, audio stream copied, poster = frame 112 as p/NNN.jpg.
- Push big files in small batches (about 80 MB per push) so the git proxy doesn't reject the request.
- Read README.md for where everything is and how the cards are built.
