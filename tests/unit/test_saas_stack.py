import aws_cdk as core
import aws_cdk.assertions as assertions

from saas.saas_stack import SaasStack

# example tests. To run these tests, uncomment this file along with the example
# resource in saas/saas_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SaasStack(app, "saas")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
