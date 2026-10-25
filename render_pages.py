"""render_pages.py  -- STEP 2: Turn alert JSON files into alert HTML pages."""


import json
import os

DATA_DIR = "alerts"
TEMPLATE_FILE = "alert.html" 
OUT_DIR = "out"

def load_template():
    with open(TEMPLATE_FILE) as f:
        return f.read()

def build_alert_page(template, alert):
    """Take the attached alert.html and inject ONE alert's data into it.

    Two tiny string replacements:
      1. hard-code this page's alert id so no ?id= is needed
      2. replace the GitHub fetch with the baked-in JSON
    Everything else is exactly the page in this repo.
    """
    page = template.replace(
        "const alertId = urlParams.get('id');",
        'const alertId = "' + alert["alert_id"] + '"; // baked in by render_pages.py'
    )
    old_fetch = ("const response = await fetch('https://raw.githubusercontent.com/"
                 "aditiahuja230-rgb/amberalert/refs/heads/main/alert.json');\n"
                 "        let data = await response.json();")
    page = page.replace(old_fetch,
                        "let data = " + json.dumps(alert) + "; // baked in by render_pages.py")
    return page

def build_index(alerts):
    """A bare-bones landing grid linking to each alert page."""
    cards = []
    for a in alerts:
        cards.append(
            '      <a class="card" href="' + a["alert_id"] + '.html">\n'
            '        <img src="' + a.get("photo_url", "") + '" alt="">\n'
            "        <b>" + a.get("person_name", "?") + "</b>\n"
            "        <span>" + a.get("car_color", "") + " " + a.get("car_model", "")
            + " - " + a.get("car_plate", "") + "</span>\n"
            "      </a>\n"
        )
    body = ""
    if cards:
        body = "".join(cards)
    else:
        body = "<p>No active alerts right now.</p>"
    return INDEX_TEMPLATE.replace("__CARDS__", body)

INDEX_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Active Alerts</title>
<style>
  body { font-family: 'Segoe UI', sans-serif; background: #f4f4f4; margin: 24px; }
  h1 { color: #d32f2f; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
  .card { background: #fff; border-top: 8px solid #d32f2f; border-radius: 12px;
          padding: 14px; text-decoration: none; color: #333; box-shadow: 0 4px 12px rgba(0,0,0,.08);
          display: flex; flex-direction: column; gap: 6px; }
  .card img { width: 100%; border-radius: 8px; }
</style></head>
<body><h1>Active Alerts</h1><div class="grid">
__CARDS__
</div></body></html>"""

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    template = load_template()

    # copy the template itself so out/alert.html also works standalone
    with open(os.path.join(OUT_DIR, TEMPLATE_FILE), "w") as f:
        f.write(template)

    alerts = []
    for name in sorted(os.listdir(DATA_DIR)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(DATA_DIR, name)) as f:
            alert = json.load(f)
        alerts.append(alert)

        out_path = os.path.join(OUT_DIR, name.replace(".json", ".html"))
        # skip files we already built - nothing changed, nothing to do
        if os.path.exists(out_path):
            continue
        with open(out_path, "w") as f:
            f.write(build_alert_page(template, alert))
        print(f"  -> page built: {out_path}")

    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(build_index(alerts))
    print(f"{len(alerts)} page(s) in {OUT_DIR}/ (open {OUT_DIR}/index.html)")

if __name__ == "__main__":
    main()
