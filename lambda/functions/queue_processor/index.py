import os
import time
import boto3

PRIORITY_QUEUE_URL = os.environ["PRIORITY_QUEUE_URL"]
PRIORITY_QUEUE_ARN = os.environ["PRIORITY_QUEUE_ARN"]

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
    """Handle the record or raise an error when higher priority messages are available."""
    is_priority_msg = record["eventSourceARN"] == PRIORITY_QUEUE_ARN
    if not is_priority_msg:
        _check_priority_messages_available()

    _handle_record(record)


def _check_priority_messages_available():
    response = sqs_client.get_queue_attributes(
        QueueUrl=PRIORITY_QUEUE_URL,
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
