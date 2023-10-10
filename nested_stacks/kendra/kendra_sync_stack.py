import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kendra as kendra
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_events
from aws_cdk import aws_logs
from aws_cdk import aws_logs
from aws_cdk import aws_events_targets
from aws_cdk import custom_resources


class KendraDataSyncStack(cdk.NestedStack):

    def __init__(self, scope: cdk.App, construct_id: str, kendra_index: str, kendra_ds:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Role for DataSourceSync Lambda
        lambda_role = iam.Role(
            self, "data_source_sync_lambda_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            inline_policies={
                "data_source_sync_lambda_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=[f"arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index}*"],
                            actions=["kendra:*"]
                        )
                    ]
                )
            }
        )

        # Lambda function for DataSourceSync
        data_source_sync_lambda = _lambda.Function(
            self, "data_source_sync_lambda",
            function_name='data_source_sync_lambda',
            handler="data_source_sync_lambda.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            role=lambda_role,
            timeout=cdk.Duration.minutes(15),
            memory_size=1024,
            code=_lambda.Code.from_asset("lambda/kendra-indexing-lambda"),  # Ensure this path points to your Lambda function code
            environment={
                "INDEX_ID": kendra_index,
                "DS_ID": kendra_ds
            }
        )

        data_source_sync_lambda.add_permission(
            "AllowCloudFormationInvoke",
            action="lambda:InvokeFunction",
            principal=iam.ServicePrincipal("cloudformation.amazonaws.com")
        )

        # Create a daily EventBridge (CloudWatch Events) rule
        daily_rule = aws_events.Rule(
            self, "DailySyncRule",
            schedule=aws_events.Schedule.cron(minute='0', hour='0')  # Set to run daily at midnight
        )

        # Set the Lambda function as the target for the daily rule
        daily_rule.add_target(aws_events_targets.LambdaFunction(data_source_sync_lambda))

