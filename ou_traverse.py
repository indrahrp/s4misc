

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
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

client = boto3.client('organizations')

for ou  in paginate(client.list_children(ParentId='r-011825642366',ChildType='ORGANIZATIONAL_UNIT')):
    print str(ou)
