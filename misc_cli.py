#!/usr/bin/python

# please note that I am not setting the AWS region in this code which means that it will default to the AWS region of my shell where I run this script from.
# you can specify the region in the client call by setting the region_name parameter/value to the appropriate AWS region

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
print("Yor account id is: " + account_id)

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
            #if counter > 1:
            #    break
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

    #credentials = cred['Credentials']
    if acc['Id'] == rootaccount:

        sess=boto3.session.Session()
    else:
        cred = role_to_session(acc['Id'])
        credentials = cred['Credentials']
        sess= boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])

    return sess


def getsessionv2(acc):
    #print "\n\n========================================"
    #print "account id " + acc['Id']
    #print "account name " + acc['Name']
    #print "========================================"
    #if acc['Id']==rootaccount:
    if acc==rootaccount:

        sess=boto3.session.Session()
    else:
        #cred = role_to_session(acc['Id'])
        cred = role_to_session(acc)


        credentials = cred['Credentials']


        sess= boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    #print "\n\n========================================"
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

    parser.add_argument('--natgateway', action="store_true", required=False,
                        help='--natgateway')
    parser.add_argument('--s3_probe', type=str, required=False,
                        help='analyze or probe s3 i.e. ./misc_cli.py --s3_prob s4-bucketname .')

    parser.add_argument('--listuser', type=str, required=False,
                        help='list all aws account users')


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
    parser.add_argument('--unused_secgroup',required=False, help='to find unused security group on all  accounts .i.e ./miscli.py --unused_secgroup us-east-1')


    args = parser.parse_args()
    if args.s3list:
        s3listallsub(args.s3list)
    if args.natgateway:
        natgateway()
    if args.listuser:
        listuser(args.listuser)
    if args.s3_probe:
        s3_probe(args.s3_probe)
    elif args.ssmget:
        ssmgetallsub(args.ssmget)
    elif args.ssmupdate and args.ssmupdatevalue:
        update_ssmsub(args.ssmupdate,args.ssmupdatevalue)
    elif args.unused_secgroup:
        unused_secgroup(args.unused_secgroup)
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



def listuser(subaccount):
    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])
        if 'suspend' not in account['Status'].lower():
       	    print "\n\n\n" + account['Id'], account['Name'], account['Arn']
            print "============================================="
            ###     #if account['Id'] != rootaccount:
            #if account['Id'] != rootaccount:

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            iam=client_sess.client('iam', region_name='us-east-1')
            try:
                #response = sc_client.list_user()
                paginator = iam.get_paginator('list_users')
                for response in paginator.paginate():
                    for resp in response['Users']:
                        #print(resp['UserName'],',',resp['PasswordLastUsed'])
                        print resp['UserName'] + "," + str(resp.get('PasswordLastUsed','never used'))
            except:
                print("Error getting")



def s3_probe(bucket):
    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print "\n\n\n" + account['Id'], account['Name'], account['Arn']
        print "============================================="
        ###     #if account['Id'] != rootaccount:
        #if account['Id'] != rootaccount:

        client_sess = getsessionv2(account)
        #clientcf=client_sess.client('cloudformation')
        sc_client=client_sess.client('s3', region_name='us-east-1')
        try:
            response = sc_client.list_buckets()
            for bucket in  response['Buckets']:

                print("bucket name  : " + bucket['Name'])
                #if s3list == bucket['Name']:
                #    print "Found in " + account['Id']
                #    print "Found in " + account['Id']
                #    inp=raw_input('continue')
        except:
            print("Error getting")







def listvpc():
    print "Listing VPC and subnet info on all accounts "
    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])

        print account['Id'], account['Name'], account['Arn']
        ###     #if account['Id'] != rootaccount:
        if account['Id'] != rootaccount and 'suspend' not in account['Status'].lower():

            client_sess = getsession(account)
            #clientcf=client_sess.client('cloudformation')
            sc_client=client_sess.client('ec2', region_name='us-east-1')
            try:
                response = sc_client.describe_vpcs()
                resp = response['Vpcs']
                if resp:
                    for rp in resp:
                        #if rp['IsDefault']:
                        #    return rp['VpcId']
                        print(rp['CidrBlock']) + " VPC ID " + rp['VpcId'] + " Is Default " + str(rp['IsDefault']) + " Tag " + str(rp.get('Tags',"NA"))
                else:
                    print('No vpcs found')
            except:
                print("Error getting")
                raise


def natgateway():
    print ("Finding Nat Gateway IP address" )
    Account_Session.initialize()
    try:

        for account,sessinfo in Account_Session.SESS_DICT.items():
            print "checking nat gateway on account : "  + account
            client=sessinfo['session'].client('ec2')
            natgatewaylist=client.describe_nat_gateways()['NatGateways']
            for natg in natgatewaylist:
                #print "Nat-Gaweway IP " + natg['NatGatewayAddresses'][0]['PublicIp '] + ' On VPC :  ' + natg['VpcId']
                print "Nat " + str(natg['NatGatewayAddresses'][0]['PublicIp'])
                #Nat [{u'PublicIp': '3.223.101.188', u'NetworkInterfaceId': 'eni-0c5d59863fe1e78cd', u'AllocationId': 'eipalloc-0bfb8fcd5b89c4517', u'PrivateIp': '10.70.76.134'}]



    except Exception as err:
        print str(err)
        raise



def kms_grant(kmsidarn):
    print ("Grant Key {} all accounts".format(kmsidarn))
    #Account_Session.initialize()
    try:
        Account_Session.initialize()
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




