#!/bin/bash
# Double-click this file in Finder to launch the widget. It opens the browser
# automatically and keeps the server running in this window. Close the window
# (or Ctrl+C) to stop.

cd "$(dirname "$0")"

# Try to open the page shortly after the server starts.
(sleep 1 && open "http://127.0.0.1:8765/") &

exec /opt/homebrew/bin/python3.10 server.py
