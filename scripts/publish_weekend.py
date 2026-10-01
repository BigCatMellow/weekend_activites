#!/usr/bin/env python3
import base64
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
REPO = Path(".")
NOTES_REPO = "BigCatMellow/Notes"
TRIGGER_PATH = "data/weekend-activities-trigger.txt"


def fail(message):
    raise RuntimeError(message)


def run(*args):
    subprocess.run(args, check=True)


def extract(body):
    body = body or ""
    raw = re.search(
        r"<!-- WEEKEND_ACTIVITIES_PACKAGE_JSON\n(.*?)\nWEEKEND_ACTIVITIES_PACKAGE_JSON -->",
        body,
        re.S,
    )
    if raw:
        try:
            return json.loads(raw.group(1).strip())
        except Exception as exc:
            fail(f"Invalid raw JSON package: {exc}")

    encoded = re.search(
        r"<!-- WEEKEND_ACTIVITIES_PACKAGE\n(.*?)\nWEEKEND_ACTIVITIES_PACKAGE -->",
        body,
        re.S,
    )
    if not encoded:
        fail("Missing Weekend Activities package envelope")
    try:
        return json.loads(base64.b64decode(encoded.group(1).strip()).decode("utf-8"))
    except Exception as exc:
        fail(f"Invalid package encoding: {exc}")


def maps_url(address):
    destination = urllib.parse.quote(str(address).strip(), safe="")
    return f"https://www.google.com/maps/dir/?api=1&destination={destination}"


def validate(package):
    if package.get("package_version") != 1:
        fail("Unsupported package_version")

    report = package.get("report")
    if not isinstance(report, dict):
        fail("report must be an object")

    today = datetime.now(TZ).date()
    generated_date = str(report.get("generated_date") or "")
    if generated_date != today.isoformat():
        fail(f"generated_date {generated_date!r} != Eastern today {today.isoformat()}")

    try:
        weekend_start = datetime.fromisoformat(str(report["weekend_start"])).date()
        weekend_end = datetime.fromisoformat(str(report["weekend_end"])).date()
    except Exception:
        fail("weekend_start and weekend_end must be ISO dates")

    if weekend_start.weekday() != 4:
        fail("weekend_start must be a Friday")
    if weekend_end.weekday() != 6:
        fail("weekend_end must be a Sunday")
    if (weekend_end - weekend_start).days != 2:
        fail("weekend range must be Friday through Sunday")
    if weekend_start <= today:
        fail("weekend_start must be after publication day")

    if str(report.get("center_zip") or "") != "20171":
        fail("center_zip must be 20171")

    valid_days = {
        weekend_start.isoformat(),
        (weekend_start + timedelta(days=1)).isoformat(),
        weekend_end.isoformat(),
    }

    forecast = report.get("forecast")
    if forecast is not None:
        if not isinstance(forecast, list) or len(forecast) != 3:
            fail("forecast must contain exactly Friday, Saturday, and Sunday")
        forecast_dates = []
        for day in forecast:
            if not isinstance(day, dict):
                fail("Every forecast entry must be an object")
            day_date = str(day.get("date") or "").strip()
            forecast_dates.append(day_date)
            if day_date not in valid_days:
                fail(f"Forecast date {day_date!r} is outside the weekend")
            for key in ("high_f", "low_f"):
                value = day.get(key)
                if not isinstance(value, (int, float)) or value < -100 or value > 150:
                    fail(f"Forecast {day_date} has invalid {key}")
            if not str(day.get("conditions") or "").strip():
                fail(f"Forecast {day_date} is missing conditions")
            day["notable"] = str(day.get("notable") or "").strip()
        if len(set(forecast_dates)) != 3 or set(forecast_dates) != valid_days:
            fail("forecast must contain each Friday-Sunday date exactly once")
        forecast.sort(key=lambda day: day["date"])

    events = report.get("events")
    if not isinstance(events, list) or not events:
        fail("events must be a non-empty list")

    seen_ids = set()

    for event in events:
        if not isinstance(event, dict):
            fail("Every event must be an object")

        event_id = str(event.get("id") or "").strip()
        if not event_id or event_id in seen_ids:
            fail("Each event must have a unique non-empty id")
        seen_ids.add(event_id)

        title = str(event.get("title") or "").strip()
        address = str(event.get("address") or "").strip()
        source_url = str(event.get("source_url") or "").strip()
        dates = event.get("dates")

        if not title:
            fail(f"Event {event_id} is missing title")
        if not address:
            fail(f"Event {event_id} is missing address")
        if not source_url.startswith(("http://", "https://")):
            fail(f"Event {event_id} has invalid source_url")
        if not isinstance(dates, list) or not dates:
            fail(f"Event {event_id} must have a non-empty dates list")
        normalized_dates = [str(day).strip() for day in dates]
        if len(normalized_dates) != len(set(normalized_dates)):
            fail(f"Event {event_id} contains duplicate dates")
        outside = [day for day in normalized_dates if day not in valid_days]
        if outside:
            fail(f"Event {event_id} has dates outside the Friday-Sunday weekend: {outside}")
        event["dates"] = normalized_dates

        event["map_url"] = maps_url(address)

    best = report.get("best_bet_ids") or []
    if not isinstance(best, list):
        fail("best_bet_ids must be a list")
    unknown = [event_id for event_id in best if event_id not in seen_ids]
    if unknown:
        fail(f"best_bet_ids reference unknown events: {unknown}")

    report.setdefault("title", "Weekend Activities")
    report.setdefault("weather_note", "")
    report.setdefault("generated_at", datetime.now(TZ).isoformat())
    return report


