import os
import json
import time
import boto3

MEDIUM_PRIORITY_QUEUE_URL = os.environ["MEDIUM_PRIORITY_QUEUE_URL"]
MEDIUM_PRIORITY_QUEUE_ARN = os.environ["MEDIUM_PRIORITY_QUEUE_ARN"]
HIGH_PRIORITY_QUEUE_URL = os.environ["HIGH_PRIORITY_QUEUE_URL"]
HIGH_PRIORITY_QUEUE_ARN = os.environ["HIGH_PRIORITY_QUEUE_ARN"]

sqs_client = boto3.client("sqs")


class PriorityMessageAvailable(Exception):
    pass


def event_handler(event, _context):
    returned_messages = []
    for record in event["Records"]:
        try:
            _process_record(record)
        except PriorityMessageAvailable:
            print("Yielding to priority message")
            returned_messages.append(record["messageId"])
        except Exception as exc:
            print(f"Got unexpected error: {type(exc)} - {exc}")
            returned_messages.append(record["messageId"])

    return {
        "batchItemFailures": [
            {"itemIdentifier": msg_id} for msg_id in returned_messages
        ]
    }


def _process_record(record):
    is_high_priority_msg = record["eventSourceARN"] == HIGH_PRIORITY_QUEUE_ARN
    is_medium_priority_msg = record["eventSourceARN"] == MEDIUM_PRIORITY_QUEUE_ARN
    is_main_msg = not is_medium_priority_msg and not is_high_priority_msg
    if is_medium_priority_msg:
        # Medium Prio messages should yield to High Prio messages
        _check_high_priority_messages_available()
    if is_main_msg:
        # Messages on the main queue should yield to High and Medium Prio messages
        _check_high_priority_messages_available()
        _check_medium_priority_messages_available()

    _handle_record(record)


def _check_high_priority_messages_available():
    return _check_priority_messages_available(queue_url=HIGH_PRIORITY_QUEUE_URL)


def _check_medium_priority_messages_available():
    return _check_priority_messages_available(queue_url=MEDIUM_PRIORITY_QUEUE_URL)


def _check_priority_messages_available(queue_url: str):
    response = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
        ],
    )
    for key, value in response["Attributes"].items():
        # Check if any attribute is > 0, raise error if
        # messages are in any way available on the priority queue.
        if int(value) > 0:
            raise PriorityMessageAvailable(key)


def _handle_record(record):
    body = record["body"]
    time.sleep(5)
    print(f"successfully processed {body}")
