from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct

import aws_cdk.aws_iot as iot
import aws_cdk.aws_lambda as lambda_
import aws_cdk as cdk

# Import lambda_event_sources
import aws_cdk.aws_lambda_event_sources as lambda_event_sources

from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
)
import aws_cdk.aws_iot_actions_alpha as actions



class SaasStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "SaasQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        

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
                    actions=["iot:*"],
                    resources=["*"]
                )
            ]
        )
        lambda_policy.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Attach the policy to the role
        lambda_policy.attach_to_role(lambda_role)

        # Create the lambda function
        func = lambda_.Function(
            self, "MyLambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.Code.from_inline("def handler(event, context):\n    print(event)\n"),
            handler="index.handler",
            role=lambda_role
        )


        func.apply_removal_policy(cdk.RemovalPolicy.DESTROY)



        # Créer la règle de sujet IoT pour déclencher la fonction lambda
        iot_topic_rule = iot.CfnTopicRule(
            self, "SaasIotTopicRule",
            rule_name="SaasIotTopicRule",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                actions=[
                    iot.CfnTopicRule.ActionProperty(
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn=func.function_arn
                        )
                    )
                ],
                sql="SELECT * FROM 'saas/iot'",
                rule_disabled=False
            ),
        )

        iot_topic_rule.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # OH MY GOD 10 HOURS OF MY LIFE
        # https://github.com/aws/aws-cdk/issues/16339
        cfn_permission = lambda_.CfnPermission(
            self, "LambdaPermission",
            action="lambda:InvokeFunction",
            function_name=func.function_name,
            principal="iot.amazonaws.com",
            source_arn=iot_topic_rule.attr_arn
        )
        cfn_permission.apply_removal_policy(cdk.RemovalPolicy.DESTROY)




        # Create policy certificate iot
        iot_policy = iot.CfnPolicy(
            self, "SaasIotPolicy",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Publish",
                            "iot:Receive",
                            "iot:Subscribe",
                            "iot:Connect",
                            "iot:UpdateThingShadow",
                            "iot:GetThingShadow",
                            "iot:DeleteThingShadow"
                
                        ],
                        "Resource": [
                            # Allow to publish and receive to all topics
                            "*"
                        ]
                    }
                ]
            },
            policy_name="SaasIotPolicy"
        )
        iot_policy.apply_removal_policy(cdk.RemovalPolicy.DESTROY)