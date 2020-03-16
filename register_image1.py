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
        {
            'DeviceName': '/dev/sdb',
            #'VirtualName': 'string',
            'Ebs': {
                'DeleteOnTermination': True,
                'SnapshotId': 'snap-0aa7648f7c8797608',
                #'VolumeSize': 123,
                'VolumeType': 'gp2',
                #'Encrypted': True,
                #'KmsKeyId': '2c9e26fc-3059-4eb3-8e82-a32813195943'
            },
            #'NoDevice': 'string'
        },

        {
            'DeviceName': '/dev/sdc',
            #'VirtualName': 'string',
            'Ebs': {
                'DeleteOnTermination': True,
                'SnapshotId': 'snap-0262575dc8c0b9645',
                #'VolumeSize': 123,
                'VolumeType': 'gp2',
                #'Encrypted': True,
                #'KmsKeyId': '2c9e26fc-3059-4eb3-8e82-a32813195943'
            },
            #'NoDevice': 'string'
        },
    ],
    Description='ami build from snapshot 3rd',
    DryRun=False,
    #EnaSupport=True|False,
    #KernelId='string',
    Name='testamifromsnapshot 3rd',
    #BillingProducts=[
    #    'string',
    #],
    #RamdiskId='string',
    RootDeviceName='/dev/sda1',
    #SriovNetSupport='string',
    VirtualizationType='hvm'
)
