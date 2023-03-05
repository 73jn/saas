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

class SaasStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "SaasQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        
        func = lambda_.Function(
            self, "SaasLambda",
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="index.handler",
            code=lambda_.Code.from_inline("def handler(event, context):\n    print(event)\n"),
        )
        func.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        # IoT
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
            )
        )

        iot_topic_rule.apply_removal_policy(cdk.RemovalPolicy.DESTROY)




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