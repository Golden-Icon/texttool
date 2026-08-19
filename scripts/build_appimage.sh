#!/bin/bash
# Build TextTool as a portable Linux AppImage.
# Prereqs: venv with pyinstaller (see README), appimagetool, and the
# libappindicator-gtk3 package for the tray typelib.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$HERE/.venv/bin/python}"
APPIMAGE_TOOL="${APPIMAGE_TOOL:-appimagetool}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "[1/4] Building with PyInstaller..."
"$PYTHON" -m PyInstaller --clean --noconfirm "$HERE/texttool.spec"

echo "[2/4] Assembling AppDir..."
mkdir -p "$WORK/AppDir/usr/lib/texttool" \
         "$WORK/AppDir/usr/share/icons/hicolor/256x256/apps"
cp -r "$HERE/dist/texttool/." "$WORK/AppDir/usr/lib/texttool/"
cat > "$WORK/AppDir/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/lib/texttool/texttool" "$@"
EOF
chmod +x "$WORK/AppDir/AppRun"
cp "$HERE/assets/texttool.png" "$WORK/AppDir/texttool.png"
cp "$HERE/assets/texttool.png" "$WORK/AppDir/usr/share/icons/hicolor/256x256/apps/texttool.png"
cat > "$WORK/AppDir/texttool.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=TextTool
Comment=Unicode text transformation tool
Exec=texttool
Icon=texttool
Terminal=false
Categories=Utility;
StartupNotify=false
EOF

echo "[3/4] Packaging AppImage..."
VERSION="$("$PYTHON" -c 'import sys; sys.path.insert(0,"'"$HERE"'"); import texttool; print(texttool.VERSION)')"
"$APPIMAGE_TOOL" "$WORK/AppDir" "TextTool-${VERSION}-x86_64.AppImage"

echo "[4/4] Done: TextTool-${VERSION}-x86_64.AppImage"