import tkinter as tk
import pyperclip
import threading
import base64
import urllib.parse
import re
import os
import select
import struct
import subprocess
import shutil
import pystray
from PIL import Image, ImageDraw, ImageFont


# ─────────────────────────────────────────────
# UNICODE MAPPING TABLES
# ─────────────────────────────────────────────

SMALL_CAPS = {
    'a': '\u1D00', 'b': '\u1D01', 'c': '\u1D04', 'd': '\u1D05',
    'e': '\u1D07', 'f': '\uA730', 'g': '\u0262', 'h': '\u029C',
    'i': '\u026A', 'j': '\u1D0A', 'k': '\u1D0B', 'l': '\u029F',
    'm': '\u1D0D', 'n': '\u0274', 'o': '\u1D0F', 'p': '\u1D18',
    'q': '\uA7AF', 'r': '\u0280', 's': '\uA731', 't': '\u1D1B',
    'u': '\u1D1C', 'v': '\u1D20', 'w': '\u1D21', 'x': '\u02E3',
    'y': '\u028F', 'z': '\u1D22',
}

SUPERSCRIPT = {
    'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 'f': 'ᶠ',
    'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ', 'k': 'ᵏ', 'l': 'ˡ',
    'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 'p': 'ᵖ', 'q': 'ᑫ', 'r': 'ʳ',
    's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ', 'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ',
    'y': 'ʸ', 'z': 'ᶻ',
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
}

SUBSCRIPT = {
    'a': 'ₐ', 'e': 'ₑ', 'h': 'ₕ', 'i': 'ᵢ', 'j': 'ⱼ',
    'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'o': 'ₒ',
    'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ', 'u': 'ᵤ',
    'v': 'ᵥ', 'x': 'ₓ',
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
}

BOLD = {
    'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞',
    'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
    'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨',
    'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
    'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
    'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄',
    'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉',
    'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎',
    'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓',
    'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
}

ITALIC = {
    'a': '𝑎', 'b': '𝑏', 'c': '𝑐', 'd': '𝑑', 'e': '𝑒', 'f': '𝑓',
    'g': '𝑔', 'h': 'ℎ', 'i': '𝑖', 'j': '𝑗', 'k': '𝑘', 'l': '𝑙',
    'm': '𝑚', 'n': '𝑛', 'o': '𝑜', 'p': '𝑝', 'q': '𝑞', 'r': '𝑟',
    's': '𝑠', 't': '𝑡', 'u': '𝑢', 'v': '𝑣', 'w': '𝑤', 'x': '𝑥',
    'y': '𝑦', 'z': '𝑧',
    'A': '𝐴', 'B': '𝐵', 'C': '𝐶', 'D': '𝐷', 'E': '𝐸',
    'F': '𝐹', 'G': '𝐺', 'H': '𝐻', 'I': '𝐼', 'J': '𝐽',
    'K': '𝐾', 'L': '𝐿', 'M': '𝑀', 'N': '𝑁', 'O': '𝑂',
    'P': '𝑃', 'Q': '𝑄', 'R': '𝑅', 'S': '𝑆', 'T': '𝑇',
    'U': '𝑈', 'V': '𝑉', 'W': '𝑊', 'X': '𝑋', 'Y': '𝑌', 'Z': '𝑍',
}

SCRIPT = {
    'a': '𝒶', 'b': '𝒷', 'c': '𝒸', 'd': '𝒹', 'e': 'ℯ', 'f': '𝒻',
    'g': '𝓰', 'h': '𝒽', 'i': '𝒾', 'j': '𝒿', 'k': '𝓀', 'l': '𝓁',
    'm': '𝓂', 'n': '𝓃', 'o': 'ℴ', 'p': '𝓅', 'q': '𝓆', 'r': '𝓇',
    's': '𝓈', 't': '𝓉', 'u': '𝓊', 'v': '𝓋', 'w': '𝓌', 'x': '𝓍',
    'y': '𝓎', 'z': '𝓏',
    'A': '𝒜', 'B': '𝓑', 'C': '𝒞', 'D': '𝒟', 'E': '𝓔',
    'F': '𝓕', 'G': '𝒢', 'H': '𝓗', 'I': '𝓘', 'J': '𝒥',
    'K': '𝒦', 'L': '𝓛', 'M': '𝓜', 'N': '𝒩', 'O': '𝒪',
    'P': '𝒫', 'Q': '𝒬', 'R': '𝓡', 'S': '𝒮', 'T': '𝒯',
    'U': '𝒰', 'V': '𝒱', 'W': '𝒲', 'X': '𝒳', 'Y': '𝒴', 'Z': '𝒵',
}

