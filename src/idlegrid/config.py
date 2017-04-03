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

class ConfigFile(object):
    def __init__(self, configFile, configClass):
        self.configClass = configClass
        self.configFile = configFile        
        
        self.conf = (self.configClass)()
        self.readConfig()
                
    def readConfig(self):
        try:
            file = open(self.configFile, 'r')
            self.conf.ParseFromString(file.read())
            file.close()
            
        except IOError:
            pass
        
    def writeConfig(self):
        file = open(self.configFile, 'w')
        file.write(self.conf.SerializeToString())
        file.close()
        
    def __call__(self):
        return self