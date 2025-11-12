import os
from troposphere import (
    Template, Parameter, Ref, GetAtt, Sub, Select, GetAZs, Join,
    ec2,Output, cloudwatch, iam,
)

S3_FLOW_LOG_BUCKET_NAME = "polystudents3-moureau-armbruster2"

t = Template()
t.set_description("TP4 - Question 3.2 - VPC")

# création des paramètres
env_name = t.add_parameter(Parameter(
    "EnvironmentName",
    Type="String",
    Description="environment is prefixed to resource names"
))

vpc_cidr = t.add_parameter(Parameter(
    "VpcCIDR",
    Type="String",
    Default="10.0.0.0/16",
    Description="VPC polystudent-vpc1"
))

public_sn1_cidr = t.add_parameter(Parameter(
    "PublicSubnet1CIDR",
    Type="String",
    Default="10.0.0.0/24",
    Description="Public Subnet in availability zone 1"
))

public_sn2_cidr = t.add_parameter(Parameter(
    "PublicSubnet2CIDR",
    Type="String",
    Default="10.0.16.0/24",
    Description="Public Subnet in availability zone 2"
))

private_sn1_cidr = t.add_parameter(Parameter(
    "PrivateSubnet1CIDR",
    Type="String",
    Default="10.0.128.0/24",
    Description="Private Subnet in availability zone 1"
))

private_sn2_cidr = t.add_parameter(Parameter(
    "PrivateSubnet2CIDR",
    Type="String",
    Default="10.0.144.0/24",
    Description="Private Subnet in availability zone 2"
))

# création des ressources
vpc = t.add_resource(ec2.VPC(
    "VPC",
    CidrBlock=Ref(vpc_cidr),
    EnableDnsSupport="true",
    EnableDnsHostnames="true",
    Tags=[{"Key": "Name", "Value": Ref(env_name)}]
))

public_sn1 = t.add_resource(ec2.Subnet(
    "PublicSubnet1",
    VpcId=Ref(vpc),
    AvailabilityZone=Select(0, GetAZs("")),
    CidrBlock=Ref(public_sn1_cidr),
    MapPublicIpOnLaunch=True,
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Public Subnet (AZ1)")}]
))

public_sn2 = t.add_resource(ec2.Subnet(
    "PublicSubnet2",
    VpcId=Ref(vpc),
    AvailabilityZone=Select(1, GetAZs("")),
    CidrBlock=Ref(public_sn2_cidr),
    MapPublicIpOnLaunch=True,
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Public Subnet (AZ2)")}]
))

private_sn1 = t.add_resource(ec2.Subnet(
    "PrivateSubnet1",
    VpcId=Ref(vpc),
    AvailabilityZone=Select(0, GetAZs("")),
    CidrBlock=Ref(private_sn1_cidr),
    MapPublicIpOnLaunch=False,
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Private Subnet (AZ1)")}]
))

private_sn2 = t.add_resource(ec2.Subnet(
    "PrivateSubnet2",
    VpcId=Ref(vpc),
    AvailabilityZone=Select(1, GetAZs("")),
    CidrBlock=Ref(private_sn2_cidr),
    MapPublicIpOnLaunch=False,
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Private Subnet (AZ2)")}]
))

igw = t.add_resource(ec2.InternetGateway(
    "InternetGateway",
    Tags=[{"Key": "Name", "Value": Ref(env_name)}]
))

igw_attach = t.add_resource(ec2.VPCGatewayAttachment(
    "InternetGatewayAttachment",
    InternetGatewayId=Ref(igw),
    VpcId=Ref(vpc)
))

nat_eip1 = t.add_resource(ec2.EIP(
    "NatGateway1EIP",
    Domain="vpc",
    DependsOn=igw_attach.title
))

nat_gw1 = t.add_resource(ec2.NatGateway(
    "NatGateway1",
    AllocationId=GetAtt(nat_eip1, "AllocationId"),
    SubnetId=Ref(public_sn1),
))

nat_eip2 = t.add_resource(ec2.EIP(
    "NatGateway2EIP",
    Domain="vpc",
    DependsOn=igw_attach.title
))

