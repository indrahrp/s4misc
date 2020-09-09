#! /usr/bin/env python3
import csv
import sys
with open('/Users/indraharahap/Documents/db2_schema.csv') as csvfile:
    entries=csv.reader(csvfile,delimiter=' ')
    #print ('{')
    cnt=0
    filecnt=1
    for entry in entries:
        #print (entry[0])
        if (cnt % 20 == 0):
            #print ("file number ")

            if cnt != 0 :
                print ('  ]')
                print ('}')
            ###task_file='/Users/indraharahap/Documents/db2_task/task_' + str(filecnt)
            task_file='/Users/indraharahap/tmp/db2_task/task_' + str(filecnt)
            #print ("file number ",task_file)
            sys.stdout=open(task_file,'wt')
            print ('{')
            print ('"rules": [')
            cnt=0
            filecnt=filecnt + 1
        #print ('rules: [' )
        print ('    {')
        print ('      "rule-type": "selection",')
        print ('      "rule-id":',str(cnt+1),',',sep='')
        print ('      "rule-name":',str(cnt+1),',',sep='')
        print ('      "object-locator": {')
        print ('      "schema-name": "',entry[0].strip(),'",',sep='')
        print ('      "table-name": "%"')
        print ('        },')
        print ('      "rule-action": "include",')
        print ('      "filters": []')
        cnt=cnt + 1
        if (cnt % 43 != 0):
            print ('    },')
        else:
            print ('    }')
        #if cnt > 44:
        #    print ('')
        #    cnt=2
            #print  ('{ ')
            #print  ('"rules": ['
            #

    '''
        {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "2",
                    "rule-name": "2",
                    "object-locator": {
                        "schema-name": "%",
                        "table-name": "%"
                    },
                    "rule-action": "include",
                    "filters": []
                },
    
    '''
