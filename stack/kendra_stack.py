import aws_cdk as cdk
from nested_stacks.kendra.kendra_index_stack import KendraIndexStack
from nested_stacks.kendra.kendra_ds_webcrawller_stack import KendraWebCrawlerStack


class KendraStack(cdk):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        kendra_index_stack = KendraIndexStack(scope,"KendraIndexStack")
        self.kendra_index_id = kendra_index_stack.kendra_index_id
        
        kendra_web_crawler_stack = KendraWebCrawlerStack(scope,"KendraWebCrawler",self.kendra_index_id)
        
        self.kendra_ds_id = kendra_web_crawler_stack.kendra_ds_id
        
