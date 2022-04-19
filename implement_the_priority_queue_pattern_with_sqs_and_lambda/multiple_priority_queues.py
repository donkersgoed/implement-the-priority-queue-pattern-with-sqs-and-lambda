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


class MultiplePriorityQueues(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        main_queue = sqs.Queue(
            scope=self,
            id="MainQueue",
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(scope=self, id="MultiMainQueueUrl", value=main_queue.queue_url)

        medium_priority_queue = sqs.Queue(
            scope=self,
            id="MediumPriorityQueue",
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(
            scope=self,
            id="MediumPriorityQueueUrl",
            value=medium_priority_queue.queue_url,
        )

        high_priority_queue = sqs.Queue(
            scope=self,
            id="HighPriorityQueue",
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(
            scope=self,
            id="HighPriorityQueueUrl",
            value=high_priority_queue.queue_url,
        )

        processor_function = LambdaFunction(
            scope=self,
            construct_id="ProcessorFunction",
            code=lambda_.Code.from_asset("lambda/functions/multi_queue_processor"),
            reserved_concurrent_executions=1,
            environment={
                "MEDIUM_PRIORITY_QUEUE_URL": medium_priority_queue.queue_url,
                "MEDIUM_PRIORITY_QUEUE_ARN": medium_priority_queue.queue_arn,
                "HIGH_PRIORITY_QUEUE_URL": high_priority_queue.queue_url,
                "HIGH_PRIORITY_QUEUE_ARN": high_priority_queue.queue_arn,
            },
            timeout=Duration.seconds(10),
        )
        main_queue.grant_consume_messages(processor_function.function)
        medium_priority_queue.grant_consume_messages(processor_function.function)
        high_priority_queue.grant_consume_messages(processor_function.function)

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
            id="MediumPriorityQueueEventSourceMapping",
            target=processor_function.function,
            event_source_arn=medium_priority_queue.queue_arn,
            max_batching_window=Duration.seconds(1),
            batch_size=1,
            report_batch_item_failures=True,
        )

        lambda_.EventSourceMapping(
            scope=self,
            id="HighPriorityQueueEventSourceMapping",
            target=processor_function.function,
            event_source_arn=high_priority_queue.queue_arn,
            max_batching_window=Duration.seconds(1),
            batch_size=1,
            report_batch_item_failures=True,
        )
