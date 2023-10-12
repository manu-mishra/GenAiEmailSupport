import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kendra as kendra
from aws_cdk import aws_lambda as _lambda


class KendraWebCrawlerStack(cdk.NestedStack):

    def __init__(self, scope: cdk.App, construct_id: str,kendra_index_id: str,event_bus_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Role for Kendra Data Source (Web Crawler)
        kendra_ds_role = iam.Role(
            self, "kendra_ds_role",
            assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"),
            role_name="docs_ds_role",
            inline_policies={
                "docs_ds_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=[f"arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index_id}*"],
                            actions=["kendra:BatchPutDocument", "kendra:BatchDeleteDocument"]
                        )
                    ]
                )
            }
        )

        # Kendra Web Crawler Data Source
        kendra_docs_ds = kendra.CfnDataSource(
            self, "kendra_docs_ds",
            name="kendra_docs_ds",
            type="WEBCRAWLER",
            index_id=kendra_index_id,
            role_arn=kendra_ds_role.role_arn,
            data_source_configuration={
                "webCrawlerConfiguration": {
                    "urls": {
                        "siteMapsConfiguration": {
                            "siteMaps": [
                                "https://docs.aws.amazon.com/kendra/latest/dg/sitemap.xml",
                            ]
                        }
                    },
                    "urlInclusionPatterns": [
                        ".*https://docs.aws.amazon.com/kendra/.*",
                    ]
                }
            }
        )

        # Use the provided event bus ARN to define an EventBridge rule
        event_bus = events.EventBus.from_event_bus_arn(self, "ExistingEventBus", event_bus_arn)

        # Define an EventBridge rule to send an event to the event bus when the Kendra data source is created
        data_source_created_rule = events.Rule(
            self, "DataSourceCreatedRule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(
                source=['aws.kendra'],
                detail_type=['Kendra DataSource Status'],
                detail={
                    'State': ['CREATED'],
                    'Id': [kendra_docs_ds.ref]  # Use the data source ID from the Kendra data source
                }
            )
        )
        # Specify custom input for the Lambda function
        custom_input = events.RuleTargetInput.from_object({
            'index_id': kendra_index_id,
            'data_source_id': kendra_docs_ds.ref
        })
        # Add a target for the rule (your Lambda function) with the custom input
        data_source_created_rule.add_target(targets.LambdaFunction(self.start_sync_lambda, event=custom_input))


        # Outputs for the CDK stack
        self.kendra_ds_id = kendra_docs_ds.ref
        
        self.kendra_ds_output = cdk.CfnOutput(
            self, "kendra_ds_id",
            value=kendra_docs_ds.ref
        )
