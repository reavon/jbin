# Quality of life scripts

```shell
git clone git@gitlab.com:reavon/bin.git ~/.bin
```

## `awsinfo`

Prerequisite: `python3`, `boto3`

Returns account number, region, account alias

## `decode-message`

Prerequisite: `awscli`, `jq`

Use when Amazon gives you an _"Encoded authorization failure message"_ and you need to turn it into something readable.

## `latest-python`

Prerequisite: `pyenv`

Downloads, compiles and installs the latest python and sets global python version to use.

## `smartcard`

`99999` stands in for your PIV PIN
 
* `pip install cryptography PyKCS11`
* `python smartcard certs 999999`

By inspection, choose which certificate to export. Then, run it again to export the certificate you wanted:

`python smartcard.py openssh 999999 --cert 0`
