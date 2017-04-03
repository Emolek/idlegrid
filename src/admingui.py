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

from PyQt4 import QtCore, QtGui, QtNetwork
import sys, threading


from idlegrid.admingui import logindialog, appwindow, newjobdialog
from idlegrid import packetmanager as pm
from idlegrid.structures.grid_pb2 import *
from idlegrid.structures.gridadmin_pb2 import *

from google.protobuf import message

import struct

JOB_ACTION_START, JOB_ACTION_STOP, JOB_ACTION_REMOVE, JOB_ACTION_UPDATE = range(4)
CLIENT_ACTION_SHUTDOWN, CLIENT_ACTION_CLOSE = range(2)

class SocketController(QtCore.QObject):
    packetReceived = QtCore.pyqtSignal(object)
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.sock = QtNetwork.QTcpSocket()
        
        QtCore.QObject.connect(self.sock, QtCore.SIGNAL('connected()'), self.socketConnected)
        QtCore.QObject.connect(self.sock, QtCore.SIGNAL('error(QAbstractSocket::SocketError)'), self.socketError)
        QtCore.QObject.connect(self.sock, QtCore.SIGNAL('readyRead()'), self.socketRead)
        QtCore.QObject.connect(self.sock, QtCore.SIGNAL('disconnected()'), self.disconnected)
        
        self.buffor = bytes()
        
    def socketError(self, error):
        if error != QtNetwork.QAbstractSocket.RemoteHostClosedError:
            Application.message('Błąd przy łączeniu nr. %s' % error)
        
    def socketConnected(self):
        Application.message('Połączony, czekam na rozpoczęcie procedury logowania')
        
    def socketRead(self):
        self.buffor += bytes(self.sock.readAll())
                
        while True:
            if len(self.buffor) < 4:
                return
            
            firstlen = struct.unpack('!I', self.buffor[:4])[0]
            
            if len(self.buffor) < firstlen+4:
                break
            
            try:
                packet = pm.Parse(self.buffor[4:firstlen+4])
            except Exception, e:
                Application.message('Błędny pakiet: %s' % str(e))
            finally:
                self.buffor = self.buffor[4+firstlen:]
                
            
            self.packetReceived.emit(packet)      
                
    def connect(self):
        self.sock.connectToHost(Application.host, 7002, QtCore.QIODevice.ReadWrite)
        
    def send(self, pack):
        packet = pm.Pack(pack).SerializeToString()
        self.sock.writeData(struct.pack('!I', len(packet)) + packet)
        
    def disconnected(self):
        Application.disconnected()
        
    def disconnect(self):
        self.sock.disconnectFromHost()

