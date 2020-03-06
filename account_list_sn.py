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
    if 'non-phi' in account['Name'].lower():
        phi='Non-PHI'
    elif 'phi' in account['Name'].lower():
        phi='PHI'
    elif 'prod' in account['Name'].lower():
        phi='PHI'
    elif 'test' in account['Name'].lower():
        phi='PHI'
    else:
        phi='unknown'

    if 'prod' in account['Name'].lower():
        account_type='PROD'
    elif 'dev' in account['Name'].lower():
        account_type='DEV'
    elif 'test' in account['Name'].lower():
        account_type='TEST'
    else:
        account_type='unknown'

    #print account['Name'],",",account['Id'], account['Email'], account_type,phi,account['Status'],str(account['JoinedTimestamp'])
    print account['Name'],account['Id'],account['Email'], account_type,phi,account['Status'],str(account['JoinedTimestamp'])
