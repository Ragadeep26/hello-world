# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_form_Literature.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(694, 245)
        Form.setStyleSheet("QWidget{background-color: rgb(0, 74, 127);}\n"
"\n"
"QGroupBox{background-color: rgb(251, 185, 0);}\n"
"\n"
"QWidget#widget{background-color: rgb(255, 255, 255);}\n"
"\n"
"QLabel{background-color:rgb(215, 215, 215);}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Literature"))
        self.textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">* On Gaussian Process (used for metamodeling)</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Williams, C.K. and Rasmussen, C.E., (2006). Gaussian processes for machine learning. Cambridge, MA: MIT Press.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">* On Unscented Kalman Filter for back-analysis</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Nguyen, L. T., &amp; Nestorović, T. (2015). Nonlinear Kalman filters for model calibration of soil parameters for geomechanical modeling in mechanized tunneling. </span><span style=\" font-size:8pt; font-style:italic;\">Journal of Computing in Civil Engineering</span><span style=\" font-size:8pt;\">, </span><span style=\" font-size:8pt; font-style:italic;\">30</span><span style=\" font-size:8pt;\">(2), 04015025.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">* On Particle Swarm Optimization for back-analysis</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Meier, J., Schaedler, W., Borgatti, L., Corsini, A., &amp; Schanz, T. (2008). Inverse parameter identification technique using PSO algorithm applied to geotechnical modeling. </span><span style=\" font-size:8pt; font-style:italic;\">Journal of Artificial Evolution and Applications</span><span style=\" font-size:8pt;\">, </span><span style=\" font-size:8pt; font-style:italic;\">2008</span><span style=\" font-size:8pt;\">, 3.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">* On multi-objective optimization algorithm NSGA-II (used for design optimization)</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Deb, K., Pratap, A., Agarwal, S., &amp; Meyarivan, T. A. M. T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. </span><span style=\" font-size:8pt; font-style:italic;\">IEEE Transactions on Evolutionary Computation</span><span style=\" font-size:8pt;\">, </span><span style=\" font-size:8pt; font-style:italic;\">6</span><span style=\" font-size:8pt;\">(2), 182-197.</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

