# Research: Simon Willison — Red-Green TDD as an Agentic Engineering Pattern

- Source guide: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/
- Researched for: 1-2 presentation slides on TDD for an O'Reilly **beginner** Python + AI automation course.

---

## The core pattern (plain English)

Test-Driven Development means: **write the test first, watch it fail, then write just enough code to make it pass.** [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

Willison's own framing: "You write the automated tests first, confirm that they fail, then iterate on the implementation until the tests pass." [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

The loop has a memorable color name:
- **RED** — write a test for behavior that doesn't exist yet. Run it. It fails (red). Failing first proves the test actually checks something. [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]
- **GREEN** — write/generate the smallest code that makes the test pass. Run it. It passes (green). [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

Critical rule: "It's important to confirm that the tests fail before implementing the code to make them pass." Skipping this risks a test that already passes and therefore proves nothing. [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

---

## Why this matters specifically for AI / agentic code

Tests are guardrails for AI-generated code. Willison: "A significant risk with coding agents is that they might write code that doesn't work, or build code that is unnecessary and never gets used, or both." Writing the test first forces the AI to "solve a clearly defined problem rather than generating unnecessary code." [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

It also protects future changes: "As projects grow the chance that a new change might break an existing feature grows with them. A comprehensive test suite is by far the most effective way to keep those features working." [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

Example prompt he uses to drive an agent: "Build a Python function to extract headers from a markdown string. Use red/green TDD." [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

---

## Beginner translation (course voice)

For students new to Python + AI APIs:
- A "test" is just a tiny piece of code that says **"if my function works, this should be true."**
- You write that check **before** the real function exists, so you've described the job clearly.
- The AI (or you) then writes the function until the check goes from failing (red) to passing (green).
- Bonus: the test stays around forever and yells if a later change breaks things.

This connects naturally to the course's input → process → output mental model: the test pins down the expected **output** for a given **input**, and the AI fills in the **process**.

---

## Decision — recommended 1-2 slide structure

### Slide 1 — "Red → Green: Tell the AI exactly what 'done' means"
- **Headline idea:** Write the check first, then let AI fill in the code.
- **Three bullets:**
  1. RED: write a test that describes the result you want — run it, watch it fail.
  2. GREEN: ask the AI to write code until the test passes.
  3. Why: the test stops the AI from "writing code that doesn't work, or ... unnecessary ... or both." [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]
- **Key takeaway for beginners:** A failing test first = a clear instruction the AI can't fudge.

### Slide 2 (optional) — "A 6-line example beginners can read"
Recommended minimal, framework-free code (uses plain `assert`, no pytest needed — lowest barrier for absolute beginners):

```python
# RED: describe what "done" looks like (this fails — get_headers doesn't exist yet)
def test_get_headers():
    md = "# Title\n\nsome text\n## Section"
    assert get_headers(md) == ["Title", "Section"]

test_get_headers()  # run it -> NameError / AssertionError = RED
```

Then the prompt to the AI: "Build a Python function `get_headers(markdown)` that returns the header text. Use red/green TDD." [source: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/]

- **Key takeaway:** Once the same `test_get_headers()` runs with no error, you're GREEN — and you keep the test forever as a safety net.

**Recommendation:** Use **both** slides if pacing allows (one concept, one example). If only one slide fits, use **Slide 1** and put the code example in the speaker notes or a notebook cell, since beginners absorb the loop concept faster than the syntax. `[unverified]` pacing call — depends on the section's existing slide budget, which the slides sub-agent should confirm.

---

## `[unverified]` items
- `[unverified]` Whether the guide recommends a specific test framework (pytest vs `unittest` vs plain `assert`). The extracted content shows plain-language TDD without mandating a framework; the `assert`-based example above is a course-level recommendation, not a direct quote from the guide.
- `[unverified]` Exact section budget / slide count available in the course presentation (defer to slides sub-agent).
