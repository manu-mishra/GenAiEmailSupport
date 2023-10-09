import os
import aws_cdk as cdk
from stack.main_stack import MainStack
from stack.main_stack import MainStackProps

app = cdk.App()

props = MainStackProps(
    organization_name=app.node.try_get_context('OrganizationName'),
    user_name=app.node.try_get_context('UserName'),
    password=app.node.try_get_context('PassWord'),
    human_workflow_email=app.node.try_get_context('HumanWorkflowEmail')
)

# Deploy Main Stack
MainStack(app, "GenAiEmailSupportStack", props=props)

app.synth()

