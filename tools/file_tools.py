# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 11:44:53 2018

@author: nya
"""

import os
import re
import glob
import shutil
import copy
import traceback
#import pickle
import _pickle as cPickle
import numpy as np
import pandas as pd

from imp import load_source
from os.path import basename

class Struct(dict):
    def __init__(self, *args, **kwargs):
        super(Struct, self).__init__(*args, **kwargs)
        self.__dict__ = self

def loadpy(filename):
    """ Load py file
        Make sure that the file exists before calling this function
    """
#    if not exists(filename):
#        print msg.FileError % filename
#        raise IOError

    # load module
    name = re.sub('.py$', '', basename(filename))
    module = load_source(name, filename)

    # strip private attributes
    output = Struct()
    for key, val in vars(module).items():
        if key[0] != '_':
            output[key] = val
                  
    return output

def remove_file_reg_expr(reg_expr):
    """ Romove all files that match the regular expression reg_expr
    """
    for file in glob.glob(reg_expr):
        os.remove(file)


def get_file_reg_expr(reg_expr):
    """ Gets all files that match the regular expression reg_expr
    """
    files = []
    for file in glob.glob(reg_expr):
        files.append(file)
    
    return files


def combine_Ux_NMQ_files_bk(data_files_ux, data_files_NMQ):
    """ Combines data from Plaxis2D's report generator for dimensioning
    """
    data_files = []
    for ux_file, NMQ_file in zip(data_files_ux, data_files_NMQ):
        
        master_data = pd.DataFrame()
        data1 = pd.read_csv(ux_file, delimiter="\t")
        data1.columns = data1.columns.str.replace(" ", "")
        if pd.api.types.is_numeric_dtype(data1["Y[m]"]):
            master_data["Y[m]"] = data1["Y[m]"]
        elif pd.api.types.is_string_dtype(data1["Y[m]"]):
            master_data["Y[m]"] = data1["Y[m]"].str.replace(",", ".")

        if pd.api.types.is_numeric_dtype(data1["u_x[m]"]):
            master_data["u_x[m]"] = data1["u_x[m]"]
        elif pd.api.types.is_string_dtype(data1["u_x[m]"]):
            master_data["u_x[m]"] = data1["u_x[m]"].str.replace(",", ".")

        data2 = pd.read_csv(NMQ_file, delimiter="\t")
        data2.columns = data2.columns.str.replace(" ", "")
        if pd.api.types.is_numeric_dtype(data2["N[kN/m]"]):
            master_data["N[kN/m]"] = data2["N[kN/m]"]
        elif pd.api.types.is_string_dtype(data2["N[kN/m]"]):
            master_data["N[kN/m]"] = data2["N[kN/m]"].str.replace(",", ".")

        if pd.api.types.is_numeric_dtype(data2["M[kNm/m]"]):
            master_data["M[kNm/m]"] = data2["M[kNm/m]"]
        elif pd.api.types.is_string_dtype(data2["M[kNm/m]"]):
            master_data["M[kNm/m]"] = data2["M[kNm/m]"].str.replace(",", ".")

        if pd.api.types.is_numeric_dtype(data2["Q[kN/m]"]):
            master_data["Q[kN/m]"] = data2["Q[kN/m]"]
        elif pd.api.types.is_string_dtype(data2["Q[kN/m]"]):
            master_data["Q[kN/m]"] = data2["Q[kN/m]"].str.replace(",", ".")

        txt_file = ux_file.replace(" Table of total displacements", "")
        master_data.to_csv(txt_file, header=True, sep="\t", index=False)

        data_files.append(txt_file)

    return data_files


def combine_Ux_NMQ_files(data_files_ux, data_files_NMQ, x_coord):
    """ Combines data from Plaxis2D's report generator for dimensioning
    """
    data_files = []
    for ux_file, NMQ_file in zip(data_files_ux, data_files_NMQ):

        master_data = pd.DataFrame()
        data1 = pd.read_csv(ux_file, delimiter="\t")
        data1.columns = data1.columns.str.replace(" ", "")

        data2 = pd.read_csv(NMQ_file, delimiter="\t")
        data2.columns = data2.columns.str.replace(" ", "")

        col_names_xyu = ["X[m]", "Y[m]", "u_x[m]"]
    
        for col in col_names_xyu:
            if pd.api.types.is_numeric_dtype(data1[col]):
                master_data[col] = data1[col]
            elif pd.api.types.is_string_dtype(data1[col]):
                master_data[col] = pd.to_numeric(data1[col].str.replace(",", "."))
        
        col_names_NMQ = ["N[kN/m]", "M[kNm/m]", "Q[kN/m]"]
        
        for col in col_names_NMQ:
            if pd.api.types.is_numeric_dtype(data2[col]):
                master_data[col] = data2[col]
            elif pd.api.types.is_string_dtype(data2[col]):
                master_data[col] = pd.to_numeric(data2[col].str.replace(",", "."))
    
        master_data = master_data[master_data["X[m]"] == x_coord]
        master_data.drop(["X[m]"], axis=1, inplace=True)
        txt_file = ux_file.replace(" Table of total displacements", "")
        master_data.to_csv(txt_file, header=True, sep="\t", index=False)

        data_files.append(txt_file)

    return data_files


def remove(path=''):
    """ Removes directories and files in path
    """
    for name in iterable(path):
        if os.path.isfile(name):
            os.remove(name)
        elif os.path.islink(name):
            os.remove(name)
        elif os.path.isdir(name):
            shutil.rmtree(name)


def iterable(arg):
    if not isinstance(arg, (list, tuple)):
        return [arg]
    else:
        return arg


def saveobjs(filename, *args):
    """ Save Python objects using pickle
    """
    with open(filename, 'wb') as f:
        for obj in args:
            cPickle.dump(obj, f)



def saveobjs_pathpatches_ignored(filename, *args):
    """ Save Python objects using pickle
    Matplotlib pathpatches are ignored (to save a significant amount of space)
    """
    with open(filename, 'wb') as f:
        for obj in args:

            cPickle.dump(strip_pathpatches(obj), f)


def strip_pathpatches(obj):
    """ Strips away pathpatches in object
    """
    if isinstance(obj, list):
        obj_copy = []
        for element in obj:
            if isinstance(element, dict):
                element_copy = {}
                for key, value in element.items():
                    if isinstance(value, dict):
                        value_copy = {}
                        for k,v in value.items():
                            if k not in ['pathpatches', 'pathpatch', 'pathpatch_top', 'pathpatch_bottom', 'pathpatch_layer']:
                                value_copy[k] = v
                    else:
                        value_copy = value
                    if key not in ['pathpatches', 'pathpatch', 'pathpatch_top', 'pathpatch_bottom', 'pathpatch_layer']:
                        element_copy[key] = value_copy
            else:
                element_copy = element
            obj_copy.append(element_copy)

    elif isinstance(obj, dict):
        obj_copy = {}
        for key, value in obj.items():
            if key not in  ['pathpatches', 'pathpatch', 'pathpatch_top', 'pathpatch_bottom', 'pathpatch_layer']:
                obj_copy[key] = value
    else:
        obj_copy = obj

    return obj_copy


def appendobjs(filename, *args):
    """ Save Python objects using pickle
    """
    with open(filename, 'ab') as f:
        for obj in args:
            cPickle.dump(obj, f)

#def loadobjs(filename, num_items):
#    """ Load Python object using pickle
#    """
#    objs = []
#    with open(filename, 'rb') as f:
#        for i in range(num_items):
#            objs.append(None)
#            objs[i] = pickle.load(f)
#
#    return objs


def loadobjs(filename):
    """ Load Python object using pickle
        This function returns a generator rather than an iterable for efficient loading of large file
    """
    with open(filename, 'rb') as f:
        while True:
            try:
                yield cPickle.load(f)
            except EOFError:
                break


def savetxt(filename, v):
    """Save numpy array to text file"""

    np.savetxt(filename, v, '%11.6e')



def write_traceback_to_file(path, error, fname='ERROR_LOG.txt'):
    """ Writes trackback to file
    """
    with open(os.path.join(path, 'ERROR_LOG.txt'), 'a') as f:
        f.write(str(error))
        f.write(traceback.format_exc())