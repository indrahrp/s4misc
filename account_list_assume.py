import boto3


import boto3
import uuid
import pprint
import argparse,sys
import botocore

iam_client = boto3.client('iam')
sts_client = boto3.client('sts')
org_client = boto3.client('organizations')

client = boto3.client('organizations')
rootaccount="r-011825642366"

response = client.list_accounts(MaxResults=20)
responsemore = client.list_accounts(NextToken=response['NextToken'])


def main(argv):
    parser = argparse.ArgumentParser(description='Misc Sub Account Information')


    # add args
    parser.add_argument('command',
                        type=str,
                        choices=["sub-account-list", "s3-list","ebsvol-list","findec2byeip"])
    #parser.add_argument('--db_identifier',
    #                    help='db_instance_identifier ',
    #                    type=str)
    #parser.add_argument('--unencrypted', help="Flag to only show unencrypted Volume", action='store_true')
    parser.add_argument('--findec2byeip', help="Find EC2 instance assigned to an elastic IP  ", action='store',required=True)

    # parse args
    args = parser.parse_args()
    command = args.command
    print "command " + command

    if command == 's3-list':
        s3list()
    elif command == 'ebsvol-list':
        ebsvollist(args.unencrypted)
    elif command == 'findec2byeip':
        findec2byeip(args.findec2byeip)


    print("Starting in account: %s" % sts_client.get_caller_identity().get('Account'))
def role_to_session(accountid):
    #print "account id " + accountid
    rolearn="arn:aws:iam::" + accountid + ":role/OrganizationAccountAccessRole"
    assumedRoleObject = sts_client.assume_role(
        #RoleArn="arn:aws:iam::011825642366:role/OrganizationAccountAccess",

        #RoleArn="arn:aws:iam::417302553802:role/OrganizationAccountAccessRole",
        RoleArn=rolearn,
        RoleSessionName="organizational-su"
        )
    return assumedRoleObject

def getsession(acc):
    print "\n\n========================================"
    print "account id " + acc['Id']
    print "account name " + acc['Name']
    print "========================================"
    cred = role_to_session(acc['Id'])
    credentials = cred['Credentials']


    sess= boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])

    return sess

def findec2byeip(eip):
    ip=[]
    ip.append(eip)
    for acc in responsemore['Accounts']:
        #print "accis " + str(acc['Id'])
        sess=getsession(acc)

        target_ec2 = sess.client('ec2')
        filters = [{
            'Name': 'ip-address',
            'Values': ['18.213.58.126']
        }]
        result_list = target_ec2.describe_instances(Filters=filters)
        print result_list



def s3list():

    for acc in responsemore['Accounts']:
        #print "accis " + str(acc['Id'])
        sess=getsession(acc)

        target_s3 = sess.client('s3')
        #target_s3 = sess.resource('s3')
        ##bucketinfo = target_s3.buckets.all()
        bucketinfo = target_s3.list_buckets()
        #print bucketinfo
        #print bucketinfo['Buckets'][0]

        #for bucket in bucketinfo['Buckets']:
        #    print bucket['Name']

        for bucket in bucketinfo['Buckets']:
            #bkt = target_s3.Bucket(bucket)
            try:
            #print bucket['buu']
                print bucket['Name'], str(target_s3.get_bucket_lifecycle(Bucket = bucket['Name'])['Rules'][0]['ID']), \
                str(target_s3.get_bucket_encryption(Bucket = bucket['Name'])['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']), \
                str(target_s3.get_bucket_versioning(Bucket = bucket['Name']).get('Status','NA')), \
                str(target_s3.get_bucket_logging(Bucket = bucket['Name']).get('LoggingEnabled',{}).get('TargetBucket','NA'))
            except botocore.exceptions.ClientError:
                continue



            #print bucket

        #for key,val in bucketinfo.items():
        #    print key
        #    print val


        #client = boto3.client('organizations')
        #rootaccount="r-011825642366"
        #response = client.list_accounts_for_parent(ParentId=rootaccount,NextToken='ttt',MaxResults=12)
        #response = client.list_accounts(MaxResults=20)
        #print response['Accounts']
        #responsemore = client.list_accounts(NextToken=response['NextToken'])
        #for account in getListAccounts['Accounts']:
        #    print account['Id'], account['Name']

def ebsvollist(unencrypted=False):
    for acc in responsemore['Accounts']:
      #print "accis " + str(acc['Id'])
        sess=getsession(acc)

         #target_s3 = sess.resource('s3', region_name='us-east-1')


        ec2 = sess.resource('ec2', region_name='us-east-1')
        #volumes = ec2.volumes.all() # If you want to list out all volumes
        #volumes = ec2.volumes.filter(Filters=[{'Name': 'status', 'Values': ['in-use']}]) # if you want to list out only attached volumes
        #print ([volume for volume in volumes])
        print "No VolumeID               Status    InstanceId                Encrypted      Size   Tags"
        volume_iterator = ec2.volumes.all()
        counter=0
        for v in volume_iterator:
            #for a in v.attachments:
            #print "{0} {1} {2}".format(v.id, v.state, v.attachments[0]['InstanceId'])
            counter = counter + 1
            #print v.attachments
            if unencrypted:
                if not v.encrypted:
                 if  v.attachments:
                    print "{0} {1}     {2}       {3}   {4}        {5}    {6}   ".format(counter,v.id, v.state, v.attachments[0]['InstanceId'], v.encrypted, v.size,str(v.tags))
                 else:
                    print "{0} {1}  No Instance               {2}  {3}".format(counter,v.id, v.state, v.encrypted)
            else:
                if  v.attachments:
                    print "{0} {1}     {2}       {3}   {4}        {5}    {6}   ".format(counter,v.id, v.state, v.attachments[0]['InstanceId'], v.encrypted, v.size,str(v.tags))
                else:
                     print "{0} {1}  No Instance               {2}  {3}".format(counter,v.id, v.state, v.encrypted)




if __name__ == "__main__":
    main(sys.argv[1:])