from PyQt5 import QtWidgets
from ImageDisplayerMatplot import ImageDisplay
from PyQt5.QtGui import QDoubleValidator, QFont
import numpy as np
from skimage.data import shepp_logan_phantom
from skimage.transform import radon, rescale, iradon

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

class Task9(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setContentsMargins(15,15,15,15)
        self.setLayout(self.layout_main)

        self.step_label = QtWidgets.QLabel('Enter Step: ')
        self.step_label.setFont(QFont('impact', 15))
        self.step_label.setStyleSheet(TEXT_COLOR)
        self.step = 0

        self.step_text = QtWidgets.QLineEdit()
        self.step_text.setValidator(QDoubleValidator())
        self.step_text.setStyleSheet("color: #BCBCBC;")
        
        self.max_label = QtWidgets.QLabel('Enter max angle: ')
        self.max_label.setFont(QFont('impact', 15))
        self.max_label.setStyleSheet(TEXT_COLOR)
        self.max = 0

        self.max_text = QtWidgets.QLineEdit()
        self.max_text.setValidator(QDoubleValidator())
        self.max_text.setStyleSheet("color: #BCBCBC;")

        self.FilterComboBox = QtWidgets.QComboBox()
        self.FilterComboBox.addItems(['No filter', 'Ram-Lak filter', 'Hamming filter'])

        self.ApplyButton = QtWidgets.QPushButton('Apply filter')
        self.ApplyButton.setStyleSheet(PUSH_BUTTON_STYLE)
        self.ApplyButton.clicked.connect(lambda: self.DisplayRadon())

        self.phantom_display = ImageDisplay()
        self.phantom_scroll = QtWidgets.QScrollArea()
        self.phantom_scroll.setWidget(self.phantom_display)

        self.sinogram_display = ImageDisplay()
        self.sinogram_scroll = QtWidgets.QScrollArea()
        self.sinogram_scroll.setWidget(self.sinogram_display)
        
        self.laminogram_display = ImageDisplay()
        self.laminogram_scroll = QtWidgets.QScrollArea()
        self.laminogram_scroll.setWidget(self.laminogram_display)

        self.CreatePhantom()

        
        self.layout_main.addWidget(self.max_label,0,0)
        self.layout_main.addWidget(self.max_text,0,1)
        self.layout_main.addWidget(QtWidgets.QWidget().setFixedWidth(20),0,2)
        self.layout_main.addWidget(self.step_label,0,3)
        self.layout_main.addWidget(self.step_text,0,4)
        self.layout_main.addWidget(QtWidgets.QWidget().setFixedWidth(20),0,5)
        self.layout_main.addWidget(self.FilterComboBox,0,6)
        self.layout_main.addWidget(self.ApplyButton,0,7)
        self.layout_main.addWidget(self.phantom_scroll,1,0,1,4)
        self.layout_main.addWidget(self.sinogram_scroll,1,4,1,4)
        self.layout_main.addWidget(self.laminogram_scroll,2,0,1,8)


    def CreatePhantom(self):
        image = shepp_logan_phantom()
        image = rescale(image, scale=0.4, mode='reflect')
        rows, columns = image.shape
        self.phantom_display.ShowArray(image, width = columns, height = rows)
        self.PixelsArray = image

    def CreateSinogram(self, theta):
        sinogram = radon(self.PixelsArray, theta=theta)
        rows, columns = self.PixelsArray.shape
        self.sinogram_display.ShowArray(sinogram, width = columns, height = rows, aspect=True)
        return sinogram
    def DisplayRadon(self):
        try:
            self.max = int(self.max_text.text())
        except:
            self.sinogram_display.DisplayError('value error', 'please enter max angle')
            return

        if not(self.max>=0 and self.max<=180):
            self.sinogram_display.DisplayError('value error', 'the maximum angle should be between 0 and 180')
            return

        try:
            self.step = int(self.step_text.text())
        except:
            self.sinogram_display.DisplayError('value error', 'please enter step')
            return

        if self.step>=self.max:
            self.sinogram_display.DisplayError('value error', 'the step should be less thant maximum angle {}'.format(self.max))
            return
        filter = ''
        if self.FilterComboBox.currentText() == 'No filter':
            filter = None
        elif self.FilterComboBox.currentText() == 'Ram-Lak filter':
            filter = 'ramp'
        elif self.FilterComboBox.currentText() == 'Hamming filter':
            filter = 'hamming'

        theta = np.linspace(0., self.max, self.max//self.step, endpoint=True)
        sinogram = self.CreateSinogram(theta=theta)
        reconstruction_fbp = iradon(sinogram, theta=theta, filter_name=filter)
        rows, columns = reconstruction_fbp.shape
        self.laminogram_display.ShowArray(reconstruction_fbp, width=columns, height=rows)

        
    def DeleteWidget(self):
        self.phantom_display.deleteLater()
        self.phantom_scroll.deleteLater()
        self.sinogram_display.deleteLater()
        self.sinogram_scroll.deleteLater()

        self.max_text.deleteLater()
        self.step_text.deleteLater()
        self.max_label.deleteLater()
        self.step_label.deleteLater()
        self.FilterComboBox.deleteLater()
        self.ApplyButton.deleteLater()
        self.layout_main.deleteLater()