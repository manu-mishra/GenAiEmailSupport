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

def lambda_handler(event, context):
    logger.info("Received event: %s" % json.dumps(event))
    
    request_type = event['RequestType']
    if request_type == 'Create': 
        return on_create(event)
    elif request_type == 'Update': 
        return on_update(event)
    elif request_type == 'Delete': 
        return on_delete(event)
    else:
        raise Exception("Invalid request type: %s" % request_type)

def is_complete(event):
    # Always return success as we do not need to wait for sync job to complete.
    return {
        'IsComplete': True
    }
def on_create(event):
    try:
        start_data_source_sync(DS_ID, INDEX_ID)
        response = {'PhysicalResourceId': 'KendraSyncResource'}
        return response
    except Exception as e:
        logger.error(f"Error processing the event: {e}")
        raise e

def on_update(event):
    # For now, treat update same as create
    return on_create(event)

def on_delete(event):
    # No specific delete logic as of now
    response = {
        'PhysicalResourceId': event.get('PhysicalResourceId', 'DefaultKendraSyncResourceId')
    }
    return response

def start_data_source_sync(dsId, indexId):
    logger.info(f"start_data_source_sync(dsId={dsId}, indexId={indexId})")
    resp = KENDRA.start_data_source_sync_job(Id=dsId, IndexId=indexId)
    logger.info(f"response:" + json.dumps(resp))
