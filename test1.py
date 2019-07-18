import copy,boto3

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


TARGET_ACCOUNT_ID='386451404987'
role_arn="arn:aws:iam::" + TARGET_ACCOUNT_ID+ ":role/itadmin_role"

target_session = role_arn_to_session(
    RoleArn=role_arn,
    RoleSessionName='share-admin-temp-session'
)
target_ec2 = target_session.resource('ec2', region_name='us-east-1')

ld=[{u'DeviceName': '/dev/xvda', u'Ebs': {u'SnapshotId': 'snap-01199de44db890726', u'DeleteOnTermination': True, u'VolumeType': 'gp2', u'VolumeSize': 8, u'Encrypted': True}}, {u'DeviceName': '/dev/xvdcz', u'Ebs': {u'SnapshotId': 'snap-0ba7d5f2fdec4890b', u'DeleteOnTermination': True, u'VolumeType': 'gp2', u'VolumeSize': 100, u'Encrypted': True}}]
target_snapshot=['snap-0a819335506473c8d','snap-09e58cfd36d90cfe5']
blockdevmap=[]
devdict={}
snapno=0
for dev in ld:
    devdict={}
    ebsdict={}
    devdict['DeviceName']= dev['DeviceName']


    ebsdict['SnapshotId']= target_snapshot[snapno]
    ebsdict['VolumeSize'] = dev['Ebs']['VolumeSize']
    ebsdict['DeleteOnTermination']= dev['Ebs']['DeleteOnTermination']
    ebsdict['VolumeType']=dev['Ebs']['VolumeType']
    devdict['Ebs']=copy.deepcopy(ebsdict)

    print 'devdict ' + str(devdict)
    snapno=snapno + 1
    blockdevmap.append(devdict)
print 'blockdevmap ' + str(blockdevmap)

new_image = target_ec2.register_image(
    Name='aminame' ,
    Architecture='x86_64',
    RootDeviceName='/dev/xvda',
    BlockDeviceMappings=blockdevmap,
    VirtualizationType='hvm'
)

print("New AMI created: " + str(new_image))
#block device [{u'DeviceName': '/dev/xvda', u'Ebs': {u'SnapshotId': 'snap-01199de44db890726', u'DeleteOnTermination': True, u'VolumeType': 'gp2', u'VolumeSize': 8, u'Encrypted': True}}, {u'DeviceName': '/dev/xvdcz', u'Ebs': {u'SnapshotId': 'snap-0ba7d5f2fdec4890b', u'DeleteOnTermination': True, u'VolumeType': 'gp2', u'VolumeSize': 100, u'Encrypted': True}}]
