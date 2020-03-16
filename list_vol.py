import boto3
ec2 = boto3.resource('ec2', region_name='us-east-1')
#volumes = ec2.volumes.all() # If you want to list out all volumes
#volumes = ec2.volumes.filter(Filters=[{'Name': 'status', 'Values': ['in-use']}]) # if you want to list out only attached volumes
#print ([volume for volume in volumes])
print "No VolumeID               Status    InstanceId                Encrypted"
volume_iterator = ec2.volumes.all()
counter=0
for v in volume_iterator:
   #for a in v.attachments:
   #print "{0} {1} {2}".format(v.id, v.state, v.attachments[0]['InstanceId'])
   counter = counter + 1
   if  v.attachments:
        print "{0} {1}     {2}       {3}   {4}".format(counter,v.id, v.state, v.attachments[0]['InstanceId'], v.encrypted)
   else:
       print "{0} {1}  No Instance               {2}  {3}".format(counter,v.id, v.state, v.encrypted)

   #print "volume id {} with attachment {}".format(v.id, v.attachments)