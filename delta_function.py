import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd



def delta_function():

    imp = signal.unit_impulse(100, 'mid') 
    
    return imp


imp=[]

wave = np.arange(400) + 4000.0


for ivar in range(4):
    imp.extend(delta_function())


plt.figure()
plt.plot(wave, imp)
plt.xlabel('wave')
plt.ylabel('Amplitude')
plt.show()
