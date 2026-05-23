# Security

Lost Apple stores Apple credentials, session material, and polling state inside the Home Assistant App data volume. The companion Home Assistant integration stores only the local App URL and pairing token.

Do not log or export the following values in plain text:

- Apple IDs
- passwords
- two-factor codes
- session cookies
- session tokens
- pairing tokens
- raw Apple response payloads

Diagnostics redaction should keep credential-like fields out of exported payloads. The current redaction list includes `pairing_token`, `token`, `password`, `apple_id`, and `session`.

The App setup page is intended for Home Assistant Ingress where available. The local API used by the integration requires a bearer pairing token on every request under `/api/v1/`.
