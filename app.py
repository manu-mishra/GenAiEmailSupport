import os
import aws_cdk as cdk
from stack.email_automation_workflow_stack import EmailAutomationWorkflowStack
from stack.workmailorg_project_stack import WorkMailOrgStack

        

app = cdk.App()
env = cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"]
    )
WorkMailOrgStack(app, "WorkMailOrgStack")
EmailAutomationWorkflowStack(app, "EmailAutomationWorkflowStack")
app.synth()
