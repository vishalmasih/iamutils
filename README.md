# iamutils
AWSIAM_RolesToPolicyCSV.py consumes the output of the AWS GetAccountAuthorizationDetails (https://aws.amazon.com/blogs/security/a-simple-way-to-export-your-iam-settings/) call to produce a CSV listing all the 
roles, associated permissions, conditions, and all inline or attached policies and their details.

The output produced has data in this format:
RoleName,AssumedRoleEffect,AssumedRoleAction,AssumedRoleCondition,AssumedRolePrincipal,PolicyType,PolicyName,PolicyEffect,PolicyAction,PolicyCondition,PolicyResource


ELKCuratorLambda.py is a Lambda function supposed to run daily. Taking snapshots of AWS ES indicies one day before their deletion, deleting them the next day, and deleting old snapshots. These are configurable. I am passing the access key and secret key via encrypted environment variables but ideally you would want to assign your Lambda role the permissions needed, and access to your ES domain.
