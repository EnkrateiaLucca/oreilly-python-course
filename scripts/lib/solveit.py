"""
solveit.py — a tiny, teachable SolveIt-style toolkit for Jupyter notebooks.

Inspired by Jeremy Howard's SolveIt (https://solve.it.com), which builds on
George Pólya's "How to Solve It" (1945). The whole philosophy in four ideas:

  1. DIALOGUE, not prompting   -> talk *with* the AI over many small turns.
  2. PÓLYA's loop              -> Understand -> Plan -> Do (tiny steps) -> Review.
  3. TINY STEPS + feedback     -> 1-2 lines, run it, look at the result, repeat.
  4. THE HUMAN IS THE AGENT    -> the AI proposes; *you* read, edit, and run.

This module gives you a handful of functions that make those four ideas the
path of least resistance inside a normal notebook. Drop it next to your
notebook and start a class with:

    import sys; sys.path.append("..")     # if solveit.py is one level up
    from solveit import *

Then use `ask(...)`, `tutor.ask(...)`, `hint(...)`, `explain(...)`,
`explain_error()`, `propose(...)`, `quiz(...)`, `review(...)`.

Backend: defaults to a fast, free, fully-local model — **gemma4 via Ollama** —
so the whole toolkit works offline with no API key. Falls back to
ANTHROPIC_API_KEY (Claude) or OPENAI_API_KEY (GPT) if Ollama isn't installed.
Override anything with `configure(model=..., backend=...)` or env vars
SOLVEIT_MODEL / SOLVEIT_BACKEND (e.g. SOLVEIT_BACKEND=anthropic).
"""

from __future__ import annotations
import os
import sys
import re
import csv
import json
import base64
import string as _string
import datetime
import tempfile
import textwrap

# ----------------------------------------------------------------------------
# Rendering helpers (degrade gracefully outside Jupyter)
# ----------------------------------------------------------------------------
try:
    from IPython.display import Markdown, HTML, display, update_display
    from IPython import get_ipython
    _IN_NB = get_ipython() is not None
except Exception:  # pragma: no cover - not in IPython
    _IN_NB = False

    def display(*a, **k):
        print(*a)

    def update_display(*a, **k):
        pass

    class Markdown(str):  # type: ignore
        def __init__(self, x): self.data = x

    class HTML(str):  # type: ignore
        def __init__(self, x): self.data = x

    def get_ipython():
        return None


def md(text: str):
    """Render `text` as Markdown in the notebook (plain print elsewhere)."""
    if _IN_NB:
        display(Markdown(text))
    else:
        print(text)
    return None


def html(markup: str):
    """Render raw HTML in the notebook (plain print elsewhere)."""
    if _IN_NB:
        display(HTML(markup))
    else:
        print(markup)
    return None


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
_CFG = {
    "backend": os.environ.get("SOLVEIT_BACKEND"),   # "ollama" | "anthropic" | "openai"
    "model": os.environ.get("SOLVEIT_MODEL"),       # e.g. "gemma4", "claude-sonnet-4-6"
    "max_tokens": 4096,
    "stream": True,
}

# Local-first: gemma4 over Ollama is the default — fast, free, no API key.
_DEFAULTS = {
    "ollama": "gemma4",
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-5.4-mini",
}

# Speed/quality knobs for the local Ollama backend. `keep_alive` keeps the model
# resident between cells (no reload cost); a low temperature + capped output make
# replies fast and focused — exactly what a tiny-steps tutoring loop wants.
_OLLAMA_OPTS = {
    "temperature": 0.3,
    "top_p": 0.9,
}
_OLLAMA_KEEP_ALIVE = "30m"

# Prepended to every system prompt so answers stay short and fast across ALL
# tools, while still obeying any explicit format instruction in the request
# (e.g. "return ONLY JSON" or "produce a full HTML document").
_BREVITY = (
    "Be concise and fast. Skip preamble, filler, and don't restate the question. "
    "Prefer one tiny runnable example over long prose; stop as soon as the point "
    "is made. Still follow any explicit formatting instruction in the request "
    "exactly (e.g. 'return ONLY JSON', or producing a complete HTML document)."
)

# Image generation is its own backend (text and images can use different vendors).
_IMG_CFG = {
    "backend": os.environ.get("SOLVEIT_IMAGE_BACKEND"),   # "gemini" | "openai"
    "model": os.environ.get("SOLVEIT_IMAGE_MODEL"),
}
_IMG_DEFAULTS = {
    "gemini": "gemini-3-pro-image-preview",   # "nano banana pro"
    "openai": "gpt-image-2",
}

# A breadcrumb trail of what the learner did this session, so `recap()` can
# summarize the WHOLE session — not just the turns that went through `tutor`.
_SESSION_LOG: list[dict] = []


def _log(action: str, detail: str = ""):
    detail = (detail or "").strip().replace("\n", " ")
    if len(detail) > 140:
        detail = detail[:137] + "…"
    _SESSION_LOG.append({"action": action, "detail": detail})


def session_log():
    """Return the raw list of this session's logged actions."""
    return list(_SESSION_LOG)


def _detect_backend() -> str:
    if _CFG["backend"]:
        return _CFG["backend"]
    # Local-first: prefer gemma4 over Ollama when the package is installed.
    if _can_import("ollama"):
        return "ollama"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    # default guess; will raise a friendly error at call time if unreachable
    return "ollama"


def configure(backend: str | None = None, model: str | None = None,
              max_tokens: int | None = None, stream: bool | None = None):
    """Override defaults for the session. e.g. configure(model='gpt-5')."""
    if backend is not None:
        _CFG["backend"] = backend
    if model is not None:
        _CFG["model"] = model
    if max_tokens is not None:
        _CFG["max_tokens"] = max_tokens
    if stream is not None:
        _CFG["stream"] = stream
    b = _detect_backend()
    md(f"**solveit configured** · backend=`{b}` · model=`{_CFG['model'] or _DEFAULTS[b]}`")


# ----------------------------------------------------------------------------
# LLM backends — streaming generators of text chunks
# ----------------------------------------------------------------------------
def _model_for(backend: str) -> str:
    return _CFG["model"] or _DEFAULTS[backend]


def _stream_chunks(messages, system):
    """Yield text chunks from whichever backend is active."""
    backend = _detect_backend()
    model = _model_for(backend)

    if backend == "ollama":
        try:
            import ollama
        except ImportError:
            raise RuntimeError("pip install ollama  (or configure(backend='anthropic'/'openai'))")
        msgs = ([{"role": "system", "content": system}] if system else []) + messages
        try:
            stream = ollama.chat(
                model=model, messages=msgs, stream=True,
                keep_alive=_OLLAMA_KEEP_ALIVE,
                options={**_OLLAMA_OPTS, "num_predict": _CFG["max_tokens"]})
            for chunk in stream:
                piece = (chunk.get("message") or {}).get("content") \
                    if isinstance(chunk, dict) else getattr(chunk.message, "content", "")
                if piece:
                    yield piece
        except Exception as e:
            raise RuntimeError(
                f"Ollama call failed ({type(e).__name__}: {e}). Is the Ollama app "
                f"running and is the model pulled?  Try: `ollama pull {model}`  "
                "(or switch with configure(backend='anthropic'/'openai')).")

    elif backend == "anthropic":
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("pip install anthropic  (or configure(backend='openai'))")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("Set ANTHROPIC_API_KEY (or configure(backend='openai')).")
        client = anthropic.Anthropic()
        with client.messages.stream(
            model=model,
            system=system or "You are a helpful assistant.",
            messages=messages,
            max_tokens=_CFG["max_tokens"],
        ) as stream:
            for text in stream.text_stream:
                yield text

    elif backend == "openai":
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("pip install openai  (or configure(backend='anthropic'))")
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("Set OPENAI_API_KEY (or configure(backend='anthropic')).")
        client = OpenAI()
        msgs = ([{"role": "system", "content": system}] if system else []) + messages
        resp = client.chat.completions.create(model=model, messages=msgs, stream=True)
        for chunk in resp:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    else:
        raise RuntimeError(f"Unknown backend: {backend!r}")


