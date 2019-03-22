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

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

LOGGER = logging.getLogger(__name__)

deploylist=['417302553802',
          '333080083406',
          '346997421618',
          '006775277657']

def paginate(method, **kwargs):
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

def get_log_level(level_string):
    levels = {
        "DEBUG":logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "CRITICAL":logging.CRITICAL
    }
    return levels[level_string]

def make_kv_from_args(params_as_querystring, name_prefix="", use_previous=None):

    nvs = parse_qs(params_as_querystring)

    #{'i': ['main'], 'enc': [' Hello '], 'mode': ['front'], 'sid': ['12ab']}
    kv_pairs = []
    for key in nvs:
        # print "key: %s , value: %s" % (key, nvs[key])
        kv = {
            "{0}Key".format(name_prefix):key,
            "{0}Value".format(name_prefix):nvs[key][0],
        }
        if use_previous != None:
            kv['UsePreviousValue'] = use_previous

        kv_pairs.append(kv)

    return kv_pairs

def parseyaml(inFileType, outFileType):
    #infile = input('Please enter a {} filename to parse: '.format(inFileType))
    #outfile = input('Please enter a {} filename to output: '.format(outFileType))

    with open(infile, 'r') as stream:
        try:
            datamap = yaml.safe_load(stream)
            with open(outfile, 'w') as output:
                json.dump(datamap, output)
        except yaml.YAMLError as exc:
            print(exc)

    print('Your file has been parsed.\n\n')


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
    ##python  deploy_cf.py --name test --templatefile Sema4-ITAdmin_Role.yaml --params ...
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True,
                        help='the name of the stack to create.')
    parser.add_argument('--templatefile', type=str, required=True,
                        help='template file of CF stack i.e file://Sema4.yaml')
    parser.add_argument('--subaccount', type=str, required=True,
                        help='a specific account to deploy')
    parser.add_argument('--params', type=str, required=False,
                        help='the key value pairs for the parameters of the stack.')
    parser.add_argument('--topicarn', type=str, required=False,
                        help='the SNS topic arn for notifications to be sent to.')
    parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
    parser.add_argument('--tags', type=str, required=False,
                        help='the tags to attach to the stack.')
    parser.add_argument('--config', type=str, required=False,
                        help='the config file used for the application.')

    args = parser.parse_args()
    if args.subaccount:
        deploylist=[args.subaccount]
    # init LOGGER
    logging.basicConfig(level=get_log_level(args.log), format=LOG_FORMAT)

    #load the client using app config or default
    #client = make_cloudformation_client(args.config)


    print ('user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
    client = boto3.client('organizations')
    ##client2 = boto3.client('ec2'

    #)
    rootaccount="011825642366"
    #response = client.list_accounts(MaxResults=10)

    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
        #print "result  " + str(account['Id'])
         if account['Id'] in deploylist or deploylist is []:
            print account['Id'], account['Name'], account['Arn']
           ###     #if account['Id'] != rootaccount:
            if account['Id'] != rootaccount:
                yn = raw_input(" YN  :")
                client_sess = getsession(account)
                print "CF client"
                clientcf=client_sess.client('cloudformation')
                try:
                    # setup the model
                    #template_object = get_json(args.templateurl)
                      params = make_kv_from_args(args.params, "Parameter", False)
                        #tags = make_kv_from_args(args.tags)
                      print "parameter"
                        #params=[
                        #    {
                        #        "ParameterKey": "BucketName",
                        #        "ParameterValue": "S4-it-cf-testindra"
                        #    }
                        #    ]
                      print str(params)
                      print str(args.templatefile)
                      with open(args.templatefile,'r') as f:
                          print " file content " + str(f)

                          response = clientcf.create_stack(
                              StackName=args.name,
                              TemplateBody=f.read(),
                              #Parameters=params,
                              Capabilities=[
                              'CAPABILITY_IAM','CAPABILITY_NAMED_IAM'
                               ],
                          )
                        #    Tags=tags


                    # we expect a response, if its missing on non 200 then show response
                    #if 'ResponseMetadata' in response and \
                    #        response['ResponseMetadata']['HTTPStatusCode'] < 300:
                    #    logging.info("succeed. response: {0}".format(json.dumps(response)))
                    #else:
                    #    logging.critical("There was an Unexpected error. response: {0}".format(json.dumps(response)))

                except ValueError as e:
                   logging.critical("Value error caught: {0}".format(e))
                except botocore.exceptions.ClientError as e:
                   logging.critical("Boto client error caught: {0}".format(e))
                except:
                  ##catch any failure
                  logging.critical("Unexpected error: {0}".format(sys.exc_info()[0]))



if __name__ == '__main__':
    main()