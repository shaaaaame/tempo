import json
import logging

import base64 # Dude why is it encoded in Base64 lmao

from fastapi import APIRouter, Request, Response, HTTPException, status

logger = logging.getLogger(__name__) # 2🟣 -> 🪵-> 💀❌💀❌💀❌💀❌💀❌💀❌💀❌💀❌💀❌💀❌🗼

router = APIRouter(
    prefix="/v1/gmail/pubsub",
    tags=["Gmail Pub/Sub"],
)

def decode_pubsub_message(pubsub_body: dict) -> dict:
    """
    Decode the Pub/Sub message from Gmail. The data field within the message is base64 which is weird.

    We need to decode it and then parse the JSON to get the actual message content.

    Pubby 🐶

    Params:
    pubsub_body (dict): The body of the Pub/Sub message received from Gmail.

    Returns:
    dict: The decoded message content as a dictionary.

    Raises:
    ValueError: If the message cannot be decoded or parsed, or if pubusb message missing.
    """

    message = pubsub_body.get("message")

    if not message:
        raise ValueError("Pub/Sub message is missing the 'message' field.")

    encoded_data = message.get("data")

    if not encoded_data:
        raise ValueError("Pub/Sub message is missing the 'data' field.")

    try:
        # Decode the base64 encoded data
        decoded_bytes = base64.b64decode(encoded_data)
        decoded_str = decoded_bytes.decode("utf-8")

        gmail_notif = json.loads(decoded_str)

        return gmail_notif
    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to decode or parse the Pub/Sub message: {e}") from e


