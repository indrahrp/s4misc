#!/usr/bin/python

"""
Overview:
    Iterate through each attached volume and encrypt it for EC2.
Params:
    ID for EC2 instance
    Customer Master Key (CMK) (optional)
    Profile to use
Conditions:
    Return if volume already encrypted
    Use named profiles from credentials file
"""

import sys
import boto3
import botocore
import argparse
import pprint

TARGET_ACCOUNT_ID = '316878946072'
ROLE_ON_TARGET_ACCOUNT = 'arn:aws:iam::316878946072:role/OrganizationAccountAccessRole'
SOURCE_REGION = 'us-east-1'
TARGET_REGION = 'us-east-1'


def role_arn_to_session(**args):
    """
    Lets you assume a role and returns a session ready to use
    Usage :
        session = role_arn_to_session(
            RoleArn='arn:aws:iam::012345678901:role/example-role',
            RoleSessionName='ExampleSessionName')
        client = session.client('sqs')
    """
    client = boto3.client('sts')
    response = client.assume_role(**args)
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])



def main(argv):

    device_snap = {}
    pp=pprint.PrettyPrinter(indent=4)

    parser = argparse.ArgumentParser(description='Encrypts EC2 root volume.')
    parser.add_argument('-i', '--instance',
                        help='Instance to encrypt volume on.', required=True)
    parser.add_argument('-key', '--customer_master_key',
                        help='Customer master key', required=True)
    parser.add_argument('-p', '--profile',
                        help='Profile to use', required=False)
    parser.add_argument('-r', '--region',
                        help='Region of source volume', required=True)
    args = parser.parse_args()

    """ Set up AWS Session + Client + Resources + Waiters """
    if args.profile:
        # Create custom session
        print('Using profile {}'.format(args.profile))
        session = boto3.session.Session(profile_name=args.profile)
    else:
        # Use default session
        session = boto3.session.Session()

    # Get CMK
    customer_master_key = args.customer_master_key
    print ("customer master key {}".format(customer_master_key))

    client = session.client('ec2')
    ec2 = session.resource('ec2')

    waiter_instance_exists = client.get_waiter('instance_exists')
    waiter_instance_stopped = client.get_waiter('instance_stopped')
    waiter_instance_running = client.get_waiter('instance_running')
    waiter_snapshot_complete = client.get_waiter('snapshot_completed')
    waiter_snapshot_complete.config.max_attempts = 1000
    waiter_volume_available = client.get_waiter('volume_available')

    """ Check instance exists """
    instance_id = args.instance
    print('---Checking instance ({})'.format(instance_id))
    instance = ec2.Instance(instance_id)

    try:
        waiter_instance_exists.wait(
            InstanceIds=[
                instance_id,
            ]
        )
    except botocore.exceptions.WaiterError as e:
        sys.exit('ERROR: {}'.format(e))

    all_mappings = []
    all_sub_mappings = []

    block_device_mappings = instance.block_device_mappings
    pp.pprint(block_device_mappings)

    for device_mapping in block_device_mappings:
        original_mappings = {
            'DeleteOnTermination': device_mapping['Ebs']['DeleteOnTermination'],
            'VolumeId': device_mapping['Ebs']['VolumeId'],
            'DeviceName': device_mapping['DeviceName'],
        }

        all_mappings.append(original_mappings)
        sub_mappings = {
            'Ebs': {'DeleteOnTermination': device_mapping['Ebs']['DeleteOnTermination']},
            'DeviceName': device_mapping['DeviceName'],
            'Ebs': {'SnapshotId':''},
        }
        all_sub_mappings.append(sub_mappings)


    pp.pprint(all_sub_mappings)
    volume_data = []

    print('---Preparing instance')
    """ Get volume and check if it is  already encrypted """
    volumes = [v for v in instance.volumes.all()]
    for volume in volumes:
        volume_encrypted = volume.encrypted

        current_volume_data = {}
        for mapping in all_mappings:
            if mapping['VolumeId'] == volume.volume_id:
                current_volume_data = {
                    'volume': volume,
                    'DeleteOnTermination': mapping['DeleteOnTermination'],
                    'DeviceName': mapping['DeviceName'],
                }

        if volume_encrypted:
            #sys.exit(
            print (  '**Volume ({}) is already encrypted but it will be reencrypted with sema4 Key'
                    .format(volume.id))


        """ Step 1: Prepare instance """

        # Exit if instance is pending, shutting-down, or terminated
        instance_exit_states = [0, 32, 48]
        if instance.state['Code'] in instance_exit_states:
            sys.exit(
                'ERROR: Instance is {} please make sure this instance is active.'
                    .format(instance.state['Name'])
            )

        # Validate successful shutdown if it is running or stopping
        if instance.state['Code'] is 16:
            ##instance.stop()
            print "Ready for snapshot taking ..."

        # Set the max_attempts for this waiter (default 40)
        #waiter_instance_stopped.config.max_attempts = 80

        #try:
        #    waiter_instance_stopped.wait(
        #        InstanceIds=[
        #            instance_id,
        #        ]
        #    )
        # except botocore.exceptions.WaiterError as e:
        #    sys.exit('ERROR: {}'.format(e))

        """ Step 2: Take snapshot of volume """
        print('---Create snapshot of volume ({})'.format(volume.id))
        snapshot = ec2.create_snapshot(
            VolumeId=volume.id,
            Description='Snapshot of volume ({})'.format(volume.id),
        )

        waiter_snapshot_complete.config.max_attempts = 1000

        try:
            waiter_snapshot_complete.wait(
                SnapshotIds=[
                    snapshot.id,
                ]
            )
        except botocore.exceptions.WaiterError as e:
            snapshot.delete()
            sys.exit('ERROR: {}'.format(e))

        """ Step 3: Create encrypted copy snapshot """
        print('---Create encrypted copy of snapshot')
        if customer_master_key:
            # Use custom key
            snapshot_encrypted_dict = snapshot.copy(
                SourceRegion=args.region,
                Description='Encrypted copy of snapshot #{}'
                    .format(snapshot.id),
                KmsKeyId=customer_master_key,
                Encrypted=True,
                    )
        else:
            print "Default KMS  can not be used to share AMI cross account"
            sys.exit(1)
            # Use default key
            #snapshot_encrypted_dict = snapshot.copy(
            #    SourceRegion=args.region,
            #    Description='Encrypted copy of snapshot ({})'
            #        .format(snapshot.id),
            #    Encrypted=True,
            #        )

        snapshot_encrypted = ec2.Snapshot(snapshot_encrypted_dict['SnapshotId'])

        try:
            waiter_snapshot_complete.wait(
                SnapshotIds=[
                    snapshot_encrypted.id,
                ],
            )
        except botocore.exceptions.WaiterError as e:
            snapshot.delete()
            snapshot_encrypted.delete()
            sys.exit('ERROR: {}'.format(e))

        ###print('---Create encrypted volume from snapshot')

        #source_snapshot = source_ec2.Snapshot(source_ami.block_device_mappings[0]['Ebs']['SnapshotId'])
        source_snapshot = snapshot_encrypted
        # Ensure the snapshot is shared with target account
        source_sharing = source_snapshot.describe_attribute(Attribute='createVolumePermission')
        if source_sharing['CreateVolumePermissions'] \
                and source_sharing['CreateVolumePermissions'][0]['UserId'] != TARGET_ACCOUNT_ID:
            print("Snapshot already shared with account, creating a copy")
        else:
             print("Sharing with target account")
             source_snapshot.modify_attribute(
                    Attribute='createVolumePermission',
                    OperationType='add',
                    UserIds=[TARGET_ACCOUNT_ID]
             )

        target_session = role_arn_to_session(
            RoleArn=ROLE_ON_TARGET_ACCOUNT,
            RoleSessionName='share-admin-temp-session'
        )
        target_ec2 = target_session.resource('ec2', region_name=TARGET_REGION)
        # A shared snapshot, owned by source account
        shared_snapshot = target_ec2.Snapshot(source_snapshot.id)

        # Ensure source snapshot is completed, cannot be copied otherwise
        if shared_snapshot.state != "completed":
            print("Shared snapshot not in completed state, got: " + shared_snapshot.state)
            exit(1)

        # Create a copy of the shared snapshot on the target account
        copy = shared_snapshot.copy(
            SourceRegion=SOURCE_REGION,
            Encrypted=True,
        )

        # Wait for the copy to complete
        copied_snapshot = target_ec2.Snapshot(copy['SnapshotId'])
        #copied_snapshot.wait_until_completed()

        waiter_snapshot_complete.config.max_attempts = 1000

        try:
            waiter_snapshot_complete.wait(
                SnapshotIds=[
                    copied_snapshot.snapshot_id,
                ]
            )
        except botocore.exceptions.WaiterError as e:
            copied_snapshot.delete()
            sys.exit('ERROR: {}'.format(e))

        device_snap[current_volume_data['DeviceName']]=copied_snapshot.snapshot_id
        print("Created target-owned copy of shared snapshot with id: " + copy['SnapshotId'])

    ##Build Block Device Mapping - BDM
    #volsnap={"vol1":"snap1aa","vol2":"snap2aa"}

    for key  in device_snap:
        for map in all_sub_mappings:
            if map['DeviceName']== key:
              map["Ebs"]["SnapshotId"]= device_snap[key]

    pp.pprint(all_sub_mappings)

    #print block_device_mappings

    new_image = target_ec2.register_image(
        Name='copy-' + copied_snapshot.snapshot_id,
        Architecture='x86_64',
        RootDeviceName='/dev/sda1',
        BlockDeviceMappings=all_sub_mappings,
        VirtualizationType='hvm'
    )

    print("New AMI created: " + str(new_image))







##for bdm in volume_data:
    ##    # Modify instance attributes
    ##    instance.modify_attribute(
    ##        BlockDeviceMappings=[
    ##            {
    ##                'DeviceName': bdm['DeviceName'],
    ##                'Ebs': {
    ##                    'DeleteOnTermination':
    ##                        bdm['DeleteOnTermination'],
    ##                },
    ##            },
    ##       ],
    ##    )
    """ Step 7: Clean up """
    print('---Clean up resources')
    for cleanup in volume_data:
        print('---Remove snapshot {}'.format(cleanup['snapshot'].id))
        cleanup['snapshot'].delete()
        print('---Remove encrypted snapshot {}'.format(cleanup['snapshot_encrypted'].id))
        cleanup['snapshot_encrypted'].delete()
        ##print('---Remove original volume {}'.format(cleanup['volume'].id))
        ##cleanup['volume'].delete()

    print('Encryption finished')











if __name__ == "__main__":
    main(sys.argv[1:])