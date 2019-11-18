#################
# This is the function of applying redshift and applying noise to a noiseless, rest-frame data.

# 2019-11-18: fixed the bug of redshift created. Change the IO package from Paradise to Astropy


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

        mean_noise = 0
        noise = np.random.normal(mean_noise, data[length,:]/noise_level, len(data[length,:]))

        new_noise_data.append(data[length,:] + noise)
        new_error_data.append(data[length,:]/noise_level)


    return new_noise_data, new_error_data



    

#########################CALL Main Fuction####################



# Main ssp_noise

PATH = '/Volumes/Transcend/pyparadise/simulation_spectra/test_noiseless/test_CB09/'
pre='test_CB09_spectra'
prefix = '_noiseless'

filename = fits.open(PATH+pre+prefix+'.fits')
rss = filename[0].data
header = filename[0].header

snr = 50.0 

data_with_noise = []

(y,x) = rss.shape

data_with_noise, data_error = apply_noise(rss, snr)

print(np.array(data_with_noise).shape)




"""

Adding redshift to the noise data

"""

z = 0.01

wave = header['CRVAL1'] + header['CDELT1'] * np.arange(header['NAXIS1'])

new_wave = apply_redshift(wave, z)

new_fwhm = float(header['SPECFWHM']) * (1+z)

print(new_fwhm)



plt.figure()
plt.plot(wave, rss[28])
plt.plot(new_wave, data_with_noise[28])
plt.show()








"""

Create the new fits file with redshift


"""

hdus = [None, None]
hdus[0] = pyfits.PrimaryHDU()
hdus[1] = pyfits.ImageHDU()
hdus[0].header = header
hdus[0].header['CRVAL1'] = new_wave[0]
hdus[0].header['CDELT1'] =  header['CDELT1'] * (1+z)
hdus[0].header['SPECFWHM'] = new_fwhm
hdus[1].header['EXTNAME'] = 'ERROR'
hdus[0].data = data_with_noise
hdus[1].data = data_error

hdu = pyfits.HDUList(hdus)
hdu.writeto(PATH+pre+'_noise50_z001_new'+'.fits', overwrite=True)


