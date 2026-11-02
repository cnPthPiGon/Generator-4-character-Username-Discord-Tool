import time
import random
import string
import json
import datetime
import os
import sys
from collections import Counter

import pyautogui
import numpy as np
import tkinter as tk
import keyboard
import requests
import colorsys

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

WEBHOOK_URL = "https://discord.com/api/webhooks/1566586654095843378/5cqaYBXxl9p4VDEGlsEAWP3TkQ-rakHUBpSVlqmgqFgKgDOXZsHgFWw1rxXSF61njsZG"
SNIPE_IMAGE_URL = "https://raw.githubusercontent.com/Daziusm/Daziusm/refs/heads/main/sniped.jpg"

CHARS = string.ascii_lowercase + string.digits
LENGTH = 4
DELAY_BETWEEN = 1.5

RESOLUTION_POSITIONS = {
    "2560x1440": {"box_width": 410, "box_height": 45, "box_y_ratio": 0.479},
    "1920x1440": {"box_width": 410, "box_height": 45, "box_y_ratio": 0.479},
    "1920x1200": {"box_width": 410, "box_height": 45, "box_y_ratio": 0.479},
    "1920x1080": {"box_width": 410, "box_height": 45, "box_y_ratio": 0.479},
}

ASCII_TITLE = r"""
 _   _                                       
| | | |___  ___ _ __ _ __   __ _ _ __ ___  ___ 
| | | / __|/ _ \ '__| '_ \ / _` | '_ ` _ \/ __|
| |_| \__ \  __/ |  | | | | (_| | | | | | \__ \
 \___/|___/\___|_|  |_| |_|\__,_|_| |_| |_|___/
  ____ _               _             
 / ___| |__   ___  ___| | _____ _ __ 
| |   | '_ \ / _ \/ __| |/ / _ \ '__|
| |___| | | |  __/ (__|   <  __/ |   
 \____|_| |_|\___|\___|_|\_\___|_|   
"""

DISCORD_ERROR_COLOR = (237, 66, 69)
DISCORD_SUCCESS_COLOR = (87, 242, 135)
DISCORD_WARNING_COLOR = (254, 231, 92)
DISCORD_AVAILABLE_GREEN = (40, 92, 54)
DISCORD_UNAVAILABLE_RED = (237, 66, 69)
DISCORD_ERROR_TEXT_RED = (229, 57, 53)

RED_COLORS = [
    DISCORD_ERROR_COLOR,
    DISCORD_UNAVAILABLE_RED,
    DISCORD_ERROR_TEXT_RED,
    (0xaa, 0x58, 0x57),
    (0x6a, 0x3a, 0x3a),
    (0xeb, 0x75, 0x71),
    (0x97, 0x4f, 0x4e),
    (0xbc, 0x61, 0x5f),
    (255, 99, 71),
    (240, 128, 128),
    (205, 92, 92),
    (220, 20, 60),
]

GREEN_COLORS = [
    DISCORD_SUCCESS_COLOR,
    DISCORD_AVAILABLE_GREEN,
    (0x39, 0x96, 0x51),
    (0x33, 0x7e, 0x46),
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
]

YELLOW_COLORS = [
    DISCORD_WARNING_COLOR,
    (255, 255, 0),
    (255, 215, 0),
    (255, 165, 0),
    (255, 191, 0),
    (241, 196, 15),
]

UI_COLORS = [
    (88, 101, 242),
    (78, 93, 148),
    (60, 60, 65),
    (53, 54, 56),
    (41, 28, 54),
    (72, 73, 75),
    (56, 57, 60),
]

BORDER_COLOR = "#8A2BE2"


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


should_exit = False


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def center_text(text, width=80):
    return "\n".join(line.center(width) for line in text.split("\n"))


def print_status(message, color=None, centered=True, width=80):
    if color:
        message = f"{color}{message}{Colors.END}"
    if centered:
        message = center_text(message, width)
    print(message)


def print_separator(char="=", length=80):
    print(char * length)


def on_esc_press(e):
    global should_exit
    should_exit = True


