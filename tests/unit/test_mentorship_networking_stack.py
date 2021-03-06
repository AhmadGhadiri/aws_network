import aws_cdk as core
import aws_cdk.assertions as assertions

from mentorship_networking.mentorship_networking_stack import (
    MentorshipNetworkingStack,
)


# example tests. To run these tests, uncomment this file along with the example
# resource in mentorship_networking/mentorship_networking_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MentorshipNetworkingStack(app, "mentorship-networking")
    template = assertions.Template.from_stack(stack)
    print(template)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
