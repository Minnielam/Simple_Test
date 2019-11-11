#################
# This is the function of applying redshift and applying noise to a noiseless, rest-frame data.

# Requirements:
# numpy
# astropy
# math
# PyParadise (optional): fits.open could work as well
# matplotlib (optional): 

#################

import numpy as np
import astropy.io.fits as pyfits
from astropy.io import fits
import Paradise
from matplotlib import pyplot as plt
import math



def apply_redshift(wave = None, redshift = None):

    """
    The fuction is applying the redshift to mock data.

    Required inputs:

    wave: input spectra wavelength, could be one spectrum or a bunch of spectra
    redshift: the redshift that would like to apply to data, could be a list or a number

    Return:

    output spectra with applying redshift

    """
   
    new_redshift_wave = wave * (1 + redshift)

    return new_redshift_wave


def apply_noise(data = None, noise_level = None):

    """
    The fuction is applying noise to spectra. In the end of function, it will return the new
    data which includes noise, and the error  

    Required inputs:
    
    data: input spectra
    noise_level: final SNR that you would like to reach

    Return:

    new_noise_data: the new output data, which includes noise = data/SNR, the distriubution of noise is a Gaussian function.
    new_error_data: the error array (noise array)

    """

    
    new_noise_data = []
    new_error_data = []

    (y,x) = data.shape

    for length in range(y):
        data_mean = np.mean(data[length,:])
        sig_data = 10 * np.log10(data_mean)

        noise_level_new = sig_data - noise_level
        noise_new = 10**(noise_level_new/10) 

        mean_noise = 0
        noise = np.random.normal(mean_noise, np.sqrt(noise_new), len(data[length,:]))

        new_noise_data.append(data[length,:] + noise)
        new_error_data.append(noise)


    return new_noise_data, new_error_data



    

#########################CALL Main Fuction####################



# Main ssp_noise

PATH = '/Volumes/Transcend/pyparadise/simulation_spectra/test_noiseless/test_CB09/'
pre='test_CB09_spectra'
prefix = '_noiseless'

rss = Paradise.loadRSS(PATH+pre+prefix+'.fits')

snr = 40.0 

data_with_noise = []

(y,x) = rss._data.shape

data_with_noise, data_error = apply_noise(rss._data, snr)

print(np.array(data_with_noise).shape)


plt.figure()
plt.plot(rss._wave,np.array(data_with_noise)[28])
plt.plot(rss._wave, rss._data[28])
plt.show()



"""

Create the new fits file

"""

hdus = [None, None]
hdus[0] = pyfits.PrimaryHDU()
hdus[1] = pyfits.ImageHDU()
hdus[0].header = rss._header
hdus[1].header['EXTNAME'] = 'ERROR'
hdus[0].data = data_with_noise
hdus[1].data = data_error

hdu = pyfits.HDUList(hdus)
hdu.writeto(PATH+pre+'_noise'+'.fits', overwrite=True)


