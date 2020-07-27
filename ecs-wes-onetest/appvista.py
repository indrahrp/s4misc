from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    core,
)

# Based on https://aws.amazon.com/blogs/compute/introducing-cloud-native-networking-for-ecs-containers/

app = core.App()
stack = core.Stack(app, "ec2-service-with-task-networking")


tag=[core.CfnTag(key='FundNo',value='114'),core.CfnTag(key='Project',value='Wes-Onetest')]
#secgroup=['sg-06c3e84ede99c1818']
#vpc=ec2.Vpc.from_lookup( self,'vpctouse',vpc_id='vpc-00c9250b0605cd368')
vpc=ec2.Vpc.from_lookup( self,'vpctouse',vpc_id='vpc-00c9250b0605cd368')
#vpc=ec2.Vpc.from_vpc_attributes(self,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=core.Fn.import_value('indravpcid'),public_subnet_ids=[core.Fn.import_value('sema4testvpc-PublicSubnet1ID'),core.Fn.import_value('sema4testvpc-PublicSubnet12D')])
#subnetvpc=vpc.select_subnets(self,'subnettouse',subnets=subnetlist)
#subnetused=ec2.SubnetSelection(subnets=subnetvpc)
#subnetused=vpc.public_subnets
#print ("subnetused ",str(subnetused))
#for sub in subnetused:
#    print ("subnetused ",str(sub.subnet_id))
print ("vpc id is ",vpc.vpc_id)




cluster = ecs.Cluster(
    stack, "awsvpc-ecs-demo-cluster",
    vpc=vpc
)
cluster.add_capacity("DefaultAutoScalingGroup",
                     instance_type=ec2.InstanceType("t2.micro"))

# Create a task definition with its own elastic network interface
task_definition = ecs.Ec2TaskDefinition(
    stack, "nginx-awsvpc",
    network_mode=ecs.NetworkMode.AWS_VPC,
)

web_container = task_definition.add_container(
    "nginx",
    image=ecs.ContainerImage.from_registry("nginx:latest"),
    cpu=100,
    memory_limit_mib=256,
    essential=True
)
port_mapping = ecs.PortMapping(
    container_port=80,
    protocol=ecs.Protocol.TCP
)
web_container.add_port_mappings(port_mapping)

# Create a security group that allows HTTP traffic on port 80 for our
# containers without modifying the security group on the instance
security_group = ec2.SecurityGroup(
    stack, "nginx--7623",
    vpc=vpc,
    allow_all_outbound=False
)
security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(80)
)

# Create the service
service = ecs.Ec2Service(
    stack, "awsvpc-ecs-demo-service",
    cluster=cluster,
    task_definition=task_definition,
    security_group=security_group
)

app.synth()
