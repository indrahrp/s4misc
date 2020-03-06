'''Custom generic CloudFormation resource example'''

import json
import logging
import signal
import boto3
from urllib2 import build_opener, HTTPHandler, Request
from awspolicy import BucketPolicy

#LOGGER = logging.getLogger()
#LOGGER.setLevel(logging.INFO)

sts_client = boto3.client('sts')

def lc_intelligent_tier(bucket_name):

    s3 = boto3.resource('s3')
    s3Client = boto3.client('s3')
    bucket_lifecycle = s3.BucketLifecycle(bucket_name)
    #######LOGGER.info("in lcintelligentn_tier")
    #LOGGER.info(bucket_lifecycle)
    #LOGGER.info(bucket_name)



    response = bucket_lifecycle.put(
        LifecycleConfiguration={
            'Rules': [
                {
                    'Status': 'Enabled',
                    'Prefix': '',
                    'Transition':
                        {
                            'Days': 0,
                            'StorageClass': 'INTELLIGENT_TIERING'
                        }
                    ,
                    'ID': 'Intelligent_Tiering',
                    'NoncurrentVersionTransition': {
                        'NoncurrentDays': 0,
                        'StorageClass': 'INTELLIGENT_TIERING'
                    }
                }
            ]
        }
    )
    #LOGGER.info(response)

    print "Versioning and lifecycle have been enabled for buckets."

def bucket_policy(service_role,bucket_name,sub_account):

    #s3_client = boto3.client('s3')
    print "in bucket policy"
    subaccount={}
    subaccount["Id"]=sub_account
    sess = getsession(subaccount)
    s3_client = sess.client('s3')
    stsclient = sess.client('sts')


    #bucket_name = 'testcustomresourc47s3'

    # Load the bucket policy as an object
    bucket_policy = BucketPolicy(serviceModule=s3_client, resourceIdentifer=bucket_name)
    print "bucket policy dary call " + str(bucket_policy.get_policy())

    statementid= "CrossAccountAccess"
    #print "statement" + statementid
    print("Using  account: %s" % stsclient.get_caller_identity().get('Account'))
    print "bucket name " + bucket_name
    # Select the statement that will be modified
    statement_to_modify = bucket_policy.select_statement(statementid)
    print "statement llla " + str(statement_to_modify.source_policy.get_policy())

    # Insert new_user_arn into the list of Principal['AWS']
    #new_user_arn = 'arn:aws:iam::888888888888:user/daniel'
    print "servicerole" + service_role
    aaa=statement_to_modify.Principal['AWS']
    #statement_to_modify.Principal['AWS'].append(service_role)
    print str(aaa)
    print "servicerole after " + service_role

    # Save change of the statement
    statement_to_modify.save()

    # Save change of the policy. This will update the bucket policy
    statement_to_modify.source_policy.save() # Or bucket_policy.save()



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
    #print "account name " + acc['Name']
    print "========================================"
    cred = role_to_session(acc['Id'])
    credentials = cred['Credentials']


    sess= boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])

    return sess


