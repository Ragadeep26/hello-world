# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 14:52:33 2018

@author: nya
"""

from PyQt5 import QtGui

class OutLog:
    def __init__(self, edit, out=None, color=None):
        """(edit, out=None, color=None) -> can write stdout, stderr to a
        QTextEdit.
        edit = QTextEdit
        out = alternate stream ( can be the original sys.stdout )
        color = alternate color (i.e. color stderr a different color)
        """
        self.edit = edit
        self.out = None
        self.color = color

    def write(self, m):
        if self.color:
            tc = self.edit.textColor()
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText( m )

        if self.color:
            self.edit.setTextColor(tc)

        if self.out:
            self.out.write(m)
            
            

#Example usage:
#import sys
#sys.stdout = OutLog( edit, sys.stdout)
#sys.stderr = OutLog( edit, sys.stderr, QtGui.QColor(255,0,0) )