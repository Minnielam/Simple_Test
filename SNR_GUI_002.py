#########################################
#
# A test UI for SNR plot
# Simple plot for stack images, error images, SNR image and pure spectra
# Version: 0.01 created on 04-Nov-2019, first created by Anika Beer & Joseph, modified by Man I
#
#
# Required Packages:
# Pyqtgraph
# PyParadise
# 
# Change list:
# V0.02 12-Dec-2019 
#    - Added time consuming caculator
#    - Added functions to load one or two cubes
#    - Replaced SNR maps to be second flux map if two cubes are selected
#    - Locked SNR to IMAGE1 & IMAGE 2
#    - Changed the execution method of v0.02
#    - How to call the script?
#    - cube1 & cube2 have to be the same size
#    - cube1: shall be blue (shorter wavelength)
#    - cube2: shall be red (longer wavelength)
#    - cube2 - cube1 == -1
#        -- python SNR_GUI_002.py FILE_DIRECTORY FILENAME(cube1, no .fit suffix) NUMBER_OF_FILES (only accepted 1 or 2)
#
# To-Do List:
# Add Raise ERROR messages
# Try to make it prettier
#    
##########################################

# interface packages
from PyQt5.QtWidgets import *
import pyqtgraph as pg

# calulation packages
import numpy as np
import argparse
import sys
import os
import numpy as np
from astropy.io import fits
import re


class SNR_GUI(QWidget):

