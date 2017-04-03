# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newjobdialog.ui'
#
# Created: Sun May 29 23:29:11 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_newJobDialog(object):
    def setupUi(self, newJobDialog):
        newJobDialog.setObjectName(_fromUtf8("newJobDialog"))
        newJobDialog.resize(400, 141)
        self.formLayout = QtGui.QFormLayout(newJobDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(newJobDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.id = QtGui.QSpinBox(newJobDialog)
        self.id.setMaximum(65530)
        self.id.setObjectName(_fromUtf8("id"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.id)
        self.label_2 = QtGui.QLabel(newJobDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.clientUrl = QtGui.QLineEdit(newJobDialog)
        self.clientUrl.setObjectName(_fromUtf8("clientUrl"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.clientUrl)
        self.label_3 = QtGui.QLabel(newJobDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.realtime = QtGui.QCheckBox(newJobDialog)
        self.realtime.setText(_fromUtf8(""))
        self.realtime.setObjectName(_fromUtf8("realtime"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.realtime)
        self.buttonBox = QtGui.QDialogButtonBox(newJobDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.buttonBox)
        self.label.setBuddy(self.id)
        self.label_2.setBuddy(self.clientUrl)
        self.label_3.setBuddy(self.realtime)

        self.retranslateUi(newJobDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), newJobDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), newJobDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(newJobDialog)

    def retranslateUi(self, newJobDialog):
        newJobDialog.setWindowTitle(QtGui.QApplication.translate("newJobDialog", "Nowe zadanie", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("newJobDialog", "Identyfikator:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("newJobDialog", "Adres skryptu:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("newJobDialog", "Czasu rzeczywistego", None, QtGui.QApplication.UnicodeUTF8))

