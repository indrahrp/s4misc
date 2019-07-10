#!/usr/bin/python
"""
Automate the build of Shared Service Catalog Portfolio, Products and Template baseline_constraint in Child accounts
"""

# please note that I am not setting the AWS region in this code which means that it will default to the AWS region of my shell where I run this script from.
# you can specify the region in the client call by setting the region_name parameter/value to the appropriate AWS region

###############
#Create Template definitions
###############
import boto3
import random
import time
import sys
import argparse

def get_aws_account_id(session):
    sts = session.client('sts')
    user_arn = sts.get_caller_identity()["Arn"]
    return user_arn.split(":")[4]


rootaccount="011825642366"
#sc_client = boto3.client('servicecatalog', region_name='us-east-1')
iam_client = boto3.client('iam', region_name='us-east-1')
session_client = boto3.client('sts')
# import_portfolios = ['port-rx4vc3kthfxfw']
# linux_portfolio_id = 'port-rx4vc3kthfxfw'



account_id = boto3.client('sts').get_caller_identity()['Account']
print("Yor account id is: " +account_id)

def getsessionv2(acc):
    print "\n\n========================================"
    #print "account id " + acc['Id']
    #print "account name " + acc['Name']
    #print "========================================"
    if acc==rootaccount:
        sess=boto3.Session()
    else:
        cred = role_to_session(acc)
        credentials = cred['Credentials']


        sess= boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])

    return sess


class Account_Session:
    SESS_DICT={}
    ACCLIST=[]
    ROOT='011825642366'

    @staticmethod
    def initialize():
        print "Initializing Session to All Subaccounts .. It will take about 2 minutes"
        sess=boto3.session.Session()
        currentacc=get_aws_account_id(sess)
        if currentacc != Account_Session.ROOT:
            print "The session need to start from root account"
            exit(1)
        client = boto3.client('organizations')
        counter=0
        for account in paginate(client.list_accounts):
            counter += 1
            print "initializing session to account " + account['Id']
            if not account['Id'] == Account_Session.ROOT:
                ses=getsessionv2(account['Id'])
            else:
                ses=boto3.session.Session()
            #Account_Session.SESS_LIST.append([ses,account[id],account['Name']])
            Account_Session.SESS_DICT.update({account['Id']:{'session':ses,'name':account['Name']}})
            if counter > 1:
                break
        return
    @staticmethod
    def build_sess_subaccount(subaccount=None):
        #if not subaccount:
        #    Account_Session.initialize()
        #    return
        accountdict={}
        client = boto3.client('organizations')
        for account in paginate(client.list_accounts):
            accountdict.update({account['Id']:account['Name']})
        print 'creating session for account ' + subaccount

        ses=getsessionv2(subaccount)
        Account_Session.SESS_DICT.update({subaccount:{'session':ses,'name':accountdict[subaccount]}})
        #return Account_Session.SESS_DICT[subaccount]
        return
    @staticmethod
    def get_account_list():
        Account_Session.ACCLIST=[]
        print "Gather Sema4 Account List ..."
        sess=boto3.session.Session()
        currentacc=get_aws_account_id(sess)
        if currentacc != Account_Session.ROOT:
            print "The session need to start from root account"
            exit(1)
        client = boto3.client('organizations')
        for account in paginate(client.list_accounts):
            print "account inv " + account['Id']
            Account_Session.ACCLIST.append(account['Id'])
        return Account_Session.ACCLIST


#Account_Session.initialize()

def role_to_session(accountid):
    #print "account id " + accountid
    sts_client = boto3.client('sts')
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

def paginate(method, **kwargs):
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result


