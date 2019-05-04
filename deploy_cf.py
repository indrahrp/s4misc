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
          '006775277657'
            '011825642366']

def _stack_exists(stack_name,clientcf):
    #stacks = clientcf.list_stacks()['StackSummaries']
    #print "stack exist stack_name " + stack_name
    for stack in paginate(clientcf.list_stacks):
        #print account['Id'], account['Name'], account['Arn']
        #print str(stack['StackName']) + str(stack['StackStatus'])


        #print "in stack loop " + stack['StackName']
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name.upper() == stack['StackName'].upper():
            return True
    return False


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

def stack_status(stack_name,sess):
    cf = sess.resource('cloudformation')
    ##python  deploy_cf.py --templatefile ..\ITProdSupport\DevOpsStam\AWS\cloudformation\Sema4-AWS-Template\Sema4-IT-Lambda.1.yaml
    ##--subaccount 333080083406  --name  test --stack_status itlamtest
    #python  deploy_cf.py --name ITAdmin-Role --templatefile ..\ITProdSupport\DevOpsStam\AWS\cloudformation\Sema4-AWS-Template\Sema4-ITAdmin_Role.yaml --name ITAdmin-Role --subaccount 417302553802
    #print "in stack_stauts"
    cfobj= cf.Stack(stack_name)
    #print "status of the stack " + stack_name
    #print str(cfobj.stack_name)
    print str(cfobj.stack_status)
    print str(cfobj.stack_status_reason)
    events=cfobj.events.all()
    #print "events " + str(events)
    for event in events:
        ###print (event.logical_resource_id,event.physical_resource_id,event.resource_properties,event.resource_status,event.resource_status_reason,event.resource_type)
        print (event.logical_resource_id,event.physical_resource_id,event.resource_status,event.resource_status_reason,event.resource_type)
    ##print "parm " + str(cfobj.parameters)
    for param in cfobj.parameters:
        #print ("parameter : " , str(param.get('ParameterKey',"NA")))
        print ("parameter : " , str(param))
    ##print str(cfobj.outputs)
    if cfobj.outputs:
        for output in cfobj.outputs:
             print ("output: " , str(output))
             #print "output "

def stack_list(sess):
    cf = sess.resource('cloudformation')
    ##python  deploy_cf.py --templatefile ..\ITProdSupport\DevOpsStam\AWS\cloudformation\Sema4-AWS-Template\Sema4-IT-Lambda.1.yaml
    ##--subaccount 333080083406  --name  test --stack_status itlamtest
    stacklist= cf.stacks.all()
    print "List of Stack :"
    #print str(cfobj.stack_name)

    for stack in stacklist:

        ###print (event.logical_resource_id,event.physical_resource_id,event.resource_properties,event.resource_status,event.resource_status_reason,event.resource_type)
        # print (event.logical_resource_id,event.physical_resource_id,event.resource_status,event.resource_status_reason,event.resource_type)
        #print "Name {%20s} Created {%10s}".format(stack.stack_name,stack.creation_time)
        ##print "parm " + str(cfobj.parameters)
        print "--------------------------------------------------------------"
        print stack.stack_name,stack.stack_status,stack.outputs




