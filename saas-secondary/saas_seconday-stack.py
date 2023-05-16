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
)
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_assets as s3_assets

# Import pyOpenSSL
import OpenSSL
import json



class SaasStack(Stack):

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


    1   # Create a lambda who 