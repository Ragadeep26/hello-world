# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_widget_Dim_MIP_steel_profile.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1423, 847)
        Form.setStyleSheet("QWidget{\n"
"background-color: rgb(0, 74, 127);\n"
"}\n"
"\n"
"QPushButton{\n"
"background-color: rgb(205, 205, 205);\n"
"}\n"
"\n"
"QLineEdit{\n"
"background-color:rgb(255, 255, 255)\n"
"}\n"
"\n"
"QSpinBox{\n"
"background-color:rgb(255, 255, 255)\n"
"}\n"
"\n"
"QLabel{\n"
"background-color:rgb(215, 215, 215)\n"
"}\n"
"\n"
"QCheckBox{\n"
"background-color:rgb(215, 215, 215)\n"
"}\n"
"\n"
"\n"
"QTableWidget{\n"
"background-color:rgb(215, 215, 215)\n"
"}\n"
"\n"
"QTabWidget{\n"
"background-color:rgb(215, 215, 215)\n"
"}\n"
"\n"
"QComboBox{\n"
"background-color:rgb(255, 255, 255)\n"
"}\n"
"\n"
"QGroupBox{\n"
"background-color: rgb(251, 185, 0);\n"
"}\n"
"\n"
"\n"
"\n"
"")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 120))
        self.groupBox.setStyleSheet("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(964, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setStyleSheet("background-color:rgb(242, 255, 116)")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 4)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 210))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridLayout_2.addWidget(self.comboBox_2, 0, 1, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_2.addWidget(self.spinBox, 0, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_2.addWidget(self.checkBox, 0, 8, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(567, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 6, 1, 2)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 0, 9, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 4, 1, 1)
        self.groupBox_9 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_9.setObjectName("groupBox_9")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_9)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.groupBox_9)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget_2.sizePolicy().hasHeightForWidth())
        self.tableWidget_2.setSizePolicy(sizePolicy)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(170)
        self.horizontalLayout.addWidget(self.tableWidget_2)
        self.gridLayout_2.addWidget(self.groupBox_9, 1, 0, 1, 10)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 500))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setMaximumSize(QtCore.QSize(350, 16777215))
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableWidget_3 = QtWidgets.QTableWidget(self.groupBox_4)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget_3)
        self.gridLayout_3.addWidget(self.groupBox_4, 0, 0, 2, 2)
        self.groupBox_8 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_8.setMaximumSize(QtCore.QSize(350, 16777215))
        self.groupBox_8.setObjectName("groupBox_8")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_8)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.tableWidget_7 = QtWidgets.QTableWidget(self.groupBox_8)
        self.tableWidget_7.setObjectName("tableWidget_7")
        self.tableWidget_7.setColumnCount(0)
        self.tableWidget_7.setRowCount(0)
        self.verticalLayout_6.addWidget(self.tableWidget_7)
        self.gridLayout_3.addWidget(self.groupBox_8, 1, 2, 1, 2)
        self.groupBox_7 = QtWidgets.QGroupBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_7.sizePolicy().hasHeightForWidth())
        self.groupBox_7.setSizePolicy(sizePolicy)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.tableWidget_6 = QtWidgets.QTableWidget(self.groupBox_7)
        self.tableWidget_6.setObjectName("tableWidget_6")
        self.tableWidget_6.setColumnCount(0)
        self.tableWidget_6.setRowCount(0)
        self.verticalLayout_5.addWidget(self.tableWidget_6)
        self.gridLayout_3.addWidget(self.groupBox_7, 1, 4, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.groupBox_5.setMaximumSize(QtCore.QSize(350, 16777215))
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tableWidget_4 = QtWidgets.QTableWidget(self.groupBox_5)
        self.tableWidget_4.setObjectName("tableWidget_4")
        self.tableWidget_4.setColumnCount(0)
        self.tableWidget_4.setRowCount(0)
        self.verticalLayout_3.addWidget(self.tableWidget_4)
        self.gridLayout_3.addWidget(self.groupBox_5, 0, 2, 1, 2)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_6.sizePolicy().hasHeightForWidth())
        self.groupBox_6.setSizePolicy(sizePolicy)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tableWidget_5 = QtWidgets.QTableWidget(self.groupBox_6)
        self.tableWidget_5.setObjectName("tableWidget_5")
        self.tableWidget_5.setColumnCount(0)
        self.tableWidget_5.setRowCount(0)
        self.tableWidget_5.horizontalHeader().setDefaultSectionSize(120)
        self.verticalLayout_4.addWidget(self.tableWidget_5)
        self.gridLayout_3.addWidget(self.groupBox_6, 0, 4, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Dimensioning tool for MIP steel profile"))
        self.groupBox.setTitle(_translate("Form", "Design settings"))
        self.comboBox.setItemText(0, _translate("Form", "BS-P: Persistent"))
        self.comboBox.setItemText(1, _translate("Form", "BS-T: Transient"))
        self.comboBox.setItemText(2, _translate("Form", "BS-A: Accidential"))
        self.comboBox.setItemText(3, _translate("Form", "BS-E: Seismic"))
        self.label.setText(_translate("Form", "Design situation"))
        self.groupBox_2.setTitle(_translate("Form", "Maximal wall internal forces"))
        self.label_3.setText(_translate("Form", "Phase"))
        self.label_2.setText(_translate("Form", "Selected wall"))
        self.checkBox.setText(_translate("Form", "Envelop of internal forces?"))
        self.pushButton_2.setText(_translate("Form", "Retrieve Plaxis2D database"))
        self.label_4.setText(_translate("Form", "Phase name"))
        self.groupBox_9.setTitle(_translate("Form", "Max. internal forces"))
        self.groupBox_3.setTitle(_translate("Form", "Design of steel profile and steel beam - concrete connection"))
        self.groupBox_4.setTitle(_translate("Form", "Geometric data"))
        self.groupBox_8.setTitle(_translate("Form", "Sketch"))
        self.groupBox_7.setTitle(_translate("Form", "Verification of the steel-concrete connection"))
        self.groupBox_5.setTitle(_translate("Form", "Cross-section classification"))
        self.groupBox_6.setTitle(_translate("Form", "Verification of the steel profile"))
        self.pushButton.setText(_translate("Form", "Print report"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

