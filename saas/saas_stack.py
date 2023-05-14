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
                    actions=["iot:*",
                            "iot:CreateThingGroup",
                            "iot:DeleteThingGroup",
                            # Create template provisioning
                            "iot:CreateProvisioningTemplate",
                            "iam:PassRole",],
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
            self, "SaasIotPolicy12",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "*"
                        ],
                        "Resource": [
                            # Allow to publish and receive to all topics
                            "*"
                        ]
                    }
                ]
            },
            policy_name="SaasIotPolicy12"
        )
        iot_policy.apply_removal_policy(cdk.RemovalPolicy.DESTROY)


        # Bulk registration
        # Create an S3 bucket containing the json with the devices name and the serial number and the CSR
        # bucket = s3.Bucket(
        #     self, "SaasBucket",
        #     removal_policy=cdk.RemovalPolicy.DESTROY
        # )

        # # Fill the bucket with the json file
        # s3_assets.Asset(
        #     self, "SaasAsset",
        #     path="saas/asset.json",
        #     bucket=bucket,

        # )


        
        iot_thing_group_lambda = lambda_.Function(
            self,
            "IotThingGroupLambda",
            code=lambda_.Code.from_asset("saas/iot_thing_group"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,

            # Add the policy to the role
            role=lambda_role,
        )
        iot_thing_group_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        


        thing_group_name = "MyIotThingGroup"
        iot_thing_group = cfn.CfnCustomResource(
            self,
            "IotThingGroup",
            service_token=iot_thing_group_lambda.function_arn,
        )
        iot_thing_group.add_override("Properties.ThingGroupName", thing_group_name)


        # Add the policy to the custom resource to allow trigger the lambda function
        iot_thing_group_cfn_permission = lambda_.CfnPermission(
            self, "IotThingGroupPermission",
            action="lambda:InvokeFunction",
            function_name=iot_thing_group_lambda.function_name,
            principal="cloudformation.amazonaws.com",  # Change this to cloudformation.amazonaws.com
            source_arn=iot_thing_group.get_att(attribute_name="Arn").to_string()
        )
        iot_thing_group.apply_removal_policy(cdk.RemovalPolicy.DESTROY)






        # Provisioning template
        # Import json template
        template_body = open("saas/iot_provisioning_template.json", "r").read()

        # Provision role for the template
        iot_provioning_role = iam.Role(
            self, "SaasIotProvisioningRole",
            assumed_by=iam.ServicePrincipal("iot.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSIoTThingsRegistration"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSIoTFullAccess"),
            ]
        )
        iot_provioning_role.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Pre-provisioning hook lambda
        iot_provioning_pre_provisioning_hook_lambda = lambda_.Function(
            self,
            "IotProvisioningPreProvisioningHookLambda",
            code=lambda_.Code.from_asset("saas/iot_provisioning_pre_provisioning_hook"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,

            # Add the policy to the role
            role=lambda_role,
        )
        iot_provioning_pre_provisioning_hook_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)



        # Create the template
        iot_provioning_template = iot.CfnProvisioningTemplate(
            self, "SaasIotProvisioningTemplate",
            provisioning_role_arn = iot_provioning_role.role_arn,
            template_body=template_body,
            template_name="SaasIotProvisioningTemplate",
            enabled=True,
            pre_provisioning_hook=iot.CfnProvisioningTemplate.ProvisioningHookProperty(
                target_arn=iot_provioning_pre_provisioning_hook_lambda.function_arn
            )
            
        )
        iot_provioning_template.apply_removal_policy(cdk.RemovalPolicy.DESTROY)


        # Permit the lambda to call the iot api
        permission_hook_pre_provisionning = lambda_.CfnPermission(
            self, "LambdaPermissionPreProvisioningHook",
            action="lambda:InvokeFunction",
            function_name=iot_provioning_pre_provisioning_hook_lambda.function_name,
            principal="iot.amazonaws.com",
        )
        permission_hook_pre_provisionning.apply_removal_policy(cdk.RemovalPolicy.DESTROY)



        # JITP
        # Lambda iot_jitp_template
        iot_jitp_template_lambda = lambda_.Function(
            self,
            "IotJitpTemplateLambda",
            code=lambda_.Code.from_asset("saas/iot_jitp_template"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,

            # Add the policy to the role
            role=lambda_role,
        )
        iot_jitp_template_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Create Provisioning template WITH CUSTOM RESOURCE
        iot_jitp_template = cfn.CfnCustomResource(
            self,
            "IotJitpTemplate",
            service_token=iot_jitp_template_lambda.function_arn,
        )
        #iot_jitp_template.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        iot_jitp_template.add_override("Properties.TemplateName", "SaasIotJitpTemplate")
        iot_jitp_template.add_override("Properties.ProvisioningRoleArn", iot_provioning_role.role_arn)
        template_body = open("saas/body.json", "r").read()
        iot_jitp_template.add_override("Properties.TemplateBody", template_body)
