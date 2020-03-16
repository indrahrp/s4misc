##############
import boto3
import random
import time
import sys
import argparse
import uuid
import json
import os
import datetime
import pprint
import operator
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import pytz

utc=pytz.UTC
rootaccount="011825642366"
#sc_client = boto3.client('servicecatalog', region_name='us-east-1')
iam_client = boto3.client('iam', region_name='us-east-1')
session_client = boto3.client('sts')
# import_portfolios = ['port-rx4vc3kthfxfw']
# linux_portfolio_id = 'port-rx4vc3kthfxfw'
application_name = 'Linux Application'
linux_portfolio = 'Linux Portfolio'

#ec2vpcrole=json.dumps({"RoleArn" : "arn:aws:iam:::role/SCEC2LaunchRole"})


date=datetime.datetime.now().strftime('%m%d%Y')
account_id = boto3.client('sts').get_caller_identity()['Account']
print(("Your account id is: " +account_id))


def main():

    parser = argparse.ArgumentParser()
    #parser.add_argument('--checking_provision_io', type=str, required=False,
    #                    help='--checking_provision_io.')
    parser.add_argument('--checking_provision_disk',required=False,
                    help='--checking_provision_disk  io1 or gp2 or st1 or sc1 , check for any provision io type usage')
    parser.add_argument('--available',action="store_true",required=False,default=False,
                        help='--checking_provision_disk  io1 or gp2 or st1 or sc1 --available, check for any provision io type usage with status AVAILABLE ')
    parser.add_argument('--check_instance_type',required=False,
                        help='--check_instance_type All, standard or spot , check whether standard, spot or reserved instances, default is All')
    parser.add_argument('--ami_snap',action="store_true", default=False,required=False,
                        help='--ami_snap  ,  used with --list_snapshot All to list Snapshot used by AMI')
    parser.add_argument('--unencrypted',action="store_true", default=False,required=False,
                    help='--unencrypted  ,  used with --list_snapshot All to list unencrypt Snapshot')

    parser.add_argument('--list_ami',required=False, help='--list_ami All ,  list AMI  default is All accounts')
    parser.add_argument('--list_rds',required=False,
                        help='--list_rds All ,  check whether standard, spot or reserved instances, default is All')
    parser.add_argument('--list_snapshot',required=False,
                        help='--list_snapshot All ,  list snapshot, default is All accounts')
    parser.add_argument('--encr_unencrypted_snap',required=False,action="store_true",default=False,
                        help='--encr_unencrypted_snap  ,  encrypt unecrypte snapshot and delete unncrypted ones after')




    args = parser.parse_args()

    if args.checking_provision_disk:
        checking_provision_disk(args.checking_provision_disk,args.available)
    if args.check_instance_type:
        check_instance_type(args.check_instance_type)
    if args.list_rds:
        list_rds(args.list_rds)
    if args.list_snapshot:
        list_snapshot(args.list_snapshot,args.ami_snap,args.unencrypted)
    if args.list_ami:
        list_ami(args.list_ami)
    if args.encr_unencrypted_snap:
        encr_unencrypted_snap()



def get_aws_account_id(session):
    sts = session.client('sts')
    user_arn = sts.get_caller_identity()["Arn"]
    return user_arn.split(":")[4]


def getsessionv2(acc):
    print ("\n\n========================================")
    #print "account id " + acc['Id']
    #print "account name " + acc['Name']
    #print "========================================="
    cred = role_to_session(acc)
    credentials = cred['Credentials']


    sess= boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])

    return sess


