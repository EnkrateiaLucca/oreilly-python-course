# 04 — Voice notes to text

## The problem

You record voice notes on your commute — ideas, to-dos, meeting debriefs — and
then never listen to them again, because replaying 6 minutes of your own rambling
to find one action item is worse than losing the idea.

## The ticket

- **Trigger:** I run it manually on a voice note I just recorded.
- **Touches:** reads ONE audio file; transcribes it LOCALLY (the audio never
  leaves my machine); sends only the transcript text to the Anthropic API; with
  `--apply` writes two new files next to the audio. Needs `ANTHROPIC_API_KEY`
  (or `--no-summary` for a fully local, key-free run).
- **Must never:** upload the audio itself anywhere, modify or delete the
  recording, or write any file without `--apply`.
- **Done means:** a readable transcript, a 2-3 sentence summary, and every task I
  spoke out loud captured as a `- [ ]` checkbox item.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that takes an audio file as a CLI argument,
> transcribes it locally with faster-whisper (cpu, int8, vad_filter), then sends
> only the transcript to the Anthropic API — client.messages.create with model
> "claude-opus-4-8" and max_tokens=16000, collecting text blocks where
> block.type == "text" — asking for a short summary plus '- [ ]' action items.
> Print both; only save .transcript.txt and .summary.md next to the audio when I
> pass --apply. Add a --no-summary flag that skips the API entirely. Load
> ANTHROPIC_API_KEY with python-dotenv from the repo-root .env and exit with a
> friendly 3-line fix message if missing — BEFORE the slow transcription step.
> argparse, no classes, friendly errors, under 150 lines.

## Run it

```bash
cd demos/reserve/voice-notes

# Dry run — transcribe + summarize, print everything, save nothing:
uv run voice_notes.py audio-sample.mp3

# No API key yet? Fully local transcript only:
uv run voice_notes.py audio-sample.mp3 --no-summary

# Happy? Save the transcript and summary next to the audio:
uv run voice_notes.py audio-sample.mp3 --apply
```

## Prove it

- The transcript reads like what the recording says (play `audio-sample.mp3`).
- The summary is 2-3 sentences and action items appear as `- [ ]` lines.
- Dry run ends with "nothing saved"; after `--apply`,
  `audio-sample.transcript.txt` and `audio-sample.summary.md` exist next to the
  mp3 and the original mp3 is untouched (same size, same date).

## ✏️ Your turn (5 minutes)

Make the summary speak the note's language. `transcribe()` already detects it
(`info.language`) — then prints it and throws it away — while the prompt in
`summarize()` never mentions language at all, so Claude answers in English no
matter what you spoke. Return the language code from `transcribe()` alongside
the text, and pass it into `summarize()` so the prompt ends with something like
`Reply in language: {language}.` (`main()` is where the two functions meet.)

- **Done means:** `uv run voice_notes.py audio-sample.mp3` still gives an English
  summary — and a 10-second voice note you record in another language gets its
  summary and `- [ ]` items back in that language.
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Ship it

```bash
# macOS/Linux (~/.zshrc):
alias voicenote='uv run ~/oreilly-python-course/demos/reserve/voice-notes/voice_notes.py'
# then:  voicenote ~/Recordings/idea-2026-08-12.m4a --apply
```
