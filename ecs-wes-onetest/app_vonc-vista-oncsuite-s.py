from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    core,
    aws_iam as iam,
    aws_efs as efs
)

# Based on https://aws.amazon.com/blogs/compute/introducing-cloud-native-networking-for-ecs-containers/

App_Name='VoncV-OncSuite-S'
app = core.App()
#stack = core.Stack(app, "onetest", env={'region': 'us-east-1','account':'417302553802'})
stack = core.Stack(app, App_Name, env={'region': 'us-east-1','account':'921279086507'})


#ecr_repo="925786249844.dkr.ecr.us-east-1.amazonaws.com/sema4ecr"
ecr_repo_voncweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/voncweb-ecr:latest"
ecr_repo_dispatcher="921279086507.dkr.ecr.us-east-1.amazonaws.com/dispatcherapi-ecr:latest"
ecr_repo_vistaweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/vistaweb-ecr:latest"
ecr_repo_varsleuth="921279086507.dkr.ecr.us-east-1.amazonaws.com/vistaweb-ecr:latest"
ecr_repo_spliceai="921279086507.dkr.ecr.us-east-1.amazonaws.com/spliceweb-ecr:latest"
#ecr_repo_vistaweb=""
#spliceaiweb
#certificate_arn_sema4='arn:aws:acm:us-east-1:417302553802:certificate/b46a1c06-bc3b-4012-8f47-b2735ceccbc5'
certificate_arn_sema4='arn:aws:acm:us-east-1:921279086507:certificate/1cdc5fa6-0978-4c3c-96fa-ced4188b4fd0'
app_security_group='sg-072a5e0e3cadbbaa5'
app_security_group_import=ec2.SecurityGroup.from_security_group_id(stack,'app_security_group',app_security_group)

#ecr_read_only_policy=iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly')

#managed_policy=iam.ManagedPolicy.from_aws_managed_policy_name





tag=[core.CfnTag(key='FundNo',value='114'),core.CfnTag(key='Project',value='Proj-VONC_VISTA')]


vpc=ec2.Vpc.from_vpc_attributes(stack,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=core.Fn.import_value('SC-921279086507-pp-y3a2eii4lnfzc-VpcID'),
                                private_subnet_ids=[core.Fn.import_value('SC-921279086507-pp-y3a2eii4lnfzc-PrivateSubnet1ID'),core.Fn.import_value('SC-921279086507-pp-y3a2eii4lnfzc-PrivateSubnet2ID')],
                                public_subnet_ids=[core.Fn.import_value('SC-921279086507-pp-y3a2eii4lnfzc-PublicSubnet1ID'),core.Fn.import_value('SC-921279086507-pp-y3a2eii4lnfzc-PublicSubnet2ID')])





amitouse = ec2.MachineImage.lookup(
    name="biornd-ecs-ami-unc"
    #owners=["amazon"]
)
deployment_mode=ecs.DeploymentController
deployment_mode.type=ecs.DeploymentControllerType.CODE_DEPLOY
custom_actions=[

                  "ecr:GetAuthorizationToken",
                  "ecr:BatchCheckLayerAvailability",
                  "ecr:GetDownloadUrlForLayer",
                  "ecr:GetRepositoryPolicy",
                  "ecr:DescribeRepositories",
                  "ecr:ListImages",
                  "ecr:DescribeImages",
                  "ecr:BatchGetImage",
                  "ecr:GetLifecyclePolicy",
                  "ecr:GetLifecyclePolicyPreview",
                  "ecr:ListTagsForResource",
                  "ecr:DescribeImageScanFindings",
                  "kms:*",
                  "ecr:*",
                  "secretsmanager:*"
              ]

custom_policy=iam.PolicyStatement(actions=custom_actions)
custom_policy.add_all_resources()
#custom_policy.add_actions(custom_actions)



security_group = ec2.SecurityGroup(
    stack, App_Name+"-sg",
    vpc=vpc,
    allow_all_outbound=True
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
    ec2.Port.tcp(2049)
)
security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.udp(111)
)
security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(5000)
)

security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(3000)
)

efsvol=efs.FileSystem(stack,App_Name+"_efsvolume",vpc=vpc,file_system_name='wes',security_group=security_group)

efsdns=efsvol.file_system_id+".efs.us-east-1.amazonaws.com"

efs_to_connect="addr=" + efsdns +",nfsvers=4.0,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2"
#efs_to_connect="addr=" + efsvol.file_system_id
##device_set=efsdns+":/"
#driveropts={
#    "type": "nfs",
#    "device":device_set,
#    "o": efs_to_connect
#    #"o": "addr=fs-XXXXXX.efs.us-east-1.amazonaws.com,nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport"

#}

