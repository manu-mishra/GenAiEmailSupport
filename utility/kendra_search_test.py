import boto3
import json

def search_kendra_index(index_id, query_text, dataset_id=None):
    # Create a Kendra client
    kendra = boto3.client('kendra')
    
    # Define the query parameters
    query_params = {
        'IndexId': index_id,
        'QueryText': query_text
    }

    # If DataSetId is provided, add it as a filter
    if dataset_id:
        attribute_filter = {
            'AndAllFilters': [
                {
                    'EqualsTo': {
                        'Key': 'DataSetId',
                        'Value': {
                            'StringValue': dataset_id
                        }
                    }
                }
            ]
        }
        query_params['AttributeFilter'] = attribute_filter
    
    # Query the index
    response = kendra.query(**query_params)

    # Print the entire document (result item) as JSON with all properties
    for item in response.get('ResultItems', []):
        print(json.dumps(item, indent=4))
        print('-----')

def list_all_datasets(index_id):
    # Create a Kendra client
    kendra = boto3.client('kendra')

    # List all data sources for the given index
    response = kendra.list_data_sources(IndexId=index_id)
    
    # Print dataset names and their IDs
    for item in response.get('SummaryItems', []):
        print(f"Name: {item['Name']}, ID: {item['Id']}")

if __name__ == "__main__":
    INDEX_ID = "YOUR_KENDRA_INDEX_ID"  # Replace with your Kendra Index ID
    QUERY_TEXT = "YOUR_SEARCH_QUERY"   # Replace with your search query
    
    # Uncomment the following line and replace YOUR_DATASET_ID if you want to filter by DataSetId
    # DATASET_ID = "YOUR_DATASET_ID"
    # search_kendra_index(INDEX_ID, QUERY_TEXT, DATASET_ID)
    
    # Uncomment the following line to search without a DataSetId filter
    # search_kendra_index(INDEX_ID, QUERY_TEXT)

    # Uncomment the following line to list all datasets with their IDs
    # list_all_datasets(INDEX_ID)
