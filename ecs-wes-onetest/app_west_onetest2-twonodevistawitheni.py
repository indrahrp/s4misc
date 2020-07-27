from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    core,
)

# Based on https://aws.amazon.com/blogs/compute/introducing-cloud-native-networking-for-ecs-containers/

app = core.App()
stack = core.Stack(app, "wes-vistaall-four", env={'region': 'us-east-1','account':'417302553802'})

#ecr_repo="925786249844.dkr.ecr.us-east-1.amazonaws.com/sema4ecr"
ecr_repo_voncweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/voncweb-ecr:latest"
ecr_repo_dispatcher="921279086507.dkr.ecr.us-east-1.amazonaws.com/dispatcherapi-ecr:latest"
ecr_repo_vistaweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/vistaweb-ecr:latest"
ecr_repo_varsleuth="921279086507.dkr.ecr.us-east-1.amazonaws.com/vistaweb-ecr:latest"
#ecr_repo_vistaweb=""




tag=[core.CfnTag(key='FundNo',value='114'),core.CfnTag(key='Project',value='Wes-Onetest')]

#vpc=ec2.Vpc.from_vpc_attributes(stack,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=core.Fn.import_value('devops-rnd-vpc-VpcID'),
#                                private_subnet_ids=[core.Fn.import_value('devops-rnd-vpc-PrivateSubnet1ID'),core.Fn.import_value('devops-rnd-vpc-PrivateSubnet2ID')],
#                                public_subnet_ids=[core.Fn.import_value('devops-rnd-vpc-PublicSubnet1ID'),core.Fn.import_value('devops-rnd-vpc-PublicSubnet2ID')])



vpc=ec2.Vpc.from_vpc_attributes(stack,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=core.Fn.import_value('sema4testvpc-VpcID'),
                                private_subnet_ids=[core.Fn.import_value('sema4testvpc-PrivateSubnet1ID'),core.Fn.import_value('sema4testvpc-PrivateSubnet2ID')],
                                public_subnet_ids=[core.Fn.import_value('sema4testvpc-PublicSubnet1ID'),core.Fn.import_value('sema4testvpc-PublicSubnet2ID')])







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
                     instance_type=ec2.InstanceType("c5.xlarge"), key_name='aws-eb',max_capacity=4,machine_image=amitouse,
                     desired_capacity=2,min_capacity=2)

# Create a task definition with its own elastic network interface


task_definition_vistaweb = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task-vistaweb",
    network_mode=ecs.NetworkMode.AWS_VPC
)

task_definition_varsleuth = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task-varsleuth",
    network_mode=ecs.NetworkMode.AWS_VPC
)

task_definition_voncweb = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task-voncweb",
    network_mode=ecs.NetworkMode.AWS_VPC,
)

task_definition_dispatcher = ecs.Ec2TaskDefinition(
    stack, "west-onetest-task-dispatcher",
    network_mode=ecs.NetworkMode.AWS_VPC,
)

voncweb_container = task_definition_voncweb.add_container(
    "west-onetest-voncwebserver",
    image=ecs.ContainerImage.from_registry(ecr_repo_voncweb),
    cpu=16,
    memory_limit_mib=256,
    essential=True,
    #environment= {'USE':'me','LAGI':'ddd'}
)

port_mapping = ecs.PortMapping(
    container_port=3000,
    #host_port=443,
    protocol=ecs.Protocol.TCP
)
voncweb_container.add_port_mappings(port_mapping)


dispatcher_container = task_definition_dispatcher.add_container(
    "west-onetest-dispatcher",
    image=ecs.ContainerImage.from_registry(ecr_repo_dispatcher),
    cpu=16,
    memory_limit_mib=256,
    essential=True,
    #environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=3000,
    #host_port=5000,
    protocol=ecs.Protocol.TCP
)
dispatcher_container.add_port_mappings(port_mapping)

vistaweb_container = task_definition_vistaweb.add_container(
    "west-onetest-vistaweb",
    image=ecs.ContainerImage.from_registry(ecr_repo_vistaweb),
    cpu=16,
    memory_limit_mib=256,
    essential=True,
    environment= {'HG19':'/var/www/html/mydo/hg19/ucsc.hg19.fasta','refSeqVer':'GRCH37','MYDO_DIR':'/var/www/html/mydo/LAGI','TMPDIR':'/tmp'}

)

port_mapping = ecs.PortMapping(
    container_port=80,
    #host_port=8080,
    protocol=ecs.Protocol.TCP
)
vistaweb_container.add_port_mappings(port_mapping)


varsleuth_container = task_definition_varsleuth.add_container(
    "west-onetest-varsleuth",
    image=ecs.ContainerImage.from_registry(ecr_repo_varsleuth),
    cpu=16,
    memory_limit_mib=256,
    essential=True,
    #environment= {'HG19':'/var/www/html/mydo/hg19/ucsc.hg19.fasta','refSeqVer':'GRCH37','MYDO_DIR':'/var/www/html/mydo/LAGI','TMPDIR':'/tmp'}

)

port_mapping = ecs.PortMapping(
    container_port=80,
    #host_port=8080,
    protocol=ecs.Protocol.TCP
)
varsleuth_container.add_port_mappings(port_mapping)





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

security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(443)
)

security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(5000)
)

security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(3000)
)



# Create the service

service_voncweb = ecs.Ec2Service(
    stack, "west-onetest-ecs-service-voncweb",
    cluster=cluster,
    task_definition=task_definition_voncweb,
    deployment_controller=deployment_mode,
    desired_count=1,
    security_group=security_group
)

