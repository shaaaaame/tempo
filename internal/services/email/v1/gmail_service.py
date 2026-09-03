import logging 

from typing import Any

from googleapiclient.discovery import Resource

logger = logging.getLogger(__name__)

# Temporary History ID Storage
_last_processed_history_id: str | None = None
# SUPER TEMPORARY THIS WILL BE REMOVED THIS IS HERE FOR TESTING PURPOSES ONLY, IT SHOULD BE IN THE DB DONT WORRY


def get_gmail_service() -> Resource:
    """
    Return  an authed gmail API client object

    Should return something like this:
        service = build('gmail', 'v1', credentials=creds) <-   note to self service is API client object 
    """

    # TODO: Write OAuth Credential Loading Code

    raise NotImplementedError("Gmail service not implemented yet")

# def load_oauth_credentials() -> Any: ???

# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""
creds.json -> OAuth login -> token.json -> FastAPI ? -> Gmail API  
"""


def get_last_processed_history_id() -> str | None:
    """
    Return the last processed history ID
    """
    global _last_processed_history_id

    return _last_processed_history_id

def save_last_processed_history_id(history_id: str) -> None:
    """
    Save the last processed history ID
    """
    global _last_processed_history_id

    _last_processed_history_id = history_id

    logger.info(f"Saved last processed history ID: {history_id}")

def get_history_changes(service: Resource, user_id: str, start_history_id: str) -> list[dict]:
    """
    Get what has changed since a particular history ID. We want newly added messages.
    We have to loop through all pages of results until we reach the end so we don't accidentally miss some.

    Params:
        service: The Gmail API service object
        user_id: The user's email address. The special value "me"
            can be used to indicate the authenticated user.
        start_history_id: The history ID to start from
    
    Returns:
    list[dict]:
        A list of gmail history records 
    """

    history_records = []
    page_token = None

    while nextPageExist == True:
        request = service.users().history().list(userId=user_id, startHistoryId=start_history_id, pageToken=page_token) # Gmail history request

        response = request.execute() # Execute request to gmail

        history_records.extend(response.get("history", [])) # Add history records from page

        page_token = response.get("nextPageToken") # Check for next page

        if not page_token: # no more pages yipee
            nextPageExist = False

    return history_records

def extract_added_message_ids(history_records: list[dict[str,Any]],) -> set[str]:
    """
    Extract the message IDs of newly added messages from the history records.

    Params:
        history_records: A list of gmail history records
    Returns:
        list[str]: A list of message IDs of newly added messages
    """

    message_ids = set()

    # Loop through every history record

    for record in history_records:
        messages_added = record.get("messagesAdded", []) # get all messageAdded events, if none then return an empty list


        for added in messages_added:

            message = added.get("message", {}) # extract actual gmail message object

            message_id = message.get("id") # get unique gmail message id

            if message_id:
                message_ids.add(message_id)

    return message_ids


def get_message(service: Resource, message_id: str) -> dict[str, Any]:
    """
    Retrieve full gmail messaige given message ID

    Params:
        service: The Gmail API service object
        message_id: The unique ID of the message to retrieve
    
    Returns:
        dict[str, any]: The full gmail message object
    """
    message = service.users().messages().get(userId="me", id=message_id,format="full",).execute() # Get full message object

    return message

# Process a single emial

async def process_email(service: Resource, message: dict[str, Any]) -> None:
    """
    Process a single email message.

    Params:
        service: The Gmail API service object
        message: The full gmail message object
    """

    #email_data = parse_email(message) # Parse the email message
    # TODO implement parse logic somewhere

    logger.info(f"Processing email with ID: {message.get('id')}") # Log the processing of the email
    print(f"Processing email with ID: {message.get('id')}") # Print the processing of the email

# def parse_email(message: dict[str, Any]) -> dict[str, Any]:


async def process_gmail_notification(notification_history_id: str,) -> None:

    """
    Process a Gmail notification by retrieving the history changes since the last processed history ID,
    extracting the newly added message IDs, and processing each new email message.

    Params:
        notification_history_id: The history ID from the Gmail notification
    """
    logger.info(f"Processing Gmail notification with history ID: {notification_history_id}") # Log the processing of the notification

    service = get_gmail_service() # Get the Gmail API service object

    previous_history_id = get_last_processed_history_id() # Get the last processed history ID

    if previous_history_id is None:
        logger.info("No previous history ID found. Saving the current notification history ID and exiting.")
        save_last_processed_history_id(notification_history_id) # Save the current notification history ID
        return

    history_records = get_history_changes(service = service, start_history_id=previous_history_id) # Get history changes since the last processed history ID

    logger.info(f"Retrieved {len(history_records)} history records since history ID: {previous_history_id}") # Log the number of history records retrieved

    message_ids = extract_added_message_ids(history_records) # Extract the newly added message IDs

    logger.info(f"Extracted {len(message_ids)} newly added message IDs") # Log the number of newly added message IDs

    for message_id in message_ids:
        message = get_message(service, message_id) # Retrieve the full email message

        await process_email(service, message) # Process the email message

    save_last_processed_history_id(notification_history_id) # Save the current notification history ID

    logger.info(f"Finished processing Gmail notification with history ID: {notification_history_id}") # Log the completion of the notification processing
