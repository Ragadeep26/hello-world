# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_widget_Borelogs.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1283, 858)
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
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.groupBox = QtWidgets.QGroupBox(self.splitter)
        self.groupBox.setStyleSheet("QGroupBox{\n"
"background-color: rgb(251, 185, 0);\n"
"}\n"
"")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_2.setMaximumSize(QtCore.QSize(120, 16777215))
        self.lineEdit_2.setText("")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(826, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 3)
        spacerItem1 = QtWidgets.QSpacerItem(889, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 4)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEdit.setMaximumSize(QtCore.QSize(120, 16777215))
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 3, 5, 1, 2)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 6, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 3, 4, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 6, 1, 1)
        self.treeWidget = QtWidgets.QTreeWidget(self.groupBox)
        self.treeWidget.setStyleSheet("background-color: rgb(215, 215, 215);")
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.header().setDefaultSectionSize(80)
        self.treeWidget.header().setStretchLastSection(False)
        self.gridLayout.addWidget(self.treeWidget, 2, 0, 1, 7)
        spacerItem2 = QtWidgets.QSpacerItem(889, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 2, 1, 4)
        self.groupBox_2 = QtWidgets.QGroupBox(self.splitter)
        self.groupBox_2.setStyleSheet("background-color: rgb(215, 215, 215);")
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setObjectName("widget")
        self.verticalLayout_2.addWidget(self.widget)
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Borelog analyzer"))
        self.groupBox.setTitle(_translate("Form", "Bore logs"))
        self.lineEdit_2.setPlaceholderText(_translate("Form", "0.0"))
        self.lineEdit.setPlaceholderText(_translate("Form", "0.0, 0.0"))
        self.pushButton_3.setText(_translate("Form", "Interpolate elevations"))
        self.pushButton_2.setText(_translate("Form", "Remove the last borelog"))
        self.label_3.setText(_translate("Form", "Interpolation method"))
        self.label.setText(_translate("Form", "Position x, y"))
        self.label_2.setText(_translate("Form", "GW level"))
        self.comboBox.setItemText(0, _translate("Form", "linear"))
        self.comboBox.setItemText(1, _translate("Form", "cubic"))
        self.pushButton.setText(_translate("Form", "Add a borelog"))
        self.groupBox_2.setTitle(_translate("Form", "View"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

