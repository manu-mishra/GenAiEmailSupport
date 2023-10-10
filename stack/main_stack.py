import aws_cdk as cdk
from stack.email_automation_workflow_stack import EmailAutomationWorkflowStack
from stack.workmailorg_project_stack import WorkMailOrgStack
from stack.kendra_stack import KendraStack

class MainStackProps:
    def __init__(self, organization_name: str, user_name: str, password: str, human_workflow_email: str):
        self.organization_name = organization_name
        self.user_name = user_name
        self.password = password
        self.human_workflow_email = human_workflow_email


class MainStack(cdk.Stack):
    def __init__(self, scope: cdk.App, id: str, props: MainStackProps, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        kendra_stack = KendraStack(self, "Kendra")
        workmail_stack = WorkMailOrgStack(self, "WorkMailOrg", organization_name=props.organization_name, user_name=props.user_name, password=props.password)
        EmailAutomationWorkflowStack(self, "EmailAutomationWorkflow", support_email=workmail_stack.support_email_id, human_workflow_email=props.human_workflow_email, kendra_index=kendra_stack.kendra_index_id)
