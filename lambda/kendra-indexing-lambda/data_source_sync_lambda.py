import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INDEX_ID = os.environ['INDEX_ID']
DS_ID = os.environ['DS_ID'].split('|')[0]  # extracting the correct ID part
KENDRA = boto3.client('kendra')

def lambda_handler(event, context):
    logger.info("Received event: %s" % json.dumps(event))
    start_data_source_sync(DS_ID, INDEX_ID)

def start_data_source_sync(dsId, indexId):
    try:
        logger.info(f"Starting data source sync (dsId={dsId}, indexId={indexId})")
        resp = KENDRA.start_data_source_sync_job(Id=dsId, IndexId=indexId)
        logger.info(f"Response: " + json.dumps(resp))
    except Exception as e:
        logger.error(f"Error starting data source sync: {e}")
        raise e