#docker_vol_config=ecs.DockerVolumeConfiguration(driver='local', scope=ecs.Scope.TASK, driver_opts=driveropts, labels=None)

#docker_volume=ecs.Volume(name='docker_vol',docker_volume_configuration=docker_vol_config)

#efs_mount=ecs.MountPoint(container_path='/efs',read_only=True, source_volume='docker_vol')

cluster = ecs.Cluster(
    stack, "wes-ecs",
    vpc=vpc,
    cluster_name=App_Name
)
print ('cluster sec group ',str(type(cluster.autoscaling_group)))
#cluster.add_capacity("DefaultAutoScalingGroup",
#                     instance_type=ec2.InstanceType("c5.xlarge"), key_name='Vonc-Prod-Key',max_capacity=4,machine_image=amitouse,
#                     desired_capacity=2,min_capacity=2)

print ('connections ',str(cluster.connections))
port=ec2.Port(protocol=ec2.Protocol.TCP,string_representation='inbound to container instances', from_port=22, to_port=22)
cluster.connections.add_security_group(app_security_group_import)
cluster.connections.allow_from_any_ipv4(port,'in bound to container instances')

# Create a task definition with its own elastic network interface

task_definition_vistaweb = ecs.FargateTaskDefinition(
    stack, App_Name+"-task-vistaweb",
    memory_limit_mib=8192,
    cpu=4096,
    #volumes=[docker_volume],
    family=App_Name+'-Vista'
)
task_definition_vistaweb.add_to_execution_role_policy(custom_policy)
task_definition_vistaweb.add_to_task_role_policy(custom_policy)
#task_definition_vistaweb.task_role.add_managed_policy(ecr_read_only_policy)
#print ("testk role ",str(taskrole))
#secret_policy.attach_to_role(task_definition_vistaweb.task_role)
#secret_policy.attach_to_role(task_definition_vistaweb.role)
#secret_policy.attach_to_role(task_definition_vistaweb.role)


task_definition_varsleuth = ecs.FargateTaskDefinition(
    stack, App_Name+"-task-varsleuth",
    memory_limit_mib=8192,
    cpu=4096,
    family=App_Name+ "-VarSleuth"
)
task_definition_varsleuth.add_to_execution_role_policy(custom_policy)
task_definition_varsleuth.add_to_task_role_policy(custom_policy)

task_definition_voncweb = ecs.FargateTaskDefinition(
    stack, App_Name + "-task-voncweb",
    memory_limit_mib=8192,
    cpu=4096,
    family=App_Name+"-VISTA-Web"
)
task_definition_voncweb.add_to_execution_role_policy(custom_policy)
task_definition_voncweb.add_to_task_role_policy(custom_policy)

task_definition_dispatcher = ecs.FargateTaskDefinition(
    stack, App_Name+"-task-dispatcher",
    memory_limit_mib=8192,
    cpu=4096,
    family=App_Name+'-Dispatcher'
)

task_definition_dispatcher.add_to_execution_role_policy(custom_policy)
task_definition_dispatcher.add_to_task_role_policy(custom_policy)


task_definition_spliceai = ecs.FargateTaskDefinition(
    stack, App_Name + "-task-spliceai",
    memory_limit_mib=8192,
    cpu=4096,
    #volumes=[docker_volume],
    family=App_Name + '-Spliceai'
)
task_definition_spliceai.add_to_execution_role_policy(custom_policy)
task_definition_spliceai.add_to_task_role_policy(custom_policy)
                                         
voncweb_container = task_definition_voncweb.add_container(
    App_Name + "-vonc-container",
    image=ecs.ContainerImage.from_registry(ecr_repo_voncweb),
    essential=True,
    logging=ecs.LogDriver.aws_logs(stream_prefix=App_Name + "_vonc_logs"),
    #stop_timeout=core.Duration.hours(8)

    #environment= {'USE':'me','LAGI':'ddd'}
)

port_mapping = ecs.PortMapping(
    container_port=3000,
    #host_port=443,
    protocol=ecs.Protocol.TCP
)
voncweb_container.add_port_mappings(port_mapping)


dispatcher_container = task_definition_dispatcher.add_container(
    App_Name + "-dispatcher-container",
    image=ecs.ContainerImage.from_registry(ecr_repo_dispatcher),
    essential=True,
    logging=ecs.LogDriver.aws_logs(stream_prefix=App_Name + "_dispatcher_logs"),
    #stop_timeout=core.Duration.hours(8)

    #environment= {'USE':'me','LAGI':'ddd'}
)
port_mapping = ecs.PortMapping(
    container_port=3000,
    #host_port=5000,
    protocol=ecs.Protocol.TCP
)
dispatcher_container.add_port_mappings(port_mapping)

