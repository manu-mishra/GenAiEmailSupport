import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kendra as kendra
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deploy

class KendraS3DataSourceStack(cdk.NestedStack):

    def __init__(self, scope: cdk.App, construct_id: str, kendra_index_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket with a unique name
        data_bucket = s3.Bucket(self, "DataBucket",
                                removal_policy=cdk.RemovalPolicy.DESTROY,
                                auto_delete_objects=True)

        # Upload a file to the S3 bucket
        s3_deploy.BucketDeployment(self, "DeployData",
                                   destination_bucket=data_bucket,
                                   sources=[s3_deploy.Source.asset('./data')],
                                   destination_key_prefix="referencedata")  # Optional prefix in S3

        # Role for Kendra Data Source (S3)
        kendra_ds_role = iam.Role(
            self, "kendra_reference_ds_role",
            assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"),
            role_name="kendra_reference_ds_role",
            inline_policies={
                "docs_ds_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=[f"arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index_id}*"],
                            actions=["kendra:BatchPutDocument", "kendra:BatchDeleteDocument"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            resources=[data_bucket.bucket_arn, f"{data_bucket.bucket_arn}/*"],
                            actions=["s3:GetObject", "s3:ListBucket"]
                        )
                    ]
                )
            }
        )

        # Kendra S3 Data Source
        kendra_s3_ds = kendra.CfnDataSource(
            self, "kendra_s3_ds",
            name="kendra_s3_ds",
            type="S3",
            index_id=kendra_index_id,
            role_arn=kendra_ds_role.role_arn,
            data_source_configuration={
                "s3Configuration": {
                    "bucketName": data_bucket.bucket_name,
                    "inclusionPrefixes": [
                        "referencedata/"  # Include files with this prefix
                    ]
                }
            }
        )

        # Outputs for the CDK stack
        self.kendra_ds_id = kendra_s3_ds.ref
        
        self.kendra_ds_output = cdk.CfnOutput(
            self, "kendra_ds_id",
            value=kendra_s3_ds.ref
        )
