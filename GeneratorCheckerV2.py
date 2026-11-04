# Made By Chxris & — Rixer95-x2 In Youtube
# 4 character checker discord W?

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

from PIL import Image, ImageOps, ImageFilter, ImageEnhance

try:
    import pytesseract
    _OCR = True
except ImportError:
    _OCR = False

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

HOOK = "your-webhook"

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

PALETTE_PASS = [
    (87, 242, 135), (40, 92, 54), (57, 150, 81), (51, 126, 70),
    (46, 204, 113), (80, 220, 100), (118, 172, 63), (47, 114, 65),
    (49, 122, 69), (59, 157, 84), (57, 151, 81), (58, 155, 83),
    (53, 140, 76), (60, 179, 113), (46, 139, 87), (152, 251, 152),
]

PALETTE_FAIL = [
    (237, 66, 69), (229, 57, 53), (170, 88, 87), (106, 58, 58),
    (235, 117, 113), (151, 79, 78), (188, 97, 95), (255, 99, 71),
    (205, 92, 92), (220, 20, 60),
]

PALETTE_NEUTRAL = [
    (88, 101, 242), (78, 93, 148), (60, 60, 65), (53, 54, 56),
    (41, 28, 54), (72, 73, 75), (56, 57, 60),
]

PASS_WORDS = [
    "disponible", "available", "verfügbar", "verfugbar", "verfuegbar",
    "disponibile", "disponível", "disponivel", "beschikbaar", "dostępna",
    "dostępny", "可用", "使用可能", "사용 가능", "사용가능", "frei", "libre",
    "vacant", "offen", "parfait", "perfect", "perfekt", "dispo", "usable",
    "usable", "premier", "arrive",
]

FAIL_WORDS = [
    "pas disponible", "not available", "unavailable", "nicht verfügbar",
    "nicht verfugbar", "nicht verfuegbar", "non disponibile", "indisponível",
    "indisponivel", "niet beschikbaar", "niedostępna", "不可用", "使用できません",
    "사용할 수 없", "pris", "taken", "belegt", "occupé", "occupe", "occupato",
    "ocupado", "bezet", "zajęta", "zajeta", "essaie", "try", "no disponible",
    "non disponible", "already taken", "déjà pris", "deja pris",
]

PLACEHOLDER_WORDS = [
    "merci de n'utiliser", "merci de n utiliser", "only use numbers",
    "nur zahlen", "solo numeros", "só números", "solo números",
    "alleen cijfers", "tylko cyfry", "数字のみ", "숫자만", "只能使用",
    "underscores", "periods", "tirets bas", "points", "chiffres",
    "letters", "lettres", "buchstaben", "letras", "lettere",
]

TICK_MIN = 1.4
TICK_MAX = 2.5
DRIFT_EVERY = 28
DRIFT_MIN = 5.0
DRIFT_MAX = 16.0
TYPE_MIN = 0.04
TYPE_MAX = 0.13
SAMPLES = 3
SAMPLE_GAP = 0.09

ANSI_RED = "\033[31m"
ANSI_GRN = "\033[32m"
ANSI_YLW = "\033[33m"
ANSI_CYN = "\033[36m"
ANSI_DIM = "\033[90m"
ANSI_RST = "\033[0m"

_stop = False
_region = None
_OCR_LANGS = "eng+fra+deu+spa+ita+por+nld+pol"


def _dist(a, b):
    try:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 * 1.2 + (a[2] - b[2]) ** 2 * 0.8) ** 0.5
    except OverflowError:
        return 999


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
        pyautogui.moveTo(
            x + random.randint(-3, 3),
            y + random.randint(-2, 2),
            duration=random.uniform(0.04, 0.13)
        )
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


def _scan_colors(box):
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


def _prep_images(box):
    x, y, w, h = box
    img = pyautogui.screenshot(region=(x, y, w, h))
    variants = []

    for scale in (4, 6):
        for thresh in (80, 100, 120, 140, 160):
            for invert in (True, False):
                try:
                    base = img.convert("L")
                    base = base.resize((w * scale, h * scale), Image.LANCZOS)
                    base = ImageEnhance.Contrast(base).enhance(1.5)
                    if invert:
                        base = ImageOps.invert(base)
                    base = base.point(lambda p: 255 if p > thresh else 0, "1")
                    variants.append(base)
                except Exception:
                    pass
    return variants


