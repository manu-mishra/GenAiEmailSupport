import boto3
import json
import os

index_id=os.getenv("KENDRA_INDEX")
knowledgebase_dataset_id = os.getenv("FAQ_DATASOURCE_REF").split('|')[0]
support_case_requirements_dataset_id = os.getenv("SUPPORT_DATASOURCE_REF").split('|')[0]
class KendraSearch:

    def __init__(self):
        self.kendra = boto3.client('kendra')

    def _search_kendra_index(self, index_id, query_text, dataset_id=None):
        # Define the query parameters
        query_params = {
            'IndexId': index_id,
            'QueryText': query_text,
            "PageSize": 3,
        }

        # If DataSetId is provided, add it as a filter
        if dataset_id:
            attribute_filter = {
                'AndAllFilters': [
                    {
                        'EqualsTo': {
                            'Key': '_data_source_id',
                            'Value': {
                                'StringValue': dataset_id
                            }
                        }
                    }
                ]
            }
            query_params['AttributeFilter'] = attribute_filter
        
        # Query the index
        response = self.kendra.retrieve(**query_params)
        data = response.get('ResultItems', [])
        filtered_data = [item for item in data if item.get('ScoreAttributes', {}).get('ScoreConfidence', '') in ["VERY_HIGH", "HIGH"]]
        return filtered_data

    def search_knowledge_base(self, query_text):
        data = self._search_kendra_index(index_id, query_text, knowledgebase_dataset_id)
        return self.transform_to_flat_format(data,"knowledgebase")

    def support_case_requirements(self, query_text):
        data = self._search_kendra_index(index_id, query_text, support_case_requirements_dataset_id)
        return self.transform_to_flat_format(data,"case_requirements")
        
    def transform_to_flat_format(self, data, tag):
        if not data:
            return f"<{tag}>No relevant information found <{tag}>"
        flat_format = f"<{tag}>\n"
    
        for entry in data:
            flat_format += "Document Title: " + entry['DocumentTitle'] + "\n"
            flat_format += "Document Excerpt: \n" + entry['Content'] +"\n\n" 
    
        flat_format += f"</{tag}>"
        return flat_format

