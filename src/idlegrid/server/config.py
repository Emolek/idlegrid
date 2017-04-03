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

from idlegrid.structures.config_pb2 import ServerConfigInfo
from idlegrid import config


class GridConfig(config.ConfigFile):
    def readConfig(self):
        config.ConfigFile.readConfig(self)
        
        if self.conf.login == '' and self.conf.password == '':                        
            self.conf.login = 'admin'
            self.conf.password = 'admin'
        

        
GridConfig = GridConfig('server_config.dat', ServerConfigInfo)
        