def _compose_system(system: str | None) -> str:
    """Fold the global brevity directive into whatever system prompt is in use."""
    base = system.strip() if system else "You are a helpful assistant."
    return f"{base}\n\n{_BREVITY}"


def _run(messages, system=None, stream=None, render=True) -> str:
    """Core call. Streams into the notebook live and returns the full text."""
    stream = _CFG["stream"] if stream is None else stream
    system = _compose_system(system)
    acc = ""

    if render and _IN_NB and stream:
        handle = display(Markdown("▌"), display_id=True)
        for chunk in _stream_chunks(messages, system):
            acc += chunk
            handle.update(Markdown(acc + " ▌"))
        handle.update(Markdown(acc))
    else:
        for chunk in _stream_chunks(messages, system):
            acc += chunk
        if render:
            md(acc)
    return acc


# ----------------------------------------------------------------------------
# 1) ask — one-shot question, pretty-rendered
# ----------------------------------------------------------------------------
def ask(prompt: str, *, system: str | None = None, render: bool = True,
        stream: bool | None = None, _loggable: bool = True):
    """Ask the AI a single question. Renders Markdown in the notebook.

    Returns None when it has already rendered into the notebook (so Jupyter
    doesn't also echo the raw string). Pass `render=False` to get the text back.

    >>> ask("In one sentence, what is a Python list?")   # renders, returns None
    >>> txt = ask("...", render=False)                    # returns the string
    """
    out = _run([{"role": "user", "content": prompt}], system=system,
               stream=stream, render=render)
    if render and _loggable:
        _log("asked a question", prompt)
    return None if (render and _IN_NB) else out


# ----------------------------------------------------------------------------
# 2) Dialogue — persistent conversation (this is "dialogue engineering")
# ----------------------------------------------------------------------------
class Dialogue:
    """A running conversation that remembers prior turns.

    The whole point of SolveIt: don't fire one-shot prompts, hold a
    *dialogue*. Each `.ask()` appends to history so the AI keeps context.

        chat = Dialogue(system="You are a patient Python tutor.")
        chat.ask("What's a dictionary?")
        chat.ask("Show me a tiny example.")   # remembers the previous turn
    """

    def __init__(self, system: str | None = None, name: str = "dialogue"):
        self.system = system
        self.name = name
        self.history: list[dict] = []

    def ask(self, prompt: str, *, render: bool = True,
            stream: bool | None = None):
        self.history.append({"role": "user", "content": prompt})
        out = _run(self.history, system=self.system, stream=stream, render=render)
        self.history.append({"role": "assistant", "content": out})
        # Don't echo the raw string when we've already rendered it in the notebook.
        return None if (render and _IN_NB) else out

    def reset(self):
        """Forget the conversation, keep the system prompt."""
        self.history = []
        md(f"*{self.name} reset.*")

    def show(self):
        """Print the conversation so far (useful for review / export)."""
        lines = []
        for m in self.history:
            who = "🧑 You" if m["role"] == "user" else "🤖 AI"
            lines.append(f"**{who}:**\n\n{m['content']}")
        md("\n\n---\n\n".join(lines) or "*empty dialogue*")

    def _condensed_history(self, limit: int = 16) -> str:
        recent = self.history[-limit:]
        out = []
        for m in recent:
            who = "Student" if m["role"] == "user" else "Tutor"
            text = m["content"].strip().replace("\n", " ")
            if len(text) > 220:
                text = text[:217] + "…"
            out.append(f"{who}: {text}")
        return "\n".join(out)

    def recap(self, *, render: bool = True, stream: bool | None = None):
        """Summarize the whole learning session: what was covered & what's next.

        Use this as the closing "look back" of a SolveIt session:

            tutor.recap()   # a warm, structured summary of everything you did
        """
        breadcrumbs = "\n".join(
            f"- {e['action']}" + (f": {e['detail']}" if e['detail'] else "")
            for e in _SESSION_LOG) or "(no actions logged)"
        convo = self._condensed_history() or "(no tutor dialogue)"
        if not _SESSION_LOG and not self.history:
            md("*Nothing to recap yet — do some learning first, then call "
               "`tutor.recap()`.*")
            return None

        prompt = (
            "Below is a record of a beginner's Python learning session. Write a "
            "warm, concise session recap addressed to the student ('you'). Use "
            "these markdown sections, and keep each tight:\n\n"
            "## 📚 What we covered\n"
            "## 💡 Key takeaways\n(3-6 bullets of concrete concepts/skills)\n"
            "## 🛠️ What you practiced\n"
            "## 🎯 Suggested next steps\n(2-3 specific things to try next)\n"
            "## 🌟 Nice work\n(one encouraging sentence)\n\n"
            "Base it ONLY on what actually happened below; don't invent topics.\n\n"
            f"=== ACTIONS THIS SESSION ===\n{breadcrumbs}\n\n"
            f"=== TUTOR DIALOGUE (recent) ===\n{convo}")

        if render and _IN_NB:
            html("<div style='background:linear-gradient(135deg,#0ea5e9,#6366f1);"
                 "color:white;padding:12px 18px;border-radius:12px;"
                 "font-family:system-ui,sans-serif;font-size:17px;font-weight:700'>"
                 "🎓 Session Recap</div>")
        out = _run([{"role": "user", "content": prompt}],
                   system=self.system, stream=stream, render=render)
        self.history.append({"role": "user", "content":
                             "(generated a session recap)"})
        self.history.append({"role": "assistant", "content": out})
        return None if (render and _IN_NB) else out


# A default tutor dialogue, ready to use out of the box.
_TUTOR_SYSTEM = textwrap.dedent("""
    You are a patient, encouraging Python tutor for a complete beginner.
    Rules:
    - Keep answers short and concrete. Prefer a tiny runnable example over prose.
    - Build understanding in small steps; never dump a huge solution.
    - When you show code, keep it to a few lines and explain each line plainly.
    - Use everyday analogies. Avoid jargon, or define it immediately.
    - End with one small question or next step to keep the dialogue going.
""").strip()

tutor = Dialogue(system=_TUTOR_SYSTEM, name="tutor")


# ----------------------------------------------------------------------------
# 3) Pólya scaffolds — Understand -> Plan -> Do -> Review
# ----------------------------------------------------------------------------
_POLYA_SYSTEM = textwrap.dedent("""
    You are a problem-solving coach using George Pólya's "How to Solve It".
    You help a beginner programmer think, you do NOT solve everything for them.
    Keep every reply short and focused on the current Pólya stage only.
""").strip()


class Polya:
    """A guided Pólya session over a single problem, as a dialogue.

        p = Polya("Count how many words are in a sentence")
        p.understand()   # restate the problem, surface unknowns
        p.plan()         # propose a step-by-step plan in plain words
        p.step()         # suggest the *smallest next* line of code to try
        p.review()       # reflect once you have something working
    """

    def __init__(self, problem: str):
        self.problem = problem
        self.chat = Dialogue(system=_POLYA_SYSTEM, name="polya")
        _log("started a Pólya problem-solving session", problem)
        md(f"### 🧩 Problem\n{problem}\n\n*Use `.understand()`, `.plan()`, "
           f"`.step()`, `.review()` to work through it.*")

    def understand(self):
        md("#### 1 · Understand the problem")
        return self.chat.ask(
            f"PROBLEM: {self.problem}\n\nStage 1 — UNDERSTAND. Restate the problem "
            "in plain language. List the inputs, the desired output, and any "
            "unknowns or assumptions. Ask me 1-2 clarifying questions. No code yet.")

    def plan(self):
        md("#### 2 · Devise a plan")
        return self.chat.ask(
            "Stage 2 — PLAN. Give a short numbered plan in plain English (no code). "
            "Each step should be tiny enough to become 1-2 lines of Python.")

    def step(self, note: str = ""):
        md("#### 3 · Carry it out (one tiny step)")
        extra = f" Here's where I am: {note}" if note else ""
        return self.chat.ask(
            "Stage 3 — DO. Suggest only the SINGLE smallest next step. Show at most "
            "1-3 lines of code for that step and tell me what to look for when I run "
            f"it. Wait for me before going further.{extra}")

    def review(self, note: str = ""):
        md("#### 4 · Look back")
        extra = f" My current solution / result: {note}" if note else ""
        return self.chat.ask(
            "Stage 4 — REVIEW. Help me look back: is the result correct? What edge "
            "cases might break it? How could it be simpler or clearer? "
            f"What did I learn that transfers to other problems?{extra}")


