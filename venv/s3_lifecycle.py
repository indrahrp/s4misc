import boto3
from datetime import datetime
print ('user acount {}'.format(boto3.client('sts').get_caller_identity().get('Account')))
bucket='test73stckbucket'
s3 = boto3.resource('s3')
s3Client = boto3.client('s3')
bucket_lifecycle = s3.BucketLifecycle('test73stckbucket')

#rint bucket_lifecycle.rules



response = bucket_lifecycle.put(
    LifecycleConfiguration={
        'Rules': [
            {
                'Expiration': {
                    'Date': datetime(2015, 1, 1),
                    'Days': 123,
                    'ExpiredObjectDeleteMarker': True
                },
                'ID': 'intelligent_tier lifecycle',
                'Prefix': 'fdaf',
                'Status': 'Enabled',
                'Transition': {

                    'Days': 123,
                    'StorageClass': 'STANDARD_IA'
                },
                'NoncurrentVersionTransition': {
                    'NoncurrentDays': 123,
                    'StorageClass': 'STANDARD_IA'
                }

            }
        ]
    }
   )

print "Versioning and lifecycle have been enabled for buckets."

#print bucket_lifecycle