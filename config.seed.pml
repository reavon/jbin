# put this in ~/.aws/config
# aws sso login --profile aws-sso

[profile aws-sso]
sso_start_url = https://d-90679b857f.awsapps.com/start
sso_region = us-east-1
sso_account_id = 480914844964
sso_role_name = AdministratorAccess
region = us-east-1
output = json