vistaweb_container = task_definition_vistaweb.add_container(
    App_Name + "-vistaweb-container",
    image=ecs.ContainerImage.from_registry(ecr_repo_vistaweb),
    essential=True,
    environment= {'HG19':'/var/www/html/mydo/hg19/ucsc.hg19.fasta','refSeqVer':'GRCH37','MYDO_DIR':'/var/www/html/mydo/LAGI','TMPDIR':'/tmp'},
    logging=ecs.LogDriver.aws_logs(stream_prefix=App_Name + "_vista_logs"),
    #stop_timeout=core.Duration.hours(8)

)
#vistaweb_container.add_mount_points(efs_mount)

port_mapping = ecs.PortMapping(
    container_port=80,
    #host_port=8080,
    protocol=ecs.Protocol.TCP
)
vistaweb_container.add_port_mappings(port_mapping)


varsleuth_container = task_definition_varsleuth.add_container(
    App_Name + "-varsleuth-container",
    image=ecs.ContainerImage.from_registry(ecr_repo_varsleuth),
    essential=True,
    logging=ecs.LogDriver.aws_logs(stream_prefix=App_Name + "_varsleuth_logs"),
    #stop_timeout=core.Duration.hours(8)
    #environment= {'HG19':'/var/www/html/mydo/hg19/ucsc.hg19.fasta','refSeqVer':'GRCH37','MYDO_DIR':'/var/www/html/mydo/LAGI','TMPDIR':'/tmp'}

)

port_mapping = ecs.PortMapping(
    container_port=80,
    #host_port=8080,
    protocol=ecs.Protocol.TCP
)
varsleuth_container.add_port_mappings(port_mapping)


spliceai_container = task_definition_spliceai.add_container(
    App_Name + "-spliceai-container",
    image=ecs.ContainerImage.from_registry(ecr_repo_varsleuth),
    essential=True,
    logging=ecs.LogDriver.aws_logs(stream_prefix=App_Name + "_spliceai_logs"),
    #stop_timeout=core.Duration.hours(8)
    #environment= {'HG19':'/var/www/html/mydo/hg19/ucsc.hg19.fasta','refSeqVer':'GRCH37','MYDO_DIR':'/var/www/html/mydo/LAGI','TMPDIR':'/tmp'}

)

port_mapping = ecs.PortMapping(
    container_port=80,
    #host_port=8080,
    protocol=ecs.Protocol.TCP
)
spliceai_container.add_port_mappings(port_mapping)







# Create a security group that allows HTTP traffic on port 80 for our
# containers without modifying the security group on the instance




# Create the service



service_voncweb = ecs.FargateService(
    stack, App_Name + "-ecs-service-voncweb",
    cluster=cluster,
    platform_version=ecs.FargatePlatformVersion.VERSION1_4,
    task_definition=task_definition_voncweb,
    deployment_controller=deployment_mode,
    desired_count=2,
    security_group=security_group,
    service_name=App_Name + '-Vonc'

)

service_dispatcher = ecs.FargateService(
    stack, App_Name + "-ecs-service-dispatcher",
    cluster=cluster,
    platform_version=ecs.FargatePlatformVersion.VERSION1_4,
    task_definition=task_definition_dispatcher,
    deployment_controller=deployment_mode,
    desired_count=1,
    security_group=security_group,
    service_name=App_Name + "-Dispatcher"
)

service_vistaweb = ecs.FargateService(
    stack, App_Name + "-ecs-service-vistaweb",
    cluster=cluster,
    platform_version=ecs.FargatePlatformVersion.VERSION1_4,
    task_definition=task_definition_vistaweb,
    deployment_controller=deployment_mode,
    desired_count=1,
    security_group=security_group,
    service_name=App_Name + '-Vista'
    #health_check_grace_period=core.Duration.minutes(15)

)

service_varsleuth = ecs.FargateService(
    stack, App_Name + "-ecs-service-varsleuth",
    cluster=cluster,
    platform_version=ecs.FargatePlatformVersion.VERSION1_4,
    task_definition=task_definition_varsleuth,
    deployment_controller=deployment_mode,
    #placement_constraints=[ecs.PlacementConstraint.distinct_instances()],
    desired_count=1,
    security_group=security_group,
    service_name=App_Name + '-VarSleuth'

)


service_spliceai = ecs.FargateService(
    stack, App_Name + "-ecs-service-spliceai",
    cluster=cluster,
    platform_version=ecs.FargatePlatformVersion.VERSION1_4,
    task_definition=task_definition_spliceai,
    deployment_controller=deployment_mode,
    #placement_constraints=[ecs.PlacementConstraint.distinct_instances()],
    desired_count=1,
    security_group=security_group,
    service_name=App_Name + '-SpliceAI'

)





