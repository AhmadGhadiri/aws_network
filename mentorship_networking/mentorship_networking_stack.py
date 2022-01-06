import json
import os

from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2  # Duration,; aws_sqs as sqs,
from constructs import Construct
from dotenv import load_dotenv


class MentorshipNetworkingStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpc_props: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Code for creating one VPC
        # self.vpc1 = ec2.Vpc(self, 'demovpc1',
        #     cidr = '192.168.50.0/24',
        #     max_azs = 2,
        #     enable_dns_hostnames = True,
        #     enable_dns_support = True,
        #     subnet_configuration=[
        #         ec2.SubnetConfiguration(
        #             name = 'Public-Subent',
        #             subnet_type = ec2.SubnetType.PUBLIC,
        #             cidr_mask = 26
        #         ),
        #         ec2.SubnetConfiguration(
        #             name = 'Private-Subnet',
        #             subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT,
        #             cidr_mask = 26
        #         )
        #     ],
        #     nat_gateways = 1,

        # )
        # priv_subnets = [subnet.subnet_id for subnet in self.vpc1.private_subnets]

        # count = 1
        # for psub in priv_subnets:
        #     ssm.StringParameter(self, 'private-subnet-'+ str(count),
        #         string_value = psub,
        #         parameter_name = '/'+"ahmad1"+'/private-subnet-'+str(count)
        #         )
        #     count += 1

        # read allowed ip addresses
        load_dotenv()
        allowed_cidrs = json.loads(os.getenv("ALLOWED_IPS"))

        created_vpcs = []
        cidrs = vpc_props["vpc_setups"]["cidrs"]
        for i, cidr in enumerate(cidrs, start=1):
            created_vpcs.append(
                ec2.Vpc(
                    self,
                    f"demoVpc{i}",
                    cidr=cidr,
                    max_azs=2,
                    subnet_configuration=[
                        ec2.SubnetConfiguration(
                            cidr_mask=27,
                            name="public",
                            subnet_type=ec2.SubnetType.PUBLIC,
                        ),
                        ec2.SubnetConfiguration(
                            cidr_mask=27,
                            name="private",
                            subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                        ),
                    ],
                )
            )
        
        self.security_group_ids = []
        for index, vpc in enumerate(created_vpcs, start=1):
            # create the security group
            vpc_sg = ec2.SecurityGroup(
                self,
                f"DefaultSecurityGroup{index}",
                vpc=vpc,
                allow_all_outbound=True,
                description=f"Security group for VPC{index}",
            )
            # Add ingress rule
            for cidr in allowed_cidrs:
                vpc_sg.add_ingress_rule(
                    ec2.Peer.ipv4(cidr),
                    ec2.Port.tcp(443),
                    f"Allow https access for internal {cidr}",
                )
            self.security_group_ids.append(vpc_sg.security_group_id)
        self.created_vpcs = created_vpcs
