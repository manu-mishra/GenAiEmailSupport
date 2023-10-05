import boto3
import logging
import os
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns_client = boto3.resource('sns')
ses_client = boto3.client('ses')

human_workflow_topic_arn = os.getenv("HUMAN_WORKFLOW_SNS_TOPIC_ARN")
source_email = os.getenv("SOURCE_EMAIL")

if not human_workflow_topic_arn:
    raise ValueError("env variable HUMAN_WORKFLOW_SNS_TOPIC is required.")  
    
if not source_email:
    raise ValueError("env variable SOURCE_EMAIL is required.")     

human_workflow_topic = sns_client.Topic(human_workflow_topic_arn)

def validate_params(event):  
    email = event['email']
    meta = event['meta']
   
    if not email:
        raise ValueError("No email found.")
    if not meta:
        raise ValueError("No metadata found.")
   
    email_body = email['body']
    email_subject = email['subject']
    user_email = email['to']
    message_source = meta['source']
    message_id = meta['id']
   
    if not email_body:
        raise ValueError("No email body found.")
    if not email_subject:
        raise ValueError("No email subject found.")
    if not user_email:
        raise ValueError("No user email found.")
    if not message_source:
        raise ValueError("No email source found.")
    if not message_id:
        raise ValueError("No email source id found.")
      
    return email, meta

def send_response_email(to_email, subject, body):
    response = ses_client.send_email(
        Source=source_email,
        Destination={
            'ToAddresses': [to_email]
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    
    logger.info(f"Sent email. Response: {response}")

def lambda_handler(event, context):
    email, meta = validate_params(event)   
   
    logger.info(f"Received email with content {email['body']}")
   
    send_response_email(email['to'], "Re: " + email['subject'], "Thanks, email received.")
      
    return {"message": "Response email sent."}
