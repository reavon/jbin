#!/usr/bin/env python

import datetime
import sys
import boto3
age = 30
aws_profile_name = 'prod'


def days_old(date):
    date_obj = date.replace(tzinfo=None)
    diff = datetime.datetime.now() - date_obj
    return diff.days

boto3.setup_default_session(profile_name = aws_profile_name)
ec2 = boto3.client('ec2')
amis = ec2.describe_snapshots(OwnerIds=[
        'self'
        ])
    # ], MaxResults=90000)
for ami in amis['Snapshots']:
    create_date = ami['StartTime']
    snapshot_id = ami['SnapshotId']
    day_old = days_old(create_date)
    if day_old > age:
        try:

            print "deleting -> " + snapshot_id + " as image is " + str(day_old)  + " old."
            # delete the snapshot
            ec2.delete_snapshot(SnapshotId=snapshot_id)
        except:
            print "can't delete " + snapshot_id
