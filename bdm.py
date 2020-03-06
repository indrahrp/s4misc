import boto3

bdms=[]
dictbdms={}
#
#original_mappings = {
#    'DeleteOnTermination': device_mapping['Ebs']['DeleteOnTermination'],
#    'VolumeId': device_mapping['Ebs']['VolumeId'],
#    'DeviceName': device_mapping['DeviceName'],
#}
#all_mappings.append(original_mappings)

all_mappings=[
    {
        "DeviceName": "/dev/sda1",
        "Ebs": {
            "SnapshotId": 'snap1',
            "VolumeSize": 8,
            "DeleteOnTermination": True,
            "VolumeType": "gp2",
            "VolumeId": "vol1"
        },
    },
    {
        "DeviceName": "/dev/sdb",
        "Ebs": {
                 "SnapshotId": 'snap2',
                 "VolumeSize": 8,
                 "DeleteOnTermination": True,
                 "VolumeType": "gp2",
                 "VolumeId": "vol2"
        },
   }
]
print all_mappings

volsnap={"vol1":"snap1aa","vol2":"snap2aa"}

for volkey in volsnap:

    for map in all_mappings:
        if map['Ebs']['VolumeId']== volkey:
            map["Ebs"]["SnapshotId"]=volsnap[volkey]


print all_mappings
#shared_snapshot=['sn1','sn2','sn4','sn3']
#for snp in shared_snapshot:
#    dictbdms['DeviceName']=