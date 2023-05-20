from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct

import aws_cdk.aws_iot as iot
import aws_cdk.aws_lambda as lambda_
import aws_cdk as cdk
from aws_cdk import aws_cloudformation as cfn
# Import lambda_event_sources
import aws_cdk.aws_lambda_event_sources as lambda_event_sources

from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_dynamodb as ddb,
)
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_assets as s3_assets

# Import pyOpenSSL
import OpenSSL
import json



class SaasStackSecondary(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a role for the lambda function
        lambda_role = iam.Role(
            self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_role.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Define the IAM policy
        lambda_policy = iam.Policy(
            self, "LambdaPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    resources=["arn:aws:logs:*:*:*"]
                ),
                iam.PolicyStatement(
                    actions=["iot:*",
                            "iot:CreateThingGroup",
                            "iot:DeleteThingGroup",
                            # Create template provisioning
                            "iot:CreateProvisioningTemplate",
                            "iam:PassRole",
                            # Publish to dynamodb
                            "dynamodb:*",

                            ],
                    resources=["*"]
                )
            ]
        )
        lambda_policy.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Attach the policy to the role
        lambda_policy.attach_to_role(lambda_role)


        # Lambda
        lambda_dynamo_handler_iot_create = lambda_.Function(
            self, "lambda_dynamo_handler_iot_create",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.Code.from_asset("saassecondary/dynamo_handler_iot_create"),
            handler="index.lambda_handler",
            role=lambda_role
        )


        # Create the lambda event source
        lambda_event_source = lambda_event_sources.DynamoEventSource(
            # Exisiting table
            table=ddb.Table.from_table_attributes(
                self, "Table",
                table_name="testDyn",
                table_stream_arn="arn:aws:dynamodb:eu-west-1:688793167504:table/testDyn/stream/2023-05-15T14:04:35.784"
            ),


            starting_position=lambda_.StartingPosition.LATEST,
            batch_size=1,

        )

        # Add the event source to the lambda
        lambda_dynamo_handler_iot_create.add_event_source(lambda_event_source)


        # OH MY GOD 10 HOURS OF MY LIFE
        # https://github.com/aws/aws-cdk/issues/16339
        cfn_permission = lambda_.CfnPermission(
            self, "LambdaPermission",
            action="lambda:InvokeFunction",
            function_name=lambda_dynamo_handler_iot_create.function_name,
            # Triggered by dynamodb
            principal="dynamodb.amazonaws.com",
            source_arn="arn:aws:dynamodb:eu-west-1:688793167504:table/testDyn/stream/2023-05-15T14:04:35.784"
        )

