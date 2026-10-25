# AMBER+ Alert Pipeline

A tiny,  pipeline that turns plain-text emergency alerts into visual web pages:
one JSON file per alert comes in, and a ready-to-host HTML page (with an AI-generated
picture of the suspect vehicle) comes out.


| Piece | What it does |
|---|---|
| `poll_alerts.py` | Checks the alert feed every 60s and saves each active alert as `alerts/<alert_id>.json`. Also keeps a combined `alert.json` of everything still active. |
| `render_pages.py` | For every `<id>.json`, bakes the data into the attached `alert.html` template and writes `out/<id>.html`, plus an `out/index.html` landing grid. Runs automatically after each poll, or by hand. |
| `alert.html` | The alert page template. The AI generator script is already embedded - it builds a car image from `car_color` + `car_model` in the browser via pollinations.ai. Supports `?view=driver` and `?view=mini` square layouts. |


`fetch_real_alerts()` expects a JSON list of alert objects with the same field names
as the demo data. Change that one function to match whatever your feed returns -
the rest of the pipeline doesn't care where the data came from.

## The alert JSON format

```json
{
  "alert_id": "A102",
  "person_name": "Sam Rivera",
  "description": "8 years old, brown hair, blue backpack with rockets",
  "last_seen": "Main St & 5th Ave, walking a red bike",
  "photo_url": "https://...",
  "car_model": "Toyota Camry",
  "car_color": "blue",
  "car_plate": "TX-7KP2",
  "contact_email": "tips@example.police.gov"
}
```


## Safety notes

- The demo data in this repo is fictional. 
- AI vehicle images are reference illustrations
