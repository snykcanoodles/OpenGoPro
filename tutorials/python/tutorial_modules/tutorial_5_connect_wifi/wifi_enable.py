# wifi_enable.py/Open GoPro, Version 1.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Thu, May  6, 2021 11:38:49 AM

import bleak
import time
import asyncio
import logging
import argparse
from binascii import hexlify
from typing import Tuple

from bleak import BleakClient

from tutorial_modules import GOPRO_BASE_UUID, connect_ble

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_arguments() -> str:
    parser = argparse.ArgumentParser(
        description="Connect to a GoPro camera via BLE, get WiFi info, and enable WiFi."
    )
    parser.add_argument(
        "-i",
        "--identifier",
        type=str,
        help="Last 4 digits of GoPro name to scan for. If not used, first discovered GoPro will be connected to",
        default=None,
    )
    args = parser.parse_args()

    return args.identifier


async def enable_wifi(identifier: str = None) -> Tuple[str, str]:
    """Connect to a GoPro via BLE, find its WiFi AP SSID and password, and enable its WiFI AP

    If identifier is None, the first discovered GoPro will be connected to.

    Args:
        identifier (str, optional): Last 4 digits of GoPro serial number. Defaults to None.

    Returns:
        Tuple[str, str]: ssid, password
    """
    # Synchronization event to wait until notification response is received
    event = asyncio.Event()

    # UUIDs to write to and receive responses from, and read from
    COMMAND_REQ_UUID = GOPRO_BASE_UUID.format("0072")
    COMMAND_RSP_UUID = GOPRO_BASE_UUID.format("0073")
    WIFI_AP_SSID_UUID = GOPRO_BASE_UUID.format("0002")
    WIFI_AP_PASSWORD_UUID = GOPRO_BASE_UUID.format("0003")

    client: BleakClient

    def notification_handler(handle: int, data: bytes) -> None:
        logger.info(f'Received response at {handle=}: {hexlify(data, ":")}')

        # If this is the correct handle and the status is success, the command was a success
        if client.services.characteristics[handle].uuid == COMMAND_RSP_UUID and data[2] == 0x00:
            logger.info("Command sent successfully")
        # Anything else is unexpected. This shouldn't happen
        else:
            logger.error("Unexpected response")

        # Notify the writer
        event.set()

    client = await connect_ble(notification_handler, identifier)

    # Read from WiFi AP SSID UUID
    logger.info("Reading the WiFi AP SSID")
    ssid = await client.read_gatt_char(WIFI_AP_SSID_UUID)
    ssid = ssid.decode()
    logger.info(f"SSID is {ssid}")

    # Read from WiFi AP Password UUID
    logger.info("Reading the WiFi AP password")
    password = await client.read_gatt_char(WIFI_AP_PASSWORD_UUID)
    password = password.decode()
    logger.info(f"Password is {password}")

    # Write to the Command Request UUID to enable WiFi
    logger.info("Enabling the WiFi AP")
    event.clear()
    await client.write_gatt_char(COMMAND_REQ_UUID, bytearray([0x03, 0x17, 0x01, 0x01]))
    await event.wait()  # Wait to receive the notification response
    logger.info("WiFi AP is enabled")

    return ssid, password


async def main():
    identifier = parse_arguments()

    await enable_wifi(identifier)


if __name__ == "__main__":
    asyncio.run(main())
