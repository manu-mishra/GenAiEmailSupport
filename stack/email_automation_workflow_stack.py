import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs

import os.path as path

class EmailAutomationWorkflowStack(cdk.Stack):

    def __init__(self, scope: cdk.App, construct_id: str, support_email: str, human_workflow_email: str, kendra_index:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        human_topic = self.human_workflow_topic(human_workflow_email)
        
        email_handler_lambda = self.email_handler_lambda(human_topic, support_email,kendra_index)
        
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
        
    def email_handler_lambda(self, human_workflow_topic, support_email, kendra_index):        
        
        email_handler_lambda = lambda_.Function(
            self, "id_email_handler_lambda_fn",
            function_name="email-handler-lambda-fn",
            code = lambda_.Code.from_asset(path.join("./lambda", "email-handler-lambda")),
            handler = "email_handler_function.lambda_handler",
            runtime = lambda_.Runtime.PYTHON_3_11,
            timeout = cdk.Duration.minutes(1),
            environment={
                "HUMAN_WORKFLOW_SNS_TOPIC_ARN": human_workflow_topic.topic_arn,
                "SOURCE_EMAIL": support_email,
                "KENDRA_INDEX": kendra_index
            }
        )

        email_handler_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail"],
                resources=['*']
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
