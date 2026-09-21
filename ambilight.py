"""Universal game Ambilight bridge for Home Assistant.

Reads the left, right and center edge colors of the primary monitor and sends
rate-limited RGB updates to Home Assistant while a configured game is running.
"""
import colorsys
import json, time, subprocess
from pathlib import Path

import mss
import numpy as np
import requests

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config.json"

def load_config():
    with CONFIG.open("r", encoding="utf-8") as f:
        return json.load(f)

def process_exists(exe):
    try:
        out = subprocess.check_output(
            ["tasklist", "/FO", "CSV"],
            encoding="utf-8",
            errors="ignore",
            stderr=subprocess.DEVNULL,
        )
        return exe.lower() in out.lower()
    except Exception:
        return False

def avg_rgb(img):
    # MSS returns BGRA. Ignore alpha and convert to RGB.
    sample = img[:, :, :3].mean(axis=(0, 1))[::-1]
    rgb = [max(0, min(255, int(x))) / 255 for x in sample]
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    s = min(1.0, s * 2.2)
    v = min(1.0, v * 1.05)
    return tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v))

def changed(a, b, threshold):
    return a is None or sum(abs(x-y) for x, y in zip(a, b)) >= threshold

def ha_call(cfg, entity, rgb, brightness):
    url = cfg["home_assistant_url"].rstrip("/") + "/api/services/light/turn_on"
    headers = {"Authorization": "Bearer " + cfg["home_assistant_token"], "Content-Type": "application/json"}
    payload = {"entity_id": entity, "rgb_color": list(rgb), "brightness_pct": round(brightness * 100), "transition": 0}
    requests.post(url, headers=headers, json=payload, timeout=3)

def main():
    cfg = load_config()
    active = False
    previous = {"left": None, "right": None, "center": None}
    interval = 1 / max(1, cfg.get("capture_fps", 5))
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            game = next((v for exe, v in cfg["games"].items() if process_exists(exe)), None)
            if not game:
                if active and cfg.get("restore_lights_when_game_closes", True):
                    # Keep the current lights on. HA automation can restore the normal scene.
                    active = False
                time.sleep(2)
                continue
            active = True
            shot = np.asarray(sct.grab(monitor))
            h, w = shot.shape[:2]
            edge_x = max(8, int(w * 0.12)); edge_y = max(8, int(h * 0.12))
            colors = {
                "left": avg_rgb(shot[int(h*.15):int(h*.85), :edge_x]),
                "right": avg_rgb(shot[int(h*.15):int(h*.85), w-edge_x:]),
                "center": avg_rgb(shot[int(h*.15):int(h*.85), int(w*.35):int(w*.65)])
            }
            for key, entity in (("left", cfg["entities"]["left"]), ("right", cfg["entities"]["right"]), ("center", cfg["entities"]["center"])):
                if changed(previous[key], colors[key], cfg.get("minimum_color_change", 12)):
                    ha_call(cfg, entity, colors[key], game.get("brightness", 0.75) * (0.55 if key == "center" else 1.0))
                    previous[key] = colors[key]
            time.sleep(interval)

if __name__ == "__main__":
    main()
