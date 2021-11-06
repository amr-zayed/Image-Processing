from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QWidget
from PyQt5 import QtWidgets
import numpy as np
from ImageDisplayerMatplot import ImageDisplay

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
class Task2(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.layout_main = QGridLayout()
        self.layout_main.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout_main)

        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.setContentsMargins(15,15,15,0)
        self.layout_main.addLayout(self.layout_buttons,0,0)
        self.CreateImagebutton = QPushButton('Create Image')
        self.CreateImagebutton.clicked.connect(lambda: self.CreateImage())
        self.CreateImagebutton.setStyleSheet(PUSH_BUTTON_STYLE)
        self.ChangePixelsButton = QPushButton('Change Pixel Colors')
        self.ChangePixelsButton.setStyleSheet(PUSH_BUTTON_STYLE)
        self.ChangePixelsButton.clicked.connect(lambda: self.ChangePixels())
        self.ChangePixelsButton.setDisabled(True)

        self.Image=ImageDisplay()
        self.ScrollArea = QtWidgets.QScrollArea()
        self.ScrollArea.setWidget(self.Image)
        self.layout_main.addWidget(self.ScrollArea,1,0)
        self.layout_buttons.addWidget(self.CreateImagebutton)
        self.layout_buttons.addWidget(self.ChangePixelsButton)

        self.PixelArray = None

    def CreateImage(self):
        """creates a white image and shows it in GUI
        """
        width = 1080
        height = 720
        self.PixelArray = np.full((height, width, 3), 255)       
        self.Image.ShowArray(np.uint8(self.PixelArray), width=width, height=height)
        self.ChangePixelsButton.setDisabled(False)

    def ChangePixels(self):
        """change the pixels of image"""
        self.PixelArray[2,-4:] = (255,0,0)
        self.PixelArray[-4:,2] = (0,0,255)

        self.Image.ShowArray(self.PixelArray, width=1080, height=721)
        self.Image.ShowArray(self.PixelArray, width=1080, height=720)

    def DeleteWidget(self):
        """Destructs the widget
        """
        self.layout_main.deleteLater()
        self.ChangePixelsButton.deleteLater()
        self.CreateImagebutton.deleteLater()
        self.layout_buttons.deleteLater()
        self.Image.deleteLater()
        self.deleteLater()