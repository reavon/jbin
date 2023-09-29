#!/usr/bin/env python

# Description: Remove Unattached Volumes > 30 days
# Author: Tracy Phillips
# Last Updated: Nov 18th, 2022


from datetime import datetime, timedelta
import boto3


ec2 = boto3.client('ec2')
filters = [
    {
        'Name': 'status', 'Values': ['available']
    }
]
response = ec2.describe_volumes(Filters=filters)


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown Type")


def remove_unattached_volumes():
    timethreshhold = datetime_handler(datetime.now() - timedelta(days=30))
    unattached_volumes = []
    for volitem in response['Volumes']:
        volume_id = volitem['VolumeId']
        volume_date = datetime_handler(volitem['CreateTime'])
        try:
            if volume_date < timethreshhold:
                unattached_volumes.append(volume_id)
                ec2.delete_volume(VolumeId=volume_id)
            else:
                pass

        except Exception as e:
            print(e)
            pass


def main():
    remove_unattached_volumes()


if __name__ == '__main__':
    main()
