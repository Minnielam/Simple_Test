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
#
##########################################


from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg

import numpy as np
import argparse
import pylab
import sys
import os
from PyAstronomy import pyasl
import numpy as np
from astropy.io import fits


class SNR_GUI(QWidget):

# load definition
    def __init__(self):
        super().__init__()
        
        parser = argparse.ArgumentParser()
        parser.add_argument('Directory', help = 'Location of files')
        parser.add_argument('GalaxyName', help = 'Name of the galaxy as in file to be used, no path is required')
        args = parser.parse_args()
        self.path = args.Directory
        self.pre = args.GalaxyName
        
        self.initUI()
    
    
    def initUI(self):
         
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        app = pg.mkQApp()

        # set windows
        self.window = pg.GraphicsWindow(title='TEST Data SNR Interface')
        self.window.resize(1200,1000)
   
        #Load paradise data, variables
        self.paradise_data()
       
        # set first image
        self.p1 = self.window.addPlot(title='FLUX')

        self.image1 = pg.ImageItem()
        self.image1.setImage(image = self.stackflux())
        self.p1.addItem(self.image1, row=0, col=0)
        self.p1.setMenuEnabled(enableMenu=False)

        # set first image control bar
        hist1 = pg.HistogramLUTItem(fillHistogram=False)
        hist1.setImageItem(self.image1)
        hist1.setLevels(-1,5)
        hist1.setHistogramRange(-1,5)
        self.window.addItem(hist1,row=0,col=1)

        # set second image
        self.p2 = self.window.addPlot(title='SNR')
        self.image2 = pg.ImageItem()
        self.image2.setImage(image = self.SNR_data())
        self.p2.addItem(self.image2, row=0, col=2)
        self.p2.setMenuEnabled(enableMenu=False)
        
        # set second image control bar

        hist2 = pg.HistogramLUTItem(fillHistogram=False)
        hist2.setImageItem(self.image2)
        hist2.setLevels(3,10)
        hist2.setHistogramRange(3,10)
        self.window.addItem(hist2,row=0,col=3)

        # set third plot

        self.p3 = self.window.addPlot(title='Input', row=1, col=0, colspan=3)
        self.p3.plot(self.cube._wave, self.cube._data[:, self.x_mid, self.y_mid]/np.median(self.cube._data[:, self.x_mid, self.y_mid]), pen=(0,0,0), name='Input')
        self.p3.setXRange(min(self.cube._wave), max(self.cube._wave))
        self.p3.setYRange(-1.0, 2.0)
        
        #cross hair and text
        self.text = pg.TextItem(anchor=(0,1),color=(255,153,51))
        self.p1.addItem(self.text)
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=(255,153,51))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=(255,153,51))
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)
        self.vb = self.p1.vb
        
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        #self.proxy1 = pg.SignalProxy(self.p1.scene().sigMouseClicked, rateLimit=60, slot=self.mouseClickImg)
        self.image1.mouseClickEvent = self.mouseClickImg

            
    
    # load data
    # Open data format which suitable for PyParadise 
    # Not the original cube
    
    
    def paradise_data(self):

        self.cube = fits.open(self.path + self.pre + '.fit')
        self.cube._data = self.cube[0].data
        self.cube._wave = self.cube[0].header['CRVAL3'] + np.arange(self.cube[0].header['NAXIS3']) * self.cube[0].header['CDELT3']
        (self.z,self.y,self.x) = self.cube._data.shape
        self.x_mid = self.x//2
        self.y_mid = self.y//2


    def stackflux(self):
        #Use white background and black foreground
        
        # Enable antialiasing
        pg.setConfigOptions(antialias=True)
        
       
        self.map=[]
        for xvar in range(self.x):
            for yvar in range(self.y):
                if self.cube._data[300, yvar, xvar] !=0:
                    snrEsti = sum(self.cube._data[:,yvar,xvar])/1e5                    
                    self.map.append(snrEsti)
                else:
                    self.map.append(0)

        self.imagesum = np.array(self.map).reshape(self.x,self.y)
        
        return self.imagesum

        
    
    # calculate SNR from PyAstronomy
    def SNR_data(self):
        
        #Use white background and black foreground
        
        # Enable antialiasing
        pg.setConfigOptions(antialias=True)
        
       
        self.snr=[]
        for xvar in range(self.x):
            for yvar in range(self.y):
                if self.cube._data[300, yvar, xvar] !=0:
                    snrEsti = np.median(self.cube._data[2000:2500,yvar,xvar])/np.std(self.cube._data[2000:2500,yvar,xvar])                   
                    self.snr.append(snrEsti)
                else:
                    self.snr.append(0)

        self.imageData = np.array(self.snr).reshape(self.x,self.y)
        
         
        return self.imageData
        
                                            
    
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.p1.vb.mapSceneToView(pos)
            indexx = int(np.floor(mousePoint.x()))
            indexy = int(np.floor(mousePoint.y()))
    
            if (indexx >= 0 and indexx <= self.x) and (indexy >= 0 and indexy <= self.y):
                self.text.setText("x=%1.0f, y=%1.0f, flux=%0.01f" % (indexx,indexy,self.imageData[indexy,indexx]))
                textposx = mousePoint.x()
                textposy = mousePoint.y()
            if (indexx > self.x_mid): #and indexx < (len(imageData)+len(imageData)*0.3)):
                 textposx = mousePoint.x() - int(self.x * 0.4)
            if (indexy > self.y - self.y * .1):
                textposy = mousePoint.y()-int(self.y * 0.1)
    
            self.text.setPos(textposx,textposy)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
    
    
    def mouseClickImg(self, event):
        pos_add = event.pos() # position of the mouse
    
        self.pixelx = int(np.floor(pos_add[int(0)]))
        self.pixely = int(np.floor(pos_add[int(1)]))
    
        self.p3.clear()
        
        #Add new data
        self.p3.setYRange(np.amin(self.cube._data[:, self.pixely, self.pixelx]), np.amax(self.cube._data[:, self.pixely, self.pixelx])) 
        self.p3.plot(self.cube._wave, self.cube._data[:, self.pixely, self.pixelx], pen=(0,0,0), name="Input")

        




# Start Qt event loop unless running in interactive mode or using pyside
if __name__ == '__main__':
    
    #Select instance of QApplication
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    #Run the GUI if being run in interactive mode
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        ex = SNR_GUI()
        sys.exit(app.exec_())