class Account_Session:
    SESS_DICT={}
    ACCLIST=[]
    ROOT='011825642366'

    @staticmethod
    def initialize():
        print("Initializing Session to All Subaccounts .. It will take about 2 minutes")
        sess=boto3.session.Session()
        currentacc=get_aws_account_id(sess)
        if currentacc != Account_Session.ROOT:
            print("The session need to start from root account")
            exit(1)
        client = boto3.client('organizations')
        counter=0
        acclistall=[ account  for account in paginate(client.list_accounts)]
        #acclist=acclistall[0:20]
        acclist=acclistall[0:(len(acclistall)-1)]

        step=5
        batchno=0
        print "Running batch of  Batch of " + str(step)
        for cnt in range((len(acclist)/step) + 1):
            batchno += 1
            print "====== Running Batch No : " + str(batchno) + " =============="
            pool = ThreadPool(step + 2)
            var=[ v for v in  acclist[(step * cnt):((step*cnt)+step)]  ]
            results = pool.map(Account_Session.__create_sess,var)
            pool.close()
            pool.join()
            for r in results:
                print "result " + str(r)
        return
    @staticmethod
    def __create_sess(account):
        print("initializing session to account " + account['Id'])
        if not account['Id'] == Account_Session.ROOT:
            ses=getsessionv2(account['Id'])
        else:
            ses=boto3.session.Session()
        #Account_Session.SESS_LIST.append([ses,account[id],account['Name']])
        Account_Session.SESS_DICT.update({account['Id']:{'session':ses,'name':account['Name']}})
        #if counter > 10:

    @staticmethod
    def build_sess_subaccount(subaccount=None):
        #if not subaccount:
        #    Account_Session.initialize()
        #    return
        accountdict={}
        client = boto3.client('organizations')
        for account in paginate(client.list_accounts):
            accountdict.update({account['Id']:account['Name']})
        print('creating session for account ' + subaccount)

        ses=getsessionv2(subaccount)
        Account_Session.SESS_DICT.update({subaccount:{'session':ses,'name':accountdict[subaccount]}})
        return

    @staticmethod
    def get_account_list():
        Account_Session.ACCLIST=[]
        print("Gather Sema4 Account List ...")
        sess=boto3.session.Session()
        currentacc=get_aws_account_id(sess)
        if currentacc != Account_Session.ROOT:
            print("The session need to start from root account")
            exit(1)
        client = boto3.client('organizations')
        for account in paginate(client.list_accounts):
            Account_Session.ACCLIST.append(account['Id'])
        return Account_Session.ACCLIST



def role_to_session(accountid):
    #print "account id " + accountid
    sts_client = boto3.client('sts')
    rolearn="arn:aws:iam::" + accountid + ":role/OrganizationAccountAccessRole"
    assumedRoleObject = sts_client.assume_role(
        #RoleArn="arn:aws:iam::011825642366:role/OrganizationAccountAccess",

        #RoleArn="arn:aws:iam::417302553802:role/OrganizationAccountAccessRole",
        RoleArn=rolearn,
        RoleSessionName="organizational-su"
    )
    return assumedRoleObject

def getsession(acc):
    print("\n\n========================================")
    print("account id " + acc['Id'])
    print("account name " + acc['Name'])
    print("========================================")
    cred = role_to_session(acc['Id'])
    credentials = cred['Credentials']


    sess= boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])

    return sess



def paginate(method, **kwargs):
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result



def encr_unencrypted_snap(subaccount='All',ami_snap=False,unencrypted=False):
    print("################Encrypting Unencrypted Snapshot ################")
    total_account_sub_dict={}
    Account_Session.initialize()
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print('\n\n\n====================Finding Snapshoton account : ' + account + ' ' + sessinfo['name'] + ' ============================\n\n\n')
            # Define the connection
            ec2 = sessinfo['session'].resource('ec2', region_name="us-east-1")
            ec2_client = sessinfo['session'].client('ec2', region_name="us-east-1")

            # Find all volumes
            maxsize=101
            resp=ec2.snapshots.filter(OwnerIds=['self'])


            for snapshot in resp:
                try:
                    if not snapshot.encrypted:
                        print "Finding unencrypted snapshot max size " + str(maxsize)
                        print(("snapshotid,{},start_time,{},state,{},volume_id,{},owner_id,{},encrypted,{},volumesize,{},description,{} ".
                            format(snapshot.id,str(snapshot.start_time),snapshot.state,snapshot.volume_id,snapshot.owner_id,str(snapshot.encrypted),
                                   str(snapshot.volume_size),snapshot.description)))
                        if 'Create' not in snapshot.description and 'Ami' not in snapshot.description and snapshot.volume_size < maxsize:
                                print "Encrypting this now ..."
                                snapshot_encrypted = snapshot.copy(
                                    SourceRegion='us-east-1',
                                    Description='Encrypted of snapshot {} {} '.format(snapshot.id,snapshot.description),
                                    #KmsKeyId=customer_master_key,
                                    Encrypted=True
                                )
                                encsnap=ec2.Snapshot(snapshot_encrypted['SnapshotId'])
                                waiter_snapshot_complete.wait(
                                    SnapshotIds=[
                                        encsnap.id,
                                    ]
                                )
                                print "encrypting by copying  snapshot  completed at  " + str(datetime.datetime.now())


                                #print "encrypted at the source of volume " + volume.id +  "  completed at  " + str(datetime.datetime.now())

                                if encsnap.state == 'completed' and encsnap.encrypted:
                                                    print "deleting unencrypted snapshot " + snapshot.id
                                                    ans=raw_input(" hit return to delete \n")
                                                    snapshot.delete()
                        else:
                            print "snapshot " + snapshot.id + " is used for AMI or size above " + maxsize
                except Exception as err :
                    if 'InvalidSnapshot.InUse' in err.message:
                        print "skipping this snapshot. It is used by ami"
                        continue
    except Exception as err :
            print(("Encrypting Unencrypted Snapshot  error " + str(err)))
            raise


