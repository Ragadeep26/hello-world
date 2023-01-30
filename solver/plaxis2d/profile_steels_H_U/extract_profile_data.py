# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 16:27:54 2021

@author: nya
"""

import os
import json
import pandas as pd
from collections import OrderedDict
import numpy as np

infile_csv = r'D:\Data\3Packages\Moniman\solver\plaxis2d\profile_steels\profile_steels_wm.csv'    # steel profiles from Wallman
dir_out = r'D:\Data\3Packages\Moniman\solver\plaxis2d\profile_steels\jsons'

df = pd.read_csv(infile_csv, sep=';', keep_default_na=False).fillna(value=np.nan)
for i_row, row in df.iterrows():
    profile_i = row.to_json()

    #if i_row == 163:    # for debugging
    if i_row >= 0:
        try:
            #print(profile_i)
            profile_i_dict = OrderedDict(eval(profile_i))
            name_profile_i = profile_i_dict['Profile'].replace('*', 'x')    # some W profiles have '*' in name
            with open(os.path.join(dir_out, name_profile_i + '.json'), "w") as write_file:    
                json.dump(profile_i_dict, write_file)

        except Exception as e:
            print(e)
            print(i_row)