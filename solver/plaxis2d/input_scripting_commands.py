# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 14:53:32 2018

@author: nya
"""

import os
import shutil
#import io 
#class InputPlaxis2D(io.TextIOWrapper):

def write_imports(file, PATHS):
    with open(file, 'w') as f:
        f.write('import sys, os, glob\n')
        f.write('#import imp\n')
        f.write('import json\n')
        f.write("PLAXIS2D_SCRIPTING = r'{}'\n".format(PATHS['PLAXIS2D_SCRIPTING']))
        f.write("PLAXIS2D = r'{}'\n".format(PATHS['PLAXIS2D']))
        f.write("MONIMAN = r'{}'\n".format(PATHS['MONIMAN']))
        f.write("MONIMAN_OUTPUTS = r'{}'\n".format(PATHS['MONIMAN_OUTPUTS']))
        f.write('sys.path.append(PLAXIS2D_SCRIPTING)\n')
        f.write('sys.path.append(PLAXIS2D)\n')
        f.write('sys.path.append(MONIMAN)\n')
        f.write('sys.path.append(MONIMAN_OUTPUTS)\n')
        f.write("""
#try:
#    found_module = imp.find_module('plxscripting', [PLAXIS2D_SCRIPTING])
##    print('found plxscripting module:', found_module)
#    plxscripting = imp.load_module('plxscripting',*found_module)
#except ImportError:
#    sys.exit("Please check if PLAXIS2D_SCRIPTING path is correct!")

from plxscripting.easy import new_server
from common.boilerplate import start_plaxis, get_calculation_status

# Start PLAXIS2D Input for the first time and do not close 
p = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DXInput.exe'))

# Initialize Input server which has been opened at Port number PORT
s_i, g_i = new_server('localhost', 10000, password = 'mypassword')
    
# Start a new project and create the desired model.
s_i.new()    
                """)
            
def rewrite_imports(file, PATHS):
    """ Rewrite imports in retaining_wall.py
    """
    filetemp = 'temp.txt'
    line_marker = 'MONIMAN_OUTPUTS'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip().split()[0] == line_marker:               
                #in_file.readline() # line 1 is ignored
                #out_file.write(line) # keep marker line
                out_file.write("MONIMAN_OUTPUTS = r'{}'\n".format(PATHS['MONIMAN_OUTPUTS']))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def write_predefined_funtions(file):
    with open(file, 'a') as f:
        f.write('\n\n## Predefined functions\n')
        f.write("""
# Create anchors
def make_ground_anchor(x, y, angle, Lfree, Lbond):
    pntA = g_i.point(x, y)

    # create a new line under angle
    # also creates a new point
    g_i.lineangles(pntA, angle, Lfree)

    anchor = g_i.n2nanchor(g_i.Lines[-1])

    g_i.lineangles(g_i.Points[-1], angle, Lbond)
    groutbody = g_i.embeddedbeamrow(g_i.Lines[-1])

    groutbody.Behaviour = "Grout body" 
    
    return anchor, groutbody


def write_calculation_status(g_i):
    allpassed, status_details = get_calculation_status(g_i)
    
    reg_expr = os.path.join(MONIMAN_OUTPUTS,'plaxisinfo*.txt')
    for file in glob.glob(reg_expr):
        os.remove(file)
    
    if allpassed:
        plaxisinfo_file = os.path.join(MONIMAN_OUTPUTS, 'plaxisinfo_PASSED.txt')
    else:
        plaxisinfo_file = os.path.join(MONIMAN_OUTPUTS, 'plaxisinfo_FAILED.txt')

    with open(plaxisinfo_file, 'w') as f:
        for item in status_details:
            f.write("%s\\n" % item)
            
        """)

def write_markers(file, prefix, close_plaxis=True):
    with open(file, 'a') as f:
        f.write('\n\n####BEGIN_OF_SOIL_LAYERS####\n\n')
        f.write('####END_OF_SOIL_LAYERS####\n')

        f.write('\n\n####BEGIN_OF_SOIL_MATERIALS####\n\n')
        f.write('####END_OF_SOIL_MATERIALS####\n')
        
        f.write('\n\n####BEGIN_OF_STRUCTURES####\n\n')
        f.write('{}.gotostructures()\n'.format(prefix))
        f.write('####END_OF_STRUCTURES####\n')
        
        f.write('\n\n####BEGIN_OF_MESH####\n\n') 
        f.write('{}.gotomesh()\n'.format(prefix))
        f.write('\n')
        f.write('\n')
        f.write('{}.mesh(0.06, False)\n\n'.format(prefix))
        f.write('####END_OF_MESH####\n')

        f.write('\n\n####BEGIN_OF_FLOW####\n\n') 
        f.write('{}.gotoflow()\n'.format(prefix))      
        f.write('####END_OF_FLOW####\n')

        f.write('\n\n####BEGIN_OF_STAGES####\n\n') 
        f.write('{}.gotostages()\n'.format(prefix)) 
        f.write('####END_OF_INITIAL_PHASE####\n\n')
        f.write('####END_OF_STAGES####\n')
        f.write('{}.calculate()\n'.format(prefix)) 
        f.write('write_calculation_status({})\n'.format(prefix))
        f.write("{}.save(os.path.join(MONIMAN_OUTPUTS, 'retaining_wall.p2dx'))\n\n".format(prefix)) 
        if close_plaxis:
            f.write('####TERMINATION####\n')
            f.write('{}.close()\n'.format('s_i'))    # close model (project)
            f.write('p.terminate()\n')  # close Plaxis2D Input
        

def remove_termination(file):
    """ Removes lines for termination of Plaxis2D Input after calculation
    """
    filetemp = 'temp.txt'
    line_marker = '####TERMINATION####'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                in_file.readline() # line 2 is ignored
                out_file.write(line) # keep marker line
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_termination(file):
    """ Adds lines for termination of Plaxis2D Input after calculation
    """
    filetemp = 'temp.txt'
    line_marker = '####TERMINATION####'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                in_file.readline() # line 2 is ignored
                out_file.write(line) # keep marker line
                out_file.write('{}.close()\n'.format('s_i'))    # close model (project)
                out_file.write('p.terminate()\n')  # close Plaxis2D Input
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)

    
def set_project_properties(file, prefix, project_properties, PATHS):
    """ Write out project properties to input file
    """
    project_title = project_properties['project_title']
    model_type = project_properties['model_type']
    element_type = project_properties['element_type']

    write_imports(file, PATHS)
    
    write_predefined_funtions(file)
    
    with open(file, 'a') as f:
        f.write('\n\n## Set project properties\n')
        f.write('project_title = {}\n'.format(repr(project_title))) 
        f.write('model_type = {}\n'.format(repr(model_type)))
        f.write('element_type = {}\n'.format(repr(element_type)))
        f.write('''\nproject_properties = [('Title', project_title),
                      ('UnitForce', 'kN'),
                      ('UnitLength', 'm'),
                      ('UnitTime', 's'),    # time unit in seconds
                      ('ModelType', model_type),
                      ('ElementType', element_type)]\n''')
        f.write(prefix + '.Project.setproperties(*project_properties)\n')
            
    write_markers(file, prefix)
    

def set_project_title(file, project_title):
    """ Rewrite imports in retaining_wall.py
    """
    filetemp = 'temp.txt'
    line_marker = 'project_title'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip().split()[0] == line_marker:               
                #in_file.readline() # line 1 is ignored
                #out_file.write(line) # keep marker line
                out_file.write("project_title = '{}'\n".format(project_title))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def set_geometry(file, prefix, geometry, line_marker = '####END_OF_SOIL_LAYERS####'):
    """ Writes out geometric settings to input file
    """
    xmin = geometry[0]
    ymin = geometry[1]
    xmax = geometry[2]
    ymax = geometry[3]

    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##GEOMETRY\n')
                f.write('xmin, ymin, xmax, ymax = {0}, {1}, {2}, {3}\n'.format(xmin, ymin, xmax, ymax))
                f.write(prefix + '.SoilContour.initializerectangular(xmin, ymin, xmax, ymax)\n\n')
                f.write(line_marker + '\n')
            else:
                f.write(line)
        

def update_geometry(file, prefix, geometry):
    """ Modifies x_min and x_max of the model
    """
    xmin = geometry[0]
    ymin = geometry[1]
    xmax = geometry[2]
    ymax = geometry[3]
    filetemp = 'temp.txt'
    line_marker = '##GEOMETRY'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                out_file.write(line) # keep marker line
                out_file.write('xmin, ymin, xmax, ymax = {0}, {1}, {2}, {3}\n'.format(xmin, ymin, xmax, ymax))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_borehole(file, prefix, BH_number, borehole, line_marker = '####END_OF_SOIL_LAYERS####'):
    """ Writes out adding a borehole to input file
    """
    x = borehole['x']
    Head = borehole['Head']
    identification = borehole['id']
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##BOREHOLE ({})\n'.format(identification))
                f.write('borehole_' + str(BH_number) + ' = ' + prefix + '.borehole({})\n'.format(x))
                f.write('borehole_' + str(BH_number) + '.Head = {}\n'.format(Head))
                f.write("{0}.rename(borehole_{1}, '{2}')\n\n".format(prefix, BH_number, borehole['name']))
                f.write(line_marker + '\n')
            else:
                f.write(line)
        

def update_borehole(file, prefix, borehole, bh_number):
    """ Updates borehole properties
    """
    filetemp = 'temp.txt'
    line_marker = '##BOREHOLE ({})'.format(borehole['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                in_file.readline() # line 2 is ignored
                in_file.readline() # line 3 is ignored
                out_file.write(line) # keep marker line
                out_file.write('borehole_{0} = {1}.borehole({2})\n'.format(bh_number, prefix, borehole['x']))
                out_file.write('borehole_{0}.Head = {1}\n'.format(bh_number, borehole['Head']))
                out_file.write("{0}.rename(borehole_{1}, '{2}')\n".format(prefix, bh_number, borehole['name']))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_layer(file, prefix, layer_number, identification, line_marker = '####END_OF_SOIL_LAYERS####') :
    """ Write out adding a soil layer to input file
    """
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##SOIL_LAYER ({0}): Layer {1}\n'.format(identification, layer_number))
                f.write(prefix + '.soillayer(0)\n\n')
                f.write(line_marker + '\n')
            else:
                f.write(line)


def add_layer_values(file, prefix, borehole_number, layer_number, layer_top, layer_bottom, line_marker = '####END_OF_SOIL_LAYERS####'):
    """ Write out adding a layer to input file
    """
    # borehole_number starting from 1, layer_number starting from 0
    # layer_top and layer_bottom are levels
    borehole = 'borehole_' + str(borehole_number)
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write(prefix + '.setsoillayerlevel({0}, {1}, {2})\n'.format(borehole, layer_number, layer_top))
                f.write(prefix + '.setsoillayerlevel({0}, {1}, {2})\n\n'.format(borehole, layer_number+1, layer_bottom))
                f.write(line_marker + '\n')
            else:
                f.write(line)
        

#def update_layer_values(file, prefix, layer_polygon_id, layer_number, bh_number, bh_top, bh_bottom):
#    """ Updates layer properties
#    """
#    filetemp = 'temp.txt'
#    line_marker = '##SOIL_LAYER ({0}): Layer {1}'.format(layer_polygon_id, layer_number)
#    with open(file) as in_file, open(filetemp, 'w+') as out_file:
#        while True:
#            line = in_file.readline()
#            if not line: 
#                break
#            elif line.split() == []:
#                out_file.write(line)
#            elif line.strip() == line_marker:               
#                out_file.write(line) # keep marker line
#                out_file.write(in_file.readline())   # keep line 1
#                out_file.write(in_file.readline())   # keep line 2
#                in_file.readline() # line 3 is ignored
#                in_file.readline() # line 4 is ignored
#                out_file.write('{0}.setsoillayerlevel(borehole_{1}, {2}, {3})\n'.format(prefix, bh_number, layer_number - 1, bh_top))
#                out_file.write('{0}.setsoillayerlevel(borehole_{1}, {2}, {3})\n'.format(prefix, bh_number, layer_number, bh_bottom))
#              
#            else:
#                out_file.write(line)
#    
#    # overwrite filename
#    shutil.move(filetemp, file)


