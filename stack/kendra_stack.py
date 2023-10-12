import aws_cdk as cdk
from nested_stacks.kendra.kendra_index_stack import KendraIndexStack
from nested_stacks.kendra.kendra_ds_webcrawller_stack import KendraWebCrawlerStack
from nested_stacks.kendra.kendra_ds_bucket_stack import KendraS3DataSourceStack
from nested_stacks.kendra.kendra_sync_stack import KendraDataSyncStack


class KendraStack(cdk.NestedStack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        kendra_index_stack = KendraIndexStack(scope,"KendraIndex")
        self.kendra_index_id = kendra_index_stack.kendra_index_id

        kendra_data_sync_stack = KendraDataSyncStack(scope,"KendraDataSyncStack", self.kendra_index_id)

        kendra_web_crawler_stack = KendraWebCrawlerStack(scope,"KendraWebCrawler",self.kendra_index_id)
        kendra_s3_data_source_stack = KendraS3DataSourceStack(scope,"KendraS3DataSource",self.kendra_index_id)
        
        self.kendra_ds_id = kendra_web_crawler_stack.kendra_ds_id
        self.kendra_ds_web_id = kendra_web_crawler_stack.kendra_ds_id
        self.kendra_ds_s3_id = kendra_s3_data_source_stack.kendra_ds_id
        
