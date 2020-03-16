import boto3
devlist=[
    {
        'DeviceName': '/dev/xvdab',
        'Ebs': {
            'SnapshotId': 'snap-0fa816ba096c8041f',
            'VolumeType': 'st1'
        }
    },
    {
        'DeviceName': '/dev/xvdac',
        'Ebs': {
            'SnapshotId': 'snap-071b2eb737368b97d',
            'VolumeType': 'st1'
        }
    }
]
ec2=boto3.client('ec2')
instance=ec2.create_instances(
    BlockDeviceMappings=devlist,
    ImageId='essosami'
)