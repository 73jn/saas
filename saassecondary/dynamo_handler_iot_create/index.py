import boto3
import json

iot_client = boto3.client('iot')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    for record in event['Records']:
        # Récupération de awsRegion
        aws_region = record['awsRegion']
        print("AWS Region: ", aws_region)
        
        .
        # Récupération de certificatePem
        certificate_pem = record['dynamodb']['NewImage']['certificatePem']['S']
        print("Certificate PEM: ", certificate_pem)
        
        # Récupération de thingName à partir du payload
        payload = json.loads(record['dynamodb']['NewImage']['payload']['S'])
        thing_name = payload['thingName']
        print("Thing Name: ", thing_name)

        # Création du Thing
        response_thing = iot_client.create_thing(thingName=thing_name)
        print(f'Thing {thing_name} created with response: {response_thing}')
        
        # List all certificates
        certificates_response = iot_client.list_certificates()
        
        # Find if certificate exists
        certificate_id = None
        for cert in certificates_response['certificates']:
            cert_desc = iot_client.describe_certificate(certificateId=cert['certificateId'])
            if 'certificateDescription' in cert_desc and 'certificatePem' in cert_desc['certificateDescription']:
                if cert_desc['certificateDescription']['certificatePem'] == certificate_pem:
                    certificate_id = cert['certificateId']
                    print(f'Certificate already exists with ID: {certificate_id}')
                    break
        
        # If certificate does not exist, register it
        if certificate_id is None:
            response_cert = iot_client.register_certificate_without_ca(
                certificatePem=certificate_pem,
                status='ACTIVE'
            )
            print(f'Certificate registered without CA with response: {response_cert}')
            certificate_id = response_cert['certificateId']
        
        response = iot_client.describe_certificate(certificateId=certificate_id)
        certificate_arn = response['certificateDescription']['certificateArn']
        print(f'Certificate ARN: {certificate_arn}')

        # Attach the certificate to the thing
        attach_response = iot_client.attach_thing_principal(
            thingName=thing_name,
            principal=certificate_arn
        )
        print(f'Certificate attached to thing with response: {attach_response}')
