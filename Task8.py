from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from numpy.core.fromnumeric import amax, amin
from ImageDisplayerMatplot import ImageDisplay
from math import sqrt

import os
import numpy as np

TEXT_COLOR = "color: #BCBCBC;"

PUSH_BUTTON_STYLE = """QPushButton {
    color: #BCBCBC;
    background: #0F62FE;
    border-width: 0px;
    border-color: yellow;
    border-style: solid;
    border-radius: 10px;
    min-width: 3em;
    min-height: 30px;
    padding: 6px;}
    
    QPushButton:hover {
background-color: #c2c2c2;
color: black;
}
    QPushButton:pressed {
background-color: #FFFFFF;
color: black;
}
"""

class Task8(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setContentsMargins(10,10,10,10)
        self.setLayout(self.layout_main)

        self.mean_label = QtWidgets.QLabel('Mean: ')
        self.mean_label.setFont(QFont('impact', 15))
        self.mean_label.setStyleSheet(TEXT_COLOR)

        self.segma_label = QtWidgets.QLabel('Segma: ')
        self.segma_label.setFont(QFont('impact', 15))
        self.segma_label.setStyleSheet(TEXT_COLOR)

        self.Image = ImageDisplay()

        self.NoiseImage = ImageDisplay()
        self.NoiseImage.ImageDisplayer.mousePressEvent = lambda event:self.MousePressed(event)
        self.MouseControlls = []
        self.NoiseImage.ImageDisplayer.mouseReleaseEvent = lambda event:self.MouseReleased(event)

        self.HistoImage = ImageDisplay()
        self.HistoScrollArea = QtWidgets.QScrollArea()
        self.HistoScrollArea.setWidget(self.HistoImage)

        self.CroppedImage = ImageDisplay()

        self.NoiseComboBox = QtWidgets.QComboBox()
        self.NoiseComboBox.addItems(['Gaussian', 'Uniform'])
        self.NoiseComboBox.activated[str].connect(self.select_noise)

        self.MainImage = None
        self.SlicedImage = None
        self.NoiseArray = None
        self.Histogram = None
        self.InitializeImage()
        self.select_noise('Gaussian')

        self.layout_main.addWidget(self.Image, 0,0, 2,1)
        self.layout_main.addWidget(self.NoiseComboBox, 0,1)
        self.layout_main.addWidget(self.NoiseImage, 1,1)
        self.layout_main.addWidget(self.HistoScrollArea, 2,0,3,1)
        self.layout_main.addWidget(self.CroppedImage, 2,1,)
        self.layout_main.addWidget(self.mean_label, 3,1,)
        self.layout_main.addWidget(self.segma_label, 4,1,)

    def MousePressed(self, event):
        x = event.x() 
        y = event.y() 
        if event.x()<0:
            x=0
        if event.y()<0:
            y=0
        self.MouseControlls.append([x, y])

    def MouseReleased(self, event):
        x = event.x()
        y = event.y()
        if event.x()<0:
            x=0
        if event.y()<0:
            y=0
        self.MouseControlls.append([x, y])
        self.MouseControlls = np.array(self.MouseControlls)
        print(self.MouseControlls)
        try:
            if self.MouseControlls[0][0]==self.MouseControlls[1][0] or self.MouseControlls[0][1]==self.MouseControlls[1][1]:
                self.MouseControlls = []
                return
        except:
            self.MouseControlls = []
            return
        x_min=int(amin(self.MouseControlls[:,0]))
        x_max=int(amax(self.MouseControlls[:,0]))
        y_min=int(amin(self.MouseControlls[:,1]))
        y_max=int(amax(self.MouseControlls[:,1]))
        self.MouseControlls = []
        self.SlicedImage = self.NoiseArray[y_min:y_max, x_min:x_max]
        rows, columns = self.SlicedImage.shape
        self.CroppedImage.ShowArray(self.SlicedImage, 'gray', columns, rows, 0, 255)
        self.Histogram = self.CalculateHistogram(self.SlicedImage)
        mean, segma = self.CalculateStats(self.Histogram)
        self.mean_label.setText('Mean: ' + str(mean))
        self.segma_label.setText('Segma: '+ str(segma))
        self.PlotHistogram(self.Histogram)

    def select_noise(self, text):
        noise = None
        if text =='Gaussian':
            noise = self.gaussian_noise(self.MainImage, 0, 5)
        else:
            noise =self.uniform_noise(self.MainImage, -10, 10)
        rows, columns = noise.shape
        for i in range(rows):
            for j in range(columns):
                noise[i][j] = int(np.round(noise[i][j]))
        self.NoiseArray = noise
        self.NoiseImage.ShowArray(self.NoiseArray, 'gray', columns, rows, 0, 255)
        
        
    def gaussian_noise(self, image, mue, std):
        noise = np.random.normal(loc=mue, scale=std, size=image.shape)
        # noise = self.normalize(noise)
        noisy_image = np.add(image, noise)
        noisy_image = self.normalize(noisy_image)
        return noisy_image
        
    def uniform_noise(self, image, a, b):
        noise = np.random.uniform(low=a, high=b, size=image.shape)
        # noise = self.normalize(noise)
        noisy_image = np.add(image, noise)
        noisy_image = self.normalize(noisy_image)
        return noisy_image

    def InitializeImage(self):
        image_size = 256
        square_size = 200
        radius = 80
        self.MainImage = np.full((image_size, image_size), 50)

        #creating the square in the middle
        small_square = np.full((square_size, square_size), 150)
        square_pad = (image_size-square_size)//2
        self.MainImage[square_pad:-square_pad, square_pad:-square_pad]=small_square

        #creating the circle in the middle
        radius_pad = (image_size-(2*radius))//2
        for i in range(2*radius):
            row_pad = int(sqrt(radius**2-(i-radius)**2))
            self.MainImage[radius_pad+i, (image_size//2)-row_pad:(image_size//2)+row_pad] = np.full((1,2*row_pad), 250)

        rows, columns = self.MainImage.shape
        self.Image.ShowArray(self.MainImage, 'gray', columns, rows, 0, 255)

    def CalculateHistogram(self, array):
        Rows, Columns = array.shape

        Data = {}
        for i in range(256):
            Data[i]=0
        for i in range(Rows):
            for j in range(Columns):
                Data[array[i][j]] += 1
        return Data

    def CalculateStats(self, histo):
        sum_x = 0
        sum_x2 = 0
        freq = 0
        for i in range(256):
            freq = freq + histo[i]
            sum_x = sum_x + i*histo[i]
            sum_x2 = sum_x2 + (i**2)*histo[i]
        segma = sqrt((sum_x2/freq)-(sum_x/freq)**2)
        return round(sum_x/freq,2) , round(segma,2)

    def PlotHistogram(self, histo):
        Intensities = list(histo.keys())
        Values = list(histo.values())
        self.HistoImage.PltHistogram(Intensities, Values)

    def normalize(self, image):
        minimum = amin(image)
        maximum = amax(image)
        slope = 255/(maximum-minimum)
        yint = -slope*minimum
        new_image = slope*image+yint
        return new_image

    def DeleteWidget(self):
        self.Image.deleteLater()
        self.HistoImage.deleteLater()
        self.HistoScrollArea.deleteLater()
        self.NoiseComboBox.deleteLater()
        self.NoiseImage.deleteLater()
        self.CroppedImage.deleteLater()
        self.mean_label.deleteLater()
        self.segma_label.deleteLater()
        self.layout_main.deleteLater()