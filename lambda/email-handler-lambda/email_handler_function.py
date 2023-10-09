# lambda_handler.py

import boto3
import logging
import os
import datetime
from chain_logic import generate_response 

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


def send_response_email(to_email, subject, response_body, original_email_body, original_sender):
    out_of_context_tag = "##outofcontext##"
    if out_of_context_tag in response_body:
        response_body = response_body.replace(out_of_context_tag, "")
        notification_message = f"User's email: {original_email_body}\n\nResponse sent: {response_body}"
        human_workflow_topic.publish(Message=notification_message)
        logger.info(notification_message)

    # Get the current date and time
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format the original email content to look like a typical email client reply
    original_message_format = (
        f"\n\nFrom: {original_sender}\n"
        f"Sent: {current_date}\n"
        f"To: {source_email}\n"
        f"Subject: {subject}\n\n"
        f"{original_email_body}"
    )
    
    final_body = response_body + original_message_format
        
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
                    'Data': final_body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    logger.info(f"Sent email. Response: {response}")



def lambda_handler(event, context):
    email, meta = validate_params(event)   
    logger.info(f"Received email with content {email['body']}")

    # Use the chain to generate a response
    response_text = generate_response(email['body'])

    send_response_email(email['to'], "Re: " + email['subject'], response_text, email['body'],email['to'])
      
    return {"message": "Response email sent."}
