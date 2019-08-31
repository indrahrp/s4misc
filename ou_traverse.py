

import boto3
import random
import time
import sys
import argparse
import uuid
import json
import os
import datetime
import pprint
import operator

def paginate(method, **kwargs):
    client = method.__self__
    print "pg "  + str(client)
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

client = boto3.client('organizations')
resp=client.list_roots()
#print str(resp)
#response = client.list_accounts_for_parent(ParentId="o-o89uiwb37y")
#print str(response)
#response = client.describe_organization(ParentId="r-011825642366")
#print str(response)

res=client.list_children(ParentId="r-66ay",ChildType='ORGANIZATIONAL_UNIT')
#print str(res)
b=res['Children']
#for ou  in paginate(client.list_children(ParentId="r-66ay",ChildType='ORGANIZATIONAL_UNIT')):
for ou  in paginate(client.list_children,ParentId="r-66ay",ChildType='ORGANIZATIONAL_UNIT'):
    print str(ou['Id'])
    for ouacc  in paginate(client.list_children,ParentId=ou['Id'],ChildType='ORGANIZATIONAL_UNIT'):
        print "ou again " + str(ouacc)
        for ouacc  in paginate(client.list_children,ParentId=ouacc['Id'],ChildType='ACCOUNT'):
            print "ou account again " + str(ouacc)
    #for ouacc  in paginate(client.list_children,ParentId=ou['Id'],ChildType='ACCOUNT'):
    #    print str(ouacc)
#for ou  in paginate(client.list_children,ParentId="r-66ay",ChildType='ACCOUNT'):
#    print "ou root"
#    print str(ou['Id'])
  #for oua in ou:
  #  print str(oua)
#for a in b:
#    print str(a)
