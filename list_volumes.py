import boto3

# Define the connection
ec2 = boto3.resource('ec2', region_name="us-east-1")

# Find all volumes
volumes = ec2.volumes.all()

# Loop through all volumes and pass it to ec2.Volume('xxx')
for vol in volumes:
    iv = ec2.Volume(str(vol.id))
    print "Created(" + str(iv.create_time) + "),AZ(" + str(iv.availability_zone) + "),VolumeID(" + str(iv.volume_id) + "),VolumeType(" + str(iv.volume_type) + "),State(" + str(iv.state) + "),Size(" + str(iv.size) + "),IOPS(" + str(iv.iops) + "),IsEncrypted(" + str(iv.encrypted) + "),SnapshotID(" + str(iv.snapshot_id) + "),KMS_KEYID(" + str(iv.kms_key_id) + ")",
    print "========================================================================================="
    # The following next 2 print statements variables apply only in my case.
    #print ",InstanceID(" + str(iv.attachments[0]['InstanceId']) + "),InstanceVolumeState(" + str(iv.attachments[0]['State']) + "),DeleteOnTerminationProtection(" + str(iv.attachments[0]['DeleteOnTermination']) + "),Device(" + str(iv.attachments[0]['Device']) + ")",
    print "InstanceID : " + str(iv.attachments[0]['InstanceId'])

## if iv.tags:
    ##    print ",Name(" + str(iv.tags[0]['Name']) + "),Mirror(" + str(iv.tags[0]['mirror']) + "),Role(" + str(iv.tags[0]['role']) + "),Cluster(" + str(iv.tags[0]['cluster']) + "),Hostname(" + str(iv.tags[0]['hostname']) + "),Generation(" + str(iv.tags[0]['generation']) + "),Index(" + str(iv.tags[0]['index']) + ")"
    ##print ""