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
import idlegrid.packetmanager as pm
import struct

class ProtocolHandler(SocketServer.StreamRequestHandler):
    def __init__(self, *args, **kwargs):
        self.buffor = bytes()
        SocketServer.StreamRequestHandler.__init__(self, *args, **kwargs)
        
        
    
    def sendPack(self, pack):
        packet = pm.Pack(pack).SerializeToString()
        
        self.wfile.write(struct.pack('!I', len(packet)) + packet)
        
        
        
    def handle(self):
        while True:
            try:
                recv = self.request.recv(10240)
            except:
                return
            
            if not recv:
                return
            
            self.buffor += recv

            
            while True:
                if len(self.buffor) < 4:
                    break
                
                firstlen = struct.unpack('!I', self.buffor[:4])[0]
                
                if len(self.buffor) < firstlen+4:
                    break
                                        
                try:
                    packet = pm.Parse(self.buffor[4:firstlen+4])
                except:
                    self.log('received bad packet')
                    return
                finally:
                    self.buffor = self.buffor[4+firstlen:]
                
                if self.handlePacket(packet) == False:
                    return
            
    def handlePacket(self, packet):
        raise Exception('handlePacket is not overridden')
    
    def log(self, message):
        raise Exception('log is not overridden')