nat_gw2 = t.add_resource(ec2.NatGateway(
    "NatGateway2",
    AllocationId=GetAtt(nat_eip2, "AllocationId"),
    SubnetId=Ref(public_sn2),
))

public_rt = t.add_resource(ec2.RouteTable(
    "PublicRouteTable",
    VpcId=Ref(vpc),
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Public Routes")}]
))

t.add_resource(ec2.Route(
    "DefaultPublicRoute",
    RouteTableId=Ref(public_rt),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(igw),
    DependsOn=igw_attach.title
))

t.add_resource(ec2.SubnetRouteTableAssociation(
    "PublicSubnet1RouteTableAssociation",
    RouteTableId=Ref(public_rt),
    SubnetId=Ref(public_sn1)
))

t.add_resource(ec2.SubnetRouteTableAssociation(
    "PublicSubnet2RouteTableAssociation",
    RouteTableId=Ref(public_rt),
    SubnetId=Ref(public_sn2)
))

private_rt1 = t.add_resource(ec2.RouteTable(
    "PrivateRouteTable1",
    VpcId=Ref(vpc),
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Private Routes (AZ1)")}]
))

t.add_resource(ec2.Route( 
    "DefaultPrivateRoute1",
    RouteTableId=Ref(private_rt1),
    DestinationCidrBlock="0.0.0.0/0",
    NatGatewayId=Ref(nat_gw1)
))

t.add_resource(ec2.SubnetRouteTableAssociation(
    "PrivateSubnet1RouteTableAssociation",
    RouteTableId=Ref(private_rt1),
    SubnetId=Ref(private_sn1)
))


private_rt2 = t.add_resource(ec2.RouteTable(
    "PrivateRouteTable2",
    VpcId=Ref(vpc),
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Private Routes (AZ2)")}]
))

t.add_resource(ec2.Route( 
    "DefaultPrivateRoute2",
    RouteTableId=Ref(private_rt2),
    DestinationCidrBlock="0.0.0.0/0",
    NatGatewayId=Ref(nat_gw2)
))

t.add_resource(ec2.SubnetRouteTableAssociation(
    "PrivateSubnet2RouteTableAssociation",
    RouteTableId=Ref(private_rt2),
    SubnetId=Ref(private_sn2)
))

# création du groupe de sécurité avec les règles d'ingress 
ingress_rules = [
    # Ports TCP
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="22", ToPort="22", CidrIp="0.0.0.0/0"),    # SSH
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="80", ToPort="80", CidrIp="0.0.0.0/0"),    # HTTP
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="443", ToPort="443", CidrIp="0.0.0.0/0"),  # HTTPS
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="1433", ToPort="1433", CidrIp="0.0.0.0/0"), # MSSQL
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="5432", ToPort="5432", CidrIp="0.0.0.0/0"), # PostgreSQL
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="3306", ToPort="3306", CidrIp="0.0.0.0/0"), # MySQL
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="3389", ToPort="3389", CidrIp="0.0.0.0/0"), # RDP
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="1514", ToPort="1514", CidrIp="0.0.0.0/0"), # OSSEC
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="9200", ToPort="9300", CidrIp="0.0.0.0/0"), # ElasticSearch Range
    ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="53", ToPort="53", CidrIp="0.0.0.0/0"),    # DNS TCP
    # Ports UDP
    ec2.SecurityGroupRule(IpProtocol="udp", FromPort="53", ToPort="53", CidrIp="0.0.0.0/0"),    # DNS UDP
]

sg_ingress = t.add_resource(ec2.SecurityGroup(
    "IngressSecurityGroup",
    GroupName="polystudent-sg",
    GroupDescription="Security group allows required ports (SSH, HTTP, HTTPS, MSSQL, etc...)",
    VpcId=Ref(vpc),
    SecurityGroupIngress=ingress_rules
))


flow_log = t.add_resource(ec2.FlowLog(
    "VPCFlowLog",
    LogDestinationType="s3", 
    LogDestination=Join("", ["arn:aws:s3:::", S3_FLOW_LOG_BUCKET_NAME]), 
    ResourceId=Ref(vpc), 
    ResourceType="VPC",
    TrafficType="REJECT" # enregistre seulement les paquets rejetés
))


