"""Module for the main ImplementThePriorityQueuePatternWithSqsAndLambda Stack."""

# Third party imports
from aws_cdk import (
    Stack,
)
from constructs import Construct


class ImplementThePriorityQueuePatternWithSqsAndLambdaStack(Stack):
    """The ImplementThePriorityQueuePatternWithSqsAndLambda Stack."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Construct a new ImplementThePriorityQueuePatternWithSqsAndLambdaStack."""
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