def get_resolution():
    w, h = pyautogui.size()
    return f"{w}x{h}"


def get_box_position():
    resolution = get_resolution()
    screen_width, screen_height = pyautogui.size()
    settings = RESOLUTION_POSITIONS.get(resolution, RESOLUTION_POSITIONS["1920x1080"])
    box_width = settings["box_width"]
    box_height = settings["box_height"]
    box_y_ratio = settings["box_y_ratio"]
    box_x = (screen_width - box_width) // 2
    box_y = int(screen_height * box_y_ratio)
    return (box_x, box_y, box_width, box_height)


def debug_log(msg):
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")


def generate_random_4char():
    return "".join(random.choices(CHARS, k=LENGTH))


def color_distance(c1, c2, weights=(1.0, 1.2, 0.8)):
    try:
        return sum(w * (a - b) ** 2 for a, b, w in zip(c1, c2, weights)) ** 0.5
    except OverflowError:
        return 1000


def is_border_color(color, border_rgb=(138, 43, 226), threshold=50):
    return sum(abs(color[i] - border_rgb[i]) for i in range(3)) < threshold


def get_saturation(color):
    r, g, b = [c / 255.0 for c in color]
    if max(r, g, b) == 0:
        return 0
    _, s, _ = colorsys.rgb_to_hsv(r, g, b)
    return s


def get_box_color(x, y, w, h):
    img = pyautogui.screenshot(region=(x, y, w, h))
    arr = np.array(img)
    avg = np.mean(arr, axis=(0, 1))
    return tuple(map(int, avg))


def check_color_matches(color):
    if color_distance(color, DISCORD_ERROR_COLOR) < 35:
        return "RED"
    if color_distance(color, DISCORD_UNAVAILABLE_RED) < 35:
        return "RED"
    if color_distance(color, DISCORD_SUCCESS_COLOR) < 40:
        return "GREEN"
    if color_distance(color, DISCORD_AVAILABLE_GREEN) < 30:
        return "GREEN"
    if color_distance(color, DISCORD_WARNING_COLOR) < 40:
        return "YELLOW"
    for ui in UI_COLORS:
        if color_distance(color, ui) < 40:
            return "UI"
    for g in GREEN_COLORS:
        if color_distance(color, g) < 45:
            return "GREEN"
    for r in RED_COLORS:
        if color_distance(color, r) < 45:
            return "RED"
    for y in YELLOW_COLORS:
        if color_distance(color, y) < 60:
            return "YELLOW"
    return "UNKNOWN"


def get_dominant_text_color(x, y, w, h):
    img = pyautogui.screenshot(region=(x, y, w, h))
    arr = np.array(img)

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            pixel = tuple(arr[i, j])
            for g in GREEN_COLORS[:5]:
                if color_distance(pixel, g) < 30:
                    return "GREEN", pixel
            for r in RED_COLORS[:5]:
                if color_distance(pixel, r) < 35:
                    return "RED", pixel

    return check_color_matches(get_box_color(x, y, w, h)), None


def check_single_color(box):
    x, y, w, h = box
    try:
        img = pyautogui.screenshot(region=(x, y, w, h))
        arr = np.array(img)

        found_green = False
        found_red = False

        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                pixel = tuple(arr[i, j])
                for g in GREEN_COLORS[:5]:
                    if color_distance(pixel, g) < 30:
                        found_green = True
                        break
                for r in RED_COLORS[:5]:
                    if color_distance(pixel, r) < 35:
                        found_red = True
                        break
                if found_green and found_red:
                    break
            if found_green and found_red:
                break

        if found_green and not found_red:
            return "GREEN", GREEN_COLORS[0]
        if found_red and not found_green:
            return "RED", RED_COLORS[0]
    except Exception:
        pass

    status, color = get_dominant_text_color(x, y, w, h)
    if status in ["RED", "GREEN", "YELLOW", "UI"]:
        return status, color

    if color is None:
        color = get_box_color(x, y, w, h)
    status = check_color_matches(color)
    if "RED" in status:
        return "RED", color
    if "GREEN" in status:
        return "GREEN", color
    if "YELLOW" in status:
        return "YELLOW", color
    if "UI" in status:
        return "UI", color
    return "UNKNOWN", color


