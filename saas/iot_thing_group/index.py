import boto3
import json

def lambda_handler(event, context):
    iot_client = boto3.client("iot")

    if event["RequestType"] == "Create":
        thing_group_name = event["ResourceProperties"]["ThingGroupName"]
        iot_client.create_thing_group(thingGroupName=thing_group_name)

    if event["RequestType"] == "Delete":
        thing_group_name = event["ResourceProperties"]["ThingGroupName"]
        iot_client.delete_thing_group(thingGroupName=thing_group_name)

    response_data = {}
    return {
        "Status": "SUCCESS",
        "PhysicalResourceId": thing_group_name,
        "Data": response_data,
    }
