
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

response = ec2.describe_vpcs()
sg='sg-0aa5efdab5517a454'
#vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
vpcid='vpc-034a1f4030ee4698b'

try:
    print "updating sec group : " + sg
    data = ec2.authorize_security_group_ingress(
        GroupId=sg,
        IpPermissions=
        [
            {
                "FromPort": 80,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "146.203.0.0/16",
                        "Description": "Sinai and Brandford"
                    },
                    {
                        "CidrIp": "144.121.126.146/32",
                        "Description": "Stamford Sema4 IP"
                    },
                    {
                        "CidrIp": "172.58.232.201/32",
                        "Description": "Zach public IP"
                    },
                    {
                        "CidrIp": "32.212.37.157/32",
                        "Description": "JaneSong Home ip"
                    },
                    {
                        "CidrIp": "98.109.80.221/32",
                        "Description": "kk home ip"
                    },
                    {
                        "CidrIp": "35.173.21.157/32",
                        "Description": "OpenVPN"
                    },
                    {
                        "CidrIp": "34.195.91.139/32",
                        "Description": "essos"
                    },
                    {
                        "CidrIp": "54.144.16.248/32",
                        "Description": "xavier"
                    },
                    {
                        "CidrIp": "148.77.84.18/32",
                        "Description": "2nd Sema4 LightTower"
                    },
                    {
                        "CidrIp": "32.208.30.33/32",
                        "Description": "Janet Carr"
                    },
                    {
                        "CidrIp": "10.80.178.50/32",
                        "Description": "Rong Chen remote"
                    },
                    {
                        "CidrIp": "32.213.130.190/32",
                        "Description": "remote for Megda Antov"
                    },
                    {
                        "CidrIp": "108.53.195.152/32",
                        "Description": "Kathryn Manheimer"
                    },
                    {
                        "CidrIp": "73.239.42.80/32",
                        "Description": "Viaeria Vasta"
                    },
                    {
                        "CidrIp": "50.24.250.47/32",
                        "Description": "Tian Yu"
                    },
                    {
                        "CidrIp": "108.20.43.148/32",
                        "Description": "Cynthia Perreault-Micale"
                    },
                    {
                        "CidrIp": "71.105.210.197/32",
                        "Description": "Jane Dunning Broadben"
                    },
                    {
                        "CidrIp": "76.121.58.61/32",
                        "Description": "Sunhee Jung "
                    },
                    {
                        "CidrIp": "54.80.146.5/32",
                        "Description": "VarSleuth"
                    },
                    {
                        "CidrIp": "108.46.236.143/32",
                        "Description": "Rebecca Fox"
                    },
                    {
                        "CidrIp": "98.109.84.97/32",
                        "Description": "Ivan M"
                    },
                    {
                        "CidrIp": "67.81.133.73/32",
                        "Description": "John Li"
                    },
                    {
                        "CidrIp": "69.112.97.91/32",
                        "Description": "Robert Wisotzkey"
                    },
                    {
                        "CidrIp": "69.113.70.161/32",
                        "Description": "Geetu M"
                    },
                    {
                        "CidrIp": "69.117.252.2/32",
                        "Description": "Jinlian wang"
                    },
                    {
                        "CidrIp": "24.115.43.246/32",
                        "Description": "osman home ip"
                    },
                    {
                        "CidrIp": "73.119.207.45/32",
                        "Description": "Joerg Heyer"
                    },
                    {
                        "CidrIp": "32.208.39.62/32",
                        "Description": "Janet Hager"
                    },
                    {
                        "CidrIp": "209.6.141.61/32",
                        "Description": "Ivenise Carrero"
                    },
                    {
                        "CidrIp": "47.14.134.214/32",
                        "Description": "Kate Bogdanova"
                    },
                    {
                        "CidrIp": "74.72.57.66/32",
                        "Description": "Jixia Liu"
                    },
                    {
                        "CidrIp": "52.1.72.228/32",
                        "Description": "vonc"
                    },
                    {
                        "CidrIp": "10.80.230.24/32",
                        "Description": "BI-Pipeline"
                    }
                ],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "ToPort": 80,
                "UserIdGroupPairs": []
            },
            {
                "FromPort": 8080,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "32.212.37.157/32",
                        "Description": "JaneSong Home ip"
                    }
                ],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "ToPort": 8080,
                "UserIdGroupPairs": []
            },
            {
                "FromPort": 22,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "144.121.126.146/32",
                        "Description": "Stamford Sema4 IP"
                    },
                    {
                        "CidrIp": "146.203.0.0/16",
                        "Description": "Sinai and Brandford"
                    },
                    {
                        "CidrIp": "67.80.191.149/32"
                    },
                    {
                        "CidrIp": "32.212.37.157/32",
                        "Description": "JaneSong Home ip"
                    },
                    {
                        "CidrIp": "34.195.91.139/32",
                        "Description": "essos"
                    },
                    {
                        "CidrIp": "34.192.70.9/32",
                        "Description": "vista"
                    },
                    {
                        "CidrIp": "35.173.21.157/32",
                        "Description": "OpenVPN"
                    },
                    {
                        "CidrIp": "52.70.87.29/32",
                        "Description": "vista"
                    },
                    {
                        "CidrIp": "54.80.146.5/32",
                        "Description": "VarSleuth"
                    },
                    {
                        "CidrIp": "69.117.252.2/32"
                    },
                    {
                        "CidrIp": "24.115.43.246/32",
                        "Description": "osman home ip"
                    },
                    {
                        "CidrIp": "32.215.214.171/32",
                        "Description": "Howard Rosof"
                    }
                ],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "ToPort": 22,
                "UserIdGroupPairs": []
            },
            {
                "FromPort": 5000,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "54.144.16.248/32",
                        "Description": "xavier"
                    },
                    {
                        "CidrIp": "69.117.252.2/32",
                        "Description": "Jinlian Wang"
                    }
                ],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "ToPort": 5000,
                "UserIdGroupPairs": []
            },
            {
                "FromPort": 3306,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "144.121.126.146/32"
                    }
                ],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "ToPort": 3306,
                "UserIdGroupPairs": []
            },
            {
                "FromPort": 3000,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "144.121.126.146/32"
                    },
                    {
                        "CidrIp": "146.203.0.0/16",
                        "Description": "sinai branfford"
                    },
                    {
                        "CidrIp": "35.173.21.157/32",
                        "Description": "OpenVPN"
                    },
                    {
                        "CidrIp": "54.144.16.248/32",
                        "Description": "xavier"
                    }
                ],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "ToPort": 3000,
                "UserIdGroupPairs": []
            },
            {
                "FromPort": 443,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "144.121.126.146/32",
                        "Description": "Stamford"
                    },
                    {
                        "CidrIp": "13.82.43.82/32",
                        "Description": "azure adfs"
                    },
                    {
                        "CidrIp": "24.115.43.246/32",
                        "Description": "osman home ip"
                    },
                    {
                        "CidrIp": "32.212.37.157/32",
                        "Description": "JaneSong Home ip"
                    },
                    {
                        "CidrIp": "146.203.0.0/16",
                        "Description": "All Sinai"
                    },
                    {
                        "CidrIp": "35.173.21.157/32",
                        "Description": "Open VPN"
                    },
                    {
                        "CidrIp": "52.1.72.228/32",
                        "Description": "vonc"
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
