# What Python Can and Can't Do For You

The previous guide helped you spot automations.
This one helps you avoid **building the wrong thing**.

A lot of beginner frustration with Python + AI comes from aiming it at tasks it was never going to handle well. Knowing the shape of the wall before you run at it saves hours.

---

## 1. The core frame: reach, rules, reliability, risk

Before you commit to automating something, ask four questions:

| Question            | What it's really asking                                                  |
| ------------------- | ------------------------------------------------------------------------ |
| **Reach?**          | Can my code actually *get to* the data and *act on* the system?          |
| **Rules?**          | Can I describe the logic in plain steps, or does it need real judgment?  |
| **Reliability?**    | Am I OK with occasional mistakes, or does it have to be perfect?         |
| **Risk?**           | If the script misbehaves, is the worst case recoverable or a disaster?   |

The four answers sort every task into a **green, yellow, or red zone**.

---

## 2. The green zone — Python is great at this

[Inference] These are the categories where a short script plus AI help tends to pay off quickly for beginners.

- **Moving data between files and formats.** CSV ↔ JSON ↔ Excel, PDF text extraction, folder cleanup, log parsing.
- **Talking to APIs.** Anything with an official, documented API — OpenAI, Anthropic, GitHub, Notion, Gmail, Slack, Stripe, weather, maps.
- **Scraping public, static web pages.** Pages that render their content in plain HTML without requiring login.
- **Running things on a schedule.** Nightly backups, daily reports, weekly summaries.
- **Language tasks via an LLM.** Summarizing, classifying, extracting, rewriting, translating — as long as you're willing to spot-check.
- **Gluing tools together.** "When X happens in A, write to B." Python is an excellent plumber.

Common thread: the data is **reachable**, the rules are **describable**, and a small error is **cheap**.

---

## 3. The yellow zone — possible, but fragile

You *can* do these with Python, but they break often and cost more to maintain than beginners expect.

- **Scraping sites that require login, have captchas, or load content via JavaScript.** Playwright can handle some of it, but sites change and scripts rot.
- **Automating desktop apps without an API** (clicking buttons in a native app). Works until the app updates and every coordinate shifts.
- **Parsing wildly inconsistent documents** (e.g., hand-scanned PDFs, messy emails). AI helps a lot, but accuracy is rarely 100%.
- **Anything that "mostly works" 90% of the time** when the other 10% matters. An LLM that summarizes correctly 9 out of 10 times is a demo, not a production tool.
- **Long chains of AI calls without checks.** Each step compounds small errors into big ones.

Rule of thumb: if it's in the yellow zone, **build it small, watch it run, and expect to babysit it.**

---

## 4. The red zone — don't aim Python here

These aren't impossible in some absolute sense, but [Inference] for a beginner learning automation, they're the wrong shape of problem.

### Reach problems (the data isn't reachable)
- Systems behind strict SSO, 2FA, or enterprise auth without an API
- Content inside closed apps (many mobile apps, DRM-protected files)
- Anything that requires physical presence (signing a paper, being in a room)

### Rules problems (the logic needs real judgment)
- "Decide whether this email needs a human reply." (The rules genuinely differ every time.)
- Legal, medical, or hiring decisions where accountability matters.
- Creative work where the value *is* the human judgment, not the throughput.

### Reliability problems (near-perfect is required)
- Anything financial where a mistaken transaction is unrecoverable
- Sending mass communications without a human in the loop
- Medical dosing, safety-critical calculations

### Risk problems (the blast radius is too big)
- Executing trades or moving money automatically
- Bulk-deleting files with no backup
- Auto-responding to customers with AI-generated content with no review

If any of the four "R"s lands in the red — **keep the human in the loop**, or pick a smaller version of the task.

---

## 5. The specific trap of AI-powered automations

Because this course uses AI heavily, it's worth naming the two failure modes beginners run into:

1. **Silent wrongness.** LLMs produce confident, fluent output even when it's wrong. [Inference] Based on observed patterns, this is the single most common source of broken automations students build. *Always* build in a verification step (a human spot-check, a rule-based sanity check, or a second model cross-checking).
2. **Drift.** The same prompt can give different outputs on different days, or when the model version changes. Scripts that worked last month may need re-tuning.

A useful habit: **print the AI's output before you act on it**, for the first dozen runs at least.

---

## 6. A 30-second "which zone is this?" checklist

Before you start:

- [ ] I can reach the input without manual steps. *(if no → yellow or red)*
- [ ] I can describe the processing rules in a paragraph. *(if no → yellow or red)*
- [ ] I'm OK with occasional errors, or I have a way to catch them. *(if no → yellow)*
- [ ] If the script misfires, the worst case is easy to undo. *(if no → red)*

Four checks → build it.
Three checks → build it small and watch it.
Two or fewer → don't automate yet. Do it by hand a few more times and learn the shape of the task first.

---

## 7. A 5-minute exercise for students

1. Take the three "repetitive tasks" list from the previous guide.
2. For each one, answer the four R's: reach, rules, reliability, risk.
3. Sort them into green / yellow / red.
4. Only build the green ones this week.
5. Write one sentence for each red-zone task explaining *why* it's red — that sentence is often the most valuable thing you'll learn in the course.

The goal isn't to become someone who automates everything. It's to become someone who **instantly recognizes what's automatable and what isn't** — and who doesn't waste a weekend fighting a problem that was always in the red zone.
