# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_dialog_edit_soil_LE.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1090, 331)
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
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 8, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 4, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 0, 5, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 0, 7, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 0, 6, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Soil properties"))
        self.label_4.setText(_translate("Dialog", "E\' [kN/m<sup>2</sup>]"))
        self.label_5.setText(_translate("Dialog", "v\' [-]"))
        self.pushButton_2.setText(_translate("Dialog", "Update"))
        self.pushButton_3.setText(_translate("Dialog", "Select color"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

