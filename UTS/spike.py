import os
import sys
import time
import math
import json
import random
import threading
from datetime import datetime

try:
    if sys.platform.startswith("win"):
        import winsound
    else:
        winsound = None
except Exception:
    winsound = None

# --------------------------
# Configuration / Globals
# --------------------------
PRESET_FILE = "presets.json"
LOCK = threading.Lock()

# terminal control
CLEAR = "cls" if os.name == "nt" else "clear"
RESET = "\033[0m"
# Basic neon-like ANSI colors (bright)
COLORS = [
    "\033[95m",  # magenta
    "\033[96m",  # cyan
    "\033[92m",  # green
    "\033[93m",  # yellow
    "\033[91m",  # red
    "\033[94m",  # blue
]

# State
state = {
    "running": False,
    "paused": False,
    "thread": None,
    "mode": "Wave",
    "speed": 0.06,
    "color_mode": "cycle",  # cycle, random, single
    "single_color": COLORS[1],
    "sound": True,
    "auto_mode": False,
    "auto_interval": 8,
    "auto_random": True,
    "presets": {},
    "current_preset": None
}

# load presets if exists
def load_presets_file():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r", encoding="utf-8") as f:
                state["presets"] = json.load(f)
        except Exception:
            state["presets"] = {}
    else:
        state["presets"] = {}

def save_presets_file():
    try:
        with open(PRESET_FILE, "w", encoding="utf-8") as f:
            json.dump(state["presets"], f, indent=2)
    except Exception as e:
        print("Failed saving presets:", e)

load_presets_file()

# --------------------------
# Utilities
# --------------------------
def clear():
    os.system(CLEAR)

def beep(kind="short"):
    if not state["sound"]:
        return
    try:
        if winsound:
            if kind == "short":
                winsound.Beep(700, 100)
            else:
                winsound.Beep(400, 260)
        else:
            # fallback bell
            print("\a", end="", flush=True)
    except Exception:
        pass

def color_text(s, idx):
    return (state["single_color"] if state["color_mode"] == "single"
            else (random.choice(COLORS) if state["color_mode"] == "random"
                  else COLORS[idx % len(COLORS)])) + s + RESET

def safe_sleep(t):
    # allow small sleeps to be interruptible by state changes
    end = time.time() + t
    while time.time() < end:
        if not state["running"]:
            break
        time.sleep(min(0.05, end - time.time()))

# --------------------------
# Animation Modes
# All animations read `state["speed"]` and `state["paused"]`
# --------------------------

def anim_wave():
    i = 0.0
    idx = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            y = int((math.sin(i) + 1) * 20)
            line = "-" * y
            print(color_text(line, idx))
            i += 0.25
            idx += 1
            safe_sleep(state["speed"])
    finally:
        pass

def anim_matrix():
    chars = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ@#%&*"
    width = min(100, os.get_terminal_size().columns if hasattr(os, "get_terminal_size") else 80)
    idx = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            for _ in range(10):
                line = "".join(random.choice(chars) for _ in range(width))
                print(color_text(line, idx))
            idx += 1
            safe_sleep(state["speed"])
    finally:
        pass

def anim_particles():
    width = min(100, os.get_terminal_size().columns if hasattr(os, "get_terminal_size") else 80)
    height = 20
    chars = ["*", "+", ".", "•"]
    idx = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            for _ in range(height):
                line = "".join(random.choice(chars) if random.random() < 0.04 else " " for _ in range(width))
                print(color_text(line, idx))
            idx += 1
            safe_sleep(state["speed"])
    finally:
        pass

def anim_loading():
    bars = ["|", "/", "-", "\\"]
    i = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            print(color_text("Loading " + bars[i % len(bars)], i))
            i += 1
            safe_sleep(state["speed"])
    finally:
        pass

def anim_spiral():
    t = 0.0
    width = min(80, os.get_terminal_size().columns if hasattr(os, "get_terminal_size") else 80)
    idx = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            size = 12
            lines = []
            for i in range(size):
                x = int(size * math.sin(t + i / 2))
                spacing = max(0, x + size)
                lines.append(" " * spacing + color_text("*", idx))
            print("\n".join(lines))
            t += 0.35
            idx += 1
            safe_sleep(state["speed"])
    finally:
        pass

def anim_flames():
    # simulate flame columns using colored blocks and chars
    width = min(80, os.get_terminal_size().columns if hasattr(os, "get_terminal_size") else 80)
    colors_flame = ["\033[91m", "\033[93m", "\033[95m", "\033[33m"]  # reds/yellows
    idx = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            height = 18
            for row in range(height):
                line = ""
                for col in range(width):
                    p = random.random()
                    if p < (0.12 + (row / height) * 0.18):
                        # choose flame char and color biased by row
                        ch = random.choice(["^", "~", "*", ".", " "])
                        colr = colors_flame[int((row / height) * (len(colors_flame)-1))]
                        if state["color_mode"] == "single":
                            colr = state["single_color"]
                        line += f"{colr}{ch}{RESET}"
                    else:
                        line += " "
                print(line)
            idx += 1
            safe_sleep(max(0.02, state["speed"] * 0.8))
    finally:
        pass

