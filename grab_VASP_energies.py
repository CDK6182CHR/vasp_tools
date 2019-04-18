#!/usr/bin/env python3

__version__ = "1.0"
__author__ = "Dr. Huan Wang, email: huan.wang@whut.edu.cn"
__date__ = "2019-04-11"

"""
    This is a Python3 script for grabbing the energies in the VASP OUTCAR files
in the main project directory. The main project directory stands for the parent
directory containing several subdirectories, i.e. the structure folders of your
calculations.

To be exact, the following diagram would help to understand clearly.

The main project directory ______
                             |___ structure_01 (folder) --- OUTCAR (file)
                             |___ structure_02 (folder) --- OUTCAR (file)
                             |___ structure_03 (folder) --- OUTCAR (file)
                             |___ ...           ...     --- ...
                             |___ structure_n  (folder) --- OUTCAR (file)
                             |___ grab_VASP_energies.py (script)

##############################  target strings  ##############################

  free  energy   TOTEN  =      -443.25426460 eV

  energy  without entropy=     -443.23301459  energy(sigma->0) =     -443.24363959

##############################################################################

    The aim of this script is to grab the last TOTEN, energy without entropy, and 
energy(sigma->0) values in each OUTCAR file. Then, the script will combine all 
structure names and the corresponding energies into an "energies.csv" file.

#########################  How to Use this script  ############################

to see help:
python grab_VASP_energies.py h [OR -h OR help OR -help]

to run:
python grab_VASP_energies.py

#########################  Let's try it and enjoy! ############################
"""

from pathlib import Path, PurePath
import csv, re, sys, time


drawline = "".join(("\n", "-" * 79, "\n"))

help_str = "\n".join((drawline, "HOW TO USE THIS SCRiPT:",
                      "Go to your main project directory, then type\n",
                      "python grab_VASP_energies.py", drawline))

str_TOTEN = r"\s+free\s\senergy\s+TOTEN.*\s+([-+]?\d*\.\d+)"

str_Eentr = r"\s+energy\s\s.*entropy.*\s+([-+]?\d*\.\d+)\s+energy.*\s+([-+]?\d*\.\d+)"

pattern_TOTEN = re.compile(str_TOTEN)
pattern_Eentr = re.compile(str_Eentr)

data = []
TOTEN = []
Eentro = []
Esigma = []


def parse_OUTCAR():
    """  This function first collects all subdirectories containing the OUTCAR, 
	and then parses each OUTCAR file to find the TOTEN, energy without entropy,
	and energy(sigma->0) values in the last SCF cycle.
      Finally, all data and the corresponding filename in the current directory 
    will be combined into an energies.csv file.
	"""
    for index, fullpath in enumerate(Path.cwd().rglob("OUTCAR")):
        specie = fullpath.parts[-2]
        
        with open(fullpath, "r") as fo:
            for line in fo:
                if line.startswith("  free  energy   TOTEN"):
                    toten = re.search(pattern_TOTEN, line)
                    tot_energy = toten.group(1)
                    TOTEN.append(tot_energy)

                if line.startswith("  energy  without entropy"):
                    eentr = re.search(pattern_Eentr, line)
                    Eentropy = eentr.group(1)
                    Eentro.append(Eentropy)
                    
                    E_sigma = eentr.group(2)
                    Esigma.append(E_sigma)
            data.append([specie, TOTEN[-1], Eentro[-1], Esigma[-1]])
        print("\t".join((" ", str(index + 1), specie, "has done.")))
    #print(data)
    return data


def main():
    """
    (1) parses each OUTCAR file.
    (2) save data into an energies.csv file.
    """
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "-help", "h", "help"):
        print(help_str)
        sys.exit(0)
    else:
        initial_time = time.time()
        print(drawline)

        data = parse_OUTCAR()

        cols = ["specie", "TOTEN / eV", "E without entropy", "E(sigma->0)"]
        with open("energies.csv", "w", newline="") as fw:
            csv_out = csv.writer(fw)
            csv_out.writerow(cols)
            csv_out.writerows(data)
        total_time = time.time() - initial_time
        print(drawline)
        print("Work Completed. Used Time: {:.3f} Seconds\n".format(total_time))


if __name__ == "__main__":
    main()