def solve(problem: str) -> Polya:
    """Start a Pólya session. `p = solve("..."); p.understand()`."""
    return Polya(problem)


# ----------------------------------------------------------------------------
# 4) Teaching helpers
# ----------------------------------------------------------------------------
def _thing_body(thing) -> str:
    """Describe `thing` for a prompt: code block if it looks like code, else value."""
    if isinstance(thing, str) and ("\n" in thing or any(
            k in thing for k in ("def ", "import ", "=", "(", "print"))):
        return f"this Python code:\n\n```python\n{thing}\n```"
    return f"this Python value: `{thing!r}` (type: {type(thing).__name__})"


def explain(thing, *, level: str = "beginner") -> str:
    """Explain a value, an object, or a snippet of code in plain language.

    >>> explain([1, 2, 3])
    >>> explain("for i in range(3): print(i)")
    """
    res = ask(f"Explain {_thing_body(thing)}\n\nKeep it to a {level} level: a few "
              "short sentences, one tiny analogy, no fluff.",
              system=_TUTOR_SYSTEM, _loggable=False)
    _log("explored a concept", str(thing))
    return res


# Builds a self-contained, interactive HTML "artifact" alongside the explanation.
_ARTIFACT_SYSTEM = textwrap.dedent("""
    You are a patient Python tutor who teaches with small INTERACTIVE artifacts.
    You produce two things: a tiny plain-language explanation, then one
    self-contained, interactive HTML artifact that lets a beginner *play* with
    the idea (e.g. a slider that re-runs a loop, buttons that step through code,
    a live visualization of a list being indexed).

    Hard rules for the artifact:
    - ONE complete HTML document: <!doctype html> ... </html>.
    - ALL CSS and JS inline. No external requests, no CDNs, no fetch — it runs in
      a sandboxed iframe with NO network and NO same-origin access.
    - Vanilla JS only. It must visibly DO something the moment the user interacts.
    - Clean, friendly look: system-ui font, generous spacing, rounded corners.
    - Keep it focused on the ONE concept being explained; small, not a dashboard.
""").strip()


def _split_explanation_and_artifact(raw: str):
    """Split an LLM reply into (markdown_explanation, html_document_or_None)."""
    # Prefer an explicit ```html fence; fall back to any fenced block that is a doc.
    m = re.search(r"```html\s*\n(.*?)```", raw, re.S | re.I)
    if not m:
        m = re.search(r"```\s*\n(\s*<(?:!doctype|html).*?)```", raw, re.S | re.I)
    if not m:
        return raw.strip(), None
    explanation = raw[:m.start()].strip()
    return explanation, m.group(1).strip()


def _render_artifact(html_doc: str, *, title: str = "Interactive artifact",
                     height: int = 420):
    """Embed a self-contained HTML doc inline as a sandboxed, isolated iframe."""
    # srcdoc must escape & and " so the whole document survives as one attribute.
    srcdoc = html_doc.replace("&", "&amp;").replace('"', "&quot;")
    html(
        "<div style='font-family:system-ui,sans-serif;margin-top:6px'>"
        "<div style='display:flex;align-items:center;gap:8px;"
        "background:linear-gradient(135deg,#0ea5e9,#6366f1);color:white;"
        "padding:8px 14px;border-radius:10px 10px 0 0;font-weight:700;font-size:14px'>"
        f"🧪 {_html_escape(title)}"
        "<span style='font-weight:400;opacity:.85;font-size:12px'>"
        "· interactive — try it</span></div>"
        f"<iframe sandbox='allow-scripts allow-popups' srcdoc=\"{srcdoc}\" "
        f"style='width:100%;height:{height}px;border:1px solid #e5e7eb;"
        "border-top:0;border-radius:0 0 10px 10px;background:white'></iframe></div>")


