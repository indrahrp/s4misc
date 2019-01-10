import boto3

print ('user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
client = boto3.client('organizations')
rootaccount="r-011825642366"
#response = client.list_accounts_for_parent(ParentId=rootaccount,NextToken='ttt',MaxResults=12)
response = client.list_accounts(MaxResults=20)
#print response['Accounts']
responsemore = client.list_accounts(NextToken=response['NextToken'])
for account in responsemore['Accounts']:
    print account['Id'], account['Name'], account['Arn']