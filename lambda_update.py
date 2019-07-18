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
                        choices=["sub-account-list", "s3-list","ebsvol-list","findec2byeip","updatefunc"])
    #parser.add_argument('--db_identifier',
    #                    help='db_instance_identifier ',
    #                    type=str)
    parser.add_argument('--unencrypted', help="Flag to only show unencrypted Volume", action='store_true')
    #parser.add_argument('--findec2byeip', help="Find EC2 instance assigned to an elastic IP  ", action='store',required=True)
    parser.add_argument('--funcname', help="Lambda Function Name  ", action='store',required=True)
    parser.add_argument('--s3bucket', help="s3 bucket where lambda is  ", action='store',required=True)
    parser.add_argument('--s3key', help="s3 key obj  ", action='store',required=True)

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
    elif command == 'updatefunc':
        update_func(args.funcname,args.s3bucket,args.s3key)

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

def update_func(functionname,s3bucket,s3key):


    for acc in responsemore['Accounts']:
        #print "accis " + str(acc['Id'])
        sess=getsession(acc)

        lambda_client = sess.client('lambda')
        #lambda_client.update_function_code(
        #    FunctionName=functionname,
        #    S3Bucket=s3bucket,
        #    S3Key=s3key
        #)





if __name__ == "__main__":
    main(sys.argv[1:])