class PacketController(QtCore.QObject):
    loggedIn = QtCore.pyqtSignal()
    loginFailure = QtCore.pyqtSignal()
    clientsFetched = QtCore.pyqtSignal(object)
    newClientConnected = QtCore.pyqtSignal(object)
    clientDisconnected = QtCore.pyqtSignal(object)
    reportSystemResourcesResponse = QtCore.pyqtSignal(int, object)
    reportClientJobsResponse = QtCore.pyqtSignal(int, object)
    clientException = QtCore.pyqtSignal(int, object)
    reportServerJobsResponse = QtCore.pyqtSignal(object)
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.pack = SocketController()
        
        self.now = 0
        
        self.eventsProxy = False
        self.packetProxy = False
        self.packetProxyEnabledForSessionId = None
        
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('packetReceived(PyQt_PyObject)'), self.packetReceived)
        
    def packetReceived(self, pack):
        # TODO: dict it!
        if pack.__class__ == AuthorizationChallenge:
            request = AuthorizationRequest()
            
            request.login = Application.login
            
            import hashlib
                        
            request.password = hashlib.sha256(Application.password + pack.challenge).hexdigest()
            
            self.send(request)
            
            Application.message('Podjąłem wyzwanie ;P')
        elif pack.__class__ == AuthorizationResponse:
            if pack.success:
                self.loggedIn.emit()
            else:
                self.loginFailure.emit()
        elif pack.__class__ == ReportClientsResponse:
            self.enableEvents()
            self.clientsFetched.emit(pack)
        elif pack.__class__ == AdminNewClient:
            self.newClientConnected.emit(pack)
        elif pack.__class__ == AdminClientDisconnect:
            self.clientDisconnected.emit(pack)
        elif pack.__class__ == IncomingPacketProxy:
            inside = pm.Parse(pack.packet)
            if inside.__class__ == ReportSystemResourcesResponse:
                self.reportSystemResourcesResponse.emit(pack.sessionId, inside)
            elif inside.__class__ == ReportJobsResponse:
                self.reportClientJobsResponse.emit(pack.sessionId, inside)
            elif inside.__class__ == ExceptionMessage:
                self.clientException.emit(pack.sessionId, inside)
            #self.enablePacketProxy(False)
        elif pack.__class__ == ReportJobsResponse:
            self.reportServerJobsResponse.emit(pack)
        
    def fetchClients(self):
        req = ReportClientsRequest()        
        self.send(req)
        
    def send(self, pack):
        self.pack.send(pack)
        
    def connect(self):
        self.pack.connect()
        
    def closeConnection(self):
        self.pack.disconnect()
        
    
        
    def enablePacketProxy(self, enable=True, enabledForSessionId = None):
        if self.packetProxyEnabledForSessionId == enabledForSessionId and self.packetProxy == enable:
            return       
        
        request = AdminPacketProxy()
        request.enabled = self.packetProxy = enable
        request.events = self.eventsProxy
        
        if enabledForSessionId != None:
            request.enabledForSessionId = enabledForSessionId
        
        self.packetProxyEnabledForSessionId = enabledForSessionId
        
        self.send(request)
        
    def enableEvents(self):
        request = AdminPacketProxy()
        request.enabled = self.packetProxy
        request.events = self.eventsProxy = True
        
        self.send(request)
        
    def getSystemReportFor(self, sessionId):
        request = ReportSystemResourcesRequest()
        request.reportProcessList = False
        request.reportNode = True
        request.reportResources = True
        
        
        self.enablePacketProxy(True, sessionId)
        self.sendProxy(sessionId, request)
        
    def sendProxy(self, sessionIds, packet):
        proxy = PacketProxy()
        
        if sessionIds.__class__ == list:
            proxy.sessionIds.extend(sessionIds)
        else:
            proxy.sessionIds.append(sessionIds)
        
        proxy.packet = pm.Pack(packet).SerializeToString()
        
        self.send(proxy)
        
    def getJobsReportFor(self, sessionId, reportIds = None):
        request = ReportJobsRequest()
                
        if reportIds.__class__ == list:
            request.reportIds.extend(reportIds)
        elif reportIds.__class__ == int:
            request.reportIds.append(reportIds)
        
        self.enablePacketProxy(True, sessionId)    
        self.sendProxy(sessionId, request)
        
        
    def getServerJobs(self):
        request = ReportJobsRequest()
        
        self.send(request)
        
        
    def newJobRequest(self, where, id, clientUrl, realtime):
        request = NewJobRequest()
            
        request.id = id
        request.clientUrl = clientUrl
        request.realtime = realtime
        
        if where != None:
            self.sendProxy(where.data.sessionId, request)
        else:
            self.send(request)

        # we will simply ignore response...
        
    def jobAction(self, where, jobId, action):
        request = JobActionRequest()
        
        request.id = jobId
        request.action = action
        
        if where != None:
            self.sendProxy(where.data.sessionId, request)
        else:
            self.send(request)
            
    def clientAction(self, sessionIds, action):
        request = ActionRequest()
        
        request.action = action
        
        self.sendProxy(sessionIds, request)


class ClientItem(QtGui.QListWidgetItem):
    def __init__(self, where, data):
        QtGui.QListWidgetItem.__init__(self, data.address, where)
        
        self.data = data

