import boto3
import json

def print_model_names_and_ids():
    bedrock = boto3.client(service_name='bedrock')

    response = bedrock.list_foundation_models()
    model_summaries = response['modelSummaries']

    for model_summary in model_summaries:
        model_name = model_summary['modelName']
        model_id = model_summary['modelId']
        model_provider = model_summary['providerName']
        print(f"ModelName: {model_name} --- ModelId: {model_id} --- ModelProvider: {model_provider}")
        

# Call the method to execute the code
print_model_names_and_ids()
