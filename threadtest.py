

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import time

def _testfunc(var,var2):
    try:
        print str(var * var2)
        print "\n"
        if var2 == 3:
            raise Exception
        time.sleep(var2)
        return (var * var2 * 10)
    except Exception as err:
        return 'salah'
func=partial(_testfunc,10)
varlist=[1,3,5,7]

pool = ThreadPool(10)
results = pool.map(func, varlist)
pool.close()
pool.join()
for r in results:
    print "result " + str(r)


