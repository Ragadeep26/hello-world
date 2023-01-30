# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_form_output_Wall.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1127, 894)
        Form.setStyleSheet("QWidget{background-color: rgb(0, 74, 127);}\n"
"\n"
"QGroupBox{background-color: rgb(251, 185, 0);}\n"
"\n"
"QWidget#widget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QLabel{background-color:rgb(215, 215, 215);}\n"
"")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setStyleSheet("")
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(895, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setStyleSheet("background-color: rgb(215, 215, 215);")
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 6, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 4, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setStyleSheet("background-color: rgb(215, 215, 215);")
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 0, 5, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.widget = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout.addWidget(self.widget)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 200))
        self.tabWidget.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableWidget = QtWidgets.QTableWidget(self.tab)
        self.tableWidget.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(120)
        self.gridLayout_2.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_3.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.tab_2)
        self.tableWidget_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(150)
        self.gridLayout_3.addWidget(self.tableWidget_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_4.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.tableWidget_3 = QtWidgets.QTableWidget(self.tab_3)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)
        self.tableWidget_3.horizontalHeader().setDefaultSectionSize(150)
        self.gridLayout_4.addWidget(self.tableWidget_3, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Wall outputs"))
        self.label.setText(_translate("Form", "Phase"))
        self.label_2.setText(_translate("Form", "Phase name"))
        self.pushButton.setText(_translate("Form", "Export data"))
        self.label_4.setToolTip(_translate("Form", "<html><head/><body><p>Wall internal forces are displayed for both for the selected phase and an envelope until that phase. In the table for max./min. wall forces, cross section forces are displayed at wall levels where minimal/ maximal shear force and bending moment occur. Wall internal forces can be saved for later dimensioning of the wall by clicking on \'Export data\'. The data path is shown at the bottom of this window.</p><p>Maximal anchor forces (AnchorForceMax2D) are read until the selected phase. Minimal strut forces (StrutForceMin2D) are read until the selected phase. Anchor forces and strut forces until the selected phase will be stored for later dimensioning.</p><p>Data can be exported for all of the calculation phases when clicking on \'Export data for all phases\'.</p></body></html>"))
        self.label_4.setText(_translate("Form", "Information?"))
        self.pushButton_2.setText(_translate("Form", "Export data for all phases"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Max./min. wall forces"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Anchor forces"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "Strut forces"))
        self.label_3.setText(_translate("Form", "Data path: "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

