# Research: Simon Willison — "Building Python tools with a one-shot prompt using uv run and Claude Projects"

- Source article: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/
- Researched for: course slide titled **"Using AI != Slop"**
- Slide's current angle: using AI for coding doesn't automatically mean low-quality "slop" — it requires deliberate craft and intention.

---

## What the article actually is

This is primarily a **workflow** post, not a polemic essay titled "AI isn't slop." Willison shows that Claude can reliably one-shot complete, runnable Python CLI tools and small web apps when you give it the right reusable context (a Claude Project with custom system instructions) and the right packaging mechanism (`uv run` + inline dependencies). [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

This matters for the "Using AI != Slop" slide because the *mechanism* of his success — deliberate setup, reusable instructions, and a self-contained runnable artifact — is exactly the "craft and intention" the slide argues for. The quality comes from the human's deliberate scaffolding, not from luck.

> Note on extraction honesty: this article does **not** contain an explicit, quotable passage about "reviewing/testing code before trusting it" or "human expertise being required." Two independent fetches confirmed the article focuses on the workflow rather than on quality-assurance rhetoric. Claims below that go beyond the article's literal text are marked `[unverified]` or framed as interpretation. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

---

## Key points (verified from the article)

1. **Reusable, intentional context is the lever.** Willison drives quality by storing custom instructions in a Claude Project so every prompt inherits a known good style and packaging convention — he isn't re-deriving quality each time. "providing just a short example is enough to get the models to write code that takes advantage of its capabilities." [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

2. **Self-contained, runnable artifacts via PEP 723 / `uv run`.** The generated scripts declare their own dependencies inline so anyone can run them with no setup: "This is an example of inline script dependencies, a feature described in PEP 723 and implemented by `uv run`. Running the script causes `uv` to create a temporary virtual environment with those dependencies installed, a process that takes just a few milliseconds." [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

3. **Specific, capability-aware prompts produce real tools.** His prompts name the libraries and the exact behavior, e.g. an S3 debugging CLI: "Write me a Python CLI tool using Click and boto3 which takes a URL of that form and then uses EVERY single boto3 trick in the book to try and debug why the file is returning a 404." The output ran immediately. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

4. **Small, well-scoped web tools work the same way.** Example: "Starlette web app that provides an API where you pass in ?url= and it strips all HTML tags and returns just the text, using beautifulsoup." Also worked first try. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

5. **Trust is explicitly acknowledged as the user's responsibility.** The one place verification surfaces: "Anyone with `uv` installed can run the following command (provided you trust me not to have replaced the script with something malicious)." This is the seed of the "not slop" point — you are accountable for what you ship. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

6. **The system prompt encodes taste.** His Python Project instructions enforce the inline-dependency format (`# /// script`, `requires-python`, `dependencies`); his HTML/JS Project instructions enforce concrete style rules (avoid React, vanilla HTML/CSS/JS, two-space indents, universal box-sizing, 16px inputs, Helvetica). Quality = his preferences baked into reusable instructions. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

---

## Decision — how to reflect this in the "Using AI != Slop" slide

Recommend leading the slide with these 3-5 slide-relevant points, framed as *the difference between slop and craft is what the human brings to the prompt*:

1. **Slop comes from vague prompts; craft comes from specific, capability-aware prompts.** Show his S3-debug or HTML-stripper prompt as the "good prompt" example — it names the libraries, the input, and the exact behavior. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

2. **Reusable context beats one-off prompting.** Willison's Claude Project instructions mean his standards are applied every time. Slide takeaway: encode your conventions once; don't re-roll the dice each prompt. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

3. **Ship self-contained, runnable artifacts.** The `uv run` + PEP 723 inline-dependency pattern is a concrete "anti-slop" practice already taught in this course — connect the slide directly to the course's existing `uv run` workflow. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

4. **You own what you run.** Use his "provided you trust me not to have replaced the script with something malicious" line to make the accountability point: AI output is a draft you are responsible for, which is precisely why it isn't slop when done right. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

**Suggested slide one-liner:** "AI doesn't produce slop — vague prompts and zero review do. Bring specificity, reusable standards, and ownership."

**Caution for slide authors:** Do **not** attribute to Willison an explicit "always review/test the code" quote from this article — it isn't there. If the slide needs a TDD/review citation, pull it from the companion red-green TDD guide (see `research/tdd-agentic-patterns.md`) rather than misquoting this post. [source: https://simonwillison.net/2024/Dec/19/one-shot-python-tools/]

---

## `[unverified]` items
- `[unverified]` That Willison personally reads/reviews every generated script before using it. (Plausible from his broader writing, but this specific article makes no such statement.)
- `[unverified]` Any claim that "human expertise is required" as a stated thesis of *this* article. The expertise is demonstrated implicitly through his prompts and instructions, but not asserted as a quote.
