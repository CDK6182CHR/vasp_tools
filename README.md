# VASP Tools
---
This repository contains some tools for parsing or plotting VASP results.

## grab_VASP_energies.py

    This is a Python3 script for grabbing the energies in the VASP OUTCAR files in the main project directory. The main project directory stands for the parent directory containing several subdirectories, i.e. the structure folders of your
calculations.

To be exact, the following diagram would help to understand clearly.
```bash
The main project directory ______
                             |___ structure_01 (folder) --- OUTCAR (file)
                             |___ structure_02 (folder) --- OUTCAR (file)
                             |___ structure_03 (folder) --- OUTCAR (file)
                             |___ ...           ...     --- ...
                             |___ structure_n  (folder) --- OUTCAR (file)
                             |___ grab_VASP_energies.py (this script)
##############################  target strings  ##############################
  free  energy   TOTEN  =      -443.25426460 eV
  energy  without entropy=     -443.23301459  energy(sigma->0) =     -443.24363959
##############################################################################
    The aim of this script is to grab the last TOTEN, energy without entropy, and 
energy(sigma->0) values in each OUTCAR file. Then, the script will combine all 
structure names and the corresponding energies into an "energies.csv" file.
#########################  How to Use this script  ############################
to see help:
python grab_VASP_energies.py -h [OR --help]
to run:
python grab_VASP_energies.py
#########################  Let's try it and enjoy! ############################
```
## grad3_dev1.py

    This is a Python3 script for checking the convergency of a optimization or relaxation job in VASP based on the OUTCAR file. The script will first check the existence of the OUTCAR file, then parse the keywords in it, e.g. EDIFF, NELM, NIONS, EDIFFG, etc. Finally, the script would check the convergency based on the Total Energy and Force criteria. The report will be printed on the screen directly.

```bash
usage:

Python grad3_dev1 -o OUTCAR

```	
## band_v2.py

## dos.py `to do`
