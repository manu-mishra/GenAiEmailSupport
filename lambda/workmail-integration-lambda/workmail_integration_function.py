# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import email
import os
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

workmail = boto3.client('workmailmessageflow')
handler_lambda = boto3.client('lambda')

# Changed the env variable name to EMAIL_HANDLER_LAMBDA_FN_NAME
handler_lambda_function_name = os.getenv("EMAIL_HANDLER_LAMBDA_FN_NAME")

if not handler_lambda_function_name:
   raise ValueError("EMAIL_HANDLER_LAMBDA_FN_NAME env variable required.")
   
def start_handler_flow(body, subject, from_, ref_id):
   
   event = {
     "email" : {
      "body": body,   
      "subject": subject,
      "to" : from_
     },
     "meta" : {
         "source" : "workmail",
         "id" : ref_id
     }
   }
   
   handler_lambda.invoke(
      FunctionName=handler_lambda_function_name,
      InvocationType='Event',
      Payload=json.dumps(event)
   )

def lambda_handler(event, context):
    
    msg_id = event['messageId']
    logger.info("An Email received with messageId : [{}]".format(msg_id))
    
    raw_msg = workmail.get_raw_message_content(messageId=msg_id)
    parsed_email = email.message_from_bytes(raw_msg['messageContent'].read())
    logger.info("Email content is : {}".format(parsed_email))
    
    from_ = parsed_email['From']
    subject = parsed_email['Subject']

    if parsed_email.is_multipart():
         for part in parsed_email.walk():
             content_type = part.get_content_type()
             content_disposition = str(part.get_content_disposition())
             if content_type == 'text/plain' and 'attachment' not in content_disposition:
                 text_content = part.get_payload(decode=True)
                 text_charset = part.get_content_charset()
                 break
    else:
         text_content = parsed_email.get_payload(decode=True)
         text_charset = parsed_email.get_content_charset()

    logger.info("Subject : [{}]".format(subject))
    logger.info("From : [{}]".format(from_))
    logger.info("body : [{}]".format(text_content)) 

    if text_content and text_charset:
         email_text =  text_content.decode(text_charset)
         start_handler_flow(email_text, subject, from_, msg_id)
    else:
       raise ValueError("Error while reading the email.")
