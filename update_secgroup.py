
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

response = ec2.describe_vpcs()
sg='sg-0faaa34f24b5b5526'
#vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
#vpcid='vpc-034a1f4030ee4698b'

try:
    print "updating sec group : " + sg
    data = ec2.authorize_security_group_ingress(
        GroupId=sg,
        IpPermissions =  [
                             {
                                 "FromPort": 80,
                                 "IpProtocol": "tcp",
                                 "IpRanges": [
                                     {
                                         "CidrIp": "146.203.0.0/16"
                                     },
                                 {
                                         "CidrIp": "35.173.21.157/32",
                                         "Description": "openvpn"
                                     },
                                     {
                                         "CidrIp": "34.202.124.161/32",
                                         "Description": "OpenVPN IT Admin"
                                     }
                                 ],
                                 "Ipv6Ranges": [],
                                 "PrefixListIds": [],
                                 "ToPort": 80,
                                 "UserIdGroupPairs": []
                             },
                             {
                                 "FromPort": 22,
                                 "IpProtocol": "tcp",
                                 "IpRanges": [
                                     {
                                         "CidrIp": "146.203.121.18/32"
                                     },
                                     {
                                         "CidrIp": "109.230.199.67/32",
                                         "Description": "daniil lapshin"
                                     },
                                     {
                                         "CidrIp": "35.173.21.157/32",
                                         "Description": "openvpn"
                                     },
                                     {
                                         "CidrIp": "146.203.0.0/16",
                                         "Description": "sinai "
                                     },
                                     {
                                         "CidrIp": "74.88.89.75/32",
                                         "Description": "Brent home"
                                     },
                                     {
                                         "CidrIp": "108.46.243.28/32",
                                         "Description": "bino home"
                                     },
                                     {
                                         "CidrIp": "47.19.96.152/29",
                                         "Description": "SLAB"
                                     },
                                     {
                                         "CidrIp": "4.35.28.64/29",
                                         "Description": "SLAB"
                                     },
                                     {
                                         "CidrIp": "34.202.124.161/32",
                                         "Description": "openvpn"
                                     }
                                 ],
                                 "Ipv6Ranges": [],
                                 "PrefixListIds": [],
                                 "ToPort": 22,
                                 "UserIdGroupPairs": []
                             },
                             {
                                 "FromPort": 443,
                                 "IpProtocol": "tcp",
                                 "IpRanges": [
                                     {
                                         "CidrIp": "35.173.21.157/32",
                                         "Description": "openvpn"
                                     },
                                     {
                                         "CidrIp": "146.203.0.0/16"
                                     },
                                     {
                                         "CidrIp": "74.88.89.75/32",
                                         "Description": "Brent home"
                                     },
                                     {
                                         "CidrIp": "108.46.243.28/32",
                                         "Description": "bino home"
                                     },
                                     {
                                         "CidrIp": "4.35.28.64/29",
                                         "Description": "SLAB"
                                     },
                                     {
                                         "CidrIp": "47.19.96.152/29",
                                         "Description": "SLAB"
                                     },
                                     {
                                         "CidrIp": "18.205.99.110/32"
                                     },
                                     {
                                         "CidrIp": "34.202.124.161/32",
                                         "Description": "OpenVPN IT Admin"
                                     }
                                 ],
                                 "Ipv6Ranges": [],
                                 "PrefixListIds": [],
                                 "ToPort": 443,
                                 "UserIdGroupPairs": []
                             }


        ],


    )

    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)
