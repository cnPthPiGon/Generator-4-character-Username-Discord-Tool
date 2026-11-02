import os
import sys
import time
import random
import string
import datetime

import pyautogui
import numpy as np
import tkinter as tk
import keyboard
import requests

try:
    import win32gui
    import win32con
    _WIN = True
except ImportError:
    _WIN = False

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

HOOK = "UR WEBHOOK HERE"

ASCII_HEAD = r"""
  __  __           _        ____           _____ _               _                _____  _               ___  _____            ___    _____        __     __         _         _          
 |  \/  |         | |      |  _ \         / ____| |             (_)       ___    |  __ \(_)             / _ \| ____|          |__ \  |_   _|       \ \   / /        | |       | |         
 | \  / | __ _  __| | ___  | |_) |_   _  | |    | |__ __  ___ __ _ ___   ( _ )   | |__) |___  _____ _ _| (_) | |__ ________  __  ) |   | |  _ __    \ \_/ /__  _   _| |_ _   _| |__   ___ 
 | |\/| |/ _` |/ _` |/ _ \ |  _ <| | | | | |    | '_ \\ \/ / '__| / __|  / _ \/\ |  _  /| \ \/ / _ \ '__\__, |___ \______\ \/ / / /    | | | '_ \    \   / _ \| | | | __| | | | '_ \ / _ \
 | |  | | (_| | (_| |  __/ | |_) | |_| | | |____| | | |>  <| |  | \__ \ | (_>  < | | \ \| |>  <  __/ |    / / ___) |      >  < / /_   _| |_| | | |    | | (_) | |_| | |_| |_| | |_) |  __/
 |_|  |_|\__,_|\__,_|\___| |____/ \__, |  \_____|_| |_/_/\_\_|  |_|___/  \___/\/ |_|  \_\_/_/\_\___|_|   /_/ |____/      /_/\_\____| |_____|_| |_|    |_|\___/ \__,_|\__|\__,_|_.__/ \___|
 | |  | |                          __/ |            / ____| |             | |             |  __ \(_)                     | |                                                              
 | |  | |___  ___ _ __ _ __   __ _|___/ ___   ___  | |    | |__   ___  ___| | _____ _ __  | |  | |_ ___  ___ ___  _ __ __| |                                                              
 | |  | / __|/ _ \ '__| '_ \ / _` | '_ ` _ \ / _ \ | |    | '_ \ / _ \/ __| |/ / _ \ '__| | |  | | / __|/ __/ _ \| '__/ _` |                                                              
 | |__| \__ \  __/ |  | | | | (_| | | | | | |  __/ | |____| | | |  __/ (__|   <  __/ |    | |__| | \__ \ (_| (_) | | | (_| |                                                              
  \____/|___/\___|_|  |_| |_|\__,_|_| |_| |_|\___|  \_____|_| |_|\___|\___|_|\_\___|_|    |_____/|_|___/\___\___/|_|  \__,_|                                                              
"""

SCREEN_MAP = {
    "2560x1440": (410, 45, 0.479),
    "1920x1440": (410, 45, 0.479),
    "1920x1200": (410, 45, 0.479),
    "1920x1080": (410, 45, 0.479),
}

PALETTE_FAIL = [
    (237, 66, 69),
    (229, 57, 53),
    (170, 88, 87),
    (106, 58, 58),
    (235, 117, 113),
    (151, 79, 78),
    (188, 97, 95),
    (255, 99, 71),
    (205, 92, 92),
    (220, 20, 60),
]

PALETTE_PASS = [
    (87, 242, 135),
    (40, 92, 54),
    (57, 150, 81),
    (51, 126, 70),
    (46, 204, 113),
    (80, 220, 100),
    (118, 172, 63),
    (47, 114, 65),
    (49, 122, 69),
    (59, 157, 84),
    (57, 151, 81),
    (58, 155, 83),
    (53, 140, 76),
    (60, 179, 113),
    (46, 139, 87),
    (152, 251, 152),
]

PALETTE_NEUTRAL = [
    (88, 101, 242),
    (78, 93, 148),
    (60, 60, 65),
    (53, 54, 56),
    (41, 28, 54),
    (72, 73, 75),
    (56, 57, 60),
]

FRAME_TINT = "#6A0DAD"
TICK_MIN = 1.4
TICK_MAX = 2.5
DRIFT_EVERY = 28
DRIFT_MIN = 5.0
DRIFT_MAX = 16.0
SAMPLES = 5
SAMPLE_GAP = 0.07
TYPE_MIN = 0.04
TYPE_MAX = 0.13

ANSI_RED = "\033[31m"
ANSI_GRN = "\033[32m"
ANSI_YLW = "\033[33m"
ANSI_CYN = "\033[36m"
ANSI_MAG = "\033[35m"
ANSI_DIM = "\033[90m"
ANSI_RST = "\033[0m"

