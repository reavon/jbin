#!/usr/bin/env python

import boto3
from pathlib import Path

session = boto3.session.Session(profile_name='mntv-management')
client = session.client('organizations')
results = (
    client.get_paginator('list_accounts').paginate().build_full_result())


def accounts() -> list:
    id_list = []
    name_list = []
    account_list = []
    for aws_account in results["Accounts"]:
        account_id = aws_account["Id"]
        account_name = aws_account["Name"]
        id_list.append(account_id)
        name_list.append(account_name)
    for i in range(len(id_list)):
        account_list.append([id_list[i], name_list[i]])
    return account_list


def aws_accounts():
    aws_account_list = []
    with open(Path('~/.aws/config').expanduser(), "w") as file:
        file.seek(0)
        file.truncate()
    for account in accounts():
        aws_account_list = """
        [profile {id}]
        sso_start_url = https://momentive.awsapps.com/start
        sso_region = us-west-2
        sso_account_id = {name}
        sso_role_name = AWSAdministratorAccess
        region = us-west-2
        output = json
        """.format(id=account[1].lower(), name=account[0]).replace("    ", "")
        with open(Path('~/.aws/config').expanduser(), "a") as file:
            file.write(aws_account_list)
            #  The 'with' block automatically takes care closing the file at the end of the block.
            #  file.close()
    return aws_account_list


def existing_aws_accounts():
    existing_accounts = """
    [profile mntv-prod]
    region = us-west-2

    [profile mntv-sandbox]
    region = eu-west-1

    [profile aws-sm-dev]
    region = us-west-2

    [profile sm-assets]
    region = us-west-2

    [profile aws-canada]
    region = ca-central-1
    """.replace("  ", "")
    with open(Path('~/.aws/config').expanduser(), "a") as file:
        file.write(existing_accounts)
    return existing_aws_accounts


def main():
    aws_accounts()
    existing_aws_accounts()


if __name__ == "__main__":
    main()
