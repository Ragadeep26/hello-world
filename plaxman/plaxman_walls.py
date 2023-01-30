# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 15:25:31 2021

@author: nya
"""
import os
import sys
import solver.walls.input_walls_commands as walls_input

class Plaxman_WALLS():
    """ This class implements an interface to WALLS
    No user interface is needed. It only creates an input file for WALLS, runs the analysis, and gets back results.
    At the moment, it is purposed for getting an embedment depth resulting from iterations in WALLS.
    """
    def __init__(self, walls_input_file, project_title):
        """ Initializes WALLS file
        """
        if not walls_input_file:
            walls_input_file = os.path.join(sys.modules['moniman_paths']['MONIMAN_OUTPUTS'], 'retaining_wall.walls')

        self.walls_input_file = walls_input_file
        walls_input.write_markers(self.walls_input_file, project_title)
