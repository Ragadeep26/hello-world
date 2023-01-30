# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_dialog_edit_all_soils.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1491, 371)
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
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(70)
        self.verticalLayout.addWidget(self.tableWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