lab_role = t.add_resource(iam.Role(
    "LabRole",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    },
    Policies=[],
    Path="/"
))

iam_profile = t.add_resource(iam.InstanceProfile(
    "LabInstanceProfile",
    Path="/",
    Roles=[Ref(lab_role)]
))

AMI_ID_Public = "ami-0abac8735a38475db" # Ubuntu Server 24.04
AMI_ID_Private = "ami-0f8f4e8fb1da4298f" # Windows Server 2025 Base
KEY_NAME = "cle_ssh_tp4" # nous avons généré une nouvelle clé SSH pour le TP4 au préalable

# instance public AZ1
t.add_resource(ec2.Instance(
    "PublicInstanceAZ1",
    ImageId=AMI_ID_Public,
    InstanceType="t3.micro",
    KeyName=KEY_NAME,
    SubnetId=Ref(public_sn1),
    SecurityGroupIds=[Ref(sg_ingress)],
    IamInstanceProfile=Ref(iam_profile),
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Public Server AZ1")}]
))

# instance privée AZ1
t.add_resource(ec2.Instance(
    "PrivateInstanceAZ1",
    ImageId=AMI_ID_Private,
    InstanceType="t3.micro",
    KeyName=KEY_NAME,
    SubnetId=Ref(private_sn1),
    SecurityGroupIds=[Ref(sg_ingress)],
    IamInstanceProfile=Ref(iam_profile),
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Private Server AZ1")}]
))

# instance public AZ2
t.add_resource(ec2.Instance(
    "PublicInstanceAZ2",
    ImageId=AMI_ID_Public,
    InstanceType="t3.micro",
    KeyName=KEY_NAME,
    SubnetId=Ref(public_sn2),
    SecurityGroupIds=[Ref(sg_ingress)],
    IamInstanceProfile=Ref(iam_profile),
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Public Server AZ2")}]
))

# instance privée AZ2
t.add_resource(ec2.Instance(
    "PrivateInstanceAZ2",
    ImageId=AMI_ID_Private,
    InstanceType="t3.micro",
    KeyName=KEY_NAME,
    SubnetId=Ref(private_sn2),
    SecurityGroupIds=[Ref(sg_ingress)],
    IamInstanceProfile=Ref(iam_profile),
    Tags=[{"Key": "Name", "Value": Sub("${EnvironmentName} Private Server AZ2")}]
))

t.add_resource(cloudwatch.Alarm(
    "IngressPacketsAlarm",
    AlarmDescription="Alarme pour le trafic entrant global sur toutes les instances > 1000 pkts/sec.",
    Namespace="AWS/EC2",
    MetricName="NetworkPacketsIn",
    Statistic="Average",
    Period="60",
    EvaluationPeriods="1", 
    Threshold="1000",
    ComparisonOperator="GreaterThanThreshold",
))

t.add_output([
    Output("VPC", Description="A reference to the created VPC", Value=Ref(vpc)),
    Output("PublicSubnets", Description="List of public subnets.",
           Value=Join(",", [Ref(public_sn1), Ref(public_sn2)])),
    Output("PrivateSubnets", Description="List of private subnets.",
           Value=Join(",", [Ref(private_sn1), Ref(private_sn2)])),
    Output("PublicSubnet1", Description="Reference to the public subnet in AZ1.", Value=Ref(public_sn1)),
    Output("PrivateSubnet1", Description="Reference to the private subnet in AZ1.", Value=Ref(private_sn1)),
    Output("PublicSubnet2", Description="Reference to the public subnet in AZ2.", Value=Ref(public_sn2)),
    Output("PrivateSubnet2", Description="Reference to the private subnet in AZ2.", Value=Ref(private_sn2)),
    Output("IngressSecurityGroup", Description="ID of the Ingress Security Group.", Value=Ref(sg_ingress)),
])


# écriture du template dans un fichier YAML
with open("./yaml/vpc3.yaml", 'w') as f:
    f.write(t.to_yaml())

print(f"Fichier généré: ./yaml/vpc3.yaml")