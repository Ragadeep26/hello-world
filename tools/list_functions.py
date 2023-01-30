# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 14:45:52 2020

@author: nya
"""

import collections


def flatten_list(l):
    """ Flattens a list of iterable and non-iterable elements
    """
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el
            
if __name__ == '__main__':
    l = [[0.9], 10.565517534117031]
    l_flattened = list(flatten_list(l))
    
    print(l_flattened)