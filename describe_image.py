import boto3

client=boto3.client('ec2')
response = client.describe_images(

    ImageIds=[
        'ami-03ae5bea494757da0',
        'ami-01f5e2a34f650e35c'
    ],

    DryRun=False
)
print response
print response ['Images'][0]['ImageId']
print response ['Images'][0]['BlockDeviceMappings']
bdms=response ['Images'][1]['BlockDeviceMappings']
for bdm in bdms:
    print bdm['DeviceName'] + "  " + bdm["Ebs"]["SnapshotId"]


#print response ['Images'][0]['DeviceName'] + ['Images'][0]['SnapshotId']
#print response ['Images'][0]['DeviceName'] + ['Images'][0]['SnapshotId']
#print '\n\n\n\n'
#print response ['Images']

