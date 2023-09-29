#!/usr/bin/env python

"""
Description: Create grant for KMS. Run this in each target account where
you want to give access to source encrypted AMI.

Input info in lines 22 & 24
"""

import boto3


def create_grant():

    """
    Create grant for to use KMS for cross-accounts
    """
    kms_client = boto3.client('kms')
    account_no = boto3.client('sts').get_caller_identity()['Account']
    region = boto3.client('ssm').meta.region_name
    print("Giving grants to account no: ", account_no)
    if region == 'us-east-1':
        key_id = 'arn:aws:kms:us-east-1:{source-account-number-goes-here}:key/source-key-id-goes-here'
    if region == 'us-west-2':
        key_id = 'arn:aws:kms:us-west-2:{source-account-number-goes-here}:key/source-key-id-goes-here'
    print("The region is: ", region)
    print("Creating grant with key_id: ", key_id)
    grantee_principal = 'arn:aws:iam::'+account_no+':role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling'
    operation = ['CreateGrant', 'GenerateDataKey', 'RetireGrant', 'Encrypt', \
                'ReEncryptTo', 'Decrypt', 'GenerateDataKeyWithoutPlaintext', \
                'DescribeKey', 'Verify', 'ReEncryptFrom', 'Sign']

    response = kms_client.create_grant(
        KeyId=key_id,
        GranteePrincipal=grantee_principal,
        Operations=operation
    )
    return response


def main():
    print(create_grant())


if __name__ == '__main__':
    main()