def api(url, token, method="GET", data=None):
    request = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if data is not None:
        request.data = json.dumps(data).encode("utf-8")
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def get_trigger_token():
    token = (os.getenv("NOTES_TRIGGER_TOKEN") or "").strip()
    if not token:
        fail(
            "NOTES_TRIGGER_TOKEN is not configured; refusing to publish because "
            "the email handoff cannot be completed"
        )
    return token


def preflight_notes_access(token):
    api(f"https://api.github.com/repos/{NOTES_REPO}", token)


def update_trigger(report, token):
    url = f"https://api.github.com/repos/{NOTES_REPO}/contents/{TRIGGER_PATH}"
    content = f"{report['weekend_start']}\n{report['generated_at']}\n"
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")

    try:
        current = api(url, token)
        existing = base64.b64decode(current.get("content", "")).decode("utf-8")
        if existing == content:
            print("Notes trigger is already current; no duplicate email trigger.")
            return False
        payload = {
            "message": f"Trigger Weekend Activities {report['weekend_start']}",
            "content": encoded,
            "sha": current["sha"],
        }
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        payload = {
            "message": f"Initialize Weekend Activities trigger {report['weekend_start']}",
            "content": encoded,
        }

    api(url, token, "PUT", payload)
    return True


def main():
    package = extract(os.getenv("ISSUE_BODY", ""))
    report = validate(package)
    weekend_start = report["weekend_start"]
    token = get_trigger_token()
    preflight_notes_access(token)

    latest = REPO / "data/latest.json"
    if latest.exists():
        current = json.loads(latest.read_text(encoding="utf-8"))
        if current.get("weekend_start") == weekend_start:
            validate({"package_version": 1, "report": current})
            changed = update_trigger(current, token)
            if changed:
                print("Weekend report was already published; recovered the missing email trigger.")
            else:
                print("Weekend report was already published and already triggered.")
            return

    serialized = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    files = {
        "data/latest.json": serialized,
        f"data/archive/{weekend_start}.json": serialized,
    }

    for path, content in files.items():
        target = REPO / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    run("git", "config", "user.name", "github-actions[bot]")
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )
    run("git", "add", *files.keys())
    run("git", "commit", "-m", f"Publish Weekend Activities {weekend_start}")
    run("git", "push", "origin", "HEAD:main")

    persisted = json.loads((REPO / "data/latest.json").read_text(encoding="utf-8"))
    archived = json.loads(
        (REPO / f"data/archive/{weekend_start}.json").read_text(encoding="utf-8")
    )
    if persisted != archived:
        fail("Persisted archive/latest mismatch")

    validate({"package_version": 1, "report": persisted})
    update_trigger(persisted, token)
    print(f"Published and triggered Weekend Activities for {weekend_start}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
