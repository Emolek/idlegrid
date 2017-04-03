# coding: utf-8
#
# This file is part of IdleGrid project.
# Copyright (C) 2010 Tadeusz Magura-Witkowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

Class for managing running jobs.

'''

from multiprocessing import Process
from threading import RLock
import os
from idlegrid.client.config import GridConfig as gc
from idlegrid.structures.config_pb2 import ClientConfigInfo

STATUS_RUNNING = 0
STATUS_DOWNLOADING = 1
STATUS_STOPPED = 2
STATUS_ERROR = 3
STATUS_FINISHED = 4




class JobManager(object):
    def __init__(self, callback):        
        self.myJobs = {}
        self.myJobsLock = RLock()
        self.statusChangeCallback = callback
        
        self.restoreJobs()
        
    def restoreJobs(self):
        for job in gc.conf.jobs:
            self.myJobs[job.id] = JobWorker(job.id, job.clientUrl, job.realtime, self)
    
    def addJob(self, id, clientUrl, realtime):
        self.myJobsLock.acquire()
        if id in self.myJobs.keys():
            raise Exception('Key already in jobs!')
                
        newj = gc.conf.jobs.add()
        
        newj.id = id
        newj.clientUrl = clientUrl
        newj.status = STATUS_STOPPED
        newj.realtime = realtime
        
        gc.writeConfig()
        
        
        self.myJobs[id] = JobWorker(id, clientUrl, realtime, self)
        self.myJobsLock.release()
        
    def getJob(self, id):
        return self.myJobs[id]
        
    def removeJob(self, id):
        self.myJobsLock.acquire()
        if not id in self.myJobs.keys():
            raise Exception('Key not in jobs!')
        
        for job in gc.conf.jobs:
            if job.id == id:
                job = None
                
        gc.writeConfig()        
        del self.myJobs[id]
        
        import shutil
        
        shutil.rmtree('jobs%s%s' % (os.sep, int(id)))
        
        self.myJobsLock.release()
        
    def getJobs(self):
        self.myJobsLock.acquire()
        jobs = self.myJobs
        self.myJobsLock.release()
        
        return jobs
    
    def jobStatusChanged(self, job):
        if callable(self.statusChangeCallback):
            self.statusChangeCallback(job)
            
        if job.status == STATUS_FINISHED:
            i = 0
            
            #forget about it
            for j in gc.conf.jobs:
                if j.id == job.id:
                    del j[i]
                    break
                i += 1
            gc.conf.writeConfig()
            
                
    def __call__(self):
        return self

class JobWorker(object):
    def __init__(self, id, clientUrl, realtime, manager):
        
        self._path = 'jobs%s%s%s' % (os.sep, int(id), os.sep)
        self._mainFile = self._path+os.sep+'main.py'
        
        try:
            os.makedirs(self._path)
        except OSError:
            pass
                        
        self._id = id
        self._process = Process(target=self.run)
        self._clientUrl = clientUrl
        self.__status = STATUS_STOPPED
        self._realtime = realtime        
        
        self.manager = manager
        
    def startDownload(self):
        import urllib        
        urllib.urlretrieve(self._clientUrl, self._mainFile)
            
        
    def tryToStart(self):
        if os.path.exists(self._mainFile):
            self._status = STATUS_RUNNING
            self.start()
        else:
            self._status = STATUS_DOWNLOADING
            
            try:
                self.startDownload()
            except:
                self._status = STATUS_ERROR
            else:
                self._status = STATUS_RUNNING
                self.start()
        
    def start(self):
        self._process.start()
        
    def stop(self):
        self._process.terminate()
        self._process._popen = None
        
    def update(self):
        self.stop()
        self._status = STATUS_STOPPED
        
        os.remove(self._mainFile)
        
    def setNice(self):
        """ Set the priority of the process to below-normal."""
        import sys
        try:
            sys.getwindowsversion()
        except:
            isWindows = False
        else:
            isWindows = True
    
        if isWindows:
            # Based on:
            #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
            #   http://code.activestate.com/recipes/496767/
            import win32api,win32process,win32con
    
            pid = win32api.GetCurrentProcessId()
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
            win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            import os
    
            os.nice(1)
        
    def run(self):
        if not self._realtime:
            self.setNice()
        
        from idlegrid.client.config import GridConfig
        
        
        pass_globals = {
                        'id': self._id,
                        'machineId': GridConfig().conf.machineId
                        }
        
        try:
            exec(compile(open(self._mainFile).read(), "main.py", 'exec'), pass_globals)
        except:
            self._status = STATUS_ERROR
        else:
            self._status = STATUS_FINISHED
        
    def getStatus(self):
        return self._status
    
    def setStatus(self, new):
        assert new in (STATUS_RUNNING, STATUS_STOPPED)
        
        if new == STATUS_RUNNING:
            assert self._status in (STATUS_STOPPED, STATUS_ERROR)
            self.tryToStart()
            return
        elif new == STATUS_STOPPED:
            # assert new not in (STATUS_ERROR, STATUS_FINISHED, STATUS_STOPPED)            
            if self._status == STATUS_RUNNING:
                self.stop()
                self._status = new
                    
    def set_Status(self, new):
        self.manager.jobStatusChanged(self)
        self.__status = new
        
    def get_Status(self):
        return self.__status
    
    _status = property(get_Status, set_Status)        
    status = property(getStatus, setStatus)
    
    def __del__(self):
        try:
            self.stop()
        except:
            pass
    
    
