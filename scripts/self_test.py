#!/usr/bin/env python3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import publish_weekend as publisher

TZ = ZoneInfo("America/New_York")


def next_friday(today):
    days = (4 - today.weekday()) % 7
    if days == 0:
        days = 7
    return today + timedelta(days=days)


def main():
    today = datetime.now(TZ).date()
    friday = next_friday(today)
    sunday = friday + timedelta(days=2)

    package = {
        "package_version": 1,
        "report": {
            "title": "Weekend Activities",
            "generated_date": today.isoformat(),
            "generated_at": datetime.now(TZ).isoformat(),
            "center_zip": "20171",
            "weekend_start": friday.isoformat(),
            "weekend_end": sunday.isoformat(),
            "weather_note": "Test weather note.",
            "best_bet_ids": ["test-event"],
            "events": [
                {
                    "id": "test-event",
                    "title": "Test Event",
                    "dates": [friday.isoformat(), sunday.isoformat()],
                    "time": "10 AM-2 PM",
                    "venue": "Test Venue",
                    "address": "12000 Government Center Pkwy, Fairfax, VA 22035",
                    "area": "Fairfax",
                    "price": "Free",
                    "category": "Community",
                    "summary": "Schema validation test event.",
                    "registration": "",
                    "buy_now": False,
                    "source_url": "https://example.com/test-event",
                }
            ],
        },
    }

    report = publisher.validate(package)
    assert report["events"][0]["dates"] == [friday.isoformat(), sunday.isoformat()]
    assert report["events"][0]["map_url"].startswith(
        "https://www.google.com/maps/dir/?api=1&destination="
    )

    invalid = {
        "package_version": 1,
        "report": {
            **report,
            "events": [
                {
                    **report["events"][0],
                    "dates": [(sunday + timedelta(days=1)).isoformat()],
                }
            ],
        },
    }
    try:
        publisher.validate(invalid)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Out-of-weekend event date was not rejected")

    print("Weekend Activities publisher self-test passed.")


if __name__ == "__main__":
    main()
