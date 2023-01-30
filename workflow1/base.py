# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 09:26:08 2019

@author: nya
"""

class base():
    """ Inversion base class
    """

    def check(self):
        """ Check parameters and paths
        """
        raise NotImplementedError('Must be implemented in subclass')


    def main(self):
        """ Main workflow routine
        """
        raise NotImplementedError('Must be implemented in subclass')


    def checkpoint(self):
        """ Write workflow's state to disk so that it can be resumed
        """
        pass