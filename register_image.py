import boto3

ec2=boto3.client('ec2')
image = ec2.register_image(
    #ImageLocation='locationanywhereins3',
    Architecture='x86_64',
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/sda1',
            #'VirtualName': 'string',
            'Ebs': {
                'DeleteOnTermination': True,
                'SnapshotId': 'snap-006d811efad950e9c',
                #'VolumeSize': 123,
                'VolumeType': 'gp2',
                #'Encrypted': True,
                #'KmsKeyId': '2c9e26fc-3059-4eb3-8e82-a32813195943'
            },
            #'NoDevice': 'string'
        },
    ],
    Description='ami build from snapshot 1st',
    DryRun=False,
    #EnaSupport=True|False,
    #KernelId='string',
    Name='testamifromsnapshot 1st',
    #BillingProducts=[
    #    'string',
    #],
    #RamdiskId='string',
    RootDeviceName='/dev/sda1',
    #SriovNetSupport='string',
    VirtualizationType='hvm'
)