FRAKTUR = {
    'a': '𝔞', 'b': '𝔟', 'c': '𝔠', 'd': '𝔡', 'e': '𝔢', 'f': '𝔣',
    'g': '𝔤', 'h': '𝔥', 'i': '𝔦', 'j': '𝔧', 'k': '𝔨', 'l': '𝔩',
    'm': '𝔪', 'n': '𝔫', 'o': '𝔬', 'p': '𝔭', 'q': '𝔮', 'r': '𝔯',
    's': '𝔰', 't': '𝔱', 'u': '𝔲', 'v': '𝔳', 'w': '𝔴', 'x': '𝔵',
    'y': '𝔶', 'z': '𝔷',
    'A': '𝔄', 'B': '𝔅', 'C': 'ℭ', 'D': '𝔇', 'E': '𝔈',
    'F': '𝔉', 'G': '𝔊', 'H': 'ℌ', 'I': 'ℑ', 'J': '𝔍',
    'K': '𝔎', 'L': '𝔏', 'M': '𝔐', 'N': '𝔑', 'O': '𝔒',
    'P': '𝔓', 'Q': '𝔔', 'R': 'ℜ', 'S': '𝔖', 'T': '𝔗',
    'U': '𝔘', 'V': '𝔙', 'W': '𝔚', 'X': '𝔛', 'Y': '𝔜', 'Z': 'ℨ',
}

DOUBLE_STRUCK = {
    'a': '𝕒', 'b': '𝕓', 'c': '𝕔', 'd': '𝕕', 'e': '𝕖', 'f': '𝕗',
    'g': '𝕘', 'h': '𝕙', 'i': '𝕚', 'j': '𝕛', 'k': '𝕜', 'l': '𝕝',
    'm': '𝕞', 'n': '𝕟', 'o': '𝕠', 'p': '𝕡', 'q': '𝕢', 'r': '𝕣',
    's': '𝕤', 't': '𝕥', 'u': '𝕦', 'v': '𝕧', 'w': '𝕨', 'x': '𝕩',
    'y': '𝕪', 'z': '𝕫',
    'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼',
    'F': '𝔽', 'G': '𝔾', 'H': 'ℍ', 'I': '𝕀', 'J': '𝕁',
    'K': '𝕂', 'L': '𝕃', 'M': '𝕄', 'N': 'ℕ', 'O': '𝕆',
    'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'S': '𝕊', 'T': '𝕋',
    'U': '𝕌', 'V': '𝕍', 'W': '𝕎', 'X': '𝕏', 'Y': '𝕐', 'Z': 'ℤ',
}

MONOSPACE = {
    'a': '𝚊', 'b': '𝚋', 'c': '𝚌', 'd': '𝚍', 'e': '𝚎', 'f': '𝚏',
    'g': '𝚐', 'h': '𝚑', 'i': '𝚒', 'j': '𝚓', 'k': '𝚔', 'l': '𝚕',
    'm': '𝚖', 'n': '𝚗', 'o': '𝚘', 'p': '𝚙', 'q': '𝚚', 'r': '𝚛',
    's': '𝚜', 't': '𝚝', 'u': '𝚞', 'v': '𝚟', 'w': '𝚠', 'x': '𝚡',
    'y': '𝚢', 'z': '𝚣',
    'A': '𝙰', 'B': '𝙱', 'C': '𝙲', 'D': '𝙳', 'E': '𝙴',
    'F': '𝙵', 'G': '𝙶', 'H': '𝙷', 'I': '𝙸', 'J': '𝙹',
    'K': '𝙺', 'L': '𝙻', 'M': '𝙼', 'N': '𝙽', 'O': '𝙾',
    'P': '𝙿', 'Q': '𝚀', 'R': '𝚁', 'S': '𝚂', 'T': '𝚃',
    'U': '𝚄', 'V': '𝚅', 'W': '𝚆', 'X': '𝚇', 'Y': '𝚈', 'Z': '𝚉',
}

