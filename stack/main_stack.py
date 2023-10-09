import aws_cdk as cdk
from email_automation_workflow_stack import EmailAutomationWorkflowStack
from workmailorg_project_stack import WorkMailOrgStack
from kendra_stack import KendraStack

class MainStackProps:
    def __init__(self, organization_name: str, user_name: str, password: str, human_workflow_email: str):
        self.organization_name = organization_name
        self.user_name = user_name
        self.password = password
        self.human_workflow_email = human_workflow_email


class MainStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, props: MainStackProps, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Instantiate nested stacks here
        kendra_stack = KendraStack(self, "KendraStack")
        workmail_stack = WorkMailOrgStack(self, "WorkMailOrgStack", organization_name=props.organization_name, user_name=props.user_name, password=props.password)
        EmailAutomationWorkflowStack(self, "EmailAutomationWorkflowStack", support_email=workmail_stack.support_email_id, human_workflow_email=props.human_workflow_email, kendra_index=kendra_stack.kendra_index_id)
