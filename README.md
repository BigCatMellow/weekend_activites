# Weekend Activities

## Website

The repository includes a responsive `index.html` that reads directly from `data/latest.json`. The Thursday publishing workflow therefore updates the email data and the website from the same source automatically.

Expected GitHub Pages URL after Pages is enabled:

`https://bigcatmellow.github.io/weekend_activites/`

### One-time GitHub Pages setup

In this repository:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select **main** and **/(root)**.
4. Click **Save**.

No separate build step is required.

The site includes:

- weekend dates and weather note;
- a compact local / nova+ scope selector in the hero;
- a Best Bets section within each scope when applicable;
- Friday, Saturday, and Sunday sections;
- concrete event descriptions;
- date, time, location, and cost;
- Plan Ahead warnings;
- one-click Google Maps directions;
- links to the official event source;
- responsive fall styling for desktop and mobile.


A weekly Thursday roundup of things to do around ZIP code **20171** (Herndon / Oak Hill / Chantilly / Fairfax County), delivered by email through the existing `BigCatMellow/Notes` SMTP setup.

## How it works

1. A scheduled ChatGPT task researches the coming Friday-Sunday.
2. It submits one owner-authored GitHub issue titled:
   `[publish] Weekend Activities YYYY-MM-DD`
3. GitHub Actions validates the package and writes:
   - `data/latest.json`
   - `data/archive/YYYY-MM-DD.json`
4. Each event gets a one-click Google Maps directions URL generated from its address. No Google Maps API key is required.
5. After the persisted JSON is re-read and validated, the workflow updates:
   `BigCatMellow/Notes/data/weekend-activities-trigger.txt`
6. That push triggers the existing Notes email infrastructure, which sends a clean HTML + plain-text email.

## Email structure

The email is intentionally simple:

- Weekend dates and short weather note
- **Best bets**
- Friday
- Saturday
- Sunday
- Each event includes:
  - title
  - time
  - location
  - price
  - short description
  - registration/ticket warning when relevant
  - **Directions** link
  - **Event details** link

## Search scope

The weekly research is split into two scopes:

- **local** — the practical 20171 orbit: Herndon, Reston, Chantilly, Centreville, Fairfax, Vienna, Great Falls, Sterling, Ashburn, McLean, Burke, and similar close destinations.
- **nova+** — broader Northern Virginia, including Leesburg, Manassas, Alexandria, Arlington, Falls Church, Woodbridge, Gainesville, Purcellville, Middleburg, Lorton, Occoquan, and similar destinations.

nova+ also includes a small number of major **worth-the-drive** regional events outside Northern Virginia when the event itself justifies the trip, such as the State Fair of Virginia, Maryland Renaissance Festival, major fairs, and large seasonal or cultural festivals.

Each event carries a `scope` field (`local` or `nova_plus`) used by the website scope selector and email grouping.

Coverage should include:

- festivals, fairs, markets, and seasonal events
- family / toddler-friendly activities
- parks and nature programs
- libraries and community events
- live music and theater
- museums and cultural events
- sports
- adult / date-night options
- free events
- indoor/rain backups

The goal is breadth first, then a short curated **Best Bets** section.

## One-time setup

The email credentials already live in `BigCatMellow/Notes`, so they do **not** need to be copied here.

This repository needs one Actions secret:

`NOTES_TRIGGER_TOKEN`

Use a fine-grained GitHub token with:

- Repository access: **Only selected repositories → BigCatMellow/Notes**
- Repository permission: **Contents: Read and write**
- No other write permissions

Add it under:

**weekend_activites → Settings → Secrets and variables → Actions → New repository secret**

If the token used by Morning Edition was saved somewhere safe, the same token can be reused here because it has the same narrow purpose. GitHub does not let you reveal an existing stored secret, so create a new token if you no longer have the value.

## Manual test

After `NOTES_TRIGGER_TOKEN` is configured:

1. Let the Thursday scheduled task create the publish issue, or create a valid owner-authored publish issue manually using `SCHEDULER_HANDOFF.md`.
2. Confirm the **Publish Weekend Activities request** workflow succeeds and writes `data/latest.json`.
3. In `BigCatMellow/Notes`, the **Weekend Activities email** workflow should run automatically when its trigger file changes; it can also be run manually after `data/latest.json` exists.

## Failure behavior

- Invalid or stale packages do not publish.
- Events are deduplicated by stable event id; one event can cover multiple weekend dates.
- Events without a usable address or source URL are rejected.
- Publication is committed before the email trigger is touched.
- The committed file is re-read and validated before the trigger advances.
- If `NOTES_TRIGGER_TOKEN` is missing or invalid, the issue remains open and the workflow comments with a failure notice.


## Design direction

Use a **Playskool-style design mentality**: make important information obvious, friendly, chunky, and easy to scan without making the site childish.

Practical rules:

- prefer clear visual hierarchy over subtlety;
- use consistent SVG glyphs for functional metadata and actions; reserve emoji mainly for expressive cues such as weather or scope;
- make weather, dates, times, costs, directions, and plan-ahead warnings identifiable at a glance;
- keep controls large and plainly labeled;
- use short plain-language descriptions;
- favor warm seasonal color and subtle alternating row/card bands over decorative artwork;
- use banding to help the eye track groups without creating strong visual stripes;
- keep ornamentation minimal unless it clearly improves scanning;
- use Inter for body, controls, and metadata, with Roboto Slab reserved for display hierarchy;
- preserve accent scarcity: strong rust/olive accents should indicate hierarchy, selection, or meaningful structure rather than decorate every element;
- use restrained card elevation and let spacing, borders, header color, and alignment carry most grouping;
- keep local / nova+ as a compact segmented filter with explicit pressed state and keyboard-visible focus;
- distinguish loading, empty, and failure states and provide a direct retry path for load failures.
