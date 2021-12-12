from PyQt5 import QtWidgets
from ImageDisplayerMatplot import ImageDisplay
from PyQt5.QtGui import QDoubleValidator, QFont
import scipy.signal as sig
from Helpers import BrowseWidget, Convolotion

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

class Task5(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setContentsMargins(10,10,10,10)
        self.setLayout(self.layout_main)

        self.BrowseWidget = BrowseWidget()
        self.BrowseWidget.browse_button.clicked.connect(lambda: self.BrowseClicked())

        self.size_label = QtWidgets.QLabel('Enter Size: ')
        self.size_label.setFont(QFont('impact', 15))
        self.size_label.setStyleSheet(TEXT_COLOR)
        self.size = 3

        self.size_text = QtWidgets.QLineEdit()
        self.size_text.setValidator(QDoubleValidator())
        # self.size_text.setEnabled(False)
        self.size_text.setStyleSheet("color: #BCBCBC;")

        self.factor_label = QtWidgets.QLabel('Enter Factor: ')
        self.factor_label.setFont(QFont('impact', 15))
        self.factor_label.setStyleSheet(TEXT_COLOR)

        self.factor_text = QtWidgets.QLineEdit()
        self.factor_text.setValidator(QDoubleValidator())
        # self.factor_text.setEnabled(False)
        self.factor_text.setStyleSheet("color: #BCBCBC;")
        self.factor = 1

        self.layout_data_input = QtWidgets.QHBoxLayout()
        self.layout_data_input.addWidget(self.size_label)
        self.layout_data_input.addWidget(self.size_text)
        self.layout_data_input.addWidget(self.factor_label)
        self.layout_data_input.addWidget(self.factor_text)

        self.enhace_button = QtWidgets.QPushButton('Enhance Image')
        self.enhace_button.setStyleSheet(PUSH_BUTTON_STYLE)
        self.enhace_button.clicked.connect(lambda: self.Enhance())

        self.Image = ImageDisplay()
        self.ImageScrollArea = QtWidgets.QScrollArea()
        self.ImageScrollArea.setWidget(self.Image)

        self.ImageEnhanced = ImageDisplay()
        self.EnhancedScrollArea = QtWidgets.QScrollArea()
        self.EnhancedScrollArea.setWidget(self.ImageEnhanced)

        self.layout_main.addWidget(self.BrowseWidget, 0, 0, 1, 2)
        self.layout_main.addLayout(self.layout_data_input, 1, 0, 1, 2)
        self.layout_main.addWidget(self.enhace_button, 2, 0, 1, 2)
        self.layout_main.addWidget(self.ImageScrollArea, 3, 0)
        self.layout_main.addWidget(self.EnhancedScrollArea, 3, 1)
        self.PixelsArray = []
        self.Path = ''


    def BrowseClicked(self):
        """saves the image from path and creates the image info string
        """
        Imagepath = self.open_dialog_box()
        
        if not Imagepath: 
            return
        self.BrowseWidget.browse_text.insert(Imagepath[0])
        self.Path=Imagepath[0]

        try:
            self.Image.SetPath(Imagepath[0])
        except:
            self.Image.DisplayError("Corrupted File", "This file is corrupted")

        self.PixelsArray = self.Image.ToGrayScale(self.Image.PixelArray)
        Rows, Columns = self.PixelsArray.shape
        intensity_min = 0
        intensity_max = 255
        if self.PixelsArray.max()<255:
            intensity_max = self.PixelsArray.max()
        if self.PixelsArray.min()>0:
            intensity_min = self.PixelsArray.min()

        self.Image.ShowArray(self.PixelsArray, 'gray', Columns, Rows, intensity_min, intensity_max)


    def open_dialog_box(self):
        """Creates a diaglog box for the user to select file and check if it's an image

        Returns:
            [str, str]: array of the filepath path and file type
        """
        filename = QtWidgets.QFileDialog.getOpenFileName()
        Imagepath = filename[0]
        if Imagepath == '':
            return False

        Imagepath=os.path.splitext(Imagepath)
        FileTypes = ['.bmp', '.jpeg', '.jpg', '.tif']
        if Imagepath[1].lower() in FileTypes:
            return [filename[0], Imagepath[1].lower()]
        else:
            self.Image.DisplayError('file type error', 'please select a JPEG or BMP or DICOM')
            return self.open_dialog_box()

    def Enhance(self):
        if self.Path=='':
            self.Image.DisplayError('Missing Data', 'Please choose an image')
            return
        if self.size_text.text() != '':
            temp = int(self.size_text.text())
            if temp%2 == 0:
                self.Image.DisplayError('Data Error', 'Kernel size should be odd number and positive')
                return
            if temp<=0:
                self.Image.DisplayError('Data Error', 'Kernel size should positive int')
                return
            self.size = temp

        if self.factor_text.text() != '':
            self.factor = int(self.factor_text.text())
        
        Kernel = np.ones((self.size, self.size))
        convolved_image = Convolotion(Kernel, self.PixelsArray, self.size)
        temp_image = (self.PixelsArray - convolved_image)*self.factor
        temp_image = self.PixelsArray + temp_image
        rows, columns = temp_image.shape
        self.ImageEnhanced.ShowArray(convolved_image, 'gray', rows, columns, self.PixelsArray.min(), self.PixelsArray.max())

    

                        
                        

    def DeleteWidget(self):
        """Deletes the widget and it's components
        """
        self.BrowseWidget.deleteLater()
        self.Image.deleteLater()
        self.ImageEnhanced.deleteLater()
        self.ImageScrollArea.deleteLater()
        self.EnhancedScrollArea.deleteLater()
        self.size_label.deleteLater()
        self.factor_label.deleteLater()
        self.size_text.deleteLater()
        self.factor_text.deleteLater()
        self.layout_data_input.deleteLater()
        self.layout_main.deleteLater()
        self.enhace_button.deleteLater()
        