def assign_soil_to_layer(file, prefix, layer_number, material_name, json_file, line_marker = '####END_OF_SOIL_MATERIALS####'):
    """ Block of Python scripting code for assiging soil properties to a layer
    """    
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##MATERIAL: Assign {0} to layer {1}\n'.format(material_name, layer_number))
                f.write("with open(r'{}', 'r') as f:\n".format(json_file))
                f.write('\t material_parameters = json.load(f)\n')
                f.write('params = material_parameters.items()\n')
                f.write('soil_{0} = {1}.soilmat(*params)\n'.format(material_name.replace('.',''), prefix)) # material name without '.'
                f.write('{0}.Soils[{1}].setmaterial(soil_{2})\n\n'.format(prefix, int(layer_number) - 1, material_name.replace('.',''))) # material name without '.'
                f.write(line_marker + '\n')
            else:
                f.write(line)
        

def add_wall(file, prefix, new_wall, wall_name, json_file, line_marker = '####END_OF_STRUCTURES####'):
    """ Block of Python scripting code for adding a wall structure
        using 2D plate
    """
    x1, y1 = new_wall['point1']
    x2, y2 = new_wall['point2']
    pos_interf = new_wall['interf_pos']
    neg_interf = new_wall['interf_neg']
    
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                 f.write('##WALL ({0}) with properties defined in {1}\n'.format(new_wall['id'], wall_name))
                 f.write('point1 = {0}.point({1}, {2})\n'.format(prefix, x1, y1))
                 f.write('point2 = {0}.point({1}, {2})\n'.format(prefix, x2, y2))
                 f.write('line_{1} = {0}.line(point1, point2)\n'.format(prefix, new_wall['id']))
                 f.write('plate_{0} = {1}.plate(line_{0})\n'.format(new_wall['id'], prefix))
                 f.write('pos_interf = {}\n'.format(pos_interf))
                 f.write('neg_interf = {}\n'.format(neg_interf))
                 f.write('if pos_interf: {0}.posinterface(line_{1})\n'.format(prefix, new_wall['id']))
                 f.write('if neg_interf: {0}.neginterface(line_{1})\n'.format(prefix, new_wall['id']))
                 f.write('try:\n')
                 f.write('\t wall_{0}\n'.format(new_wall['id']))
                 f.write('except NameError:\n')
                 f.write("\t with open(r'{}', 'r') as f:\n".format(json_file))
                 f.write('\t\t wall_parameters = json.load(f)\n')
                 f.write('\t params = wall_parameters.items()\n')
                 f.write('\t wall_{0} = {1}.platemat(*params)\n'.format(new_wall['id'], prefix))
                 f.write('plate_{0}.setmaterial(wall_{0})\n\n'.format(new_wall['id']))
                 f.write(line_marker + '\n')
            else:
                f.write(line)


def update_wall(file, prefix, wall):
    """ Updates wall bottom
    """
    filetemp = 'temp.txt'
    line_marker = '##WALL ({})'.format(wall['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip()[:15] == line_marker:               
                in_file.readline() # line 1 is ignored
                in_file.readline() # line 2 is ignored
                out_file.write(line) # keep marker line
                out_file.write('point1 = {0}.point({1}, {2})\n'.format(prefix, wall['point1'][0], wall['point1'][1]))
                out_file.write('point2 = {0}.point({1}, {2})\n'.format(prefix, wall['point2'][0], wall['point2'][1]))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def remove_structure(file, structure_id, signature, num_lines):
    """ Remove structure by deleting a number of lines beginning with signature
    Signature is a string
    """
    
    filetemp = 'temp.txt'
    
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == signature: 
                if structure_id == int(line.partition(signature + ' (')[2].partition(')')[0]):           
                    for _ in range(num_lines):
                        in_file.readline()
                
                else:
                    out_file.write(line)
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)
    

def remove_structure_string_id(file, structure_id, signature, num_lines):
    """ Remove structure by deleting a number of lines beginning with signature
    Signature is a string
    structure_id is a string instead of integer
    """
    
    filetemp = 'temp.txt'
    
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == signature: 
                if structure_id == line.partition(signature + ' (')[2].partition(')')[0]:           
                    for _ in range(num_lines):
                        in_file.readline()
                
                else:
                    out_file.write(line)
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def remove_structure_inbetween(file, structure_id, signature_start, signature_end):
    """ Remove structure by deleting a number of lines in between the signatures
    Signature is a string
    """
    
    filetemp = 'temp.txt'
    
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == signature_start: 
                if structure_id == int(line.partition(signature_start + ' (')[2].partition(')')[0]):           
                    while line.split()[0] != signature_end:
                        line = in_file.readline()
                    in_file.readline()

                
                else:
                    out_file.write(line)
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)

         
def unassign_soil_layer(filename, layer_number):
    """ Unassign soil layer by excluding the layer's corresponding text
    """
    filetemp = 'temp.txt'
    with open(filename) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == '##MATERIAL:': 
                material_lines = []
                #read the next 5 lines
                for _ in range(5):
                    material_lines.append(in_file.readline())

                found_layer_number = material_lines[-1].partition('Soils[')[2].partition('].')[0]
                                
                if found_layer_number != str(layer_number):
                    out_file.write(line)
                    for material_line in material_lines:
                        out_file.write(material_line)
                
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, filename)       