def handler(event, context):
    '''Handle Lambda event from AWS'''
    # Setup alarm for remaining runtime minus a second
    #signal.alarm((context.get_remaining_time_in_millis() / 1000) - 1)
    try:
        #LOGGER.info('REQUEST RECEIVED:\n %s', event)
        #LOGGER.info('REQUEST RECEIVED:\n %s', context)
        print event
        #print event["ResourceProperties"]
        #print event["ResourceProperties"]["BucketName"]
        #print event["ResourceProperties"]["ec2name"]
        #print event["ResourceProperties"]["volumename"]

        if event['RequestType'] == 'Create':
            #LOGGER.info('CREATE!')
            if event["ResourceProperties"]['OpsType'] == 'set_bucket_policy':
                 bucketname=event["ResourceProperties"]["BucketName"]
                 subaccount=event["ResourceProperties"]["SubAccount"]
                 lambdaexecrole=event["ResourceProperties"]["LambdaExecRole"]
                 print "IN BUCKET"
                 bucket_policy(lambdaexecrole,bucketname,subaccount)
                 send_response(event, context, "SUCCESS",
                               {"Message": "Resource creation successful!"})

            if event["ResourceProperties"]['OpsType'] == 'set_lifecycle':
                 bucketname=event["ResourceProperties"]["BucketName"]
                 lc_intelligent_tier(bucketname)

                 send_response(event, context, "SUCCESS",
                          {"Message": "Resource creation successful!"})
            else:
                 #LOGGER.info('Operation is not Supported!')
                 print "operation is not supported"

        elif event['RequestType'] == 'Update':
            LOGGER.info('UPDATE!')
            send_response(event, context, "SUCCESS",
                      {"Message": "Resource update successful!"})
        elif event['RequestType'] == 'Delete':
            LOGGER.info('DELETE!')
            send_response(event, context, "SUCCESS",
                      {"Message": "Resource deletion successful!"})
        else:
            LOGGER.info('FAILED!')
            send_response(event, context, "FAILED",
                          {"Message": "Unexpected event received from CloudFormation"})

    except Exception as  error:

            #LOGGER.info('FAILED!')
            #LOGGER.info(Exception)
            #LOGGER.info(error)
            print "exception thrown .." + str(error)
            send_response(event, context, "FAILED", {
                "Message": "Exception during processing"})


def send_response(event, context, response_status, response_data):
    '''Send a resource manipulation status response to CloudFormation'''
    print "osscontext"
    #print  str(context)
    print "thecontext"
    #print str(context)
    print "after thecontext"
    #print  str(context['log_stream_name'])
    print "after thecontext"

    response_body = json.dumps({
        "Status": response_status,
        "Reason": "See the details in CloudWatch Log Stream: " + context['log_stream_name'],
        "PhysicalResourceId": 'customlambda_function',
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": response_data
    })

    #LOGGER.info('ResponseURL: %s', event['ResponseURL'])
    #LOGGER.info('ResponseBody: %s', response_body)

    ###opener = build_opener(HTTPHandler)
    ###request = Request(event['ResponseURL'], data=response_body)
    ###request.add_header('Content-Type', '')
    ###request.add_header('Content-Length', len(response_body))
    ###request.get_method = lambda: 'PUT'
    ###response = opener.open(request)
    ###LOGGER.info("Status code: %s", response.getcode())
    ###LOGGER.info("Status message: %s", response.msg)


def timeout_handler(_signal, _frame):
    '''Handle SIGALRM'''
    raise Exception('Time exceeded')



print ('user acount {}'.format(boto3.client('sts').get_caller_identity()))

signal.signal(signal.SIGTERM, timeout_handler)

if __name__ == '__main__':
    request1 = {
        'StackId': 'arn:aws:cloudformation:us-west-2:accountgoeshere:stack/sample-stack/stackidgoeshere',
        'ResponseURL': 'https://test.com',
        'ResourceProperties': {
            'BucketName': 'team1-dev',
            'ServiceToken': 'lambdaarn',
            'ec2name': 'app1',
            'volumename': 'testvolume'
        },
        'RequestType': 'Create',
        'ServiceToken': 'lambdaarn',
        'ResourceType': 'Custom::Lookup',
        'RequestId': 'sampleid',
        'LogicalResourceId': 'CUSTOMLOOKUP'
    }


    request2 = {
        'StackId': 'arn:aws:cloudformation:us-west-2:accountgoeshere:stack/sample-stack/stackidgoeshere',
        'ResponseURL': 'https://test.com',
        'ResourceProperties': {
            'BucketName': 's4-it-cf-bucket',
            'ServiceToken': 'lambdaarn',
            'SubAccount': '006775277657',
            'OpsType': 'set_bucket_policy',
            'LambdaExecRole': 'arn:aws:iam::417302553802:role/S3_lambda'
        },
        'RequestType': 'Create',
        'ServiceToken': 'lambdaarn',
        'ResourceType': 'Custom::Lookup',
        'RequestId': 'sampleid',
        'LogicalResourceId': 'CUSTOMLOOKUP'
    }
    context ={ 'log_stream_name' : 'testlogstream'}


    handler(request2,context)
