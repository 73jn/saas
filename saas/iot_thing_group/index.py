import boto3
import json
import requests

def send_response(event, context, response_status, response_data, physical_resource_id):
    response_url = event["ResponseURL"]

    response_body = {
        "Status": response_status,
        "Reason": "See the details in CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": physical_resource_id,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": response_data,
    }

    headers = {
        "Content-Type": "",
        "Content-Length": str(len(json.dumps(response_body))),
    }

    try:
        response = requests.put(response_url, data=json.dumps(response_body), headers=headers)
        print("Status code: ", response.reason)
    except Exception as e:
        print("Error sending response: ", e)

def lambda_handler(event, context):
    iot_client = boto3.client("iot")

    try:
        if event["RequestType"] == "Create":
            thing_group_name = event["ResourceProperties"]["ThingGroupName"]
            create_response = iot_client.create_thing_group(thingGroupName=thing_group_name)
            thing_group_arn = create_response["thingGroupArn"]

        if event["RequestType"] == "Delete":
            thing_group_name = event["ResourceProperties"]["ThingGroupName"]
            iot_client.delete_thing_group(thingGroupName=thing_group_name)

        response_data = {"Arn": thing_group_arn} if event["RequestType"] == "Create" else {}
        send_response(event, context, "SUCCESS", response_data, thing_group_name)

    except Exception as e:
        print("Error: ", str(e))
        send_response(event, context, "FAILED", {}, "FAILED_RESOURCE")
