# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 10:43:52 2019

@author: nya
"""

from PyQt5 import QtCore

class RunThreadIter(QtCore.QThread):
    """ This class delegates process to a separate thread so as to make the main GUI responsive
    """
    run_percentage = QtCore.pyqtSignal(int) # holds the current iteration number
    iter_isDone = QtCore.pyqtSignal(bool) # if the current iteration is done
    allDone = QtCore.pyqtSignal(bool) # if the all iterations are done

    def __init__(self, workflow=None):
        super(RunThreadIter, self).__init__()
        self.is_running = True
        self.worklflow = workflow
    

    def run(self):
        """ Runs workflow iterations in a separate thread
        """

        while self.worklflow.iter < self.worklflow.iter_max:
            self.run_percentage.emit(int(100*(self.worklflow.iter + 1)//self.worklflow.iter_max))
            self.worklflow.iterate()

            self.iter_isDone.emit(True)
            
        
        self.allDone.emit(True)


    def stop(self):
        """ Stops the thread in which UKF inversion is run
        """
        self.is_running = False
        self.terminate()
        #self.wait()
        
        
class RunThreadSingle(QtCore.QThread):
    """ This class delegates process to a separate thread so as to make the main GUI responsive
    """
    isDone = QtCore.pyqtSignal(bool) # if the current iteration is done

    def __init__(self, workflow=None):
        super(RunThreadSingle, self).__init__()
        self.is_running = True
        self.worklflow = workflow
    

    def run(self):
        """ Runs a single job in separate thread
        """
        
        self.worklflow.run()

        self.isDone.emit(True)


    def stop(self):
        """ Stops the thread in which UKF inversion is run
        """
        self.is_running = False
        self.terminate()