import aws_cdk as cdk
from aws_cdk import aws_logs
from aws_cdk import aws_lambda
from aws_cdk import aws_iam
from aws_cdk import custom_resources



class WorkMailOrgStack(cdk.Stack):

    def __init__(self, scope: cdk.App, construct_id: str, organization_name=None, user_name=None, password=None,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        orgname_param = cdk.CfnParameter(self, "OrganizationName", default=organization_name or 'my-sample-workmail-org')
        username_param = cdk.CfnParameter(self, "UserName", default=user_name or 'support')
        pass_param = cdk.CfnParameter(self, "PassWord", default=password or 'Welcome@123')

        create_workmail_org_lambda = aws_lambda.Function(
            self, "id_WorkMailOrg",
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            function_name='workmail_org_creation',
            code=aws_lambda.Code.from_asset("lambda/workmail-org-user-domain-lambda"),
            handler="workmailcreateorg.handler",
            environment={
                'work_org_name': orgname_param.value_as_string,
                'user_name': username_param.value_as_string,
                'password': pass_param.value_as_string
            }
        )

        policy = aws_iam.Policy(
            self, "id_workmail_custom_resource_lambda_policy",
            policy_name="workmail_custom_resource_lambda_policy",
            statements=[
                aws_iam.PolicyStatement(
                    actions=[
                        "workmail:*",
                        "ds:*",
                        "ses:*"
                    ],
                    resources=['*'],
                )
            ]
        )

        policy.attach_to_role(create_workmail_org_lambda.role)

        is_complete_org = aws_lambda.Function(
            self, "id_workmail_org_is_complete",
            function_name="resource-is-complete-lambda",
            code=aws_lambda.Code.from_asset(
                "lambda/workmail-org-user-domain-lambda"),
            handler="workmailcreateorg.is_complete",
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            environment={
                'work_org_name': orgname_param.value_as_string,
                'user_name': username_param.value_as_string,
                'password': pass_param.value_as_string
            }
        )

        is_complete_policy = aws_iam.Policy(
            self, "id_is_complete_custom_resource_lambda_policy",
            policy_name="is_complete_custom_resource_lambda_policy",
            statements=[
                aws_iam.PolicyStatement(
                    actions=[
                        "workmail:*",
                        "ds:*",
                        "ses:*"
                    ],
                    resources=['*'],
                )
            ]
        )

        is_complete_policy.attach_to_role(is_complete_org.role)

        create_workmail_org = custom_resources.Provider(
            self, "id_workmail_org",
            on_event_handler=create_workmail_org_lambda,
            is_complete_handler=is_complete_org,
            log_retention=aws_logs.RetentionDays.ONE_DAY
        )

        cdk.CustomResource(
            self, id="id_Work_Mail_Org_Resource",
            service_token=create_workmail_org.service_token
        )

        cdk.CfnOutput(
            self, "ResponseMessage",
            description="Your support email address is",
            value="Your support email address is:  " + username_param.value_as_string +
            '@'+orgname_param.value_as_string+'.awsapps.com'
        )
