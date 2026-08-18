# Prompt
I'm about to build a small automation for this task:

<one-sentence task description>

Before I build anything, act as a skeptical advisor:
1. Is there an existing tool, app, or built-in OS feature that already does this
   (Mac and Windows)? Name specific tools, free ones first.
2. Is there a no-code service (Zapier/n8n/Shortcuts) that does it, and what would
   it cost?
3. What does a custom Python script get me that those don't?
4. Verdict: BUY / USE BUILT-IN / BUILD — one sentence why.

## How to read the verdict

- **USE BUILT-IN / BUY** — great, you just saved an afternoon. Done.
- **BUILD** — usually one of these good reasons:
  - it touches **local files** or desktop apps no web service can reach
  - it needs **your custom logic** or your AI prompt in the middle
  - it should run **on your machine** (privacy, no subscription, no upload)
  - the existing tools cost more than the 30 minutes a script takes now
- Mixed answer? Prototype the script version in 30 minutes; keep the ticket —
  if maintenance ever gets annoying, the ticket is also your shopping spec.

## The honest comparison (worth remembering)

No-code tools (Zapier, n8n) have guardrails built in — that's their safety story.
Raw Python has no guardrails — **the SCRIPT loop is your guardrails** — and in
exchange it reaches places connectors can't: your filesystem, your desktop apps,
custom logic, scheduled local jobs, zero subscription.