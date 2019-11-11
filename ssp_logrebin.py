import numpy as np
import astropy.io.fits as pyfits
from astropy.io import fits
import argparse
import pylab
import Paradise
import sys
from matplotlib import pyplot as plt
import statistics as stat
import os
from ppxf.ppxf_util import log_rebin
import math



PATH = '/Volumes/Transcend/pyparadise/simulation_spectra/test_RG04/test_RG04_ppxf/'
pre='test_RG04_spectra.RSS_convol2'

rss = Paradise.loadRSS(PATH+pre+'.fit')

(y,x)=rss._data.shape
#x_mid = x//2
y_mid = y//2

print(y,x)

class item:
    def __init__(self):
        self.name=[]
        #self.x = []
        self.y = []
        self.flux = []
        self.err = []
        self.wave = []
        self.specres = []
        self.lrange = []

"""
Log rebin data

"""

start_wave = min(rss._wave)
end_wave = max(rss._wave)

print(start_wave,end_wave)


dataconv = item()


for yvar in range(y):
    [specNew,logLam, velscale] = log_rebin((start_wave,end_wave), rss._data[yvar,:])
    [errNew, logLam_err, velscale_err] = log_rebin((start_wave, end_wave),(rss._error[yvar,:])**2)
    dataconv.y.append(yvar)
    dataconv.flux.append(specNew)
    dataconv.err.append(np.sqrt(errNew))
    dataconv.wave.append(np.exp(logLam))
    dataconv.specres.append(velscale)
    dataconv.lrange.append([int(min(np.exp(logLam))),math.ceil(max(np.exp(logLam)))])
                       

print(np.shape(dataconv.y))
print(np.shape(dataconv.flux))
print(np.array(dataconv.wave)[0,:]) 
print(rss._header['CRVAL1'])



"""

Create the new fits file

"""

hdu0 = pyfits.PrimaryHDU()
col1 = fits.Column(name='NAME', format = '8A',array=dataconv.name)
col2 = fits.Column(name='Y', format = 'D',array=dataconv.y)
col3 = fits.Column(name='FLUX', format='13321D',array=dataconv.flux)
col4 = fits.Column(name='ERR', format='13321D',array=dataconv.err)
col5 = fits.Column(name='WAVE', format='13321D',array=dataconv.wave)
col6 = fits.Column(name='SPECRES', format='13321D',array=dataconv.specres)
col7 = fits.Column(name='LRANGE', format='2D',array=dataconv.lrange)        
hdu1 = fits.BinTableHDU.from_columns([col1,col2,col3,col4,col5,col6,col7])

hdu = pyfits.HDUList([hdu0,hdu1])
hdu.writeto(PATH+pre+'_logrebin.fits',overwrite=True)


"""
Test a spectrum

"""

plt.figure()
plt.plot(rss._wave,rss._data[11,:],'k',label='loadCube')
plt.plot(dataconv.wave[11],dataconv.flux[11],'b',label='log-space')
plt.legend()
plt.show()

#print(max(dataconv.err[496]))
#print(max(cube._error[1:1650,8,25]))


