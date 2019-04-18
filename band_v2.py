#!/usr/bin/env python

'''
This Python script "band_v2.py" organized the EIGENVAL file and saved it
to band.txt file for ploting the bands.

Authors: Yang Pei <615130174@qq.com>
         Huan Wang (2nd version)   
Create Date: 2017-03-18 18:07:16
Modified: 2017-06-14 13:57:12
Improved: 2018-09-13 11:39:30
'''

from __future__ import print_function
import numpy as np
import time

filename = input("Please Enter the File Name:\n")
E_fermi  = float(input("Please Enter the Fermi energy:\n"))

def skip_two_lines():
    try:
        for k in range(2):
            next(f)
    except StopIteration:
        exit()


def extract_data(f, n_number):
    eigenval = []
    for i in range(n_number):
        line = next(f)
        value = line.strip().split()[1]
        eigenval.append(float(value))
    return eigenval

    
with open(filename, 'r') as f:
    initial_time = time.time()
    #### to skip the first five lines 
    for n in range(5):
        next(f)
        
    info = next(f)
    NELECTRON, k_number, n_number = map(int, info.strip().split()[:3])

    eigen_array = np.zeros((k_number, n_number + 1))
    eigen_array[:,0] = np.arange(1, k_number + 1)
    
    for i in range(k_number):
        skip_two_lines()
        eigenval = extract_data(f, n_number)
        eigen_array[i, 1:] = eigenval
    eigen_array[:, 1:] = eigen_array[:, 1:] - E_fermi


output_format = ','.join(('%d', '%f,' * n_number))
np.savetxt('band.csv', eigen_array, fmt=output_format)
used_time = time.time() - initial_time
print("\nWork Completed. Used Time: {:.3e} Seconds\n".format(used_time))