def main():
    global deploylist
    ##python  deploy_cf.py --name test --templatefile Sema4-ITAdmin_Role.yaml --params "BucketName=s4-research-sanofi-dev&ITLambda=ITAdmin_Libraries"
    #Account_Session.initialize()
    parser = argparse.ArgumentParser()
    parser.add_argument('--s3list', type=str, required=False,
                        help='s3 name to search.')

    parser.add_argument('--subaccount', type=str, required=False,
                        help='a specific account to deploy')

    parser.add_argument('--ssmget', type=str, required=False,
                        help='ssm param to search.')

    parser.add_argument('--ssmupdate', type=str, required=False,
                        help='ssm param to update.')
    parser.add_argument('--kms_grant', type=str ,required=False,
                        help='grant all account access to KMS key i.e --grant kmsidarn ')

    parser.add_argument('--sharing_transit_gateway', action="store_true", required=False,
                        help='sharing_transit_gateway to all sub accounts i.e --sharing_transit_gateway')
    parser.add_argument('--ssmupdatevalue', type=str, required=False,
                        help='ssm param value to update --ssmupdate and --ssmupdatevalue both have to exist.')
    parser.add_argument('--shareami', type=str, required=False,
                        help='ami to share to all sub accounts')
    parser.add_argument('--eiplistallsub', type=str, required=False,
                        help='list eip in all sub accounts')




    parser.add_argument('--dbclusterparam', type=str, required=False,
                        help='create db cluster parameter group')

    parser.add_argument('--dbdbparam', type=str, required=False,
                        help='create db database parameter group')

    parser.add_argument('--listvpc',action="store_true",required=False, help='list vpc all accounts ')


    args = parser.parse_args()
    if args.s3list:
        s3listallsub(args.s3list)
    elif args.ssmget:
        ssmgetallsub(args.ssmget)
    elif args.ssmupdate and args.ssmupdatevalue:
        update_ssmsub(args.ssmupdate,args.ssmupdatevalue)
    elif args.shareami:
        shareamiallsub(args.shareami)
    elif args.eiplistallsub:
        eiplistallsub(args.eiplistallsub)
    elif args.dbclusterparam:
        dbclusterparam(args.dbclusterparam)
    elif args.dbdbparam:
        dbdbparam(args.dbdbparam)
    elif args.sharing_transit_gateway:
       print ' executing sharing '
       sharing_transit_gateway()
    elif args.listvpc:
        listvpc()
    elif args.kms_grant:
        kms_grant(args.kms_grant)


def listvpc():
    print "Listing VPC and subnet info on all accounts "
    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('ec2', region_name='us-east-1')
            try:
                response = sc_client.describe_vpcs()
                resp = response['Vpcs']
                if resp:
                    for rp in resp:
                        if rp['IsDefault']:
                            return rp['VpcId']
                        print(rp['CidrBlock']) + " VPC ID " + rp['VpcId'] + " Is Default " + str(rp['IsDefault']) + " Tag " + str(rp.get('Tags',"NA"))
                else:
                    print('No vpcs found')
            except:
                print("Error getting")
                raise


def kms_grant(kmsidarn):
    print ("Grant Key {} all accounts".format(kmsidarn))
    #Account_Session.initialize()
    try:
        acclist=Account_Session.get_account_list()
        #print 'acc list ' + str(acclist)
        Account_Session.build_sess_subaccount(rootaccount)
        clientses=Account_Session.SESS_DICT[rootaccount]['session'].client('kms')
        for acc in acclist:
            print ("granting account {0}".format(acc))
            response = clientses.create_grant(
            # The identity that is given permission to perform the operations specified in the grant.
            GranteePrincipal=acc,
            # The identifier of the CMK to which the grant applies. You can use the key ID or the Amazon Resource Name (ARN) of the CMK.
            KeyId=kmsidarn,
            # A list of operations that the grant allows.
            Operations=[
                'Encrypt',
                'Decrypt',
                'ReEncryptTo',
                'GenerateDataKey',
                'GenerateDataKeyWithoutPlaintext',
                'DescribeKey',
                'Verify',
                'ReEncryptFrom',
                'Sign'
            ],
            Name='Subaccount-Access-KMS-for-AMI-sharing'
            )

        print ("Grant response GrantId : {0} and GrantToken : {1}".format(response['GrantId'],response['GrantToken']))

    except Exception as err:
        print str(err)
        raise


def sharing_transit_gateway():
    print "sharing transit gateway to all accounts"
    #Account_Session.initialize()
    resourcesharedarn='arn:aws:ram:us-east-1:346997421618:resource-share/fab4ff5d-ae0c-9b09-8513-ee4441aa5699'
    itadminprodacc='346997421618'
    #acc,sess=Account_Session.sess_subaccount('586916032531')
    try:
        acclist=Account_Session.get_account_list()
        #print 'acc list ' + str(acclist)
        Account_Session.build_sess_subaccount(itadminprodacc)
        clientses=Account_Session.SESS_DICT[itadminprodacc]['session'].client('ram')
        response=clientses.associate_resource_share(
            resourceShareArn=resourcesharedarn,
            principals=acclist
            )

        #print 'Resource Share Status ' + str(response['resourceShareAssociations']['status'] + ' with Status Message ' + response['resourceShareAssociations']['statusMessage']
        resp= { respo['associatedEntity']:respo['status'] for respo in  response['resourceShareAssociations'] }
        #print 'Resource Share Status ' + str(response['resourceShareAssociations'])
        print 'Resource sharing status ..... wait 4 min'
        time.sleep(240)
        for r,s in resp.items():
            print 'account: ' + r + ' status: ' + s
    except Exception as err:
        print str(err)
        raise


def dbclusterparam(dbclusterparam='sema4auroramysql57',family='aurora-mysql5.7'):
    print "create db cluster parameter group " + dbdbparam
    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('rds', region_name='us-east-1')
            try:
                response = sc_client.create_db_cluster_parameter_group(
                    DBClusterParameterGroupName=dbclusterparam,
                    DBParameterGroupFamily=family,
                    Description=family)
                print response['DBClusterParameterGroup']['DBClusterParameterGroupName']
                inp=raw_input('pause ')


            except:
                print("Error getting")



