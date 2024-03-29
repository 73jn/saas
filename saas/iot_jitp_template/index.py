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
    response = {}

    try:
        if event["RequestType"] == "Create":
            print("Creating provisioning template")
            template_name = event["ResourceProperties"]["TemplateName"]
            provisioning_role_arn = event["ResourceProperties"]["ProvisioningRoleArn"]
            template_body = event["ResourceProperties"]["TemplateBody"]
            # ca_certificate = event["ResourceProperties"]["CaCertificate"]
            # Print template body
            print(template_body)
            print(provisioning_role_arn)
            print(template_name)



            create_response = iot_client.create_provisioning_template(
            templateName=template_name,
            templateBody=template_body,
            enabled=True,
            provisioningRoleArn=provisioning_role_arn,
            type='JITP'
            )

            # # Register CA certificate
            # response2 = iot_client.register_ca_certificate(
            #     caCertificate=ca_certificate,
            #     verificationCertificate=ca_certificate,
            #     setAsActive=True,
            #     allowAutoRegistration=True,
            #     registrationConfig={
            #         'templateBody': template_body,
            #         'roleArn': provisioning_role_arn,
            #         "templateName": template_name
            #     }
            # )

        if event["RequestType"] == "Delete":
            template_name = event["ResourceProperties"]["TemplateName"]
            iot_client.delete_provisioning_template(templateName=template_name)

        response_data = {"Arn": create_response["templateArn"]} if event["RequestType"] == "Create" else {}
        send_response(event, context, "SUCCESS", response_data, template_name)

    except Exception as e:
        print("Error: ", str(e))
        send_response(event, context, "FAILED", {}, "FAILED_RESOURCE")