def add_ground_anchor(file, prefix, new_anchor, strand_file_path, grout_file_path, line_marker = '####END_OF_STRUCTURES####'):
    """ Add a ground anchor
    """
    x = new_anchor['position'][0]
    y = new_anchor['position'][1]
    angle = new_anchor['angle']
    length_free = new_anchor['length_free']
    length_fixed = new_anchor['length_fixed']
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##GROUND_ANCHOR ({})\n'.format(new_anchor['id']))
                f.write('Strand_{0}, Groutbody_{1} = make_ground_anchor({2}, {3}, {4}, {5}, {6})\n' \
                        .format(new_anchor['id'], new_anchor['id'], x, y, angle, length_free, length_fixed))
                f.write('try:\n')
                f.write('\t strand_{0}\n'.format(new_anchor['id']))
                f.write('except NameError:\n')
                f.write("\t with open(r'{}', 'r') as f:\n".format(strand_file_path))
                f.write('\t\t strand_parameters = json.load(f)\n')
                f.write('\t params = strand_parameters.items()\n')
                f.write('\t strand_{0} = {1}.anchormat(*params)\n'.format(new_anchor['id'], prefix))
                f.write('Strand_{0}.Material = strand_{0}\n'.format(new_anchor['id']))
                
                f.write('try:\n')
                f.write('\t grout_{0}\n'.format(new_anchor['id']))
                f.write('except NameError:\n')
                f.write("\t with open(r'{}', 'r') as f:\n".format(grout_file_path))
                f.write('\t\t grout_parameters = json.load(f)\n')
                f.write('\t params = grout_parameters.items()\n')
                f.write('\t grout_{0} = {1}.embeddedbeammat(*params)\n'.format(new_anchor['id'], prefix))
                f.write('Groutbody_{0}.Material = grout_{0}\n\n'.format(new_anchor['id']))
                f.write(line_marker + '\n')
            else:
                f.write(line)


def update_ground_anchor(file, prefix, anchor):
    """ Updates ground anchor
    """
    filetemp = 'temp.txt'
    line_marker = '##GROUND_ANCHOR ({})'.format(anchor['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                out_file.write(line) # keep marker line
                out_file.write('Strand_{0}, Groutbody_{0} = make_ground_anchor({1}, {2}, {3}, {4}, {5})\n' \
                        .format(anchor['id'], anchor['position'][0], anchor['position'][1], anchor['angle'], anchor['length_free'], anchor['length_fixed']))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)
    

def update_strut(file, prefix, strut):
    """ Updates strut
    """
    filetemp = 'temp.txt'
    line_marker = '##STRUT ({})'.format(strut['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                in_file.readline() # line 2 is ignored
                in_file.readline() # line 3 is ignored
                in_file.readline() # line 4 is ignored
                out_file.write(line) # keep marker line
                out_file.write('point1 = {0}.point({1}, {2})\n'.format(prefix, strut['position'][0], strut['position'][1]))
                out_file.write('Strut_{0} = {1}.fixedendanchor(point1)\n'.format(strut['id'], prefix))
                out_file.write('Strut_{0}.Direction_x = {1}\n'.format(strut['id'], strut['direct_x'] ))
                out_file.write('Strut_{0}.Direction_y = {1}\n'.format(strut['id'], strut['direct_y'] ))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_strut(file, prefix, new_strut, strut_file_path, line_marker = '####END_OF_STRUCTURES####'):
    x = new_strut['position'][0]
    y = new_strut['position'][1]
    direct_x = new_strut['direct_x']
    direct_y = new_strut['direct_y']
    
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##STRUT ({})\n'.format(new_strut['id']))
                f.write('point1 = {0}.point({1}, {2})\n'.format(prefix, x, y))
                f.write('Strut_{0} = {1}.fixedendanchor(point1)\n'.format(new_strut['id'], prefix))
                f.write('Strut_{0}.Direction_x = {1}\n'.format(new_strut['id'],direct_x ))
                f.write('Strut_{0}.Direction_y = {1}\n'.format(new_strut['id'],direct_y ))
                f.write('try:\n')
                f.write('\t strut_{0}\n'.format(new_strut['id']))
                f.write('except NameError:\n')
                f.write("\t with open(r'{}', 'r') as f:\n".format(strut_file_path))
                f.write('\t\t strut_parameters = json.load(f)\n')
                f.write('\t params = strut_parameters.items()\n')
                f.write('\t strut_{0} = {1}.anchormat(*params)\n'.format(new_strut['id'], prefix))
                f.write('Strut_{0}.Material = strut_{0}\n\n'.format(new_strut['id']))
                f.write(line_marker + '\n')
            else:
                f.write(line)

def add_lineload(file, prefix, lineload, line_marker = '####END_OF_STRUCTURES####'):
    x1 = lineload['point1'][0]
    y1 = lineload['point1'][1]
    x2 = lineload['point2'][0]
    y2 = lineload['point2'][1]
    qx = lineload['qx']
    qy = lineload['qy']
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##LINELOAD ({})\n'.format(lineload['id']))
                f.write('point1 = {0}.point({1}, {2})\n'.format(prefix, x1, y1))
                f.write('point2 = {0}.point({1}, {2})\n'.format(prefix, x2, y2))
                f.write('line1 = {0}.line(point1, point2)\n'.format(prefix))
                f.write('Lineload_{0} = {1}.lineload(line1)\n'.format(lineload['id'], prefix))
                f.write('Lineload_{0}.qx_start = {1}\n'.format(lineload['id'], qx))
                f.write('Lineload_{0}.qy_start = {1}\n\n'.format(lineload['id'], qy))
                f.write(line_marker + '\n')
            else:
                f.write(line)

def update_lineload(file, prefix, lineload):
    """ Updates line load
    """
    x1 = lineload['point1'][0]
    y1 = lineload['point1'][1]
    x2 = lineload['point2'][0]
    y2 = lineload['point2'][1]
    qx = lineload['qx']
    qy = lineload['qy']
    filetemp = 'temp.txt'
    line_marker = '##LINELOAD ({})'.format(lineload['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                for _ in range(6):  # 6 lines are skipped
                    in_file.readline()
                out_file.write(line) # keep marker line
                out_file.write('point1 = {0}.point({1}, {2})\n'.format(prefix, x1, y1))
                out_file.write('point2 = {0}.point({1}, {2})\n'.format(prefix, x2, y2))
                out_file.write('line1 = {0}.line(point1, point2)\n'.format(prefix))
                out_file.write('Lineload_{0} = {1}.lineload(line1)\n'.format(lineload['id'], prefix))
                out_file.write('Lineload_{0}.qx_start = {1}\n'.format(lineload['id'], qx))
                out_file.write('Lineload_{0}.qy_start = {1}\n'.format(lineload['id'], qy))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_pointload(file, prefix, pointload, line_marker = '####END_OF_STRUCTURES####'):
    x = pointload['point'][0]
    y = pointload['point'][1]
    Fx = pointload['Fx']
    Fy = pointload['Fy']
    
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##POINTLOAD ({})\n'.format(pointload['id']))
                f.write('point = {0}.point({1}, {2})\n'.format(prefix, x, y))
                f.write('Pointload_{0} = {1}.pointload(point)\n'.format(pointload['id'], prefix))
                f.write('Pointload_{0}.Fx = {1}\n'.format(pointload['id'], Fx))
                f.write('Pointload_{0}.Fy = {1}\n\n'.format(pointload['id'], Fy))
                f.write(line_marker + '\n')
            else:
                f.write(line)


def update_pointload(file, prefix, pointload):
    """ Updates line load
    """
    x = pointload['point'][0]
    y = pointload['point'][1]
    Fx = pointload['Fx']
    Fy = pointload['Fy']
    filetemp = 'temp.txt'
    line_marker = '##POINTLOAD ({})'.format(pointload['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                for _ in range(4):  # 4 lines are skipped
                    in_file.readline()
                out_file.write(line) # keep marker line
                out_file.write('point = {0}.point({1}, {2})\n'.format(prefix, x, y))
                out_file.write('Pointload_{0} = {1}.pointload(point)\n'.format(pointload['id'], prefix))
                out_file.write('Pointload_{0}.Fx = {1}\n'.format(pointload['id'], Fx))
                out_file.write('Pointload_{0}.Fy = {1}\n'.format(pointload['id'], Fy))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_soilcluster(file, prefix, soilcluster, json_file=None, line_marker='####END_OF_STRUCTURES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##SOIL_CLUSTER ({})\n'.format(soilcluster['id']))
                f.write('pointTL = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointTL'][0], soilcluster['pointTL'][1]))
                f.write('pointTR = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointTR'][0], soilcluster['pointTR'][1]))
                f.write('pointBR = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointBR'][0], soilcluster['pointBR'][1]))
                f.write('pointBL = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointBL'][0], soilcluster['pointBL'][1]))
                f.write('Polygon_{0}, Soil_{0}  = {1}.polygon(pointTL, pointTR, pointBR, pointBL)\n\n'.format(soilcluster['id'], prefix))
                
                f.write(line_marker + '\n')
            else:
                f.write(line)


