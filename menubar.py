#!/usr/bin/env python3
"""macOS menu-bar widget: free RAM + click-to-kill top memory hogs.

Top 5 memory consumers are listed with submenus → Quit or Force Quit right from
the menu bar. Also shows free RAM, disk, swap, CPU at a glance.

Launch:
    /opt/homebrew/bin/python3.10 menubar.py
Install as login item:
    double-click install_autostart.command
"""
import functools
import os
import signal
import subprocess
import webbrowser

import psutil
import rumps


# ─── Helpers ───────────────────────────────────────────────────────────
def fmt_bytes(n):
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    val = float(n)
    while val >= 1024 and i < len(units) - 1:
        val /= 1024
        i += 1
    return f"{val:.1f} {units[i]}" if i >= 3 else f"{int(val)} {units[i]}"


def pressure_emoji(pct_used):
    if pct_used >= 90: return "🔴"
    if pct_used >= 75: return "🟡"
    return "🟢"


# Processes we NEVER want the user to accidentally kill — they crash macOS or the widget.
PROTECTED = {
    "kernel_task", "launchd", "WindowServer", "loginwindow", "mds", "mds_stores",
    "coreaudiod", "cfprefsd", "Dock", "Finder", "SystemUIServer", "ControlCenter",
    "Python",  # that's us
}


def kill_pid(pid, force=False):
    """Send SIGTERM (graceful) or SIGKILL (force). Returns (ok, message)."""
    try:
        sig = signal.SIGKILL if force else signal.SIGTERM
        os.kill(pid, sig)
        return True, "sent"
    except PermissionError:
        return False, "Permission denied (system process — macOS won't let you kill it)."
    except ProcessLookupError:
        return False, "Process already gone."
    except Exception as e:
        return False, str(e)


# ─── App ───────────────────────────────────────────────────────────────
class SystemWidget(rumps.App):
    def __init__(self):
        super().__init__("…", quit_button=None)

        # Static menu items — titles mutate in place each tick.
        self.ram_item  = rumps.MenuItem("RAM: …")
        self.disk_item = rumps.MenuItem("Disk: …")
        self.swap_item = rumps.MenuItem("Swap: …")
        self.cpu_item  = rumps.MenuItem("CPU: …")
        self.top_header = rumps.MenuItem("— Top memory consumers (click to quit) —")

        # 5 top-consumer rows, each with a Quit/Force Quit submenu.
        # We create the submenu items once and swap their callbacks per tick so
        # the PID captured by the lambda matches the process currently displayed.
        self.top_rows = []
        for _ in range(5):
            row = rumps.MenuItem("—")
            quit_item       = rumps.MenuItem("Quit")
            forcequit_item  = rumps.MenuItem("Force Quit")
            row.add(quit_item)
            row.add(forcequit_item)
            self.top_rows.append({"row": row, "quit": quit_item, "force": forcequit_item, "pid": None})

        self.menu = [
            self.ram_item,
            self.disk_item,
            self.swap_item,
            self.cpu_item,
            None,
            self.top_header,
            *[r["row"] for r in self.top_rows],
            None,
            rumps.MenuItem("Open web dashboard…", callback=self.open_web),
            rumps.MenuItem("Open Activity Monitor", callback=self.open_activity_monitor),
            None,
            rumps.MenuItem("Quit widget", callback=rumps.quit_application),
        ]

        self.tick(None)  # initial paint

    # ── Update loop ────────────────────────────────────────────────
    @rumps.timer(2)
    def tick(self, _):
        try:
            mem  = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            swap = psutil.swap_memory()
            cpu  = psutil.cpu_percent(interval=None)

            free_gb = mem.available / (1024 ** 3)
            self.title = f"{pressure_emoji(mem.percent)} {free_gb:.1f}G"

            self.ram_item.title  = (f"RAM: {fmt_bytes(mem.available)} free  ·  "
                                    f"{mem.percent:.0f}% used of {fmt_bytes(mem.total)}")
            self.disk_item.title = f"Disk: {fmt_bytes(disk.free)} free  ·  {disk.percent:.0f}% used"
            self.swap_item.title = (f"Swap: {fmt_bytes(swap.used)} used"
                                    + (f"  ·  {swap.percent:.0f}%" if swap.total else "  ·  inactive"))
            self.cpu_item.title  = f"CPU: {cpu:.0f}%"

            self._refresh_top_consumers()
        except Exception as e:
            self.title = "⚠ err"
            self.ram_item.title = f"error: {e}"

    def _refresh_top_consumers(self):
        procs = []
        for p in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                if p.info["memory_info"] is None: continue
                procs.append((p.info["memory_info"].rss, p.info["name"] or "?", p.info["pid"]))
            except Exception:
                pass
        procs.sort(reverse=True)

        for i, slot in enumerate(self.top_rows):
            if i < len(procs):
                rss, name, pid = procs[i]
                display = name if len(name) <= 40 else name[:37] + "…"
                slot["row"].title = f"{display}  ·  {fmt_bytes(rss)}"
                slot["pid"] = pid
                # Bind new callbacks each tick so the closed-over pid always matches the
                # current slot. Using functools.partial avoids Python's "all lambdas see
                # the last value" closure gotcha.
                slot["quit"].set_callback(
                    functools.partial(self._on_quit, pid=pid, name=name, force=False))
                slot["force"].set_callback(
                    functools.partial(self._on_quit, pid=pid, name=name, force=True))
            else:
                slot["row"].title = ""
                slot["pid"] = None
                slot["quit"].set_callback(None)
                slot["force"].set_callback(None)

    # ── Actions ────────────────────────────────────────────────────
    def _on_quit(self, _, pid, name, force):
        if name in PROTECTED:
            rumps.alert(
                title="Protected process",
                message=f"{name} is a system process. macOS won't let you kill it safely.",
                ok="OK")
            return

        verb = "Force Quit" if force else "Quit"
        resp = rumps.alert(
            title=f"{verb} {name}?",
            message=f"PID {pid}  ·  This will close the app immediately"
                    + (" without letting it save." if force else " (it can save if it wants)."),
            ok=verb, cancel="Cancel")
        if resp != 1:
            return

        ok, msg = kill_pid(pid, force=force)
        if not ok:
            rumps.alert(title="Could not kill", message=msg, ok="OK")

    def open_web(self, _):
        webbrowser.open("http://127.0.0.1:8765/")

    def open_activity_monitor(self, _):
        subprocess.Popen(["open", "-a", "Activity Monitor"])


if __name__ == "__main__":
    SystemWidget().run()
