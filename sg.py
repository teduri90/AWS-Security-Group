import boto3

## Please use the below script at your own risk.
## This will list up unused Security Groups.
## Invalidate their Ingree and Egress.
## Then it will delete all the Security Groups deemed to be invalid.
## I would not be held responsible for any incient that might happen from running the code.
## So, again, please test it first and see if you want to use.
## I recommend for peronsal use only as well. Such as cleaning your own messy SGs

def DeleteUnusedSecurityGroup():
    client = boto3.client('ec2', region_name='ap-southeast-1')
    attached_group_list = list()
    unattached_group_list = list()
    all_group_list = list()

    #### LIST UP PART #####
    # List up all the Securiy Groups attached to network interfaces
    response = client.describe_network_interfaces()
    for i in response["NetworkInterfaces"]:
        if 'Attachment' in i and i['Attachment']['Status'] == "attached":
            groups = [g['GroupId'] for g in i['Groups']]
            attached_group_list.append(groups[0])

    # List up all the Security Groups
    response2 = client.describe_security_groups()
    for sg in response2['SecurityGroups']:
        groups2 = sg['GroupId']    
        #print(sg, "\n\n")
        if sg['GroupName'] != 'default':
            all_group_list.append(groups2)
        
    # Append unused Security Groups to Unattached Group List
    for each in all_group_list:
        if attached_group_list[0].count(each) < 1:
            unattached_group_list.append(each)

    # Loop through In-Use Security Groups to see check if it's referencing other Security Groups
    # on both Ingress and Egress
    try:
        response25 = client.describe_security_groups(GroupIds=attached_group_list)
        for each in response25['SecurityGroups']:
            if len(each['IpPermissions']) > 0:
                for permission in each['IpPermissions']:
                    if 'UserIdGroupPairs' in permission:
                        for each2 in permission['UserIdGroupPairs']:
                            unattached_group_list.remove(each2['GroupId'])
            if len(each['IpPermissionsEgress']) > 0:
                for permission in each['IpPermissionsEgress']:
                    if 'UserIdGroupPairs' in permission:
                        for each2 in permission['UserIdGroupPairs']:
                            unattached_group_list.remove(each2['GroupId'])
    except Exception as e:
        print(e)

    #### DELETION PART #####
    # Revoke all the Security Inbound and Outbound policies on each Seucirty Group
    try:
        if unattached_group_list != []:
            response3 = client.describe_security_groups(GroupIds=unattached_group_list)
            for each in response3['SecurityGroups']:
                respond = input(f"Would you want to invalidate {each['GroupId']}'s Ingress/Egress? y or n: ")
                if respond == "y" or respond == "Y":
                    if len(each['IpPermissions']) > 0:
                        for permission in each['IpPermissions']:
                            client.revoke_security_group_ingress(GroupId=each['GroupId'],IpPermissions=[permission])
                    if len(each['IpPermissionsEgress']) > 0:
                        for permission in each['IpPermissionsEgress']:
                            client.revoke_security_group_egress(GroupId=each['GroupId'],IpPermissions=[permission])
    except Exception as e:
        print(e)
    
    # Delete unused Security Group
    try:
        for each in unattached_group_list:
            respond = input(f"Would you want to delete {each}? y or n: ")
            if respond == "y" or respond == "Y":
                client.delete_security_group(GroupId=each)
                print(f"${each} deletion success")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    DeleteUnusedSecurityGroup()

