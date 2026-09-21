"""Low-resource universal Ambilight bridge for Home Assistant."""
import colorsys
import json
import time
from pathlib import Path

import mss
import requests
import numpy as np

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config.json"


def load_config():
    with CONFIG.open("r", encoding="utf-8") as f:
        return json.load(f)


def average_rgb(image):
    sample = image[:, :, :3].mean(axis=(0, 1))[::-1]
    rgb = [max(0.0, min(255.0, float(x))) / 255.0 for x in sample]
    hue, saturation, value = colorsys.rgb_to_hsv(*rgb)
    saturation = min(1.0, saturation * 2.0)
    value = min(1.0, value * 1.05)
    return tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, saturation, value))


def changed(old, new, threshold):
    return old is None or sum(abs(a - b) for a, b in zip(old, new)) >= threshold


def send_light(session, cfg, entity, rgb, brightness):
    url = cfg["home_assistant_url"].rstrip("/") + "/api/services/light/turn_on"
    headers = {"Authorization": "Bearer " + cfg["home_assistant_token"], "Content-Type": "application/json"}
    payload = {"entity_id": entity, "rgb_color": list(rgb), "brightness_pct": round(brightness * 100), "transition": 0}
    try:
        session.post(url, headers=headers, json=payload, timeout=1.5)
    except requests.RequestException:
        pass


def capture_colors(sct, monitor, strip):
    x, y, width, height = monitor["left"], monitor["top"], monitor["width"], monitor["height"]
    side = max(8, int(width * strip))
    top = max(8, int(height * strip))
    left = average_rgb(sct.grab({"left": x, "top": y + int(height * .15), "width": side, "height": int(height * .70)}))
    right = average_rgb(sct.grab({"left": x + width - side, "top": y + int(height * .15), "width": side, "height": int(height * .70)}))
    center = average_rgb(sct.grab({"left": x + int(width * .35), "top": y, "width": int(width * .30), "height": top}))
    return {"left": left, "right": right, "center": center}


def main():
    cfg = load_config()
    interval = 1.0 / max(1, float(cfg.get("capture_fps", 10)))
    threshold = int(cfg.get("minimum_color_change", 10))
    strip = float(cfg.get("edge_fraction", 0.06))
    previous = {"left": None, "right": None, "center": None}
    session = requests.Session()
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            started = time.perf_counter()
            colors = capture_colors(sct, monitor, strip)
            for key in ("left", "right", "center"):
                if changed(previous[key], colors[key], threshold):
                    brightness = float(cfg.get("brightness", .80))
                    if key == "center":
                        brightness *= .55
                    send_light(session, cfg, cfg["entities"][key], colors[key], brightness)
                    previous[key] = colors[key]
            time.sleep(max(0.0, interval - (time.perf_counter() - started)))


if __name__ == "__main__":
    main()
