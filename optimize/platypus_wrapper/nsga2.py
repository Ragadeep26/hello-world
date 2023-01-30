# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 09:46:08 2019

@author: nya
"""
from platypus import NSGAII, DTLZ2

class NSGAII_Wrapper(NSGAII):
    """ This class extends Platypus for Optiman 
    The purpose is mainly to use NSGAII algorithm for design optimization"""
    def __init__(self, problem):
        super().__init__(problem)
        

if __name__ == '__main__':
    print('You can test something here..')
    problem = DTLZ2()
    my_nsga2 = NSGAII_Wrapper(problem)
    #print(my_nsga2.__dict__)
    my_nsga2.population_size = 50
    print(my_nsga2.population_size)
    
    my_nsga2.run(10000)
    
    # plot the results using matplotlib
    import matplotlib.pyplot as plt
    
    plt.scatter([s.objectives[0] for s in my_nsga2.result],
                [s.objectives[1] for s in my_nsga2.result])
    plt.xlim([0, 1.1])
    plt.ylim([0, 1.1])
    plt.xlabel("$f_1(x)$")
    plt.ylabel("$f_2(x)$")
    plt.show()