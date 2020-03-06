
import boto3
from awspolicy import BucketPolicy


def bucket_policy(service_role,bucket_name):

    s3_client = boto3.client('s3')
    #bucket_name = 'testcustomresourc47s3'

    # Load the bucket policy as an object
    bucket_policy = BucketPolicy(serviceModule=s3_client, resourceIdentifer=bucket_name)
    statementid= "CrossAccountAccess"

    # Select the statement that will be modified
    statement_to_modify = bucket_policy.select_statement(statementid)

    # Insert new_user_arn into the list of Principal['AWS']
    #new_user_arn = 'arn:aws:iam::888888888888:user/daniel'
    statement_to_modify.Principal['AWS'].append(service_role)
    print str(statement_to_modify.Principal['AWS'])

    # Save change of the statement
    statement_to_modify.save()

    # Save change of the policy. This will update the bucket policy
    statement_to_modify.source_policy.save() # Or bucket_policy.save()

if __name__ == '__main__':
    lambda_arn='arn:aws:iam::417302553802:role/S3_lambda'
    bucket_name='testcustomresourc43'
    bucket_policy(lambda_arn,bucket_name)