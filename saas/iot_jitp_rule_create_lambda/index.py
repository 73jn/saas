import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Print event to CloudWatch Logs
    logger.info(json.dumps(event))

    # Extract values from event
    thing_name = event['thingName']
    
    # Create IoT client
    iot_client = boto3.client('iot')

    # aws iot list-thing-principals --thing-name sfdfsdfsdf
    things_infos = iot_client.list_thing_principals(thingName=thing_name)
    
    # things_infos =
    # {
    # "principals": [
    #     "arn:aws:iot:eu-central-1:688793167504:cert/04322b13589d3f84edd9bbe44dbd70b48b77156253594d9a5e98b3e21cf6a591"
    # ]
    # }

    # Extract certificate id from response
    certificate_id = things_infos['principals'][0].split('/')[1]

    # aws iot describe-certificate --certificate-id 04322b13589d3f84edd9bbe44dbd70b48b77156253594d9a5e98b3e21cf6a591
    certificate_infos = iot_client.describe_certificate(certificateId=certificate_id)


    # {
    #     "certificateDescription": {
    #         "certificateArn": "arn:aws:iot:eu-central-1:688793167504:cert/04322b13589d3f84edd9bbe44dbd70b48b77156253594d9a5e98b3e21cf6a591",
    #         "certificateId": "04322b13589d3f84edd9bbe44dbd70b48b77156253594d9a5e98b3e21cf6a591",
    #         "status": "INACTIVE",
    #         "certificatePem": "-----BEGIN CERTIFICATE-----\nMIIDWjCCAkKgAwIBAgIVALjO19mMJ2WAY+zGJ0wgKAKhCtsJMA0GCSqGSIb3DQEB\nCwUAME0xSzBJBgNVBAsMQkFtYXpvbiBXZWIgU2VydmljZXMgTz1BbWF6b24uY29t\nIEluYy4gTD1TZWF0dGxlIFNUPVdhc2hpbmd0b24gQz1VUzAeFw0yMzA1MTUxNDI1\nMThaFw00OTEyMzEyMzU5NTlaMB4xHDAaBgNVBAMME0FXUyBJb1QgQ2VydGlmaWNh\ndGUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCrPZ/rp2WYCw11lCUe\n/NDr2xvdH9+Rg/A86sc14Vjn619ThL9nUDWCVilI4AJO15kglpJepNgw2OYYU0gW\nH8hXt1U5lTu00e0/ACRrxAZNvl9lljrql0yPjSnJ93S1muFL3aWXmy+FNzVZw9Pa\nvNqIKJw8I6wllALYRXE7cnrwkPA1oe6GxjvYW6m6HGPbaMoX4J9eRoDAGxY9GYTF\nOdpAVJR7YEoX5uGgg32thhGnbYUAOXWyEwBwARpP4NLhL7ysXQBW0e+U4t2lBVur\ntNzQxwIBXo/ldcaQ5U1feGClGmp70MpDbIKkCgAuErLfbd2USk/rTaCPtqk0Otfi\nfufjAgMBAAGjYDBeMB8GA1UdIwQYMBaAFIc09S1vUCM5Ey3/3gmUfw4I287xMB0G\nA1UdDgQWBBSKYHt6bNFIOc4U5NnpaGHQwiCCDzAMBgNVHRMBAf8EAjAAMA4GA1Ud\nDwEB/wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAQEAyi58ujzgWB4PfkuuEHOCSl8X\nHMYvh1segyJ13zPmXvmPjAVeExmQw0aIwuB/t37ghIK7KjLhhNKrg/tUTzNbqfxq\nLCYBGVGmr1POfugow8LkIEyGiAfggEbt7Rpmvq/4434Ku+urjRaW9cTqULc10pT3\nBDL6viLy0ZwTMDTh7rH89ZDi5xOalVc9h3i5oZQwag8V2eurX7K9dSMW54Zaun5c\n7Ki3RpwbgWwj634un+kuXK7uqeEv/l4bW+Vdh1UXNTgvFeU86VbNH265aqQSjGYV\n7xkE2L35KJmqHJGhPe/AjaNyV71ljKn8NjGXPqkxxtMfaXHaXcv1GILHV56Kjg==\n-----END CERTIFICATE-----\n",
    #         "ownedBy": "688793167504",
    #         "creationDate": "2023-05-15T16:27:18.548000+02:00",
    #         "lastModifiedDate": "2023-05-15T16:27:18.548000+02:00",
    #         "customerVersion": 1,
    #         "transferData": {},
    #         "generationId": "9925b445-1a04-428f-a17c-972eb41d87d3",
    #         "validity": {
    #             "notBefore": "2023-05-15T16:25:18+02:00",
    #             "notAfter": "2050-01-01T00:59:59+01:00"
    #         },
    #         "certificateMode": "DEFAULT"
    #     }


    # Get certificate pem
    certificate_pem = certificate_infos['certificateDescription']['certificatePem']


    new_response = event
    # Add certificate pem to response
    new_response['certificatePem'] = certificate_pem
    # Add certificate id to response
    new_response['certificateId'] = certificate_id

    # Dynamodb client
    dynamodb_client = boto3.client('dynamodb')

    # Add to dynamodb testDyn with primary key event, partition key is thingId
    dynamodb_client.put_item(TableName='testDyn', Item={'event': {'S': new_response['thingId']},'payload': {'S': json.dumps(new_response)},
        'certificatePem': {'S': new_response['certificatePem']},
        'certificateId': {'S': new_response['certificateId']}
        })
    
    


















# I receive :
# {
#   "eventType": "THING_EVENT",
#   "eventId": "dafb5171e022c082dc034fbe13a698b5",
#   "timestamp": 1684168543285,
#   "operation": "CREATED",
#   "accountId": "688793167504",
#   "thingId": "8f894b02-bad9-4ca4-b957-ef613eae1bfc",
#   "thingName": "asdasdasdsa",
#   "versionNumber": 1,
#   "thingTypeName": null,
#   "billinGroupName": null,
#   "attributes": {}
# }