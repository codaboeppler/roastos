#!/bin/bash
# Double-click this to start the menu-bar widget.
# Works even if the Terminal window is closed later (nohup + disown).

cd "$(dirname "$0")"

# If it's already running, don't spawn another.
if pgrep -f "menubar.py" > /dev/null; then
    echo "Menu bar widget is already running. Look for the emoji + RAM in your top bar."
    exit 0
fi

nohup /opt/homebrew/bin/python3.10 menubar.py > menubar.log 2>&1 &
disown

echo "✓ Menu-bar widget started."
echo "  Look at the top-right of your screen for the colored dot + free RAM."
echo "  Logs: $(pwd)/menubar.log"
sleep 2
