# SPDX-FileCopyrightText: 2020 Brent Rubell, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

from os import getenv

import adafruit_connection_manager
import adafruit_requests
import board
import busio
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut

from adafruit_oauth2 import OAuth2

# Get WiFi details and Google keys, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
google_client_id = getenv("google_client_id")
google_client_secret = getenv("google_client_secret")

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(ssid, password)
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)

# Initialize a requests session
pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
requests = adafruit_requests.Session(pool, ssl_context)

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
