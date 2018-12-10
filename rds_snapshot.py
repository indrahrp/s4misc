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
    snapshot_id=""
    enc_snapshot_id=""
    client=""

    @staticmethod
    def initialize() :
        DBSnapshot.client = boto3.client('rds')

    @staticmethod
    def create(db_instance, timestamp):
        """Creates a new DB snapshot"""
        DBSnapshot.snapshot_id = "{0}-{1}-{2}".format("mysnapshot", db_instance, timestamp)
        DBSnapshot.client.create_db_snapshot(DBSnapshotIdentifier=DBSnapshot.snapshot_id, DBInstanceIdentifier=db_instance)
        time.sleep(2)  # wait 2 seconds before status request
        current_status = None
        while True:
            current_status = DBSnapshot.__status(snapshot=DBSnapshot.snapshot_id)
            if current_status == 'available' or current_status == 'failed':
                break
        return current_status

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

    @classmethod
    def copy_db_snapshot(cls):
        target_snapshot_id=cls.snapshot_id + "copy-enc"
        response = cls.client.copy_db_snapshot(
            SourceDBSnapshotIdentifier=cls.snapshot_id,
            TargetDBSnapshotIdentifier=target_snapshot_id,
            KmsKeyId=cls.cmkid,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'Enc-Copy-Snapshot'
                },
            ],
            CopyTags=True,
        )
        cls.enc_snapshot_id = target_snapshot_id
    @classmethod
    def share_db_snapshot(cls,other_subaccount):
        print ("other subaccount {} and snapshot {}".format(other_subaccount,cls.enc_snapshot_id))
        response = cls.client.modify_db_snapshot_attribute(
            DBSnapshotIdentifier=cls.enc_snapshot_id,
            AttributeName='restore',
            ValuesToAdd=[ other_subaccount]
        )




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
    print ("Snapshot status: {0}".format(response))


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

def copy_enc_db ():
    DBSnapshot.copy_db_snapshot()

def share_db_snapshot(other_sub_account):
    DBSnapshot.share_db_snapshot(other_sub_account)



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
    # parse args
    args = parser.parse_args()
    command = args.command
    db_identifier = args.db_identifier
    snapshotid = args.snapshotid
    other_sub_account = args.other_sub_account
    ##if args.db_identifier:
    ##    db_identifier = args.db_identifier
    ##else:
    ##   db_identifier = config.get('DEFAULT', INSTANCE_IDENTIFIER)

    # execute commands
    ##dbcon = DBSnapshot()
    DBSnapshot.initialize()
    if command == 'db-instance-list':
        ##print (dbcon.list_instances())
        instances()
    elif command == 'create-snapshot':
        create(db_identifier)
    elif command == 'copy-encrypt-snapshot':
        DBSnapshot.snapshot_id=snapshotid
        copy_enc_db()
    elif command == 'share-db-snapshot':
        DBSnapshot.enc_snapshot_id = snapshotid

        share_db_snapshot(other_sub_account)

if __name__ == '__main__':
    main()