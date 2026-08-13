# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///
"""
LESSON 07 — Talking to APIs (the internet as an ingredient)
===========================================================

An API is a counter where one program orders data from another. You
send a precisely-worded request ("current weather at these
coordinates, please"), a server sends back structured data. No browser,
no clicking — which is exactly why scripts love APIs.

Today we call a real one: Open-Meteo, a free weather service that needs
no account and no key. One small request, read-only, nothing personal
sent. (AI services work the same way — lesson 08 — they just check ID
at the counter first.)

After this lesson you can READ:  requests.get()  ·  status codes  ·  .json()  ·  digging into nested data

Run me with:
    uv run lessons/07_talking_to_apis.py
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

import requests   # THE package for talking to the web (verified real on PyPI!)

# The "order form": a URL saying what we want. Open-Meteo asks for
# coordinates, so here are a few cities to choose from — a dictionary
# where each city name is filed with its (latitude, longitude).
CITIES = {
    "Lisbon":   (38.72, -9.14),
    "New York": (40.71, -74.01),
    "Tokyo":    (35.68, 139.69),
}

city = "Lisbon"                    # <- a knob you're allowed to turn
latitude, longitude = CITIES[city]

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}&longitude={longitude}"
    "&current=temperature_2m,wind_speed_10m,weather_code"
)
# ^ Look closely: the URL is just an f-string (lesson 01!). Every AI
#   script that "fetches data" builds a URL exactly like this.

print(f"Ordering the current weather for {city}...")

# Why you care: requests.get(url) is the single most common line in
# AI-generated automation — see it, and you know the script goes online.
try:
    response = requests.get(url, timeout=10)
except requests.exceptions.ConnectionError:
    # ^ lesson 06's safety net, wrapped around the one line that can fail
    print("Couldn't reach the internet — check your connection and rerun.")
    raise SystemExit(1)    # stop politely, no scary traceback

# ── PREDICT: what number will this print? ──
# (200 is API-speak for "here you go". 404 = "no such thing". 500 = "we broke".)
print(f"The server answered with status code: {response.status_code}")

# The goods arrive as JSON — which Python turns into... a dictionary!
# The same {label: value} shape you read in lesson 02. This is why we
# learned dictionaries: EVERY API answers in them.
data = response.json()

# ── PREDICT: which labels (keys) came back in the answer? ──
print(f"Top-level labels in the answer: {list(data.keys())}")

# Digging in: data["current"] is a dictionary INSIDE the dictionary —
# chain the square brackets to go deeper, one label at a time.
current = data["current"]
temperature = current["temperature_2m"]
wind = current["wind_speed_10m"]

# The API reports weather as a numeric code; a small dictionary
# translates the common ones into words (.get gives a fallback — the
# polite cousin of ["..."] that never crashes on a missing label).
WEATHER_WORDS = {0: "clear skies", 1: "mostly clear", 2: "partly cloudy",
                 3: "overcast", 45: "fog", 61: "light rain", 63: "rain",
                 80: "rain showers", 95: "thunderstorm"}
sky = WEATHER_WORDS.get(current["weather_code"], "something interesting")

print()
print(f"Right now in {city}: {temperature}°C, wind {wind} km/h, {sky}.")
print()
print("That's the whole API dance: build a URL, get(), check the status,")
print("dig through a dictionary. Lesson 08 does the same dance with AI.")

# ✏️ TRY IT:
#   1. Change city to "Tokyo" and rerun. One knob, whole new answer.
#   2. Add your own city to CITIES (search the web for its latitude and
#      longitude) and point the script at it.
#   3. In the url, change temperature_2m to temperature_2m,relative_humidity_2m
#      then print current["relative_humidity_2m"]. You just READ API
#      docs behavior by experiment — exactly how you'll steer AI scripts.