class Application(object):
       
    def __init__(self):
        object.__init__(self)
        
        self.pack = PacketController()
        
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('clientsFetched(PyQt_PyObject)'), self.clientsFetched)
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('loggedIn()'), self.loggedIn)
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('loginFailure()'), self.loginFailure)
        
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('newClientConnected(PyQt_PyObject)'), self.newClient)
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('clientDisconnected(PyQt_PyObject)'), self.clientDisconnected)
        
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('reportSystemResourcesResponse(int, PyQt_PyObject)'), self.updateSystemResources)
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('clientException(int, PyQt_PyObject)'), self.clientException)
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('reportClientJobsResponse(int, PyQt_PyObject)'), self.reportClientJobsResponse)
        
        QtCore.QObject.connect(self.pack, QtCore.SIGNAL('reportServerJobsResponse(PyQt_PyObject)'), self.reportServerJobsResponse)
        
        
        
        self.loginf = None
        self.clientList = {}
        
    def clientException(self, sessionId, pack):
        client = self.clientList[sessionId]
        
        self.interface.ui.statusbar.showMessage(client.data.address + u' wyjątek: ' + pack.message)
        
    def updateSystemResources(self, sessionId, pack):
        self.interface.updateSystemResources(sessionId, pack)
        
    def reportClientJobsResponse(self, sessionId, pack):
        self.interface.reportClientJobsResponse(sessionId, pack)

    def reportServerJobsResponse(self, pack):
        self.interface.reportServerJobsResponse(pack)
        
    def run(self):
        self.app = QtGui.QApplication(sys.argv)      
        
        self.host = None
        self.login = None
        self.password = None
        
        self.interface = MainWindow()
        self.interface.show()
                
        sys.exit(self.app.exec_())
        
    def __call__(self):
        return self
    
    def connectToServer(self, host, login, password):
        self.host = host
        self.login = login
        self.password = password
        
        self.loginf = False
                
        self.message('Łączenie z %s@%s' % (login, host))
        self.disconnected()
        self.pack.connect()
        
        
    def loginFailure(self):
        self.loginf = True
        self.message('Rozłączony - zły login lub hasło')
    
    def loggedIn(self):
        self.message('Połączony!')
        self.interface.connected()
        self.fetchClients()
        
    def disconnected(self):
        if not self.loginf:
            self.message('Rozłączony')
        self.interface.disconnected()
                
    def disconnect(self):
        self.pack.closeConnection()
        
    def fetchClients(self):
        self.pack.fetchClients()
        
    def clientsFetched(self, pack):
        clients = pack.clients
        
        for client in clients:
            self.newClient(client)
                        
        
    def newClient(self, client):
        item = ClientItem(self.interface.ui.clientList, client)
        self.interface.ui.clientList.addItem(item)
        self.clientList[client.sessionId] = item
        self.interface.updateClientCount()
              
    
    def clientDisconnected(self, client):        
        item = self.interface.ui.clientList.takeItem(self.interface.ui.clientList.indexFromItem(self.clientList[client.sessionId]).row())
        item = None
        
        del self.clientList[client.sessionId]
        self.interface.updateClientCount()
        
    def getSystemReportFor(self, sessionId):
        self.pack.getSystemReportFor(sessionId)
    
    def getJobsReportFor(self, sessionId):
        self.pack.getJobsReportFor(sessionId)
        
    def getServerJobs(self):
        self.pack.getServerJobs()
        
    def addNewJob(self, where, id, clientUrl, realtime):
        self.pack.newJobRequest(where, id, clientUrl, realtime)
    
    def removeClientJob(self, client, jobId):
        self.pack.jobAction(client, jobId, JOB_ACTION_REMOVE)
        
    def startClientJob(self, client, jobId):
        self.pack.jobAction(client, jobId, JOB_ACTION_START)
        
    def stopClientJob(self, client, jobId):
        self.pack.jobAction(client, jobId, JOB_ACTION_STOP)
        
    def closeClient(self, client):
        self.pack.clientAction(client.data.sessionId, CLIENT_ACTION_CLOSE)
        
    def shutdownClient(self, client):
        self.pack.clientAction(client.data.sessionId, CLIENT_ACTION_SHUTDOWN)
    
    def message(self, text):
        #self.interface.ui.statusbar.showMessage(QtCore.QString.fromUtf8(text))
        self.interface.ui.statusbarLabel.setText(QtCore.QString.fromUtf8(text))
        
    def removeServerJob(self, jobId):
        self.pack.jobAction(None, jobId, JOB_ACTION_REMOVE)
    
    def startServerJob(self, jobId):
        self.pack.jobAction(None, jobId, JOB_ACTION_START)
    
    def stopServerJob(self, jobId):
        self.pack.jobAction(None, jobId, JOB_ACTION_STOP)
        
Application = Application()

