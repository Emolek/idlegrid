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
from grid import GridManager
import idlegrid.server.protohandler as ph
import idlegrid.structures.gridadmin_pb2
from config import GridConfig as gc
from idlegrid.structures.gridadmin_pb2 import *
from idlegrid.structures.grid_pb2 import *

import idlegrid.packetmanager as pm

import threading

class GridAdminClientHandler(ph.ProtocolHandler):
    
    def setup(self):
        ph.ProtocolHandler.setup(self)
        
        self.loggedIn = False
        self.login = None
        
        self.proxyEnabled = False        
        self.packetProxyEnabledForSessionId = None
        self.eventsEnabled = False
        
        self.authChallenge = None
        
        self.log('connected')
        
        self.server.adminManager.addAdmin(self)
        
        # authentication timeout
        self.disconnectTimeout = threading.Timer(5, self.disconnectTimer)
        self.disconnectTimeout.start()
        
    def disconnectTimer(self):
        self.log('authentication timeout')
        # TODO: disconnect client!
        #self.connection.close()
        
        
    def handlePacket(self, pack):
        if not self.loggedIn and not pack.__class__== AuthorizationRequest:
            self.log('tried to bypass authorization')
            return False
                        
        # TODO: dict it!
        if pack.__class__ == AuthorizationRequest:
            assert self.authChallenge != None
            
            import hashlib
            
            response = AuthorizationResponse()
            
            self.loggedIn = pack.login == gc.conf.login and pack.password == hashlib.sha256(gc.conf.password + self.authChallenge).hexdigest()
     
            response.success = self.loggedIn
            
            self.sendPack(response)
            
            if self.loggedIn:
                self.login = pack.login
                self.log('logged in user: %s' % self.login)
                self.disconnectTimeout.cancel()
            else:
                self.log('bad login/password')
                return False
            
       
                
                
        elif pack.__class__ == ReportClientsRequest:
            self.processReportClientsRequest()
        elif pack.__class__ == AdminPacketProxy:
            self.proxyEnabled = pack.enabled
            self.eventsEnabled = pack.events
            if pack.HasField('enabledForSessionId'):
                self.packetProxyEnabledForSessionId = pack.enabledForSessionId
            else:
                self.packetProxyEnabledForSessionId = None
            self.log('proxy settings: proxyEnabled: %s, eventsEnabled: %s, enabledForClientId: %s' % (self.proxyEnabled, self.eventsEnabled, self.packetProxyEnabledForSessionId))
        elif pack.__class__ == PacketProxy:
            self.packetProxy(pack)
        elif pack.__class__ == NewJobRequest:
            self.addServerJob(pack)
        elif pack.__class__ == ReportJobsRequest:
            self.reportJobs()
        elif pack.__class__ == JobActionRequest:
            self.processJobActionRequest(pack)
                
                
    def processJobActionRequest(self, pack):
            self.server.gridManager.jobAction(pack)
                    
    def addServerJob(self, newJob):
        for job in gc.conf.jobs:
            if job.id == newJob.id:
                raise Exception('Not unique job id!')
            

        self.server.gridManager.addJob(newJob.id, newJob.clientUrl, newJob.realtime)
        
    def reportJobs(self):        
        response = ReportJobsResponse()
        
        for j in gc.conf.jobs:
            job = response.jobs.add()
            
            job.id = j.id
            job.status = j.status
            
            
        self.sendPack(response)
                
    def packetProxy(self, pack):
        
        self.server.gridManager.packetProxyInput(pack.sessionIds, pm.Parse(pack.packet))
                
    def processReportClientsRequest(self):
        response = ReportClientsResponse()        
        
        self.server.gridManager.clientsLock.acquire()
        for client in self.server.gridManager.clients.itervalues():
            c = response.clients.add()            
            
            c.sessionId = client.sessionId
            c.machineId = client.machineId
            c.address = '%s:%s' % client.client_address
            
        self.sendPack(response)
            
        self.server.gridManager.clientsLock.release()
                
    def finish(self):
        ph.ProtocolHandler.finish(self)
        self.log('disconnected')
        
        self.server.adminManager.removeAdmin(self)
        
        
        
    def log(self, message):
        print ('AdminClient %s:%s - ' % self.client_address) + message

class AdminManager(object):
    admins = []
    adminsLock = threading.RLock()
    
    def __init__(self, server):
        self.server = server

    def addAdmin(self, admin):
        self.admins.append(admin)
        
        import random, string
        
        chall = AuthorizationChallenge()
        chall.challenge =  ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(50))
        
        admin.authChallenge = chall.challenge
        
        admin.sendPack(chall)
        
    def removeAdmin(self, admin):
        with self.adminsLock:
            self.admins.remove(admin)
            

            
        
    def packetProxyInput(self, client, packet):        
        with self.adminsLock:
            for admin in self.admins:
                if not admin.proxyEnabled:
                    continue
                
                if admin.packetProxyEnabledForSessionId != None and admin.packetProxyEnabledForSessionId != client.sessionId:
                    continue
                
                
                pack = IncomingPacketProxy()
                
                pack.sessionId = client.sessionId
                pack.packet = pm.Pack(packet).SerializeToString()
                
                admin.sendPack(pack)
                
    def notifyClientDisconnected(self, client):
        with self.adminsLock:
            for admin in self.admins:
                if not admin.eventsEnabled:
                    continue
                
                pack = AdminClientDisconnect()
                pack.sessionId = client.sessionId
                
                admin.sendPack(pack)
                
    def notifyClientRegistered(self, client):
        with self.adminsLock:
            for admin in self.admins:
                if not admin.eventsEnabled:
                    continue
                
                pack = AdminNewClient()
                
                pack.sessionId = client.sessionId
                pack.machineId = client.machineId
                pack.address = '%s:%s' % client.client_address
                
                admin.sendPack(pack)

class GridAdminServer(SocketServer.ThreadingTCPServer):
    def __init__(self, host, port, server):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), GridAdminClientHandler)
        self.gridServer = server
        self.gridManager = server._gridManager
        
        self.gridServer._adminServer = self
        
        self.adminManager = AdminManager(self)
        
        
