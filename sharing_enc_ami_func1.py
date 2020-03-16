from sys import argv

import boto3

#TARGET_ACCOUNT_ID = '417302553802'
#ROLE_ON_TARGET_ACCOUNT = 'arn:aws:iam::417302553802:role/shareami'
#rolearn="arn:aws:iam::" + TARGET_ACCOUNT_ID+ ":role/OrganizationAccountAccessRole"
SOURCE_REGION = 'us-east-1'
TARGET_REGION = 'us-east-1'


def role_arn_to_session(**args):
    """
    Lets you assume a role and returns a session ready to use
    Usage :
        session = role_arn_to_session(
            RoleArn='arn:aws:iam::012345678901:role/example-role',
            RoleSessionName='ExampleSessionName')
        client = session.client('sqs')
    """
    client = boto3.client('sts')
    response = client.assume_role(**args)
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])


##if len(argv) != 2:
##    print('usage: share-ami.py [ami]')
###    exit(1)
def sharing_ami(ami,TARGET_ACCOUNT_ID,role_arn):
    source_ec2 = boto3.resource('ec2')
    source_ami = source_ec2.Image(ami)

    source_snapshot = source_ec2.Snapshot(source_ami.block_device_mappings[0]['Ebs']['SnapshotId'])
    print "source_snapshot " + str(source_snapshot)

    print 'block device ' + str(source_ami.block_device_mappings)
    #word[0] for word in listOfWords ]
    snapshotlist=[ snap['Ebs']['SnapshotId'] for snap in source_ami.block_device_mappings ]
    print 'snaphlist ' + str(snapshotlist)
    ans=raw_input('pause ')

    # Ensure the snapshot is shared with target account
    for source_snap in snapshotlist:
        source_snapshot = source_ec2.Snapshot(source_snap)
        source_sharing = source_snapshot.describe_attribute(Attribute='createVolumePermission')
        if source_sharing['CreateVolumePermissions'] \
                and source_sharing['CreateVolumePermissions'][0]['UserId'] != TARGET_ACCOUNT_ID:
            print("Snapshot already shared with account, creating a copy")
        else:
            print("Sharing with target account")
            source_snapshot.modify_attribute(
                Attribute='createVolumePermission',
                OperationType='add',
                UserIds=[TARGET_ACCOUNT_ID]
            )
    ans=raw_input('pause1 ')

    # Get session with target account
    target_session = role_arn_to_session(
        RoleArn=role_arn,
        RoleSessionName='share-admin-temp-session'
    )
    target_ec2 = target_session.resource('ec2', region_name=TARGET_REGION)

    # A shared snapshot, owned  by source account
    target_snapshot=[]
    for source_snap in snapshotlist:
        shared_snapshot = target_ec2.Snapshot(source_snap)
        #print "shared snapshot id first " + source_ami.block_device_mappings[0]['Ebs']['SnapshotId']
        #print "shared snapshot id " + str(shared_snapshot)
        # Ensure source snapshot is completed, cannot be copied otherwise

        if shared_snapshot.state != "completed":
            print("Shared snapshot not in completed state, got: " + shared_snapshot.state)
            exit(1)

    # Create a copy of the shared snapshot on the target account
        copy = shared_snapshot.copy(
            SourceRegion=SOURCE_REGION,
            Encrypted=True,
            Description='local copy'
        )

    # Wait for the copy to complete
        copied_snapshot = target_ec2.Snapshot(copy['SnapshotId'])
        target_snapshot.append(copied_snapshot.snapshot_id)
        copied_snapshot.wait_until_completed()

        print("Created target-owned copy of shared snapshot with id: " + copy['SnapshotId'])
    ans=raw_input('pause2 ')

    # Optional: tag the created snapshot
    # copied_snapshot.create_tags(
    #     Tags=[
    #         {
    #             'Key': 'cost_centre',
    #             'Value': 'project abc',
    #         },
    #     ]
    # )

    # Create an AMI from the snapshot.
    # Modify the below if your configuration differs

    #BlockDeviceMappings=[
    #                        {
    #                            "DeviceName": "/dev/sda1",
    #                            "Ebs": {
    #                                "SnapshotId": copied_snapshot.snapshot_id,
    #                                "VolumeSize": copied_snapshot.volume_size,
    #                                "DeleteOnTermination": True,
    #                                "VolumeType": "gp2"
    #                            },
    #                        }
    #                    ],
    blockdevmap=[]
    devdict={}
    snapno=0
    for dev in source_ami.block_device_mappings:
        devdict['DeviceName']= dev['DeviceName']
        ebsdict={}

        ebsdict['SnapshotId']= target_snapshot[snapno]
        ebsdict['VolumeSize'] = dev['Ebs']['VolumeSize']
        ebsdict['DeleteOnTermination']= dev['Ebs']['DeleteOnTermination']
        ebsdict['VolumeType']=dev['Ebs']['VolumeType']
        devdict['Ebs']=ebsdict

        #devdict['Ebs']['SnapshotId']= target_snapshot[snapno]
        #devdict['Ebs']['VolumeSize'] = dev['Ebs']['VolumeSize']
        #devdict['Ebs']['DeleteOnTermination']= dev['Ebs']['DeleteOnTermination']
        #devdict['Ebs']['VolumeType']=dev['Ebs']['VolumeType']
        print 'devdict ' + str(devdict)
        snapno=snapno + 1
        blockdevmap.append(devdict)
    print 'blockdevmap ' + str(blockdevmap)
    ans=raw_input('pause3 ')

    print 'blockdevmap ' + str(blockdevmap)
    #BlockDeviceMappings=[
    #                        {
    #                            'DeviceName': bdm['DeviceName'],
    #                            'Ebs': {
    #                                'DeleteOnTermination':
    #                                    bdm['DeleteOnTermination'],
    #                            },
    #                        },
    #                    ],

    new_image = target_ec2.register_image(
        Name='copy-' + copied_snapshot.snapshot_id,
        Architecture='x86_64',
        RootDeviceName='/dev/sda1',
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "SnapshotId": copied_snapshot.snapshot_id,
                    "VolumeSize": copied_snapshot.volume_size,
                    "DeleteOnTermination": True,
                    "VolumeType": "gp2"
                },
            }
        ],
        VirtualizationType='hvm'
    )

    print("New AMI created: " + str(new_image))

    # Optional: tag the created AMI
    # new_image.create_tags(
    #     Tags=[
    #         {
    #             'Key': 'cost_centre',
    #             'Value': 'project abc',
    #         },
    #     ]
    # )

    # Optional: Remove old snapshot and image
    # source_ami.deregister()
    # source_snapshot.delete()


if __name__ == "__main__":
    TARGET_ACCOUNT_ID='386451404987'
    role_arn="arn:aws:iam::" + TARGET_ACCOUNT_ID+ ":role/itadmin_role"
    sharing_ami('ami-0aa76ce9fb7bb2b74',TARGET_ACCOUNT_ID,role_arn)