def update_soilcluster(file, prefix, soilcluster):
    """ Updates strut
    """
    filetemp = 'temp.txt'
    line_marker = '##SOIL_CLUSTER ({})'.format(soilcluster['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                in_file.readline() # line 2 is ignored
                in_file.readline() # line 3 is ignored
                in_file.readline() # line 4 is ignored
                out_file.write(line) # keep marker line
                out_file.write('pointTL = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointTL'][0], soilcluster['pointTL'][1]))
                out_file.write('pointTR = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointTR'][0], soilcluster['pointTR'][1]))
                out_file.write('pointBR = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointBR'][0], soilcluster['pointBR'][1]))
                out_file.write('pointBL = {0}.point({1}, {2})\n'.format(prefix, soilcluster['pointBL'][0], soilcluster['pointBL'][1]))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_soilcluster_multi_points(file, prefix, soilcluster, json_file=None, line_marker = '####END_OF_STRUCTURES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##SOIL_CLUSTER ({})\n'.format(soilcluster['id']))
                f.write('\n')
                f.write('\n')
                f.write('\n')
                f.write('\n')
                f.write('Polygon_{0}, Soil_{0}  = {1}.polygon({2})\n\n'.format(soilcluster['id'], prefix, ', '.join(repr(e) for e in soilcluster['points'])))

                f.write(line_marker + '\n')
            else:
                f.write(line)


def add_polygon(file, prefix, polygon, json_file, line_marker = '####END_OF_STRUCTURES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##SOIL_POLYGON ({})\n'.format(polygon['id']))
                #f.write('points = []\n')
                #f.write('for point in {}:\n'.format(polygon['points']))
                #f.write('\t point_new = {0}.point(point[0], point[1])\n'.format(prefix))
                #f.write('\t points.append(point_new)\n')                
                f.write('Polygon_{0}, Soil_{0}  = {1}.polygon({2})\n'.format(polygon['id'], prefix, ', '.join(repr(e) for e in polygon['points'])))
                f.write('try:\n')
                f.write('\t soil_{}\n'.format(polygon['soilmaterial'].replace('.','')))
                f.write('except NameError:\n')
                f.write("\t with open(r'{}', 'r') as f:\n".format(json_file))
                f.write('\t\t soil_parameters = json.load(f)\n')
                f.write('\t params = soil_parameters.items()\n')
                f.write('\t soil_{0} = {1}.soilmat(*params)\n'.format(polygon['soilmaterial'].replace('.',''), prefix))
                f.write('Soil_{0}.Material = soil_{1}\n\n'.format(polygon['id'], polygon['soilmaterial'].replace('.','')))
                f.write(line_marker + '\n')
            else:
                f.write(line)

def add_polygon_initial_phase(file, prefix, polygon, line_marker = '####END_OF_INITIAL_PHASE####'):     
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
            
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##SOIL_POLYGON_IN_STAGE ({})\n'.format(polygon['id']))  
                f.write('{0}.setmaterial(Polygon_{1}, {0}.InitialPhase, soil_{2})\n'.format(prefix, polygon['id'], polygon['soilmaterial'].replace('.','')))
                if 'to_deactivate' in polygon:  # temporarily used for loading legacy projects
                    if polygon['to_deactivate']:
                        f.write('{0}.deactivate(Polygon_{1}, {0}.InitialPhase)\n\n'.format(prefix, polygon['id']))
                    else:
                        f.write('\n\n')
                f.write(line_marker + '\n')
            else:
                f.write(line)

def add_waterlevel(file, prefix, waterlevel, line_marker = '####END_OF_FLOW####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##WATER_LEVEL ({})\n'.format(waterlevel['id']))
                f.write('Waterlevel_{0} = {1}.waterlevel({2}, {3}, {4}, {5})\n\n'.format(waterlevel['id'], prefix, waterlevel['pointL'][0],
                        waterlevel['pointL'][1], waterlevel['pointR'][0], waterlevel['pointR'][1]))
                f.write(line_marker + '\n')
            else:
                f.write(line)        


def update_waterlevel(file, prefix, waterlevel):
    """ Updates level for a user defined water
    """
    filetemp = 'temp.txt'
    line_marker = '##WATER_LEVEL ({})'.format(waterlevel['id'])
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.strip() == line_marker:               
                in_file.readline() # line 1 is ignored
                out_file.write(line) # keep marker line
                out_file.write('Waterlevel_{0} = {1}.waterlevel({2}, {3}, {4}, {5})\n'.format(waterlevel['id'], prefix, waterlevel['pointL'][0],
                        waterlevel['pointL'][1], waterlevel['pointR'][0], waterlevel['pointR'][1]))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_drain(file, prefix, drain, line_marker = '####END_OF_STRUCTURES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##DRAIN ({})\n'.format(drain['id']))
                f.write('pointL = {0}.point({1}, {2})\n'.format(prefix, drain['pointL'][0], drain['pointL'][1]))
                f.write('pointR = {0}.point({1}, {2})\n'.format(prefix, drain['pointR'][0], drain['pointR'][1]))
                f.write('line1 = {0}.line(pointL, pointR)\n'.format(prefix))
                f.write('point_wallfoot = {0}.point({1}, {2})\n'.format(prefix, drain['wallfoot'][0], drain['wallfoot'][1]))
                if drain['islefthalfmodel'] is False:
                    f.write('line2 = {0}.line(point_wallfoot, pointR)\n'.format(prefix))
                else:
                    f.write('line2 = {0}.line(point_wallfoot, pointL)\n'.format(prefix))
                f.write('{}.posinterface(line2)\n'.format(prefix))
                f.write('{}.neginterface(line2)\n'.format(prefix))
                f.write('Drain_{0} = {1}.drain(line1)\n\n'.format(drain['id'], prefix))
                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_waterlevel_automatedphases_steadystate(file, prefix, waterlevel, line_marker = '####END_OF_STRUCTURES####'):
    """ Adds a drain instead of phreatic level
    """
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##DRAIN ({})\n'.format(waterlevel['id']))
                f.write('pointL = {0}.point({1}, {2})\n'.format(prefix, waterlevel['pointL'][0], waterlevel['pointL'][1]))
                f.write('pointR = {0}.point({1}, {2})\n'.format(prefix, waterlevel['pointR'][0], waterlevel['pointR'][1]))
                f.write('line1 = {0}.line(pointL, pointR)\n'.format(prefix))
                f.write('Drain_{0} = {1}.drain(line1)\n\n'.format(waterlevel['id'], prefix))
                f.write(line_marker + '\n')
            else:
                f.write(line)        


