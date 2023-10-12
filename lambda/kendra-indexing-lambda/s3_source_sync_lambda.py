import json
import logging
import os
import boto3
import os.path as path

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    kendra_client = boto3.client('kendra')
    logger.info("Received event: %s", json.dumps(event))
    kendra_index_id=os.getenv("KENDRA_INDEX")
    kendra_data_source_id=os.getenv("KENDRA_DATA_SOURCE_ID")
    try:
        # Extract the Kendra Index ID and Data Source ID from the event
        index_id = event['index_id']
        data_source_id = event['data_source_id']

        # Start a synchronization job for the given Kendra Index and Data Source
        response = kendra_client.start_data_source_sync_job(
            Id=kendra_data_source_id,
            IndexId=kendra_index_id
        )

        return {
            'statusCode': 200,
            'body': response
        }
    except Exception as e:
        logger.error(f"Error starting sync job for Index ID: {index_id}, Data Source ID: {data_source_id}. Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Failed to start sync job: {str(e)}"
        }
