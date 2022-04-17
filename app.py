#!/usr/bin/env python3

# Third party imports
import aws_cdk as cdk

# Local application/library specific imports
from implement_the_priority_queue_pattern_with_sqs_and_lambda.implement_the_priority_queue_pattern_with_sqs_and_lambda_stack import (
    ImplementThePriorityQueuePatternWithSqsAndLambdaStack,
)


app = cdk.App()
ImplementThePriorityQueuePatternWithSqsAndLambdaStack(
    scope=app,
    construct_id="ImplementThePriorityQueuePatternWithSqsAndLambdaStack",
)

app.synth()