class NewJobDialog(QtGui.QDialog):
    def __init__(self, where, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.ui = newjobdialog.Ui_newJobDialog()
        self.ui.setupUi(self)
        
        self.where = where
        
    def accept(self):
        Application.addNewJob(self.where, int(self.ui.id.text()), str(self.ui.clientUrl.text()), bool(self.ui.realtime.isChecked()))
        QtGui.QDialog.accept(self)

class LoginDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.ui = logindialog.Ui_LoginDialog()
        self.ui.setupUi(self)
                
    def accept(self):
        Application.connectToServer(str(self.ui.host.text()), str(self.ui.login.text()), str(self.ui.password.text()))
        QtGui.QDialog.accept(self)
    

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #self.ui = mainwindow.Ui_MainWindow()
        self.ui = appwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.statusbarLabel = QtGui.QLabel()
        self.ui.statusbar.addPermanentWidget(self.ui.statusbarLabel)
        self.ui.statusbarLabel.show()        

        self.ui.statusbarLabel.setText(u'Połącz się, aby rozpocząc pracę')
        
        self.clientListPreviousSelection = None
                
        QtCore.QObject.connect(self.ui.actionConnect, QtCore.SIGNAL('triggered()'), self.connectDialogShow)
        QtCore.QObject.connect(self.ui.actionDisconnect, QtCore.SIGNAL('triggered()'), self.disconnect)
        QtCore.QObject.connect(self.ui.clientList, QtCore.SIGNAL('itemSelectionChanged()'), self.clientListItemSelectionChanged)
        QtCore.QObject.connect(self.ui.clientList, QtCore.SIGNAL('itemClicked(QListWidgetItem*)'), self.clientListItemClicked)
        
        # i'm too lazy ;)
        for v in ('Server', 'Client'):
            for a in ('new', 'remove', 'stop', 'start'):
                QtCore.QObject.connect(getattr(self.ui, a+v+'Job'), QtCore.SIGNAL('clicked()'), getattr(self, a+v+'Job'))
                
        QtCore.QObject.connect(self.ui.closeClient, QtCore.SIGNAL('clicked()'), self.closeClient)
        QtCore.QObject.connect(self.ui.shutdownClient, QtCore.SIGNAL('clicked()'), self.shutdownClient)
        
        QtCore.QObject.connect(self.ui.jobsClientList, QtCore.SIGNAL('itemSelectionChanged()'), self.jobsClientListSelectionChanged)
        
        QtCore.QObject.connect(self.ui.serverJobList, QtCore.SIGNAL('itemSelectionChanged()'), self.serverJobListSelectionChanged)
        
        self.infoTimer = QtCore.QTimer(self)
        self.infoTimer.setInterval(600)
            
        QtCore.QObject.connect(self.infoTimer, QtCore.SIGNAL('timeout()'), self.fetchInfoTimer)

    def jobsClientListSelectionChanged(self):
        enabled = len(self.ui.jobsClientList.selectedItems()) > 0
        
        for a in ('remove', 'stop', 'start'):
            getattr(self.ui, a+'ClientJob').setEnabled(enabled)

    def serverJobListSelectionChanged(self):
        enabled = len(self.ui.serverJobList.selectedItems()) > 0
        
        for a in ('remove', 'stop', 'start'):
            getattr(self.ui, a+'ServerJob').setEnabled(enabled)

    def closeClient(self):
        Application.closeClient(self.ui.clientList.selectedItems()[0])
    
    def shutdownClient(self):
        Application.shutdownClient(self.ui.clientList.selectedItems()[0])

    def newServerJob(self):
        dialog = NewJobDialog(None, self)
        dialog.show()
    
    def removeServerJob(self):
        Application.removeServerJob(self._serverJobId())
    
    def stopServerJob(self):
        Application.stopServerJob(self._serverJobId())
    
    def startServerJob(self):
        Application.startServerJob(self._serverJobId())
    
    def newClientJob(self):
        dialog = NewJobDialog(self.ui.clientList.selectedItems()[0], self)
        dialog.show()
        
    def _clientJobId(self):
        for idx in self.ui.jobsClientList.selectedItems():
            return int(idx.text())
    
    def _serverJobId(self):
        for idx in self.ui.serverJobList.selectedItems():
            return int(idx.text())
    
    def removeClientJob(self):
        Application.removeClientJob(self.ui.clientList.selectedItems()[0], self._clientJobId())
    
    def stopClientJob(self):
        Application.stopClientJob(self.ui.clientList.selectedItems()[0], self._clientJobId())
    
    def startClientJob(self):
        Application.startClientJob(self.ui.clientList.selectedItems()[0], self._clientJobId())
    

    def fetchInfoTimer(self):
        if self.ui.stackedWidget.currentIndex() == 0: # clientTab
            tab = self.ui.clientTabWidget.currentIndex()
            if tab == 0: # informations
                Application.getSystemReportFor(self.ui.clientList.selectedItems()[0].data.sessionId)
            elif tab == 1: #jobs
                Application.getJobsReportFor(self.ui.clientList.selectedItems()[0].data.sessionId)
        elif self.ui.stackedWidget.currentIndex() == 1: # gridTab
            tab = self.ui.gridTabWidget.currentIndex()
            if tab == 0: #informations
                pass
            elif tab == 1: #jobs
                Application.getServerJobs()
    
    
        
    def updateClientCount(self):
        self.ui.clientCount.setText(str(
                                     self.ui.clientList.count()
                                     ))
    def updateServerHost(self):
        self.ui.serverHost.setText(Application.host)    
    
    def disconnected(self):
        self.infoTimer.stop()        
        self.mainNotConnectedTab()
        
        self.ui.actionConnect.setEnabled(True)
        self.ui.actionDisconnect.setEnabled(False)
        
        self.ui.clientList.clear()
        
    def connected(self):
        self.infoTimer.start()
        self.updateClientCount()
        self.mainGridTab()
        self.updateServerHost()
        
        self.ui.actionConnect.setEnabled(False)
        self.ui.actionDisconnect.setEnabled(True)
        
    def mainGridTab(self):
        self.setMainTab(1)
        
    def mainNotConnectedTab(self):
        self.setMainTab(2)
        
    def mainClientTab(self):
        self.setMainTab(0)
        
    def setMainTab(self, no):
        self.ui.stackedWidget.setCurrentIndex(no)
        
    def connectDialogShow(self):
        dialog = LoginDialog(self)
        dialog.show()
        
    def disconnect(self):
        Application.disconnect()
        
    def clientListItemClicked(self, item):
        if self.clientListPreviousSelection != None:
            if self.ui.clientList.selectedItems()[0] == self.clientListPreviousSelection:
                self.clientListPreviousSelection = None
                self.ui.clientList.clearSelection()
                self.ui.clientList.clearFocus()
                return
        self.clientListPreviousSelection = item
        
    def clientListItemSelectionChanged(self):
        num = len(self.ui.clientList.selectedItems())
                        
        if num == 0:
            self.mainGridTab()
        elif num == 1:
            self.ui.clientTabWidget.setCurrentIndex(0)
            
            item = self.ui.clientList.selectedItems()[0]
            
            self.ui.machineId.setText(item.data.machineId)
            self.ui.sessionId.setText(str(item.data.sessionId))

            self.mainClientTab()
        else:
            self.mainNotConnectedTab()


    def _jobReport(self, where, pack):
        where.setRowCount(len(pack.jobs))
                
        rowno = 0
        
        JOB_STATUS = (u'uruchomiona', u'pobieranie klienta', u'zatrzymana', u'błąd', u'zakończone')
        
        for job in pack.jobs:
            where.setItem(rowno, 0, QtGui.QTableWidgetItem(str(job.id)))
            where.setItem(rowno, 1, QtGui.QTableWidgetItem(JOB_STATUS[job.status]))
            
            rowno+=1
        
    def reportClientJobsResponse(self, sessionId, pack):
        self._jobReport(self.ui.jobsClientList, pack)
        
    def reportServerJobsResponse(self, pack):        
        self._jobReport(self.ui.serverJobList, pack)    
            
    def updateSystemResources(self, sessionId, pack):
        for v in ('clientVersion', 'version', 'release', 'system', 'node', 'version', 'machine', 'processor', 'memoryFree', 'totalMemory', 'cpuUsage', 'diskFree', 'actualTime'):
            try:
                att = getattr(pack, v)
                
                if v == 'cpuUsage':
                    att = str(int(att)) + '%'
                elif v == 'actualTime':
                    from time import strftime, gmtime
                    att = strftime('%d-%m-%Y %H:%M:%S', gmtime(att))
                elif v == 'processor' and att == '':
                    raise Exception()
                
                getattr(self.ui, v).setText(str(att))
            except:
                getattr(self.ui, v).setText('-')
                
    
        
        
def main():
    app = Application()
    app.run()
    
        
if __name__ == '__main__':
    main()
