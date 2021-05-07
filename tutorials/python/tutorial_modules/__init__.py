# __init__.py/Open GoPro, Version 1.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Thu, May  6, 2021 11:38:53 AM

GOPRO_BASE_UUID = "b5f9{}-aa8d-11e3-9046-0002a5d5c51b"
GOPRO_BASE_URL = "http://10.5.5.9:8080/"

from tutorial_modules.tutorial_1_connect_ble.ble_connect import connect_ble
from tutorial_modules.tutorial_3_parse_ble_tlv_responses.ble_command_get_state import Response
from tutorial_modules.tutorial_5_connect_wifi.wifi_enable import enable_wifi
from tutorial_modules.tutorial_5_connect_wifi.wifi_enable_and_connect import connect_wifi
from tutorial_modules.tutorial_6_send_wifi_commands.wifi_command_get_media_list import get_media_list
