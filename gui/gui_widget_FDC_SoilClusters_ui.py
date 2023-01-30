# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_widget_FDC_SoilClusters.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1130, 687)
        Dialog.setStyleSheet("QWidget{\n"
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
"QComboBox{\n"
"background-color:rgb(255, 255, 255)\n"
"}\n"
"")
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 1, 1, 1, 1)
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.groupBox = QtWidgets.QGroupBox(self.splitter)
        self.groupBox.setEnabled(True)
        self.groupBox.setToolTip("")
        self.groupBox.setStyleSheet("QGroupBox{\n"
"background-color: rgb(251, 185, 0);\n"
"}\n"
"")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setContentsMargins(5, 5, 0, 5)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(408, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(80)
        self.gridLayout.addWidget(self.tableWidget, 2, 0, 1, 6)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 0, 3, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 5, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.splitter)
        self.groupBox_2.setStyleSheet("QGroupBox{\n"
"background-color: rgb(251, 185, 0);\n"
"}\n"
"")
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setContentsMargins(0, 5, 5, 5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setObjectName("widget")
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 2)
        self.gridLayout_3.addWidget(self.splitter, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "Close"))
        self.label_4.setText(_translate("Dialog", "Sublayer thickness [m]"))
        self.label.setText(_translate("Dialog", "Width of the improved soil [m]"))
        self.lineEdit_4.setText(_translate("Dialog", "2.0"))
        self.label_5.setToolTip(_translate("Dialog", "<html><head/><body><p>The calculations here follow Priebe [1]. Below are the summaries.</p><p>Depending on the sub soil layer thickness and depth of columns given, the number of sub soil layers will be adjusted accordingly. Soil parameters of the sub soil layers are copied from the original soil layers, only stiffness moduli are improved and soil strength parameters are adjusted after Priebe equations.</p><p>Soil stiffness E_s and columns stiffness E_c are calculated for each sub soil layers in the improved soil region following the relation E = v_e * 100 * (sigma_v\'/100)^w_e.</p><p>When friction angle of soil is modified by the columns, K0nc is updated by the relation K0nc = 1 - sin(phi_bar).</p><p>For HS-small soil, the ratio E_dyn/E_sta is recalculated from the current EurRef value by interpolationg from the (E_dyn/E_sta - E_sta) curve for soil. Then, G0ref is adapted following the relation G0ref = EurRef*(E_dyn/E_sta)*(1/2.4).</p><p>Reference:</p><p>[1] Priebe, H.J., 1995. The design of vibro replacement. <span style=\" font-style:italic;\">Ground engineering</span>, <span style=\" font-style:italic;\">28</span>(10), p.31.</p></body></html>"))
        self.label_5.setText(_translate("Dialog", "Information?"))
        self.lineEdit.setText(_translate("Dialog", "10.0"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

