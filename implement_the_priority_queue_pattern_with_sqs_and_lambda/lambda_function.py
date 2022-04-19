"""Module for the Lambda Function L3 Pattern."""


# Third party imports
from typing import Optional
from aws_cdk import (
    Duration,
    Fn,
    RemovalPolicy,
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as lambda_,
)
from constructs import Construct


class LambdaFunction(Construct):
    """CDK Construct for a Lambda Function and its supporting resources."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        code: lambda_.Code,
        environment: Optional[dict] = None,
        reserved_concurrent_executions: Optional[Duration] = None,
        timeout: Optional[Duration] = None,
        **kwargs,
    ) -> None:
        """Construct a new LambdaFunction."""
        super().__init__(scope, construct_id, **kwargs)

        if not environment:
            environment = {}

        # Create a role for the Lambda Function
        function_role = iam.Role(
            scope=self,
            id="FunctionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        optional_params = {}
        if reserved_concurrent_executions is not None:
            optional_params[
                "reserved_concurrent_executions"
            ] = reserved_concurrent_executions
        if timeout is not None:
            optional_params["timeout"] = timeout

        # Create the Lambda Function
        self.function = lambda_.Function(
            scope=self,
            id="Function",
            role=function_role,
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=code,
            handler="index.event_handler",
            environment=environment,
            **optional_params,
        )

        # Create the Lambda Function Log Group
        function_log_group = logs.LogGroup(
            scope=self,
            id="FunctionLogGroup",
            retention=logs.RetentionDays.ONE_MONTH,
            log_group_name=Fn.sub(
                "/aws/lambda/${Function}",
                {"Function": self.function.function_name},
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Give Lambda permission to write log streams, but not to create log groups
        log_policy = iam.Policy(
            scope=self,
            id="FunctionLogPolicy",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=["logs:PutLogEvents", "logs:CreateLogStream"],
                        effect=iam.Effect.ALLOW,
                        resources=[function_log_group.log_group_arn],
                    ),
                ]
            ),
        )
        log_policy.attach_to_role(function_role)
