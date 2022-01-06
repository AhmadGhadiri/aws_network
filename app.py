#!/usr/bin/env python3
import aws_cdk as cdk

from mentorship_networking.instance import InstanceStack
from mentorship_networking.mentorship_networking_stack import (
    MentorshipNetworkingStack,
)
from mentorship_networking.peering import PeeringStack

app = cdk.App()

settings = {"vpc_setups": {"cidrs": ["10.0.0.0/24", "10.0.1.0/24"]}}

vpc_peers = MentorshipNetworkingStack(
    app,
    "MentorshipNetworkingStack",
    vpc_props=settings
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    # env=cdk.Environment(account='123456789012', region='us-east-1'),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

InstanceStack(
    app,
    "InstancePeersStack",
    vpc_props=vpc_peers,
    sg_ids=vpc_peers.security_group_ids,
)
PeeringStack(app, "PeeringStack", vpc_peers.created_vpcs)


app.synth()
