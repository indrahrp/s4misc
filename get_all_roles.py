#!/usr/bin/env python
# coding: utf-8

import os
import json
import logging
import argparse
import boto3
import botocore
import urllib2
import botocore
import sys
import time
import signal

from urlparse import urlparse, parse_qs
#from utils import make_cloudformation_client, load_config, get_log_level



# Parameters=[
#     {
#         'ParameterKey': 'string',
#         'ParameterValue': 'string',
#         'UsePreviousValue': False
#     },
# ],



def paginate(method, **kwargs):
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result






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


def main():
    global deploylist
    ##python  deploy_cf.py --name test --templatefile Sema4-ITAdmin_Role.yaml --params "BucketName=s4-research-sanofi-dev&ITLambda=ITAdmin_Libraries"
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=False,
                        help='the name of the stack to create.')


    print ('start with root user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
    client = boto3.client('organizations')
    ##client2 = boto3.client('ec2'

    #)
    rootaccount="011825642366"
    #response = client.list_accounts(MaxResults=10)

    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
         #print "result  " + str(account['Id'])

            if account['Id'] == rootaccount:
                client_sess = boto3.session.Session()
                clientiam=client_sess.client('iam')

            else:
                ##yn = raw_input(" YN  :"
                client_sess = getsession(account)
                clientiam=client_sess.client('iam')
            try:

                roles = clientiam.list_roles()
                Role_list = roles['Roles']
                for key in Role_list:
                    print key['RoleName']
                    print key['Arn']

            except:
              ##catch any failure
              logging.critical("Unexpected error: {0}".format(sys.exc_info()[0]))



if __name__ == '__main__':
    main()