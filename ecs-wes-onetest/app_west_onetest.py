from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    core,
)

# Based on https://aws.amazon.com/blogs/compute/introducing-cloud-native-networking-for-ecs-containers/

app = core.App()
stack = core.Stack(app, "wes-onetest3", env={'region': 'us-east-1','account':'417302553802'})

#ecr_repo="925786249844.dkr.ecr.us-east-1.amazonaws.com/sema4ecr"
ecr_repo_voncweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/voncweb-ecr:latest"
ecr_repo_dispatcher="921279086507.dkr.ecr.us-east-1.amazonaws.com/dispatcherapi-ecr:latest"
ecr_repo_vistaweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/vistaweb-ecr:latest"




tag=[core.CfnTag(key='FundNo',value='114'),core.CfnTag(key='Project',value='Wes-Onetest')]

vpc=ec2.Vpc.from_vpc_attributes(stack,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=core.Fn.import_value('devops-rnd-vpc-VpcID'),
                                private_subnet_ids=[core.Fn.import_value('devops-rnd-vpc-PrivateSubnet1ID'),core.Fn.import_value('devops-rnd-vpc-PrivateSubnet2ID')],
                                                    public_subnet_ids=[core.Fn.import_value('devops-rnd-vpc-PublicSubnet1ID'),core.Fn.import_value('devops-rnd-vpc-PublicSubnet2ID')])




cluster = ecs.Cluster(
    stack, "wes-onetest-ecs",
    vpc=vpc
)
cluster.add_capacity("DefaultAutoScalingGroup",
                     instance_type=ec2.InstanceType("t2.medium"), key_name='aws-eb',max_capacity=2)

# Create a task definition with its own elastic network interface
task_definition = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task",
    #network_mode=ecs.NetworkMode.AWS_VPC,
)

voncweb_container = task_definition.add_container(
    "west-onetest-voncwebserver",
    image=ecs.ContainerImage.from_registry(ecr_repo_voncweb),
    cpu=100,
    memory_limit_mib=256,
    essential=True,
    environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=3000,
    host_port=443,
    protocol=ecs.Protocol.TCP
)
voncweb_container.add_port_mappings(port_mapping)


dispatcher_container = task_definition.add_container(
    "west-onetest-dispatcher",
    image=ecs.ContainerImage.from_registry(ecr_repo_dispatcher),
    cpu=100,
    memory_limit_mib=256,
    essential=True,
    environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=5000,
    host_port=5000,
    protocol=ecs.Protocol.TCP
)
dispatcher_container.add_port_mappings(port_mapping)


vistaweb_container = task_definition.add_container(
    "west-onetest-vistaweb",
    image=ecs.ContainerImage.from_registry(ecr_repo_vistaweb),
    cpu=100,
    memory_limit_mib=256,
    essential=True,
    environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=8080,
    host_port=8080,
    protocol=ecs.Protocol.TCP
)
vistaweb_container.add_port_mappings(port_mapping)





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

security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(8080)
)


# Create the service
service = ecs.Ec2Service(
    stack, "west-onetest-ecs-service",
    cluster=cluster,
    task_definition=task_definition,
    #security_group=security_group
)




# Create ALB
lb = elbv2.ApplicationLoadBalancer(
    stack, "LB",
    vpc=vpc,
    internet_facing=True
)
listener_voncweb = lb.add_listener(
    "voncweblistener",
    port=443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTP
)
listener_dispatcher = lb.add_listener(
    "dispatcherlistener",
    port=5000,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTP
)
listener_vista = lb.add_listener(
    "vistalistener",
    port=8080,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTP
)

health_check = elbv2.HealthCheck(
    interval=core.Duration.seconds(60),
    path="/health",
    timeout=core.Duration.seconds(5)
)

# Attach ALB to ECS Service
listener_voncweb.add_targets(
    "voncweb",
    port=443,
    targets=[service],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

listener_dispatcher.add_targets(
    "dispatcher",
    port=5000,
    targets=[service],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

listener_vista.add_targets(
    "vistaweb",
    port=8080,
    targets=[service],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)


core.CfnOutput(
    stack, "LoadBalancerDNS",
    value=lb.load_balancer_dns_name
)

app.synth()