SANS_SERIF = {
    'a': '𝖺', 'b': '𝖻', 'c': '𝖼', 'd': '𝖽', 'e': '𝖾', 'f': '𝖿',
    'g': '𝗀', 'h': '𝗁', 'i': '𝗂', 'j': '𝗃', 'k': '𝗄', 'l': '𝗅',
    'm': '𝗆', 'n': '𝗇', 'o': '𝗈', 'p': '𝗉', 'q': '𝗊', 'r': '𝗋',
    's': '𝗌', 't': '𝗍', 'u': '𝗎', 'v': '𝗏', 'w': '𝗐', 'x': '𝗑',
    'y': '𝗒', 'z': '𝗓',
    'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘',
    'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜', 'J': '𝗝',
    'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢',
    'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧',
    'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
}


def transform(text, mapping):
    """Apply a character mapping to text, preserving non-mapped chars."""
    result = []
    for ch in text:
        lower = ch.lower()
        if ch in mapping:
            result.append(mapping[ch])
        elif lower in mapping:
            result.append(mapping[lower])
        else:
            result.append(ch)
    return ''.join(result)


def _clip_copy(text):
    """Copy to clipboard. Prefer wl-clipboard, fall back to pyperclip."""
    if shutil.which("wl-copy"):
        try:
            subprocess.run(["wl-copy"], input=text.encode(), check=True)
            return True
        except Exception:
            pass
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
# RAW EVDEV HOTKEY LISTENER
# (runs unprivileged; no need for the keyboard lib or root)
# ─────────────────────────────────────────────

# linux/input-event-codes.h
KEY_LEFTCTRL = 29
KEY_RIGHTCTRL = 97
KEY_LEFTSHIFT = 42
KEY_RIGHTSHIFT = 54
KEY_E = 18

EV_KEY = 1


def _list_kbd_event_paths():
    """Yield /dev/input/eventN paths for devices that handle keyboard input."""
    paths = []
    try:
        with open("/proc/bus/input/devices") as f:
            for block in f.read().split("\n\n"):
                if "kbd" not in block or "event" not in block:
                    continue
                m = re.search(r"event(\d+)", block)
                if m:
                    paths.append(f"/dev/input/event{m.group(1)}")
    except FileNotFoundError:
        pass
    return paths


def _evdev_listen(callback, stop_event):
    """Read raw input events; call callback() when Ctrl+Shift+E is pressed."""
    fds = []
    paths = _list_kbd_event_paths()
    for path in paths:
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            fds.append(fd)
        except OSError:
            pass
    if not fds:
        return

    ctrl = False
    shift = False
    try:
        while not stop_event.is_set():
            r, _, _ = select.select(fds, [], [], 0.25)
            for fd in r:
                try:
                    data = os.read(fd, 24)
                except BlockingIOError:
                    continue
                if len(data) < 24:
                    continue
                _, _, etype, code, value = struct.unpack("llHHi", data)
                if etype != EV_KEY:
                    continue
                if code in (KEY_LEFTCTRL, KEY_RIGHTCTRL):
                    ctrl = value != 0
                elif code in (KEY_LEFTSHIFT, KEY_RIGHTSHIFT):
                    shift = value != 0
                elif code == KEY_E and value == 1 and ctrl and shift:
                    callback()
    finally:
        for fd in fds:
            try:
                os.close(fd)
            except OSError:
                pass


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────

class TextTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text Tool")
        self.root.geometry("520x460")
        self.root.minsize(460, 440)
        self.root.attributes("-topmost", True)
        self.topmost = True
        self.root.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

        # Input pane (source text — paste/capture lands here)
        input_frame = tk.LabelFrame(self.root, text="Input", padx=4, pady=2)
        input_frame.pack(fill="both", expand=True, padx=5, pady=(5, 2))
        self.input_var = tk.Text(input_frame, wrap="word", font=("Noto Sans Math", 10),
                                 undo=True, maxundo=200, height=4)
        self.input_var.pack(fill="both", expand=True)
        self.input_var.bind("<<Modified>>", self._on_modified)

        # Preview pane (read-only result of transforms)
        preview_frame = tk.LabelFrame(self.root, text="Preview", padx=4, pady=2)
        preview_frame.pack(fill="both", expand=True, padx=5, pady=2)
        self.preview_var = tk.Text(preview_frame, wrap="word", font=("Noto Sans Math", 10),
                                   state="disabled", height=4)
        self.preview_var.pack(fill="both", expand=True)

        # Copy button under preview
        copy_row = tk.Frame(self.root)
        copy_row.pack(fill="x", padx=5, pady=(0, 2))
        self.copy_btn = tk.Button(copy_row, text="Copy Preview", command=self.copy_out, width=15)
        self.copy_btn.pack(side="left")

        # Status bar
        self.status = tk.Label(self.root, text="Ready. Press Ctrl+Shift+E to show window.",
                               anchor="w", relief="sunken")
        self.status.pack(fill="x", padx=5, pady=(0, 2))

        # ── Category bar ──
        cat_frame = tk.Frame(self.root)
        cat_frame.pack(fill="x", padx=5, pady=(2, 0))

        self.categories = [
            ("Style", [
                ("Small Caps", lambda: self._apply(SMALL_CAPS, "Small Caps")),
                ("Superscript", lambda: self._apply(SUPERSCRIPT, "Superscript")),
                ("Subscript", lambda: self._apply(SUBSCRIPT, "Subscript")),
                ("Bold", lambda: self._apply(BOLD, "Bold")),
                ("Italic", lambda: self._apply(ITALIC, "Italic")),
                ("Script", lambda: self._apply(SCRIPT, "Script")),
                ("Fraktur", lambda: self._apply(FRAKTUR, "Fraktur")),
                ("Double", lambda: self._apply(DOUBLE_STRUCK, "Double-Struck")),
                ("Mono", lambda: self._apply(MONOSPACE, "Monospace")),
                ("Sans", lambda: self._apply(SANS_SERIF, "Sans-Serif")),
            ]),
            ("Case", [
                ("UPPER", self.to_upper),
                ("lower", self.to_lower),
                ("Title", self.to_title),
                ("aLtErNaTe", self.to_alternate),
                ("iNVERSE", self.to_inverse),
            ]),
            ("Text Ops", [
                ("Reverse", self.reverse_text),
                ("Rev Lines", self.reverse_lines),
                ("Sort Lines", self.sort_lines),
                ("Dedup", self.dedup_lines),
                ("Number", self.number_lines),
                ("Trim Sp", self.trim_spaces),
                ("No WS", self.remove_whitespace),
                ("Sp→NL", self.spaces_to_newlines),
                ("NL→Sp", self.newlines_to_spaces),
            ]),
            ("Encode", [
                ("B64 Enc", self.b64_encode),
                ("B64 Dec", self.b64_decode),
                ("URL Enc", self.url_encode),
                ("URL Dec", self.url_decode),
                ("Topmost", self.toggle_topmost),
            ]),
        ]

        self.cat_buttons = {}
        for name, _ in self.categories:
            b = tk.Button(cat_frame, text=name, command=lambda n=name: self._show_category(n))
            b.pack(side="left", fill="x", expand=True, padx=2, pady=1)
            self.cat_buttons[name] = b

        # Options grid (rebuilt on category click)
        self.options_frame = tk.Frame(self.root)
        self.options_frame.pack(fill="x", padx=5, pady=2)
        self._show_category("Style")

        # Hotkey listener
        threading.Thread(target=self._hotkey_listener, daemon=True).start()

        # System tray + initial position
        self._init_tray()
        self.root.after(100, self._position_bottom_right)

    def _show_category(self, name):
        for w in self.options_frame.winfo_children():
            w.destroy()
        buttons = dict(self.categories)[name]
        cols = 4
        for i, (text, command) in enumerate(buttons):
            row, col = divmod(i, cols)
            tk.Button(self.options_frame, text=text, command=command, width=10).grid(
                row=row, column=col, padx=2, pady=1, sticky="ew")
        for c in range(cols):
            self.options_frame.columnconfigure(c, weight=1)
        for cat, b in self.cat_buttons.items():
            b.config(relief="sunken" if cat == name else "raised")

    # ── Core helpers ──

    def _get_input(self):
        return self.input_var.get("1.0", "end-1c")

    def _on_modified(self, event=None):
        self.input_var.edit_modified(False)
        self._render_preview()

    def _render_preview(self):
        self.preview_var.config(state="normal")
        self.preview_var.delete("1.0", "end")
        self.preview_var.insert("1.0", self._get_input())
        self.preview_var.config(state="disabled")

    def _status(self, msg):
        self.status.config(text=msg)

    def _render(self, text, name):
        self.preview_var.config(state="normal")
        self.preview_var.delete("1.0", "end")
        self.preview_var.insert("1.0", text)
        self.preview_var.config(state="disabled")
        self._status(f"→ {name}")

    def _apply(self, mapping, name):
        self._render(transform(self._get_input(), mapping), name)

    # ── Case transforms ──

    def to_upper(self):
        self._render(self._get_input().upper(), "UPPERCASE")

    def to_lower(self):
        self._render(self._get_input().lower(), "lowercase")

    def to_title(self):
        self._render(self._get_input().title(), "Title Case")

    def to_alternate(self):
        result = "".join(c.upper() if i % 2 == 0 else c.lower()
                        for i, c in enumerate(self._get_input()))
        self._render(result, "aLtErNaTe")

    def to_inverse(self):
        result = "".join(c.lower() if c.isupper() else c.upper()
                        for c in self._get_input())
        self._render(result, "iNVERSE cASE")

    # ── Text ops ──

    def reverse_text(self):
        self._render(self._get_input()[::-1], "Reversed")

    def reverse_lines(self):
        lines = self._get_input().splitlines()
        self._render("\n".join(reversed(lines)), "Lines Reversed")

    def sort_lines(self):
        lines = self._get_input().splitlines()
        self._render("\n".join(sorted(lines)), "Lines Sorted")

    def dedup_lines(self):
        seen = set()
        lines = []
        for line in self._get_input().splitlines():
            if line not in seen:
                seen.add(line)
                lines.append(line)
        self._render("\n".join(lines), "Duplicates Removed")

    def number_lines(self):
        lines = self._get_input().splitlines()
        self._render("\n".join(f"{i+1:4d}  {l}" for i, l in enumerate(lines)), "Numbered")

    def trim_spaces(self):
        self._render(re.sub(r' {2,}', ' ', self._get_input()).strip(),
                     "Extra Spaces Removed")

    def remove_whitespace(self):
        self._render(re.sub(r'\s+', '', self._get_input()), "All Whitespace Removed")

    def spaces_to_newlines(self):
        self._render(self._get_input().replace(" ", "\n"), "Spaces → Newlines")

    def newlines_to_spaces(self):
        self._render(self._get_input().replace("\n", " "), "Newlines → Spaces")

    # ── Encoding ──

    def b64_encode(self):
        try:
            self._render(base64.b64encode(self._get_input().encode()).decode(),
                         "Base64 Encoded")
        except Exception as e:
            self._status(f"Error: {e}")

    def b64_decode(self):
        try:
            self._render(base64.b64decode(self._get_input().encode()).decode(),
                         "Base64 Decoded")
        except Exception as e:
            self._status(f"Error: {e}")

    def url_encode(self):
        self._render(urllib.parse.quote(self._get_input(), safe=""), "URL Encoded")

    def url_decode(self):
        try:
            self._render(urllib.parse.unquote(self._get_input()), "URL Decoded")
        except Exception as e:
            self._status(f"Error: {e}")

    def copy_out(self):
        text = self.preview_var.get("1.0", "end-1c")
        if _clip_copy(text):
            self._status("✓ Copied to clipboard")
        else:
            self._status("Error: no clipboard available")

    def toggle_topmost(self):
        self.topmost = not self.topmost
        self.root.attributes("-topmost", self.topmost)
        self._status(f"→ Topmost {'ON' if self.topmost else 'OFF'}")

    def _hide_to_tray(self):
        self.root.withdraw()

    def _init_tray(self):
        """Create the system tray icon with Show/Quit menu."""
        image = self._make_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show", self._tray_show, default=True),
            pystray.MenuItem("Quit", self._quit),
        )
        self.tray_icon = pystray.Icon("texttool", image, "Text Tool", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    @staticmethod
    def _make_tray_image():
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([2, 2, 62, 62], radius=14, fill="#2d7a3f")
        try:
            font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 36)
        except Exception:
            font = ImageFont.load_default()
        draw.text((32, 34), "T", font=font, fill="white", anchor="mm")
        return img

    def _tray_show(self, icon=None):
        self.root.after(0, self._show_window)

    def _toggle_window(self):
        self.root.after(0, self._do_toggle)

    def _do_toggle(self):
        if self.root.state() == "normal":
            self.root.withdraw()
        else:
            self._show_window()

    def _show_window(self):
        self.root.deiconify()
        self._position_bottom_right()
        self.root.attributes("-topmost", self.topmost)
        self.root.lift()
        self.root.focus_force()

    def _quit(self, icon=None):
        self.root.after(0, self._do_quit)

    def _do_quit(self):
        try:
            self._hotkey_stop.set()
        except Exception:
            pass
        try:
            self.tray_icon.stop()
        except Exception:
            pass
        self.root.destroy()

    def _position_bottom_right(self):
        self.root.update_idletasks()
        win_w = self.root.winfo_width() or 520
        win_h = self.root.winfo_height() or 460
        margin = 20
        geo = self._primary_monitor_geometry()
        if geo:
            mon_x, mon_y, mon_w, mon_h = geo
            x = max(0, mon_x + mon_w - win_w - margin)
            y = max(0, mon_y + mon_h - win_h - margin)
        else:
            x = max(0, self.root.winfo_screenwidth() - win_w - margin)
            y = max(0, self.root.winfo_screenheight() - win_h - margin)
        self.root.geometry(f"+{x}+{y}")

    def _primary_monitor_geometry(self):
        """Return (x, y, w, h) of the primary monitor via xrandr, or None."""
        try:
            out = subprocess.run(["xrandr", "--current"],
                                 capture_output=True, text=True, timeout=5).stdout
            for line in out.splitlines():
                if "primary" not in line or " connected " not in line:
                    continue
                m = re.search(r'(\d+)x(\d+)\+(\d+)\+(\d+)', line)
                if m:
                    return int(m.group(3)), int(m.group(4)), int(m.group(1)), int(m.group(2))
        except Exception:
            pass
        return None

    # ── Hotkey ──

    def _hotkey_listener(self):
        self._hotkey_stop = threading.Event()
        threading.Thread(
            target=_evdev_listen,
            args=(self._toggle_window, self._hotkey_stop),
            daemon=True,
        ).start()
        self.root.after(0, lambda: self._status("Ready. Press Ctrl+Shift+E to toggle the window."))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TextTool()
    app.run()