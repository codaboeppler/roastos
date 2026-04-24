#!/bin/bash
# One-click installer for the RoastOS.
# Does everything: installs deps, starts the menu bar app, starts the web server,
# opens the dashboard, and sets up auto-start on login.

set -e

cd "$(dirname "$0")"
WIDGET_DIR="$(pwd)"
PY=/opt/homebrew/bin/python3.10

echo ""
echo "╭──────────────────────────────────────────╮"
echo "│   ◆  RoastOS — installer           │"
echo "╰──────────────────────────────────────────╯"
echo ""

if [ ! -x "$PY" ]; then
    echo "✗ python3.10 not found at $PY"
    echo "  Install it: brew install python@3.10"
    exit 1
fi
echo "✓ python3.10 present"

echo ""
echo "1/4  Installing Python dependencies (psutil, rumps)…"
"$PY" -m pip install --quiet --upgrade psutil rumps
echo "✓ deps installed"

echo ""
echo "2/4  Stopping any previous instances…"
pkill -f "menubar_popover.py"    2>/dev/null || true
pkill -f "server.py"     2>/dev/null || true
launchctl unload "$HOME/Library/LaunchAgents/com.danielboeppler.roastos.plist" 2>/dev/null || true
sleep 1
echo "✓ clean"

echo ""
echo "3/4  Installing as a login item (menu bar will start automatically)…"
mkdir -p "$HOME/Library/LaunchAgents"
PLIST="$HOME/Library/LaunchAgents/com.danielboeppler.roastos.plist"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.danielboeppler.roastos</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PY</string>
    <string>$WIDGET_DIR/menubar_popover.py</string>
  </array>
  <key>WorkingDirectory</key><string>$WIDGET_DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$WIDGET_DIR/menubar.log</string>
  <key>StandardErrorPath</key><string>$WIDGET_DIR/menubar.log</string>
</dict>
</plist>
EOF
launchctl load "$PLIST"
echo "✓ installed at $PLIST"

echo ""
echo "4/4  Starting the web dashboard (http://127.0.0.1:8765)…"
nohup "$PY" server.py > server.log 2>&1 &
disown
sleep 1
open "http://127.0.0.1:8765/"
echo "✓ dashboard open in browser"

echo ""
echo "╭──────────────────────────────────────────╮"
echo "│   ✓  All set — widget is live            │"
echo "╰──────────────────────────────────────────╯"
echo ""
echo "  Menu bar:     top-right of screen (🟢/🟡/🔴 + free RAM)"
echo "  Dashboard:    http://127.0.0.1:8765/"
echo "  Auto-start:   yes, on every login"
echo ""
echo "  To uninstall:"
echo "    launchctl unload \"$PLIST\" && rm \"$PLIST\""
echo ""
sleep 4
