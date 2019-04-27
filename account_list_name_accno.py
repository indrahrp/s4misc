import boto3


def paginate(method, **kwargs):
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

print ('user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))

rootaccount="r-011825642366"

client = boto3.client('organizations')
for account in paginate(client.list_accounts):
        print '- identifier: '+ account['Name'] + '\n' + '  number: ' + account['Id']