def anim_equalizer():
    width = 40
    max_h = 16
    idx = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            # simulate few bars
            bars = [random.randint(1, max_h) for _ in range(width//4)]
            for level in range(max_h, 0, -1):
                line = ""
                for b in bars:
                    line += color_text(" █ " if b >= level else "   ", idx)
                print(line)
            idx += 1
            safe_sleep(state["speed"])
    finally:
        pass

def anim_glitch():
    width = min(100, os.get_terminal_size().columns if hasattr(os, "get_terminal_size") else 80)
    chars = "@#$%^&*()_-=+[]{}<>?/\\|~`"
    idx = 0
    try:
        while state["running"]:
            if state["paused"]:
                time.sleep(0.1)
                continue
            clear()
            # flicker header
            if random.random() < 0.4:
                print(color_text("ACCESS GRANTED", idx))
            else:
                print(color_text("!!! GLITCH !!!", idx))
            # noise region
            for _ in range(12):
                line = "".join(random.choice(chars + "   ") for _ in range(width//2))
                print(color_text(line, idx))
            idx += 1
            safe_sleep(max(0.03, state["speed"] * (0.6 + random.random()*0.8)))
    finally:
        pass

MODES = {
    "Wave": anim_wave,
    "Matrix": anim_matrix,
    "Particles": anim_particles,
    "Loading": anim_loading,
    "Spiral": anim_spiral,
    "Flames": anim_flames,
    "Equalizer": anim_equalizer,
    "Glitch": anim_glitch
}

# --------------------------
# Threading control: start / stop / pause / resume
# --------------------------
def _runner(mode_name):
    try:
        func = MODES.get(mode_name, anim_wave)
        func()
    except Exception as e:
        print("Animation error:", e)
    finally:
        state["running"] = False

def start_mode(mode_name=None):
    if mode_name:
        state["mode"] = mode_name
    if state["running"]:
        return
    state["running"] = True
    state["paused"] = False
    t = threading.Thread(target=_runner, args=(state["mode"],), daemon=True)
    state["thread"] = t
    t.start()
    beep("start")

def stop_mode():
    state["running"] = False
    state["paused"] = False
    # give thread small time to exit
    if state["thread"] and state["thread"].is_alive():
        state["thread"].join(timeout=1.0)
    beep("stop")

def pause_mode():
    if state["running"]:
        state["paused"] = True

def resume_mode():
    if state["running"]:
        state["paused"] = False

# --------------------------
# Auto mode handler
# --------------------------
def auto_mode_loop():
    modes_list = list(MODES.keys())
    idx = 0
    try:
        while state["auto_mode"] and (not state["running"] or state["thread"].is_alive()):
            # pick next mode
            if state["auto_random"]:
                next_mode = random.choice(modes_list)
            else:
                next_mode = modes_list[idx % len(modes_list)]
                idx += 1
            stop_mode()
            start_mode(next_mode)
            # wait interval but allow interruption
            end = time.time() + state["auto_interval"]
            while time.time() < end:
                if not state["auto_mode"]:
                    break
                time.sleep(0.5)
            # continue loop
            if not state["auto_mode"]:
                break
    except Exception:
        pass

def start_auto():
    state["auto_mode"] = True
    t = threading.Thread(target=auto_mode_loop, daemon=True)
    t.start()

def stop_auto():
    state["auto_mode"] = False

# --------------------------
# Preset manager
# --------------------------
def preset_save(name):
    if not name:
        print("Preset name empty.")
        return
    preset = {
        "mode": state["mode"],
        "speed": state["speed"],
        "color_mode": state["color_mode"],
        "single_color": state["single_color"],
        "sound": state["sound"],
        "auto_interval": state["auto_interval"],
        "auto_random": state["auto_random"]
    }
    state["presets"][name] = preset
    save_presets_file()
    print(f"Preset '{name}' saved.")

def preset_load(name):
    p = state["presets"].get(name)
    if not p:
        print("Preset not found.")
        return
    state["mode"] = p.get("mode", state["mode"])
    state["speed"] = p.get("speed", state["speed"])
    state["color_mode"] = p.get("color_mode", state["color_mode"])
    state["single_color"] = p.get("single_color", state["single_color"])
    state["sound"] = p.get("sound", state["sound"])
    state["auto_interval"] = p.get("auto_interval", state["auto_interval"])
    state["auto_random"] = p.get("auto_random", state["auto_random"])
    print(f"Preset '{name}' loaded.")

def preset_delete(name):
    if name in state["presets"]:
        del state["presets"][name]
        save_presets_file()
        print(f"Preset '{name}' deleted.")
    else:
        print("Preset not found.")

def preset_list():
    if not state["presets"]:
        print("[no presets saved]")
        return
    print("Saved presets:")
    for k in state["presets"].keys():
        print(" -", k)

# --------------------------
# Main interactive menu
# --------------------------
def main_menu():
    try:
        while True:
            clear()
            print("\033[95m=== CONSOLE ANIMATION PRO v2 ===\033[0m")
            print(f" Mode: {state['mode']} | Speed: {state['speed']:.3f}s/frame | ColorMode: {state['color_mode']} | Sound: {'ON' if state['sound'] else 'OFF'}")
            print(" Auto:", "ON" if state["auto_mode"] else "OFF", f"(Interval {state['auto_interval']}s, Random {state['auto_random']})")
            print("\n1) Start Mode")
            print("2) Stop")
            print("3) Pause")
            print("4) Resume")
            print("5) Choose Mode")
            print("6) Toggle Sound")
            print("7) Color Mode (cycle/random/single)")
            print("8) Set Single Color (ANSI code index 0..5)")
            print("9) Speed (seconds per frame)")
            print("10) Auto Mode Start/Stop")
            print("11) Auto settings (interval/random)")
            print("12) Preset: Save")
            print("13) Preset: Load")
            print("14) Preset: Delete")
            print("15) Preset: List")
            print("16) Toggle Pause While Running")
            print("0) Exit")
            print("\nAvailable Modes:", ", ".join(MODES.keys()))
            choice = input("\nSelect > ").strip()

            if choice == "1":
                start_mode()
            elif choice == "2":
                stop_mode()
            elif choice == "3":
                pause_mode()
            elif choice == "4":
                resume_mode()
            elif choice == "5":
                print("Modes:", ", ".join(MODES.keys()))
                m = input("Enter mode name: ").strip()
                if m in MODES:
                    start_mode(m)
                else:
                    print("Unknown mode.")
                    time.sleep(1)
            elif choice == "6":
                state["sound"] = not state["sound"]
                print("Sound set to", state["sound"])
                time.sleep(0.6)
            elif choice == "7":
                cm = input("Enter color mode (cycle/random/single): ").strip().lower()
                if cm in ("cycle", "random", "single"):
                    state["color_mode"] = cm
                else:
                    print("Invalid option.")
                time.sleep(0.6)
            elif choice == "8":
                print("Pick single color index:")
                for i, c in enumerate(COLORS):
                    print(i, color_text("███", i))
                idx = input("index> ").strip()
                try:
                    idx = int(idx)
                    state["single_color"] = COLORS[idx % len(COLORS)]
                    state["color_mode"] = "single"
                except Exception:
                    print("Invalid index")
                time.sleep(0.6)
            elif choice == "9":
                v = input("Enter speed (seconds per frame, e.g. 0.05): ").strip()
                try:
                    state["speed"] = max(0.005, float(v))
                except Exception:
                    print("Invalid value")
                time.sleep(0.4)
            elif choice == "10":
                if state["auto_mode"]:
                    stop_auto()
                    print("Auto mode stopped.")
                else:
                    start_auto()
                    print("Auto mode started.")
                time.sleep(0.6)
            elif choice == "11":
                try:
                    iv = int(input("Auto interval seconds (>1): ").strip())
                    state["auto_interval"] = max(1, iv)
                    ar = input("Random order? (y/n): ").strip().lower()
                    state["auto_random"] = (ar == "y")
                except Exception:
                    print("Invalid input")
                time.sleep(0.6)
            elif choice == "12":
                name = input("Preset name to save: ").strip()
                if name:
                    preset_save(name)
                time.sleep(0.6)
            elif choice == "13":
                name = input("Preset name to load: ").strip()
                if name:
                    preset_load(name)
                time.sleep(0.6)
            elif choice == "14":
                name = input("Preset name to delete: ").strip()
                if name:
                    preset_delete(name)
                time.sleep(0.6)
            elif choice == "15":
                preset_list()
                input("Press ENTER...")
            elif choice == "16":
                if state["running"]:
                    state["paused"] = not state["paused"]
            elif choice == "0":
                print("Exiting...")
                stop_auto()
                stop_mode()
                break
            else:
                print("Unknown choice.")
                time.sleep(0.6)
    except KeyboardInterrupt:
        print("\nInterrupted. Stopping...")
        stop_auto()
        stop_mode()
    finally:
        print("Goodbye.")

if __name__ == "__main__":
    main_menu()
