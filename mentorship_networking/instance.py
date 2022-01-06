from typing import List

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class InstanceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_props: dict,
        sg_ids: List,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for index, vpc in enumerate(vpc_props.created_vpcs, start=1):
            instance_name = f"Instance{index}"
            instance_resource = ec2.BastionHostLinux(
                self,
                instance_name,
                vpc=vpc,
                instance_name=instance_name,
                security_group=ec2.SecurityGroup.from_security_group_id(
                    self, f"{instance_name}SecurityGroup", sg_ids[index - 1]
                ),
            )
            cdk.CfnOutput(
                self,
                f"{instance_name}PrivateIp",
                value=instance_resource.instance_private_ip,
            )
