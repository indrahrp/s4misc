import boto3
import sys
import logging
import datetime
import argparse


logger = logging.getLogger("FT_AMI_BACKUP")
logger.setLevel(logging.INFO)
signature = "__bkp__"
backup_tag = "backup"
instance_list = []
old_images_list = []
snapshot_descriptions = []
snapshots_to_delete = []
dict = {}
#instanceid=''

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


current_datetime = datetime.datetime.now()
delete_datetime = datetime.datetime.now() + datetime.timedelta(days=7)  # Edit days to change backup retention period
date_hour_stamp = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
date_only_stamp = current_datetime.strftime("%Y-%m-%d")
delete_datetime_stamp = delete_datetime.strftime("%Y-%m-%d")

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
vpc = ec2.Vpc("vpc-06e54b8f9eccf7067")

if ec2 is None:
    print("I could not connect to AWS with the specified credentials")  # Tell me if you can't connect


# Searching and printing instances with tag "backup"

# Getting all the snapshots ids associated with the ami ids.
# I'm doing this because I want to delete the associated snapshot when I deregister an AMI image

def get_snapshots():
    aws_id = iam.get_user()['User']['Arn'].split(':')[4]
    snapshot_response = client.describe_snapshots(OwnerIds=aws_id)

    # if image id matches any of the entries in the snapshot description --> scheduled to be deleted
    for snap in snapshot_response['Snapshots']:
        # print(snap['Description'])
        # print(old_images_list)
        for image in old_images_list:
            if image.id in snap['Description']:
                snapshots_to_delete.append(snap['SnapshotId'])

    # print('\n\nHere is the snap list {}\n'.format(snapshots_to_delete))
    print('\nThe following snapshots will be deleted:')
    for snap in snapshots_to_delete:
        print('\t * {}'.format(snap))


# Given the list provided by get_instances() I'm creating AMIs for the list of instances
def create_ami(key):
    print(BColors.OKGREEN + '\nCreating AMI for instance ' + key  + BColors.ENDC)
    ami_name = 'AMIbackup_' + key + signature + date_hour_stamp + '__' + delete_datetime_stamp
    print("\t * Creating AMI of {}...".format(key))
    ami_id = client.create_image(
        Name=ami_name,
        InstanceId=key,
        Description='Taken at {} - from {}'.format(date_hour_stamp, key))
    #print('\n')


# Going through the AMIs and find the ones ready to be deregistered
def find_images_to_deregister():
    my_images = list(ec2.images.filter(
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    'DW_*',
                ]}]).all())

    if len(my_images) is 0:
        print("Did not find any AMI images with DW_* name")
    else:
        print(BColors.OKGREEN + "Checking for images/snapshots due to be deleted...\n" + BColors.ENDC)
    for image in my_images:
        if date_only_stamp == image.name[-10:]:  # Checking if last 10 characters (deregister date) matched today's date
            old_images_list.append(image)        # I'm creating a list with ami id's to be deregistered

    if len(old_images_list) is 0:
        print("\t * No images scheduled for deletion today")
    else:
        print("The following instances will be deleted:\n")
        for image_id in old_images_list:
            print('\t * ' + str(image_id.id) + ' -->  ' + str(image_id.name))


# Function to deregister images
def deregister_images():
    if len(old_images_list) is 0:
        sys.exit()
    else:
        print(BColors.OKGREEN + "\nDe-registering AMIs:\n" + BColors.ENDC)
    for image in old_images_list:
        image.deregister()
        print("\t * de-registered {}".format(image.id))

# Function to delete snaps
def delete_snapshots():
    if len(snapshots_to_delete) is 0:
        sys.exit()
    else:
        for snapshot in snapshots_to_delete:
            client.delete_snapshot(SnapshotId=snapshot)
            # print('\Just deleted: {}'.format(snapshot))




def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--instance_id',
                        help='Instance_id of ec2 for AMI backup', required=True)

    # parse args
    args = parser.parse_args()
    instanceid = args.instance_id

    # Start
    #get_instances()
    #for key in dict:
    create_ami(instanceid)
    #find_images_to_deregister()
    #deregister_images()
    #get_snapshots()
    #delete_snapshots()


if __name__ == '__main__':
    main()