def explain_with_artifacts(thing, *, level: str = "beginner",
                           height: int = 420) -> str:
    """Explain `thing` AND render an interactive HTML artifact inline.

    Like `explain(...)`, but the AI also builds a small, self-contained,
    *interactive* HTML widget (sliders, buttons, live visuals) that lets you
    play with the idea right in the cell — Claude-style "artifacts", inline.

        explain_with_artifacts("for i in range(3): print(i)")
        explain_with_artifacts([10, 20, 30])           # visualize indexing
        explain_with_artifacts("f-strings in Python")

    Returns the raw explanation text (the artifact is rendered as a side effect).
    """
    raw = ask(
        f"Explain {_thing_body(thing)}\n\n"
        f"First, a {level}-level explanation: a few short sentences and one tiny "
        "analogy, as markdown. Then, on its own, a single ```html fenced block "
        "containing the COMPLETE interactive artifact for exactly this idea.",
        system=_ARTIFACT_SYSTEM, render=False)
    explanation, artifact = _split_explanation_and_artifact(raw)

    if explanation:
        md(explanation)
    if artifact and _IN_NB:
        _render_artifact(artifact, title=f"Explore: {str(thing)[:48]}",
                         height=height)
    elif artifact:  # headless: persist so it's still usable outside Jupyter
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "artifacts")
        os.makedirs(out_dir, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(out_dir, f"artifact-{stamp}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(artifact)
        md(f"*Interactive artifact saved to* `{path}` *(open it in a browser).*")
    elif not artifact:
        md("*(No interactive artifact this time — here's the explanation above.)*")
    _log("explained with an interactive artifact", str(thing))
    return explanation


# ----------------------------------------------------------------------------
# 4b) generate_visual_analogy — an AI-drawn visual mnemonic, shown inline
# ----------------------------------------------------------------------------
_VISUAL_DESIGN_SYSTEM = textwrap.dedent("""
    You design VISUAL MNEMONICS for a learner. Given a concept, invent ONE simple,
    concrete, slightly exaggerated visual metaphor that encodes the core idea so it
    sticks in memory (think: a single striking image you'd never forget).
    The scene must be drawable and uncluttered — ONE focal metaphor, not a collage,
    and NO text/letters/labels in the picture.
""").strip()

# A house style that keeps every analogy minimal and memorable.
_VISUAL_STYLE = (
    "Minimal flat vector illustration. A SINGLE bold iconic visual metaphor, "
    "centered, with lots of negative space. Limited palette of 2-3 colors on a "
    "warm cream (#F5F3EB) background, thick clean black linework, no gradients, "
    "no 3D, no photorealism, and absolutely NO text, letters, numbers or labels. "
    "Slightly playful and exaggerated so it is instantly memorable.")


def _detect_image_backend() -> str:
    if _IMG_CFG["backend"]:
        return _IMG_CFG["backend"]
    have_gemini = bool(os.environ.get("GOOGLE_API_KEY")
                       or os.environ.get("GEMINI_API_KEY"))
    have_openai = bool(os.environ.get("OPENAI_API_KEY"))
    # Prefer a vendor whose SDK is actually importable (better first-run UX).
    if have_gemini and _can_import("google.genai"):
        return "gemini"
    if have_openai and _can_import("openai"):
        return "openai"
    return "gemini" if have_gemini else "openai"


def _can_import(mod: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(mod) is not None


def configure_images(backend: str | None = None, model: str | None = None):
    """Pick the image backend/model. e.g. configure_images(backend='gemini')."""
    if backend is not None:
        _IMG_CFG["backend"] = backend
    if model is not None:
        _IMG_CFG["model"] = model
    b = _detect_image_backend()
    md(f"**images configured** · backend=`{b}` · "
       f"model=`{_IMG_CFG['model'] or _IMG_DEFAULTS[b]}`")


def _gen_image_gemini(prompt: str, aspect: str, model: str, path: str):
    from google import genai
    from google.genai import types
    client = genai.Client()   # reads GOOGLE_API_KEY / GEMINI_API_KEY
    resp = client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(aspect_ratio=aspect)))
    parts = [p for p in resp.candidates[0].content.parts
             if getattr(p, "inline_data", None)]
    if not parts:
        raise RuntimeError("Gemini returned no image (it may have refused the prompt).")
    parts[0].as_image().save(path)


# Map a friendly aspect ratio to the sizes gpt-image-* accepts.
_OPENAI_SIZE = {"1:1": "1024x1024", "16:9": "1536x1024",
                "9:16": "1024x1536", "4:5": "1024x1536"}


def _gen_image_openai(prompt: str, aspect: str, model: str, path: str):
    import base64
    from openai import OpenAI
    client = OpenAI()
    resp = client.images.generate(
        model=model, prompt=prompt, size=_OPENAI_SIZE.get(aspect, "1024x1024"), n=1)
    datum = resp.data[0]
    if getattr(datum, "b64_json", None):
        with open(path, "wb") as f:
            f.write(base64.b64decode(datum.b64_json))
    elif getattr(datum, "url", None):
        import urllib.request
        urllib.request.urlretrieve(datum.url, path)
    else:
        raise RuntimeError("OpenAI returned no image data.")


def _render_visual_analogy(path: str, concept: str, analogy: str,
                           mnemonic: str, width: int):
    """Showcase the generated image + its mnemonic caption inline in the cell."""
    html("<div style='font-family:system-ui,sans-serif;display:flex;gap:8px;"
         "align-items:center;background:linear-gradient(135deg,#f5c542,#e86b5a);"
         "color:#1a1a1a;padding:8px 14px;border-radius:10px;font-weight:700;"
         f"font-size:14px;margin-top:6px'>🧠 Visual analogy · "
         f"<span style='font-weight:500'>{_html_escape(concept)}</span></div>")
    if _IN_NB:
        from IPython.display import Image as _Img
        display(_Img(filename=path, width=width))
    cap = []
    if analogy:
        cap.append(f"<b>“{_html_escape(analogy)}”</b>")
    if mnemonic:
        cap.append(f"<span style='color:#374151'>{_html_escape(mnemonic)}</span>")
    if cap:
        html("<div style='font-family:system-ui,sans-serif;line-height:1.5;"
             "border-left:4px solid #e86b5a;background:#fff8e1;padding:8px 14px;"
             f"border-radius:8px;max-width:560px'>{'<br>'.join(cap)}</div>")
    md(f"<sub>saved to <code>{path}</code></sub>")


def generate_visual_analogy(concept: str, *, aspect: str = "1:1",
                            width: int = 420, backend: str | None = None,
                            model: str | None = None,
                            filename: str | None = None) -> str:
    """Draw a minimal *visual mnemonic* for a concept and show it inline.

    The AI first invents a single striking visual metaphor for `concept`, then an
    image model (Gemini "nano banana pro" or OpenAI `gpt-image-2`) draws it as a
    clean, memorable picture rendered right in the notebook — a memory device for
    whatever you're learning.

        generate_visual_analogy("Python list indexing starts at 0")
        generate_visual_analogy("a dictionary maps keys to values", aspect="16:9")

    Returns the saved image path (or None if generation failed).
    """
    # 1) Design the mnemonic (text model) — metaphor, why-it-sticks, image prompt.
    raw = ask(
        f"Concept the learner is studying:\n\n{concept}\n\n"
        'Return ONLY JSON: {"analogy": "<the metaphor in one vivid line>", '
        '"mnemonic": "<1-2 sentences: how the picture maps to the concept so '
        'recalling the image recalls the idea>", "image_prompt": "<a concrete, '
        "literal description of the SINGLE minimal scene to draw — objects, "
        'layout, colors; no text in the image>"}.',
        system=_VISUAL_DESIGN_SYSTEM, render=False)
    spec = _extract_json(raw) or {}
    analogy = (spec.get("analogy") or "").strip()
    mnemonic = (spec.get("mnemonic") or "").strip()
    image_prompt = (spec.get("image_prompt") or analogy or concept).strip()

    # 2) Render the image (image model).
    b = backend or _detect_image_backend()
    if model:
        chosen_model = model
    else:
        chosen_model = _IMG_CFG["model"] or _IMG_DEFAULTS.get(b, "")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = filename or f"analogy-{stamp}.png"
    if not filename.endswith(".png"):
        filename += ".png"
    path = os.path.join(out_dir, filename)

    full_prompt = f"{image_prompt}\n\nStyle: {_VISUAL_STYLE}"
    if _IN_NB:
        md(f"🎨 *Drawing a visual analogy with `{b}` (`{chosen_model}`)…*")
    try:
        if b == "gemini":
            _gen_image_gemini(full_prompt, aspect, chosen_model, path)
        elif b == "openai":
            _gen_image_openai(full_prompt, aspect, chosen_model, path)
        else:
            raise RuntimeError(f"Unknown image backend: {b!r}")
    except ImportError:
        pkg = "google-genai" if b == "gemini" else "openai"
        md(f"*Image backend `{b}` needs `pip install {pkg}` "
           "(or `configure_images(backend=...)`).*")
        return None
    except Exception as e:
        md(f"*Couldn't generate the image ({type(e).__name__}: {e}). "
           "Try again or `configure_images(backend=...)`.*")
        return None

    _render_visual_analogy(path, concept, analogy, mnemonic, width)
    _log("made a visual analogy", concept)
    return path


def explain_error() -> str:
    """Explain the LAST exception that happened, in beginner terms.

    Run this in a fresh cell right after a cell raised an error.
    """
    exc = getattr(sys, "last_value", None)
    tb_type = getattr(sys, "last_type", None)
    if exc is None:
        md("*No recent error found. Run the failing cell first, then call "
           "`explain_error()` in the next cell.*")
        return None
    name = tb_type.__name__ if tb_type else type(exc).__name__
    res = ask(
        f"A beginner hit this Python error:\n\n{name}: {exc}\n\n"
        "1) Explain in plain English what it means. "
        "2) List the most likely causes. "
        "3) Suggest how to fix it. Be concise and kind.",
        system=_TUTOR_SYSTEM, _loggable=False)
    _log("debugged an error", f"{name}: {exc}")
    return res


def hint(problem: str) -> str:
    """Get a SOCRATIC hint — a nudge, never the full solution.

    Keeps the human as the agent. Great for exercises.
    """
    res = ask(
        f"I'm working on this and I'm stuck:\n\n{problem}\n\n"
        "Give me ONE small Socratic hint that nudges my thinking. Do NOT give "
        "the answer or write the solution code. Maybe ask me a guiding question.",
        system=_TUTOR_SYSTEM, _loggable=False)
    _log("asked for a hint", problem)
    return res


def _extract_json(text: str):
    """Best-effort pull a JSON array/object out of an LLM reply."""
    t = _strip_fences(text).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    # find the outermost [ ... ] or { ... }
    for open_c, close_c in (("[", "]"), ("{", "}")):
        i, j = t.find(open_c), t.rfind(close_c)
        if i != -1 and j != -1 and j > i:
            try:
                return json.loads(t[i:j + 1])
            except Exception:
                continue
    return None


# Verdict -> (emoji, accent colour, soft background)
_VERDICT_STYLE = {
    "correct": ("✅", "#1a7f37", "#e6f4ea"),
    "partial": ("🟡", "#9a6700", "#fff8e1"),
    "incorrect": ("❌", "#c0392b", "#fdecea"),
}


class Quiz:
    """An interactive, self-contained check-for-understanding.

    Unlike a one-shot question, a Quiz *remembers* the questions it asked.
    You type answers into boxes, hit one button, and the AI grades them with
    full knowledge of both the questions AND your answers — no copy-pasting.

        q = quiz("Python variables and f-strings", n=3)   # renders the quiz
        # ...type answers in the boxes, click "Submit for feedback"...
        tutor.ask("explain question 2 more")   # tutor already knows the quiz
    """

    def __init__(self, topic: str, n: int = 3):
        self.topic = topic
        self.questions = self._generate(n)
        self.answers: list[str] = []
        self.graded: list[dict] = []
        self._boxes = []
        _log("took a quiz on", topic)
        if _IN_NB:
            self._render_interactive()
        else:  # headless fallback
            for i, q in enumerate(self.questions, 1):
                print(f"{i}. [{q.get('kind','')}] {q['question']}")

    # -- generation ---------------------------------------------------------
    def _generate(self, n: int) -> list[dict]:
        raw = ask(
            f"Create {n} short check-for-understanding questions about: {self.topic}. "
            "Include a mix: one recall, one 'predict the output' (show a tiny code "
            "snippet in the question), and one 'spot the bug'. "
            'Return ONLY JSON: a list of objects like '
            '[{"question": "...", "kind": "recall|predict|bug"}]. No answers.',
            system=_TUTOR_SYSTEM, render=False)
        data = _extract_json(raw) or []
        out = []
        for item in data:
            if isinstance(item, dict) and item.get("question"):
                out.append({"question": item["question"],
                            "kind": item.get("kind", "")})
            elif isinstance(item, str):
                out.append({"question": item, "kind": ""})
        return out or [{"question": raw, "kind": ""}]

    # -- interactive UI -----------------------------------------------------
    def _render_interactive(self):
        import ipywidgets as W
        header = W.HTML(
            "<div style='background:linear-gradient(135deg,#6366f1,#8b5cf6);"
            "color:white;padding:14px 18px;border-radius:12px;"
            "font-family:system-ui,sans-serif'>"
            f"<div style='font-size:18px;font-weight:700'>🧠 Quick Check</div>"
            f"<div style='opacity:.9;font-size:13px;margin-top:2px'>{self.topic} "
            "· answer in the boxes, then hit submit</div></div>")

        cards = []
        for i, q in enumerate(self.questions, 1):
            kind = q["kind"]
            tag = (f"<span style='background:#eef2ff;color:#4338ca;font-size:11px;"
                   f"padding:1px 8px;border-radius:999px;margin-left:6px'>{kind}</span>"
                   if kind else "")
            qhtml = W.HTML(
                "<div style='font-family:system-ui,sans-serif;margin-bottom:4px'>"
                f"<span style='display:inline-block;width:24px;height:24px;"
                "background:#6366f1;color:white;border-radius:50%;text-align:center;"
                f"line-height:24px;font-weight:700;font-size:13px'>{i}</span>"
                f"&nbsp;<b>{_html_escape(q['question'])}</b>{tag}</div>")
            box = W.Textarea(placeholder="Type your answer here…",
                             layout=W.Layout(width="98%", height="64px"))
            self._boxes.append(box)
            cards.append(W.VBox([qhtml, box], layout=W.Layout(
                border="1px solid #e5e7eb", border_radius="10px",
                padding="10px 12px", margin="8px 0")))

        submit = W.Button(description="Submit for feedback", icon="check",
                          button_style="success",
                          layout=W.Layout(width="220px", height="38px"))
        self._out = W.Output()
        submit.on_click(self._on_submit)
        display(W.VBox([header] + cards + [submit, self._out]))

    def _on_submit(self, _btn):
        import ipywidgets as W
        self.answers = [b.value for b in self._boxes]
        with self._out:
            self._out.clear_output()
            display(Markdown("⏳ *Grading your answers…*"))
            self.grade()
            self._out.clear_output()
            self._render_feedback()

    # -- grading (AI sees questions + answers together) ---------------------
    def grade(self) -> list[dict]:
        qa = "\n\n".join(
            f"Q{i}. ({q['kind']}) {q['question']}\nStudent answer: "
            f"{self.answers[i-1].strip() or '(left blank)'}"
            for i, q in enumerate(self.questions, 1))
        raw = ask(
            "You are grading a beginner's quiz. For EACH question below, judge the "
            "student's answer. Be encouraging but honest.\n\n" + qa + "\n\n"
            'Return ONLY JSON: a list (same order) of objects like '
            '[{"verdict": "correct|partial|incorrect", "feedback": "one or two '
            'sentences addressed to the student", "ideal": "the correct answer, '
            'briefly"}].',
            system=_TUTOR_SYSTEM, render=False)
        data = _extract_json(raw) or []
        self.graded = data if isinstance(data, list) else []
        score = sum(1 for g in self.graded if g.get("verdict") == "correct")
        _log("scored on the quiz", f"{score}/{len(self.questions)} on {self.topic}")
        self._remember()   # make the tutor aware of this quiz
        return self.graded

    def _render_feedback(self):
        score = sum(1 for g in self.graded if g.get("verdict") == "correct")
        total = len(self.questions)
        pct = int(100 * score / total) if total else 0
        bar = (f"<div style='background:#e5e7eb;border-radius:999px;height:10px;"
               f"width:100%;overflow:hidden;margin-top:6px'>"
               f"<div style='background:linear-gradient(90deg,#34d399,#10b981);"
               f"height:10px;width:{pct}%'></div></div>")
        parts = [
            "<div style='font-family:system-ui,sans-serif'>"
            f"<div style='font-size:17px;font-weight:700'>📊 You scored "
            f"{score}/{total}" + ("  🎉" if score == total else "") + "</div>"
            + bar + "</div>"]
        for i, q in enumerate(self.questions, 1):
            g = self.graded[i-1] if i-1 < len(self.graded) else {}
            emoji, accent, bg = _VERDICT_STYLE.get(
                g.get("verdict", "partial"), _VERDICT_STYLE["partial"])
            ans = _html_escape(self.answers[i-1].strip() or "(blank)")
            parts.append(
                f"<div style='border-left:4px solid {accent};background:{bg};"
                "padding:10px 14px;border-radius:8px;margin:8px 0;"
                "font-family:system-ui,sans-serif;line-height:1.5'>"
                f"<b>{emoji} Q{i}.</b> {_html_escape(q['question'])}<br>"
                f"<span style='color:#374151'><i>Your answer:</i> {ans}</span><br>"
                f"<span style='color:{accent}'><b>Feedback:</b> "
                f"{_html_escape(g.get('feedback',''))}</span><br>"
                f"<span style='color:#4b5563'><b>Ideal:</b> "
                f"{_html_escape(g.get('ideal',''))}</span></div>")
        html("".join(parts))
        md("💬 *Want more detail? Ask `tutor.ask(\"explain question 2 more\")` — "
           "it already knows this quiz.*")

    def _remember(self):
        """Push the quiz Q&A into the shared tutor dialogue so follow-ups work."""
        lines = [f"We just did a quiz on '{self.topic}'. Here it is:"]
        for i, q in enumerate(self.questions, 1):
            ans = self.answers[i-1].strip() if i-1 < len(self.answers) else ""
            lines.append(f"Q{i} ({q['kind']}): {q['question']}\n"
                         f"My answer: {ans or '(blank)'}")
        tutor.history.append({"role": "user", "content": "\n".join(lines)})
        tutor.history.append({"role": "assistant", "content":
            "Got it — I have all the quiz questions and your answers in mind. "
            "Ask me about any of them."})


def quiz(topic: str, n: int = 3) -> "Quiz":
    """Start an interactive check-for-understanding. Returns a `Quiz`.

    Type answers in the boxes, click submit, get color-coded feedback. The
    grader sees your answers AND the questions, and the `tutor` remembers it.
    """
    return Quiz(topic, n)


def _html_escape(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def recap(*, render: bool = True, stream: bool | None = None):
    """Closing 'look back': summarize the whole session. Same as `tutor.recap()`."""
    return tutor.recap(render=render, stream=stream)


def _session_material(limit: int = 40) -> str:
    """Stitch the session log + tutor dialogue into source material for the AI."""
    parts = []
    if _SESSION_LOG:
        parts.append("Actions this session:\n" + "\n".join(
            f"- {e['action']}" + (f": {e['detail']}" if e['detail'] else "")
            for e in _SESSION_LOG))
    if tutor.history:
        parts.append("Tutor dialogue:\n" + tutor._condensed_history(limit=limit))
    return "\n\n".join(parts)


# ----------------------------------------------------------------------------
# 8) anki — export the session (or a custom focus) to Anki-importable cards
# ----------------------------------------------------------------------------
def anki(focus: str = "", n: int = 12, filename: str | None = None):
    """Generate Anki flashcards from the session and save an importable .txt.

    The file is `front;back;source` per line (semicolon-separated, CSV-quoted),
    ready for Anki's File → Import.

        anki()                      # cards from everything you did this session
        anki("f-strings and loops") # only those topics
        anki(focus="just the errors I debugged", n=6)
    """
    material = _session_material()
    if not material and not focus:
        md("*Nothing to make cards from yet. Do some learning (or pass a "
           "`focus=` topic), then call `anki(...)`.*")
        return None

    instr = (f"Focus ONLY on what the student asked for: {focus}.\n" if focus
             else "Cover the key concepts and skills from this session.\n")
    raw = ask(
        f"Create {n} high-quality Anki flashcards for a Python beginner.\n{instr}"
        "Rules: each card is ATOMIC (one idea), uses active recall, front is a "
        "clear question/prompt, back is a concise answer (you may use a tiny code "
        "snippet). Add a short 'source' tag naming the topic. Avoid duplicates.\n\n"
        'Return ONLY JSON: a list like '
        '[{"front":"...","back":"...","source":"..."}].\n\n'
        f"=== SESSION MATERIAL ===\n{material or focus}",
        system=_TUTOR_SYSTEM, render=False)
    cards = _extract_json(raw) or []
    cards = [c for c in cards if isinstance(c, dict) and c.get("front") and c.get("back")]
    if not cards:
        md("*Could not generate cards — try again or narrow the `focus`.*")
        return None

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anki_exports")
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = filename or f"anki-{stamp}.txt"
    if not filename.endswith(".txt"):
        filename += ".txt"
    path = os.path.join(out_dir, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")          # auto-quotes fields with ; or \n
        for c in cards:
            w.writerow([c["front"].strip(), c["back"].strip(),
                        str(c.get("source", "")).strip()])
    _log("exported Anki cards", f"{len(cards)} cards" + (f" on {focus}" if focus else ""))

    # preview
    rows = "".join(
        f"<tr><td style='padding:4px 10px;border-bottom:1px solid #eee'>"
        f"{_html_escape(c['front'])}</td>"
        f"<td style='padding:4px 10px;border-bottom:1px solid #eee'>"
        f"{_html_escape(c['back'])}</td></tr>" for c in cards[:6])
    html(
        "<div style='font-family:system-ui,sans-serif'>"
        "<div style='background:linear-gradient(135deg,#22c55e,#16a34a);color:white;"
        "padding:10px 16px;border-radius:10px;font-weight:700'>"
        f"🗂️ {len(cards)} Anki cards saved</div>"
        "<table style='border-collapse:collapse;margin-top:8px;font-size:13px'>"
        "<tr><th style='text-align:left;padding:4px 10px'>Front</th>"
        "<th style='text-align:left;padding:4px 10px'>Back</th></tr>"
        f"{rows}</table>"
        f"<div style='color:#6b7280;font-size:12px;margin-top:6px'>showing "
        f"{min(6,len(cards))} of {len(cards)}</div></div>")
    md(f"**Saved to:** `{path}`\n\n"
       "**Import into Anki:** *File → Import* → pick this file → set "
       "**Field separator = Semicolon** → map **Field 1 → Front, Field 2 → Back** "
       "(Field 3 is the source/topic, map it to a tag or extra field). "
       "Allow HTML if your backs contain code.")
    return path


# ----------------------------------------------------------------------------
# 9) cmd — reusable custom prompts ("/commands"), discoverable via TAB-complete
# ----------------------------------------------------------------------------
_CMD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "solveit_commands.json")

# A few starters so `cmd.<TAB>` shows working examples immediately.
_DEFAULT_COMMANDS = {
    "eli5": "Explain this Python idea like I'm five, with one everyday analogy: {input}",
    "analogy": "Give me a vivid real-world analogy for this Python concept: {input}",
    "example": "Show ONE tiny runnable Python example (under 6 lines) of: {input}",
    "realworld": "Where would a working programmer actually use this? Be concrete: {input}",
    "cheatsheet": "Make a compact markdown-table cheat-sheet for: {input}",
    "interview": "Ask me ONE beginner interview question (no answer yet) about: {input}",
}


class Commands:
    """Reusable prompt templates — your notebook's version of `/commands`.

    Type `cmd.` then press **TAB** to see all commands. Call one with your text:

        cmd.eli5("recursion")
        cmd.example("dictionary comprehension")

    Make your own (saved to disk, reused every session):

        cmd.add("roast", "Roast my Python code, then fix it kindly:\\n{input}")
        cmd.roast("for i in range(len(xs)): print(xs[i])")

    Templates use `{input}` for your text (or any named `{placeholders}` you
    fill with keyword args). `cmd.list()` shows them; `cmd.remove("name")` drops one.
    """

    def __init__(self, path: str):
        self._path = path
        self._templates: dict[str, str] = {}
        self._reserved = {"add", "remove", "list", "run"} | \
            {a for a in dir(self.__class__) if not a.startswith("__")}
        for name, tmpl in _DEFAULT_COMMANDS.items():
            self.add(name, tmpl, _persist=False)
        self._load()

    @staticmethod
    def _placeholders(template: str):
        return [fn for _, fn, _, _ in _string.Formatter().parse(template) if fn]

    def _make(self, name: str, template: str):
        phs = self._placeholders(template)

        def runner(*args, **kwargs):
            fill = dict(kwargs)
            remaining = [p for p in phs if p not in fill]
            for p, val in zip(remaining, args):
                fill[p] = val
            extra = args[len(remaining):] if len(args) > len(remaining) else ()
            try:
                prompt = template.format(**{k: fill.get(k, "") for k in phs}) \
                    if phs else template
            except Exception:
                prompt = template
            if extra:                       # leftover positional text -> append
                prompt = prompt + "\n\n" + " ".join(str(e) for e in extra)
            if not phs and args:            # template has no slots: append input
                prompt = template + "\n\n" + " ".join(str(a) for a in args)
            _log(f"ran /{name}", " ".join(str(a) for a in args))
            return ask(prompt, system=_TUTOR_SYSTEM, _loggable=False)

        runner.__name__ = str(name)
        runner.__doc__ = f"/{name} → {template}"
        return runner

    def add(self, name: str, template: str, *, _persist: bool = True):
        """Register (and save) a reusable command. `cmd.add('name', 'template {input}')`."""
        if not name.isidentifier() or name in self._reserved or name.startswith("_"):
            raise ValueError(f"'{name}' is not a valid/allowed command name.")
        self._templates[name] = template
        setattr(self, name, self._make(name, template))
        if _persist:
            self._save()
            md(f"✅ Saved command **/{name}** — type `cmd.{name}(\"...\")` "
               "(or `cmd.` + TAB to find it).")

    def remove(self, name: str):
        """Delete a custom command."""
        self._templates.pop(name, None)
        if hasattr(self, name):
            try:
                delattr(self, name)
            except AttributeError:
                pass
        self._save()
        md(f"🗑️ Removed **/{name}**.")

    def list(self):
        """Show all available commands and their templates."""
        rows = "".join(
            f"<tr><td style='padding:4px 10px;border-bottom:1px solid #eee;"
            f"font-weight:600;color:#4338ca'>cmd.{n}</td>"
            f"<td style='padding:4px 10px;border-bottom:1px solid #eee;"
            f"font-family:ui-monospace,monospace;font-size:12px'>"
            f"{_html_escape(t)}</td></tr>"
            for n, t in sorted(self._templates.items()))
        html("<div style='font-family:system-ui,sans-serif'>"
             "<b>🧩 Your commands</b> <span style='color:#6b7280;font-size:12px'>"
             "(type <code>cmd.</code> then TAB)</span>"
             "<table style='border-collapse:collapse;margin-top:6px'>"
             f"{rows}</table></div>")

    def _save(self):
        try:
            json.dump(self._templates, open(self._path, "w"), indent=2)
        except Exception as e:  # non-fatal: commands still work this session
            md(f"*(couldn't persist commands: {e})*")

    def _load(self):
        if os.path.exists(self._path):
            try:
                for n, t in json.load(open(self._path)).items():
                    self.add(n, t, _persist=False)
            except Exception:
                pass


cmd = Commands(_CMD_PATH)


# ----------------------------------------------------------------------------
# 10) edit — give the AI a code cell; it rewrites it in place + explains why
# ----------------------------------------------------------------------------
def _edit_code(code: str, instruction: str):
    """Return (summary, edited_code) for an AI edit of `code`."""
    raw = ask(
        "You are editing a beginner's Python code. Apply this instruction "
        f"(or, if blank, improve it):\n\nINSTRUCTION: {instruction or '(improve it)'}\n\n"
        f"```python\n{code}\n```\n\n"
        'Return ONLY JSON: {"summary": "one short line on what changed and why", '
        '"code": "the full edited code"}. Keep it beginner-clear; only change '
        "what the instruction asks for.",
        system=_TUTOR_SYSTEM, render=False)
    data = _extract_json(raw) or {}
    return (data.get("summary") or instruction or "edited",
            data.get("code") or code)


def edit(code: str, instruction: str = ""):
    """AI-edit a snippet and drop the result into a NEW cell (you review & run).

    For an *in-place* edit of the current cell, use the `%%edit` magic instead.

        edit('''for i in range(len(xs)): print(xs[i])''', "make it pythonic")
    """
    summary, new_code = _edit_code(code, instruction)
    _log("edited code", summary)
    _show_edit_summary(summary)
    block = f"# ✏️ EDIT: {summary}\n{new_code}"
    ip = get_ipython()
    if ip is not None:
        ip.set_next_input(block, replace=False)
        return None
    md(f"```python\n{block}\n```")
    return new_code


def _show_edit_summary(summary: str):
    html("<div style='border-left:4px solid #6366f1;background:#eef2ff;"
         "padding:8px 14px;border-radius:8px;font-family:system-ui,sans-serif'>"
         f"✏️ <b>What changed:</b> {_html_escape(summary)}</div>")


def _register_magics():
    """Register the `%%edit` cell magic (in-place edit of THIS cell)."""
    ip = get_ipython()
    if ip is None:
        return
    from IPython.core.magic import register_cell_magic

    @register_cell_magic
    def edit(line, cell):  # noqa: A001  (magic name)
        """%%edit <instruction>  — AI rewrites this cell's code in place + a comment."""
        summary, new_code = _edit_code(cell, line.strip())
        _log("edited code (in place)", summary)
        _show_edit_summary(summary)
        block = f"# ✏️ EDIT: {summary}\n{new_code}"
        ip.set_next_input(block, replace=True)   # replace THIS cell's contents


if _IN_NB:
    try:
        _register_magics()
    except Exception:
        pass


def review(code: str) -> str:
    """Review the student's OWN code: correctness, clarity, idioms."""
    res = ask(
        f"Review this beginner's Python code kindly but honestly:\n\n"
        f"```python\n{code}\n```\n\n"
        "Cover: (1) does it work / any bugs, (2) is it clear, (3) one or two "
        "small idiomatic improvements. Keep it short and show tiny diffs only.",
        system=_TUTOR_SYSTEM, _loggable=False)
    _log("got a code review", code)
    return res


# ----------------------------------------------------------------------------
# 5) propose — AI writes code into a NEW editable cell (you read/edit/run it)
# ----------------------------------------------------------------------------
def propose(task: str, *, context: str = "") -> str:
    """Ask the AI for code, then drop it into a NEW cell below — NOT run.

    This is the SolveIt move: the AI *proposes*, you stay the agent. You read
    it, edit it, and decide to run it. Falls back to printing if not in Jupyter.

        propose("read a CSV file called data.csv into a list of rows")
    """
    raw = ask(
        f"Write a SHORT Python snippet (a few lines, beginner-friendly) for:\n\n"
        f"{task}\n\n{('Context: ' + context) if context else ''}\n\n"
        "Return ONLY the code, no markdown fences, no explanation. Add a brief "
        "inline comment on tricky lines.",
        system=_TUTOR_SYSTEM, render=False)
    code = _strip_fences(raw)
    _log("had AI propose code for", task)

    ip = get_ipython()
    if ip is not None:
        md("🤖 *Proposed code dropped into a new cell below — read it, edit it, "
           "then run it yourself.*")
        ip.set_next_input(f"# 🤖 PROPOSED (review & edit before running)\n{code}",
                          replace=False)
        return None   # the code is now in a new cell; don't echo it here too
    else:
        md(f"```python\n{code}\n```")
    return code


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t.rsplit("```", 1)[0]
        # drop a leading 'python' language tag if present
        if t.lstrip().startswith("python\n"):
            t = t.lstrip()[len("python\n"):]
    return t.strip()


# ----------------------------------------------------------------------------
# 11) upload_pdf / read_pdf — expand a PDF into a NEW reader notebook of cells.
#
# Design (see research-pdf-upload-jupyter.md): the only portable way to get a
# whole PDF as real markdown cells is to WRITE A NEW .ipynb with nbformat and
# open it. Images are embedded as base64 data-URIs INSIDE markdown cells, so
# they render the moment the notebook opens (no file-serving, no "run me",
# no broken `![](path)` links). Parsing prefers **docling** for fidelity
# (great tables/figures) and falls back to **PyMuPDF** when docling is absent.
# ----------------------------------------------------------------------------
_PDF_PAGEBREAK = "<!--SOLVEIT-PAGEBREAK-->"


def _slugify(name: str) -> str:
    base = os.path.splitext(os.path.basename(name))[0]
    return re.sub(r"[^A-Za-z0-9_-]+", "-", base).strip("-").lower() or "pdf"


def _img_to_datauri(data: bytes, ext: str = "png") -> str:
    ext = "jpeg" if ext.lower() in ("jpg", "jpeg") else ext.lower()
    return f"data:image/{ext};base64," + base64.b64encode(data).decode()


def _pdf_markdown_docling(pdf_path: str) -> str:
    """High-fidelity PDF -> markdown with base64-embedded images (docling)."""
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling_core.types.doc import ImageRefMode

    opts = PdfPipelineOptions()
    opts.generate_picture_images = True
    opts.images_scale = 2.0
    conv = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    res = conv.convert(pdf_path)
    return res.document.export_to_markdown(
        image_mode=ImageRefMode.EMBEDDED, page_break_placeholder=_PDF_PAGEBREAK)


def _pdf_markdown_fitz(pdf_path: str) -> str:
    """Lightweight PDF -> markdown: per-page text + base64-embedded images."""
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            raise ImportError("pip install docling  (or pymupdf)")
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, 1):
        parts = [f"## Page {i}"]
        text = page.get_text("text").strip()
        if text:
            parts.append(text)
        for info in page.get_images(full=True):
            try:
                ext = doc.extract_image(info[0])
            except Exception:
                continue
            uri = _img_to_datauri(ext["image"], ext.get("ext", "png"))
            parts.append(f"![figure]({uri})")
        pages.append("\n\n".join(parts))
    doc.close()
    return f"\n\n{_PDF_PAGEBREAK}\n\n".join(pages)


def _pdf_to_markdown(pdf_path: str, backend: str = "auto") -> tuple[str, str]:
    """Return (markdown, backend_used). 'auto' prefers docling, falls back to fitz."""
    order = {"auto": ["docling", "fitz"], "docling": ["docling"],
             "fitz": ["fitz"], "pymupdf": ["fitz"]}.get(backend, ["docling", "fitz"])
    last_err = None
    for b in order:
        try:
            if b == "docling":
                return _pdf_markdown_docling(pdf_path), "docling"
            return _pdf_markdown_fitz(pdf_path), "fitz"
        except ImportError as e:
            last_err = e
            continue
    raise last_err or ImportError("pip install docling")


def _split_markdown_sections(md: str) -> list[str]:
    """Split markdown into reading sections: by heading, else by page, else by size."""
    md = md.replace(_PDF_PAGEBREAK, "").strip()
    # Primary: start a new section at each markdown heading line.
    sections, cur = [], []
    for line in md.splitlines():
        if re.match(r"^#{1,6}\s", line) and cur:
            sections.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)
    if cur:
        sections.append("\n".join(cur).strip())
    sections = [s for s in sections if s]
    if len(sections) > 1:
        return sections
    # Fallback: no headings — group paragraphs (never split a data-URI, which is
    # a single line) into chunks of a few blocks each.
    blocks = [b for b in md.split("\n\n") if b.strip()]
    chunk, out = [], []
    for b in blocks:
        chunk.append(b)
        if len(chunk) >= 6:
            out.append("\n\n".join(chunk))
            chunk = []
    if chunk:
        out.append("\n\n".join(chunk))
    return out or [md]


