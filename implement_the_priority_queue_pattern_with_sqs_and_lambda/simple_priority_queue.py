# Third party imports
from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    aws_sqs as sqs,
    aws_lambda as lambda_,
)
from constructs import Construct

# Local application/library specific imports
from implement_the_priority_queue_pattern_with_sqs_and_lambda.lambda_function import (
    LambdaFunction,
)


class SimplePriorityQueue(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        main_queue = sqs.Queue(
            scope=self, id="MainQueue", removal_policy=RemovalPolicy.DESTROY
        )
        CfnOutput(scope=self, id="SimpleMainQueueUrl", value=main_queue.queue_url)

        priority_queue = sqs.Queue(
            scope=self, id="PriorityQueue", removal_policy=RemovalPolicy.DESTROY
        )
        CfnOutput(
            scope=self, id="SimplePriorityQueueUrl", value=priority_queue.queue_url
        )

        processor_function = LambdaFunction(
            scope=self,
            construct_id="ProcessorFunction",
            code=lambda_.Code.from_asset("lambda/functions/queue_processor"),
            reserved_concurrent_executions=1,
            environment={
                "PRIORITY_QUEUE_URL": priority_queue.queue_url,
                "PRIORITY_QUEUE_ARN": priority_queue.queue_arn,
            },
            timeout=Duration.seconds(10),
        )
        main_queue.grant_consume_messages(processor_function.function)
        priority_queue.grant_consume_messages(processor_function.function)

        lambda_.EventSourceMapping(
            scope=self,
            id="MainQueueEventSourceMapping",
            target=processor_function.function,
            event_source_arn=main_queue.queue_arn,
            max_batching_window=Duration.seconds(1),
            batch_size=1,
            report_batch_item_failures=True,
        )

        lambda_.EventSourceMapping(
            scope=self,
            id="PriorityQueueEventSourceMapping",
            target=processor_function.function,
            event_source_arn=priority_queue.queue_arn,
            max_batching_window=Duration.seconds(1),
            batch_size=1,
            report_batch_item_failures=True,
        )
