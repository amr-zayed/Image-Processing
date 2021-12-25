from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QWidget, QFileDialog
from ImageDisplayerMatplot import ImageDisplay
from Helpers import BrowseWidget
from PyQt5.QtGui import QDoubleValidator, QFont
import os
import numpy as np
from numba import jit
import numpy as np
from math import ceil, floor, sqrt

from timeit import default_timer as timer 

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

class Task3(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.Path = ''
        self.ZoomFactor = 1

        self.NearestArray = None
        self.LinearArray = None
        self.MainArray = None
        self.layout_main = QGridLayout()
        self.layout_main.setContentsMargins(0,0,0,0)
        self.layout_images = QHBoxLayout()
        self.layout_images.setContentsMargins(10,10,10,10)
        self.layout_controls = QHBoxLayout()
        self.layout_controls.setContentsMargins(10,10,10,10)
        self.layout_labels = QHBoxLayout()
        self.layout_labels.setContentsMargins(0,0,0,0)
        
        self.ImageLinear = ImageDisplay()
        self.LinearScrollArea = QtWidgets.QScrollArea()
        self.LinearScrollArea.setWidget(self.ImageLinear)
        
        self.ImageNearest = ImageDisplay()
        self.NearestScrollArea = QtWidgets.QScrollArea()
        self.NearestScrollArea.setWidget(self.ImageNearest)

        self.Browse = BrowseWidget()
        self.Browse.browse_button.clicked.connect(lambda: self.BrowseClicked())

        self.number_label = QtWidgets.QLabel("Enter Zoom Factor: ")
        self.number_label.setFont(QFont('impact', 15))
        self.number_label.setStyleSheet(TEXT_COLOR)
        self.number_text = QtWidgets.QLineEdit()
        self.number_text.setValidator(QDoubleValidator())
        self.number_text.setEnabled(False)
        self.number_text.setStyleSheet("color: #BCBCBC;")
        self.number_button = QtWidgets.QPushButton('Apply')
        self.number_button.setStyleSheet(PUSH_BUTTON_STYLE)
        self.number_button.setEnabled(False)
        self.number_button.clicked.connect(lambda: self.Zoom())

        self.linear_label = QtWidgets.QLabel("Linear")
        self.linear_label.setFont(QFont('impact', 15))
        self.linear_label.setStyleSheet(TEXT_COLOR)
        self.linear_label.setAlignment(QtCore.Qt.AlignCenter)
        self.nearest_label = QtWidgets.QLabel("Nearest neighbor")
        self.nearest_label.setFont(QFont('impact', 15))
        self.nearest_label.setAlignment(QtCore.Qt.AlignCenter)
        self.nearest_label.setStyleSheet(TEXT_COLOR)
        self.layout_labels.addWidget(self.linear_label)
        self.layout_labels.addWidget(self.nearest_label)

        self.layout_controls.addWidget(self.number_label)
        self.layout_controls.addWidget(self.number_text)
        self.layout_controls.addWidget(self.number_button)

        
        self.layout_images.addWidget(self.LinearScrollArea)
        self.layout_images.addWidget(self.NearestScrollArea)
        self.layout_main.addLayout(self.layout_controls,0,0)
        self.layout_main.addLayout(self.layout_labels,1,0)
        self.layout_main.addLayout(self.layout_images,2,0)
        self.layout_main.addWidget(self.Browse,3,0)
        self.layout_main.setRowStretch(3,0)


        
        self.setLayout(self.layout_main)

    def BrowseClicked(self):
        """saves the image from path and creates the image info string
        """
        Imagepath = self.open_dialog_box()
        
        if not Imagepath: 
            return
        self.Browse.browse_text.insert(Imagepath[0])
        self.Path=Imagepath[0]

        try:
            if Imagepath[1] == '.dcm':
                    self.ImageLinear.SetDicom(Imagepath[0])
                    self.ImageNearest.SetDicom(Imagepath[0])
            else:
                self.ImageLinear.SetPath(Imagepath[0])
                self.ImageNearest.SetPath(Imagepath[0])
        except:
            self.ImageNearest.DisplayError("Corrupted File", "This file is corrupted")
        
        self.NearestArray = self.ImageNearest.PixelArray
        self.NearestArray = self.ImageNearest.ToGrayScale(self.NearestArray)
        self.LinearArray = self.NearestArray.copy()
        self.MainArray = self.NearestArray.copy()

        self.ImageLinear.ShowArray(np.uint8(self.LinearArray), 'gray')
        self.ImageNearest.ShowArray(np.uint8(self.NearestArray), 'gray')
        self.number_button.setEnabled(True)
        self.number_text.setEnabled(True)

    def open_dialog_box(self):
        """Creates a diaglog box for the user to select file and check if it's an image

        Returns:
            [str, str]: array of the filepath path and file type
        """
        filename = QFileDialog.getOpenFileName()
        Imagepath = filename[0]
        if Imagepath == '':
            return False

        Imagepath=os.path.splitext(Imagepath)
        FileTypes = ['.bmp', '.jpeg', '.dcm', '.jpg']
        if Imagepath[1].lower() in FileTypes:
            return [filename[0], Imagepath[1].lower()]
        else:
            self.ImageLinear.DisplayError('file type error', 'please select a JPEG or BMP or DICOM')
            return self.open_dialog_box()

    def Zoom(self):
        if self.number_text.text()=='' or self.ImageLinear.Info['depth']==1:
            return
        self.number_button.setEnabled(False)
        self.ZoomFactor = float(self.number_text.text())
        self.number_text.clear()
        
        start = timer()
        self.NearestArray, width, height = self.NearestNeighborZoom(self.MainArray, self.ZoomFactor)
        self.ImageNearest.ShowArray(self.NearestArray, color='gray', width= width, height= height)

        start = timer()
        self.LinearArray, width, height = self.LinearInterpZoom(self.MainArray, self.ZoomFactor)
        self.ImageLinear.ShowArray(self.LinearArray, color='gray', width= width, height= height)
        self.number_button.setEnabled(True)

    @jit(forceobj=True)
    def NearestNeighborZoom(self, Array, ZoomFactor):
        Rows, Columns = Array.shape
        Rows = int(Rows*ZoomFactor)
        Columns = int(Columns*ZoomFactor)
        NewArray = np.ndarray((Rows, Columns))
        for i in range(Rows):
            for j in range(Columns):
                NewArray[i][j]=Array[round(i/ZoomFactor)][round(j/ZoomFactor)]
        
        return NewArray, Columns, Rows

    @jit(forceobj=True)
    def LinearInterpZoom(self, Array, ZoomFactor):
        Rows, Columns = Array.shape
        Rows = int(Rows*ZoomFactor)
        Columns = int(Columns*ZoomFactor)
        NewArray = np.ndarray((Rows, Columns))
        topRight = []
        topleft = []
        bottomRight = []
        bootomLeft = []
        for i in range(Rows):
            for j in range(Columns):
                x= i/ZoomFactor
                if ceil(x) >= floor(Rows/ZoomFactor):
                    x=(Rows/ZoomFactor)-1
                y= j/ZoomFactor
                if ceil(y) >= floor(Columns/ZoomFactor):
                    y = (Columns/ZoomFactor)-1
                if x.is_integer() and y.is_integer():
                    NewArray[i][j]=Array[int(x)][int(y)]
                    continue
                topRight.append(Array[floor(x)][ceil(y)])
                topRight.append(self.DistanceBet(floor(x), ceil(y), x, y))
                topleft.append(Array[floor(x)][floor(y)])
                topleft.append(self.DistanceBet(floor(x), ceil(y), x, y))
                bottomRight.append(Array[ceil(x)][ceil(y)])
                bottomRight.append(self.DistanceBet(floor(x), ceil(y), x, y))
                bootomLeft.append(Array[ceil(x)][ceil(y)])
                bootomLeft.append(self.DistanceBet(floor(x), ceil(y), x, y))
                norms = self.Normalize(topRight[1], topleft[1], bottomRight[1], bootomLeft[1])
                topRight[1]= norms[0]
                topleft[1]= norms[1]
                bottomRight[1]= norms[2]
                bootomLeft[1]= norms[3]
                NewArray[i][j] = topRight[0]*topRight[1]+ topleft[0]*topleft[1] + bottomRight[0]*bottomRight[1] + bootomLeft[0]*bootomLeft[1]
                topRight=[]
                topleft=[]
                bottomRight=[]
                bootomLeft=[]
        
        return NewArray, Columns, Rows


    def DistanceBet(self, x1, y1, x2, y2):
        return sqrt((x1-x2)**2+(y1-y2)**2)

    def Normalize(self, p1, p2, p3, p4):
        norm = 1/(p1+p2+p3+p4)
        return norm*p1, norm*p2, norm*p3, norm*p4 

    def DeleteWidget(self):
        """Destructs the widget
        """
        self.ImageLinear.deleteLater()
        self.ImageNearest.deleteLater()
        self.Browse.deleteLater()
        self.layout_main.deleteLater()
        self.LinearScrollArea.deleteLater()
        self.NearestScrollArea.deleteLater()
        self.number_text.deleteLater()
        self.number_button.deleteLater()
        self.number_label.deleteLater()
        self.linear_label.deleteLater()
        self.nearest_label.deleteLater()
        self.layout_controls.deleteLater()
        self.layout_images.deleteLater()
        self.layout_labels.deleteLater()