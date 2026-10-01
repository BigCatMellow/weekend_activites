# Scheduled Weekend Activities handoff

This file is the authoritative contract for the recurring Thursday research task.

## Parent outcome

By Thursday morning, produce and email a broad, useful roundup of events and activities for the coming Friday through Sunday around ZIP code **20171**.

DONE means:

1. the coming Friday-Sunday dates are correctly identified in America/New_York;
2. current event information has been researched broadly;
3. material details have been verified from current sources where reasonably possible;
4. a structured package matching the schema below has been submitted as one OWNER-authored issue;
5. GitHub Actions validates and persists the report;
6. the Notes trigger advances only after persisted validation;
7. the Notes workflow sends the email.

The scheduled task should not write publication files directly.

## Research scope

Research in two explicit scopes:

### Local

Center this on **20171 / Herndon-Oak Hill-Chantilly** and the practical nearby orbit: Herndon, Reston, Chantilly, Centreville, Fairfax, Vienna, Great Falls, Sterling, Ashburn, McLean, Burke, and similarly close destinations.

### NoVA+

Search the broader Northern Virginia region as well, including **Leesburg, Manassas, Alexandria, Arlington, Falls Church, Woodbridge, Gainesville, Purcellville, Middleburg, Lorton, Occoquan**, and other worthwhile Northern Virginia destinations.

Also include a small number of **major worth-the-drive regional events** outside Northern Virginia when they are genuinely notable, especially large annual events such as:

- State Fair of Virginia
- Maryland Renaissance Festival
- major state/county fairs
- large seasonal festivals
- major museum, cultural, food, or holiday events
- unusually strong one-off events that justify the longer drive

Do not pad NoVA+ with ordinary distant events. Distance needs a reason.

Search deliberately across:

- festivals, fairs, street festivals, Oktoberfests, seasonal events
- farmers markets and special markets
- family / toddler-friendly activities
- libraries and community centers
- Fairfax County / Loudoun County / town and city programs
- parks, farms, nature centers, hikes, paddles, classes, ranger/naturalist programs
- museums, science centers, historic sites
- theater, concerts, live music, comedy
- sports and spectator events
- adult / date-night options
- free events
- indoor / rain-backup options
- unusual one-off events that would be easy to miss

The goal is broad coverage, not a tiny recommendation list. Do not omit good options merely because they are not one of the Best Bets.

Every event must be assigned a `scope`:

- `local` — practical nearby outing from 20171
- `nova_plus` — broader Northern Virginia or a major regional destination event

The website uses this field for the **Local** and **NoVA+** tabs. Prefer enough useful events in both scopes for the tabs to be meaningful, but do not force weak NoVA+ picks.

## Source quality

Prefer, in order:

1. official venue/event pages;
2. county, city, town, library, park, museum, or organizer pages;
3. primary ticket pages;
4. reputable local event calendars for discovery.

A calendar/aggregator can be used to discover an event, but verify important details against the organizer or venue when reasonably possible.

Do not invent price, time, address, age range, registration status, or availability.

If a detail cannot be verified, use concise language such as "Price not confirmed" rather than guessing.

## Weather

Include a structured Friday-Sunday forecast in `forecast` plus a short overall `weather_note`.

For each day, include:

- `date`
- `high_f`
- `low_f`
- `conditions`
- `notable` — one concise planning note, especially timing that matters (for example, "Rain after 2 PM", "Gusty after sunset", or "Dry through early afternoon")

For weather copy, **prefer brevity over grammatical completeness**. Telegraphic fragments are encouraged when clearer at a glance. Examples: "Rain after 2 PM", "Cooler, breezy", "Dry until evening", "Best outdoor day", "Wettest day". Avoid filler such as "there is a chance of", "it looks like", or "conditions are expected to" unless needed for accuracy.

Use a current, reputable forecast source and do not invent hour-specific timing. If the available forecast does not support a useful timing claim, keep `notable` broad and accurate.

The overall `weather_note` should also be short and scannable, preferably one compact sentence or a few terse clauses, for example:

> Fri best outdoors. Sat cooler. Sun wettest — keep an indoor backup.

## Best Bets

Choose roughly **4-6** when the event pool supports it.

Best Bets should be deliberately varied rather than six versions of the same outing. Include strong picks from both Local and NoVA+ when warranted. A useful mix might include:

