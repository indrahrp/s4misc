import boto3
devlist=[

    {
        'DeviceName': '/dev/xvdab',
        'Ebs': {
            'SnapshotId': 'snap-054b61a1db8c648c4',
            'VolumeType': 'st1'
        }
    },

    {
        'DeviceName': '/dev/xvdaa',
        'Ebs': {
            'SnapshotId': 'snap-0b551e4dfbe376409',
            'VolumeType': 'st1'
        }
    },








    {
        'DeviceName': '/dev/xvdy',
        'Ebs': {
            'SnapshotId': 'snap-0b7f585b7070b0d95',
            'VolumeType': 'st1'
        }
    },
    {
        'DeviceName': '/dev/sda1',
        'Ebs': {
            'SnapshotId': 'snap-0d444ac9edc85f2db',
            'VolumeType': 'gp2'
        }
    },
    {
        'DeviceName': '/dev/sdw',
        'Ebs': {
            'SnapshotId': 'snap-044aaa36dbcca281c',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/xvdz',
        'Ebs': {
            'SnapshotId': 'snap-02304128c78797856',
            'VolumeType': 'st1'
        }
    },
    {
        'DeviceName': '/dev/sdu',
        'Ebs': {
            'SnapshotId': 'snap-09c908b44a88ac0ac',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/sds',
        'Ebs': {
            'SnapshotId': 'snap-01438657702d91837',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/sdq',
        'Ebs': {
            'SnapshotId': 'snap-0450dec0cef8d50ab',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/sdo',
        'Ebs': {
            'SnapshotId': 'snap-0f5133e21dea86c06',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/sdm',
        'Ebs': {
            'SnapshotId': 'snap-071c5cd60dcbe6e1c',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/sdj',
        'Ebs': {
            'SnapshotId': 'snap-0c336a97f118e8b71',
            'VolumeType': 'gp2'
        }
    },
    {
        'DeviceName': '/dev/sdk',
        'Ebs': {
            'SnapshotId': 'snap-051295f42e116d724',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/sdi',
        'Ebs': {
            'SnapshotId': 'snap-0be59536e253cd3b8',
            'VolumeType': 'sc1'
        }
    },
    {
        'DeviceName': '/dev/sdf',
        'Ebs': {
            'SnapshotId': 'snap-0941bc7b316f62719',
            'VolumeType': 'gp2'
        }
    },
    {
        'DeviceName': '/dev/sdg',
        'Ebs': {
            'SnapshotId': 'snap-00fbad7ef93036e9a',
            'VolumeType': 'gp2'
        }
    }
]






ec2=boto3.resource('ec2')
instance=ec2.create_instances(
    BlockDeviceMappings=devlist,
    ImageId='to be filled out',
    InstanceType='r4.16xlarge'
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=['sg-024aced7356217948'],
    SubnetId='subnet-0bde89a58d7331d81',
    KeyName='Essos-newkey',
    PrivateIpAddress='10.80.230.21'


)