def checking_provision_disk(iotype, available=False):
    print("################Checking EBS Provision IO allocation ################")
    Account_Session.initialize()
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print('\n\n\n====================Finding EBS provision Volume on account : ' + account + ' ============================\n\n\n')



             # Define the connection
            ec2 = sessinfo['session'].resource('ec2', region_name="us-east-1")

            # Find all volumes
            volumes = ec2.volumes.all()

              # Loop through all volumes and pass it to ec2.Volume('xxx')
            for vol in volumes:
                iv = ec2.Volume(str(vol.id))

                if iv.volume_type==iotype:

                    if available:

                        if iv.state=='available':
                            #print "Getting Disk Type : " + iotype + " With 'available' State"

                            print("Created," + str(iv.create_time) + " , AZ,"  + str(iv.availability_zone) +",VolumeID," + str(iv.volume_id) + ", VolumeType," + str(iv.volume_type) + ",State," + str(iv.state)  + ",Size," +  str(iv.size) + ",IOPS," + str(iv.iops) + " , IsEncrypted," + str(iv.encrypted)  + ",SnapshotID," + str(iv.snapshot_id) + ",kms_key_id," +  str(iv.kms_key_id))


                            # The following next 2 print statements variables apply only in my case.
                            #print ",InstanceID(" + str(iv.attachments[0]['InstanceId']) + "),InstanceVolumeState(" + str(iv.attachments[0]['State']) + "),DeleteOnTerminationProtection(" + str(iv.attachments[0]['DeleteOnTermination']) + "),Device(" + str(iv.attachments[0]['Device']) + ")",
                            if iv.attachments:
                                #print "iv attaccments " + str(iv.attachments[0])
                                print(",InstanceID : " + str(iv.attachments[0].get('InstanceId','NA')))
                                #_list_product_local_or_imported(sessinfo['session'])
                    else:
                        #print "Getting Disk Type : " + iotype + " With Any State"
                        #print "Created(" + str(iv.create_time) + "),AZ(" + str(iv.availability_zone) + "),VolumeID(" + str(iv.volume_id) + "),VolumeType(" + str(iv.volume_type) + "),State(" + str(iv.state) + "),Size(" + str(iv.size) + "),IOPS(" + str(iv.iops) + "),IsEncrypted(" + str(iv.encrypted) + "),SnapshotID(" + str(iv.snapshot_id) + "),KMS_KEYID(" + str(iv.kms_key_id) + ")\n",

                        print("Created," + str(iv.create_time) + " , AZ,"  + str(iv.availability_zone) +",VolumeID," + str(iv.volume_id) + ", VolumeType," + str(iv.volume_type) + ",State," + str(iv.state)  + ",Size," +  str(iv.size) + ",IOPS," + str(iv.iops) + " , IsEncrypted," + str(iv.encrypted)  + ",SnapshotID," + str(iv.snapshot_id) + ",kms_key_id," +  str(iv.kms_key_id))

                        if iv.attachments:
                                #print "iv attaccments " + str(iv.attachments[0])
                                print(",InstanceID , " + str(iv.attachments[0].get('InstanceId','NA')))
                                #_list_product_local_or_imported(sessinfo['session'])

    except Exception as err :
        print(("Finding EBS Provision Volume  " + str(err)))



def list_rds(type='All',unencrypted=False):
    print("################Listing RDS ################")
    Account_Session.initialize()
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print('\n\n\n====================Finding EBS provision Volume on account : ' + account + ' ============================\n\n\n')
            # Define the connection
            rdsc = sessinfo['session'].client('rds', region_name="us-east-1")

            # Find all volumes
            if type == 'All':
                resp=rdsc.describe_db_instances()
                dbiter=resp['DBInstances']
                #print str(dbiter)
                for db in dbiter:
                    if unencrypted:
                        if not db['StorageEncrypted']:
                            print(("DBInstanceId,{}, DBInstanceClass,{}, Engine,{}, DBName,{},Endpoint,{},DBInstanceStatus,{},AllocatedStorage,{},InstanceCreateTime,{},MultiAZ,{},LicenseMode,{},Iops,"
                                   "{},PubliclyAccessible,{},StorageType,{},Encrypted,{},DeletionProtection,{}".format(db['DBInstanceIdentifier'],db['DBInstanceClass'],db['Engine'],db.get('DBName','NA'),
                                   db['Endpoint']['Address'],db['DBInstanceStatus'],str(db['AllocatedStorage']),str(db['InstanceCreateTime']),db['MultiAZ'],db['LicenseModel'],str(db.get('Iops','NA')),
                                   str(db['PubliclyAccessible']),db['StorageType'],str(db['StorageEncrypted']),str(db.get('DeletionProtection','NA')))))




    except Exception as err :
        print(("List RDS   " + str(err)))
        raise

