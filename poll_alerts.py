"""poll_alerts.py  -- STEP 1: Poll for active alerts. """

import argparse
import json
import os
import random
import time
from urllib.request import urlopen

DATA_DIR = "alerts"          # where the id.json files live
COMBINED_FILE = "alert.json" # combined list, used by alert.html
POLL_EVERY = 60              # seconds between polls
MAX_DEMO_ACTIVE = 2          # demo mode keeps at most this many alerts active

# ---------------- Step A: get the alerts ----------------

SAMPLE_ALERTS = [
    {
        "alert_id": "A102",
        "person_name": "Sam Rivera",
        "description": "8 years old, brown hair, blue backpack with rockets",
        "last_seen": "Main St & 5th Ave, walking a red bike",
        "photo_url": "https://ui-avatars.com/api/?name=Sam+R&background=d32f2f&color=fff&size=300",
        "car_model": "Toyota Camry",
        "car_color": "blue",
        "car_plate": "TX-7KP2",
        "contact_email": "tips@example.police.gov",
    },
    {
        "alert_id": "A103",
        "person_name": "Maya Chen",
        "description": "6 years old, black braids, yellow raincoat",
        "last_seen": "Riverside Park playground",
        "photo_url": "https://ui-avatars.com/api/?name=Maya+C&background=376BD0&color=fff&size=300",
        "car_model": "Honda Odyssey",
        "car_color": "silver",
        "car_plate": "TX-3MN9",
        "contact_email": "tips@example.police.gov",
    },
    {
        "alert_id": "A104",
        "person_name": "Leo Brooks",
        "description": "10 years old, glasses, green hoodie",
        "last_seen": "Bus stop on County Rd 12",
        "photo_url": "https://ui-avatars.com/api/?name=Leo+B&background=1B2A44&color=fff&size=300",
        "car_model": "Ford F-150",
        "car_color": "white",
        "car_plate": "TX-9QT4",
        "contact_email": "tips@example.police.gov",
    },
]

def fetch_real_alerts(feed_url):
    """Ask the real feed for alerts. Expects a JSON list of alert objects."""
    with urlopen(feed_url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def fetch_demo_alerts(state):
    """Pretend to be a real feed: recycle the 3 sample alerts forever.

    Keeps at most MAX_DEMO_ACTIVE alerts 'active' at a time so you can
    watch alerts appear AND disappear, just like the real thing.
    """
    idx = state.get("next", 0)
    if random.random() < 0.7 or not state.get("active_ids"):
        alert = SAMPLE_ALERTS[idx % len(SAMPLE_ALERTS)]
        state.setdefault("active_ids", [])
        if alert["alert_id"] not in state["active_ids"]:
            state["active_ids"].append(alert["alert_id"])
            state["next"] = idx + 1
        while len(state["active_ids"]) > MAX_DEMO_ACTIVE:
            state["active_ids"].pop(0)
    by_id = {a["alert_id"]: a for a in SAMPLE_ALERTS}
    return [by_id[a] for a in state["active_ids"]]

# ---------------- Step B: save the alerts ----------------

def save_alert(alert):
    """Write one alert to alerts/<alert_id>.json"""
    path = os.path.join(DATA_DIR, f"{alert['alert_id']}.json")
    if not os.path.exists(path):  # don't rewrite files we already have
        with open(path, "w") as f:
            json.dump(alert, f, indent=2)
        print(f"  -> new alert saved: {path}")

def update_combined(active_alerts):
    """Rewrite alert.json so it only lists alerts that are STILL active."""
    with open(COMBINED_FILE, "w") as f:
        json.dump(active_alerts, f, indent=2)

def poll_once(demo, feed_url, state):
    alerts = fetch_demo_alerts(state) if demo else fetch_real_alerts(feed_url)
    for a in alerts:
        save_alert(a)
    update_combined(alerts)
    print(f"{len(alerts)} alert(s) currently active. ids={[a['alert_id'] for a in alerts]}")

    # Step 2 happens right after: turn any new/changed json files into pages
    try:
        import render_pages
        render_pages.main()
    except ImportError:
        print("render_pages.py not found - skipping page build")

def main():
    parser = argparse.ArgumentParser(description="Poll for active alerts, save as JSON.")
    parser.add_argument("--demo", action="store_true", help="use built-in fake alerts")
    parser.add_argument("--feed-url", default=None, help="real JSON feed URL")
    parser.add_argument("--once", action="store_true", help="poll a single time then exit")
    args = parser.parse_args()

    if not args.demo and not args.feed_url:
        parser.error("use --demo or provide --feed-url")

    os.makedirs(DATA_DIR, exist_ok=True)
    state = {}
    while True:
        print(f"[{time.strftime('%H:%M:%S')}] polling...")
        poll_once(args.demo, args.feed_url, state)
        if args.once:
            break
        print(f"sleeping {POLL_EVERY}s\n")
        time.sleep(POLL_EVERY)

if __name__ == "__main__":
    main()
