from typing import List

from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class PeeringStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpcs: List, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the peering connection
        peer = ec2.CfnVPCPeeringConnection(
            self,
            "Peer",
            vpc_id=vpcs[0].vpc_id,
            peer_vpc_id=vpcs[1].vpc_id,
        )

        # Add route from the private subnet of the first VPC to the second VPC over the peering connection
        # NB the below was taken from:
        # https://stackoverflow.com/questions/62525195/adding-entry-to-route-table-with-cdk-typescript-when-its-private-subnet-alread
        for index, priv_subnet in enumerate(vpcs[0].private_subnets, start=1):
            route_table_id = priv_subnet.route_table.route_table_id
            ec2.CfnRoute(
                self,
                f"RouteFromPrivateSubnetOfVpc1ToVpc2{index}",
                destination_cidr_block=vpcs[1].vpc_cidr_block,
                route_table_id=route_table_id,
                vpc_peering_connection_id=peer.ref,
            )

        # Add route from the private subnet of the second VPC to the first VPC over the peering connection
        for index, priv_subnet in enumerate(vpcs[1].private_subnets, start=1):
            route_table_id = priv_subnet.route_table.route_table_id
            ec2.CfnRoute(
                self,
                f"RouteFromPrivateSubnetOfVpc2ToVpc1{index}",
                destination_cidr_block=vpcs[0].vpc_cidr_block,
                route_table_id=route_table_id,
                vpc_peering_connection_id=peer.ref,
            )
