#!/usr/bin/env python3

from pathlib import Path
import argparse as ap
import math
import numpy as np
import re
import sys


#### The patterns need to search
pattern_nions     = re.compile("NIONS\s+=\s+(\d+)")
pattern_ediff     = re.compile("EDIFF\s+=\s+(\d+\.\d+\w[-+]?\d+)")
pattern_ediffg    = re.compile("EDIFFG\s+=\s+([-+]?[\d+]?\.\d+\w[-+]?\d+)")
pattern_nelmax    = re.compile("NELM\s+=\s+(\d+)")
pattern_spin      = re.compile("ISPIN\s+=\s+(\d+)")
pattern_lorbit    = re.compile("LORBIT\s+=\s+(\d+)")

pattern_flag      = re.compile("\s+(LOOP\+:)")
pattern_timing    = re.compile("^\s+LOOP:\s+.+(\d+\.\d+$)")
pattern_energy    = re.compile("free  energy\s+\w+\s+=\s+([-+]?\d+\.\d+)")
pattern_iteration = re.compile("Iteration\s+\d+\(\s+(\d+)\)")
pattern_force     = re.compile("^\s+POSITION\s+TOTAL-FORCE")
pattern_magnetic  = re.compile("magnetization \(x\)")
pattern_volume    = re.compile("volume of cell :\s+(\d+\.\d+)")


# The ANSI colors
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'


# argument (for the input file, i.e. OUTCAR)
parser = ap.ArgumentParser(add_help=True,
                           formatter_class=ap.RawDescriptionHelpFormatter,
                           description="""
Summarize Convergency of VAPS job via OUTCAR file.

    Author:  Dr. Huan Wang
    Email:   huan.wang@whut.edu.cn
    Version: v0.1
    Date:    Jun. 13th, 2019""")
parser.add_argument("-o", metavar="OUTCAR", type=str, 
                    help="the OUTCAR file", required=True)
args = parser.parse_args()


def convert_time(time):
    """ dealing with time.
    """
    # seconds
    if time >= 60.0:
        time = time
    # minutes
    elif 60.0 < time < 3600.0:
        time = time / 60.0
    # hours
    elif 3600.0 < time < 86400: # (3600.0 * 24, i.e. day)
        time = time / 3600.0
    # days
    elif 86400.0 <= time < 2592000: # (86400 * 30, i.e. month)
        time = 86400.0
    return time


def grab_outcar(inputf):
    """  This function first checks whether the OUTCAR file exists.
    If OUTCAR exists, then read all information into a list. If not,
    closes the script and leaves a warning.
    """
    if Path(inputf).exists():
        with Path(inputf).open("r") as fo:
            info = fo.readlines()                
        return info

    else:
        sys.stderr.write("".join((FAIL, "\n")))
        sys.stderr.write(" ".join(("Could NOT open the OUTCAR file.",
                                       "Does it exist at all?")))
        sys.stderr.write("".join((ENDC, "\n")))
        sys.exit()


def grab_parameters(data_list):
    """  This function grabs ISPIN, LORBIT, EDIFF, NELM, NIONS EDIFFG, 
    and restores the rest loop information.
    """
    for index, line in enumerate(data_list):
        if pattern_spin.search(line):
            ispin = int(pattern_spin.search(line).group(1))
            print("ISPIN: {:}".format(ispin))
            
        if pattern_lorbit.search(line):
            lorbit = int(pattern_lorbit.search(line).group(1))
            print("LORBIT: {:}".format(lorbit))
            
        if pattern_ediff.search(line):
            ediff = float(pattern_ediff.search(line).group(1))
            print("EDIFF: {:}".format(ediff))
            
        if pattern_ediffg.search(line):
            ediffg = float(pattern_ediffg.search(line).group(1))
            print("EDIFFG: {:}".format(ediffg))
            
        if pattern_nelmax.search(line):
            nelmax = int(pattern_nelmax.search(line).group(1))
            print("NELM: {:}".format(nelmax))
    
        if pattern_nions.search(line):
            nions = int(pattern_nions.search(line).group(1))
            print("NIONS: {:}".format(nions))
    
        if re.compile("\s+FEWALD").search(line):
            print("OK, break")
            data = data_list[index:]
            break
            
    return data, ispin, lorbit, ediff, nelmax, nions, ediffg


def parse_outcar(data, ispin, lorbit, ediff, nelmax, atom_num, ediffg):
    """  This function parse the OUTCAR loops and check the convergency
    of the VASP job by using the Total energy and Force criteria.
    The report will be printed on the screen directly.
    """
    step    = 0
    volume  = []
    cycles  = []
    energy  = 0.0
    cputime = []

    
    for ind, line in enumerate(data):
        """
        """
        if pattern_iteration.search(line):
            cyc = int(pattern_iteration.search(line).group(1))
            cycles.append(cyc)
            
        if pattern_volume.search(line):
            vol = float(pattern_volume.search(line).group(1))
            volume.append(vol)
        
        if pattern_timing.search(line):
            seconds = float(pattern_timing.search(line).group(1))
            cputime.append(seconds)

        if pattern_energy.search(line):
            lastenergy = energy
            energy = float(pattern_energy.search(line).group(1))
            dE = math.log10(abs(energy - lastenergy + 1.0E-12))
            if (dE < ediff):
                sys.stdout.write(OKGREEN)
        
        if ispin == 2 and lorbit == 11 and pattern_magnetic.search(line):
            totmag = float(data[ind + 3 + atom_num + 2].strip().split()[-1])
        
        if pattern_force.search(line):         
            start = ind + 2
            stop  = ind + 2 + atom_num
            xyz = []
            for i in range(start, stop):
                xyz.append(data[i].strip().split()[3:])
            force = np.linalg.norm(np.array(xyz), axis=1)
            averageF = force.sum() / atom_num
            maximumF = np.max(force)
            if maximumF < abs(ediffg):
                sys.stdout.write(OKGREEN)
            else: # maximumF > abs(ediffg):
                sys.stdout.write(FAIL)
            
        if pattern_flag.search(line):
            maxscf = cycles[-1]
            if maxscf == nelmax:
                sys.stdout.write(FAIL)
            cycles = []
            volume = []
            
            time_arr = np.array(cputime).sum()
            usedtime = convert_time(time_arr)
            cputime = []
            time = 0.0
            
            step += 1
            
            if ispin == 2 and lorbit == 11:
                fmt = "  ".join(("{:>4}", "Energy:{:>11.5f}", "Log|dE|:{:> 5.1f}", 
                                 "SCF:{:>4}", "Ave|F|:{:>6.3f}", "Max|F|:{:>6.3f}", 
                                 "Vol:{:>8.2f}", "mag:{:>5.2f}", "Time:{:>6.2f}"))
                print(fmt.format(step, energy, dE, maxscf, averageF, 
                                 maximumF, vol, totmag, usedtime))
                
            else:
                fmt = "  ".join(("{:>4}","Energy:{:>11.5f}","Log|dE|:{:> 5.1f}",
                                 "SCF:{:>4}","Ave|F|:{:>6.3f}","Max|F|:{:>6.3f}",
                                 "Vol:{:>8.2f}","Time:{:>6.2f}"))
                print(fmt.format(step, energy, dE, maxscf, 
                                 averageF, maximumF, vol, usedtime))


def main(inputf):
    data = grab_outcar(inputf)
    parse_outcar(*grab_parameters(data))


if __name__ == "__main__":
    main(args.o)
    
