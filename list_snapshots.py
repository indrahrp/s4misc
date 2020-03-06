import boto3

owner='006775277657'
ec2=boto3.resource('ec2')
snaplist=ec2.snapshots.filter(
    Filters=[
        {
        "Name": "owner-id",
        "Values": [
                owner
        ]
    }
    ]
).all()
#  OwnerIds=['417302553802' ]
#).all()

for aa in snaplist:
    print " {0}      {1}      {2}    {3}   {4}  ".format(aa.snapshot_id,aa.encrypted,aa.volume_id,aa.volume_size,aa.description,aa.tags)