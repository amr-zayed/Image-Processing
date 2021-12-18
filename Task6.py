from PyQt5 import QtWidgets
from ImageDisplayerMatplot import ImageDisplay
from Helpers import BrowseWidget, FourierTransform
from PyQt5.QtGui import QIntValidator, QFont

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
class Task6(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setContentsMargins(10,10,10,10)
        self.setLayout(self.layout_main)

        self.BrowseWidget = BrowseWidget()
        self.BrowseWidget.browse_button.clicked.connect(lambda: self.BrowseClicked())

        self.Image = ImageDisplay()
        self.ImageScrollArea = QtWidgets.QScrollArea()
        self.ImageScrollArea.setWidget(self.Image)

        self.ImagePhase = ImageDisplay()
        self.PhaseScrollArea = QtWidgets.QScrollArea()
        self.PhaseScrollArea.setWidget(self.ImagePhase)
        
        self.ImageMag = ImageDisplay()
        self.MagScrollArea = QtWidgets.QScrollArea()
        self.MagScrollArea.setWidget(self.ImageMag)
        
        self.freq_label = QtWidgets.QLabel('Enter Frequency: ')
        self.freq_label.setFont(QFont('impact', 15))
        self.freq_label.setStyleSheet(TEXT_COLOR)
        self.Frequency = -1

        self.freq_text = QtWidgets.QLineEdit()
        self.freq_text.setValidator(QIntValidator())
        self.freq_text.setEnabled(False)
        self.freq_text.setStyleSheet("color: #BCBCBC;")

        self.ApplyButton = QtWidgets.QPushButton('Remove freq')
        self.ApplyButton.setStyleSheet(PUSH_BUTTON_STYLE)
        self.ApplyButton.clicked.connect(lambda: self.RemoveFreq())
        self.ApplyButton.setEnabled(False)

        self.layout_main.addWidget(self.BrowseWidget, 0, 0, 1,5)
        self.layout_main.addWidget(self.freq_label, 1,0)
        self.layout_main.addWidget(self.freq_text, 1,2)
        self.layout_main.addWidget(self.ApplyButton, 1,3)
        self.layout_main.addWidget(self.ImageScrollArea, 2,0,2,4)
        self.layout_main.addWidget(self.MagScrollArea, 1,4,2,1)
        self.layout_main.addWidget(self.PhaseScrollArea, 3,4)

        self.PixelsArray = None

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
        self.Transform(self.PixelsArray)
        self.freq_text.setEnabled(True)
        self.ApplyButton.setEnabled(True)
        
    def Transform(self, array):
        """Generates the fourier magnitude and phase of the
        array

        Args:
            arr (np.ndarray): array of values from 0-255
        """

        fourier_mag, fourier_phase = FourierTransform(array)
        mag_rows, mag_columns = fourier_mag.shape
        phase_rows, phase_columns = fourier_phase.shape
        print(fourier_mag)
        self.ImageMag.ShowArray(fourier_mag, 'gray', mag_columns, mag_rows, np.amin(fourier_mag), np.amax(fourier_mag))
        self.ImagePhase.ShowArray(fourier_phase, 'gray', phase_columns, phase_rows, np.amin(fourier_phase), np.amax(fourier_phase))

    def RemoveFreq(self):
        pass

    def DeleteWidget(self):
        """Deletes the widget and it's components
        """
        self.layout_main.deleteLater()
        self.BrowseWidget.deleteLater()
        
        self.Image.deleteLater()
        self.ImageScrollArea.deleteLater()
        
        self.ImagePhase.deleteLater()
        self.PhaseScrollArea.deleteLater()

        self.freq_text.deleteLater()
        self.freq_label.deleteLater()
        self.ApplyButton.deleteLater()
        self.ImageMag.deleteLater()
        self.MagScrollArea.deleteLater()