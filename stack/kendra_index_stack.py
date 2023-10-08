import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kendra as kendra
from aws_cdk import aws_lambda as _lambda

class KendraStack(cdk.Stack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Role for Kendra Index
        kendra_index_role = iam.Role(
            self, "kendra_index_role",
            assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"),
            role_name=f"{cdk.Aws.STACK_NAME}_docs_kendra_index_role",
            inline_policies={
                f"{cdk.Aws.STACK_NAME}_docs_kendra_index_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                            actions=["cloudwatch:PutMetricData"],
                            conditions={"StringEquals": {"cloudwatch:namespace": "Kendra"}}
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                            actions=["logs:DescribeLogGroups"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=[f"arn:aws:logs:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:log-group:/aws/kendra/*"],
                            actions=["logs:CreateLogGroup"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=[f"arn:aws:logs:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:log-group:/aws/kendra/*:log-stream:*"],
                            actions=["logs:DescribeLogStreams", "logs:CreateLogStream", "logs:PutLogEvents"]
                        )
                    ]
                )
            }
        )

        # Kendra Index
        kendra_index = kendra.CfnIndex(
            self, "docs_kendra_index",
            name=f"{cdk.Aws.STACK_NAME}Index",
            edition="DEVELOPER_EDITION",
            role_arn=kendra_index_role.role_arn
        )

        # Outputs for the CDK stack
        kendra_index_output = cdk.CfnOutput(
            self, "kendra_index_id",
            value=kendra_index.ref
        )
        self.kendra_index_id = kendra_index.ref

        # Role for Kendra Data Source (Web Crawler)
        kendra_ds_role = iam.Role(
            self, "kendra_ds_role",
            assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"),
            role_name=f"{cdk.Aws.STACK_NAME}-docs_ds_role",
            inline_policies={
                f"{cdk.Aws.STACK_NAME}_docs_ds_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=[f"arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index.ref}*"],
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
            index_id=kendra_index.ref,
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
                            resources=[f"arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index.ref}*"],
                            actions=["kendra:*"]
                        ),
                        iam.PolicyStatement( 
                        effect=iam.Effect.ALLOW,
                        resources=[f"arn:aws:cloudformation:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:stack/{cdk.Aws.STACK_NAME}/*"],
                        actions=["cloudformation:SignalResource"]
                        )
                    ]
                )
            }
        )

        # Lambda function for DataSourceSync
        data_source_sync_lambda = _lambda.Function(
            self, "data_source_sync_lambda",
            handler="data_source_sync_lambda.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            role=lambda_role,
            timeout=cdk.Duration.minutes(15),
            memory_size=1024,
            code=_lambda.Code.from_asset("lambda/kendra-indexing-lambda"), 
            environment={
                "INDEX_ID": kendra_index.ref,
                "DS_ID": kendra_docs_ds.ref
            }
        )

        # Custom resource for DataSourceSync
        data_source_sync = cdk.CustomResource(
            self, "DataSourceSync",
            service_token=data_source_sync_lambda.function_arn
        )
        data_source_sync.node.add_dependency(kendra_index)
        data_source_sync.node.add_dependency(kendra_docs_ds)

