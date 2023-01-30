# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 2018

@author: nya
"""

import sys, os, subprocess
from os.path import join, exists
from tools.file_tools import loadpy
from gui.gui_all_dialogs_ui import Ui_Dialog

def get_uuid():
    uuid_bytes = subprocess.check_output('wmic csproduct get UUID')
    uuid = uuid_bytes.decode('utf-8').split()[1]
    return uuid


def load_paths(path_file):
    path = join(os.getcwd(), path_file)

    if not exists(path):
        dialog = Ui_Dialog()
        dialog.show_message_box('Warning', '{} does not exist!'.format(path))
    else:
        paths = loadpy(path_file)
        sys.modules['moniman_paths'] = paths        