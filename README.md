# iamutils
AWSIAM_RolesToPolicyCSV.py consumes the output of the AWS GetAccountAuthorizationDetails (https://aws.amazon.com/blogs/security/a-simple-way-to-export-your-iam-settings/) call to produce a CSV listing all the 
roles, associated permissions, conditions, and all inline or attached policies and their details.

The output produced has data in this format:
RoleName,AssumedRoleEffect,AssumedRoleAction,AssumedRoleCondition,AssumedRolePrincipal,PolicyType,PolicyName,PolicyEffect,PolicyAction,PolicyCondition,PolicyResource
