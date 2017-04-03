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

import asyncore, socket

from idlegrid.structures.grid_pb2 import *
import idlegrid.packetmanager as pm
from idlegrid.client.jobmanager import JobManager, STATUS_RUNNING,\
    STATUS_STOPPED
import idlegrid.client.config as conf

import threading
import time

import struct

import sys, os

CLIENT_VERSION = 1

class GridClient(asyncore.dispatcher_with_send):

    def __init__(self, host):
        asyncore.dispatcher_with_send.__init__(self)
        self._host = host        
        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (self._host, 7001) )
        
        self.jobManager = JobManager(self.processJobStatusChange)
        
        self.buffor = bytes()
            
    def handle_close(self):
        print 'disconnected :<'
        self.jobManager.close()
        try:
            self.socket.close()
        except:
            pass

    def sendResponse(self, pack):
        packet = pm.Pack(pack).SerializeToString()
        
        self.send(struct.pack('!I', len(packet)) + packet)
        
    def handle_read(self):
        data = self.recv(10240)
        
        if not data:
            return True
        
        self.buffor += data
        
        
        while True:            
            if len(self.buffor) < 4:
                return
            
            firstlen = struct.unpack('!I', self.buffor[:4])[0]
                        
            if len(self.buffor) < firstlen+4:
                return
                        
            try:
                packet = pm.Parse(self.buffor[4:firstlen+4])
            except pm.PacketException, e:
                print 'received bad packet: %s' % str(e) 
                return
            finally:
                self.buffor = self.buffor[4+firstlen:]
            
            try:        
                if packet.__class__ == PingRequest:
                    self.sendPingResponse(packet)
                elif packet.__class__ == RegisterRequest:
                    self.sendRegisterResponse()
                elif packet.__class__ == ReportJobsRequest:
                    self.sendReportJobsResponse(packet)
                elif packet.__class__ == NewJobRequest:
                    self.processNewJobRequest(packet)
                elif packet.__class__ == JobActionRequest:
                    self.processJobActionRequest(packet)
                elif packet.__class__ == ReportSystemResourcesRequest:
                    self.processReportSystemResourcesRequest(packet)
                elif packet.__class__ == ActionRequest:
                    self.processActionRequest(packet)
            except Exception, e:
                raise
                p = ExceptionMessage()
                p.message = str(e)
                
                self.sendResponse(p)
                
        
             
    # process section
    
    def processActionRequest(self, packet):
        if packet.action == ActionRequest.ACTION_CLOSE:
            raise KeyboardInterrupt()
        else:
            raise NotImplementedError('Shutdown action')
    
    def processReportSystemResourcesRequest(self, packet):
        def getDiskFree():
            import ctypes, platform, os   
            
            if platform.system() == 'Windows':
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p('C:\\'), None, None, ctypes.pointer(free_bytes))
                return free_bytes.value
            else:
                return os.statvfs('/').f_bfree
            
        response = ReportSystemResourcesResponse()
        
        import platform
        
        if packet.reportNode:
            response.clientVersion = CLIENT_VERSION
            response.system, response.node, response.release, response.version, response.machine, response.processor = platform.uname()
            response.python_version = platform.python_version()
            
            
        if packet.reportResources:
            import psutil
              
            response.memoryFree = psutil.avail_phymem()
            response.totalMemory = psutil.TOTAL_PHYMEM
            response.cpuUsage = psutil.cpu_percent()
            response.diskFree = getDiskFree()
            
            from time import time
            
            response.actualTime = int(time());
                    
        
        if packet.reportProcessList:
            import psutil
            
            for process in psutil.process_iter():
                proc = response.processList.add()
                
                proc.pid = process.pid
                proc.name = process.name
                try:
                    proc.exe = process.exe
                except:
                    pass
                proc.userName = process.username
                #proc.cpuPercent = process.cpu_percent()
                proc.memoryPercent = process.get_memory_percent()
                
        self.sendResponse(response)
            
    def processNewJobRequest(self, pack):
        response = NewJobResponse()
                
        response.id = pack.id
          
        try:
            self.jobManager.addJob(pack.id, pack.clientUrl, pack.realtime)
        except Exception, e:
            response.success = False
            response.message = str(e)
        else:
            response.success = True
        finally:
            self.sendResponse(response)
    def processJobActionRequest(self, pack):        
        #response = JobActionResponse()
        
        #response.id = pack.id
        
        #try:
        if pack.action == JobActionRequest.ACTION_START:
            self.jobManager.getJob(pack.id).status = STATUS_RUNNING
        elif pack.action == JobActionRequest.ACTION_STOP:
            self.jobManager.getJob(pack.id).status = STATUS_STOPPED
        elif pack.action == JobActionRequest.ACTION_REMOVE:
            self.jobManager.removeJob(pack.id)
        elif pack.action == JobActionRequest.ACTION_UPDATE:
            self.jobManager.getJob(pack.id).update()
        #except Exception, e:            
        #    raise
        #    response.success = False
        #    response.message = str(e)
        #else:
        #    response.success = True
        #finally:
        #    self.sendResponse(response)
             
    # responses section
    def sendPingResponse(self, pack):
        req = PingResponse()
        
        if pack.data:
            req.data = pack.data
                
        self.sendResponse(req)
        
    def sendRegisterResponse(self):
        pack = RegisterResponse()
        
        config = conf.GridConfig()        
        pack.machineId = config.conf.machineId
        pack.clientVersion = CLIENT_VERSION

        self.sendResponse(pack)
        
    def sendReportJobsResponse(self, pack):
        jobs = self.jobManager.getJobs()
                
        if pack.reportIds:
            to_report = pack.reportIds
        else:
            to_report = list(jobs.keys())
        
        response = ReportJobsResponse()
        
        for id in to_report:       
            job = response.jobs.add()
            
            job.id = id
            job.status = jobs[id].status
            
        self.sendResponse(response)
        
        
    def processJobStatusChange(self, job):
        response = JobStatusChanged()
        
        response.id = job._id
        response.status = job.status
        
        self.sendResponse(response)
                
    
while True:
    try:
        client = GridClient('localhost')
        asyncore.loop()
    except KeyboardInterrupt:
        break
    except:
        pass
    
    time.sleep(5)
    
exit(0)
