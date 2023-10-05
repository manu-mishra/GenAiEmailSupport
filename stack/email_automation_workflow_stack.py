from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    core
)

import os.path as path

class EmailAutomationWorkflowStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        human_topic = self.human_workflow_topic()
        
        # Renamed method invocation
        email_handler_lambda = self.email_handler_lambda(human_topic)
        
        workmail_lambda = self.workmail_integration_lambda(email_handler_lambda)

    def workmail_integration_lambda(self, email_handler_lambda):        
        workmail_lambda = lambda_.Function(
            self, "id_workmail_integration_lambda_lambda_fn", 
            function_name="workmail-integration-lambda-fn",
            code = lambda_.Code.from_asset(path.join("./lambda", "workmail-integration-lambda")),
            handler = "lambda_function.lambda_handler",
            runtime = lambda_.Runtime.PYTHON_3_8,
            timeout = core.Duration.minutes(1),
            environment={
                "EMAIL_HANDLER_LAMBDA_FN_NAME" : email_handler_lambda.function_name  # Renamed environment variable
            }
        )
        
        current_region = self.region        
        principal = iam.ServicePrincipal("workmail.{}.amazonaws.com".format(current_region))        
        workmail_lambda.grant_invoke(principal)
        
        workmail_lambda.add_to_role_policy(
            iam.PolicyStatement(
                        actions = [
                            "workmailmessageflow:GetRawMessageContent",
                        ],
                        resources= [ '*' ]
                    )
            
        )
        
        email_handler_lambda.grant_invoke(workmail_lambda)        
        return workmail_lambda
        
    def email_handler_lambda(self, human_workflow_topic):        
        support_email = core.CfnParameter(self, "supportEmail").value_as_string
        
        email_handler_lambda = lambda_.Function(
            self, "id_email_handler_lambda_fn",  # Changed the identifier
            function_name="email-handler-lambda-fn",  # Changed the function name
            code = lambda_.Code.from_asset(path.join("./lambda", "email-handler-lambda")),  # Ensure your Lambda file name matches this
            handler = "lambda_function.lambda_handler",
            runtime = lambda_.Runtime.PYTHON_3_8,
            timeout = core.Duration.minutes(1),
            environment={
                "HUMAN_WORKFLOW_SNS_TOPIC_ARN" : human_workflow_topic.topic_arn,
                "SOURCE_EMAIL" : support_email
            }
        )

        # Changed the SES permission from "SendTemplatedEmail" to "SendEmail"
        email_handler_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions = ["ses:SendEmail"],
                resources= [ '*' ]
            )
        )
        
        human_workflow_topic.grant_publish(email_handler_lambda)
        return email_handler_lambda
        
    def human_workflow_topic(self):        
        human_workflow_email = core.CfnParameter(self, "humanWorkflowEmail").value_as_string
        
        topic =  sns.Topic(
            self, "id_human_workflow_topic",
            display_name="Email-classification-human-workflow-topic",
            topic_name="Email-classification-human-workflow-topic"
        )
        
        topic.add_subscription(subs.EmailSubscription(human_workflow_email))
        return topic
