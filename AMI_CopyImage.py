import boto3
import json
import pprint

def  create_enc_image_from_image_handler(event, context):
    cfn_event = event['cfn_event']
    if cfn_event['RequestType'] == 'Update':
        resource_properties = cfn_event['ResourceProperties']
        old_resource_properties = cfn_event['OldResourceProperties']

        image_params = resource_properties['Image']
        old_image_params = old_resource_properties['Image']

        if image_params['Name'] == old_image_params['Name']:
            physical_resource_id = cfn_event['PhysicalResourceId']
            print("Deleting AMI {physical_resource_id} with name {old_image_params['Name']} "
                  "before creating a new AMI with the same name")
            delete_ami(ami_id=physical_resource_id)

    ami_id = create_enc_ami(event['ami_id'], cfn_event['ResourceProperties']['Image'])

    event['ami_id'] = ami_id

    return event

def create_enc_ami(image_id, image_params):
    client = boto3.client('ec2')

    for forbidden_param in ['InstanceId', 'NoReboot', 'DryRun']:
        if forbidden_param in image_params:
            del image_params[forbidden_param]

    response = client.copy_image(
        SourceImageId=image_id,
        SourceRegion='us-east-1',
        Encrypted=True,
        #DryRun=True,
        **image_params

    )

    ami_id = response['ImageId']

    return ami_id



event = {
    "cfn_event": {
        "RequestType": "Create",
        "ServiceToken": "arn:aws:lambda:us-east-1:417302553802:function:cfami-AMILambdaFunction-1A7XLWDLSADMM",
        "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A417302553802%3Astack/testami13/25ab8840-235d-11e9-852e-0eb85d5eff94%7CAMI%7C1aa46db9-4552-49d6-b94d-c60fb241fbb3?AWSAccessKeyId=AKIAI5B7XFKUGEZ7W2RQ&Expires=1548729201&Signature=y%2BJflvAaAcfIgH8%2BN0uTmORgHoY%3D",
        "StackId": "arn:aws:cloudformation:us-east-1:417302553802:stack/testami13/25ab8840-235d-11e9-852e-0eb85d5eff94",
        "RequestId": "1aa46db9-4552-49d6-b94d-c60fb241fbb3",
        "LogicalResourceId": "AMI",
        "ResourceType": "Custom::AMI",
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:us-east-1:417302553802:function:cfami-AMILambdaFunction-1A7XLWDLSADMM",
            "Image": {
                "Description": "some description for the image",
                "Name": "testaminipt"
            },
            "TemplateInstance": {
                "KeyName": "aws-eb",
                "UserData": "IyEvYmluL2Jhc2ggLXgKZWNobyAiVEVTVElHIiAjIHByb3Zpc2lvbmluZyBleGFtcGxlCiN5dW0tY29uZmlnLW1hbmFnZXIgLS1kaXNhYmxlIFwqCnl1bSBpbnN0YWxsIHdnZXQgLXkKeXVtIGluc3RhbGwgcHl0aG9uLXBpcCAteQojIFNpZ25hbCB0aGF0IHRoZSBpbnN0YW5jZSBpcyByZWFkeQpJTlNUQU5DRV9JRD1gd2dldCAtcSAtTyAtIGh0dHA6Ly8xNjkuMjU0LjE2OS4yNTQvbGF0ZXN0L21ldGEtZGF0YS9pbnN0YW5jZS1pZGAKL3Vzci9iaW4vcHl0aG9uLXBpcCBpbnN0YWxsIGF3c2NsaQovdXNyL2xvY2FsL2Jpbi9hd3MgZWMyIGNyZWF0ZS10YWdzIC0tcmVzb3VyY2VzICRJTlNUQU5DRV9JRCAtLXRhZ3MgS2V5PVVzZXJEYXRhRmluaXNoZWQsVmFsdWU9dHJ1ZSAtLXJlZ2lvbiB1cy1lYXN0LTEK",
                "ImageId": "ami-0bf2fb355727b7faf",
                "BlockDeviceMappings": [{
                    "Ebs": {
                        "VolumeType": "gp2",
                        "VolumeSize": "30"
                    },
                    "DeviceName": "/dev/xvdcz"
                }],
                "IamInstanceProfile": {
                    "Arn": "arn:aws:iam::417302553802:instance-profile/testami13-TemplateInstanceProfile-TY7ECPRO9CW7"
                },
                "SubnetId": "subnet-0e490b8fce25ce59c",
                "InstanceType": "t2.nano"
            }
        },
        "PhysicalResourceId": "cdf91fb7-fa5f-40d0-9827-7cf4c0b4f0f6"
    },
    "instance_id": "i-0ce3fbd8cd7a017a3",
    "instance_state": "READY",
    "ami_id": "ami-07dcc0e41c7676156",
    "image_state": "READY"
}
context=None
#event=json.dumps(varjson)
#print type(event)
#pprint.PrettyPrinter(event)
#context=None
#event=[]
#event[]
#cfn_event

create_enc_image_from_image_handler(event,context)