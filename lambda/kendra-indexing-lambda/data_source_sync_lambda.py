import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INDEX_ID = os.environ['INDEX_ID']
DS_ID = os.environ['DS_ID'].split('|')[0]  # extracting the correct ID part
AWS_REGION = os.environ['AWS_REGION']
KENDRA = boto3.client('kendra')
CLOUDFORMATION = boto3.client('cloudformation')

def start_data_source_sync(dsId, indexId):
    logger.info(f"start_data_source_sync(dsId={dsId}, indexId={indexId})")
    resp = KENDRA.start_data_source_sync_job(Id=dsId, IndexId=indexId)
    logger.info(f"response:" + json.dumps(resp))

def lambda_handler(event, context):
    try:
        logger.info("Received event: %s" % json.dumps(event))
    
        if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            start_data_source_sync(DS_ID, INDEX_ID)
            signal_cloudformation(event, 'SUCCESS', context)
        elif event['RequestType'] == 'Delete':
            # Handle cleanup if necessary, then signal SUCCESS
            signal_cloudformation(event, 'SUCCESS', context)
    except Exception as e:
        logger.error(f"Error processing the event: {e}")
        signal_cloudformation(event, 'FAILURE', context)

def signal_cloudformation(event, status, context):
    response_data = {}
    physicalResourceId = event.get('PhysicalResourceId', context.log_stream_name)

    try:
        CLOUDFORMATION.signal_resource(
            StackName=event['StackId'],
            LogicalResourceId=event['LogicalResourceId'],
            UniqueId=physicalResourceId,
            Status=status
        )
    except Exception as e:
        logger.error(f"Failed signaling CloudFormation: {e}")
