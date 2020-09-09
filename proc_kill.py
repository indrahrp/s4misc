
import psutil
import os
import signal
from datetime import datetime,timedelta

proc_name=['sleep']
timenow=datetime.now()
hour_running=2



def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        p.send_signal(sig)
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return (gone, alive)

def find_procs_by_name(name):
    "Return a list of processes matching 'name'."
    ls = []
    for p in psutil.process_iter(['name']):
        if p.info['name'] == name:
            #print ("create  ",p.create_time() )
                 
            ls.append(p)
    return ls



lsall=[]
for pname in proc_name:
    ls_local=(find_procs_by_name(pname))
    lsall.extend(ls_local)
        #print ("create  ",pname.create_time() )


#print ("lsall ",str(lsall))
for p in lsall:
    creation_time= datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
    creation_time_time= datetime.strptime(creation_time,"%Y-%m-%d %H:%M:%S")

    #if (timenow - creation_time_time ) > timedelta(hours=hour_running):
    print (" process name {:}, process _id {:}, creation_time {:} ".format(p.info['name'],p.pid,creation_time))
    print (" already running for {:} ".format(str(timenow - creation_time_time )))
    if (timenow - creation_time_time ) > timedelta(seconds=10):
        print ("process _id {:} is about to be killed ".format(p.pid))
        kill_proc_tree(p.pid)

    #datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
