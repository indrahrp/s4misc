import boto3
conn=boto3.client('ec2')
dct=conn.describe_instances(
    Filters=[
       {
         'Name':'tag:owner',
         'Values': [
            'drain'
          ]
       },
       {
         'Name': 'tag:namaku',
         'Values': [
            'somse',
            'ola'
         ]

    }
    ]
)
print dct
