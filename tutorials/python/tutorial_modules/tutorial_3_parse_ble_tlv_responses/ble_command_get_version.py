# ble_command_get_version.py/Open GoPro, Version 1.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Thu, May  6, 2021 11:38:47 AM

import json
import enum
import asyncio
import logging
import argparse
from binascii import hexlify
from typing import Dict

from bleak import BleakClient

from tutorial_modules import GOPRO_BASE_UUID, connect_ble

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_arguments() -> str:
    parser = argparse.ArgumentParser(
        description="Connect to a GoPro camera via BLE, then get the Open GoPro version."
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


async def main():
    identifier = parse_arguments()

    # Synchronization event to wait until notification response is received
    event = asyncio.Event()

    # UUIDs to write to and receive responses from
    COMMAND_REQ_UUID = GOPRO_BASE_UUID.format("0072")
    COMMAND_RSP_UUID = GOPRO_BASE_UUID.format("0073")
    response_uuid = COMMAND_RSP_UUID

    client: BleakClient

    def notification_handler(handle: int, data: bytes) -> None:
        logger.info(f'Received response at {handle=}: {hexlify(data, ":")}')

        # If this is the correct handle and the status is success, the command was a success
        if client.services.characteristics[handle].uuid == response_uuid:
            # First byte is the length
            len = data[0]
            # Second byte is the ID
            command_id = data[1]
            # Third byte is the status
            status = data[2]
            index = 3
            params = []
            # Remaining bytes are individual values of (len...len bytes)
            while index <= len:
                param_len = data[index]
                index += 1
                params.append(data[index : index + param_len])
                index += param_len
            major, minor = params

            logger.info(f"Received a response to {command_id=} with {status=}: version={major[0]}.{minor[0]}")

        # Anything else is unexpected. This shouldn't happen
        else:
            logger.error("Unexpected response")

        # Notify the writer if we have received the entire response
        event.set()

    client = await connect_ble(notification_handler, identifier)

    # Write to command request UUID to get the Open GoPro Version
    logger.info("Getting the Open GoPro version...")
    event.clear()
    await client.write_gatt_char(COMMAND_REQ_UUID, bytearray([0x01, 0x51]))
    await event.wait()  # Wait to receive the notification response


if __name__ == "__main__":
    asyncio.run(main())
