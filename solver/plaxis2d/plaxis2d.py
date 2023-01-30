# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 10:48:58 2019

@author: nya
"""
import sys
import os
import subprocess
import numpy as np
import json
import glob
import time
from shutil import copyfile
import psutil # for check running procecesses (Plaxis2DInput.exe, Plaxis2DOutput.exe)
from collections import OrderedDict
from tools.file_tools import savetxt
from solver.plaxis2d.parameter_relations import (get_HS_moduli, get_soil_parameters_based_on_correlations_with_ve, 
                                          get_HSsmall_G0ref, get_HS_K0nc_empirical, get_psi,
                                          get_Eref_SPW, get_Eref_CPW, get_SPW_parameters, get_CPW_parameters)
from common.boilerplate import start_plaxis
from solver.plaxis2d.output_commands import get_wall_displ, get_soil_displ, get_anchor_force, get_strut_force, get_wall_hoopforce, get_msf, get_wall_internal_forces_envelope_at_points
from plxscripting.easy import new_server

PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
PLAXIS2D_SCRIPTING = sys.modules['moniman_paths']['PLAXIS2D_SCRIPTING']
#MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
#MATERIAL_LIBRARY = os.path.join(MONIMAN_OUTPUTS,'materials')

class plaxis2d():
    """ This class implements methods interfacing with PLAXIS2D Input/ Output
    """
    def calculate(self):
        """ Executes PLAXIS2D calculation by running Python script of the model'.
        Simulation result is saved in the same place
        """

        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']

        #cmd = [os.path.join(PLAXIS2D, r'python\python')]   # PLAXIS2D 2019
        cmd = [os.path.join(PLAXIS2D_SCRIPTING, r'..\..\python')]   # PLAXIS2D 2020 Connect edition

        script = os.path.join(MONIMAN_OUTPUTS, 'retaining_wall.py')
        cmd.append(script)
        
        output_database = os.path.join(MONIMAN_OUTPUTS, 'retaining_wall.p2dx')
        try: 
            os.remove(output_database)
        except OSError:
            pass
                        
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True)
        #outs, errs = p.communicate()
        p.wait()
        #p.terminate()

        #r = subprocess.check_output(cmd)   # executable crashed
        

        #if p.poll() is not None:            
        #    print('Simulation has finished, exit code: {}\n'.format(p.returncode))


    #def read_output_points(self, obs_points, obs_type, obs_phase):
    #    """ Opens database and gets requested outputs at observation points given observation type and phase
    #    """
    #    from common.boilerplate import start_plaxis
    #    from solver.plaxis2d.output_commands import get_wall_displacement_points, get_anchor_forces
    #    from plxscripting.easy import new_server
    #    
    #    # start PLAXIS Output
    #    p = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001, no_controllers=True)

    #    output_database = os.path.join(MONIMAN_OUTPUTS, 'retaining_wall.p2dx')
    #    s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
    #    s_o.open(output_database)

    #    # get wall displacements
    #    displ_wall = get_wall_displacement_points(g_o, obs_points, obs_type, obs_phase)

    #    # get anchor forces
    #    force_anchor =  get_anchor_forces(g_o, (0, 8), obs_phase)

    #    # close PLAXIS2D output object and remote server
    #    g_o.close()
    #    s_o.close()

    #    # terminate subprocess
    #    p.terminate()

    #    return np.array(displ_wall), np.array(force_anchor)
            

    def read_point_outputs(self, Points_obs, WallFootUx_Is_Zero=False):
        """ Opens PLAXIS2D output database and gets requested outputs
        Data of the requested outputs are saved back in 'data' field of Points_obs
        """
        #from common.boilerplate import start_plaxis
        #from solver.plaxis2d.output_commands import get_wall_displ, get_soil_displ, get_anchor_force, get_strut_force, get_wall_hoopforce, get_msf, get_wall_internal_forces_envelope_at_points
        #from plxscripting.easy import new_server
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        
        # start PLAXIS2D Output for the first time and do not close
        if 'Plaxis2DOutput.exe' not in (p.name() for p in psutil.process_iter()):
            # start PLAXIS2D Output
            #p = start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001, no_controllers=True)
            start_plaxis(os.path.join(PLAXIS2D, 'Plaxis2DOutput.exe'), portnr=10001, no_controllers=False)

        output_database = os.path.join(MONIMAN_OUTPUTS, 'retaining_wall.p2dx')
        s_o, g_o = new_server('localhost', 10001, password = 'mypassword')
        s_o.open(output_database)

        for obs_set in Points_obs:
            #if obs_set['data']:
            #    obs_set['data'].clear()     # clear data

            if (obs_set['obs_type'] == 'WallUx') or (obs_set['obs_type'] == 'WallUy'):
                obs_set['data'] = get_wall_displ(g_o, obs_set)
                if WallFootUx_Is_Zero: # displace WallUx by horizontal deflection at the wall toe
                    obs_set['data'] = [obs_set['data'][i] - obs_set['data'][-1] for i in range(len(obs_set['data']))]

            elif obs_set['obs_type'] == 'SoilUx' or obs_set['obs_type'] == 'SoilUy':
                obs_set['data'] = get_soil_displ(g_o, obs_set)

            elif obs_set['obs_type'] == 'WallHoopForce':
                obs_set['data'] = get_wall_hoopforce(g_o, obs_set)

            elif obs_set['obs_type'] == 'AnchorForce':
                obs_set['data'] =  get_anchor_force(g_o, obs_set)
                
            elif obs_set['obs_type'] == 'StrutForce':
                obs_set['data'] =  get_strut_force(g_o, obs_set)

            elif obs_set['obs_type'] == 'FoS':
                obs_set['data'] =  get_msf(g_o, obs_set)

            elif obs_set['obs_type'] == 'WallNxMQ_Envelope':
                #x_wall = obs_set['points'][0][0] # needed for getting internal forces on wall
                #obs_set['data'] =  get_wall_internal_forces_envelope(g_o, obs_set, x_wall)
                obs_set['data'] =  get_wall_internal_forces_envelope_at_points(g_o, obs_set)

        # close PLAXIS2D output object and remote server
        g_o.close()
        s_o.close()

        # terminate subprocess
        #p.terminate()

        #return np.array(wall_displ), np.array(soil_displ), np.array(anchor_force)


    def assign_model_parameters(self, m, Parameters, Soilmaterials):
        """ Assigns soil parameters to model
        Soilmaterials hold information such as correlations_ve which is used to check correlations b/w soil parameters
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        MATERIAL_LIBRARY = os.path.join(MONIMAN_OUTPUTS,'materials')

        cnt_para = 0
        for parameter_set in Parameters:
            soil = parameter_set['soil']
            json_file = os.path.join(MATERIAL_LIBRARY, soil + '.json')
            json_file_moniman = os.path.join(MATERIAL_LIBRARY, soil + 'moniman.json')
            with open(json_file_moniman, 'r') as file:
                data = OrderedDict(json.load(file, object_pairs_hook = OrderedDict))

            for key in parameter_set['parameter'].keys():
                data[key] = m[cnt_para]

                cnt_para += 1

            # for HS and HSsmall soil
            if 'HS' in soil:
                Eref50Oed = data['E50ref']/data['EoedRef']
                ErefUr50 = data['EurRef']/data['E50ref']
                EurRef_pre = data['EurRef'] # EurRef before updating, to calculate E_dyn/E_sta for HSsmall
                EoedRef, E50ref, EurRef = get_HS_moduli(data['ve'], data['we'], data['Pref'], Eref50Oed, ErefUr50)
                # update threee stiffness moduli
                data['EoedRef'] = EoedRef
                data['E50ref'] = E50ref
                data['EurRef'] = EurRef
                data['K0nc'], data['phi'] = get_HS_K0nc_empirical(data['phi'])

            # for HSsmall soil
            if 'HSsmall' in soil:
                G0ref = data['G0ref']
                E_dyn_over_sta = 2.4*G0ref/EurRef_pre
                #print('E_dyn_over_sta is: ', E_dyn_over_sta)
                G0ref = get_HSsmall_G0ref(EurRef, E_dyn_over_sta)
                data['G0ref'] = G0ref

            # check if correlations_ve is used
            json_item_selected = soil
            selected_soil = None
            for soilmaterial in Soilmaterials:
                if soilmaterial['json_item'] == json_item_selected:
                    selected_soil = soilmaterial
                    break
            if selected_soil['correlations_ve']:
                ve = data['ve']
                phi, we, gammaSat, gammaUnsat = get_soil_parameters_based_on_correlations_with_ve(ve)
                K0nc = 1.0 - np.sin(phi*np.pi/180)
                data['phi'] = phi
                data['K0nc'] = K0nc
                data['we'] = we
                data['powerm'] = we
                data['gammaSat'] = gammaSat
                data['gammaUnsat'] = gammaUnsat

            # apply condition for dilation angle
            data['psi'] = get_psi(data['phi'])

            with open(json_file_moniman, 'w') as file:
                json.dump(data, file)

            # remove redundant parameters and save
            data.pop('ve', None)
            data.pop('we', None)
            with open(json_file, 'w') as file:
                json.dump(data, file)
        
        return cnt_para # return the number of parameters that has been assigned to soils


    def assign_wall_parameters(self, m, Parameters_wall, cnt_para):
        """ Assigns wall parameters to model
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        MATERIAL_LIBRARY = os.path.join(MONIMAN_OUTPUTS,'materials')

        for parameter_set in Parameters_wall:
            json_item = parameter_set['json_item']
            json_file = os.path.join(MATERIAL_LIBRARY, json_item + '.json')
            json_file_moniman = os.path.join(MATERIAL_LIBRARY, json_item + 'moniman.json')
            with open(json_file_moniman, 'r') as file:
                data = OrderedDict(json.load(file, object_pairs_hook = OrderedDict))

            for key in parameter_set['parameter'].keys():
                if key == 'E':
                    Eref = m[cnt_para]  # Young's modulus
                    if parameter_set['wall_type'] == 'Dwall':
                        d, nu = data['d'], data['nu']
                        data['Gref'] = Eref/(2*(1 + nu))
                        data['EA'] = Eref*d*1.0
                        data['EA2']= data['EA']
                        data['EI'] = Eref*(d**3*1.0/12)
                    elif parameter_set['wall_type'] == 'SPW':
                        D, S, nu = data['D'], data['S'], data['nu']
                        (data['EA'], data['EA2'], data['EI'], data['w'], data['d'], data['Gref']) = get_SPW_parameters(D, S, Eref, nu)
                    elif parameter_set['wall_type'] == 'CPW':
                        D, S, nu = data['D'], data['S'], data['nu']
                        (data['EA'], data['EA2'], data['EI'], data['w'], data['d'], data['Gref']) = get_CPW_parameters(D, S, Eref, nu)

                cnt_para += 1

            with open(json_file_moniman, 'w') as file:
                json.dump(data, file)
            # remove redundant parameters and save
            data.pop('D', None)
            data.pop('S', None)
            with open(json_file, 'w') as file:
                json.dump(data, file)


    def write_output(self, dest, pnt_obs, Points_obs):
        """ Write simulation output from source to dest
        """
        # open PLAXIS2D Output and read database
        #data_sim = self.read_output_points(obs_points, obs_type, obs_phase)
        data_sim = self.read_point_outputs(Points_obs)
        savetxt(dest, data_sim)


    def write_point_outputs(self, Points_obs, path_output, suffix=''):
        """ Write all requested outputs to disc
        """
        for i, obs_set in enumerate(Points_obs):
            data = obs_set['data']
            data_type = obs_set['obs_type']
            data_phase = obs_set['obs_phase']
            # data
            dest_data = os.path.join(path_output, 'data_' + 'Obs' + str(i+1) + '_' + data_type + '_Phase' + str(data_phase) + suffix)
            savetxt(dest_data, data)
            # point coordinates
            points_x = [point[0] for point in obs_set['points']]
            points_y = [point[1] for point in obs_set['points']]
            dest_points = os.path.join(path_output, 'points_' + 'Obs' + str(i+1) + '_' + data_type + '_Phase' + str(data_phase) + suffix)
            np.savetxt(dest_points, np.c_[points_x, points_y])


    def write_point_outputs_local_sensitivity(self, Points_obs, path_output, suffix=''):
        """ Write all requested outputs to disc for local sensitivity
        """
        for i, obs_set in enumerate(Points_obs):
            data = obs_set['data']
            data_type = obs_set['obs_type']
            data_phase = obs_set['obs_phase']
            # data
            dest_data = os.path.join(path_output, 'data_phase_{0}{1}'.format(data_phase, suffix))
            savetxt(dest_data, data)
            # point coordinates
            points_x = [point[0] for point in obs_set['points']]
            points_y = [point[1] for point in obs_set['points']]
            dest_points = os.path.join(path_output, 'points_' + 'Obs' + str(i+1) + '_' + data_type + '_Phase' + str(data_phase) + suffix)
            np.savetxt(dest_points, np.c_[points_x, points_y])


    def write_point_outputs_data_type_optiman_sensitivity(self, Points_obs, path_output, suffix=''):
        """ Write all requested outputs to disc for local sensitivity without phase number
        """
        for obs_set in Points_obs:
            data = obs_set['data']
            data_type = obs_set['obs_type']
            #data_phase = str(obs_set['obs_phase'])
            # data
            #dest_data = os.path.join(path_output, 'data_' + data_type  + suffix)
            dest_data = os.path.join(path_output, 'data_' + data_type + suffix)
            savetxt(dest_data, data)
            # point coordinates
            points_x = [point[0] for point in obs_set['points']]
            points_y = [point[1] for point in obs_set['points']]
            dest_points = os.path.join(path_output, 'points_' + data_type  + suffix)
            np.savetxt(dest_points, np.c_[points_x, points_y])


    def write_point_outputs_data_type(self, Points_obs, path_output, suffix=''):
        """ Write all requested outputs to disc, being sorted by data type (used for Optiman)
        """
        for obs_set in Points_obs:
            data = obs_set['data']
            data_type = obs_set['obs_type']
            data_phase = str(obs_set['obs_phase'])
            # data
            #dest_data = os.path.join(path_output, 'data_' + data_type  + suffix)
            dest_data = os.path.join(path_output, 'data_' + data_type + '_Phase' + data_phase + suffix)
            savetxt(dest_data, data)
            # point coordinates
            points_x = [point[0] for point in obs_set['points']]
            points_y = [point[1] for point in obs_set['points']]
            dest_points = os.path.join(path_output, 'points_' + data_type  + suffix)
            np.savetxt(dest_points, np.c_[points_x, points_y])


    def write_plaxis_calc_status(self, dest):
        """ Write calculation status of PLAXIS2D Input
        """
        MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
        reg_expr = os.path.join(MONIMAN_OUTPUTS,'plaxisinfo*.txt')

        # remove plaxisinfo in dest from the previous calculation
        reg_expr_dest = dest + '_*'
        for file in glob.glob(reg_expr_dest):
            os.remove(file)

        isPassed = True
        for file in glob.glob(reg_expr):
            if 'FAILED' in file:
                source = file
                dest_extended = dest + '_FAILED'
                isPassed = False
            else:
                source = file
                dest_extended = dest + '_PASSED'

            copyfile(source, dest_extended)
            time.sleep(0.1) # wait for copying to finish

        return isPassed


if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(r'C:\Users\nya\Packages\Moniman'))
    from system.system import load_paths
    load_paths(r'..\common\\PATHS.py')
    PLAXIS2D = sys.modules['moniman_paths']['PLAXIS2D']
    print(PLAXIS2D)
    MONIMAN_OUTPUTS = sys.modules['moniman_paths']['MONIMAN_OUTPUTS']
    print(MONIMAN_OUTPUTS)
    
    pl = plaxis2d()
    pl.calculate()
    
    