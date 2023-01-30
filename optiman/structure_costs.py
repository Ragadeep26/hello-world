# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:42:10 2020

@author: nya
"""


from abc import ABC, abstractmethod
import numpy as np
from tools.math import calc_dist_2p
from tools.json_functions import read_data_in_json_item
from dimensioning.py_StB.StB_R_As_and_a_s import StB_R_MN, StB_R_Q
from dimensioning.py_StB.StB_K_As_and_a_s import StB_K_MN, StB_K_Q


class Cost(ABC):
    """ Implements abstract base class for calculating structural cost
    """
    @abstractmethod
    def calculate_cost(self):
        """ This is an interface
        Concrete implementation of this method should be written in the subclasses
        """
        pass
    

class Cost_DWall(Cost):
    """ Implements the specific class for calculating cost of DWall
    """
    def __init__(self, wall, unit_costs, N, M, Q):
        self.wall = wall
        self.unit_costs = unit_costs
        self.N = N
        self.M = M
        self.Q = Q
        
    def calculate_cost(self):
        """ Calculates total cost for DWall
        """
        cost = 0.0
        cost += self.calculate_cost_concrete_volume()
        cost += self.calculate_cost_reinf()
        
        return cost
        
    
    def calculate_cost_concrete_volume(self):
        """ Calculates cost of concrete volume per cross-section linear meter
        """
        cost_concrete = 0.0
        wall_point1 = self.wall['point1']
        wall_point2 = self.wall['point2']
        wall_thickness = read_data_in_json_item(self.wall['json_item'], 'd')
        wall_length = calc_dist_2p(wall_point1, wall_point2)

        cost_concrete += wall_thickness * wall_length * self.unit_costs.concrete_volume

        return cost_concrete
        
    
    def calculate_cost_reinf(self, B=2800, dia=10, H1=100, H2=100, rho=0.78):
        """ Calculates cost of reinforcement
        D: d-wall thickness
        B: breadth of 1 barret
        dia: steel bar diameter for stirrup
        rho = 0.78 Kg/cm^3
        """
        cost_reinf = 0.0
        D = read_data_in_json_item(self.wall['json_item'], 'd') # wall thickness in meter
        A_s1, A_s2, a_s = self.get_required_reinf(self.N, self.M, self.Q, D*1000, B, H1, H2)
        ass = np.pi/4 * dia**2    #from dia of steel
        vss = rho * ass  #changing in to kg
        Asw_per_leg = a_s/6  #calculating per leg, legs = 6
        final_per_b = (Asw_per_leg/ass) * vss * ((B-0.3)*2 + (D-H1-H2)*2 + 2*(2*(0.4)+2*(D-H1-H2)))
        shearreinf_per_sqm = final_per_b/B #shear rein in kg per sqm

        verticalreinf_per_b = A_s1 + A_s2
        verticalreinf_per_sqm = (verticalreinf_per_b * rho)/B #vertical rein in kg per sqm

        wall_point1 = self.wall['point1']
        wall_point2 = self.wall['point2']
        wall_length = calc_dist_2p(wall_point1, wall_point2)

        total_rein = (shearreinf_per_sqm + verticalreinf_per_sqm) * wall_length
        #print('Total reinforcement (Kg): ', total_rein)
        cost_reinf += total_rein * self.unit_costs.steel * 0.001    # kg to ton
        
        return cost_reinf

    
    def get_required_reinf(self, N, M, Q, D, B, H1, H2, sym=True):
        """ Gets the required reinforcement
        """
        code = 2
        gam_c, gam_s = 1.5, 1.15
        gam_perm = 1.35
        f_ck = 30.0
        alpha = 0.85
        eps_c2, eps_c2u = 0.002, 0.0035
        exp = 2.0
        delta_S, delta_K = 0.18, '0.1 0.2'
        f_yk, f_tk = 500.0, 525.0
        Es = 200000.0
        eps_su = 0.025
        RissP1 = 0.0
        minBew = 0
        
        A_s1 = StB_R_MN(code, gam_c, gam_s, gam_perm*M, gam_perm*N, M, N, D, B, H1, H2, sym, 0.0, 0.0 , f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 17)
        A_s2 = StB_R_MN(code, gam_c, gam_s, gam_perm*M, gam_perm*N, M, N, D, B, H1, H2, sym, 0.0, 0.0 , f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 18)
        a_s = StB_R_Q(code, gam_c, gam_s, gam_perm*M, gam_perm*N, gam_perm*Q, D, B, H1, H2, A_s1, A_s2, f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, 0.0, 0.0, 0.0, 19)
        
        return A_s1, A_s2, a_s
    

class Cost_PWall(Cost):
    """ Implements the specific class for calculating cost of PWall
    """
    def __init__(self, wall, unit_costs, N, M, Q):
        self.wall = wall
        self.unit_costs = unit_costs
        self.N = N
        self.M = M
        self.Q = Q
        
    def calculate_cost(self):
        """ Calculates total cost for DWall
        """
        cost = 0.0
        cost += self.calculate_cost_concrete_volume()
        #print('Concrete cost:', cost)
        cost += self.calculate_cost_reinf()
        #print('Concrete & steel cost:', cost)
        
        return cost

    
    def calculate_cost_concrete_volume(self):
        """ Calculates cost of concrete volume per cross-section linear meter
        """
        cost_concrete = 0.0
        wall_point1 = self.wall['point1']
        wall_point2 = self.wall['point2']
        D = read_data_in_json_item(self.wall['json_item'], 'D')     # pile diameter
        S = read_data_in_json_item(self.wall['json_item'], 'S')     # spacing between piles
        wall_length = calc_dist_2p(wall_point1, wall_point2)

        cost_concrete += np.pi*(D**2)*1/4 * 1/S * wall_length * self.unit_costs.concrete_volume

        return cost_concrete
    
    
    def calculate_cost_reinf(self, dia=10, H=100, rho=7850):
        """ Calculates cost of reinforcement
        dia: steel bar diameter for stirrup
        rho = 7850 Kg/m^3
        """
        cost_reinf = 0.0
        D = read_data_in_json_item(self.wall['json_item'], 'D')     # pile diameter
        S = read_data_in_json_item(self.wall['json_item'], 'S')     # spacing between piles
        A_s, a_s = self.get_required_reinf(self.N, self.M, self.Q, D*1000, S, H)
        wall_point1 = self.wall['point1']
        wall_point2 = self.wall['point2']
        wall_length = calc_dist_2p(wall_point1, wall_point2)
        weight_vertical_reinf = wall_length * A_s*1e-4 * rho        # weight of vertical reinf per pile [Kg]
        perimeter = np.pi * (D - 2*(H/1000 - 10/1000)) # perimeter of the stirrup [m]
        weight_shear_reinf = wall_length * a_s*1e-4 * rho * perimeter     # weight of shear reinf per pile [Kg]
        
        weight_per_perimeter_meter = (weight_vertical_reinf + weight_shear_reinf)*1/(2*S)*1e-3 # [ton]
        
        cost_reinf += weight_per_perimeter_meter * self.unit_costs.steel
        
        return cost_reinf
    
    
    def get_required_reinf(self, N, M, Q, D, S, H, sym=True):
        """ Gets the required reinforcement
        """
        code = 3
        gam_c, gam_s = 1.5, 1.15
        gam_perm = 1.35
        f_ck = 30.0
        alpha = 0.85
        eps_c2, eps_c2u = 0.002, 0.0035
        exp = 2.0
        delta_S, delta_K = 0.18, '0.1 0.2'
        f_yk, f_tk = 500.0, 525.0
        Es = 200000.0
        eps_su = 0.025
        RissP1 = 0.0
        minBew = 0
        
        A_s = StB_K_MN(code, gam_c, gam_s, gam_perm*M*2*S, gam_perm*N*2*S, M*2*S, N*2*S, D, H, 0.0, f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, RissP1, minBew, 17)
        a_s = StB_K_Q(code, gam_c, gam_s, gam_perm*M*2*S, gam_perm*N*2*S, gam_perm*Q*2*S, D, H, float(A_s), f_ck, alpha, eps_c2, eps_c2u, exp, delta_S, delta_K, f_yk, f_tk, Es, eps_su, 0.0, 0.0, 0.0, 19)
        
        return A_s, a_s
    

class Cost_StoneColumns(Cost):
    """ Implements the specific class for calculating cost of stone columns
    """
    def __init__(self, Walls, unit_costs, sc_params, polygonPoints):
        self.sc_params = sc_params
        self.polygonPoints = polygonPoints
        self.Walls = Walls
        self.unit_costs = unit_costs
        self.N = None
        self.M = None
        self.Q = None

        
    def calculate_cost(self):
        """ Calculates total cost for DWall
        """
        cost = 0.0
        cost += self.calculate_cost_stone_volume()
        cost += self.calculate_cost_mobilization()
        for wall in self.Walls:
            cost += self.calculate_cost_reinf(wall)
        
        return cost


    def calculate_cost_stone_volume(self):
        """ Calculates cost of stones 
        """
        cost_stones = 0.0
        x_TL = self.polygonPoints[0]['point'][0]
        x_TR = self.polygonPoints[1]['point'][0]
        y_TL = self.polygonPoints[0]['point'][1]
        y_BL = self.polygonPoints[3]['point'][1]
        sc_depth = y_TL - y_BL
        sc_width = x_TR - x_TL
        Ac_over_A = self.sc_params['Ac_over_A']
        sc_volumn = (sc_width**2) * np.pi * sc_depth * Ac_over_A # volumn of stones

        cost_stones += sc_volumn*self.unit_costs.stone_columns
        return cost_stones


    def calculate_cost_mobilization(self):
        """ Calculates cost for mobilization (fixed mobilization cost)
        """

        return self.unit_costs.mobilization


    def calculate_cost_reinf(self, wall, B=1000, dia=10, H1=100, H2=100, rho=0.78):
        """ Calculates cost of reinforcement for the foundation slab
        D: d-wall thickness
        B: breadth of 1 barret
        dia: steel bar diameter for stirrup
        rho = 0.78 Kg/cm^3
        """
        cost_reinf = 0.0
        D = read_data_in_json_item(wall['json_item'], 'd') # wall thickness in meter
        A_s1, A_s2, a_s = Cost_DWall.get_required_reinf(None, self.N, self.M, self.Q, D*1000, B, H1, H2)    # from DWall
        ass = np.pi/4 * dia**2    #from dia of steel
        vss = rho * ass  #changing in to kg
        Asw_per_leg = a_s/6  #calculating per leg, legs = 6
        final_per_b = (Asw_per_leg/ass) * vss * ((B-0.3)*2 + (D-H1-H2)*2 + 2*(2*(0.4)+2*(D-H1-H2)))
        shearreinf_per_sqm = final_per_b/B #shear rein in kg per sqm

        verticalreinf_per_b = A_s1 + A_s2
        verticalreinf_per_sqm = (verticalreinf_per_b * rho)/B #vertical rein in kg per sqm

        wall_point1 = wall['point1']
        wall_point2 = wall['point2']
        wall_length = calc_dist_2p(wall_point1, wall_point2)

        total_rein = (shearreinf_per_sqm + verticalreinf_per_sqm) * wall_length * 2*np.pi
        #print('Total reinforcement (Kg): ', total_rein)
        cost_reinf += total_rein * self.unit_costs.steel * 0.001    # kg to ton
        
        return cost_reinf


class Cost_RigidInclusions(Cost):
    """ Implements the specific class for calculating cost of rigid inclusion
    """
    def __init__(self, Walls, unit_costs, FDC_params, polygonPoints):
        self.FDC_params = FDC_params
        self.polygonPoints = polygonPoints
        self.Walls = Walls
        self.unit_costs = unit_costs
        #self.N = N #to be done with plate
        #self.M = M
        #self.Q = Q

        
    def calculate_cost(self):
        """ Calculates total cost for DWall
        """
        cost = 0.0
        cost += self.calculate_cost_piles_volume()
        #for wall in self.Walls:    #to be done with plate
        #    cost += self.calculate_cost_reinf(wall)
        
        return cost


    def calculate_cost_piles_volume(self):
        """ Calculates cost of stones 
        """
        cost_piles = 0.0
        x_TL = self.polygonPoints[0]['point'][0]
        x_TR = self.polygonPoints[1]['point'][0]
        y_TL = self.polygonPoints[0]['point'][1]
        y_BL = self.polygonPoints[3]['point'][1]
        ri_depth = y_TL - y_BL
        ri_width = x_TR - x_TL
        #print(ri_width)
        Ac_over_A = (0.25 * np.pi * self.FDC_params['Dc']**2)/(self.FDC_params['a'] * self.FDC_params['a'])
        sc_volumn = ri_width**2 * np.pi * ri_depth * Ac_over_A # volumn of concrete piles

        cost_piles += sc_volumn*self.unit_costs.rigid_inclusions
        return cost_piles


class StructureCostFactory():
    """ This class implements the factory method
    """
    def get_cost_structure(self, wall_type, wall, unit_costs, N, M, Q, Walls=None, sc_params=None, polygonPoints=None):
        """ Factory method for creating a wall cost object for the wall type
        """
        if wall_type == 'DWall':
            return Cost_DWall(wall, unit_costs, N, M, Q)
        elif wall_type == 'PWall':
            #print(unit_costs)
            #print(N, M, Q)
            return Cost_PWall(wall, unit_costs, N, M, Q)
        elif wall_type == 'StoneColumns':
            return Cost_StoneColumns(Walls, unit_costs, sc_params, polygonPoints)
        elif wall_type == 'RigidInclusions':
            return Cost_RigidInclusions(Walls, unit_costs, sc_params, polygonPoints)