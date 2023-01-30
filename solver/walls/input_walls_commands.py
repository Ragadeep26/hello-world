# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 14:51:25 2021

@author: nya
"""


def write_markers(file, project_title):
    """ Write makers to WALLS input file
    """
    with open(file, 'a') as f:
        f.write('PROG Walls\n')
        f.write('KOPF {0}\n'.format(project_title))
        f.write('SEIT - - 999 2\n')

        f.write('\n\n$$$$BEGIN_OF_BAUG$$$$\n')
        f.write('$ BAUG zgw nabla KW KK KE KB KA a b Kad fad min_Kagh V_Kopf alpha\n\n')
        f.write('$$$$END_OF_BAUG$$$$\n')

        f.write('\n\n$$$$BEGIN_OF_BERM$$$$\n')
        f.write('$ BERM x1 x2 dh1 Proz HNN x3 x3 dh2\n\n')
        f.write('$$$$END_OF_BERM$$$$\n')

        f.write('\n\n$$$$BEGIN_OF_ERDE$$$$\n')
        f.write('$ ERDE Sch dh EI phi del c gam gama Kah\n\n')
        f.write('$$$$END_OF_ERDE$$$$\n')

        f.write('\n\n$$$$BEGIN_OF_BAST$$$$\n')
        f.write('$ BAST LF KL1 KL2 KL3 q1 xA1 xE1 zq1 q2 xA2 xE2 zq2 q3 xA3 xE3 zq3\n\n')
        f.write('$$$$END_OF_BAST$$$$\n')

        f.write('\n\n$$$$BEGIN_OF_AUSH$$$$\n')
        f.write('$ AUSH Pha KR zF zs zA1 zA2 zA3 zA4 zA5 zA6 zA7 zA8 zv zw KC z1 z2 eps ks1 ks2 t2 ...\n\n')
        f.write('$$$$END_OF_AUSH$$$$\n')

        f.write('\n\n$$$$BEGIN_OF_BEME$$$$\n')
        f.write('$ Phas KN etA alphA1 alphA2 alphA3 alphA4 alphA5 alphA6 alphA7 alphA8 LM1 LM2 LM3 LM4 LM5 LM6 LM7 LM8\n\n')
        f.write('$$$$END_OF_BEME$$$$\n')

        f.write('\n\n$$$$BEGIN_OF_PLOS$$$$\n')
        f.write('$ Pha IDI IHU IDR IWM MASS\n\n')
        f.write('$$$$END_OF_PLOS$$$$\n')

        f.write('\n\n$$$$BEGIN_OF_PLOT$$$$\n')
        f.write('$ Pha KTY KG DW DB DZB VS AV AH\n\n')
        f.write('$$$$END_OF_PLOT$$$$\n')

        f.write('\n\nENDE')


def write_BAUG(file, syntax, line_marker='$$$$END_OF_SOIL_BAUG$$$$'):
    """ Write input for BAUG
    """
    pass