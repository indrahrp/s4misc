#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dbsnap is a DB snapshot management tool for Amazon RDS.
Demo tool used for educational purposes in http://blog.codebender.cc/2015/12/08/automating-db-snapshots-at-amazon-rds/
"""

from __future__ import print_function

import boto3
import datetime
import time
import sys
import argparse

__version__ = '0.1.0'


class DBSnapshot(object):
    """DBSnapshot"""
    cmkid='2c9e26fc-3059-4eb3-8e82-a32813195943'
    targetkeyid='200b9779-1a4c-45c6-bdd9-b0295d5cbaee'
    snapshot_id=""
    snapcopy_enc_id=""
    snapcopy_enc_sub_id=""
    ###snapcopy_enc1_sub_id=""

    #enc_snapshot_id=""
    client=""
    db_identifier=""
    ROLE_ON_TARGET_ACCOUNT= 'arn:aws:iam::417302553802:role/shareami'
    TARGET_REGION='us-east-1'
    snap_arn=""

    @staticmethod
    def initialize(subaccount_client=None) :
        if not subaccount_client:
            DBSnapshot.client = boto3.client('rds')
        else:
            DBSnapshot.client = subaccount_client
    @staticmethod
    def create(db_instance, timestamp):
        """Creates a new DB snapshot"""
        DBSnapshot.snapshot_id = "{0}-{1}-{2}".format("mysnapshot", db_instance, timestamp)
        DBSnapshot.client.create_db_snapshot(DBSnapshotIdentifier=DBSnapshot.snapshot_id, DBInstanceIdentifier=db_instance)
        time.sleep(2)  # wait 2 seconds before status request

        waiter = DBSnapshot.client.get_waiter('db_snapshot_available')
        waiter.wait(
        DBSnapshotIdentifier=DBSnapshot.snapshot_id
        )
        #current_status = None
        #while True:
        #    current_status = DBSnapshot.__status(snapshot=DBSnapshot.snapshot_id)
        #    if current_status == 'available' or current_status == 'failed':
        #        break
        #return current_status

    @staticmethod
    def delete(self, snapshot):
        """Deletes a user-specified DB snapshot"""
        try:
            current_status = DBSnapshot.__status(snapshot=DBSnapshot.snapshot_id)
            if current_status == 'available':
                DBSnapshot.client.delete_db_snapshot(DBSnapshotIdentifier=DBSnapshot.snapshot_id)
                current_status = DBSnapshot.__status(snapshot=DBSnapshot.snapshot_id)
        except:
            current_status = 'does not exist'
        return current_status

    @staticmethod
    def list_instances():
        """Lists the available RDS instances"""
        return DBSnapshot.client.describe_db_instances()['DBInstances']

    @staticmethod
    def __status(snapshot):
        """Returns the current status of the DB snapshot"""
        return DBSnapshot.client.describe_db_snapshots(DBSnapshotIdentifier=snapshot)['DBSnapshots'][0]['Status']

    @staticmethod
    def get_snapshot_arn(snapshot_id):
        """Returns the current status of the DB snapshot"""
        print ("in get snapshot")
        dbsnapshot=DBSnapshot.client.describe_db_snapshots(
            IncludeShared=True
        )
        for dbsnap in dbsnapshot['DBSnapshots']:
                #print(dbsnap)
                #print ("SNAPID")
                print (dbsnap['DBSnapshotIdentifier'])
                if dbsnap['DBSnapshotIdentifier'] == snapshot_id:
                   # DBSnapshot.snap_arn=dbsnap['DBSnapshotArn']
                    print ('snap arn {}'.format( dbsnap['DBSnapshotArn']))
                    return dbsnap['DBSnapshotArn']

        #return DBSnapshot.client.describe_db_snapshots(DBSnapshotIdentifier=snapshot)['DBSnapshots'][0]['Status']

    @classmethod
    def copy_db_snapshot(cls,snapshot_arn, suffix, subaccount=False):
        if  not subaccount:
            enckey=cls.cmkid
        else:
            enckey=cls.targetkeyid
        print ('enckey ' + enckey)

        print('snapshot_arn ' + snapshot_arn)
        target_snapshot_id=cls.snapshot_id + suffix
        response = cls.client.copy_db_snapshot(
            SourceDBSnapshotIdentifier=snapshot_arn,
            TargetDBSnapshotIdentifier=target_snapshot_id,
            KmsKeyId=enckey,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'Enc-Copy-Snapshot'
                },
            ],

        )
        waiter = DBSnapshot.client.get_waiter('db_snapshot_available')
        waiter.wait(
            DBSnapshotIdentifier=target_snapshot_id
        )
        #cls.enc_snapshot_id = target_snapshot_id
        return target_snapshot_id


    @classmethod
    def share_db_snapshot(cls,other_subaccount):
        print ("other subaccount {} and snapshot {}".format(other_subaccount,cls.snapcopy_enc_id))
        response = cls.client.modify_db_snapshot_attribute(
            DBSnapshotIdentifier=cls.snapcopy_enc_id,
            AttributeName='restore',
            ValuesToAdd=[ other_subaccount]
        )

    @classmethod
    def restore_db_snapshot(cls,dbsubnetgroupname,dbinstanceclass,availabilityzone,dbparametergroupname,vpcsecuritygroupids):
        print ("Restore DB {} on other sub account  with snapshot {}".format(cls.db_identifier,cls.snapcopy_enc_sub_id))
        response = cls.client.restore_db_instance_from_db_snapshot(
            DBSnapshotIdentifier=cls.snapcopy_enc_sub_id,
            DBInstanceIdentifier=cls.db_identifier,
            DBInstanceClass=dbinstanceclass,
            AvailabilityZone=availabilityzone,
            DBSubnetGroupName=dbparametergroupname,
            DBParameterGroupName=dbparametergroupname,
            VpcSecurityGroupIds = vpcsecuritygroupids
        )
        print (response)


#@cli.command()
def instances():
    """Returns the available RDS instances"""
    ##dbcon = DBSnapshot()
    db_instances = DBSnapshot.list_instances()
    ##click.echo("Database Instances:")
    for instance in db_instances:
        print("\t- {0}".format(instance['DBInstanceIdentifier']))


#@cli.command()
#@click.option('--db-instance', help='Database instance')
def create(db_instance):
    """Creates a new DB snapshot"""
    if not db_instance:
        print ("Please specify a database using --db-instance option")
        return sys.exit(1)
    ##dbcon = DBSnapshot()
    date = datetime.datetime.now()
    timestamp = date.strftime("%Y-%m-%d")
    print ("Creating a new snapshot from {0} instance...".format(db_instance))
    response = DBSnapshot.create(db_instance=db_instance, timestamp=timestamp)
    #print ("Snapshot status: {0}".format(response))


#@cli.command()
#@click.option('--db-snapshot', help='Database snapshot')
def delete(db_snapshot):
    """Deletes a user-specified DB snapshot"""
    if not db_snapshot:
        click.echo("Please specify a database using --db-snapshot option", err=True)
        return sys.exit(1)
    dbcon = DBSnapshot()
    response = dbcon.delete(snapshot=db_snapshot)
    if response == 'does not exist':
        output = "Snapshot: {0} has been deleted".format(db_snapshot)
    else:
        output = "Snapshot: {0} deletion failed".format(db_snapshot)
    print (output)

##def copy_enc_db (snapshot_arn,target=False):
##    DBSnapshot.copy_db_snapshot(snapshot_arn,target)

def share_db_snapshot(other_sub_account):
    DBSnapshot.share_db_snapshot(other_sub_account)



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



def main():
    parser = argparse.ArgumentParser()


    # add args
    parser.add_argument('command',
                        type=str,
                        choices=["db-instance-list", "create-snapshot","copy-encrypt-snapshot","share-db-snapshot"])
    parser.add_argument('--db_identifier',
                        help='db_instance_identifier ',
                        type=str)
    parser.add_argument('--snapshotid', help="Copy and Encrypt of a particular  Snapshot Identifier ", action='store')
    parser.add_argument('--other_sub_account', help="Share db snapshot access to another sub acccount  ", action='store')
    parser.add_argument('--restore_sub_account', help="Restore db snapshot to another sub acccount  ", action='store_true')

    # parse args
    args = parser.parse_args()
    command = args.command

    DBSnapshot.snapshotid = args.snapshotid
    other_sub_account = args.other_sub_account
    restore_sub_account = args.restore_sub_account
    ##if args.db_identifier:
    ##    db_identifier = args.db_identifier
    ##else:
    ##   db_identifier = config.get('DEFAULT', INSTANCE_IDENTIFIER)

    # execute commands
    ##dbcon = DBSnapshot()
    DBSnapshot.initialize()
    DBSnapshot.db_identifier = args.db_identifier

    ##First snapshot
    create(DBSnapshot.db_identifier)

    ##Second encrypted Snapshot e
    snapsource_arn=DBSnapshot.get_snapshot_arn(DBSnapshot.snapshot_id)
    DBSnapshot.snapcopy_enc_id=DBSnapshot.copy_db_snapshot(snapsource_arn,"-2nd-encrypt")

    ##Sharing snapshot to another sub account
    share_db_snapshot(other_sub_account)


    ##Copy and reencrypt snapshot on the other sub account
    target_session = role_arn_to_session(
        RoleArn=DBSnapshot.ROLE_ON_TARGET_ACCOUNT,
        RoleSessionName='share-admin-temp-session'
    )
    target_rds = target_session.client('rds',region_name=DBSnapshot.TARGET_REGION)
    DBSnapshot.initialize(target_rds)

    snapsource_arn=DBSnapshot.get_snapshot_arn(DBSnapshot.snapcopy_enc_id)
    DBSnapshot.snapcopy_enc_sub_id=DBSnapshot.copy_db_snapshot(snapsource_arn,"-subaccount-encrypt",True)


    #DBSnapshot.snapshot_id=snapshotid
    #DBSnapshot.enc_snapshot_id = args.snapshotid
    #DBSnapshot.get_snapshot_arn(DBSnapshot.enc_snapshot_id)

    dbsubnetgroupname='testsg-databasesubnetgroup-11ws15wsshwf2'
    dbinstanceclass='db.t2.small'
    availabilityzone='us-east-1a'
    dbparametergroupname='default.sqlserver-se-12.0'
    vpcsecuritygroupids=['sg-001281b76fc28bd64','sg-09893714808906e32']

    if restore_sub_account:
        DBSnapshot.restore_db_snapshot(dbsubnetgroupname,dbinstanceclass,availabilityzone,dbparametergroupname,vpcsecuritygroupids)

    ###if command == 'db-instance-list':
        ##print (dbcon.list_instances())
        instances()
    #elif command == 'create-snapshot':
    #    create(DBSnapshot.db_identifier)
    #elif command == 'copy-encrypt-snapshot':
    #    DBSnapshot.snapshot_id=snapshotid
    #    copy_enc_db()
    #elif command == 'share-db-snapshot':
    #    DBSnapshot.enc_snapshot_id = snapshotid
    #    share_db_snapshot(other_sub_account)
    ##elif restore_sub_account:

       ## target_session = role_arn_to_session(
       ##     RoleArn=DBSnapshot.ROLE_ON_TARGET_ACCOUNT,
       ##     RoleSessionName='share-admin-temp-session'
       ## )
        target_rds = target_session.client('rds',region_name=DBSnapshot.TARGET_REGION)
        # A shared snapshot, owned by source account
        #shared_snapshot = target_ec2.Snapshot(source_snapshot.id)
        ##DBSnapshot.initialize(target_rds)
        ##copy_enc_db(True)
        #DBSnapshot.restore_db_snapshot(dbsubnetgroupname,dbinstanceclass,availabilityzone,dbparametergroupname,vpcsecuritygroupids)




if __name__ == '__main__':
    main()


### To test
#C:\Users\indra.harahap\PycharmProjects\s4misc>c:\Python27\python.exe rds_snapshot1.py share-db-snapshot --db_identifier testinstance --snapshotid mysnapshot-testinstance-2018-12-04copy-enc --other_sub_account 417302553802 --restore_sub_account