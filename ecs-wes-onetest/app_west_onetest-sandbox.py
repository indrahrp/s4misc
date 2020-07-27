from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    core,
)

# Based on https://aws.amazon.com/blogs/compute/introducing-cloud-native-networking-for-ecs-containers/

app = core.App()
stack = core.Stack(app, "wes-onetest1", env={'region': 'us-east-1','account':'921279086507'})

#ecr_repo="925786249844.dkr.ecr.us-east-1.amazonaws.com/sema4ecr"
ecr_repo="921279086507.dkr.ecr.us-east-1.amazonaws.com/voncweb-ecr:latest"



tag=[core.CfnTag(key='FundNo',value='114'),core.CfnTag(key='Project',value='Wes-Onetest')]

vpc=ec2.Vpc.from_vpc_attributes(stack,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=core.Fn.import_value('devops-rnd-vpc-VpcID'),private_subnet_ids=[core.Fn.import_value('devops-rnd-vpc-PrivateSubnet1ID'),core.Fn.import_value('devops-rnd-vpc-PrivateSubnet2ID')])




cluster = ecs.Cluster(
    stack, "wes-onetest-ecs",
    vpc=vpc
)
cluster.add_capacity("DefaultAutoScalingGroup",
                     instance_type=ec2.InstanceType("t2.large"))

# Create a task definition with its own elastic network interface
task_definition = ecs.Ec2TaskDefinition(
    stack, "west-onetest-webserver-task",
    network_mode=ecs.NetworkMode.AWS_VPC,
)

web_container = task_definition.add_container(
    "west-onetest-webserver",
    image=ecs.ContainerImage.from_registry(ecr_repo),
    cpu=100,
    memory_limit_mib=256,
    essential=True,
    environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=80,
    protocol=ecs.Protocol.TCP
)
web_container.add_port_mappings(port_mapping)

# Create a security group that allows HTTP traffic on port 80 for our
# containers without modifying the security group on the instance
security_group = ec2.SecurityGroup(
    stack, "west-onetest-sg",
    vpc=vpc,
    allow_all_outbound=False
)
security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(80)
)

# Create the service
service = ecs.Ec2Service(
    stack, "west-onetest-ecs-service",
    cluster=cluster,
    task_definition=task_definition,
    security_group=security_group
)

app.synth()
