from typing import List

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds

from cdk_ec2_key_pair import KeyPair
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
            # instance_name = f"Instance{index}"
            # instance_resource = ec2.BastionHostLinux(
            #     self,
            #     instance_name,
            #     vpc=vpc,
            #     instance_name=instance_name,
            #     security_group=ec2.SecurityGroup.from_security_group_id(
            #         self, f"{instance_name}SecurityGroup", sg_ids[index - 1]
            #     ),
            # )

            # Create an EC2 in the public subnet
            # user_data = ec2.UserData.for_linux()
            # user_data.add_commands('')
            key = KeyPair(self, f"keypair{index}", name=f"cdk-keypair{index}", description="{index} Key pair created with cdk deployment")
            instance_name = f"InstancePublic{index}"
            public_instance = ec2.BastionHostLinux(
                self,
                instance_name,
                vpc=vpc,
                subnet_selection=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                security_group=ec2.SecurityGroup.from_security_group_id(
                    self, f"{instance_name}SecurityGroup", sg_ids[index - 1]
                ),
            )

            public_instance.instance.instance.add_property_override('KeyName', key.key_pair_name)

            # instance_resource = ec2.BastionHostLinux(
            #     self,
            #     instance_name,
            #     vpc=vpc,
            #     instance_name=instance_name,
            #     security_group=ec2.SecurityGroup.from_security_group_id(
            #         self, f"{instance_name}SecurityGroup", sg_ids[index - 1]
            #     ),
            # )
            cdk.CfnOutput(
                self,
                f"{instance_name}PublicIP",
                value=public_instance.instance_public_ip,
            )

            # Create the db in private subnet of first VPC
            if index == 1:
                db_instance = rds.DatabaseInstance(
                    self,
                    "db-instance",
                    vpc=vpc,
                    vpc_subnets=ec2.SubnetType.PRIVATE_ISOLATED,
                    engine=rds.DatabaseInstanceEngine.postgres(
                        version=rds.PostgresEngineVersion.VER_13_4
                    ),
                    instance_type=ec2.InstanceType.of(
                        ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
                    ),
                    credentials=rds.Credentials.from_generated_secret(
                        "postgres"
                    ),
                    multi_az=False,
                    allocated_storage=100,
                    max_allocated_storage=105,
                    allow_major_version_upgrade=False,
                    auto_minor_version_upgrade=True,
                    backup_retention=cdk.Duration.days(0),
                    delete_automated_backups=True,
                    removal_policy=cdk.RemovalPolicy.DESTROY,
                    deletion_protection=False,
                    database_name="todosdb",
                    publicly_accessible=False,
                )
                db_instance.connections.allow_from(
                    public_instance, ec2.Port.tcp(5432)
                )

                cdk.CfnOutput(
                    self,
                    "dbEndpoint",
                    value=db_instance.instance_endpoint.hostname,
                )
                cdk.CfnOutput(
                    self, "secretName", value=db_instance.secret.secret_name
                )