def force_topmost(windows):
    if win32gui is None:
        return
    try:
        for win in windows:
            if hasattr(win, 'winfo_id'):
                hwnd = win32gui.GetParent(win.winfo_id())
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
                )
    except Exception:
        pass


class SimpleBorder:
    def __init__(self, x, y, w, h, border_thickness=4):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.thickness = border_thickness
        self.windows = []
        self._create()

    def _create(self):
        top = tk.Tk()
        top.overrideredirect(True)
        top.configure(background=BORDER_COLOR)
        top.geometry(f"{self.width}x{self.thickness}+{self.x}+{self.y}")
        top.attributes('-topmost', True)
        top.lift()
        self.windows.append(top)

        bottom = tk.Toplevel()
        bottom.overrideredirect(True)
        bottom.configure(background=BORDER_COLOR)
        bottom.geometry(f"{self.width}x{self.thickness}+{self.x}+{self.y + self.height - self.thickness}")
        bottom.attributes('-topmost', True)
        bottom.lift()
        self.windows.append(bottom)

        left = tk.Toplevel()
        left.overrideredirect(True)
        left.configure(background=BORDER_COLOR)
        left.geometry(f"{self.thickness}x{self.height}+{self.x}+{self.y}")
        left.attributes('-topmost', True)
        left.lift()
        self.windows.append(left)

        right = tk.Toplevel()
        right.overrideredirect(True)
        right.configure(background=BORDER_COLOR)
        right.geometry(f"{self.thickness}x{self.height}+{self.x + self.width - self.thickness}+{self.y}")
        right.attributes('-topmost', True)
        right.lift()
        self.windows.append(right)

        for win in self.windows:
            win.update()
        force_topmost(self.windows)

    def update(self):
        for win in self.windows:
            try:
                win.attributes('-topmost', True)
                win.lift()
                win.update()
            except Exception:
                pass
        force_topmost(self.windows)

    def destroy(self):
        for win in self.windows:
            try:
                win.destroy()
            except Exception:
                pass
        self.windows = []


def make_console_topmost():
    if win32gui is None:
        return
    try:
        hwnd = win32gui.GetForegroundWindow()
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )
    except Exception:
        pass


def send_webhook(username):
    now = datetime.datetime.now()
    ts = now.isoformat()
    unix_ts = int(now.timestamp())
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")

    length = len(username)
    has_num = any(c.isdigit() for c in username)
    has_special = any(not c.isalnum() for c in username)
    complexity = "Simple"
    if has_num and has_special:
        complexity = "Complex"
    elif has_num or has_special:
        complexity = "Medium"

    colors = [5793266, 5763719, 3066993, 2067276, 3447003, 10181046, 15277667, 15844367, 16705372]

    embed = {
        "title": "Username disponible",
        "description": f"```{username}```\n**Pseudo 4 caracteres trouve sur Discord**",
        "color": random.choice(colors),
        "fields": [
            {"name": "Stats", "value": f"**Longueur:** {length}\n**Complexite:** {complexity}", "inline": True},
            {"name": "Timestamp", "value": f"<t:{unix_ts}:F>\n<t:{unix_ts}:R>", "inline": True},
        ],
        "image": {"url": SNIPE_IMAGE_URL},
        "footer": {"text": f"4char checker • {formatted}"},
        "timestamp": ts,
    }

    data = {
        "content": f"**Pseudo dispo:** `{username}`",
        "embeds": [embed],
        "username": "4char Sniper",
    }

    try:
        r = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if r.status_code == 204:
            debug_log(f"webhook envoye pour {username}")
        else:
            debug_log(f"webhook http {r.status_code}")
    except Exception as e:
        debug_log(f"webhook err {e}")