_stop = False


def _cls():
    os.system("cls" if os.name == "nt" else "clear")


def _center(text, width=80):
    return "\n".join(line.center(width) for line in text.split("\n"))


def _dist(a, b):
    try:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 * 1.2 + (a[2] - b[2]) ** 2 * 0.8) ** 0.5
    except OverflowError:
        return 999


def _bounds():
    w, h = pyautogui.size()
    tag = f"{w}x{h}"
    bw, bh, ratio = SCREEN_MAP.get(tag, SCREEN_MAP["1920x1080"])
    bx = (w - bw) // 2
    by = int(h * ratio)
    return bx, by, bw, bh


def _jitter(base, span=0.35):
    time.sleep(max(0.04, base + random.uniform(-span, span)))


def _human_type(text):
    for ch in text:
        pyautogui.write(ch)
        d = random.uniform(TYPE_MIN, TYPE_MAX)
        if random.random() < 0.08:
            d += random.uniform(0.14, 0.32)
        time.sleep(d)


def _nudge_cursor():
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x + random.randint(-3, 3), y + random.randint(-2, 2),
                         duration=random.uniform(0.04, 0.13))
    except Exception:
        pass


def _sample_rgb(x, y, w, h):
    img = pyautogui.screenshot(region=(x, y, w, h))
    arr = np.array(img)
    avg = np.mean(arr, axis=(0, 1))
    return tuple(int(v) for v in avg)


def _classify_pixel(px):
    for ref in PALETTE_PASS[:6]:
        if _dist(px, ref) < 32:
            return "PASS"
    for ref in PALETTE_FAIL[:6]:
        if _dist(px, ref) < 35:
            return "FAIL"
    return None


def scan_region(box):
    x, y, w, h = box
    try:
        img = pyautogui.screenshot(region=(x, y, w, h))
        arr = np.array(img)
        hit_pass = False
        hit_fail = False
        for row in range(arr.shape[0]):
            for col in range(arr.shape[1]):
                tag = _classify_pixel(tuple(arr[row, col]))
                if tag == "PASS":
                    hit_pass = True
                elif tag == "FAIL":
                    hit_fail = True
                if hit_pass and hit_fail:
                    break
            if hit_pass and hit_fail:
                break
        if hit_pass and not hit_fail:
            return "PASS"
        if hit_fail and not hit_pass:
            return "FAIL"
    except Exception:
        pass

    avg = _sample_rgb(x, y, w, h)
    for ref in PALETTE_PASS[:3]:
        if _dist(avg, ref) < 40:
            return "PASS"
    for ref in PALETTE_FAIL[:3]:
        if _dist(avg, ref) < 35:
            return "FAIL"
    for ref in PALETTE_NEUTRAL:
        if _dist(avg, ref) < 40:
            return "NEUTRAL"
    for ref in PALETTE_PASS:
        if _dist(avg, ref) < 45:
            return "PASS"
    for ref in PALETTE_FAIL:
        if _dist(avg, ref) < 45:
            return "FAIL"
    return "UNKNOWN"


def _force_on_top(handles):
    if not _WIN:
        return
    try:
        for h in handles:
            if hasattr(h, "winfo_id"):
                hwnd = win32gui.GetParent(h.winfo_id())
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
                )
    except Exception:
        pass


class _Frame:
    def __init__(self, x, y, w, h, thick=4):
        self.x, self.y, self.w, self.h, self.t = x, y, w, h, thick
        self.handles = []
        self._build()

    def _build(self):
        root = tk.Tk()
        root.overrideredirect(True)
        root.configure(background=FRAME_TINT)
        root.geometry(f"{self.w}x{self.t}+{self.x}+{self.y}")
        root.attributes("-topmost", True)
        root.lift()
        self.handles.append(root)

        for name, geom in (
            ("b", f"{self.w}x{self.t}+{self.x}+{self.y + self.h - self.t}"),
            ("l", f"{self.t}x{self.h}+{self.x}+{self.y}"),
            ("r", f"{self.t}x{self.h}+{self.x + self.w - self.t}+{self.y}"),
        ):
            sub = tk.Toplevel()
            sub.overrideredirect(True)
            sub.configure(background=FRAME_TINT)
            sub.geometry(geom)
            sub.attributes("-topmost", True)
            sub.lift()
            self.handles.append(sub)

        for w in self.handles:
            w.update()
        _force_on_top(self.handles)

    def lift(self):
        for w in self.handles:
            try:
                w.attributes("-topmost", True)
                w.lift()
                w.update()
            except Exception:
                pass
        _force_on_top(self.handles)

    def close(self):
        for w in self.handles:
            try:
                w.destroy()
            except Exception:
                pass
        self.handles = []


