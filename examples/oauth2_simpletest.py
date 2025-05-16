# SPDX-FileCopyrightText: 2020 Brent Rubell, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

import ssl
from os import getenv

import adafruit_requests
import socketpool
import wifi

from adafruit_oauth2 import OAuth2

# Get WiFi details and Google keys, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
google_client_id = getenv("google_client_id")
google_client_secret = getenv("google_client_secret")

print(f"Connecting to {ssid}")
wifi.radio.connect(ssid, password)
print(f"Connected to {ssid}")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())


# Set scope(s) of access required by the API you're using
scopes = ["email"]

# Initialize an OAuth2 object
google_auth = OAuth2(requests, google_client_id, google_client_secret, scopes)

# Request device and user codes
# https://developers.google.com/identity/protocols/oauth2/limited-input-device#step-1:-request-device-and-user-codes
google_auth.request_codes()

# Display user code and verification url
# NOTE: If you are displaying this on a screen, ensure the text label fields are
# long enough to handle the user_code and verification_url.
# Details in link below:
# https://developers.google.com/identity/protocols/oauth2/limited-input-device#displayingthecode
print("1) Navigate to the following URL in a web browser:", google_auth.verification_url)
print("2) Enter the following code:", google_auth.user_code)

# Poll Google's authorization server
print("Waiting for browser authorization...")
if not google_auth.wait_for_authorization():
    raise RuntimeError("Timed out waiting for browser response!")

print("Successfully authorized with Google!")
print("-" * 40)
print("\tAccess Token:", google_auth.access_token)
print("\tAccess Token Scope:", google_auth.access_token_scope)
print("\tAccess token expires in: %d seconds" % google_auth.access_token_expiration)
print("\tRefresh Token:", google_auth.refresh_token)
print("-" * 40)

# Refresh an access token
print("Refreshing access token...")
if not google_auth.refresh_access_token():
    raise RuntimeError("Unable to refresh access token - has the token been revoked?")
print("-" * 40)
print("\tNew Access Token: ", google_auth.access_token)
print("-" * 40)
