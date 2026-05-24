# Lost Apple Integration

![Lost Apple logo](docs/assets/lost-apple-logo.svg)

`hass-lost-apple-integration` provides the Lost Apple Integration for Home Assistant.

The integration pairs to the separate Lost Apple App through a local bearer token and exposes Apple Find My device trackers plus diagnostics in Home Assistant. The Lost Apple App owns Apple authentication, local storage, polling, and setup.

## Install

1. Install and configure the Lost Apple App from `https://github.com/snuffy2/hass-lost-apple-app`.
2. Add `https://github.com/snuffy2/hass-lost-apple-integration` as a HACS custom repository with category `Integration`.
3. Install the Lost Apple Integration from HACS.
4. Add the Lost Apple Integration in Home Assistant and enter the Lost Apple App URL and pairing token.

## Privacy

Apple credentials, session material, and polling state stay inside the Lost Apple App's local storage. The Lost Apple Integration stores only the local Lost Apple App URL and pairing token. Diagnostics redact token-like and credential-like fields before export.

## Supported Devices

The current supported path is official Apple Find My devices exposed by the Lost Apple App API. Manual key imports, OpenHaystack accessories, and custom non-Apple accessories are not part of the current supported path.

## Status

This project is in initial development.
