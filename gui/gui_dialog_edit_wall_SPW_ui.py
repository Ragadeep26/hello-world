# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_dialog_edit_wall_SPW.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1066, 284)
        Dialog.setStyleSheet("QWidget{background-color: rgb(0, 74, 127);}\n"
"\n"
"QTableWidget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QCheckBox{background-color: rgb(255, 255, 255);}\n"
"\n"
"QWidget#widget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QGroupBox{background-color: rgb(251, 185, 0);}\n"
"\n"
"QPushButton{background-color: rgb(205, 205, 205);}\n"
"\n"
"QLineEdit{background-color:rgb(255, 255, 255);}\n"
"\n"
"QLabel{background-color:rgb(215, 215, 215);}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.horizontalLayout.addWidget(self.lineEdit_4)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout.addWidget(self.lineEdit_3)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.horizontalLayout_2.addWidget(self.lineEdit_5)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.splitter = QtWidgets.QSplitter(self.groupBox_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tableWidget = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.horizontalLayout_3.addWidget(self.splitter)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Wall properties"))
        self.label.setText(_translate("Dialog", "Material name"))
        self.label_2.setText(_translate("Dialog", "E [kN/m<sup>2</sup>]"))
        self.label_4.setText(_translate("Dialog", "nu"))
        self.label_3.setText(_translate("Dialog", "D [m]"))
        self.label_5.setText(_translate("Dialog", "S [m]"))
        self.checkBox.setText(_translate("Dialog", "SPW 1:3:1?"))
        self.pushButton_3.setText(_translate("Dialog", "Select color"))
        self.pushButton.setText(_translate("Dialog", "Update"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

