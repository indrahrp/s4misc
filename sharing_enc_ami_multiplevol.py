from sys import argv

import boto3
import botocore
import sys

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
def sharing_ami(ami,TARGET_ACCOUNT_ID,role_arn,customer_master_key):
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
    target_ec2_client = target_session.client('ec2')
    # A shared snapshot, owned  by source account
    target_snapshot=[]

    waiter_snapshot_complete = target_ec2_client.get_waiter('snapshot_completed')
    waiter_snapshot_complete.config.max_attempts = 1000
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
            Description='local copy',
            KmsKeyId=customer_master_key
        )

    # Wait for the copy to complete
        copied_snapshot = target_ec2.Snapshot(copy['SnapshotId'])
        target_snapshot.append(copied_snapshot.snapshot_id)

        try:
            waiter_snapshot_complete.wait(
                SnapshotIds=[
                    copied_snapshot.id,
                ]
            )
        except botocore.exceptions.WaiterError as e:
            copied_snapshot.delete()
            sys.exit('ERROR: {}'.format(e))


        #copied_snapshot.wait_until_completed()

        print("Created target-owned copy of shared snapshot with id: " + copy['SnapshotId'])

    ans=raw_input('pause2 ')


    blockdevmap=[]
    devdict={}
    snapno=0
    for dev in source_ami.block_device_mappings:
        devdict={}
        ebsdict={}
        devdict['DeviceName']= dev['DeviceName']
        ebsdict['SnapshotId']= target_snapshot[snapno]
        ebsdict['VolumeSize'] = dev['Ebs']['VolumeSize']
        ebsdict['DeleteOnTermination']= dev['Ebs']['DeleteOnTermination']
        ebsdict['VolumeType']=dev['Ebs']['VolumeType']
        devdict['Ebs']=ebsdict

        print 'devdict ' + str(devdict)
        snapno=snapno + 1
        blockdevmap.append(devdict)

    print 'blockdevmap ' + str(blockdevmap)
    ###RootDevicename has to be matched with blockdevmap
    new_image = target_ec2.register_image(
        Name='eywa03192019A' ,
        Architecture='x86_64',
        RootDeviceName='/dev/xvda',
        BlockDeviceMappings=blockdevmap,
        VirtualizationType='hvm'
    )

    print("New AMI created: " + str(new_image))
    #block device [{u'DeviceName': '/dev/xvda', u'Ebs': {u'SnapshotId': 'snap-01199de44db890726', u'DeleteOnTermination': True, u'VolumeType': 'gp2', u'VolumeSize': 8, u'Encrypted': True}}, {u'DeviceName': '/dev/xvdcz', u'Ebs': {u'SnapshotId': 'snap-0ba7d5f2fdec4890b', u'DeleteOnTermination': True, u'VolumeType': 'gp2', u'VolumeSize': 100, u'Encrypted': True}}]


if __name__ == "__main__":

    TARGET_ACCOUNT_ID = '880407937848'
    ##source AMI has to be encrypted with customer KMS and shared with target account
    ##KMS of destination account
    customer_master_key='1ced910d-cc36-4d69-ade9-10aee01d8c96'
    #role_arn="arn:aws:iam::" + TARGET_ACCOUNT_ID+ ":role/OrganizationAccountAccessRole"
    role_arn="arn:aws:iam::880407937848:role/ITAdmin-Role"
    sharing_ami('ami-01b3039aedec39a2e',TARGET_ACCOUNT_ID,role_arn,customer_master_key)