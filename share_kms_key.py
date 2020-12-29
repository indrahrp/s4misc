# Get the policy for a CMK
import boto3
import json

kms_client=boto3.client('kms','us-east-1')
# Replace the following example key ARN with a valid key ID or key ARN
#key_id = 'arn:aws:kms:us-east-1:011825642366:key/2594efda-7062-4313-b194-c6776974c2ea'
key_id = 'arn:aws:kms:us-east-1:011825642366:key/dcda365b-40eb-4799-be46-5d8a9327ed18'
policy_name = 'default'

response = kms_client.get_key_policy(
    KeyId=key_id,
    PolicyName=policy_name
)


#json_object = json.loads(response)

#json_formatted_str = json.dumps(response, indent=2)

#print(json_formatted_str)

#policy=response['Policy']
#statement1=json.loads(policy)['Statement'][0]['Principal']
#print "statement is "+ str(statement1)

from awspolicy import BucketPolicy, KmsPolicy, IamRoleTrustPolicy
### Update KMS Key policy to allow a new account using CMK in centralized auditing account
kms = boto3.client('kms')
cmk_policy = KmsPolicy(serviceModule=kms, resourceIdentifer=key_id)
statement = cmk_policy.select_statement('Allow access for Key Administrators')
print str(cmk_policy.get_policy())
print "statme " + str(type(statement))

new_user_arn = "arn:aws:iam::011825642366:user/anandhu.panicker"
awsst=statement.Principal['AWS']
print "awsst is " + str(type(awsst))
print "awsst entr " + str(awsst)


if isinstance(awsst,unicode):
    print "dsini dict"
    awsl=[]
    awsl.append(awsst)
    awsl.append(new_user_arn)
    statement.Principal['AWS']=awsl
elif isinstance(awsst,list):
    print "disilin list "
    statement.Principal['AWS'].append(new_user_arn)


#statement.Principal['AWS']=awsl
    #print "aws pric" + str(awsl)




#statement.Condition['StringLike']['kms:EncryptionContext:aws:cloudtrail:arn'] += [u'arn:aws:cloudtrail:*:888888888888:trail/*']
statement.save()
print "princ " + str(statement.Principal)
statement.source_policy.save()
#statement.source_policy.save()


'''
response = kms_client.put_key_policy(
    KeyId=key_id,
    Policy=policy,
    PolicyName=policy_name
)
'''