def pdf_to_notebook(pdf_path: str, out_path: str | None = None, *,
                    backend: str = "auto", setup: bool = True,
                    conversation_cells: bool = True, name: str | None = None) -> str:
    """Expand a PDF into a NEW notebook of cells and return its path.

    Each section of the PDF becomes a **markdown cell** (images embedded inline
    as base64, so they show on open), with a conversation **code cell** after it
    that already has `solveit` imported — chat about the section right there.

        pdf_to_notebook("paper.pdf")                  # docling if available, else pymupdf
        pdf_to_notebook("paper.pdf", backend="fitz")  # force the fast/light parser
    """
    import nbformat as nbf
    name = name or os.path.basename(pdf_path)
    md_text, used = _pdf_to_markdown(pdf_path, backend)
    sections = _split_markdown_sections(md_text)

    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    cells = [nbf.v4.new_markdown_cell(
        f"# 📄 {name}\n\n*Imported with `solveit` (parsed by **{used}**). The whole "
        "document is below as cells — read each section and use the code cell "
        "under it to discuss it with your tutor.*")]
    if setup:
        cells.append(nbf.v4.new_code_cell(
            f"import sys; sys.path.append({pkg_dir!r})\nfrom solveit import *"))
    for sec in sections:
        cells.append(nbf.v4.new_markdown_cell(sec))
        if conversation_cells:
            cells.append(nbf.v4.new_code_cell(
                "# 💬 Discuss this section — write your own, or uncomment:\n"
                '# tutor.ask("Explain this section simply")'))

    out_path = out_path or os.path.join(os.getcwd(), f"{_slugify(name)}-reader.ipynb")
    nbf.write(nbf.v4.new_notebook(cells=cells), out_path)
    _log("expanded a PDF into a notebook", f"{name} ({len(sections)} sections, {used})")

    base = os.getcwd()
    if _IN_NB:
        rel = os.path.relpath(out_path, base)
        href = rel if not os.path.isabs(rel) else out_path
        html("<div style='font-family:system-ui,sans-serif;background:#e6f4ea;"
             "border-left:4px solid #1a7f37;padding:10px 14px;border-radius:8px'>"
             f"📄 <b>{_html_escape(name)}</b> → <b>{len(sections)}</b> sections, parsed "
             f"by <b>{used}</b>.<br>Open <a href='{_html_escape(href)}' target='_blank'>"
             f"<code>{_html_escape(os.path.basename(out_path))}</code></a> "
             "(or use the file browser on the left) and read away.</div>")
    else:
        md(f"**Wrote reader notebook:** `{out_path}`  ·  {len(sections)} sections "
           f"· parsed by {used}")
    return out_path


