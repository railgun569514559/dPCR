# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Result_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1456, 1048)
        self.gridLayout_4 = QtWidgets.QGridLayout(Form)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.imgListWidget = QtWidgets.QListWidget(Form)
        self.imgListWidget.setObjectName("imgListWidget")
        self.gridLayout_3.addWidget(self.imgListWidget, 1, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.birghtDishesLCD = QtWidgets.QLCDNumber(self.groupBox)
        self.birghtDishesLCD.setObjectName("birghtDishesLCD")
        self.gridLayout_2.addWidget(self.birghtDishesLCD, 0, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.darkDishesLCD = QtWidgets.QLCDNumber(self.groupBox)
        self.darkDishesLCD.setObjectName("darkDishesLCD")
        self.gridLayout_2.addWidget(self.darkDishesLCD, 1, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.badDishesLCD = QtWidgets.QLCDNumber(self.groupBox)
        self.badDishesLCD.setObjectName("badDishesLCD")
        self.gridLayout_2.addWidget(self.badDishesLCD, 2, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.brightProporLabel = QtWidgets.QLabel(self.groupBox)
        self.brightProporLabel.setObjectName("brightProporLabel")
        self.gridLayout_2.addWidget(self.brightProporLabel, 3, 1, 1, 1, QtCore.Qt.AlignHCenter)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        self.testBtn = QtWidgets.QPushButton(Form)
        self.testBtn.setObjectName("testBtn")
        self.gridLayout_3.addWidget(self.testBtn, 2, 0, 1, 1)
        self.gridLayout_3.setRowStretch(0, 1)
        self.gridLayout_3.setRowStretch(1, 4)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.resultImgShowLayout = QtWidgets.QGridLayout()
        self.resultImgShowLayout.setObjectName("resultImgShowLayout")
        self.gridLayout_4.addLayout(self.resultImgShowLayout, 0, 1, 1, 1)
        self.gridLayout_4.setColumnStretch(0, 1)
        self.gridLayout_4.setColumnStretch(1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "计数显示"))
        self.label.setText(_translate("Form", "亮点："))
        self.label_2.setText(_translate("Form", "暗点："))
        self.label_3.setText(_translate("Form", "坏点："))
        self.label_4.setText(_translate("Form", "亮点所占比例："))
        self.brightProporLabel.setText(_translate("Form", "0"))
        self.testBtn.setText(_translate("Form", "test"))