def _read_variant(img):
    for psm in (6, 7, 8, 11, 13):
        try:
            txt = pytesseract.image_to_string(
                img, lang=_OCR_LANGS, config=f"--psm {psm}"
            )
            txt = txt.strip()
            if len(txt) >= 3:
                return txt
        except Exception:
            continue
    return ""


def _scan_text(box):
    if not _OCR:
        return "UNKNOWN", ""
    try:
        best_text = ""
        for variant in _prep_images(box):
            txt = _read_variant(variant)
            if len(txt) > len(best_text):
                best_text = txt
            if len(best_text) >= 20:
                break

        text = best_text.lower().replace("\n", " ").replace("  ", " ").strip()
        if not text or len(text) < 3:
            return "UNKNOWN", text

        has_fail = any(fw in text for fw in FAIL_WORDS)
        has_pass = any(pw in text for pw in PASS_WORDS)
        has_placeholder = any(ph in text for ph in PLACEHOLDER_WORDS)

        if has_fail:
            return "FAIL", text
        if has_pass:
            return "PASS", text
        if has_placeholder:
            return "PLACEHOLDER", text
        return "UNKNOWN", text
    except Exception as e:
        return "UNKNOWN", f"err:{e}"


def _read_status(box):
    results = []
    for _ in range(SAMPLES):
        status, text = _scan_text(box)
        results.append((status, text))
        _jitter(SAMPLE_GAP, 0.03)

    statuses = [r[0] for r in results]

    if "FAIL" in statuses:
        return "FAIL"
    if "PASS" in statuses:
        return "PASS"
    if statuses.count("PLACEHOLDER") >= 2:
        return "RATE_LIMIT"

    color = _scan_colors(box)
    if color == "FAIL":
        return "FAIL"
    if color == "PASS":
        return "PASS"

    return "UNKNOWN"


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


class RegionPicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Place on the Discord message")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#8A2BE2")
        self.root.geometry("400x18+200+120")
        self.root.resizable(True, True)
        self.root.attributes("-alpha", 0.75)
        self.root.bind("<Return>", self._confirm)
        self.root.bind("<Escape>", self._cancel)

        self.canvas = tk.Canvas(
            self.root, bg="#8A2BE2", highlightthickness=0, cursor="fleur"
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_text(
            200, 9,
            text="MOVE  •  ENTER = OK  •  ESC = CANCEL",
            fill="white",
            font=("Arial", 6, "bold")
        )
        self.canvas.bind("<Button-1>", self._start_move)
        self.canvas.bind("<B1-Motion>", self._do_move)
        self.result = None

    def _start_move(self, event):
        self.root._offset_x = event.x_root - self.root.winfo_x()
        self.root._offset_y = event.y_root - self.root.winfo_y()

    def _do_move(self, event):
        nx = event.x_root - self.root._offset_x
        ny = event.y_root - self.root._offset_y
        self.root.geometry(f"+{nx}+{ny}")

    def _confirm(self, event=None):
        self.result = (
            self.root.winfo_x(), self.root.winfo_y(),
            self.root.winfo_width(), self.root.winfo_height()
        )
        self.root.destroy()

    def _cancel(self, event=None):
        self.result = None
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.result


def pick_region():
    global _region
    picker = RegionPicker()
    result = picker.run()
    if result is None:
        print(f"{ANSI_RED}[picker] cancelled{ANSI_RST}")
        sys.exit(0)
    _region = result
    print(f"{ANSI_GRN}[picker] region={result}{ANSI_RST}")


def wait_for_click():
    print(f"{ANSI_CYN}Click the Discord username field to continue...{ANSI_RST}")
    print(f"{ANSI_DIM}waiting for ENTER...{ANSI_RST}")
    keyboard.wait("enter")
    time.sleep(0.3)
    print(f"{ANSI_GRN}[detected] proceed{ANSI_RST}")


def calibrate():
    print(f"{ANSI_YLW}Calibrating...{ANSI_RST}")
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.15)
    pyautogui.press("delete")
    time.sleep(0.2)
    pyautogui.write("test1234", interval=0.05)
    time.sleep(1.0)

    status, text = _scan_text(_region)
    print(f"{ANSI_DIM}[calib] read: '{text}'{ANSI_RST}")
    print(f"{ANSI_DIM}[calib] status: {status}{ANSI_RST}")

    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("delete")
    time.sleep(0.3)

    if status == "UNKNOWN" and len(text) < 5:
        print(f"{ANSI_YLW}[calib] warning: zone reads almost nothing{ANSI_RST}")
        print(f"{ANSI_YLW}Try repositioning the selector on the message line.{ANSI_RST}")
        return False
    print(f"{ANSI_GRN}[calib] zone looks good{ANSI_RST}")
    return True


