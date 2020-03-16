

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import time

def _testfunc(var,var2):
    try:
        print str(var * var2)
        print "\n"
        #if var2 == 300:
        #    raise Exception
        time.sleep(1)
        return (var * var2 * 10)
    except Exception as err:
        print "err " + str(err)
        return 'salah'

func=partial(_testfunc,10)
varlist=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]

pool = ThreadPool(40)

step=4
for cnt in range((len(varlist)/step) + 1):
    pool = ThreadPool(5)
    var=[ v for v in  varlist[(step * cnt):((step*cnt)+step)]  ]
    results = pool.map(func,var)
    pool.close()
    pool.join()
    for r in results:
        print "result " + str(r)
    #time.sleep(10)






