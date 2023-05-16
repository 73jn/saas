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
            # If the thing group is not found, it will throw an exception
            thing_group_arn = iot_client.describe_thing_group(thingGroupName=thing_group_name)["thingGroupArn"]

            if thing_group_arn:
                # List all things in the thing group
                things = iot_client.list_things_in_thing_group(thingGroupName=thing_group_name)["things"]

                # Remove all things from the thing group
                for thing in things:
                    iot_client.remove_thing_from_thing_group(thingGroupName=thing_group_name, thingName=thing)
            else:
                print("Thing group not found")




    except Exception as e:
        print("Error: ", str(e))
        send_response(event, context, "FAILED", {}, "FAILED_RESOURCE")


    response_data = {"Arn": thing_group_arn} if event["RequestType"] == "Create" else {}
    print(response_data)
    send_response(event, context, "SUCCESS", response_data, thing_group_name)