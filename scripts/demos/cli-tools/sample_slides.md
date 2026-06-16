# Automate Tasks with Python

A 60-second demo deck

Built from plain Markdown by `slides.py`

---

## Why CLI tools?

- One command, one job
- Easy to share and re-run
- They glue together with pipes: `cmd1 | cmd2`

---

## How this deck was made

1. You wrote Markdown (this file)
2. `slides.py` wrapped it in an HTML template
3. remark.js renders it in the browser

No PowerPoint involved.

---

## Try it yourself

```bash
uv run scripts/demos/cli-tools/slides.py my_talk.md --open
```

Use a line with just `---` to start a new slide.

---

# Thanks!

Questions? Open an issue or ask the AI tutor:

`uv run scripts/ask.py "How does remark.js split slides?"`