def list_snapshot(subaccount='All',ami_snap=False,unencrypted=False,age=120):
    print("################Listing Snapshot ################")
    total_account_sub_dict={}
    Account_Session.initialize()
    datebef=datetime.datetime.now() - datetime.timedelta(days=age)
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print('\n\n\n====================Finding Snapshoton account : ' + account + ' ' + sessinfo['name'] + ' ============================\n\n\n')
            # Define the connection
            ec2 = sessinfo['session'].resource('ec2', region_name="us-east-1")

            # Find all volumes
            if subaccount == 'All':
                total_size_sub=0
                resp=ec2.snapshots.filter(OwnerIds=['self'])
                for snapshot in resp:
                    if  snapshot.start_time < utc.localize(datebef):
                        if ami_snap:
                            if 'Create'  in snapshot.description or 'Ami' in snapshot.description:
                                total_size_sub += snapshot.volume_size
                                print "Finding snaphost with for AMI creation"
                                total_size_sub += total_size_sub
                                print(("snapshotid,{},start_time,{},state,{},volume_id,{},owner_id,{},encrypted,{},volumesize,{},description,{} ".
                                format(snapshot.id,str(snapshot.start_time),snapshot.state,snapshot.volume_id,snapshot.owner_id,str(snapshot.encrypted),
                                       str(snapshot.volume_size),snapshot.description)))
                        elif unencrypted:
                            if not snapshot.encrypted:
                                total_size_sub += snapshot.volume_size
                                print "Finding unencrypted snapshot"
                                print(("snapshotid,{},start_time,{},state,{},volume_id,{},owner_id,{},encrypted,{},volumesize,{},description,{} ".
                                    format(snapshot.id,str(snapshot.start_time),snapshot.state,snapshot.volume_id,snapshot.owner_id,str(snapshot.encrypted),
                                           str(snapshot.volume_size),snapshot.description)))
                        else:
                            total_size_sub += snapshot.volume_size
                            print(("snapshotid,{},start_time,{},state,{},volume_id,{},owner_id,{},encrypted,{},volumesize,{},description,{} ".
                            format(snapshot.id,str(snapshot.start_time),snapshot.state,snapshot.volume_id,snapshot.owner_id,str(snapshot.encrypted),
                                   str(snapshot.volume_size),snapshot.description)))
                total_account_sub_dict.update({sessinfo['name']:total_size_sub})


            print('Total account : ' + account + ' ' + sessinfo['name'] + ' Snapshot Size ' + str(total_account_sub_dict[sessinfo['name']]) )


    except Exception as err :
        print(("List Snapshot  " + str(err)))
        raise

def list_ami(subaccount='All'):
    print("################Listing AMI ################")
    total_account_sub_dict={}
    Account_Session.initialize()
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print('\n\n\n====================Finding AMI account : ' + account + ' ============================\n\n\n')
            # Define the connection
            ec2 = sessinfo['session'].client('ec2', region_name="us-east-1")

            # Find all volumes
            if subaccount == 'All':
                #total_size_sub=0
                resp = ec2.describe_images(Owners=['self'])
                for image in resp['Images']:
                    #total_size_sub += total_size_sub
                    #print str(image)
                    print(("CreationDate,{},ImageId,{},ImageLocation,{},ImageType,{},Public,{},OwnerId,{},State,{},BlockDeviceMappings,{},Description,{},Name,{} ".
                        format(image['CreationDate'],image['ImageId'],image['ImageLocation'],image['ImageType'],image['Public'],image['OwnerId'],image['State'],str(image['BlockDeviceMappings']),image.get('Description','NA'),image['Name'])))

                #total_account_sub_dict.update({sessinfo['Name']:total_size_sub})

    except Exception as err :
        print(("List Snapshot  " + str(err)))
        raise


