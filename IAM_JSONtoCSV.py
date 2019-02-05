import json
import pprint

outputfile = open("output.csv", "w")

with open('input.json') as data_file:    
    data = json.load(data_file)

# Create Policies Dictionary first
parsedpolicies = {}
for policy in data['Policies']:
    policyname = policy['PolicyName']
    #if policyname == 'AWSServiceCatalogAdminFullAccess':
    policystmtslist = []
    for policyversion in policy['PolicyVersionList']:
        if policyversion['IsDefaultVersion']:
            for polstmt in policyversion['Document']['Statement']:
                resource = polstmt['Resource']
                effect = polstmt['Effect']
                condition = ''
                if 'Condition' in polstmt:
                    condition = pprint.pformat(polstmt['Condition'])
                if type(polstmt['Action']) == str:
                    policyvars = {}
                    policyvars['Effect'] = effect
                    policyvars['Action'] = action
                    policyvars['Condition'] = condition
                    policyvars['Resource'] = resource
                    policystmtslist.append(policyvars)
                else:
                    for action in polstmt['Action']:
                        policyvars = {}
                        policyvars['Effect'] = effect
                        policyvars['Action'] = action
                        policyvars['Condition'] = condition
                        policyvars['Resource'] = resource
                        policystmtslist.append(policyvars)
    parsedpolicies[policyname] = policystmtslist

outputfile.write('RoleName,AssumedRoleEffect,AssumedRoleAction,AssumedRoleCondition,AssumedRolePrincipal,' \
      'PolicyType,PolicyName,PolicyEffect,PolicyAction,PolicyCondition,PolicyResource\n')

for role in data['RoleDetailList']:
    #if role['RoleName'] == 'AWSServiceRoleForSupport':
        rolename = role['RoleName']
        output1 = ''
        if len(role['AssumeRolePolicyDocument']['Statement']) > 0:
            for assumerolepolicystmt in role['AssumeRolePolicyDocument']['Statement']:
                resource = ''
                action = ''
                effect = ''
                condition = ''
                if 'Resource' in assumerolepolicystmt:
                    resource = assumerolepolicystmt['Resource']
                action = assumerolepolicystmt['Action']
                effect = assumerolepolicystmt['Effect']
                if 'Condition' in assumerolepolicystmt:
                    condition = pprint.pformat(assumerolepolicystmt['Condition'])
                principal = pprint.pformat(assumerolepolicystmt['Principal'])
                output1 = '"'+ rolename+'","'+effect+'","'+action+'","'+condition+'","'+principal+'"'
                
                if len(role['RolePolicyList']) > 0:
                    for item in role['RolePolicyList']:
                        policyname = item['PolicyName']
                        for rolepolicystmt in item['PolicyDocument']['Statement']:
                            resource = rolepolicystmt['Resource']
                            effect = rolepolicystmt['Effect']
                            condition = ''
                            if 'Condition' in rolepolicystmt:
                                condition = pprint.pformat(rolepolicystmt['Condition'])
                            roleactionslist = rolepolicystmt['Action']
                            for action in roleactionslist:
                                outputfile.write(output1 + ',"RolePolicyList","'+policyname+'","'+effect+'","'+ \
                                                 action+'","'+condition+'","'+resource+'"\n')
                    
                if len(role['AttachedManagedPolicies']) > 0:
                    for attachedpolicy in role['AttachedManagedPolicies']:
                        # We get list of dictionaries containing individual permissions on the policy
                        policyname = attachedpolicy['PolicyName']
                        for policystmt in parsedpolicies[policyname]:
                            effect = policystmt['Effect']
                            action = policystmt['Action']
                            condition = policystmt['Condition']
                            if type(policystmt['Resource']) == str:
                                outputfile.write(output1 + ',"AttachedPolicy","'+policyname+'","'+effect+'","'+ \
                                  action+'","'+condition+'","'+policystmt['Resource']+'"\n')
                            else:
                                for resource in policystmt['Resource']:
                                    outputfile.write(output1 + ',"AttachedPolicy","'+policyname+'","'+effect+'","'+ \
                                      action+'","'+condition+'","'+resource+'"\n')

        else:
            print('NO ASSUMED POLICY '+rolename)

outputfile.close()