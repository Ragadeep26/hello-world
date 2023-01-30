# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:05:19 2020

@author: nya
"""
import sys
import os
import json
from collections import OrderedDict
from tools.math import hex_to_rgb, rgb_to_integer


def read_data_in_json_item(json_item, item_name):
    """ Reads material value of item (with item_name) in a json file
    """
    PATHS = sys.modules['moniman_paths']
    PATH_MATERIAL = os.path.join(PATHS['MONIMAN_OUTPUTS'], r'materials')
    #fname = os.path.join(PATH_MATERIAL, json_item + '.json')
    materials_data = None
    fname = os.path.join(PATH_MATERIAL, json_item + 'moniman.json')
    if os.path.isfile(fname):
        with open(fname, "r") as read_file:
            materials_data = json.load(read_file, object_pairs_hook = OrderedDict)         
    
    if materials_data is not None:
        try:
            value = materials_data[item_name]
            return value
        except KeyError:
            return None


def update_data_in_json_item(json_item, materials_data_to_update):
    """ Updates material value in a json file
    """
    PATHS = sys.modules['moniman_paths']
    PATH_MATERIAL = os.path.join(PATHS['MONIMAN_OUTPUTS'], r'materials')
    fname = os.path.join(PATH_MATERIAL, json_item + '.json')
    if os.path.isfile(fname):
        with open(fname, "r") as read_file:
            materials_data = json.load(read_file, object_pairs_hook = OrderedDict)         
    else: # json file does not exist
        materials_data = None

    fname_moniman = os.path.join(PATH_MATERIAL, json_item + 'moniman.json')
    if os.path.isfile(fname_moniman):
        with open(fname_moniman, "r") as read_file:
            materials_data_moniman = json.load(read_file, object_pairs_hook = OrderedDict)         
    else: # json file does not exist
        materials_data_moniman = None

    # Update material values
    for key in materials_data_to_update.keys():
        materials_data[key] =  materials_data_to_update[key]
        materials_data_moniman[key] =  materials_data_to_update[key]

    # write data for PLAXIS2D
    with open(os.path.join(PATH_MATERIAL, json_item + '.json'), "w") as write_file:
        # Wall SPW/CPW non-plaxis parameters: D, S
        materials_data.pop('D', None)
        materials_data.pop('S', None)
        json.dump(materials_data, write_file) 
        
    # write data for MONIMAN
    with open(os.path.join(PATH_MATERIAL, json_item + 'moniman.json'), "w") as write_file:
        json.dump(materials_data_moniman, write_file) 


def set_material_color(json_file, hex_text):
    """ Assign PLAXIS's integer color code to material json file
    """
    data = None
    with open(json_file, 'r') as file:
        data = OrderedDict(json.load(file, object_pairs_hook = OrderedDict))
    data['Colour'] = rgb_to_integer(hex_to_rgb(hex_text))
    with open(json_file, 'w') as file:
        json.dump(data, file)