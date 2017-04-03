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

from structures.grid_pb2 import *
from structures.gridadmin_pb2 import *

class PacketException(Exception):
    pass

PACKET_MAPPINGS = {
                    0: RegisterRequest,
                    1: RegisterResponse,
                    2: PingRequest,
                    3: PingResponse,
                    4: NewJobRequest,
                    5: NewJobResponse,
                    6: ReportJobsRequest,
                    7: ReportJobsResponse,
                    8: JobStatusChanged,
                    9: ReportSystemResourcesRequest,
                    10: ReportSystemResourcesResponse,
                    11: ActionRequest,
                    12: JobActionRequest,
                    13: JobActionResponse,
                    14: JobProtocol,
                    15: ExceptionMessage,

                    16: PacketProxy, 
                    17: AuthorizationRequest,
                    18: AuthorizationResponse, 
                    19: ReportClientsRequest,
                    20: ReportClientsResponse,
                    21: AdminPacketProxy,
                    22: IncomingPacketProxy,
                    
                    23: AdminNewClient,
                    24: AdminClientDisconnect,
                    25: AuthorizationChallenge,
                }

class PacketException(Exception):
    pass

def Parse(packet):
    p = Packet()
    p.ParseFromString(packet)
    
    try:
        i = PACKET_MAPPINGS[p.type]()
    except KeyError:
        raise PacketException('idlegrid.client.packetmanager:Parse() cannot find packet type!')
        
    i.MergeFromString(p.packet)
        
    return i
            
def Pack(packet):
    p = Packet()
    try:
        p.type = dict((v,k) for k, v in PACKET_MAPPINGS.iteritems())[packet.__class__]
    except KeyError:
        raise Exception('idlegrid.client.packetmanager:Pack() cannot find packet type!')
    p.packet = packet.SerializeToString()
    
    return p