def add_observed_points(file, prefix, points, line_marker = '####END_OF_STRUCTURES####'):
    """ Add observed points for sensitivity and back-analysis
    """
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##POINTS_OBS ({})\n'.format(points['id']))
                f.write('Points_obs_{} = []\n'.format(points['id']))
                f.write('for point in {}:\n'.format(points['points']))
                f.write('\t Points_obs_{0}.append({1}.point(point[0], point[1]))\n\n'.format(points['id'], prefix))
                f.write(line_marker + '\n')
            else:
                f.write(line) 
                

def apply_mesh(file, prefix, mesh):
    """ Apply mesh properties
    """
    element_dist = mesh['element_dist']
    is_enhanced_refinement = mesh['is_enhanced_refinement']
    
    filetemp = 'temp.txt'
    line_marker = prefix + '.gotomesh()'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == line_marker:               
                out_file.write(line)
                line1 = in_file.readline()  # reserved empty line for fine mesh
                line2 = in_file.readline()  # reserved empty line for fine mesh
                out_file.write(line1)
                out_file.write(line2)
                _ = in_file.readline()  # g_i.mesh()
                out_file.write('{0}.mesh({1}, {2})\n'.format(prefix, element_dist, is_enhanced_refinement ))
              
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_polygon_fine_mesh(file, prefix, points_fine_mesh, line_marker = '####END_OF_STRUCTURES####'):
    """ Add a polygon named Polygon_fine_mesh for refining the mesh around wall
    """
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##FINE_MESH_POLYGON (1)\n')
                f.write('Polygon_fine_mesh, _ = {0}.polygon({1})\n\n'.format(prefix, ', '.join(repr(e) for e in points_fine_mesh)))
                f.write(line_marker + '\n')
            else:
                f.write(line)


def add_polygon_fine_mesh_with_id(file, prefix, points_fine_mesh, id_fine_mesh, line_marker = '####END_OF_STRUCTURES####'):
    """ Add a polygon named Polygon_fine_mesh for refining the mesh around wall
    id_fine_mesh: string type
    """
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
        
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##FINE_MESH_POLYGON ({})\n'.format(id_fine_mesh))
                f.write('Polygon_fine_mesh_{2}, _ = {0}.polygon({1})\n\n'.format(prefix, ', '.join(repr(e) for e in points_fine_mesh), id_fine_mesh))
                f.write(line_marker + '\n')
            else:
                f.write(line)


def apply_refine_mesh_multi_polygons(file, prefix, Polygons_fine_mesh, repeat=4):
    """ Refine mesh around wall
    Polygon_fine_mesh: list of fine mesh polygons
    """
    filetemp = 'temp.txt'
    line_marker = prefix + '.gotomesh()'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == line_marker:               
                out_file.write(line)    #g_i.gotomesh()
                _ = in_file.readline()  # reserved line for fine mesh
                _ = in_file.readline()  # reserved line for fine mesh
                line_g_i_mesh = in_file.readline()
                out_file.write('for i in range({0}):\n'.format(repeat))
                out_file.write('\t {0}.refine({1})\n'.format(prefix, ', '.join(e for e in Polygons_fine_mesh)))
                out_file.write(line_g_i_mesh)    #g_i.mesh(0.06, True)
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def refine_mesh_around_wall(file, prefix, repeat=4):
    """ Refine mesh around wall
    """
    filetemp = 'temp.txt'
    line_marker = prefix + '.gotomesh()'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == line_marker:               
                out_file.write(line)    #g_i.gotomesh()
                _ = in_file.readline()  # reserved line for fine mesh
                _ = in_file.readline()  # reserved line for fine mesh
                line_g_i_mesh = in_file.readline()
                out_file.write('for i in range({0}):\n'.format(repeat))
                out_file.write('\t {0}.refine(Polygon_fine_mesh)\n'.format(prefix))
                out_file.write(line_g_i_mesh)    #g_i.mesh(0.06, True)
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def undo_refine_mesh_around_wall(file, prefix):
    """ Undo refining mesh around wall
    """
    filetemp = 'temp.txt'
    line_marker = prefix + '.gotomesh()'
    with open(file) as in_file, open(filetemp, 'w+') as out_file:
        while True:
            line = in_file.readline()
            if not line: 
                break
            elif line.split() == []:
                out_file.write(line)
            elif line.split()[0] == line_marker:               
                out_file.write(line)    # g_i.gotomesh()
                _ = in_file.readline()  # ignore the first line in for loop
                _ = in_file.readline()  # ignore the second line in for loop
                out_file.write('\n')    # write empty line
                out_file.write('\n')    # write empty line
            else:
                out_file.write(line)
    
    # overwrite filename
    shutil.move(filetemp, file)


def add_phase_wall_construction(file, prefix, new_phase, line_marker = '####END_OF_STAGES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase({2}.InitialPhase)\n'.format(new_phase['phase_id'], prefix, prefix))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Wall phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('for lineload in {}.Lineloads:\n'.format(prefix))
                f.write('\t lineload.activate(Phase_{})\n'.format(new_phase['phase_id']))
                f.write('for pointload in {}.Pointloads:\n'.format(prefix))
                f.write('\t pointload.activate(Phase_{})\n'.format(new_phase['phase_id']))
                f.write('for plate in {}.Plates:\n'.format(prefix))
                f.write('\t plate.activate(Phase_{})\n'.format(new_phase['phase_id']))
                f.write('for interface in {}.Interfaces:\n'.format(prefix))
                f.write('\t interface.activate(Phase_{})\n'.format(new_phase['phase_id']))
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line) 

