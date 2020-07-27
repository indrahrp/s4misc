from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    core,
    aws_iam as iam,
    aws_efs as efs
)

# Based on https://aws.amazon.com/blogs/compute/introducing-cloud-native-networking-for-ecs-containers/


app = core.App()
#stack = core.Stack(app, "onetest", env={'region': 'us-east-1','account':'417302553802'})
stack = core.Stack(app, "vista-temp", env={'region': 'us-east-1','account':'921279086507'})


#ecr_repo="925786249844.dkr.ecr.us-east-1.amazonaws.com/sema4ecr"
ecr_repo_voncweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/voncweb-ecr:latest"
ecr_repo_dispatcher="921279086507.dkr.ecr.us-east-1.amazonaws.com/dispatcherapi-ecr:latest"
ecr_repo_vistaweb="921279086507.dkr.ecr.us-east-1.amazonaws.com/s4-hc-vista-farget-ecr-s"
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





tag=[core.CfnTag(key='FundNo',value='114'),core.CfnTag(key='Project',value='VONC_VISTA')]


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
    stack, "VONC_VISTA-sg",
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
    ec2.Port.tcp(5000)
)

security_group.add_ingress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(3000)
)

cluster = ecs.Cluster(
    stack, "wes-ecs",
    vpc=vpc,
    cluster_name='vista_temp'
)
print ('cluster sec group ',str(type(cluster.autoscaling_group)))
cluster.add_capacity("DefaultAutoScalingGroup",
                     instance_type=ec2.InstanceType("c5.xlarge"), key_name='Vonc-Prod-Key',max_capacity=4,machine_image=amitouse,
                     desired_capacity=2,min_capacity=2)

print ('connections ',str(cluster.connections))
port=ec2.Port(protocol=ec2.Protocol.TCP,string_representation='inbound to container instances', from_port=22, to_port=22)
cluster.connections.add_security_group(app_security_group_import)
cluster.connections.allow_from_any_ipv4(port,'in bound to container instances')

# Create a task definition with its own elastic network interface

task_definition_vistaweb = ecs.Ec2TaskDefinition(
    stack, "VONC_VISTA-task-vistaweb",
    network_mode=ecs.NetworkMode.AWS_VPC,
    family='VONC_VISTA-Vista'
)
task_definition_vistaweb.add_to_execution_role_policy(custom_policy)
task_definition_vistaweb.add_to_task_role_policy(custom_policy)
#task_definition_vistaweb.task_role.add_managed_policy(ecr_read_only_policy)
#print ("testk role ",str(taskrole))
#secret_policy.attach_to_role(task_definition_vistaweb.task_role)
#secret_policy.attach_to_role(task_definition_vistaweb.role)
#secret_policy.attach_to_role(task_definition_vistaweb.role)


vistaweb_container = task_definition_vistaweb.add_container(
    "VONC_VISTA-vistaweb-container",
    image=ecs.ContainerImage.from_registry(ecr_repo_vistaweb),
    cpu=16,
    memory_limit_mib=256,
    essential=True,
    environment= {'HG19':'/var/www/html/mydo/hg19/ucsc.hg19.fasta','refSeqVer':'GRCH37','MYDO_DIR':'/var/www/html/mydo/LAGI','TMPDIR':'/tmp'},
    logging=ecs.LogDriver.aws_logs(stream_prefix="VONC_VISTA_vista_logs"),
    privileged=True,
    #stop_timeout=core.Duration.hours(8)

)

port_mapping = ecs.PortMapping(
    container_port=80,
    #host_port=8080,
    protocol=ecs.Protocol.TCP
)
vistaweb_container.add_port_mappings(port_mapping)


service_vistaweb = ecs.Ec2Service(
    stack, "VONC_VISTA-ecs-service-vistaweb",
    cluster=cluster,
    task_definition=task_definition_vistaweb,
    deployment_controller=deployment_mode,
    desired_count=1,
    security_group=security_group,
    service_name='VONC_VISTA-Vista')
    #health_check_grace_period=core.Duration.minutes(15)




lb_vista = elbv2.ApplicationLoadBalancer(
    stack, "VONC_VISTA_lb_vista",
    load_balancer_name='Vista-temp-ELB',
    vpc=vpc,
    internet_facing=True
)

listener_vista = lb_vista.add_listener(
    "vistalistener",
    port=443,
    open=True,
    protocol=elbv2.ApplicationProtocol.HTTPS,
    certificate_arns=[certificate_arn_sema4]
)




listener_vista_green = lb_vista.add_listener(
    "vistalistener_green",
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

listener_vista.add_targets(
    "vistaweb_target",
    target_group_name='Vista-temp-blue',
    port=80,
    targets=[service_vistaweb],
    health_check=health_check,
    protocol=elbv2.ApplicationProtocol.HTTP
)

vistaweb_target_green=elbv2.ApplicationTargetGroup(stack,"vistaweb_target_green",port=80,target_group_name='Vista-temp-Green',protocol=elbv2.ApplicationProtocol.HTTP,target_type=elbv2.TargetType.IP,health_check=health_check,vpc=vpc)
listener_vista_green.add_target_groups("vistaweb_green",target_groups=[vistaweb_target_green])





core.CfnOutput(
    stack, "Vista-temp-LoadBalancerDNS_vista",
    value=lb_vista.load_balancer_dns_name
)







app.synth()
