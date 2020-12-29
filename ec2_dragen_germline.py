
import os
import json
import logging
import argparse
import boto3
import botocore
import urllib2
import botocore
import sys
import time
import signal




account_id='386451404987'
image_id='ami-0e33c66ac96a8bee4'
instance_type='f1.2xlarge'
security_group_ids=['sg-0f1619fec991ca173']
subnet_id='subnet-0827b39956a5379ac'
key_name='aws-eb'
tag_name='dragen_ec2'
tag_name_value='germline_dragen'
#account_id='386451404987'
ec2=boto3.resource('ec2')
ec2_cl=boto3.client('ec2')



def main():
    ##python  deploy_cf.py --name test --templatefile Sema4-ITAdmin_Role.yaml --params "BucketName=s4-research-sanofi-dev&ITLambda=ITAdmin_Libraries"
    #Account_Session.initialize()
    parser = argparse.ArgumentParser()
    parser.add_argument('--dragen_terminate_ec2',action="store_true", required=False,
                        help='--dragen_terminate_ec2')

    parser.add_argument('--dragen_create_ec2', action="store_true", required=False,
                        help='--dragen_create_ec2')
    parser.add_argument('--dragen_status_ec2', action="store_true", required=False,
                        help='--dragen_status_ec2')
    parser.add_argument('--dragen_stop_ec2', action="store_true", required=False,
                        help='--dragen_stop_ec2')
    parser.add_argument('--dragen_start_ec2', action="store_true", required=False,
                        help='--dragen_start_ec2')
    args = parser.parse_args()
    #print "args "+ str(args)
    if args.dragen_terminate_ec2:
        action_ec2(action='terminate')
        #print "in aotherremoving deploylist"
    elif args.dragen_create_ec2:
        #print "removing deploylist"
       create_ec2()
    elif args.dragen_status_ec2:
        #print "removing deploylist"
        find_ec2()
    elif args.dragen_stop_ec2:
        #print "removing deploylist"
        action_ec2(action='stop')
    elif args.dragen_start_ec2:
        #print "removing deploylist"
        action_ec2(action='start')

def create_ec2():

    devlist=[


        {
            'DeviceName': '/dev/xvda',
            'Ebs': {
                #'SnapshotId': 'snap-00fbad7ef93036e9a',
                'VolumeType': 'gp2',
                'Encrypted': True,
                'VolumeSize': 8
            }
        },
        {
            'DeviceName': '/dev/nvme0n1',
            'Ebs': {
                #'SnapshotId': 'snap-00fbad7ef93036e9a',
                #'VolumeType': 'gp2',
                'Encrypted': True,
                'VolumeSize': 10
            }
        }
    ]






    instance=ec2.create_instances(
        #BlockDeviceMappings=devlist,
        ImageId=image_id,
        InstanceType=instance_type,
        MaxCount=1,
        MinCount=1,
        SecurityGroupIds=security_group_ids,
        SubnetId=subnet_id,
        KeyName=key_name,
        TagSpecifications=[{
                            'ResourceType':'instance',
                            'Tags':
                                [
                                    {'Key':tag_name,
                                       'Value':tag_name_value}
                                ]
        }
        ]



)

def find_ec2():
    instance_list=[]

    response=ec2_cl.describe_instances(
        Filters=[
            {
             'Name':'tag:' + tag_name,
             'Values':[tag_name_value]
             }

        ]
    )
    #print str(response)
    resp=response['Reservations']
    print str(len(resp))
    #print "respin "+ str(response)
    for resp_inst in resp:
        resp_item=resp_inst['Instances'][0]
        tag_assigned=resp_item['Tags']
        tag_attached=[ itm for  itm in  tag_assigned if itm['Key'] == tag_name ]
        ##print "the instance " + str(tag_attached) + ' With Instance Id : ' +  resp_item + ' Launch Time ' + str(resp_item['LaunchTime']) +  \
        ##' status is  ' + resp_item['State']['Name']

        print "the instance with Id : " +   resp_item['InstanceId'] + ' with tag ' + str(tag_attached) + ' Launch Time ' + str(resp_item['LaunchTime']) + ' status is  ' + resp_item['State']['Name']
        instance_list.append( [resp_item['InstanceId'],tag_attached])

        #print "\n\n\n " + str(resp_item)

    return instance_list

def action_ec2(action='nothing'):
    ec2_term_list=find_ec2()
    #print '\n\n\nec2 etrm ' + str(ec2_term)
    for inst in ec2_term_list:
    #tag_attached=[ (itm['Key'],itm['Value']) for  itm in  ec2_term['Tags'] if itm['Key'] == tag_name ]
        if action == 'terminate':
            print "this instance Id " +  inst[0] + ' With Tag ' + str(inst[1]) + ' will be terminated '
            yn=raw_input("type YES to terminate ")
            if yn == 'YES':
                response = ec2_cl.terminate_instances(
                    InstanceIds=[
                        inst[0]
                    ]
                )
                print "terminating ..."
                time.sleep(15)

                print  inst[0]  + ' termination state ' + response ['TerminatingInstances'][0]['CurrentState']['Name']
        elif action == 'stop':
            print "this instance Id " +  inst[0] + ' With Tag ' + str(inst[1]) + ' will be shutdown '
            yn=raw_input("type YES to shutdown ")
            if yn == 'YES':
                response = ec2_cl.stop_instances(
                    InstanceIds=[
                        inst[0]
                    ]
                )
                print "shutting down ..."
                time.sleep(15)

                print  inst[0]  + ' state ' + response ['StoppingInstances'][0]['CurrentState']['Name']
        elif action == 'start':
            print "this instance Id " +  inst[0] + ' With Tag ' + str(inst[1]) + ' will be started '
            yn=raw_input("type YES to start ")
            if yn == 'YES':
                response = ec2_cl.start_instances(
                    InstanceIds=[
                        inst[0]
                    ]
                )
                print "Starting Up ..."
                time.sleep(15)

                print  inst[0]  + ' state ' + response ['StartingInstances'][0]['CurrentState']['Name']



if __name__ == '__main__':
    main()
