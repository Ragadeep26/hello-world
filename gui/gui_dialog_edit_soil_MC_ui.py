# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_dialog_edit_soil_MC.ui'
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
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 9, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 3, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 4, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 4, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 10, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 3, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 1, 5, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 6, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 0, 5, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 6, 1, 5)
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
        self.label.setText(_translate("Dialog", "Material name"))
        self.label_2.setToolTip(_translate("Dialog", "<html><head/><body><p>When <span style=\" font-weight:600;\">Update</span> is clicked, only parameters depenent on E and v are updated and shown in the material table.</p><p>By default, K0Primanry = 1 - sin(phi). To manually set K0Primary to a specific value, K0Determination must be set to 0.</p></body></html>"))
        self.label_2.setText(_translate("Dialog", "Information?"))
        self.comboBox.setItemText(0, _translate("Dialog", "Cobbles"))
        self.comboBox.setItemText(1, _translate("Dialog", "Gravel, dense"))
        self.comboBox.setItemText(2, _translate("Dialog", "Gravel, medium"))
        self.comboBox.setItemText(3, _translate("Dialog", "Gravel, loose"))
        self.comboBox.setItemText(4, _translate("Dialog", "Sand, dense"))
        self.comboBox.setItemText(5, _translate("Dialog", "Sand, medium"))
        self.comboBox.setItemText(6, _translate("Dialog", "Sand, loose"))
        self.comboBox.setItemText(7, _translate("Dialog", "Silt, hard"))
        self.comboBox.setItemText(8, _translate("Dialog", "Silt, stiff"))
        self.comboBox.setItemText(9, _translate("Dialog", "Silt, firm"))
        self.comboBox.setItemText(10, _translate("Dialog", "Silt, soft"))
        self.comboBox.setItemText(11, _translate("Dialog", "Silt, very soft"))
        self.comboBox.setItemText(12, _translate("Dialog", "Clay, hard"))
        self.comboBox.setItemText(13, _translate("Dialog", "Clay, stiff"))
        self.comboBox.setItemText(14, _translate("Dialog", "Clay, firm"))
        self.comboBox.setItemText(15, _translate("Dialog", "Clay, soft"))
        self.comboBox.setItemText(16, _translate("Dialog", "Clay, very soft"))
        self.comboBox.setItemText(17, _translate("Dialog", "Marl, hard"))
        self.comboBox.setItemText(18, _translate("Dialog", "Marl, stiff"))
        self.comboBox.setItemText(19, _translate("Dialog", "Marl, firm"))
        self.comboBox.setItemText(20, _translate("Dialog", "Marl, soft"))
        self.comboBox.setItemText(21, _translate("Dialog", "Marl, very soft"))
        self.comboBox.setItemText(22, _translate("Dialog", "Fill"))
        self.comboBox.setItemText(23, _translate("Dialog", "Rock, intact"))
        self.comboBox.setItemText(24, _translate("Dialog", "Rock, m. weathered"))
        self.comboBox.setItemText(25, _translate("Dialog", "Rock, h. weathered"))
        self.label_5.setText(_translate("Dialog", "v\' [-]"))
        self.label_4.setText(_translate("Dialog", "E\' [kN/m<sup>2</sup>]"))
        self.pushButton.setText(_translate("Dialog", "Load"))
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

