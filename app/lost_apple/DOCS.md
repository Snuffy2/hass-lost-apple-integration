# Lost Apple Documentation

## Environment Variables

- `LOST_APPLE_DB` (default `/data/lost_apple.sqlite3`)
- `LOST_APPLE_PAIRING_TOKEN` (required by `build_app()`)
- `LOST_APPLE_OPTIONS_PATH` (default `/data/options.json` when the env override is not set)
- `LOST_APPLE_APP_VERSION` (default `0.1.0`)

The App resolves `pairing_token` from `LOST_APPLE_PAIRING_TOKEN` first and then falls back to the Home Assistant App options file. In a normal Home Assistant App install, that options file lives at `/data/options.json`.

## Setup

1. Install the App package in Home Assistant OS.
2. Open the App options and set a non-empty `pairing_token`.
3. Start the App and open `GET /setup` to reach the HACS install link.
4. Install the companion Lost Apple integration from HACS.
5. Add the integration in Home Assistant, then enter the App URL and the same pairing token.
6. Configure the Find My sources that the App should poll. The current implementation expects configured sources and uses `fetch_location()`; account discovery is not implemented yet.

## Routes

- `GET /setup`
  - Shows an installation/setup page and a link to install this repository in HACS.

- `GET /api/v1/health`
  - Returns runtime health and snapshot metadata.

- `GET /api/v1/devices`
  - Returns discovered snapshots.

## Startup

The App uses a factory-based uvicorn entrypoint that loads storage, initializes schema, and starts on `0.0.0.0:8099`.
