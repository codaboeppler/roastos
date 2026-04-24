#!/bin/bash
# Install the widget as a macOS LaunchAgent so it starts automatically on login.
# Run this once. To uninstall later: launchctl unload ~/Library/LaunchAgents/com.danielboeppler.roastos.plist

set -e

LABEL="com.danielboeppler.roastos"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
WIDGET_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/python3.10</string>
    <string>$WIDGET_DIR/menubar.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$WIDGET_DIR</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$WIDGET_DIR/menubar.log</string>
  <key>StandardErrorPath</key>
  <string>$WIDGET_DIR/menubar.log</string>
</dict>
</plist>
EOF

# If it's already loaded, remove first so we pick up any changes cleanly.
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo "✓ Installed as LaunchAgent: $LABEL"
echo "  It will start automatically on every login."
echo "  Widget should appear in the menu bar within 2 seconds."
echo ""
echo "To uninstall later:"
echo "  launchctl unload \"$PLIST\" && rm \"$PLIST\""
sleep 3