class Checker:
    def __init__(self):
        self.valid = []
        self.monitoring_box = get_box_position()
        debug_log(f"resolution: {get_resolution()}")
        debug_log(f"box: {self.monitoring_box}")
        self.border = SimpleBorder(
            self.monitoring_box[0], self.monitoring_box[1],
            self.monitoring_box[2], self.monitoring_box[3],
            border_thickness=4
        )
        try:
            self.term_width = os.get_terminal_size().columns
        except Exception:
            self.term_width = 80

    def type_username(self, word):
        self.border.update()
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.15)
        pyautogui.press('delete')
        time.sleep(0.15)
        self.border.update()
        pyautogui.write(word, interval=0.03)
        self.border.update()
        time.sleep(0.5)

    def check_color_verified(self):
        samples = []
        for _ in range(3):
            status, _ = check_single_color(self.monitoring_box)
            samples.append(status)
            time.sleep(0.1)
        if "GREEN" in samples:
            return "GREEN"
        if samples.count("RED") >= 2:
            return "RED"
        return Counter(samples).most_common(1)[0][0]

    def display_progress(self, word, attempt, status=""):
        clear_screen()
        w = self.term_width
        print(Colors.CYAN + center_text(ASCII_TITLE, w) + Colors.END)
        print_separator("=", w)
        print_status(f"Test: {Colors.BOLD}{Colors.YELLOW}{word}{Colors.END}", centered=False)
        print_status(f"Deja testes: {attempt}", centered=False)
        if status:
            if status == "GREEN":
                print_status(f"Status: {Colors.GREEN}DISPO{Colors.END}", centered=False)
            elif status == "RED":
                print_status(f"Status: {Colors.RED}PRIS{Colors.END}", centered=False)
            else:
                print_status(f"Status: {Colors.YELLOW}{status}{Colors.END}", centered=False)
        if self.valid:
            print_separator("-", w)
            print_status(f"Trouves: {len(self.valid)}", color=Colors.GREEN, centered=False)
            for u in self.valid[-5:]:
                print_status(f"  -> {u}", color=Colors.GREEN, centered=False)
        print_separator("=", w)
        print_status("ESC pour stop", color=Colors.YELLOW, centered=False)

    def run(self):
        global should_exit
        if os.name == 'nt':
            os.system('color')
        clear_screen()
        print(Colors.CYAN + center_text(ASCII_TITLE, self.term_width) + Colors.END)
        print_separator("=", self.term_width)
        print_status("Mode: 4 caracteres (a-z, 0-9)", color=Colors.GREEN)
        print_status(f"Delai: {DELAY_BETWEEN}s entre chaque test", color=Colors.CYAN)
        print_status("ESC pour stop", color=Colors.YELLOW)

        keyboard.on_press_key('esc', on_esc_press)

        attempts = 0
        try:
            while not should_exit:
                word = generate_random_4char()
                self.type_username(word)
                status = self.check_color_verified()
                self.display_progress(word, attempts, status)

                if status == "GREEN":
                    self.valid.append(word)
                    debug_log(f"DISPO: {word}")
                    send_webhook(word)

                attempts += 1
                time.sleep(DELAY_BETWEEN)
        except KeyboardInterrupt:
            print_status("Stop.", color=Colors.RED)
        finally:
            self.border.destroy()
            keyboard.unhook_all()

        clear_screen()
        print(Colors.CYAN + center_text(ASCII_TITLE, self.term_width) + Colors.END)
        print_separator("=", self.term_width)
        print_status(f"Total testes: {attempts}", centered=False)
        print_status(f"Trouves: {len(self.valid)}", color=Colors.GREEN, centered=False)
        for i, u in enumerate(self.valid):
            print_status(f"  {i+1}. {u}", color=Colors.GREEN, centered=False)
        print_separator("=", self.term_width)
        print_status("Appuie sur une touche pour quitter", color=Colors.YELLOW, centered=False)
        keyboard.read_key()


if __name__ == "__main__":
    make_console_topmost()
    checker = Checker()
    print_status("Place le curseur dans le champ pseudo Discord, puis appuie sur une touche.", color=Colors.YELLOW)
    keyboard.read_key()
    checker.run()