def add_phase_excavation(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Excavation phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('soilclusters = []\n')
                f.write('for soilcluster_id in {}:\n'.format(new_phase['soilcluster_ids']))
                f.write("\t soilclusters.append('Polygon_' + str(soilcluster_id))\n")
                f.write('for soilcluster in soilclusters:\n')
                f.write('\t {0}.deactivate(eval(soilcluster), Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                #f.write('\t {0}.setwaterdry(eval(soilcluster), Phase_{1})\n\n'.format(prefix, new_phase['phase_id']))
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line) 

def add_phase_dewatering1(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    setdry_soilcluster_ids = new_phase['setdry_soilcluster_ids']
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Dewatering phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('soilclusters = []\n')
                f.write('for soilcluster_id in {}:\n'.format(new_phase['waterlevel_soilcluster_ids']))
                f.write("\t soilclusters.append('Polygon_' + str(soilcluster_id))\n")
                f.write('for soilcluster in soilclusters:\n')
                f.write('\t {0}.setwaterlevel(eval(soilcluster), Phase_{1}, Waterlevel_{2})\n'.format(prefix, new_phase['phase_id'], new_phase['water_level_id']))
                
                f.write('soilclusters = []\n')
                f.write('for soilcluster_id in {}:\n'.format(setdry_soilcluster_ids))
                f.write("\t soilclusters.append('Polygon_' + str(soilcluster_id))\n")
                f.write('for soilcluster in soilclusters:\n')
                f.write('\t {0}.setwaterdry(eval(soilcluster), Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_phase_dewatering1_porepressure_interpolation(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    setdry_soilcluster_ids = new_phase['setdry_soilcluster_ids']
    porepressure_interpolation_soilcluster_ids = new_phase['soilcluster_ids_porepressure_interpolation']
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Dewatering phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('soilclusters = []\n')
                f.write('for soilcluster_id in {}:\n'.format(new_phase['waterlevel_soilcluster_ids']))
                f.write("\t soilclusters.append('Polygon_' + str(soilcluster_id))\n")
                f.write('for soilcluster in soilclusters:\n')
                f.write('\t {0}.setwaterlevel(eval(soilcluster), Phase_{1}, Waterlevel_{2})\n'.format(prefix, new_phase['phase_id'], new_phase['water_level_id']))
                
                f.write('soilclusters = []\n')
                f.write('for soilcluster_id in {}:\n'.format(setdry_soilcluster_ids))
                f.write("\t soilclusters.append('Polygon_' + str(soilcluster_id))\n")
                f.write('for soilcluster in soilclusters:\n')
                f.write('\t {0}.setwaterdry(eval(soilcluster), Phase_{1})\n'.format(prefix, new_phase['phase_id']))

                f.write('soilclusters = []\n')
                f.write('for soilcluster_id in {}:\n'.format(porepressure_interpolation_soilcluster_ids))
                f.write("\t soilclusters.append('Polygon_' + str(soilcluster_id))\n")
                f.write('for soilcluster in soilclusters:\n')
                f.write('\t {0}.setwaterinterpolate(eval(soilcluster), Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_phase_dewatering2(file, prefix, new_phase, last_phase, drain_id, line_marker = '####END_OF_STAGES####'):
    drain_head = new_phase['drain_head']
    setdry_soilcluster_ids = new_phase['setdry_soilcluster_ids']
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Dewatering phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('drain_name = Drain_{}.Name.value\n'.format(drain_id))
                f.write('parentdrain = getattr({}, drain_name)\n'.format(prefix))
                f.write('for drainpart in parentdrain:\n')
                f.write('\t drainpart.activate(Phase_{0})\n'.format(new_phase['phase_id']))
                f.write('\t drainpart.h.set(Phase_{0}, {1})\n'.format(new_phase['phase_id'], drain_head))                   
                f.write('soilclusters = []\n')
                f.write('for soilcluster_id in {}:\n'.format(setdry_soilcluster_ids))
                f.write("\t soilclusters.append('Polygon_' + str(soilcluster_id))\n")
                f.write('for soilcluster in soilclusters:\n')
                f.write('\t {0}.setwaterdry(eval(soilcluster), Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("{0}.GroundwaterFlow.BoundaryXMin.set(Phase_{1}, 'Closed')\n".format(prefix, new_phase['phase_id']))
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line)                 


def add_phase_strut_construction(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Strut/slab construction phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('struts = []\n')
                f.write('F_prestress = {}\n'.format(new_phase['F_prestress']))
                f.write('for strut_id in {}:\n'.format(new_phase['strut_ids']))
                f.write("\t strut_name = 'Strut_' + str(strut_id) + '.Name.value'\n")
                f.write("\t struts.append(getattr({}, eval(strut_name)))\n".format(prefix))
                f.write('for i, strut in enumerate(struts):\n')
                f.write('\t {0}.activate(strut, Phase_{1})\n'.format(prefix, new_phase['phase_id']))               
                f.write('\t for strutpart in strut:\n')
                f.write("\t\t strutpart.AdjustPrestress.set(Phase_{0}, eval('F_prestress[i] > 10.0'))\n".format(new_phase['phase_id'])) 
                f.write('\t\t strutpart.PrestressForce.set(Phase_{0}, F_prestress[i])\n'.format(new_phase['phase_id'])) 
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line)        


def add_phase_strut_deconstruction(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Strut deconstruction phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('struts = []\n')
                f.write('for strut_id in {}:\n'.format(new_phase['strut_ids']))
                f.write("\t strut_name = 'Strut_' + str(strut_id) + '.Name.value'\n")
                f.write("\t struts.append(getattr({}, eval(strut_name)))\n".format(prefix))
                f.write('for strut in struts:\n')
                f.write('\t {0}.deactivate(strut, Phase_{1})\n'.format(prefix, new_phase['phase_id']))               
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line)        


def add_phase_anchoring(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Anchoring phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))
                f.write('strands = []\n')
                f.write('F_prestress = {}\n'.format(new_phase['F_prestress']))
                f.write('groutbodies = []\n')
                f.write('for anchor_id in {}:\n'.format(new_phase['anchor_ids']))
                f.write("\t strand_name = 'Strand_' + str(anchor_id) + '.Name.value'\n")
                f.write("\t groutbody_name = 'Groutbody_' + str(anchor_id) + '.Name.value'\n")
                f.write("\t strands.append(getattr({}, eval(strand_name)))\n".format(prefix))
                f.write("\t groutbodies.append(getattr({}, eval(groutbody_name)))\n".format(prefix))
                f.write('for i, strand in enumerate(strands):\n')
                f.write('\t for strandpart in strand:\n')
                f.write('\t\t {0}.activate(strand, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 
                f.write('\t\t strandpart.AdjustPrestress.set(Phase_{}, True)\n'.format(new_phase['phase_id'])) 
                f.write("\t\t strandpart.PrestressForce.set(Phase_{0}, F_prestress[i])\n".format(new_phase['phase_id'])) 
                f.write('for groutbody in groutbodies:\n')
                f.write('\t for groutbodypart in groutbody:\n')
                f.write('\t\t {0}.activate(groutbodypart, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 
                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line) 
                

def add_phase_safety(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = 'Safety phase {1}'\n".format(new_phase['phase_id'], new_phase['phase_id']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'On'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.MaxSteps = 400\n".format(new_phase['phase_id']))

                # DO NOT WORK YET
                #f.write('soilclusters = []\n')
                #f.write('for soilcluster_id in {}:\n'.format(new_phase['soilcluster_ids_no_strength_reduction']))
                #f.write("\t soilclusters.append('Soil_' + str(soilcluster_id))\n")
                #f.write('for soilcluster in soilclusters:\n')
                #f.write('\t eval(soilcluster).ApplyStrengthReduction(Phase_{0})\n'.format(new_phase['phase_id']))

                if new_phase['soilcluster_id_no_strength_reduction']:
                    f.write('parentsoilclusters = getattr({0}, Soil_{1}.Name.value)\n'.format(prefix, new_phase['soilcluster_id_no_strength_reduction']))
                    f.write('for soilcluster in parentsoilclusters:\n')
                    f.write('\t soilcluster.ApplyStrengthReduction.set(Phase_{0}, False)\n'.format(new_phase['phase_id']))

                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line)        


def add_combined_phase_info(file, prefix, new_phase, last_phase, line_marker = '####END_OF_STAGES####'):
    """ Adds markers and basic information of the combined phase
    """
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase(Phase_{2})\n'.format(new_phase['phase_id'], prefix, last_phase['phase_id']))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = '{1} {0}'\n".format(new_phase['phase_id'], new_phase['phase_name']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))

                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_info_initialphase(file, prefix, new_phase, line_marker = '####END_OF_STAGES####'):
    """ Adds markers and basic information of the combined phase
    """
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('##PHASE ({})\n'.format(new_phase['phase_id']))
                f.write('Phase_{0} = {1}.phase({1}.InitialPhase)\n'.format(new_phase['phase_id'], prefix))
                f.write('{0}.setcurrentphase(Phase_{1})\n'.format(prefix, new_phase['phase_id']))
                f.write("Phase_{0}.Identification = '{1} {0}'\n".format(new_phase['phase_id'], new_phase['phase_name']))
                f.write("Phase_{0}.PorePresCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['pore_pres_calc_type']))
                f.write("Phase_{0}.DeformCalcType = '{1}'\n".format(new_phase['phase_id'], new_phase['deform_calc_type']))
                f.write("Phase_{0}.LoadingType = '{1}'\n".format(new_phase['phase_id'], new_phase['loading_type']))
                f.write("Phase_{0}.Deform.ResetDisplacementsToZero = {1}\n".format(new_phase['phase_id'], new_phase['reset_displ_zero']))
                f.write("Phase_{0}.Deform.UseDefaultIterationParams = False\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.Deform.ArcLengthControl = 'Off'\n".format(new_phase['phase_id']))
                f.write("Phase_{0}.TimeInterval = {1}\n".format(new_phase['phase_id'], new_phase['time_interval']))

                f.write('##END_OF_PHASE ({})\n\n'.format(new_phase['phase_id']))
                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_walls(file, prefix, new_phase):
    """ Add wall actions
    """
    wall_ids_activate = new_phase['wall_ids_activate']
    wall_ids_deactivate = new_phase['wall_ids_deactivate']
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                if wall_ids_activate:
                    f.write('walls_activate = []\n')
                    f.write('for wall_id in {}:\n'.format(wall_ids_activate))
                    f.write("\t wall_name = 'line_' + str(wall_id) + '.Name.value'\n")
                    f.write("\t walls_activate.append(getattr({}, eval(wall_name)))\n".format(prefix))
                    f.write('for wall in walls_activate:\n')
                    f.write('\t wall.activate(Phase_{})\n'.format(new_phase['phase_id']))

                if wall_ids_deactivate:
                    f.write('walls_deactivate = []\n')
                    f.write('for wall_id in {}:\n'.format(wall_ids_deactivate))
                    f.write("\t wall_name = 'line_' + str(wall_id) + '.Name.value'\n")
                    f.write("\t walls_deactivate.append(getattr({}, eval(wall_name)))\n".format(prefix))
                    f.write('for wall in walls_deactivate:\n')
                    f.write('\t wall.deactivate(Phase_{})\n'.format(new_phase['phase_id']))

                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_lineloads(file, prefix, new_phase):
    """ Add lineload actions
    """
    lload_ids_activate = new_phase['lload_ids_activate']
    lload_ids_deactivate = new_phase['lload_ids_deactivate']
    lload_qys_new = new_phase['lload_qys_new']   # id: value
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                if lload_ids_activate:
                    f.write('lloads_activate = []\n')
                    f.write('for lload_id in {}:\n'.format(lload_ids_activate))
                    f.write("\t lload_name = 'Lineload_' + str(lload_id) + '.Name.value'\n")
                    f.write("\t lloads_activate.append(getattr({}, eval(lload_name)))\n".format(prefix))
                    f.write('for lload in lloads_activate:\n')
                    f.write('\t lload.activate(Phase_{})\n'.format(new_phase['phase_id']))

                if lload_ids_deactivate:
                    f.write('lloads_deactivate = []\n')
                    f.write('for lload_id in {}:\n'.format(lload_ids_deactivate))
                    f.write("\t lload_name = 'Lineload_' + str(lload_id) + '.Name.value'\n")
                    f.write("\t lloads_deactivate.append(getattr({}, eval(lload_name)))\n".format(prefix))
                    f.write('for lload in lloads_deactivate:\n')
                    f.write('\t lload.deactivate(Phase_{})\n'.format(new_phase['phase_id']))

                if lload_qys_new:
                    f.write('lloads_new_qy = []\n')
                    f.write('lload_qys = []\n')
                    #f.write('for scluster_id, material in {}.items():\n'.format(dict(scluster_ids_setmaterial.items())))
                    f.write('for lload_id, lload_value in {}.items():\n'.format(dict(lload_qys_new.items())))
                    f.write("\t lload_name = 'Lineload_' + str(lload_id) + '.Name.value'\n")
                    f.write("\t lloads_new_qy.append(getattr({}, eval(lload_name)))\n".format(prefix))
                    f.write("\t lload_qys.append(lload_value)\n")
                    f.write('for lload, value in zip(lloads_new_qy, lload_qys):\n')
                    f.write("\t for lload_part in lload:\n")
                    f.write('\t\t lload_part.qy_start.set(Phase_{0}, value)\n'.format(new_phase['phase_id']))

                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_pointloads(file, prefix, new_phase):
    """ Add pointload actions
    """
    pload_ids_activate = new_phase['pload_ids_activate']
    pload_ids_deactivate = new_phase['pload_ids_deactivate']
    pload_Fys_new = new_phase['pload_Fys_new']   # id: value
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                if pload_ids_activate:
                    f.write('ploads_activate = []\n')
                    f.write('for pload_id in {}:\n'.format(pload_ids_activate))
                    f.write("\t pload_name = 'Pointload_' + str(pload_id) + '.Name.value'\n")
                    f.write("\t ploads_activate.append(getattr({}, eval(pload_name)))\n".format(prefix))
                    f.write('for pload in ploads_activate:\n')
                    f.write('\t pload.activate(Phase_{})\n'.format(new_phase['phase_id']))

                if pload_ids_deactivate:
                    f.write('ploads_deactivate = []\n')
                    f.write('for pload_id in {}:\n'.format(pload_ids_deactivate))
                    f.write("\t pload_name = 'Pointload_' + str(pload_id) + '.Name.value'\n")
                    f.write("\t ploads_deactivate.append(getattr({}, eval(pload_name)))\n".format(prefix))
                    f.write('for pload in ploads_deactivate:\n')
                    f.write('\t pload.deactivate(Phase_{})\n'.format(new_phase['phase_id']))

                if pload_Fys_new:
                    f.write('ploads_new_Fy = []\n')
                    f.write('pload_Fys = []\n')
                    f.write('for pload_id, pload_value in {}.items():\n'.format(dict(pload_Fys_new.items())))
                    f.write("\t pload_name = 'Pointload_' + str(pload_id) + '.Name.value'\n")
                    f.write("\t ploads_new_Fy.append(getattr({}, eval(pload_name)))\n".format(prefix))
                    f.write("\t pload_Fys.append(pload_value)\n")
                    f.write('for pload, value in zip(ploads_new_Fy, pload_Fys):\n')
                    f.write("\t for pload_part in pload:\n")
                    f.write('\t\t pload_part.Fy.set(Phase_{0}, value)\n'.format(new_phase['phase_id']))

                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_soilclusters(file, prefix, new_phase):
    """ Add soilcluster actions
    """
    scluster_ids_activate = new_phase['scluster_ids_activate']
    scluster_ids_deactivate = new_phase['scluster_ids_deactivate']
    scluster_ids_setmaterial = new_phase['scluster_ids_setmaterial']
    scluster_ids_setdry = new_phase['scluster_ids_setdry']
    scluster_ids_interpolate = new_phase['scluster_ids_interpolate']
    #scluster_ids_interpolate = []
    path_material = new_phase['path_material']
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                if scluster_ids_activate:
                    f.write('sclusters_activate = []\n')
                    f.write('for scluster_id in {}:\n'.format(scluster_ids_activate))
                    f.write("\t scluster_name = 'Polygon_' + str(scluster_id) + '.Name.value'\n")
                    f.write("\t sclusters_activate.append(getattr({}, eval(scluster_name)))\n".format(prefix))
                    f.write('for scluster in sclusters_activate:\n')
                    f.write('\t scluster.activate(Phase_{})\n'.format(new_phase['phase_id']))

                if scluster_ids_deactivate:
                    f.write('sclusters_deactivate = []\n')
                    f.write('for scluster_id in {}:\n'.format(scluster_ids_deactivate))
                    f.write("\t scluster_name = 'Polygon_' + str(scluster_id) + '.Name.value'\n")
                    f.write("\t sclusters_deactivate.append(getattr({}, eval(scluster_name)))\n".format(prefix))
                    f.write('for scluster in sclusters_deactivate:\n')
                    f.write('\t scluster.deactivate(Phase_{})\n'.format(new_phase['phase_id']))

                if scluster_ids_setdry:
                    f.write('sclusters_setdry = []\n')
                    f.write('for scluster_id in {}:\n'.format(scluster_ids_setdry))
                    f.write("\t scluster_name = 'Polygon_' + str(scluster_id) + '.Name.value'\n")
                    f.write("\t sclusters_setdry.append(getattr({}, eval(scluster_name)))\n".format(prefix))
                    f.write('for scluster in sclusters_setdry:\n')
                    f.write('\t scluster.setwaterdry(Phase_{})\n'.format(new_phase['phase_id']))

                if scluster_ids_interpolate:
                    f.write('sclusters_interpolate = []\n')
                    f.write('for scluster_id in {}:\n'.format(scluster_ids_interpolate))
                    f.write("\t scluster_name = 'Polygon_' + str(scluster_id) + '.Name.value'\n")
                    f.write("\t sclusters_interpolate.append(getattr({}, eval(scluster_name)))\n".format(prefix))
                    f.write('for scluster in sclusters_interpolate:\n')
                    f.write('\t scluster.setwaterinterpolate(Phase_{})\n'.format(new_phase['phase_id']))

                if scluster_ids_setmaterial:
                    f.write('sclusters_setmaterial = []\n')
                    f.write('materials = []\n')
                    f.write('for scluster_id, material in {}.items():\n'.format(dict(scluster_ids_setmaterial.items())))
                    f.write("\t scluster_name = 'Soil_' + str(scluster_id) + '.Name.value'\n")
                    f.write("\t sclusters_setmaterial.append(getattr({}, eval(scluster_name)))\n".format(prefix))
                    f.write("\t materials.append(material)\n")

                    f.write('for i, scluster in enumerate(sclusters_setmaterial):\n')
                    f.write("\t json_file = os.path.join(r'{}', materials[i]) + '.json'\n".format(path_material))
                    f.write("\t with open(json_file, 'r') as f:\n")
                    f.write('\t\t soil_parameters = json.load(f)\n')
                    f.write('\t params = soil_parameters.items()\n')
                    f.write('\t material = {0}.soilmat(*params)\n'.format(prefix))
                    f.write('\t scluster.setmaterial(Phase_{0}, material)\n'.format(new_phase['phase_id']))

                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_waterlevels(file, prefix, new_phase):
    """ Add waterlevel actions
    """
    wlevel_ids_use = new_phase['wlevel_ids_use']
    scluster_ids_assign = new_phase['scluster_ids_assign']
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                for i, wlevel_id in enumerate(wlevel_ids_use):
                    f.write('sclusters_assign = []\n')
                    f.write('for scluster_id in {}:\n'.format(scluster_ids_assign[i]))
                    f.write("\t scluster_name = 'Polygon_' + str(scluster_id) + '.Name.value'\n")
                    f.write("\t sclusters_assign.append(getattr({}, eval(scluster_name)))\n".format(prefix))
                    f.write('for scluster in sclusters_assign:\n')
                    f.write('\t scluster.setwaterlevel(Phase_{0}, Waterlevel_{1})\n'.format(new_phase['phase_id'], wlevel_id))

                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_drain(file, prefix, new_phase):
    """ Add waterlevel actions
    """
    drain_head = new_phase['drain_head']
    drain_id = new_phase['drain_id']
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                f.write('drain_name = Drain_{}.Name.value\n'.format(drain_id))
                f.write('parentdrain = getattr({}, drain_name)\n'.format(prefix))
                f.write('for drainpart in parentdrain:\n')
                f.write('\t drainpart.activate(Phase_{0})\n'.format(new_phase['phase_id']))
                f.write('\t drainpart.h.set(Phase_{0}, {1})\n'.format(new_phase['phase_id'], drain_head))
                f.write("{0}.GroundwaterFlow.BoundaryXMin.set(Phase_{1}, 'Closed')\n".format(prefix, new_phase['phase_id']))

                f.write(line_marker + '\n')
            else:
                f.write(line) 


def add_combined_phase_anchors(file, prefix, new_phase):
    """ Add ground anchor actions
    """
    anchor_ids_activate = new_phase['anchor_ids_activate']
    anchor_ids_deactivate = new_phase['anchor_ids_deactivate']
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                if anchor_ids_activate: 
                    f.write('strands = []\n')
                    f.write('groutbodies = []\n')
                    f.write('F_prestress = {}\n'.format(new_phase['F_prestress']))
                    f.write('for anchor_id in {}:\n'.format(anchor_ids_activate))
                    f.write("\t strand_name = 'Strand_' + str(anchor_id) + '.Name.value'\n")
                    f.write("\t groutbody_name = 'Groutbody_' + str(anchor_id) + '.Name.value'\n")
                    f.write("\t strands.append(getattr({}, eval(strand_name)))\n".format(prefix))
                    f.write("\t groutbodies.append(getattr({}, eval(groutbody_name)))\n".format(prefix))
                    f.write('for i, strand in enumerate(strands):\n')
                    f.write('\t for strandpart in strand:\n')
                    f.write('\t\t {0}.activate(strand, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 
                    f.write('\t\t strandpart.AdjustPrestress.set(Phase_{}, True)\n'.format(new_phase['phase_id'])) 
                    f.write('\t\t strandpart.PrestressForce.set(Phase_{0}, F_prestress[i])\n'.format(new_phase['phase_id'])) 
                    f.write('for groutbody in groutbodies:\n')
                    f.write('\t for groutbodypart in groutbody:\n')
                    f.write('\t\t {0}.activate(groutbodypart, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 

                if anchor_ids_deactivate: 
                    f.write('strands = []\n')
                    f.write('groutbodies = []\n')
                    f.write('for anchor_id in {}:\n'.format(anchor_ids_deactivate))
                    f.write("\t strand_name = 'Strand_' + str(anchor_id) + '.Name.value'\n")
                    f.write("\t groutbody_name = 'Groutbody_' + str(anchor_id) + '.Name.value'\n")
                    f.write("\t strands.append(getattr({}, eval(strand_name)))\n".format(prefix))
                    f.write("\t groutbodies.append(getattr({}, eval(groutbody_name)))\n".format(prefix))
                    f.write('for i, strand in enumerate(strands):\n')
                    f.write('\t for strandpart in strand:\n')
                    f.write('\t\t {0}.deactivate(strand, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 
                    f.write('for groutbody in groutbodies:\n')
                    f.write('\t for groutbodypart in groutbody:\n')
                    f.write('\t\t {0}.deactivate(groutbodypart, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 

                f.write(line_marker + '\n')
            else:
                f.write(line)


def add_combined_phase_struts(file, prefix, new_phase):
    """ Add strut actions
    """
    strut_ids_activate = new_phase['strut_ids_activate']
    strut_ids_deactivate = new_phase['strut_ids_deactivate']
    line_marker = '##END_OF_PHASE ({})'.format(new_phase['phase_id'])
    with open(file, 'r') as in_file:
        buf = in_file.readlines()
    with open(file, 'w') as f:
        for line in buf:
            if line.strip() == line_marker:
                if strut_ids_activate: 
                    f.write('struts = []\n')
                    f.write('F_prestress = {}\n'.format(new_phase['F_prestress']))
                    f.write('for strut_id in {}:\n'.format(strut_ids_activate))
                    f.write("\t strut_name = 'Strut_' + str(strut_id) + '.Name.value'\n")
                    f.write("\t struts.append(getattr({}, eval(strut_name)))\n".format(prefix))
                    f.write('for i, strut in enumerate(struts):\n')
                    f.write('\t {0}.activate(strut, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 
                    f.write('\t for strutpart in strut:\n')
                    f.write("\t\t strutpart.AdjustPrestress.set(Phase_{0}, eval('F_prestress[i] > 10.0'))\n".format(new_phase['phase_id'])) 
                    f.write('\t\t strutpart.PrestressForce.set(Phase_{0}, F_prestress[i])\n'.format(new_phase['phase_id'])) 

                if strut_ids_deactivate: 
                    f.write('struts = []\n')
                    f.write('for strut_id in {}:\n'.format(strut_ids_deactivate))
                    f.write("\t strut_name = 'Strut_' + str(strut_id) + '.Name.value'\n")
                    f.write("\t struts.append(getattr({}, eval(strut_name)))\n".format(prefix))
                    f.write('for strut in struts:\n')
                    f.write('\t {0}.deactivate(strut, Phase_{1})\n'.format(prefix, new_phase['phase_id'])) 

                f.write(line_marker + '\n')
            else:
                f.write(line)


def remove_empty_lines(filename):
    """Overwrite the file, removing empty lines and lines that contain only whitespace."""
    with open(filename) as in_file, open(filename, 'r+') as out_file:
        out_file.writelines(line for line in in_file if line.strip())
        out_file.truncate()
        
def delete_last_lines(file, number):
    # Delete a number of last lines in file    
    count = 0
    
    with open(file,'r+b',  buffering=0) as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        while f.tell() > 0:
            f.seek(-1, os.SEEK_CUR)
            #print(f.tell())
            char = f.read(1)
            if char != b'\n' and f.tell() == end:
                #print ("No change: file does not end with a newline")
                #exit(1)
                break
            if char == b'\n':
                count += 1
            if count == number + 1:
                f.truncate()
                #print ("Removed " + str(number) + " lines from end of file")
                #exit(0)
                break
            f.seek(-1, os.SEEK_CUR)

        
#if __name__ == "__main__":
#    file = 'sample_python_model_file.py'
#    
#    set_project_properties(file, 'g_i', 'Sample project title', 'Plain strain', '15-Noded')
#    set_geometry(file, 'g_i', -15.0, -30.0, 40.0, 10.0)
#    #set_geometry(file, 'g_i', -15.0, -30.0, 40.0, 'ymax_var')
#    add_borehole(file, 'g_i', 1, 0, -5)
#    #remove_borehole(file)
#    add_layer(file, 'g_i', 1)
#    add_layer_values(file, 'g_i', 1, 0, 10, -30)
#    json_file = r'C:\Users\nya\Packages\Moniman\plaxis2d\materials\Cobbles_MC__.json'
#    assign_soil_to_layer(file, 'g_i', 1, 'Sand_MC', json_file)
#    assign_soil_to_layer(file, 'g_i', 2, 'Silt_MC', json_file)
#    unassign_soil_layer(file, 1-1)