def dbdbparam(dbdbparam='sema4auroramysql57',family='aurora-mysql5.7'):
    print "create db parameter group " + dbdbparam
    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('rds', region_name='us-east-1')
            try:
                response = sc_client.create_db_parameter_group(
                    DBParameterGroupName=dbdbparam,
                    DBParameterGroupFamily=family,
                    Description=family

                )
                print response['DBParameterGroup']['DBParameterGroupName']



                #inp=raw_input('pause ')


            except Exception as err:
                print("Error getting" + str(err))






def s3listallsub(s3list):




    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('s3', region_name='us-east-1')
            try:
                response = sc_client.list_buckets()
                for bucket in  response['Buckets']:

                    print("bucket name  : " + bucket['Name'])
                    if s3list == bucket['Name']:
                        print "Found in " + account['Id']
                        inp=raw_input('continue')
            except:
                print("Error getting")






def eiplistallsub(eip):




    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('ec2', region_name='us-east-1')
            try:
                response = sc_client.describe_addresses()
                #print str(response)
                for addr in  response['Addresses']:
                    #print "addr " + str(addr)
                    print "Public IP : " + addr['PublicIp']
                    #print("Public IP : " + addr['PublicIP'])
                    print("Instance ID : " + addr.get('InstanceId','NA'))
                    print("AssociationId :" + addr.get('AssociationId','NA'))
                    if eip == addr['PublicIp']:
                        print "Found in " + account['Id']
                        inp=raw_input('continue')
            except Exception as errp:
                print("Error getting" + str(errp))









def ssmgetallsub(paramtocheck):



    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('ssm', region_name='us-east-1')
            try:
                response = sc_client.describe_parameters()
                for param  in  response['Parameters']:

                    print("Parameter name  : " + param['Name'])
                    if paramtocheck == param['Name']:
                        print "Found in " + account['Id']
                        inp=raw_input('continue')
            except:
                print("Error getting")


def update_ssmsub(paramtoupdate,paramvalue):

    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
       #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('ssm', region_name='us-east-1')

            try:
                print "updating ssm parameter " + paramtoupdate
                ssm = client_sess.client('ssm')
                response= ssm.put_parameter(
                    Name=paramtoupdate,
                    #Name='/ec/ami/testparam',
                    Value=paramvalue,
                    Type="String",
                    Overwrite=True
                )
            except:
                print "error in updating ssm " + paramtoupdate





def shareamiallsub(ami):
    #ami=event['ami_id']
    source_ec2 = boto3.resource('ec2')
    #source_ami = source_ec2.Image(ami)

    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount:

            #client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            #source_ec2=client_sess.resource('ec2', region_name='us-east-1')
            source_ami = source_ec2.Image(ami)

            try:
                print "sharing to all sub accounts ami " + ami


                image = source_ec2.Image(ami)

                response = image.describe_attribute(
                    Attribute='launchPermission'
                )
                print ('image ', str(response))


                # Share the image with the destination account
                image.modify_attribute(
                    ImageId = image.id,
                    Attribute = 'launchPermission',
                    OperationType = 'add',
                    LaunchPermission = {
                        'Add' : [{ 'UserId': account['Id'] }]
                    }
                )

                #yn=raw_input('Enter')

                source_snapshot = source_ec2.Snapshot(source_ami.block_device_mappings[0]['Ebs']['SnapshotId'])
                print ("source_snapshot " + str(source_snapshot))

                #print ("block device " + str(source_ami.block_device_mappings))


                #word[0] for word in listOfWords ]
                #snapshotlist=[ snap['Ebs']['SnapshotId'] for snap in source_ami.block_device_mappings ]
                snapshotlist=[ snap['Ebs']['SnapshotId'] for snap in source_ami.block_device_mappings if snap.get('Ebs',False) ]
                print ('snaphlist ' , str(snapshotlist))
                #ans=raw_input('pause ')

                # Ensure the snapshot is shared with target account
                for source_snap in snapshotlist:
                    source_snapshot = source_ec2.Snapshot(source_snap)
                    source_sharing = source_snapshot.describe_attribute(Attribute='createVolumePermission')
                    print ("source_sharing ", str(source_sharing))
                    if source_sharing['CreateVolumePermissions'] \
                            and source_sharing['CreateVolumePermissions'][0]['UserId'] == account:
                        print("Snapshot already shared with account")
                    else:
                        print("Sharing with target account")
                        source_snapshot.modify_attribute(
                            Attribute='createVolumePermission',
                            OperationType='add',
                            UserIds=[account['Id']]
                        )
            except Exception as err :
                print "error " + str(err)





if __name__ == '__main__':
    main()
