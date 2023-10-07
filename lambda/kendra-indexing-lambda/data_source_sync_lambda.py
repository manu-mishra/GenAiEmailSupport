import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INDEX_ID = os.environ['INDEX_ID']
DS_ID = os.environ['DS_ID']
AWS_REGION = os.environ['AWS_REGION']
KENDRA = boto3.client('kendra')
CLOUDFORMATION = boto3.client('cloudformation')

def start_data_source_sync(dsId, indexId):
    logger.info(f"start_data_source_sync(dsId={dsId}, indexId={indexId})")
    resp = KENDRA.start_data_source_sync_job(Id=dsId, IndexId=indexId)
    logger.info(f"response:" + json.dumps(resp))

def lambda_handler(event, context):
    logger.info("Received event: %s" % json.dumps(event))
    start_data_source_sync(DS_ID, INDEX_ID)
    signal_cloudformation(event, 'SUCCESS')

def signal_cloudformation(event, status):
    response_data = {}
    physicalResourceId = context.log_stream_name if 'PhysicalResourceId' not in event else event['PhysicalResourceId']

    try:
        CLOUDFORMATION.signal_resource(
            StackName=event['StackId'],
            LogicalResourceId=event['LogicalResourceId'],
            UniqueId=physicalResourceId,
            Status=status
        )
    except Exception as e:
        logger.error(f"Failed signaling CloudFormation: {e}")
