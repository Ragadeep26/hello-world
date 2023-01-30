# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 13:44:18 2018

@author: nya
"""

class Structure:

    def __init__(self):
        self.pathpatch = None      # Store pathpatch for plotting/ unplotting
        self.gui_values = {}        # Hold values defined in GUI
        self.json_item = {}        # A json-item for holding structured properties such as soil/ 2d-wall properties
        self.isEditted = False     # If the properties have been edited, necessary for properties of such as soil and wall
        self.isPlotted = False     # If the structure has been plotted
        
    def get(self):
        """ Gets properties of a specific structure 
        """
        # Must be implemented in sub-class
        pass
    
    def get_gui_values(self):
        """ Gets GUI values
        """
        pass
    
    def print_gui_values(self):
        print(self.gui_values)
    
    def add(self):
        """ Adds structure with defined structural properties to model
        """
        pass
    
    def plot(self):
        """ Plots the structure's pathpatch on plotting widget
        """
        pass
    
    def remove(self):
        """ Removes structure
        """
        pass
    
    def unplot(self):
        """ Plots the structure's pathpatch from plotting widget
        """
        pass