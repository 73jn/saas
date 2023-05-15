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

            ca_certificate = event["ResourceProperties"]["CACertificate"]
            template_name = event["ResourceProperties"]["TemplateName"]
            provisioning_role_arn = event["ResourceProperties"]["ProvisioningRoleArn"]
            template_body = event["ResourceProperties"]["TemplateBody"]
            # Register CA certificate
            response = iot_client.register_ca_certificate(
                caCertificate=ca_certificate,
                verificationCertificate=ca_certificate,
                setAsActive=True,
                allowAutoRegistration=True,
                registrationConfig={
                    'templateBody': template_body,
                    'roleArn': provisioning_role_arn,
                    "templateName": template_name
                }
            )
        if event["RequestType"] == "Delete":
            certificate_id = event["PhysicalResourceId"]  # assuming the certificate id is the physical resource id

            # Update CA certificate to inactive
            iot_client.update_ca_certificate(
                certificateId=certificate_id,
                newStatus='INACTIVE'
            )

            # Delete CA certificate
            iot_client.delete_ca_certificate(
                certificateId=certificate_id
            )


        response_data = {"Arn": response["templateArn"]} if event["RequestType"] == "Create" else {}
        send_response(event, context, "SUCCESS", response_data, template_name)

    except Exception as e:
        print("Error: ", str(e))
        send_response(event, context, "FAILED", {}, "FAILED_RESOURCE")



