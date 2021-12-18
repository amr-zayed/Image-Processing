from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
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

class BrowseWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.layout_browse = QtWidgets.QHBoxLayout()
        self.layout_browse.setContentsMargins(10,10,10,10)
        self.browse_label = QtWidgets.QLabel()
        self.browse_label = QtWidgets.QLabel("Open: ")
        self.browse_label.setFont(QFont('impact', 15))
        self.browse_label.setStyleSheet(TEXT_COLOR)

        self.browse_text = QtWidgets.QLineEdit()
        self.browse_text.setStyleSheet(TEXT_COLOR)
        self.browse_button = QtWidgets.QPushButton('Browse')
        self.browse_button.setStyleSheet(PUSH_BUTTON_STYLE)

        self.layout_browse.addWidget(self.browse_label)
        self.layout_browse.addWidget(self.browse_text)
        self.layout_browse.addWidget(self.browse_button)

        self.setLayout(self.layout_browse)
    
def FourierTransform(arr):
        """Generates the fourier magnitude and phase of the
        array

        Args:
            arr (np.ndarray): array of values from 0-255
        """
        fourier = np.fft.fft2(arr)
        fourier_shift = np.fft.fftshift(fourier)
        fourier_mag = 20*np.log(np.abs(fourier_shift))

        fourier_phase = np.angle(fourier)

        return (fourier_mag, fourier_phase)

def Convolotion(arr1, arr2, k_size):
    padding = int((k_size-1)/2)

    Rows, Columns = arr2.shape
    Rows, Columns =  Rows+padding, Columns+padding
    convolved_list = np.zeros((Rows+padding, Columns+padding))
    for i in range(padding, Rows):
        for j in range(padding, Columns):
            convolved_list[i][j] = arr2[i-padding][j-padding]

    # self.ImageEnhanced.ShowArray(convolved_list, 'gray', Rows, Columns, 0, 255)
    for i in range(padding, Rows):
        for j in range(padding, Columns):
            pixels_avg = 0
            row = i - padding
            column = j - padding
            for Ki in range(k_size):
                for Kj in range(k_size):
                    pixels_avg = pixels_avg +  convolved_list[row][column]*arr1[Ki][Kj]
                    column+=1
                row+=1
                # row = i - padding
                column = j - padding
                
            # pixels_avg = pixels_avg/(k_size*k_size)
            convolved_list[i][j]= pixels_avg
    convolved_list = convolved_list[padding:Rows,padding:Columns]
    return convolved_list