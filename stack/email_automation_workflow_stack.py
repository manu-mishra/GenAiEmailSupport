import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs

import os.path as path

class EmailAutomationWorkflowStack(cdk.NestedStack):

    def __init__(self, scope: cdk.App, construct_id: str, support_email: str, human_workflow_email: str, kendra_index:str,kendra_web_datasource_ref:str,kendra_bucket_datasource_ref:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        human_topic = self.human_workflow_topic(human_workflow_email)
        
        email_handler_lambda = self.email_handler_lambda(human_topic, support_email,kendra_index,kendra_web_datasource_ref,kendra_bucket_datasource_ref)
        
        workmail_lambda = self.workmail_integration_lambda(email_handler_lambda)
       


    def workmail_integration_lambda(self, email_handler_lambda):        
        workmail_lambda = lambda_.Function(
            self, "id_workmail_integration_lambda_lambda_fn", 
            function_name="workmail-integration-lambda-fn",
            code = lambda_.Code.from_asset(path.join("./lambda", "workmail-integration-lambda")),
            handler = "workmail_integration_function.lambda_handler",
            runtime = lambda_.Runtime.PYTHON_3_11,
            timeout = cdk.Duration.minutes(1),
            environment={
                "EMAIL_HANDLER_LAMBDA_FN_NAME": email_handler_lambda.function_name
            }
        )
        
        current_region = self.region        
        principal = iam.ServicePrincipal(f"workmail.{current_region}.amazonaws.com")        
        workmail_lambda.grant_invoke(principal)
        
        workmail_lambda.add_to_role_policy(
            iam.PolicyStatement(
                        actions=["workmailmessageflow:GetRawMessageContent"],
                        resources=['*']
                    )
        )
        
        email_handler_lambda.grant_invoke(workmail_lambda)        
        return workmail_lambda
        
    def email_handler_lambda(self, human_workflow_topic, support_email, kendra_index,kendra_web_datasource_ref,kendra_bucket_datasource_ref):        
        
        email_handler_lambda = lambda_.Function(
            self, "id_email_handler_lambda_fn",
            function_name="email-handler-lambda-fn",
            code = lambda_.Code.from_asset(
                path.join("./lambda", "email-handler-lambda"),
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        'bash', '-c', 
                        'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
                    ],
                }
            ),
            handler = "email_handler_function.lambda_handler",
            runtime = lambda_.Runtime.PYTHON_3_11,
            timeout = cdk.Duration.minutes(5),
            environment={
                "HUMAN_WORKFLOW_SNS_TOPIC_ARN": human_workflow_topic.topic_arn,
                "SOURCE_EMAIL": support_email,
                "KENDRA_INDEX": kendra_index,
                "FAQ_DATASOURCE_REF": kendra_web_datasource_ref,
                "SUPPORT_DATASOURCE_REF": kendra_bucket_datasource_ref
            }
        )

        email_handler_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail"],
                resources=['*']
            )
        )
        # Grant permissions for all 'Kendra' actions 
        kendra_index_arn = f"arn:aws:kendra:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:index/{kendra_index}"
        email_handler_lambda.add_to_role_policy(
        iam.PolicyStatement(
            actions=[
                "kendra:*",
            ],
            resources=[kendra_index_arn]
            )
        )
        # Grant permissions for all 'bedrock' actions
        email_handler_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:*"],
                resources=["*"]
            )
        )
        
        human_workflow_topic.grant_publish(email_handler_lambda)
        return email_handler_lambda
        
    def human_workflow_topic(self, human_workflow_email):        
        
        topic = sns.Topic(
            self, "id_human_workflow_topic",
            display_name="Email-classification-human-workflow-topic",
            topic_name="Email-classification-human-workflow-topic"
        )
        
        topic.add_subscription(subs.EmailSubscription(human_workflow_email))
        return topic
