# Hass Lost Apple

`hass-lost-apple` provides a Home Assistant App and HACS-managed custom integration for official Apple Find My devices using FindMy.py with local anisette.

The App owns local storage, polling, and the setup page. The Home Assistant integration pairs to the App through a local bearer token and exposes device trackers plus diagnostics.

## Install

1. On Home Assistant OS, add `https://github.com/snuffy2/hass-lost-apple` as a third-party App repository.
2. Install the Lost Apple App.
3. Set a non-empty `pairing_token` in the App options. The App reads that value from Home Assistant's app options file at `/data/options.json`.
4. Open the App setup page and use the HACS link to install the Lost Apple integration.
5. Add the Lost Apple integration in Home Assistant and enter the App URL and pairing token.
6. Configure Find My sources on the setup page via `POST /setup/sources` by importing official FindMy accessory JSON exports.
   The App currently does not auto-enumerate devices from the Apple session.

## Privacy

Apple credentials, session material, and polling state stay inside the App's local storage. The Home Assistant integration stores only the local App URL and pairing token. Diagnostics redact token-like and credential-like fields before export.

## Supported Devices

The current supported path is official Apple Find My devices that can be represented as configured sources and fetched through `fetch_location()`. Manual key imports, OpenHaystack accessories, and custom non-Apple accessories are not part of the current supported path.

## Status

This project is in initial development.
