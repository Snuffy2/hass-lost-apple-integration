# Lost Apple App

This folder contains the Home Assistant App packaging metadata and execution files for `hass-lost-apple`.

The app exposes:
- `GET /api/v1/health` and `/api/v1/devices` for integration polling,
- `GET /setup` for interactive setup and a quick HACS install link.

The app is built around a simple FastAPI server that expects a non-empty pairing token passed as
`LOST_APPLE_PAIRING_TOKEN`.