def delete_snapshot(subaccount,description,day='14'):
    print(("################Deleting Snapshot older than {}################".format(days)))
    Account_Session.initialize()
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print('\n\n\n====================Finding Snapshoton account : ' + account + ' ============================\n\n\n')
            # Define the connection
            ec2 = sessinfo['session'].resource('ec2', region_name="us-east-1")

            # Find all volumes
            if  account==subaccount:
                resp=ec2.snapshots.filter(OwnerIds=['self'])
                for snapshot in resp:
                    start_time=snapshot.start_time
                    delete_time=datetime.now - datetime.timedelta(days=day)
                    if delete_time > start_time:
                        print(("snapshotid,{},start_time,{},state,{},volume_id,{},owner_id,{},encrypted,{},volumesize,{},description,{} ".
                            format(snapshot.id,str(snapshot.start_time),snapshot.state,snapshot.volume_id,snapshot.owner_id,str(snapshot.encrypted),
                                   str(snapshot.volume_size),snapshot.description)))



    except Exception as err :
        print(("List Snapshot  " + str(err)))
        raise







def check_instance_type(type='All'):


    print("################Checking EBS Provision IO allocation ################")
    Account_Session.initialize()
    try:
        for account,sessinfo in Account_Session.SESS_DICT.items():
            print('\n\n\n====================Checking Instances  on account : ' + account + ' ============================\n\n\n')



            # Define the connection
            ec2 = sessinfo['session'].resource('ec2', region_name="us-east-1")

            response = ec2.instances.all()
            #print str(response)
            for inst in  response:
                #print "addr " + str(addr)
                #print "Public IP : " + addr['PublicIp']
                #print("Public IP : " + addr['PublicIP'])
                if type == 'kpi':
                    f = open("ec2","w+")
                    print("generating kpi report ")
                    print(("Instance ID, {}, Instance Type, {}  , State, {}, Spot_Insta_Req_Id, {},state_reason , {},capacity_reservation_id , {}".format( inst.instance_id,inst.instance_type,inst.state,inst.spot_instance_request_id,inst.state_reason,inst.capacity_reservation_id)))
                    #f.write("Instance ID, {}, Instance Type, {}  , State, {}, Spot_Insta_Req_Id, {},state_reason , {},capacity_reservation_id , {} \n" (% inst.instance_id,inst.instance_type,inst.state,inst.spot_instance_request_id,inst.state_reason,inst.capacity_reservation_id))
                    f.write("Instance ID,  inst.instance_id, Instance Type, inst.instance_type  , State, inst.state, Spot_Insta_Req_Id, inst.spot_instance_request_id,state_reason , inst.state_reason,capacity_reservation_id , inst.capacity_reservation_id \n" )


                elif type == 'spot':
                    if inst.spot_instance_request_id:
                      print(("Instance ID, {}, Instance Type, {}  , State, {}, Spot_Insta_Req_Id, {},state_reason , {},capacity_reservation_id , {}".format( inst.instance_id,inst.instance_type,inst.state,inst.spot_instance_request_id,inst.state_reason,inst.capacity_reservation_id)))
                elif type == 'standard':
                    if not inst.spot_instance_request_id:
                        print(("Instance ID, {}, Instance Type, {}  , State, {}, Spot_Insta_Req_Id, {},state_reason , {},capacity_reservation_id , {}".format( inst.instance_id,inst.instance_type,inst.state,inst.spot_instance_request_id,inst.state_reason,inst.capacity_reservation_id)))
                else:
                    print(("Instance ID, {}, Instance Type, {}  , State, {}, Spot_Insta_Req_Id, {},state_reason , {},capacity_reservation_id , {}".format( inst.instance_id,inst.instance_type,inst.state,inst.spot_instance_request_id,inst.state_reason,inst.capacity_reservation_id)))
        if type == 'kpi':
            s3key='temp/' + 'ec2'
            upload_file(s3key,date,f.name)
            f.close()


    except Exception as errp:
        print(("Error getting" + str(errp)))
        raise

def testup():
    print("intestup")
    s3key='temp/' + 'ec2'
    date=datetime.datetime.now().strftime('%m%d%Y')
    fileloc='testfile'
    upload_file(s3key,date,fileloc)


def upload_file(s3key,fileloc,bucket='s4-it-cf-bucket'):
    bucket_account='006775277657'
    Account_Session.build_sess_subaccount(bucket_account)
    try:
        s3=Account_Session.SESS_DICT[bucket_account]['session'].client('s3')
        s3keyobj = s3key + "/" + date
        print("s3keyobj " + s3keyobj)
        print("uploading to s3 ")
        s3.upload_file( fileloc,bucket,s3keyobj)
    except Exception as err:
        print(("errro ", str(err)))






if __name__ == '__main__':
    #testup()
    main()
