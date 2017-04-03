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

import SocketServer

from idlegrid.structures.grid_pb2 import *
import idlegrid.server.protohandler as ph
import idlegrid.packetmanager as pm

import threading

from config import GridConfig as gc 

import pdb
from idlegrid.structures.config_pb2 import ServerConfigInfo, ClientConfigInfo

class GridClientHandler(ph.ProtocolHandler):
    def __init__(self, *args, **kwargs):
        ph.ProtocolHandler.__init__(self, *args, **kwargs)   
    
   
    def setup(self):    
        self.registered = False
        self.machineId = ''
        self.clientVersion = 0
        
        ph.ProtocolHandler.setup(self)
        
        self.packetNeeded = {}
        
        registerRequest = RegisterRequest()
        self.sendPack(registerRequest)
        
        self.server._gridManager.addClient(self)


        # authentication and ping timeout
        #self.registerTimeout = threading.Timer(5, self.disconnectRegisterTimeout)
        #self.registerTimeout.start()

        #self.pingTimeout = threading.Timer(5, self.disconnectPingTimeout)


        #self.pingGoing = False

    def sendPack(self, pack):
        #if pack.__class__ == PingRequest and not self.pingGoing:
        #    self.pingGoing = True
        #    self.pingTimeout.start()
        ph.ProtocolHandler.sendPack(self, pack)
        
    def disconnectRegisterTimeout(self):
        self.log('register timeout')
        # TODO: disconnect client!
        #self.connection.close()
        
    def disconnectPingTimeout(self):
        self.log('ping timeout')
        # TODO: disconnect client!
        #self.connection.close()
        
    def handlePacket(self, packet):
        if not self.registered and packet.__class__ not in (PingResponse, RegisterResponse):
            self.log('not registered')
            self.request.close()
        
        if packet.__class__ == RegisterResponse:
            try:
                self.handleRegister(packet)
            except Exception, e:
                self.log('registration failed: %s' % str(e))
                return False
        elif packet.__class__ == PingResponse:
            try:
                self.handlePingResponse(packet)
            except Exception, e:
                self.log('bad PingReply: %s' % str(e))
                
            #if self.pingGoing:
            #    self.pingTimeout.cancel()
            #else:
            #    raise Exception('too much ping replies')
            
            #self.pingGoing = False
            #else:
            #    self.log('PingReply')
        else:
            self.server._gridManager.packetProxy(self, packet)
            
                    
        if packet.__class__ in self.packetNeeded.keys():
            for callback in self.packetNeeded[packet.__class__]:
                self.server._gridManager.executeCallback(callback, self, packet)
                self.packetNeeded[packet.__class__].remove(callback)


    def log(self, message):
        self.server._gridManager.log(self, message)
        
    def handlePingResponse(self, packet):
        #if packet.data != 'qazwsxedcrfvtgbyhnujmikolp':
        #    raise Exception('bad ping answer')
        pass
    
    def handleRegister(self, pack):
        if self.registered:
            raise Exception('already registered')
        
        if len(pack.machineId) != 42:
            raise Exception('bad machineId length')
        for c in pack.machineId:
            if c not in 'qazwsxedcrfvtgbyhnujmikolpQAZWSXEDCRFVTGBYHNUJMIKOLP1234567890':
                raise Exception('bad machineId character detected')
        
        self.registered = True
        self.machineId = pack.machineId
        self.clientVersion = pack.clientVersion
        
        self.log('registration succeed! - machineId: %s, clientVersion: %s' % (self.machineId, self.clientVersion))
        
        self.server._gridManager.clientRegistered(self)
        
        #self.registerTimeout.cancel()
        #del self.registerTimeout

    def onReceive(self, packetType, callback):
        '''
        try:
            self.packetNeeded[packetType].append(callback)
        except KeyError:
        '''
        self.packetNeeded[packetType] = [callback] 
            
    def sendReportJobsRequest(self, ids=[]):
        pack = ReportJobsRequest()        
    
        if len(ids):
            pack.ids = ids
        
        self.sendPack(pack)

    def finish(self):
        self.server._gridManager.removeClient(self)
        ph.ProtocolHandler.finish(self)
        
