import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kendra as kendra
from aws_cdk import aws_lambda as _lambda
from aws_cdk import custom_resources

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
        # Outputs for the CDK stack
        self.kendra_index_output = cdk.CfnOutput(
            self, "kendra_index_id",
            value=kendra_index.ref
        )
        
        self.kendra_ds_output = cdk.CfnOutput(
            self, "kendra_ds_id",
            value=kendra_docs_ds.ref
        )