def unused_secgroup(region,delete=False):
    print "Finding unused Security Group .."

    print "reg " + region
    Account_Session.initialize()
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print "checking account : "  + account
            client=sessinfo['session'].client('ec2')

            regions_dict = client.describe_regions()

            region_list = [region['RegionName'] for region in regions_dict['Regions']]

            # parse arguments


            client=sessinfo['session'].client('ec2')
            ec2 = sessinfo['session'].resource('ec2')
            all_groups = []
            security_groups_in_use = []
            # Get ALL security groups names
            security_groups_dict = client.describe_security_groups()
            security_groups = security_groups_dict['SecurityGroups']
            for groupobj in security_groups:
                if groupobj['GroupName'] == 'default' or groupobj['GroupName'].startswith('d-') or groupobj['GroupName'].startswith('AWS-OpsWorks-'):
                    security_groups_in_use.append(groupobj['GroupId'])
            all_groups.append(groupobj['GroupId'])

            # Get all security groups used by instances
            instances_dict = client.describe_instances()
            reservations = instances_dict['Reservations']
            network_interface_count = 0

            for i in reservations:
                for j in i['Instances']:
                    for k in j['SecurityGroups']:
                        if k['GroupId'] not in security_groups_in_use:
                            security_groups_in_use.append(k['GroupId'])

            # Security Groups in use by Network Interfaces
            #eni_client = boto3.client('ec2', region_name=args.region)
            eni_dict = client.describe_network_interfaces()
            for i in eni_dict['NetworkInterfaces']:
                for j in i['Groups']:
                    if j['GroupId'] not in security_groups_in_use:
                        security_groups_in_use.append(j['GroupId'])

            # Security groups used by classic ELBs
            elb_client = sessinfo['session'].client('elb')
            elb_dict = elb_client.describe_load_balancers()
            for i in elb_dict['LoadBalancerDescriptions']:
                for j in i['SecurityGroups']:
                    print "SEC GROUP In Use " + str()
                    if j not in security_groups_in_use:
                         security_groups_in_use.append(j)

            # Security groups used by ALBs
            elb2_client = sessinfo['session'].client('elbv2')
            elb2_dict = elb2_client.describe_load_balancers()
            for i in elb2_dict['LoadBalancers']:
            #for j in i['SecurityGroups']:
                for j in i.get('SecurityGroups','NA'):
                     if j not in security_groups_in_use:
                        security_groups_in_use.append(j)

            # Security groups used by RDS
            rds_client = sessinfo['session'].client('rds')
            rds_dict = rds_client.describe_db_instances()
            for i in rds_dict['DBInstances']:
                for j in i['VpcSecurityGroups']:
                     if j['VpcSecurityGroupId'] not in security_groups_in_use:
                         security_groups_in_use.append(j['VpcSecurityGroupId'])
            print "SEC GROUP In Use " + str()



            delete_candidates = []
            for group in all_groups:
                if group not in security_groups_in_use:
                    print str(delete_candidates)
                    delete_candidates.append(group)

            if delete:
                print("We will now delete security groups identified to not be in use.")
                for group in delete_candidates:
                    security_group = ec2.SecurityGroup(group)
                    try:
                        ##security_group.delete()
                        print "DDDDDD"
                    except Exception as e:
                        print(e)
                        print("{0} requires manual remediation.".format(security_group.group_name))
            else:
                print("The list of security groups to be removed is below.")
                print("Run this again with `-d` to remove them")
                for group in sorted(delete_candidates):
                    print("   " + group)

            print("---------------")
            print("Activity Report")
            print("---------------")

            print(u"Total number of Security Groups evaluated: {0:d}".format(len(all_groups)))
            print(u"Total number of EC2 Instances evaluated: {0:d}".format(len(reservations)))
            print(u"Total number of Load Balancers evaluated: {0:d}".format(len(elb_dict['LoadBalancerDescriptions']) +
                                                                            len(elb2_dict['LoadBalancers'])))
            print(u"Total number of RDS Instances evaluated: {0:d}".format(len(rds_dict['DBInstances'])))
            print(u"Total number of Network Interfaces evaluated: {0:d}".format(len(eni_dict['NetworkInterfaces'])))
            print(u"Total number of Security Groups in-use evaluated: {0:d}".format(len(security_groups_in_use)))
            if delete:
                print(u"Total number of Unused Security Groups deleted: {0:d}".format(len(delete_candidates)))
            else:

                print(u"Total number of Unused Security Groups targeted for removal: {0:d}".format(len(delete_candidates)))

    except Exception as err:
        print "error .." + str(err)
        raise
def dbclusterparam(dbclusterpar='sema4auroramysql57',family='aurora-mysql5.7'):
    print "create db cluster parameter group " + dbclusterpar
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
                    DBClusterParameterGroupName=dbclusterpar,
                    DBParameterGroupFamily=family,
                    Description=family)
                print response['DBClusterParameterGroup']['DBClusterParameterGroupName']
                inp=raw_input('pause ')


            except:
                print("Error getting")



def dbdbparam(dbdbpar='sema4auroramysql57',family='aurora-mysql5.7'):
    print "create db parameter group " + dbdbpar
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
                    DBParameterGroupName=dbdbpar,
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
        if account['Id'] != rootaccount and "suspend" not in  account['Status'].lower():

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
                        resp = sc_client.get_parameter(
                            Name=param['Name']
                        )
                        print "SSM Parameter " + resp['Parameter']['Name'] + ' with value : ' + resp['Parameter']['Value']
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


fadsf='d:\\fdaf\\'



if __name__ == '__main__':
    main()
