import os
import aws_cdk as cdk
from stack.email_automation_workflow_stack import EmailAutomationWorkflowStack
from stack.workmailorg_project_stack import WorkMailOrgStack
from stack.kendra_index_stack import KendraStack

        

app = cdk.App()
env = cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"]
    )
# parse parameters
organization_name = app.node.try_get_context('OrganizationName')
user_name = app.node.try_get_context('UserName')
password = app.node.try_get_context('PassWord')
human_workflow_email = app.node.try_get_context('HumanWorkflowEmail')

# Deploy Stacks
kendra_index_stack = KendraStack(app,"KendraStack")
workmail_stack = WorkMailOrgStack(app, "WorkMailOrgStack", organization_name=organization_name, user_name=user_name, password=password)
EmailAutomationWorkflowStack(app, "EmailAutomationWorkflowStack", support_email=workmail_stack.support_email_id, human_workflow_email=human_workflow_email, kendra_index = kendra_index_stack.kendra_index_id)
app.synth()
