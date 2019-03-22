
import boto3,argparse
from awspolicy import BucketPolicy


def bucket_policy(service_role,bucket_name,session):

    s3_client = session.client('s3')
    #bucket_name = 'testcustomresourc47s3'

    # Load the bucket policy as an object
    bucket_policy = BucketPolicy(serviceModule=s3_client, resourceIdentifer=bucket_name)
    statementid= "CrossAccountAccess"

    # Select the statement that will be modified
    statement_to_modify = bucket_policy.select_statement(statementid)

    # Insert new_user_arn into the list of Principal['AWS']
    #new_user_arn = 'arn:aws:iam::888888888888:user/daniel'
    statement_to_modify.Principal['AWS'].append(service_role)
    print "statemement to modify " + str(statement_to_modify.Principal['AWS'])

    # Save change of the statement
    statement_to_modify.save()

    # Save change of the policy. This will update the bucket policy
    statement_to_modify.source_policy.save() # Or bucket_policy.save()






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


def main(arn,bucket_name,account):
    ##python  deploy_cf.py --name test --templatefile Sema4-ITAdmin_Role.yaml --params ...
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket_name', type=str, required=True,
                        help='bucket name .')
    parser.add_argument('--arn', type=str, required=True,
                        help='role arn')
    parser.add_argument('--accountid', type=str, required=True,
                        help='account id which owned the bucket')
    args = parser.parse_args()


    print ('user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
    client = boto3.client('organizations')
    ##client2 = boto3.client('ec2'

    #)
    rootaccount="011825642366"
    response = client.list_accounts(MaxResults=10)

    #while response.get('NextToken',False):
    #    for account in response['Accounts']:
    #        print account['Id'], account['Name'], account['Arn']
    #        if account['Id'] != rootaccount:
    #            yn = raw_input(" YN  :")
    client_sess = getsession(account)
    print "CF client"
    #clientcf=client_sess.client('cloudformation')
    try:
        bucket_policy(arn,bucket_name,client_sess)
    except Exception as e:
        print str(e)




if __name__ == '__main__':

    ##arn='arn:aws:iam::417302553802:role/S3_lambda'
    account={}
    account['Id']='417302553802'
    account['Name'] = 'test'

    arn='arn:aws:iam::586916032531:role/ITAdmin-Role'
    bucket_name='testcustomresourc43'
    main(arn,bucket_name,account)