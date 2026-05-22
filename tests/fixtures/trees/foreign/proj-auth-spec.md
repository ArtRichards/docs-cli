# Authentication Subsystem

The authentication subsystem handles login, session issuance, and token
refresh for every client. It is the single gatekeeper in front of the
application; nothing reaches a protected endpoint without a valid session
token minted here.

## Login flow

A client posts credentials to `/auth/login`. The handler verifies them
against the user store, mints a signed session token, and returns it in the
response body. The token carries the subject id and an expiry timestamp.

## Token refresh

A near-expiry token may be exchanged for a fresh one at `/auth/refresh`
without re-presenting credentials, provided the original is still inside its
grace window.
