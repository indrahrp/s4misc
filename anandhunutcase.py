import boto3
import datetime
timeLimit=datetime.datetime.now() - datetime.timedelta(days=30)
print timeLimit
#ec2 = boto3.resource('ec2',region_name='us-east-1')
client = boto3.client('ec2',region_name='us-east-1')
print ('start with root user account: {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
#snapshot = client.Snapshots ('id')
des_snap = client.describe_snapshots()
#print des_snap
list_dict = [{snap_dict['OwnerId']:snap_dict['SnapshotId'] } for snap_dict in des_snap['Snapshots']]
print ('start with root user account: {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
#print list_dict
print "list dict legnt "
for X in list_dict:
    # print('{}:{}'.format(X, eip_dict[X]))
    #print('{}: {}'.format(X+1, list_dict[X]))
    print "output : "  + str(X)

print ('start with root user account: {}'.format(boto3.client('sts').get_caller_identity().get('Account')))