def read_pdf(pdf_path: str, *, backend: str = "auto") -> str:
    """Expand a PDF *from a path* into a reader notebook (see `pdf_to_notebook`)."""
    if not os.path.exists(pdf_path):
        md(f"*No such file:* `{pdf_path}`")
        return None
    return pdf_to_notebook(pdf_path, backend=backend)


def upload_pdf(*, backend: str = "auto"):
    """Show an **Upload PDF** button; the dropped file is expanded into a notebook.

    The new notebook contains the WHOLE PDF as cells (text as markdown, images
    embedded inline) plus a `from solveit import *` setup cell, so you can read
    it and talk to your `tutor` beneath each section. Parsing prefers **docling**
    for fidelity and falls back to **PyMuPDF**.
    """
    if not _IN_NB:
        md("*`upload_pdf()` needs Jupyter — use `read_pdf('file.pdf')` instead.*")
        return
    import ipywidgets as W
    up = W.FileUpload(accept=".pdf", multiple=False, description="📄 Upload PDF",
                      layout=W.Layout(width="220px"))
    out = W.Output()

    def on_change(change):
        files = change["new"]
        if not files:
            return
        item = files[0] if isinstance(files, (list, tuple)) else \
            list(files.values())[0]
        fname = item["name"]
        content = item["content"]
        content = content.tobytes() if hasattr(content, "tobytes") else bytes(content)
        with out:
            out.clear_output()
            display(Markdown(f"⏳ *Parsing **{_html_escape(fname)}**… "
                             "(docling's first run downloads models — give it a moment)*"))
            tmp = os.path.join(tempfile.gettempdir(), fname)
            with open(tmp, "wb") as f:
                f.write(content)
            try:
                path = pdf_to_notebook(tmp, backend=backend, name=fname)
            except ImportError:
                out.clear_output()
                display(Markdown("*PDF support needs `pip install docling` "
                                 "(or `pip install pymupdf`).*"))
                return
            except Exception as e:
                out.clear_output()
                display(Markdown(f"*Couldn't parse the PDF ({type(e).__name__}: {e}).*"))
                return
            out.clear_output()
            display(Markdown(f"✅ Done — opened **`{os.path.basename(path)}`** below."))

    up.observe(on_change, names="value")
    display(W.VBox([up, out]))