# load definition
    def __init__(self):
        super().__init__()

        # Definition of the arguments, call interface function
        
        parser = argparse.ArgumentParser()
        parser.add_argument('Directory', help = 'Location of files')
        parser.add_argument('FileName', help = 'Name of the galaxy as in file to be used, no path is required')
        parser.add_argument('Num', help = 'Number of file(s) to be used')
        args = parser.parse_args()
        self.path = args.Directory
        self.pre = args.FileName
        self.number = args.Num
        self.initUI()

    
    def initUI(self):
        
        # The major plot function, this tells you how the interface structure.
         
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        app = pg.mkQApp()

        # Enable antialiasing
        pg.setConfigOptions(antialias=True)

        # set windows
        self.window = pg.GraphicsWindow(title='TEST Data SNR Interface')
        self.window.resize(1150,1000)
   
        #Load paradise data, variables
        self.paradise_data()
       
        # set first image
        self.p1 = self.window.addPlot(title='IMAGE 1')

        self.image1 = pg.ImageItem()
        self.image1.setImage(image = self.stackflux())
        self.p1.addItem(self.image1, row=0, col=0)
        self.p1.setMenuEnabled(enableMenu=False)

        # set first image control bar
        hist1 = pg.HistogramLUTItem(fillHistogram=False)
        hist1.setImageItem(self.image1)
        hist1.setLevels(-1,10)
        hist1.setHistogramRange(-1,10)
        self.window.addItem(hist1,row=0,col=1)

        # set second image

        self.p2 = self.window.addPlot(title='IMAGE 2')
        self.image2 = pg.ImageItem()

        if self.number == 1:
            
            self.image2.setImage(image = self.SNR_data())

        else: 
            self.SNR_data_red()
            self.stackflux_red()
            self.SNR_data() 
            self.image2.setImage(image = self.stackflux_red())
            
        self.p2.addItem(self.image2, row=0, col=2)
        self.p2.setMenuEnabled(enableMenu=False)

        # set second control bar

        hist2 = pg.HistogramLUTItem(fillHistogram=False)
        hist2.setImageItem(self.image2)
        hist2.setLevels(-1,10)
        hist2.setHistogramRange(-1,10)
        self.window.addItem(hist2,row=0,col=3)

 
        
        # set third plot

        self.p3 = self.window.addPlot(title='Input', row=1, col=0, colspan=3)
        self.p3.plot(self.cube._wave, self.cube._data[:, self.y_mid, self.x_mid], pen=(0,0,0), name='Input')
        self.p3.plot(self.cube2._wave, self.cube2._data[:,self.y_mid, self.x_mid], pen=(0,153,153))
        self.p3.setXRange(min(self.cube._wave), max(self.cube._wave))
        self.p3.setYRange(np.amin(self.cube._data[:, self.y_mid, self.x_mid]), np.amax(self.cube._data[:, self.x_mid, self.x_mid])) 
        self.textposx =  0
        self.textposy = 0

        
        #cross hair and text
        self.text = pg.TextItem(anchor=(0,1),color=(255,153,51))
        self.p1.addItem(self.text)
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=(255,153,51))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=(255,153,51))
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)
        self.vb = self.p1.vb

        
        self.text2 = pg.TextItem(anchor=(0,1),color=(255,153,51))
        self.p2.addItem(self.text2)
        self.vLine2 = pg.InfiniteLine(angle=90, movable=False, pen=(255,153,51))
        self.hLine2 = pg.InfiniteLine(angle=0, movable=False, pen=(255,153,51))
        self.p2.addItem(self.vLine2, ignoreBounds=True)
        self.p2.addItem(self.hLine2, ignoreBounds=True)
        self.vb2 = self.p2.vb

        

        # executions
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=120, slot=self.mouseMoved)
        self.image1.mouseClickEvent = self.mouseClickImg

        self.proxy2 = pg.SignalProxy(self.p2.scene().sigMouseMoved, rateLimit=120, slot=self.mouseMoved)
        self.image2.mouseClickEvent = self.mouseClickImg
                
    
    def paradise_data(self):

        # load spectra
        # Now it only fit for PyParadise readable data format. 
        if self.number == str(1) or self.number == str(2):

            self.cube = fits.open(self.path + self.pre + '.fit')
            self.cube._data = np.array(list(map(lambda x: x[0] * x[1], zip(self.cube[1].data, self.cube[5].data))))
            self.cube._wave = self.cube[1].header['CRVAL3'] + np.arange(self.cube[1].header['NAXIS3']) * self.cube[1].header['CD3_3']
            (self.z,self.y,self.x) = np.array(self.cube._data).shape
            self.x_mid = self.x//2
            self.y_mid = self.y//2

        if self.number == str(2):
    
            num_fil = re.sub("\D", "", self.pre)
            self.pre2 = "stackcube_" + str(int(num_fil) - 1)
            print(self.pre2)
            self.cube2 = fits.open(self.path + self.pre2 + '.fit')
            self.cube2._data = np.array(list(map(lambda x: x[0] * x[1], zip(self.cube2[1].data, self.cube2[5].data))))
            self.cube2._wave = self.cube2[1].header['CRVAL3'] + np.arange(self.cube2[1].header['NAXIS3']) * self.cube2[1].header['CD3_3']
            (self.z2,self.y2,self.x2) = np.array(self.cube2._data).shape
            self.cube._wave = np.concatenate((self.cube._wave, self.cube2._wave), axis=0)
            self.cube._data = np.concatenate((self.cube._data, self.cube2._data), axis=0)

        print("load data: --- %s seconds ---" % (time.time() - start_time))        


    def stackflux(self):

        # Stack Image for cube 1
        # Get the collapse flux from WEAVE data

        self.map= self.cube[6].data
        self.imagesum = np.transpose(self.map)/1e5

        print("stack data cube 1: --- %s seconds ---" % (time.time() - start_time))

        
        return self.imagesum

    def stackflux_red(self):

        # Stack Image for cube2
        # Get the collapse flux

        if self.number == str(2):
            self.map2= self.cube2[6].data
            self.imagesum2 = np.transpose(self.map2)/1e5
            print("stack data cube 2: --- %s seconds ---" % (time.time() - start_time))
        else:
            self.imagesum2 = self.stackflux()
       
        print("stack data cube 2: --- %s seconds ---" % (time.time() - start_time))
        
        return self.imagesum2

    
    def SNR_data(self):

        # SNR calculation for cube1, initally it only used one number. It will be used PyAstronomy package as its final method.
        
        self.snr=[]
        for xvar in range(self.x):
            for yvar in range(self.y):
                if self.cube._data[300, yvar, xvar] !=0:
                    snrEsti = np.median(self.cube._data[1500:2000,yvar,xvar])/np.std(self.cube._data[1500:2000,yvar,xvar])                   
                    self.snr.append(snrEsti)
                else:
                    self.snr.append(0)

        self.imageData = np.array(self.snr).reshape(self.x,self.y)

        print("SNR calculation in cube 1: -- %s seconds ---" % (time.time() - start_time))
         
        return self.imageData

    def SNR_data_red(self):

        # SNR calculation for cube2, initally it only used one number. It will be used PyAstronomy package as its final method.
        if self.number == str(2):
        
            self.snr2=[]
            for xvar in range(self.x):
                for yvar in range(self.y):
                    if self.cube2._data[300, yvar, xvar] !=0:
                        snrEsti = np.median(self.cube2._data[1500:2000,yvar,xvar])/np.std(self.cube2._data[1500:2000,yvar,xvar])                   
                        self.snr2.append(snrEsti)
                    else:
                        self.snr2.append(0)
        else: 
            self.snr2 = self.SNR_data()

        self.imageData2 = np.array(self.snr2).reshape(self.x,self.y)

        print("SNR calculation in cube 2: -- %s seconds ---" % (time.time() - start_time))
         
        return self.imageData2

                                                   
    
    def mouseMoved(self, evt):

        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.p1.vb.mapSceneToView(pos)
            indexx = int(np.floor(mousePoint.x()))
            indexy = int(np.floor(mousePoint.y()))
    
            if (indexx >= 0 and indexx <= self.x) and (indexy >= 0 and indexy <= self.y):
                self.text.setText("x=%1.0f, y=%1.0f, SNR=%0.01f" % (indexx,indexy,self.imageData[indexx,indexy]))
                self.text2.setText("x=%1.0f, y=%1.0f, SNR=%0.01f" % (indexx,indexy,self.imageData2[indexx,indexy]))
                self.textposx = mousePoint.x()
                self.textposy = mousePoint.y()
            if (indexx > self.x_mid): #and indexx < (len(imageData)+len(imageData)*0.3)):
                self.textposx = mousePoint.x() - int(self.x * 0.4)
            if (indexy > self.y - self.y * .1):
                self.textposy = mousePoint.y()-int(self.y * 0.1)

            self.text.setPos(self.textposx,self.textposy)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

            self.text2.setPos(self.textposx,self.textposy)
            self.vLine2.setPos(mousePoint.x())
            self.hLine2.setPos(mousePoint.y())

    
    
    def mouseClickImg(self, event):

        pos_add = event.pos() # position of the mouse
    
        self.pixelx = int(np.floor(pos_add[int(0)]))
        self.pixely = int(np.floor(pos_add[int(1)]))
    
        self.p3.clear()
        
        #Add new data
        self.p3.setYRange(np.amin(self.cube._data[:, self.pixely, self.pixelx]), np.amax(self.cube._data[:, self.pixely, self.pixelx])) 
        self.p3.plot(self.cube._wave, self.cube._data[:, self.pixely, self.pixelx], pen=(0,0,0), name="Input")
        self.p3.plot(self.cube2._wave, self.cube2._data[:,self.pixely, self.pixelx], pen=(0,153,153))


# Start Qt event loop unless running in interactive mode or using pyside
if __name__ == '__main__':

    import time

    start_time = time.time()


    #Select instance of QApplication
    if not QApplication.instance():
        app = QApplication(sys.argv)
        
    else:
        app = QApplication.instance()
    
    #Run the GUI if being run in interactive mode
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        ex = SNR_GUI()
        print("--- %s seconds ---" % (time.time() - start_time))
        sys.exit(app.exec_())


