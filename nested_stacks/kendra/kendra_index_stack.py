import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kendra as kendra


class KendraIndexStack(cdk.NestedStack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Role for Kendra Index
        kendra_index_role = iam.Role(
            self, "app_kendra_index_role",
            assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"),
            role_name="docs_kendra_index_role",
            inline_policies={
                "docs_kendra_index_policy": iam.PolicyDocument(
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
            name=f"{self.stack_name}Index",
            edition="DEVELOPER_EDITION",
            role_arn=kendra_index_role.role_arn
        )
 
        self.kendra_index_id = kendra_index.ref
       
        self.kendra_index_output = cdk.CfnOutput(
            self, "kendra_index_id",
            value=kendra_index.ref
        )