# Create ALB

lb_voncweb = elbv2.ApplicationLoadBalancer(
    stack, App_Name + "_lb_voncweb",
    load_balancer_name=App_Name + '-Vonc-ELB',
    vpc=vpc,
    internet_facing=True
)

lb_dispatcher = elbv2.ApplicationLoadBalancer(
    stack, App_Name + "_lb_dispatcher",
    load_balancer_name=App_Name + '-Dispatcher-ELB',
    vpc=vpc,
    internet_facing=True
)


lb_vista = elbv2.ApplicationLoadBalancer(
    stack, App_Name + "_lb_vista",
    load_balancer_name=App_Name + '-Vista-ELB',
    vpc=vpc,
    internet_facing=True
)


lb_varsleuth = elbv2.ApplicationLoadBalancer(
    stack, App_Name + "_lb_varleuth",
    vpc=vpc,
    load_balancer_name=App_Name + '-Varsleuth-ELB',
    internet_facing=True
)



lb_spliceai = elbv2.ApplicationLoadBalancer(
    stack, App_Name + "_lb_spliceai",
    vpc=vpc,
    load_balancer_name=App_Name + '-SpliceAI-ELB',
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



listener_spliceai = lb_spliceai.add_listener(
    "spliceailistener",
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


listener_spliceai_green = lb_spliceai.add_listener(
    "spliceailistener_green",
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
    target_group_name=App_Name + '-VoncWeb-Bl',
    port=443,
    targets=[service_voncweb],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTPS
)

listener_dispatcher.add_targets(
    "dispatcher",
    target_group_name=App_Name + '-Dispatcher-Bl',
    port=3000,
    targets=[service_dispatcher],
    health_check=dispatcher_health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

listener_vista.add_targets(
    "vistaweb_target",
    target_group_name=App_Name + '-Vista-Bl',
    port=80,
    targets=[service_vistaweb],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

listener_varsleuth.add_targets(
    "varsleuth_target",
    target_group_name=App_Name + '-Varsleuth-Bl',
    port=80,
    targets=[service_varsleuth],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)


listener_spliceai.add_targets(
    "spliceai_target",
    target_group_name=App_Name + '-SpliceAI-Bl',
    port=80,
    targets=[service_spliceai],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)


voncweb_target_green=elbv2.ApplicationTargetGroup(stack,"voncweb_target_green",target_group_name=App_Name +'-VoncWeb-Gr',port=443,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_voncweb_green.add_target_groups("voncweb_green",target_groups=[voncweb_target_green])


dispatcher_target_green=elbv2.ApplicationTargetGroup(stack,"dispatcher_target_green",target_group_name=App_Name + '-Dispatcher-Gr',port=3000,protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=dispatcher_health_check,vpc=vpc)
listener_dispatcher_green.add_target_groups("dispatcher_green",target_groups=[dispatcher_target_green])

vistaweb_target_green=elbv2.ApplicationTargetGroup(stack,"vistaweb_target_green",port=80,target_group_name=App_Name + '-Vista-Gr',protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_vista_green.add_target_groups("vistaweb_green",target_groups=[vistaweb_target_green])


varsleuth_target_green=elbv2.ApplicationTargetGroup(stack,"varsleuth_target_green",port=80,target_group_name=App_Name + '-Varsleuth-Gr',protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_varsleuth_green.add_target_groups("varsleuth_green",target_groups=[varsleuth_target_green])



spliceai_target_green=elbv2.ApplicationTargetGroup(stack,"spliceai_target_green",port=80,target_group_name=App_Name + '-SpliceAI-Gr',protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_spliceai_green.add_target_groups("spliceai_green",target_groups=[spliceai_target_green])

#listener_vista_green.add_targets(
#    "vistaweb_green_target",
#    port=80,
#    #targets=[service_vistaweb],
#    health_check=health_check,
#    protocol=elbv2.ApplicationProtocol.HTTP
#)




core.CfnOutput(
    stack, App_Name + "'-LoadBalancerDNS_voncweb",
    value=lb_voncweb.load_balancer_dns_name
)

core.CfnOutput(
    stack, App_Name + "-LoadBalancerDNS_dispatcher",
    value=lb_dispatcher.load_balancer_dns_name
)


core.CfnOutput(
    stack, App_Name + "-LoadBalancerDNS_vista",
    value=lb_vista.load_balancer_dns_name
)

core.CfnOutput(
    stack, App_Name + "LoadBalancerDNS_varsleuth",
    value=lb_varsleuth.load_balancer_dns_name
)


core.CfnOutput(
    stack, App_Name + "LoadBalancerDNS_spliceai",
    value=lb_varsleuth.load_balancer_dns_name
)







app.synth()
