# Lost Apple App

This folder contains the Home Assistant App packaging metadata and execution files for `hass-lost-apple`.

The app exposes:
- `GET /api/v1/health` and `/api/v1/devices` for integration polling,
- `GET /setup` for interactive setup and a quick HACS install link.

Setup now includes guided Apple login and 2FA endpoints:
- `POST /setup/login`
- `GET /setup/2fa/methods`
- `POST /setup/2fa/request`
- `POST /setup/2fa/submit`
- `POST /setup/sources` for official FindMy accessory payload import.

The app is built around a simple FastAPI server that expects a non-empty pairing token passed as
`LOST_APPLE_PAIRING_TOKEN`.
