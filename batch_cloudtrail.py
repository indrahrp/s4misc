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
import json

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


def getsessionv2(acc):
    #print "\n\n========================================"
    #print "account id " + acc['Id']
    #print "account name " + acc['Name']
    #print "========================================"
    if acc==rootaccount:
        sess=boto3.session.Session()
    else:
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

    parser.add_argument('--batch_ct', type=str, required=False,
                        help='analyze or probe s3 i.e. ./misc_cli.py --s3_prob s4-bucketname .')

    parser.add_argument('--subaccount', type=str, required=False,
                        help='a specific account to deploy')


    args = parser.parse_args()

    if args.batch_ct:
        batch_ct(args.batch_ct)


def batch_ct(subaccount):
    Account_Session.initialize()

    for account,sessinfo in Account_Session.SESS_DICT.items():
        try:
            print "checking account : "  + account
            ct_client=sessinfo['session'].client('cloudtrail')
            #ct_client=client('cloudtrail', region_name='us-east-1')
            events_dict= ct_client.lookup_events(LookupAttributes=[{'AttributeKey':'EventName', 'AttributeValue':'RunInstances'}])

            for data in events_dict['Events']:
                json_file= json.loads(data['CloudTrailEvent'])
                print str(json_file)
                #print (json_file['userIdentity']['userName'])

        except Exception as err:
                print("Error getting",err)




if __name__ == '__main__':
    main()
