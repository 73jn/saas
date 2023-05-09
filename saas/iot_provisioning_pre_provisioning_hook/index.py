import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))
    certificate_id = event["certificateId"]
    certificate_arn = event["certificateArn"]
    certificate_properties = event["certificateProperties"]
    logger.info(f"Certificate ID: {certificate_id}")
    logger.info(f"Certificate ARN: {certificate_arn}")
    logger.info(f"Certificate properties: {json.dumps(certificate_properties, indent=2)}")

    # Print event to CloudWatch Logs
    logger.info(json.dumps(event))

    # Return an ALLOW action for all devices
    return {
        "allowCertificate": True,
        "certificateId": certificate_id,
        "certificateProperties": certificate_properties
    }
