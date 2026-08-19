# Cross-platform platform helpers for TextTool.
#
# Linux uses raw evdev reads (/dev/input) for the global hotkey, which works
# unprivileged when the user is in the input group. It also shells out to
# xrandr to find the primary monitor geometry.
#
# Windows uses the built-in RegisterHotKey API (via ctypes) for the hotkey and
# the Win32 monitor APIs for primary-monitor geometry. No third-party deps.

import os
import re
import select
import struct
import subprocess
import sys

_IS_WINDOWS = sys.platform.startswith("win")

# linux/input-event-codes.h
KEY_LEFTCTRL = 29
KEY_RIGHTCTRL = 97
KEY_LEFTSHIFT = 42
KEY_RIGHTSHIFT = 54
KEY_E = 18
EV_KEY = 1

# Windows RegisterHotKey modifier flags (winuser.h)
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000

if _IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    _user32 = ctypes.windll.user32
    _user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
    _user32.RegisterHotKey.restype = wintypes.BOOL
    _user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
    _user32.UnregisterHotKey.restype = wintypes.BOOL

    WM_HOTKEY = 0x0312

    def _kbd_event_paths():
        return []

    def _evdev_listen(callback, stop_event):
        # Not used on Windows; kept for interface parity.
        return

    def hotkey_listen(callback, stop_event):
        """Windows RegisterHotKey listener running in the current thread."""
        hotkey_id = 0x4242
        if not _user32.RegisterHotKey(None, hotkey_id, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, ord('E')):
            return

        msg = wintypes.MSG()
        try:
            while not stop_event.is_set():
                res = _user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res == 0:
                    break
                if res == -1:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == hotkey_id:
                    callback()
        finally:
            _user32.UnregisterHotKey(None, hotkey_id)

    def primary_monitor():
        """Return (x, y, w, h) of the primary monitor via Win32 APIs."""
        try:
            # Primary monitor work area (excludes taskbar) in screen coords.
            rect = wintypes.RECT()
            if _user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):  # SPI_GETWORKAREA
                x, y = rect.left, rect.top
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                return x, y, w, h
        except Exception:
            pass
        return None

else:

    def _kbd_event_paths():
        """Return /dev/input/eventN paths for devices that handle keyboard input."""
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
        for path in _kbd_event_paths():
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

    def hotkey_listen(callback, stop_event):
        """Linux evdev hotkey listener running in the current thread."""
        _evdev_listen(callback, stop_event)

    def primary_monitor():
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