# Simple_Test

The Simple_Test package contrains rountins for testing.
1. SNR_GUI_002.py 

A simple interface to check stack image and Signal-to-Noise per pixel in large IFU. 

Change list: 

V0.02 12-Dec-2019 

   - Added time consuming caculator
   
   - Added functions to load one or two cubes
   
   - Replaced SNR maps to be second flux map if two cubes are selected
    
   - Locked SNR to IMAGE1 & IMAGE 2
   
   - Changed the execution method of v0.02
   
   - How to call the script?
   
    - cube1 & cube2 have to be the same size
    
    - cube1: shall be blue (shorter wavelength)
    
    - cube2: shall be red (longer wavelength)
    
    - cube2 - cube1 == -1
    
        -- python SNR_GUI_002.py FILE_DIRECTORY FILENAME(cube1, no .fit suffix) NUMBER_OF_FILES (only accepted 1 or 2)

Required Packages:

 PyQt5.QtWidgets
 
 pyqtgraph
 
 astropy
 
 numpy
 
 argparse
 
 sys
 
 os
 
 re


How to execute?

python SNR_GUI_002.py FILE_DIRECTORY FILENAME(cube1, no .fit suffix) NUMBER_OF_FILES (only accepted 1 or 2)



2. delta_function.py
A simple delta function generator

3. ssp_logrebin.py
A simple log-rebin procedure based on ppxf package.

4. ssp_noise.py
A simple code for adding gaussian distribution noise to a noise-less spectra.