# ----------------------------------------------------------------------------
# Banner
# ----------------------------------------------------------------------------
__all__ = [
    "ask", "Dialogue", "tutor", "Polya", "solve",
    "explain", "explain_with_artifacts", "generate_visual_analogy",
    "explain_error", "hint", "quiz", "Quiz", "review",
    "propose", "edit", "recap", "anki", "cmd", "Commands",
    "upload_pdf", "read_pdf", "pdf_to_notebook",
    "session_log", "configure", "configure_images", "md", "html",
    "help_solveit",
]


def help_solveit():
    md(textwrap.dedent("""
    ### 🧰 solveit toolkit — quick reference

    | function | what it does |
    |---|---|
    | `ask("...")` | one-shot question, answer rendered as Markdown |
    | `tutor.ask("...")` | **persistent** tutor dialogue (remembers context) |
    | `solve("problem")` | start a **Pólya** session → `.understand() .plan() .step() .review()` |
    | `explain(x)` | explain a value or snippet at beginner level |
    | `explain_with_artifacts(x)` | explain **+ an interactive HTML artifact** rendered inline |
    | `generate_visual_analogy("concept")` | AI-drawn **visual mnemonic** image, shown inline (Gemini / `gpt-image-2`) |
    | `explain_error()` | explain the **last error** that occurred |
    | `hint("...")` | a **Socratic** nudge — never the full answer |
    | `quiz("topic")` | **interactive** quiz: type answers in boxes → AI-graded feedback |
    | `review(code)` | review the student's *own* code |
    | `propose("task")` | AI writes code into a **new editable cell** (you run it) |
    | `%%edit <how>` | AI rewrites **this cell's** code in place + a comment |
    | `edit(code, "how")` | same, but into a new cell |
    | `cmd.<TAB>` | reusable custom prompts (`/commands`) — `cmd.eli5("loops")` |
    | `cmd.add(name, tmpl)` | save your own command (persists across sessions) |
    | `anki(focus="")` | export session to an **Anki**-importable `.txt` |
    | `upload_pdf()` | **Upload-PDF button** → expands the whole PDF into a new reader notebook (cells + images), parsed by docling/pymupdf |
    | `read_pdf("f.pdf")` | same, from a file path |
    | `tutor.recap()` | **session summary** — what you covered & what to try next |

    *The human is the agent: the AI proposes, **you** read, edit, and run.*
    """).strip())


if _IN_NB:
    _b = _detect_backend()
    md(f"✅ **solveit loaded** · backend=`{_b}` · model=`{_model_for(_b)}` · "
       "type `help_solveit()` for the cheat-sheet.")
