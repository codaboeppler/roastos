#!/usr/bin/env python3
"""Native macOS menu-bar app with a beautiful popover UI.

Drops rumps' text-only menu for a proper NSPopover + WKWebView — the same pattern
1Password, Fantastical, Bartender use. Click the menu-bar icon → rich HTML panel
unfolds with an arrow pointing at the icon, closes on outside click.

Title shows color-coded free RAM (🟢/🟡/🔴 + GB). Popover loads popover.html from
the local server (http://127.0.0.1:8765/) so any CSS / JS change updates instantly.

Launch:
    /opt/homebrew/bin/python3.10 menubar_popover.py
"""
import objc
from Foundation   import NSObject, NSURL, NSURLRequest, NSMakeRect, NSTimer, NSRunLoop
from AppKit       import (
    NSApplication, NSApp, NSApplicationActivationPolicyAccessory,
    NSStatusBar, NSRectEdgeMinY,
    NSPopover, NSPopoverBehaviorTransient,
    NSViewController, NSView,
    NSFont,
)
from WebKit       import WKWebView, WKWebViewConfiguration

import psutil


# ── tunables ─────────────────────────────────────────────────────────
POPOVER_WIDTH  = 380
POPOVER_HEIGHT = 620  # roomier so the settings drawer fits without scrolling when possible
POPOVER_URL    = "http://127.0.0.1:8765/popover.html"
TITLE_REFRESH_S = 2.0


def fmt_gb(b):
    return f"{b / (1024 ** 3):.1f}"


def pressure_emoji(pct_used):
    if pct_used >= 90: return "🔴"
    if pct_used >= 75: return "🟡"
    return "🟢"


# ── AppKit delegate ──────────────────────────────────────────────────
class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, _):
        # Accessory = menu-bar-only, no Dock icon, no main window.
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        self._build_status_item()
        self._build_popover()
        self._start_title_timer()

    # ── status bar item (the icon at top right) ──────────────────
    def _build_status_item(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)
        btn = self.status_item.button()
        btn.setTitle_("⋯")
        btn.setFont_(NSFont.menuBarFontOfSize_(0))
        btn.setTarget_(self)
        btn.setAction_(objc.selector(self.togglePopover_, signature=b"v@:@"))

    # ── popover (the rich UI that unfolds on click) ──────────────
    def _build_popover(self):
        self.popover = NSPopover.alloc().init()
        self.popover.setContentSize_((POPOVER_WIDTH, POPOVER_HEIGHT))
        self.popover.setBehavior_(NSPopoverBehaviorTransient)  # auto-close on outside click
        self.popover.setAnimates_(True)

        vc = NSViewController.alloc().init()
        container = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, POPOVER_WIDTH, POPOVER_HEIGHT))

        config = WKWebViewConfiguration.alloc().init()
        # Disable the right-click context menu and text-selection cursor — more app-like.
        config.preferences().setJavaScriptEnabled_(True)
        web = WKWebView.alloc().initWithFrame_configuration_(
            NSMakeRect(0, 0, POPOVER_WIDTH, POPOVER_HEIGHT), config)
        web.setAutoresizingMask_(0x12)  # width+height flexible

        req = NSURLRequest.requestWithURL_(NSURL.URLWithString_(POPOVER_URL))
        web.loadRequest_(req)
        container.addSubview_(web)
        vc.setView_(container)

        self.popover.setContentViewController_(vc)
        self.web = web  # retain

    # ── title updater (free RAM at a glance) ─────────────────────
    def _start_title_timer(self):
        self._refresh_title()
        timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            TITLE_REFRESH_S, self, objc.selector(self.refreshTitle_, signature=b"v@:@"),
            None, True)
        NSRunLoop.currentRunLoop().addTimer_forMode_(timer, "NSDefaultRunLoopMode")

    def refreshTitle_(self, _timer):
        self._refresh_title()

    def _refresh_title(self):
        try:
            mem = psutil.virtual_memory()
            title = f"{pressure_emoji(mem.percent)} {fmt_gb(mem.available)}G"
        except Exception:
            title = "⚠"
        self.status_item.button().setTitle_(title)

    # ── click handler ────────────────────────────────────────────
    def togglePopover_(self, sender):
        button = self.status_item.button()
        if self.popover.isShown():
            self.popover.performClose_(sender)
        else:
            # Reload on open so any CSS / JS tweaks show immediately.
            self.web.reload()
            self.popover.showRelativeToRect_ofView_preferredEdge_(
                button.bounds(), button, NSRectEdgeMinY)
            NSApp.activateIgnoringOtherApps_(True)


# ── bootstrap ────────────────────────────────────────────────────────
def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


if __name__ == "__main__":
    main()