def stack_delete(stack_name,sess,retained):
    cf = sess.client('cloudformation')
    retained_resources=[]
    try:
        retained_resources = retained if retained else []

        if retained and len(retained)>0:
            retained_respources = retained.split(",")

        print "in stack_Delete" + str(type(retained_resources))
        print "in stack_Delete" + stack_name

        response = cf.delete_stack(
            StackName=stack_name,
            RetainResources=retained_resources
        )

        # we expect a response, if its missing on non 200 then show response
        if 'ResponseMetadata' in response and \
                response['ResponseMetadata']['HTTPStatusCode'] < 300:
            logging.info("succeed. response: {0}".format(json.dumps(response)))
        else:
            logging.critical("There was an Unexpected error. response: {0}".format(json.dumps(response)))

    except ValueError as e:
        logging.critical("Value error caught: {0}".format(e))
    except:
        # catch any failure
        logging.critical("Unexpected error: {0}".format(sys.exc_info()[0]))











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
    parser.add_argument('--templatefile', type=str, required=False,
                        help='template file of CF stack i.e file://Sema4.yaml')
    parser.add_argument('--subaccount', type=str, required=False,
                        help='a specific account to deploy')
    parser.add_argument('--params', type=str, required=False,
                        help="input parameters of the stack i.e. --params 'BucketName=s4-research-sanofi&ITLambda=ITAdmin'")

    parser.add_argument('--topicarn', type=str, required=False,
                        help='the SNS topic arn for notifications to be sent to.')

    parser.add_argument('--log', type=str, default="INFO", required=False,
                        help='which log level. DEBUG, INFO, WARNING, CRITICAL')
    parser.add_argument('--tags', type=str, required=False,
                        help='the tags to attach to the stack.')

    parser.add_argument('--stack_status_all', type=str, required=False,
                        help='check a specific deployment in all  account.')

    parser.add_argument('--deploy_all',action="store_true",required=False,default=False,
                        help='True or False to deploy to  all  account.')
    parser.add_argument('--yes_all',action="store_true",required=False,default=False,
                        help='True or False to Yes All To deploy to All account.')






    parser.add_argument('--stack_status', type=str, required=False,
                        help='the status of the stack.')
    parser.add_argument('--stack_delete', type=str, required=False,
                        help='to delete a stack. It needs to specify sub account where stack lives off.')
    parser.add_argument('--retained', type=str, required=False,
                        help='Resource to retain when deleting the stack.')

    parser.add_argument('--stack_list', action="store_true", default=False,required=False,
                        help='List Of Cloudformation Stack.')
    args = parser.parse_args()
    #print "args "+ str(args)
    if args.subaccount or args.stack_delete:
        deploylist=[args.subaccount]
        #print "in aotherremoving deploylist"
    elif args.stack_status_all:
        #print "removing deploylist"
        deploylist=[]
        #print "in aotherremoving deploylist"
    elif args.deploy_all:
        #print "removing deploylist"
        deploylist=[]


    # init LOGGER
    logging.basicConfig(level=get_log_level(args.log), format=LOG_FORMAT)

    #load the client using app config or default
    #client = make_cloudformation_client(args.config)


    print ('start with root user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
    client = boto3.client('organizations')
    ##client2 = boto3.client('ec2'

    #)
    rootaccount="011825642366"
    #response = client.list_accounts(MaxResults=10)

    client = boto3.client('organizations')
    for account in paginate(client.list_accounts):
         #print "result  " + str(account['Id'])
         if account['Id'] in deploylist or len(deploylist) == 0:
            #print account['Id'], account['Name'], account['Arn']
           ###     #if account['Id'] != rootaccount:
            if account['Id'] == rootaccount:
                client_sess = boto3.session.Session()
                clientcf=client_sess.client('cloudformation')

            else:
                ##yn = raw_input(" YN  :"
                client_sess = getsession(account)
                clientcf=client_sess.client('cloudformation')
            try:
                #print "args " + str(args.stack_status_all)
                if args.stack_status:
                    #print "Stack " + args.stack_status + " Status "
                    stack_status(args.stack_status,client_sess)
                    return
                elif args.stack_status_all:
                    try:
                         #print "Stack " + args.stack_status_all + " Status all "
                         stack_status(args.stack_status_all,client_sess)
                    except:
                         print "stack " + args.stack_status_all + " does not exist"
                         #logging.critical("Validation error caught: {0}".format(v))
                    finally:
                         pass


                elif args.stack_list:
                    print "List of Stack : " + account['Id']
                    stack_list(client_sess)
                    return

                elif args.stack_delete:
                        print "Deleting this stack " + args.stack_delete
                        yn=raw_input('Type Y to delete the stack: ')
                        if yn == 'Y':
                            stack_delete(args.stack_delete,client_sess,args.retained)
                        else:
                            print "Delete Stack Canceled"

                else:
                    # setup the model
                    #template_object = get_json(args.templateurl)
                      yn='N'
                      params = make_kv_from_args(args.params, "Parameter", False) if args.params else []
                      print "parms " + str(params)
                      tags = make_kv_from_args(args.tags) if args.tags else []


                      #print str(args.templatefile)
                      with open(args.templatefile,'r') as f:
                          ##print " file content " + str(f)
                          allparams={
                              'StackName' : args.name,
                              'TemplateBody' : f.read(),
                              'Parameters': params,
                              'Capabilities' :['CAPABILITY_IAM','CAPABILITY_NAMED_IAM'],
                              'Tags': tags
                          }
                          print "stack name " + args.name
                          if _stack_exists(args.name,clientcf):
                              print('Updating Stack {}'.format(args.name))
                              if  args.yes_all:
                                  yn='Y'
                              else:
                                  yn=raw_input('Type Y to update the stack : ')
                              if yn == 'Y':
                                  response = clientcf.update_stack(**allparams)
                                  waiter = clientcf.get_waiter('stack_update_complete')
                                  waiter.wait(StackName=args.name)
                                  # we expect a response, if its missing on non 200 then show response
                                  if 'ResponseMetadata' in response and  response['ResponseMetadata']['HTTPStatusCode'] < 300:
                                      logging.info("succeed. response: {0}".format(json.dumps(response)))
                                  else:
                                      logging.critical("There was an Unexpected error. response: {0}".format(json.dumps(response)))

                              else:
                                    print "Update Stack Canceled "


                          else:
                              print('Creating Stack {}'.format(args.name))
                              yn='N'
                              if  args.yes_all:
                                  yn='Y'
                              else:
                                  yn=raw_input('Type Y to create the stack : ')
                              if yn == 'Y':
                                  response = clientcf.create_stack(**allparams)
                                  waiter = clientcf.get_waiter('stack_create_complete')
                                  waiter.wait(StackName=args.name)
                                  # we expect a response, if its missing on non 200 then show response
                                  if 'ResponseMetadata' in response and  response['ResponseMetadata']['HTTPStatusCode'] < 300:
                                     logging.info("succeed. response: {0}".format(json.dumps(response)))
                                  else:
                                     logging.critical("There was an Unexpected error. response: {0}".format(json.dumps(response)))

                              else:
                                  print "Stack Creation Canceled "

            except ValueError as e:
               logging.critical("Value error caught: {0}".format(e))
            except botocore.exceptions.ClientError as e:
               logging.critical("Boto client error caught: {0}".format(e))


            except:
              ##catch any failure
              logging.critical("Unexpected error: {0}".format(sys.exc_info()[0]))



if __name__ == '__main__':
    main()