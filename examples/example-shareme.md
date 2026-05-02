# SHAREME — `weather-bot`

> Companion document to `SKILL.md`. Read this **before** installing or running the skill.
>
> *This is a synthetic example for the SHAREME standard. The `weather-bot` skill is fictional.*

## 1. What this is

A Claude Code skill that fetches weather forecasts for a given location, renders them as a markdown briefing, and saves them under `${BRIEFING_ROOT}/`.

## 2. What I can do

- **Fetch current weather** — pulls current conditions from a public weather API.
  Example: `/weather-bot:brief Milan`
- **Render multi-day forecast** — formats up to 7-day forecast as markdown with emoji icons.
  Example: `/weather-bot:brief Milan --days 5`
- **Save briefings to disk** — writes timestamped markdown to a configured folder.
  Example: output `${BRIEFING_ROOT}/2026-05-02_milan.md`

## 3. What I do NOT do

- No historical weather lookups (only current and forecast)
- No automatic location detection (city name must be passed explicitly)
- No alerting or notifications (output is files only)
- No multi-language output (English only)

## 4. What I do behind the scenes

- **Network calls**: HTTPS GET to `api.open-meteo.com` (free public API, no auth)
- **File system writes**: creates files in `${BRIEFING_ROOT}/` only
- **External services**: open-meteo.com (no account required, rate-limited to 10k requests/day)
- **Persistent state**: none (stateless between runs)
- **Tools used**: Python `requests` library, no shell commands, no MCP servers

## 5. What is author-specific

| What | Where | Why | How to change |
|---|---|---|---|
| `${BRIEFING_ROOT}` = `~/Documents/weather/` | `scripts/save_briefing.py:12` | Author writes daily weather logs to that folder | Pick any writable path; pass via `--output-dir` flag or edit the constant |
| `default_units = "metric"` | `scripts/fetch_weather.py:8` | Author is in Europe | Change to `"imperial"` for °F, mph |
| Locale `en_US` for date formatting | `scripts/render_briefing.py:21` | Author wanted English output | Replace with your locale string |

## 6. What you might do with it

- **Daily team standup briefing** — pipe the markdown into a Slack message instead of saving to disk
- **Travel planning** — call it for multiple destinations and diff the outputs
- **Dashboard data source** — use the JSON output (with `--format json`) to feed a home dashboard
- **Triggered alerts** — wrap it in a cron and grep for `"warning"` in the output to send conditional notifications
- **Localized briefings** — adapt the rendering layer to produce non-English output for your team

## 7. Onboarding questions

Answer these before touching code:

1. Where do you want briefings saved? What is your `${BRIEFING_ROOT}`?
2. Which units do you want — metric or imperial?
3. Do you need stateful behaviour (e.g., diff against yesterday's forecast)? If yes, this skill does not provide it.
4. Is calling a public US-hosted weather API acceptable under your data policy?
5. How frequently will you run it? (Stay under 10k requests/day or rate limits will hit.)

## 8. Technical prerequisites

- **Runtime**: Python 3.11+
- **OS**: any (tested on macOS and Linux)
- **Dependencies**: `requests >= 2.31`, `pyyaml >= 6.0`
- **OS permissions**: write access to `${BRIEFING_ROOT}`
- **Accounts and tokens**: none (open-meteo is keyless)

## 9. Cyber and security warnings

- Sends location names in plain HTTPS to `api.open-meteo.com`. If your locations are sensitive (e.g., undisclosed travel), do not use a public API.
- Output files are written unencrypted to disk. If your filesystem is shared, consider encrypted storage.
- No input sanitization on the location string beyond URL-encoding. Do not pipe untrusted input into the city argument without validation.

## 10. How to adapt

1. Read sections 4 and 5 of this file
2. Answer the onboarding questions in section 7
3. Install prerequisites: `pip install -r scripts/requirements.txt`
4. Set your `${BRIEFING_ROOT}` — either via `--output-dir` or by editing `scripts/save_briefing.py:12`
5. Choose units (`metric` / `imperial`) in `scripts/fetch_weather.py:8`
6. Grep for `TODO_ADAPT:` markers and address each one
7. Test: run `/weather-bot:brief London` and verify output file is created

## 11. License and disclaimer

- **License**: MIT
- **Warranty**: none. Forecast accuracy is whatever open-meteo.com decides.
- **Attribution**: not required for forks, but a link back is appreciated
- **Contact**: GitHub issues at `github.com/<fictional-author>/weather-bot`

---

## Optional sections

### Provenance

Written for personal daily-briefing automation. Not designed for production use, redundancy, or mission-critical scheduling.

### Alternatives

- `wttr.in` (curl-based, no skill needed)
- Commercial weather APIs (AccuWeather, Tomorrow.io) for higher accuracy and SLA

### Roadmap

Possible future direction: support for multiple locations in a single run, optional alerting layer. No commitment to deliver.
