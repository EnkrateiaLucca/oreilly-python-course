# Course slides

- `slides.md` — the deck source (Marp markdown, `automata` brand theme)
- `slides.html` — rendered deck; open in any browser, present with `F` (fullscreen) / `P` (presenter view with speaker notes)
- `slides.pdf` — print/handout export

## Editing

Edit `slides.md`, then rebuild with the house scripts:

```bash
# live-reload while editing
~/.claude/skills/marp-slides/scripts/marp-live.sh slides/slides.md

# one-shot export
~/.claude/skills/marp-slides/scripts/marp-build.sh slides/slides.md slides/slides.html

# PDF: build directly so local images (slides/img/) are embedded —
# marp blocks local files in PDF conversion without this flag
cd slides && npx -y @marp-team/marp-cli@latest slides.md --html --no-stdin --allow-local-files \
  --theme-set ~/.claude/skills/marp-slides/assets/brand/automata.css --pdf -o slides.pdf
```

Speaker notes are the plain HTML comments inside each slide — visible in presenter
view and in the source, invisible when presenting.

Bulleted lists written with `*` reveal one-per-keypress while presenting (theme
fragment CSS); `-` lists appear all at once. PDF export always shows everything.
