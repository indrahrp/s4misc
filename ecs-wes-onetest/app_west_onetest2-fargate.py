from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    core,
)

# Based on https://aws.amazon.com/blogs/compute/introducing-cloud-native-networking-for-ecs-containers/

app = core.App()
stack = core.Stack(app, "wes-onetest3a", env={'region': 'us-east-1','account':'417302553802'})

#ecr_repo="925786249844.dkr.ecr.us-east-1.amazonaws.com/sema4ecr"
ecr_repo_voncweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/voncweb-ecr:latest"
ecr_repo_dispatcher="921279086507.dkr.ecr.us-east-1.amazonaws.com/dispatcherapi-ecr:latest"
ecr_repo_vistaweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/vistaweb-ecr:latest"




tag=[core.CfnTag(key='FundNo',value='114'),core.CfnTag(key='Project',value='Wes-Onetest')]

vpc=ec2.Vpc.from_vpc_attributes(stack,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=core.Fn.import_value('devops-rnd-vpc-VpcID'),
                                private_subnet_ids=[core.Fn.import_value('devops-rnd-vpc-PrivateSubnet1ID'),core.Fn.import_value('devops-rnd-vpc-PrivateSubnet2ID')],
                                public_subnet_ids=[core.Fn.import_value('devops-rnd-vpc-PublicSubnet1ID'),core.Fn.import_value('devops-rnd-vpc-PublicSubnet2ID')])

amitouse = ec2.MachineImage.lookup(
    name="biornd-ecs-ami"
    #owners=["amazon"]
)
deployment_mode=ecs.DeploymentController
deployment_mode.type=ecs.DeploymentControllerType.CODE_DEPLOY

certificate_arn_sema4='arn:aws:acm:us-east-1:417302553802:certificate/b46a1c06-bc3b-4012-8f47-b2735ceccbc5'



cluster = ecs.Cluster(
    stack, "wes-onetest-ecs",
    vpc=vpc
)
cluster.add_capacity("DefaultAutoScalingGroup",
                     instance_type=ec2.InstanceType("t2.medium"), key_name='aws-eb',max_capacity=3,machine_image=amitouse)

# Create a task definition with its own elastic network interface
task_definition_voncweb = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task-voncweb"
    #network_mode=ecs.NetworkMode.AWS_VPC,
)

task_definition_dispatcher = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task-dispatcher"
    #network_mode=ecs.NetworkMode.AWS_VPC,
)

task_definition_vistaweb = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task-vistaweb"
    #network_mode=ecs.NetworkMode.AWS_VPC,
)

voncweb_container = task_definition_voncweb.add_container(
    "west-onetest-voncwebserver",
    image=ecs.ContainerImage.from_registry(ecr_repo_voncweb),
    cpu=16,
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


dispatcher_container = task_definition_dispatcher.add_container(
    "west-onetest-dispatcher",
    image=ecs.ContainerImage.from_registry(ecr_repo_dispatcher),
    cpu=16,
    memory_limit_mib=256,
    essential=True,
    environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=3000,
    host_port=5000,
    protocol=ecs.Protocol.TCP
)
dispatcher_container.add_port_mappings(port_mapping)


vistaweb_container = task_definition_vistaweb.add_container(
    "west-onetest-vistaweb",
    image=ecs.ContainerImage.from_registry(ecr_repo_vistaweb),
    cpu=16,
    memory_limit_mib=256,
    essential=True,
    environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=80,
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
service_voncweb = ecs.Ec2Service(
    stack, "west-onetest-ecs-service-voncweb",
    cluster=cluster,
    task_definition=task_definition_voncweb,
    deployment_controller=deployment_mode

    #security_group=security_group
)

service_dispatcher = ecs.Ec2Service(
    stack, "west-onetest-ecs-service-dispatcher",
    cluster=cluster,
    task_definition=task_definition_dispatcher,
    deployment_controller=deployment_mode
    #security_group=security_group
)

service_vistaweb = ecs.Ec2Service(
    stack, "west-onetest-ecs-service-vistaweb",
    cluster=cluster,
    task_definition=task_definition_vistaweb,
    deployment_controller=deployment_mode
    #security_group=security_group
)





# Create ALB
lb_voncweb = elbv2.ApplicationLoadBalancer(
    stack, "lb_voncweb",
    vpc=vpc,
    internet_facing=True
)

lb_dispatcher = elbv2.ApplicationLoadBalancer(
    stack, "lb_dispatcher",
    vpc=vpc,
    internet_facing=True
)

lb_vista = elbv2.ApplicationLoadBalancer(
    stack, "lb_vista",
    vpc=vpc,
    internet_facing=True
)
listener_voncweb = lb_voncweb.add_listener(
    "voncweblistener",
    port=443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTPS,
    certificate_arns=[certificate_arn_sema4]
)
listener_dispatcher = lb_dispatcher.add_listener(
    "dispatcherlistener",
    port=5000,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTP,
    #certificate_arns=[certificate_arn_sema4]
)
listener_vista = lb_vista.add_listener(
    "vistalistener",
    port=443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTPS,
    certificate_arns=[certificate_arn_sema4]
)

health_check = elbv2.HealthCheck(
    interval=core.Duration.seconds(60),
    path="/",
    timeout=core.Duration.seconds(5)
)

# Attach ALB to ECS Service
listener_voncweb.add_targets(
    "voncweb",
    port=443,
    targets=[service_voncweb],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTPS
)

listener_dispatcher.add_targets(
    "dispatcher",
    port=5000,
    targets=[service_dispatcher],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

listener_vista.add_targets(
    "vistaweb",
    port=8080,
    targets=[service_vistaweb],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)




core.CfnOutput(
    stack, "LoadBalancerDNS_voncweb",
    value=lb_voncweb.load_balancer_dns_name
)


core.CfnOutput(
    stack, "LoadBalancerDNS_vista",
    value=lb_vista.load_balancer_dns_name
)


core.CfnOutput(
    stack, "LoadBalancerDNS_dispatcher",
    value=lb_dispatcher.load_balancer_dns_name
)



app.synth()