def main():
    global _stop, _region
    _stop = False

    if os.name == "nt":
        os.system("color")

    try:
        term_w = os.get_terminal_size().columns
    except Exception:
        term_w = 80

    os.system("cls" if os.name == "nt" else "clear")
    print(f"{ANSI_RED}{_center(ASCII_HEAD, term_w)}{ANSI_RST}")
    print(f"{ANSI_CYN}{'=' * term_w}{ANSI_RST}")
    print(f"{ANSI_YLW}ocr      : {'active' if _OCR else 'disabled'}{ANSI_RST}")
    print(f"{ANSI_YLW}mode     : colors + text + multi-psm + multi-threshold{ANSI_RST}")
    print(f"{ANSI_YLW}interval : {TICK_MIN}-{TICK_MAX}s{ANSI_RST}")
    print(f"{ANSI_YLW}rest     : every {DRIFT_EVERY} checks{ANSI_RST}")
    print(f"{ANSI_YLW}stop     : ESC{ANSI_RST}")
    print(f"{ANSI_CYN}{'=' * term_w}{ANSI_RST}\n")

    wait_for_click()

    print(f"{ANSI_CYN}Place the purple window on the message line, then ENTER.{ANSI_RST}")
    pick_region()

    print(f"{ANSI_CYN}Starting in 2 seconds... click Discord window to focus.{ANSI_RST}")
    time.sleep(2)

    calibrate()

    keyboard.on_press_key("esc", _interrupt)

    state = {"n": 0}
    unknown_streak = 0

    try:
        while not _stop:
            name = build_candidate()

            if random.random() < 0.16:
                _nudge_cursor()

            pyautogui.hotkey("ctrl", "a")
            _jitter(0.11, 0.04)
            pyautogui.press("delete")
            _jitter(0.11, 0.04)

            _human_type(name)
            _jitter(0.65, 0.15)

            status = _read_status(_region)

            if status == "RATE_LIMIT":
                print(f"{ANSI_RED}{name} : rate limited{ANSI_RST}")
                print(f"\n{ANSI_RED}{'=' * term_w}{ANSI_RST}")
                print(f"{ANSI_RED}  RATE LIMITED — STOPPING{ANSI_RST}")
                print(f"{ANSI_RED}{'=' * term_w}{ANSI_RST}\n")
                keyboard.unhook_all()
                print(f"{ANSI_RED}Press any key to exit.{ANSI_RST}")
                keyboard.read_key()
                sys.exit(1)

            elif status == "PASS":
                print(f"{ANSI_GRN}{name} : false{ANSI_RST}")
                print(f"\n{ANSI_GRN}{'=' * term_w}{ANSI_RST}")
                print(f"{ANSI_GRN}  FOUND : {name}{ANSI_RST}")
                print(f"{ANSI_GRN}{'=' * term_w}{ANSI_RST}\n")
                post_result(name)
                keyboard.unhook_all()
                print(f"{ANSI_GRN}Press any key to exit.{ANSI_RST}")
                keyboard.read_key()
                sys.exit(0)

            elif status == "FAIL":
                print(f"{ANSI_RED}{name} : true{ANSI_RST}")
                unknown_streak = 0

            else:
                print(f"{ANSI_YLW}{name} : unknown{ANSI_RST}")
                unknown_streak += 1
                if unknown_streak >= 15:
                    print(f"\n{ANSI_RED}15 unknowns — zone is wrong{ANSI_RST}")
                    print(f"{ANSI_RED}Restart and reposition the selector.{ANSI_RST}")
                    keyboard.unhook_all()
                    print(f"{ANSI_RED}Press any key to exit.{ANSI_RST}")
                    keyboard.read_key()
                    sys.exit(2)

            _wait_cycle(state)

    except KeyboardInterrupt:
        print(f"\n{ANSI_RED}stopped{ANSI_RST}")
    except SystemExit:
        raise
    finally:
        try:
            keyboard.unhook_all()
        except Exception:
            pass


def _center(text, width=80):
    return "\n".join(line.center(width) for line in text.split("\n"))


if __name__ == "__main__":
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        print(f"{ANSI_RED}[warn] tesseract not found{ANSI_RST}")
        print(f"{ANSI_RED}install: https://github.com/UB-Mannheim/tesseract/wiki{ANSI_RST}")
        _OCR = False

    main()
