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
import idlegrid.packetmanager as pm
from idlegrid.server.grid import GridServer
from idlegrid.server.admin import GridAdminServer



import time
import threading
'''
def info():
    while True:
        p = ReportJobsRequest()
        
        for client in server._gridManager.clients.itervalues():
            client.sendPack(p)
                
        time.sleep(5)
'''    
if __name__ == "__main__":
    
    server = GridServer('0.0.0.0', 7001) #10284
    
    serverAdmin = GridAdminServer('0.0.0.0', 7002, server) #10285
    
    serverAdminThread = threading.Thread(target=serverAdmin.serve_forever)
    serverAdminThread.setDaemon(True)
    serverAdminThread.start()
    
    '''
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    '''
    '''
    info = threading.Thread(target=info)
    info.start()
    '''    
    server.serve_forever()
    server.shutdown()
