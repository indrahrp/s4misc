import boto3
def paginate(method, **kwargs):
    print "met " + str(method.__name__) + "with kawrs " + str(kwargs)
    paginator = client.get_paginator(method.__name__)
    pp=paginator.paginate(**kwargs)
    #for p in pp:
    #    for dd in p['Accounts']:
    #        print "dd cont " + str(dd)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

print ('user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))

rootaccount="r-011825642366"

client= boto3.client('organizations')
for account in paginate(client.list_accounts):
        print account['Id'], account['Name'], account['Arn']
