import json

def json_to_curl(event):
    # Extracting relevant information from the JSON
    response_url = event['ResponseURL']
    stack_id = event['StackId']
    request_id = event['RequestId']
    logical_resource_id = event['LogicalResourceId']
    physical_resource_id = event['PhysicalResourceId']

    # Formatting a new JSON payload for the cURL command
    payload = {
        "Status": "SUCCESS",
        "PhysicalResourceId": physical_resource_id,
        "StackId": stack_id,
        "RequestId": request_id,
        "LogicalResourceId": logical_resource_id
    }

    # Constructing the cURL command
    curl_command = (f"curl -H 'Content-Type: application/json' -X PUT -d '{json.dumps(payload)}' '{response_url}'")

    return curl_command

event = {
    "RequestType": "Delete",
    "ServiceToken": "arn:aws:lambda:us-west-2:463216347886:function:KendraStack-datasourcesynclambda8341FEEB-bHCePU8JWxwm",
    "ResponseURL": "https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A463216347886%3Astack/KendraStack/365b6220-657d-11ee-a4be-022fec806ad5%7CDataSourceSync%7C02a9ebf9-6415-4912-8adc-423a78c33a49?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20231008T025500Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA54RCMT6SBGALGB7S%2F20231008%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=f82d2d2bdd11173a56a82704a61254985d7a0e6ae25e881e0bb7a823cd858d12",
    "StackId": "arn:aws:cloudformation:us-west-2:463216347886:stack/KendraStack/365b6220-657d-11ee-a4be-022fec806ad5",
    "RequestId": "02a9ebf9-6415-4912-8adc-423a78c33a49",
    "LogicalResourceId": "DataSourceSync",
    "PhysicalResourceId": "KendraStack-DataSourceSync-4KO2BOZEF7KL",
    "ResourceType": "AWS::CloudFormation::CustomResource",
    "ResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-west-2:463216347886:function:KendraStack-datasourcesynclambda8341FEEB-bHCePU8JWxwm"
    }
}

print(json_to_curl(event))
