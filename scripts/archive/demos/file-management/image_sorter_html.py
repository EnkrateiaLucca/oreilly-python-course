#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Image sorter with a simple swipe UI.

Usage:
    uv run image_sorter.py /path/to/images
    uv run image_sorter.py /path/to/images --port 8765
    uv run image_sorter.py /path/to/images --permanent-delete

Behavior:
- Swipe RIGHT or press → / D to KEEP
- Swipe LEFT or press ← / A to DELETE
- By default, "delete" moves files into a "_deleted" subfolder
- With --permanent-delete, files are actually removed
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import shutil
import sys
import threading
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import List
from urllib.parse import parse_qs, unquote, urlparse


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
    ".avif",
}


HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
  <title>Image Sorter</title>
  <style>
    :root {
      --bg: #0f1115;
      --panel: #171a21;
      --muted: #9aa4b2;
      --text: #f5f7fb;
      --danger: #ff5f6d;
      --ok: #4cd38a;
      --accent: #6ea8fe;
      --border: rgba(255,255,255,0.08);
    }
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      overflow: hidden;
    }
    .app {
      height: 100%;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 10px;
      padding: 12px;
    }
    .topbar, .bottombar {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 12px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .meta {
      min-width: 0;
    }
    .title {
      font-size: 14px;
      color: var(--muted);
      margin-bottom: 4px;
    }
    .filename {
      font-size: 16px;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: min(70vw, 900px);
    }
    .progress {
      color: var(--muted);
      font-size: 14px;
      white-space: nowrap;
    }
    .stage {
      position: relative;
      min-height: 0;
      display: grid;
      place-items: center;
      overflow: hidden;
      border-radius: 24px;
    }
    .card-wrap {
      position: relative;
      width: min(96vw, 1100px);
      height: min(72vh, 820px);
      display: grid;
      place-items: center;
      touch-action: none;
      user-select: none;
    }
    .card {
      position: absolute;
      width: min(92vw, 980px);
      height: min(68vh, 760px);
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 18px 50px rgba(0,0,0,0.35);
      overflow: hidden;
      display: grid;
      place-items: center;
      transition: transform 180ms ease, opacity 180ms ease;
      will-change: transform;
      backdrop-filter: blur(6px);
    }
    .card img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      pointer-events: none;
    }
    .badge {
      position: absolute;
      top: 18px;
      padding: 10px 14px;
      border-radius: 999px;
      font-weight: 800;
      letter-spacing: 0.08em;
      border: 2px solid currentColor;
      opacity: 0;
      transform: rotate(-10deg);
      background: rgba(0,0,0,0.18);
    }
    .badge.keep { right: 18px; color: var(--ok); }
    .badge.delete { left: 18px; color: var(--danger); transform: rotate(10deg); }
    .hint {
      color: var(--muted);
      font-size: 14px;
    }
    .actions {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }
    button {
      border: 0;
      border-radius: 14px;
      padding: 12px 16px;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      color: white;
    }
    .btn-delete { background: var(--danger); }
    .btn-keep { background: var(--ok); color: #09110d; }
    .btn-skip { background: #2b3340; color: var(--text); }
    .empty {
      text-align: center;
      color: var(--muted);
      padding: 32px;
    }
    .toast {
      position: fixed;
      left: 50%;
      bottom: 90px;
      transform: translateX(-50%);
      background: rgba(20, 23, 30, 0.94);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 12px 16px;
      border-radius: 12px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 180ms ease, transform 180ms ease;
    }
    .toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(-4px);
    }
  </style>
</head>
<body>
  <div class="app">
    <div class="topbar">
      <div class="meta">
        <div class="title">Current image</div>
        <div class="filename" id="filename">Loading…</div>
      </div>
      <div class="progress" id="progress">0 / 0</div>
    </div>

    <div class="stage">
      <div class="card-wrap" id="cardWrap">
        <div class="empty" id="emptyState" style="display:none;">
          <h2>Done 🎉</h2>
          <p>No more images left in this folder.</p>
        </div>

        <div class="card" id="card" style="display:none;">
          <div class="badge delete" id="deleteBadge">DELETE</div>
          <div class="badge keep" id="keepBadge">KEEP</div>
          <img id="image" alt="Current image" draggable="false" />
        </div>
      </div>
    </div>

    <div class="bottombar">
      <div class="hint">
        Swipe left = delete · swipe right = keep · keyboard: ←/A delete, →/D keep, space skip
      </div>
      <div class="actions">
        <button class="btn-delete" id="deleteBtn">Delete</button>
        <button class="btn-skip" id="skipBtn">Skip</button>
        <button class="btn-keep" id="keepBtn">Keep</button>
      </div>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    const state = {
      images: [],
      index: 0,
      pointerDown: false,
      startX: 0,
      currentX: 0,
      dragging: false,
      threshold: 120,
      busy: false,
    };

    const el = {
      filename: document.getElementById("filename"),
      progress: document.getElementById("progress"),
      card: document.getElementById("card"),
      image: document.getElementById("image"),
      keepBadge: document.getElementById("keepBadge"),
      deleteBadge: document.getElementById("deleteBadge"),
      keepBtn: document.getElementById("keepBtn"),
      deleteBtn: document.getElementById("deleteBtn"),
      skipBtn: document.getElementById("skipBtn"),
      emptyState: document.getElementById("emptyState"),
      toast: document.getElementById("toast"),
    };

    function showToast(msg) {
      el.toast.textContent = msg;
      el.toast.classList.add("show");
      clearTimeout(showToast._t);
      showToast._t = setTimeout(() => el.toast.classList.remove("show"), 1200);
    }

    async function fetchJSON(url, options = {}) {
      const res = await fetch(url, options);
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      return await res.json();
    }

    async function loadImages() {
      const data = await fetchJSON("/api/images");
      state.images = data.images || [];
      state.index = 0;
      render();
    }

    function currentImage() {
      return state.images[state.index] || null;
    }

    function resetCardVisual() {
      el.card.style.transform = "translateX(0px) rotate(0deg)";
      el.card.style.opacity = "1";
      el.keepBadge.style.opacity = "0";
      el.deleteBadge.style.opacity = "0";
    }

    function render() {
      const img = currentImage();
      el.progress.textContent = state.images.length
        ? `${state.index + 1} / ${state.images.length}`
        : "0 / 0";

      if (!img) {
        el.card.style.display = "none";
        el.emptyState.style.display = "block";
        el.filename.textContent = "No images left";
        return;
      }

      el.emptyState.style.display = "none";
      el.card.style.display = "grid";
      el.filename.textContent = img.name;
      el.image.src = `/image?path=${encodeURIComponent(img.path)}&ts=${Date.now()}`;
      resetCardVisual();
    }

    function updateDragVisual(dx) {
      const rotate = dx * 0.04;
      el.card.style.transform = `translateX(${dx}px) rotate(${rotate}deg)`;
      const keepOpacity = Math.max(0, Math.min(1, dx / 120));
      const deleteOpacity = Math.max(0, Math.min(1, -dx / 120));
      el.keepBadge.style.opacity = String(keepOpacity);
      el.deleteBadge.style.opacity = String(deleteOpacity);
    }

    async function act(action) {
      if (state.busy) return;
      const img = currentImage();
      if (!img) return;

      state.busy = true;
      try {
        if (action === "keep") {
          showToast("Kept");
        } else if (action === "delete") {
          await fetchJSON("/api/action", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ action: "delete", path: img.path }),
          });
          showToast("Deleted");
        }

        state.index += 1;
        render();
      } catch (err) {
        console.error(err);
        showToast("Action failed");
      } finally {
        state.busy = false;
      }
    }

    function flyOut(direction) {
      const dx = direction === "right" ? window.innerWidth : -window.innerWidth;
      const rot = direction === "right" ? 18 : -18;
      el.card.style.transform = `translateX(${dx}px) rotate(${rot}deg)`;
      el.card.style.opacity = "0";
    }

    async function commitSwipe(direction) {
      flyOut(direction);
      await new Promise(r => setTimeout(r, 140));
      if (direction === "right") {
        await act("keep");
      } else {
        await act("delete");
      }
    }

    el.keepBtn.addEventListener("click", () => commitSwipe("right"));
    el.deleteBtn.addEventListener("click", () => commitSwipe("left"));
    el.skipBtn.addEventListener("click", () => {
      if (state.images.length) {
        state.index += 1;
        render();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (state.busy || !currentImage()) return;
      if (e.key === "ArrowRight" || e.key.toLowerCase() === "d") {
        commitSwipe("right");
      } else if (e.key === "ArrowLeft" || e.key.toLowerCase() === "a") {
        commitSwipe("left");
      } else if (e.key === " ") {
        e.preventDefault();
        state.index += 1;
        render();
      }
    });

    const dragStart = (clientX) => {
      if (!currentImage() || state.busy) return;
      state.pointerDown = true;
      state.dragging = true;
      state.startX = clientX;
      state.currentX = clientX;
      el.card.style.transition = "none";
    };

    const dragMove = (clientX) => {
      if (!state.pointerDown || !state.dragging) return;
      state.currentX = clientX;
      const dx = state.currentX - state.startX;
      updateDragVisual(dx);
    };

    const dragEnd = async () => {
      if (!state.pointerDown) return;
      state.pointerDown = false;
      const dx = state.currentX - state.startX;
      el.card.style.transition = "transform 180ms ease, opacity 180ms ease";

      if (dx > state.threshold) {
        await commitSwipe("right");
      } else if (dx < -state.threshold) {
        await commitSwipe("left");
      } else {
        resetCardVisual();
      }
      state.dragging = false;
    };

    el.card.addEventListener("pointerdown", (e) => {
      dragStart(e.clientX);
      el.card.setPointerCapture(e.pointerId);
    });
    el.card.addEventListener("pointermove", (e) => dragMove(e.clientX));
    el.card.addEventListener("pointerup", dragEnd);
    el.card.addEventListener("pointercancel", dragEnd);

    loadImages().catch(err => {
      console.error(err);
      el.filename.textContent = "Failed to load images";
      el.progress.textContent = "Error";
    });
  </script>
</body>
</html>
"""


@dataclass
class AppState:
    image_dir: Path
    deleted_dir: Path
    permanent_delete: bool

    def list_images(self) -> List[Path]:
        files = []
        for p in sorted(self.image_dir.iterdir()):
            if not p.is_file():
                continue
            if p.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            files.append(p)
        return files

    def delete_image(self, rel_path: str) -> None:
        target = (self.image_dir / rel_path).resolve()
        base = self.image_dir.resolve()

        if not str(target).startswith(str(base)):
            raise ValueError("Invalid image path.")

        if not target.exists() or not target.is_file():
            raise FileNotFoundError("Image not found.")

        if self.permanent_delete:
            target.unlink()
        else:
            self.deleted_dir.mkdir(exist_ok=True)
            destination = self.deleted_dir / target.name
            destination = unique_path(destination)
            shutil.move(str(target), str(destination))


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


class Handler(BaseHTTPRequestHandler):
    server_version = "ImageSorter/1.0"

    @property
    def state(self) -> AppState:
        return self.server.app_state  # type: ignore[attr-defined]

    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, text: str, status: int = 200, content_type: str = "text/plain; charset=utf-8") -> None:
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._send_text(HTML_PAGE, content_type="text/html; charset=utf-8")
            return

        if parsed.path == "/api/images":
            images = self.state.list_images()
            payload = {
                "images": [
                    {
                        "name": p.name,
                        "path": p.relative_to(self.state.image_dir).as_posix(),
                    }
                    for p in images
                ]
            }
            self._send_json(payload)
            return

        if parsed.path == "/image":
            qs = parse_qs(parsed.query)
            raw_path = qs.get("path", [""])[0]
            rel_path = unquote(raw_path)

            try:
                target = (self.state.image_dir / rel_path).resolve()
                base = self.state.image_dir.resolve()
                if not str(target).startswith(str(base)):
                    raise ValueError("Invalid path.")
                if not target.exists() or not target.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND, "Image not found.")
                    return

                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", guess_mime(target))
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                self.send_error(HTTPStatus.BAD_REQUEST, str(e))
                return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found.")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path != "/api/action":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found.")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            body = json.loads(raw.decode("utf-8"))

            action = body.get("action")
            rel_path = body.get("path", "")

            if action != "delete":
                self._send_json({"ok": False, "error": "Unsupported action."}, status=400)
                return

            self.state.delete_image(rel_path)
            self._send_json({"ok": True})
        except FileNotFoundError as e:
            self._send_json({"ok": False, "error": str(e)}, status=404)
        except Exception as e:
            self._send_json({"ok": False, "error": str(e)}, status=400)

    def log_message(self, fmt: str, *args) -> None:
        # quieter output
        sys.stderr.write("[server] " + fmt % args + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Swipe-based image sorter.")
    parser.add_argument("folder", help="Folder containing images.")
    parser.add_argument("--port", type=int, default=8765, help="Port to run the local server on.")
    parser.add_argument(
        "--permanent-delete",
        action="store_true",
        help="Actually delete files instead of moving them to a _deleted subfolder.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open the browser.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    image_dir = Path(args.folder).expanduser().resolve()
    if not image_dir.exists() or not image_dir.is_dir():
      raise SystemExit(f"Folder does not exist or is not a directory: {image_dir}")

    deleted_dir = image_dir / "_deleted"
    state = AppState(
        image_dir=image_dir,
        deleted_dir=deleted_dir,
        permanent_delete=bool(args.permanent_delete),
    )

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.app_state = state  # type: ignore[attr-defined]

    url = f"http://127.0.0.1:{args.port}"
    mode = "permanent delete" if args.permanent_delete else f"move deleted files to {deleted_dir.name}/"

    print(f"\nServing: {image_dir}")
    print(f"Mode: {mode}")
    print(f"Open: {url}\n")

    if not args.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()