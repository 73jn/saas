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
    template_name = ""

    try:
        if event["RequestType"] == "Create":
            print("Creating provisioning template")
            template_name = event["ResourceProperties"]["TemplateName"]
            provisioning_role_arn = event["ResourceProperties"]["ProvisioningRoleArn"]
            template_body = event["ResourceProperties"]["TemplateBody"]
            # Print template body
            print(template_body)
            print(provisioning_role_arn)
            print(template_name)

            response = iot_client.create_provisioning_template(
            templateName=template_name,
            templateBody=template_body,
            enabled=True,
            provisioningRoleArn=provisioning_role_arn,
            type='JITP'
            )

        if event["RequestType"] == "Delete":
            template_name = event["ResourceProperties"]["TemplateName"]
            list_of_templates = iot_client.list_provisioning_templates()
            for template in list_of_templates["templates"]:
                if template["templateName"] == template_name:
                    response = iot_client.delete_provisioning_template(templateName=template_name)
    
        template_arn = response["templateArn"]
        response_data = {"Arn": template_arn}
        send_response(event, context, "SUCCESS", response_data, template_name)

    except Exception as e:
        print("Error: ", str(e))
        send_response(event, context, "FAILED", {}, "FAILED_RESOURCE")



