"""Module for the main ImplementThePriorityQueuePatternWithSqsAndLambda Stack."""

# Third party imports
from aws_cdk import (
    Stack,
)
from constructs import Construct

# Local application/library specific imports
from implement_the_priority_queue_pattern_with_sqs_and_lambda.simple_priority_queue import (
    SimplePriorityQueue,
)
from implement_the_priority_queue_pattern_with_sqs_and_lambda.fifo_priority_queue import (
    FifoPriorityQueue,
)
from implement_the_priority_queue_pattern_with_sqs_and_lambda.multiple_priority_queues import (
    MultiplePriorityQueues,
)
from implement_the_priority_queue_pattern_with_sqs_and_lambda.multiple_priority_fifo_queues import (
    MultiplePriorityFifoQueues,
)
from implement_the_priority_queue_pattern_with_sqs_and_lambda.fifo_priority_queue_concurrency_three import (
    FifoPriorityQueueConcurrencyThree,
)


class ImplementThePriorityQueuePatternWithSqsAndLambdaStack(Stack):
    """The ImplementThePriorityQueuePatternWithSqsAndLambda Stack."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Construct a new ImplementThePriorityQueuePatternWithSqsAndLambdaStack."""
        super().__init__(scope, construct_id, **kwargs)

        SimplePriorityQueue(scope=self, construct_id="SimplePriorityQueue")
        FifoPriorityQueue(scope=self, construct_id="FifoPriorityQueue")
        MultiplePriorityQueues(scope=self, construct_id="MultiplePriorityQueues")
        MultiplePriorityFifoQueues(
            scope=self, construct_id="MultiplePriorityFifoQueues"
        )
        FifoPriorityQueueConcurrencyThree(
            scope=self, construct_id="FifoPriorityQueueConcurrencyThree"
        )
