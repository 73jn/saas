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





# {
#     "claimCertificateId": "bc5b6bea248605f9325bd33cd2bbcd0b9cda14a6837a82ca8286e9f95c483dd3",
#     "certificateId": "d0521cecec902f40626b183bf88c9c68340e89177ce3f0b9fd6cc04b39487fbb",
#     "certificatePem": "-----BEGIN CERTIFICATE-----\nMIIDWTCCAkGgAwIBAgIUEAI8DfnJKgkfAzcp3bcocRVWJYowDQYJKoZIhvcNAQEL\nBQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g\nSW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTIzMDUwOTA5NDM1\nOFoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0\nZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAN4ns/gbElWvL7CXshMg\nzQ2Putz2v038KByH9r3MMAU7r/ybylXVHx5EMFlioPVhMAXJZP4i9oOiv5AIcPgf\niIpX7M23d/usGBcPmj7WCxnenE3xYKjcyUapVjfjCU+Jq0uEjMZe5IHVan36k6p3\nCk/QDx/50BigvkkespwQPkfNz8WK402n1vGLG5Wgn97hykdavKA/8REyMjW0iEOL\n5M8PHlC/FFKV5fb5Z1t127k6TzXcamVZGq+yPoetrQwzH7TrzvXbkT0bRU8ZDkL4\nVNaUyJ3wlpkqwTDP+HaZGIc9QmVyBaaokomIbdvyIB27Wy8drc0EpjVbzPzUviOB\ngo0CAwEAAaNgMF4wHwYDVR0jBBgwFoAUufadCFwrkAuWS4LmutfQ+UBe8oowHQYD\nVR0OBBYEFKpTNZ+AXa47GCY47hzzhx3tv5wSMAwGA1UdEwEB/wQCMAAwDgYDVR0P\nAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQBgOYTc6JpmTFULeY95mMl8K2jf\nF0UODHf9EOwyQr/aOOE1rMtymviaZ9JT94ykHnTKyFcUBSIcNPJipbUdkS89DcSP\no1RnVys2AW6gAFQZpU3IkX/6aQpABCjJgpzOm7fTkcPM/Yhw0Gd4wLTHZbfzG3UO\nZuvblwYmx+D3T3IZWZUdNImkRVV8rUI3i1sDpudFD6U8vEduyfMN5c4o6SMAi9qX\nQjS0K+R065ZYspB31LMxedRpdsQ176YKBhLhuGEdsdV8frUYTI3/kIYW9ifpvOeJ\n9Me1x7HLlKv75e1pp9/QuqVj0yPor89oRTXhf50jzUSjYUrOx+mZPceYrHiT\n-----END CERTIFICATE-----\n",
#     "templateArn": "arn:aws:iot:eu-central-1:688793167504:provisioningtemplate/SaasIotProvisioningTemplate",
#     "clientId": "testDevice",
#     "parameters": {
#         "SerialNumber": "SERIAL12345678910",
#         "AWS::IoT::Certificate::Id": "d0521cecec902f40626b183bf88c9c68340e89177ce3f0b9fd6cc04b39487fbb"
#     }
# }