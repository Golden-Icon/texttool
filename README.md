# TextTool

A desktop Unicode text transformer. Paste any text, then apply styles (bold, italic, script, fraktur, small caps, superscript, etc.), case conversions, text operations, or encodings. Results render in a live preview and can be copied to the clipboard.

## Features

- **Input → Preview** two-pane design: your source text is never modified.
- **Style transforms**: Small Caps, Superscript, Subscript, Bold, Italic, Script, Fraktur, Double-Struck, Monospace, Sans-Serif.
- **Case transforms**: UPPER, lower, Title, aLtErNaTe, iNVERSE.
- **Text ops**: Reverse, Reverse Lines, Sort Lines, Dedup, Number Lines, Trim Spaces, Remove Whitespace, Spaces→Newlines, Newlines→Spaces.
- **Encodings**: Base64 encode/decode, URL encode/decode.
- **System tray**: closes to tray instead of quitting; tray menu has Show/Quit.
- **Global hotkey**: **Ctrl+Shift+E** toggles the window (show/hide), positioned at the bottom-right of the primary monitor.

## Requirements (runtime)

- Python 3.10+ with tkinter (system Tcl/Tk 8.6 recommended)
- Linux: `pystray` (with GTK3 + libayatana-appindicator for the tray), `Pillow`, `pyperclip`, `wl-clipboard` (optional), and the **Noto Sans Math** font (falls back to a bundled copy if absent)
- Windows: `pystray`, `Pillow`, `pyperclip`

## Running from source

```bash
python texttool.py
```

On Linux, your user needs read access to `/dev/input` (membership in the `input` group) for the global hotkey.

## Building

### Linux AppImage

Requires Python with the app dependencies installed, plus `pyinstaller` and `pyinstaller-hooks-contrib` (for the GTK/GI typelib hook used by the system tray), and `appimagetool`.

```bash
scripts/build_appimage.sh
```

This runs PyInstaller (`texttool.spec`) and wraps the result in `TextTool-x86_64.AppImage`.

### Windows

Build on a Windows machine (or via GitHub Actions — see `.github/workflows/`). Uses the same PyInstaller spec plus NSIS for an installer.

## License

TBD.