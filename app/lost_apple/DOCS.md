# Lost Apple Documentation

## Environment Variables

- `LOST_APPLE_DB` (default `/data/lost_apple.sqlite3`)
- `LOST_APPLE_PAIRING_TOKEN` (required by `build_app()`)
- `LOST_APPLE_APP_VERSION` (default `0.1.0`)

## Routes

- `GET /setup`
  - Shows an installation/setup page and a link to install this repository in HACS.

- `GET /api/v1/health`
  - Returns runtime health and snapshot metadata.

- `GET /api/v1/devices`
  - Returns discovered snapshots.

## Startup

The App uses a factory-based uvicorn entrypoint that loads storage, initializes schema, and starts on `0.0.0.0:8099`.