- one strong family option;
- one free/community option;
- one date-night/adult option;
- one seasonal/signature event;
- one unusual or especially local option.

This is curation only. The full event list remains broad.

## Event representation

Represent one real-world event once, even when it runs on multiple days.

Use `dates` to place that event on every applicable day.

Example:

```json
{
  "id": "cox-farms-fall-festival",
  "title": "Cox Farms Fall Festival",
  "scope": "local",
  "dates": ["2026-10-02", "2026-10-03", "2026-10-04"],
  "time": "10 AM-6 PM",
  "venue": "Cox Farms",
  "address": "15621 Braddock Rd, Centreville, VA 20120",
  "area": "Centreville",
  "price": "$20 Friday; $30 Saturday-Sunday",
  "category": "Family / Fall",
  "summary": "A large fall farm festival where you can take a hayride, ride giant slides, visit farm animals, explore themed play areas and Foamhenge, and get seasonal food and cider.",
  "registration": "Online tickets required.",
  "buy_now": true,
  "source_url": "https://example.com/event"
}
```

The publisher generates `map_url` from `address`; do not supply it.

## Required package schema

Submit an issue body containing exactly one JSON package envelope:

```text
<!-- WEEKEND_ACTIVITIES_PACKAGE_JSON
{...compact valid JSON...}
WEEKEND_ACTIVITIES_PACKAGE_JSON -->
```

Top-level shape:

```json
{
  "package_version": 1,
  "report": {
    "title": "Weekend Activities",
    "generated_date": "YYYY-MM-DD",
    "generated_at": "ISO-8601 timestamp",
    "center_zip": "20171",
    "weekend_start": "YYYY-MM-DD",
    "weekend_end": "YYYY-MM-DD",
    "weather_note": "Short practical weekend weather note",
    "forecast": [
      {
        "date": "YYYY-MM-DD",
        "high_f": 72,
        "low_f": 54,
        "conditions": "Partly cloudy",
        "notable": "Dry through the afternoon; showers possible after 7 PM."
      },
      {
        "date": "YYYY-MM-DD",
        "high_f": 65,
        "low_f": 51,
        "conditions": "Cloudy",
        "notable": "Cooler all day."
      },
      {
        "date": "YYYY-MM-DD",
        "high_f": 63,
        "low_f": 52,
        "conditions": "Showers",
        "notable": "Rain most likely late morning through afternoon."
      }
    ],
    "best_bet_ids": ["event-id-1", "event-id-2"],
    "events": [
      {
        "id": "stable-short-id",
        "title": "Event title",
        "scope": "local",
        "dates": ["YYYY-MM-DD"],
        "time": "Human-readable time",
        "venue": "Venue name",
        "address": "Full geocodable street address",
        "area": "City / neighborhood",
        "price": "Free / price / concise range",
        "category": "Short category",
        "summary": "One or two sentences explaining what the event actually is and what someone can do, see, hear, eat, explore, or participate in there",
        "registration": "Registration/ticket note if applicable",
        "buy_now": false,
        "source_url": "https://current-source.example/event"
      }
    ]
  }
}
```

Required event fields:

- `id`
- `title`
- `scope` — `local` or `nova_plus`
- `dates` (one or more of the coming Friday/Saturday/Sunday)
- `address`
- `source_url`

Strongly preferred:

- `time`
- `venue`
- `area`
- `price`
- `category`
- `summary` — required in practice: write one or two concrete sentences that answer "what would I actually do there?" Avoid generic phrases such as "fun for the whole family" unless they are supported by specific activities.
- `registration`
- `buy_now`

Set `buy_now: true` only when advance action is materially useful: likely sellout, required registration, limited timed entry, or similar.

## GitHub issue handoff

Create one issue in:

`BigCatMellow/weekend_activites`

Title:

`[publish] Weekend Activities YYYY-MM-DD`

where the date is the Thursday publication date.

The issue must be created by the repository owner account so the workflow's OWNER gate passes.

Do not manually advance the Notes trigger.

## Failure behavior

If research succeeds but issue creation fails, return the researched report to the user and clearly state that publication/email did not complete.

If the GitHub workflow rejects the package, do not try to bypass validation by writing `data/latest.json` directly.

Correct the package and submit a new owner-authored publish issue.

If the report for the same upcoming weekend is already current and was already emailed, do not create a duplicate merely because the scheduler ran twice.
