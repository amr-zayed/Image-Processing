from PyQt5 import QtWidgets
from numba.cuda.simulator import kernel
from numpy.core.numeric import convolve
from ImageDisplayerMatplot import ImageDisplay
from Helpers import BrowseWidget, Convolotion, FourierTransform
from PyQt5.QtGui import QDoubleValidator, QFont

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

class Task7(QtWidgets.QWidget):
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
        self.size = 0

        self.size_text = QtWidgets.QLineEdit()
        self.size_text.setValidator(QDoubleValidator())
        self.size_text.setEnabled(False)
        self.size_text.setStyleSheet("color: #BCBCBC;")

        self.ApplyButton = QtWidgets.QPushButton('Apply filter')
        self.ApplyButton.setStyleSheet(PUSH_BUTTON_STYLE)
        self.ApplyButton.clicked.connect(lambda: self.SelectFilter())
        self.ApplyButton.setEnabled(False)

        self.Image = ImageDisplay()
        self.ImageScrollArea = QtWidgets.QScrollArea()
        self.ImageScrollArea.setWidget(self.Image)

        self.ImageFourier = ImageDisplay()
        self.ImageFourierScrollArea = QtWidgets.QScrollArea()
        self.ImageFourierScrollArea.setWidget(self.ImageFourier)

        self.ImageDiff = ImageDisplay()
        self.ImageDiffScrollArea = QtWidgets.QScrollArea()
        self.ImageDiffScrollArea.setWidget(self.ImageDiff)

        self.FilterComboBox = QtWidgets.QComboBox()
        self.FilterComboBox.addItems(['Box Filter', 'Sobel Filter'])
        # self.FilterComboBox.activated[str].connect(self.SelectFilter)
        self.FilterComboBox.setEnabled(False)

        self.layout_main.addWidget(self.BrowseWidget, 0, 0, 1, 4)
        self.layout_main.addWidget(self.size_label, 1, 0)
        self.layout_main.addWidget(self.size_text, 1, 1)
        self.layout_main.addWidget(self.ApplyButton, 1, 2, 2,1)
        self.layout_main.addWidget(self.FilterComboBox, 2, 0,1,2)
        self.layout_main.addWidget(self.ImageScrollArea, 3, 0, 2, 3)
        self.layout_main.addWidget(self.ImageFourierScrollArea, 1, 3, 3, 1)
        self.layout_main.addWidget(self.ImageDiffScrollArea, 4, 3)



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

        self.Image.ShowArray(self.PixelsArray, 'gray', Columns, Rows, 0, 255)
        self.size_text.setEnabled(True)
        self.ApplyButton.setEnabled(True)
        self.FilterComboBox.setEnabled(True)

    def ApplyFilter(self, InputKernel=[]):
        if self.size_text.text() != '':
            temp = float(self.size_text.text())
            if temp%2 == 0:
                self.Image.DisplayError('Data Error', 'Kernel size should be odd int')
                return
            if temp<=0:
                self.Image.DisplayError('Data Error', 'Kernel size should be positive int')
                return
            if not(temp.is_integer()):
                self.Image.DisplayError('Data Error', 'Kernel size should be an integer')
                return
            self.size = int(temp)

            rows, columns = self.PixelsArray.shape
            if rows%2==0:
                self.PixelsArray = np.vstack((self.PixelsArray, self.PixelsArray[rows-1,:]))
                rows+=1
            if columns%2==0:
                self.PixelsArray = np.c_[self.PixelsArray, self.PixelsArray[:,columns-1]]
                columns+=1
            if self.FilterComboBox.currentText() == 'Box Filter':
                InputKernel = np.ones((self.size, self.size))
                InputKernel = InputKernel/(self.size**2)

            Kernelpad = np.zeros((rows, columns))

            col_pad = (columns-self.size)//2
            row_pad = (rows-self.size)//2
            for i in range(row_pad, row_pad+self.size-1):
                for j in range(col_pad, col_pad+self.size-1):
                    Kernelpad[i][j] = InputKernel[i-row_pad][j-col_pad]
            kernel_fourier = np.fft.fft2(Kernelpad)
            img_fourier = np.fft.fft2(self.PixelsArray)
            filteredimage = np.fft.ifft2(img_fourier*kernel_fourier)
            filteredimage = np.fft.ifftshift(filteredimage)
            filteredimage = np.abs(filteredimage)

            convolved_image = Convolotion(InputKernel, self.PixelsArray, self.size)            

            return convolved_image, filteredimage

    def SelectFilter(self):
        text = self.FilterComboBox.currentText()
        self.size = int(self.size_text.text())
        if text == 'Box Filter':
            conv_image, f_image = self.ApplyFilter()
            rows, columns = f_image.shape
            diff_image = f_image-conv_image
            self.ImageFourier.ShowArray(f_image, 'gray', columns, rows, 0, 255)
            self.ImageDiff.ShowArray(diff_image, 'gray', columns, rows, 0, 255)
        else:
            SobelFilter0 = self.custom_sobel(self.size, 0)
            SobelFilter1 = self.custom_sobel(self.size, 1)
            print(SobelFilter0)
            print(SobelFilter1)
            conv_image0, f_image0 = self.ApplyFilter(SobelFilter0)
            conv_image1, f_image1 = self.ApplyFilter(SobelFilter1)
            f_image = np.sqrt(f_image0**2+f_image1**2)
            conv_image = np.sqrt(conv_image0**2+conv_image1**2)
            rows, columns = f_image.shape
            self.ImageFourier.ShowArray(f_image, 'gray', columns, rows, np.amin(f_image), np.amax(f_image))
            # self.ImageDiff.ShowArray(conv_image, 'gray', columns, rows, np.amin(conv_image), np.amax(conv_image))
            diff_imge = f_image - conv_image
            self.ImageDiff.ShowArray(diff_imge, 'gray', columns, rows, 0, 255)


    def custom_sobel(self, shape, axis):
        k = np.zeros((shape, shape))
        p=[]
        for j in range(shape):
            for i in range(shape):
                if not (i == (shape -1)/2. and j == (shape -1)/2.):
                    p.append((j,i))
        k=np.zeros((shape, shape))
        for j, i in p:
            j_ = int(j - (shape -1)/2.)
            i_ = int(i - (shape -1)/2.)
            if axis==0:
                k[j,i] = i_/float(i_*i_ + j_*j_)
            else:
                k[j,i] = j_/float(i_*i_ + j_*j_)
        return k
    
    def DeleteWidget(self):
        """Deletes the widget and it's components
        """
        self.layout_main.deleteLater()
        self.BrowseWidget.deleteLater()
        
        self.Image.deleteLater()
        self.ImageScrollArea.deleteLater()
        
        self.ImageDiff.deleteLater()
        self.ImageDiffScrollArea.deleteLater()

        self.ImageFourierScrollArea.deleteLater()
        self.ImageFourier.deleteLater()

        self.size_label.deleteLater()
        self.size_text.deleteLater()
        self.ApplyButton.deleteLater()

        self.FilterComboBox.deleteLater()
