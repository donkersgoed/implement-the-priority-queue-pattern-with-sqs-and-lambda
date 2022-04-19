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


class MultiplePriorityFifoQueues(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        main_queue = sqs.Queue(
            scope=self,
            id="MainFifoQueue",
            removal_policy=RemovalPolicy.DESTROY,
            fifo=True,
            content_based_deduplication=True,
        )
        CfnOutput(scope=self, id="MultiMainFifoQueueUrl", value=main_queue.queue_url)

        medium_priority_queue = sqs.Queue(
            scope=self,
            id="MediumPriorityFifoQueue",
            removal_policy=RemovalPolicy.DESTROY,
            fifo=True,
            content_based_deduplication=True,
        )
        CfnOutput(
            scope=self,
            id="FifoMediumPriorityFifoQueueUrl",
            value=medium_priority_queue.queue_url,
        )

        high_priority_queue = sqs.Queue(
            scope=self,
            id="HighPriorityFifoQueue",
            removal_policy=RemovalPolicy.DESTROY,
            fifo=True,
            content_based_deduplication=True,
        )
        CfnOutput(
            scope=self,
            id="FifoHighPriorityFifoQueueUrl",
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
            batch_size=1,
            report_batch_item_failures=True,
        )

        lambda_.EventSourceMapping(
            scope=self,
            id="MediumPriorityQueueEventSourceMapping",
            target=processor_function.function,
            event_source_arn=medium_priority_queue.queue_arn,
            batch_size=1,
            report_batch_item_failures=True,
        )

        lambda_.EventSourceMapping(
            scope=self,
            id="HighPriorityQueueEventSourceMapping",
            target=processor_function.function,
            event_source_arn=high_priority_queue.queue_arn,
            batch_size=1,
            report_batch_item_failures=True,
        )
