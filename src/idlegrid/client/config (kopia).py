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

from idlegrid.structures.config_pb2 import *


def generateMachineId():
    import random
    
    machineId = ''
    
    random.seed()
    
    for i in range(42):
        t = random.randint(0, 2)
        
        if t == 0:
            r = random.randint(48, 57)
        elif t == 1:
            r = random.randint(65, 90)
        elif t == 2:
            r = random.randint(97, 122)
        
        machineId += chr(r)           
        
    return machineId

class GridConfig(object):
    def __init__(self):
        self.configFile = 'client_config.dat'
        self.configClass = ClientConfigInfo
        
        self.conf = self.configClass()
        self.readConfig()
                
    def readConfig(self):
        try:
            file = open(self.configFile, 'r')
            self.conf.ParseFromString(file.read())
            file.close()
            
        except IOError:
            pass
        
        if self.conf.machineId == '':
            self.conf.machineId = generateMachineId()
            self.writeConfig()
        
    def writeConfig(self):
        file = open(self.configFile, 'w')
        file.write(self.conf.SerializeToString())
        file.close()
        
    def __call__(self):
        return self
        
GridConfig = GridConfig()
        