service_dispatcher = ecs.Ec2Service(
    stack, "west-onetest-ecs-service-dispatcher",
    cluster=cluster,
    task_definition=task_definition_dispatcher,
    deployment_controller=deployment_mode,
    desired_count=1,
    security_group=security_group
)

service_vistaweb = ecs.Ec2Service(
    stack, "west-onetest-ecs-service-vistaweb",
    cluster=cluster,
    task_definition=task_definition_vistaweb,
    deployment_controller=deployment_mode,
    desired_count=1,
    security_group=security_group
)

service_varsleuth = ecs.Ec2Service(
    stack, "west-onetest-ecs-service-varsleuth",
    cluster=cluster,
    task_definition=task_definition_varsleuth,
    deployment_controller=deployment_mode,
    #placement_constraints=[ecs.PlacementConstraint.distinct_instances()],
    desired_count=1,
    security_group=security_group
)






# Create ALB

lb_voncweb = elbv2.ApplicationLoadBalancer(
    stack, "lb_voncweb",
    load_balancer_name='VoncWeb-ELB',
    vpc=vpc,
    internet_facing=True
)

lb_dispatcher = elbv2.ApplicationLoadBalancer(
    stack, "lb_dispatcher",
    load_balancer_name='Dispatcher-ELB',
    vpc=vpc,
    internet_facing=True
)


lb_vista = elbv2.ApplicationLoadBalancer(
    stack, "lb_vista",
    load_balancer_name='Vista-ELB',
    vpc=vpc,
    internet_facing=True
)


lb_varsleuth = elbv2.ApplicationLoadBalancer(
    stack, "lb_varleuth",
    vpc=vpc,
    load_balancer_name='Varsleuth-ELB',
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

listener_varsleuth = lb_varsleuth.add_listener(
    "varsleuthlistener",
    port=443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTPS,
    certificate_arns=[certificate_arn_sema4]
)


listener_voncweb_green = lb_voncweb.add_listener(
    "voncweblistener_green",
    port=8443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTPS,
    certificate_arns=[certificate_arn_sema4]
)

listener_dispatcher_green = lb_dispatcher.add_listener(
    "dispatcherlistener_green",
    port=6000,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTP,
    #certificate_arns=[certificate_arn_sema4]
)




listener_vista_green = lb_vista.add_listener(
    "vistalistener_green",
    port=8443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTPS,
    certificate_arns=[certificate_arn_sema4]
)


listener_varsleuth_green = lb_varsleuth.add_listener(
    "varsleuthlistener_green",
    port=8443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTPS,
    certificate_arns=[certificate_arn_sema4]
)
health_check = elbv2.HealthCheck(
    interval=core.Duration.seconds(60),
    path="/",
    timeout=core.Duration.seconds(5)
)


dispatcher_health_check = elbv2.HealthCheck(
    interval=core.Duration.seconds(60),
    path="/getallpatients",
    timeout=core.Duration.seconds(5)
)

# Attach ALB to ECS Service

listener_voncweb.add_targets(
    "voncweb",
    target_group_name='VoncWeb-Blue',
    port=443,
    targets=[service_voncweb],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTPS
)

listener_dispatcher.add_targets(
    "dispatcher",
    target_group_name='Dispatcher-Blue',
    port=3000,
    targets=[service_dispatcher],
    health_check=dispatcher_health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

listener_vista.add_targets(
    "vistaweb_target",
    target_group_name='Vista-Blue',
    port=80,
    targets=[service_vistaweb],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

listener_varsleuth.add_targets(
    "varsleuth_target",
    target_group_name='Varsleuth-Blue',
    port=80,
    targets=[service_varsleuth],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)


voncweb_target_green=elbv2.ApplicationTargetGroup(stack,"voncweb_target_green",target_group_name='VoncWeb-Green',port=443,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_voncweb_green.add_target_groups("voncweb_green",target_groups=[voncweb_target_green])


dispatcher_target_green=elbv2.ApplicationTargetGroup(stack,"dispatcher_target_green",target_group_name='Dispatcher-Green',port=3000,protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=dispatcher_health_check,vpc=vpc)
listener_dispatcher_green.add_target_groups("dispatcher_green",target_groups=[dispatcher_target_green])

vistaweb_target_green=elbv2.ApplicationTargetGroup(stack,"vistaweb_target_green",port=80,target_group_name='Vista-Green',protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_vista_green.add_target_groups("vistaweb_green",target_groups=[vistaweb_target_green])


varsleuth_target_green=elbv2.ApplicationTargetGroup(stack,"varsleuth_target_green",port=80,target_group_name='Varsleuth-Green',protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_varsleuth_green.add_target_groups("varsleuth_green",target_groups=[varsleuth_target_green])

#listener_vista_green.add_targets(
#    "vistaweb_green_target",
#    port=80,
#    #targets=[service_vistaweb],
#    health_check=health_check,
#    protocol=elbv2.ApplicationProtocol.HTTP
#)




core.CfnOutput(
    stack, "LoadBalancerDNS_voncweb",
    value=lb_voncweb.load_balancer_dns_name
)

core.CfnOutput(
    stack, "LoadBalancerDNS_dispatcher",
    value=lb_dispatcher.load_balancer_dns_name
)


core.CfnOutput(
    stack, "LoadBalancerDNS_vista",
    value=lb_vista.load_balancer_dns_name
)

core.CfnOutput(
    stack, "LoadBalancerDNS_varsleuth",
    value=lb_varsleuth.load_balancer_dns_name
)






app.synth()
