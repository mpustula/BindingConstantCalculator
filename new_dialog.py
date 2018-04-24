# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_New(object):
    def setupUi(self, New):
        New.setObjectName("New")
        New.resize(480, 457)
        self.verticalLayout = QtWidgets.QVBoxLayout(New)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(New)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.fileComment = QtWidgets.QTextEdit(New)
        self.fileComment.setObjectName("fileComment")
        self.gridLayout.addWidget(self.fileComment, 2, 1, 1, 1)
        self.fileName = QtWidgets.QLineEdit(New)
        self.fileName.setObjectName("fileName")
        self.gridLayout.addWidget(self.fileName, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(New)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(New)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(New)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.PointName = QtWidgets.QLineEdit(New)
        self.PointName.setObjectName("PointName")
        self.gridLayout.addWidget(self.PointName, 4, 1, 1, 1)
        self.line = QtWidgets.QFrame(New)
        self.line.setLineWidth(1)
        self.line.setMidLineWidth(0)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(New)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(New)
        self.buttonBox.accepted.connect(New.accept)
        self.buttonBox.rejected.connect(New.reject)
        QtCore.QMetaObject.connectSlotsByName(New)
        New.setTabOrder(self.fileName, self.fileComment)
        New.setTabOrder(self.fileComment, self.PointName)

    def retranslateUi(self, New):
        _translate = QtCore.QCoreApplication.translate
        New.setWindowTitle(_translate("New", "New"))
        self.label.setText(_translate("New", "Add new file"))
        self.label_2.setText(_translate("New", "File name:"))
        self.label_3.setText(_translate("New", "Comment:"))
        self.label_4.setText(_translate("New", "Point name:"))