def build_candidate():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=4))


def post_result(name):
    ts = int(datetime.datetime.now().timestamp())
    pal = [5793266, 5763719, 3066993, 2067276, 3447003]
    payload = {
        "content": f"**Available:** `{name}`",
        "username": "4char",
        "embeds": [{
            "title": "Username available",
            "description": f"```{name}```",
            "color": random.choice(pal),
            "fields": [
                {"name": "Length", "value": "4 characters", "inline": True},
                {"name": "Found", "value": f"<t:{ts}:R>", "inline": True},
            ],
            "timestamp": datetime.datetime.now().isoformat(),
        }],
    }
    try:
        r = requests.post(HOOK, json=payload, timeout=10)
        if r.status_code == 204:
            print(f"{ANSI_GRN}[hook] sent{ANSI_RST}")
        else:
            print(f"{ANSI_RED}[hook] http {r.status_code}{ANSI_RST}")
    except Exception as e:
        print(f"{ANSI_RED}[hook] {e}{ANSI_RST}")


def _read_status(box):
    hits = []
    for _ in range(SAMPLES):
        hits.append(scan_region(box))
        _jitter(SAMPLE_GAP, 0.02)
    if "PASS" in hits:
        return "PASS"
    if hits.count("FAIL") >= 2:
        return "FAIL"
    from collections import Counter
    return Counter(hits).most_common(1)[0][0]


def _wait_cycle(state):
    state["n"] += 1
    if state["n"] >= DRIFT_EVERY:
        state["n"] = 0
        pause = random.uniform(DRIFT_MIN, DRIFT_MAX)
        print(f"{ANSI_DIM}[rest] {pause:.1f}s{ANSI_RST}")
        time.sleep(pause)
        return
    time.sleep(random.uniform(TICK_MIN, TICK_MAX))


def _interrupt(_):
    global _stop
    _stop = True


def main():
    global _stop
    _stop = False

    if os.name == "nt":
        os.system("color")

    try:
        term_w = os.get_terminal_size().columns
    except Exception:
        term_w = 80

    _cls()
    print(f"{ANSI_RED}{_center(ASCII_HEAD, term_w)}{ANSI_RST}")
    print(f"{ANSI_CYN}{'=' * term_w}{ANSI_RST}")
    print(f"{ANSI_YLW}interval : {TICK_MIN}-{TICK_MAX}s{ANSI_RST}")
    print(f"{ANSI_YLW}rest     : every {DRIFT_EVERY} checks{ANSI_RST}")
    print(f"{ANSI_YLW}stop     : ESC{ANSI_RST}")
    print(f"{ANSI_CYN}{'=' * term_w}{ANSI_RST}\n")

    region = _bounds()
    print(f"{ANSI_DIM}[init] region={region}{ANSI_RST}")

    frame = _Frame(*region)
    keyboard.on_press_key("esc", _interrupt)

    state = {"n": 0}
    tries = 0

    try:
        while not _stop:
            name = build_candidate()

            frame.lift()

            if random.random() < 0.16:
                _nudge_cursor()

            pyautogui.hotkey("ctrl", "a")
            _jitter(0.11, 0.04)
            pyautogui.press("delete")
            _jitter(0.11, 0.04)

            frame.lift()
            _human_type(name)
            frame.lift()
            _jitter(0.43, 0.14)

            status = _read_status(region)

            if status == "PASS":
                print(f"{ANSI_GRN}{name} : false{ANSI_RST}")
                print(f"\n{ANSI_GRN}{'=' * term_w}{ANSI_RST}")
                print(f"{ANSI_GRN}  FOUND : {name}{ANSI_RST}")
                print(f"{ANSI_GRN}{'=' * term_w}{ANSI_RST}\n")
                post_result(name)
                frame.close()
                keyboard.unhook_all()
                print(f"{ANSI_GRN}Press any key to exit.{ANSI_RST}")
                keyboard.read_key()
                sys.exit(0)

            elif status == "FAIL":
                print(f"{ANSI_RED}{name} : true{ANSI_RST}")
            else:
                print(f"{ANSI_YLW}{name} : {status.lower()}{ANSI_RST}")

            tries += 1
            _wait_cycle(state)

    except KeyboardInterrupt:
        print(f"\n{ANSI_RED}stopped{ANSI_RST}")
    except SystemExit:
        raise
    finally:
        try:
            frame.close()
        except Exception:
            pass
        try:
            keyboard.unhook_all()
        except Exception:
            pass


if __name__ == "__main__":
    if _WIN:
        try:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
            )
        except Exception:
            pass

    print(f"{ANSI_CYN}Click the Discord username field, then press any key.{ANSI_RST}")
    keyboard.read_key()

    main()
