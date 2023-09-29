#!/usr/bin/env python

import boto3

AWS_REGION = 'us-west-2'
session = boto3.Session(region_name=AWS_REGION)
ec2 = session.client('ec2')


def main(event, context):
    ec2_regions = [region['RegionName'] for region in
                   ec2.describe_regions()['Regions']]
    # For all AWS Regions
    for region in ec2_regions:
        conn = boto3.client('ec2', region_name=region)
        print("Checking AWS Region: " + region)
        status = conn.get_ebs_encryption_by_default()
        print("====" * 10)
        result = status["EbsEncryptionByDefault"]
        if result is True:
            print("Activated, nothing to do")
        else:
            print("Not activated, activation in progress")
            conn.enable_ebs_encryption_by_default()


if __name__ == '__main__':
    main(0, 0)
