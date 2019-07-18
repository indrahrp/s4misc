import boto3

ec2=boto3.client('ec2')
ec2.create_tags(Resources=['i-02c1fd2e398219d69'], Tags=[{'Key':'name', 'Value':'apphostname'}])