class GridManager(object):
    clients = {}
    maxClient = 0
    clientsLock = threading.RLock()
            
    def __init__(self, server):
        self._pingTimer()
        
        self.server = server
        
    def pingAll(self):
        ping = PingRequest()
        #ping.data = 'qazwsxedcrfvtgbyhnujmikolp' # default!
        
        self.toAll(ping)
         
    def packetProxy(self, client, packet):
        self.server._adminServer.adminManager.packetProxyInput(client, packet)
        
    def packetProxyInput(self, sessionIds, packet):
        try:
            for sessionId in sessionIds:
                self.clients[sessionId].sendPack(packet)
        except:
            raise
            print 'packet proxy failed'
            
    def _pingTimer(self):
        self._ping_timer = threading.Timer(5, self._pingTimer)
        self._ping_timer.start()
        
        self.pingAll()
            
    def log(self, client, message):
        print ('Client %s:%s - ' % client.client_address) + message
     
    def diffJobs(self, client):
        self.log(client, 'controlling job status')
        
        client.onReceive(ReportJobsResponse, self._diffJobs)
        client.sendReportJobsRequest()        
        
    def jobStatusChange(self, jobId, newStatus):
        packet = JobActionRequest()
        
        job = None
        
        no = 0
        
        for jobn in gc.conf.jobs:
            if jobn.id == jobId:
                gc.conf.jobs[no].status = newStatus
                
                job = gc.conf.jobs[no]
                break
            no += 1
                         
        assert job != None
        
        gc.writeConfig()
                           
        if job.status == 0:
            packet.action = JobActionRequest.ACTION_START
        else:
            packet.action = JobActionRequest.ACTION_STOP
            
        packet.id = jobId
            
        self.toAll(packet)
        
    def jobRemove(self, jobId):
        no = 0
        for job in gc.conf.jobs:
            if jobId == job.id:
                
                del gc.conf.jobs[no]
                
                break
            no += 1 
            
        gc.writeConfig()
        
        request = JobActionRequest()
        request.action = JobActionRequest.ACTION_REMOVE
        request.id = jobId
        
        self.toAll(request)
        
        
    def _diffJobs(self, client, packet):
        # TODO: this routine sucks, should be rewritten using "set"
        self.log(client, 'received job report, diffing')
    
        stopped = []
        started = []
    
        for job in gc.conf.jobs:
            if job.status == ClientConfigInfo.Job.STATUS_RUNNING:
                started.append(job.id)
            else:
                stopped.append(job.id)
    
        to_add = []        
        to_stop = []
        to_start = []
        to_remove = []
        to_leave = []
        
        for job in packet.jobs:
            if job.id in stopped: # jobs that should not be running
                if job.status != ReportJobsResponse.JobReport.STATUS_STOPPED: # but they are not
                    to_stop.append(job.id) # stop them
            elif job.id in started: # jobs that should be running
                if job.status != ReportJobsResponse.JobReport.STATUS_RUNNING: # but they are not
                    to_start.append(job.id) # start them
            else: # jobs that should not exist
                to_remove.append(job.id) # remove them
                
            try:
                started.remove(job.id)
            except: # do not worry
                pass
            
            try:
                stopped.remove(job.id)
            except: # do not worry
                pass
            
                
    
        to_add.extend(started)
        to_start.extend(started)
        to_add.extend(stopped)
                   
                
        server_jobs = {}
        
        for job in gc.conf.jobs:
            server_jobs[job.id] = job
        
        # removing jobs
        for jobid in to_remove:
            request = JobActionRequest()
            
            request.id = jobid
            request.action = JobActionRequest.ACTION_REMOVE
            
            client.sendPack(request)
            
            self.log(client, 'removing job %s' % jobid)     
            
        
        # adding missing jobs
        for jobid in to_add:
            request = NewJobRequest()
            request.id = jobid
            request.clientUrl = server_jobs[jobid].clientUrl
            request.realtime = server_jobs[jobid].realtime
            
            client.sendPack(request)
            
            self.log(client, 'adding job %s' % jobid)
            
        # stopping jobs
        for jobid in to_stop:
            request = JobActionRequest()
            
            request.id = jobid
            request.action = JobActionRequest.ACTION_STOP
            
            client.sendPack(request)
            
            self.log(client, 'stopping job %s' % jobid)
            
        # starting jobs
        for jobid in to_start:
            request = JobActionRequest()
            
            request.id = jobid
            request.action = JobActionRequest.ACTION_START
            
            client.sendPack(request)
            
            self.log(client, 'starting job %s' % jobid)
                    
    def addJob(self, id, clientUrl, realtime):
        new = gc.conf.jobs.add()
        
        new.id = id
        new.clientUrl = clientUrl
        new.status = ClientConfigInfo.Job.STATUS_STOPPED
        new.realtime = realtime
        
        gc.writeConfig()
        
        req = NewJobRequest()
        
        req.id= new.id
        req.clientUrl = new.clientUrl
        req.realtime = new.realtime
        
        self.toAll(req)
    
    
    def jobAction(self, pack):
        if pack.action == JobActionRequest.ACTION_START:
            self.jobStatusChange(pack.id, 0)
        elif pack.action == JobActionRequest.ACTION_STOP:
            self.jobStatusChange(pack.id, 2)
        elif pack.action == JobActionRequest.ACTION_REMOVE:
            self.jobRemove(pack.id)
                    
    def executeCallback(self, callback, client, packet):
        '''
        t = threading.Thread(target=callback, args=(client, packet))
        t.start()
        '''
        callback(client,packet)
        
    
        
    def addClient(self, client):
        with self.clientsLock:
            self.clients[self.maxClient] = client
            client.sessionId = self.maxClient
            self.maxClient += 1

        self.log(client, 'new client, sessionId: %s' % client.sessionId)
        
    def clientRegistered(self, client):
        self.diffJobs(client)
        self.server._adminServer.adminManager.notifyClientRegistered(client)

    
    def removeClient(self, client):
        with self.clientsLock:
            self.server._adminServer.adminManager.notifyClientDisconnected(client)
            del self.clients[client.sessionId]

        self.log(client, 'disconnected')
        
    def toAll(self, packet):
        with self.clientsLock:
            for client in self.clients.itervalues():
                if not client.registered:
                    continue
                client.sendPack(packet)
                
class GridServer(SocketServer.ThreadingTCPServer):
    def __init__(self, host, port):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), GridClientHandler)
        
        self._gridManager = GridManager(self)
        self._adminServer = None
        
    '''
    def shutdown(self):
        
        for client in self.clients:
            client.finish()
        
        SocketServer.ThreadingTCPServer.shutdown(self)
    '''