# Script to associate Network hub vpc with member account r53

import re
import sys
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

CONFIG = Config(
    retries={
        'mode': 'standard'
    }
)

NETWORKHUB_ACCOUNT_ID = '331062757678'
NETWORKHUB_VPC_ID = 'vpc-0d9108b823cc1a447'
assumed_role_name = 'maps-rrAssumeNetwork'
member_assume_role = 'maps-rrAssumeMember'


def assume_role(member_account_id, role_name, region='us-west-2',
                service='NOT SPECIFIED'):
    # Beginning the assume role process for account
    role_session_name = 'networkhub'
    sts_client = boto3.client('sts', config=CONFIG)

    # Get the current partition
    try:
        partition = sts_client.get_caller_identity()['Arn'].split(":")[1]
    except ClientError as e:
        print('Failed to get caller identity: {}'.format(
            e.response['Error']['Message']))
        sys.exit()
    try:
        r = sts_client.assume_role(
            RoleArn='arn:{}:iam::{}:role/{}'.format(
                partition,
                member_account_id,
                role_name
            ),
            RoleSessionName=role_session_name
        )

        # Storing STS credentials
        session = boto3.Session(
            aws_access_key_id=r['Credentials']['AccessKeyId'],
            aws_secret_access_key=r['Credentials']['SecretAccessKey'],
            aws_session_token=r['Credentials']['SessionToken'],
            region_name=region
        )

        print("Created session for account id {}, region {}, service {}".format(
            member_account_id,
            region,
            service
        ))

        return session
    except ClientError as e:
        print(
            'Failed to create session and assume role for account id {}, '
            'region {}, service {}: {}'.format(
                member_account_id,
                region,
                service,
                e.response['Error']['Message']
            ))
        sys.exit()


def get_all_org_accounts(client):
    '''
    Retrieve all the accounts under AWS organization
    :param client: Boto3 Organization client
    :return: List of account IDs and account details
    '''
    print("Get all the AWS accounts under Organization")
    org_accounts = []
    ignore_account = ["-rr-", "-networking-", "management", "LogArchive",
                      "Audit", "-prod-", "-poc-"]

    try:
        paginator = client.get_paginator('list_accounts')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for i in page['Accounts']:
                if not any(account in i['Name'] for account in ignore_account):
                    org_accounts.append(i['Id'])
        return org_accounts
    except ClientError as error:
        print('Error getting all account under the organization: {}'.format(
            error))


def create_client(session, service_name):
    try:
        print('Creating Boto3 client for the service - {}'.format(service_name))
        client = session.client(service_name)
        return client
    except Exception as e:
        print.error(
            'Failed to create Boto3 client for the service - {} : {} '.format(
                service_name, e))


def create_vpc_association_authorization(route53Client, hostedZoneId, region,
                                         main_vpc_id):
    """ Create an association authorization on the client account which
    allows the main VPC to associate with the private hosted zone. Return the
    hosted zone ID since we use it later."""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.create_vpc_association_authorization

    # Create the authorization
    print('create_vpc_association_authorization')
    args = {
        'HostedZoneId': hostedZoneId,
        'VPC': {
            'VPCRegion': region,
            'VPCId': main_vpc_id
        },
    }
    route53Client.create_vpc_association_authorization(**args)['HostedZoneId']


def associate_vpc_with_hosted_zone(serviceRoute53Client, networkRoute53Client,
                                   hostedZoneId, region, main_vpc_id):
    """ Associate the private hosted zone with the main VPC. """
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.associate_vpc_with_hosted_zone

    print('associate_vpc_with_hosted_zone')
    # Make sure the Main VPC isn't already associated.
    isMainVpcAssociated = False
    vpcs = serviceRoute53Client.get_hosted_zone(Id=hostedZoneId)['VPCs']
    for vpc in vpcs:
        isMainVpcAssociated |= (vpc['VPCId'] == main_vpc_id)

    # If the Main VPC is not associated, associate it.
    if not isMainVpcAssociated:
        # Associate the main VPC
        args = {
            'HostedZoneId': hostedZoneId,
            'VPC': {
                'VPCRegion': region,
                'VPCId': main_vpc_id
            },
        }
        networkRoute53Client.associate_vpc_with_hosted_zone(**args)[
            'ChangeInfo']


def delete_vpc_association_authorization(route53Client, hostedZoneId, region,
                                         main_vpc_id):
    """ Remove association authorizations because they build up and there is
    a max."""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.delete_vpc_association_authorization
    print('delete_vpc_association_authorization')
    args = {
        'HostedZoneId': hostedZoneId,
        'VPC': {
            'VPCRegion': region,
            'VPCId': main_vpc_id
        },
    }
    return route53Client.delete_vpc_association_authorization(**args)


# if you want to run this on all the accounts in the org uncomment the code
# org_client = boto3.client('organizations')
# accounts = get_all_org_accounts(org_client)
#
# single account run
accounts = ['354396421831']

regions = ['us-west-2', 'us-east-2', 'ca-central-1']

for account in accounts:
    for r in regions:
        member_session = assume_role(account, member_assume_role, r)

        networkhub_session = assume_role(NETWORKHUB_ACCOUNT_ID,
                                         assumed_role_name, r)

        # create Client
        member_ec2_client = create_client(member_session, 'ec2')
        member_sd_client = create_client(member_session, 'servicediscovery')
        member_r53_client = create_client(member_session, 'route53')
        networkhub_r53_client = create_client(networkhub_session, 'route53')
        networkhub_ec2_client = create_client(networkhub_session, 'ec2')
        response = member_r53_client.list_hosted_zones()
        hosted_id_list = []
        for hosted_zone in response['HostedZones']:
            hosted_id = re.search('/hostedzone/(.*)', hosted_zone['Id']).group(
                1)
            response = member_r53_client.get_hosted_zone(
                Id=hosted_id
            )
            if response['VPCs'][0]['VPCRegion'] == 'us-west-2':
                hosted_id_list.append(hosted_id)
        for h in hosted_id_list:
            print('Account Id : %s | Hosted Zones Id: %s' % (
                account, hosted_id_list))
            create_vpc_association_authorization(member_r53_client, h, r,
                                                 NETWORKHUB_VPC_ID)
            # In the network account, associate the Route53 private hosted
            # zone with the main VPC
            associate_vpc_with_hosted_zone(member_r53_client,
                                           networkhub_r53_client, h, r,
                                           NETWORKHUB_VPC_ID)
            # In the service account, delete the VPC association authorization
            delete_vpc_association_authorization(member_r53_client, h, r,
                                                 NETWORKHUB_VPC_ID)
