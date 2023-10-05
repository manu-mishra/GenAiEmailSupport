from aws_cdk import core
# Import the stack classes from their respective modules
from email_automation_workflow_stack import EmailAutomationWorkflowStack
from workmailorg_project_stack import WorkMailOrgStack

class MainApp(core.App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Instantiate the stacks
        WorkMailOrgStack(self, "WorkMailOrgStack")
        EmailAutomationWorkflowStack(self, "EmailAutomationWorkflowStack")

app = MainApp()
app.synth()
