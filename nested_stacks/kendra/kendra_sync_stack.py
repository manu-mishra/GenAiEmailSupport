import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kendra as kendra
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_events as events
from aws_cdk import aws_logs
from aws_cdk import aws_events_targets as targets
import os.path as path

class KendraDataSyncStack(cdk.NestedStack):

    def __init__(self, scope: cdk.App, construct_id: str, kendra_index_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function to start Kendra sync job
        self.start_sync_lambda = _lambda.Function(
            self, 'StartSyncLambda',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='data_source_sync_lambda.handler',
            code=_lambda.Code.from_asset(path.join("./lambda", "kendra-indexing-lambda"))
        )

        # Grant permissions to the Lambda function to start Kendra sync job
        self.start_sync_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[
                f'arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index_id}',
                f'arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index_id}/data-source/*'
            ],
            actions=['kendra:StartDataSourceSyncJob']
        ))

        # Create a custom EventBridge event bus
        event_bus = events.EventBus(self, "KendraDataSourceEventBus")

        # Define an EventBridge rule to trigger the Lambda function when a Kendra data source is created
        data_source_created_rule = events.Rule(
            self, "DataSourceCreatedRule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(
                source=['aws.kendra'],
                detail_type=['Kendra DataSource Status'],
                detail={
                    'State': ['CREATED', 'UPDATED']
                }
            )
        )

        # Add the Lambda function as the target for the rule
        data_source_created_rule.add_target(targets.LambdaFunction(self.start_sync_lambda))

        # Expose the Lambda function's ARN for use in other stacks
        self.lambda_arn_output = cdk.CfnOutput(
            self, "LambdaArn",
            value=self.start_sync_lambda.function_arn
        )

       
