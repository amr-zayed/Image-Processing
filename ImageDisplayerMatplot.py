from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget
import pydicom as dicom
from os import stat
from PIL.Image import open
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from numba import jit

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor='#1e1e1e')
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self.axes.axis('off')
        super(MplCanvas, self).__init__(self.figure)
    def mousePressEvent(self, event):
        return (event.x(), event.y())





class ImageDisplay(QtWidgets.QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ImageDisplayer = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setContentsMargins(0,0,0,0)
        self.layout_main.addWidget(self.ImageDisplayer)
        self.setLayout(self.layout_main)
        self.path = ''
        self.PixelArray = None
        self.DicomImage = None
        self.Info = {'width': 0,
        'height': 0,
        'size': 0,
        'depth': 0,
        'color': ''}

        self.DicomInfo = {'Modality': '',
        'PatientName': '',
        'PatientAge': '',
        'BodyPartExamined': ''}

        self.MessageBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Error", "Error")

    def SetPath(self, path):
        """Sets the path of the image and generates the information and puts it in a dictionary called Info

        Args:
            path (str): File Path
        """
        self.DicomImage = None
        self.path = path
        data = open(self.path)
        self.PixelArray = np.asarray(data)
        mode_to_depth = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}
        width, height = data.size
        self.ImageDisplayer.axes.margins(0, 0)
        self.ImageDisplayer.axes.imshow(data)
        self.Info['width'] = width
        self.Info['height'] = height
        self.Info['size'] = stat(self.path).st_size
        self.Info['depth'] = mode_to_depth[data.mode]
        self.setFixedWidth(self.Info['width'])
        self.setFixedHeight(self.Info['height'])
        if self.Info['depth'] == 1:
            self.Info['color'] = 'Binary'
        elif self.Info['depth']==8:
            self.Info['color'] = 'grayscale'
        else:
            self.Info['color'] = 'RGB'
        self.update()

    def SetDicom(self, path):
        """Sets the path of a dicom and generates its information and puts it in a
        dictionaries called Info and and DicomInfo 

        Args:
            path (str): Dicom Path
        """
        self.path = path
        self.DicomImage = dicom.dcmread(path)
        self.CheckDicomData('PatientName')
        self.CheckDicomData('PatientAge')
        self.CheckDicomData('Modality')
        self.CheckDicomData('BodyPartExamined')

        self.PixelArray = self.DicomImage.pixel_array
        self.ImageDisplayer.axes.imshow(self.PixelArray, cmap='gray')

        self.Info['width'] = self.PixelArray.shape[0]
        self.Info['height'] = self.PixelArray.shape[1]
        self.Info['size'] = stat(self.path).st_size
        self.Info['color'] = 'grayscale'
        self.Info['depth'] = 8
        self.setFixedWidth(self.Info['width'])
        self.setFixedHeight(self.Info['height'])
        self.update()

    def CheckDicomData(self, attribute):
        """checks if there is an a value for attribute in the dicom image.
        if so, the value is set in DicomInfo. otherwise, it sets the attribute
        in DicomInfo as empty string

        Args:
            attribute (str): the name of the attribute to be cheked
        """
        try:
            self.DicomInfo[attribute] = self.DicomImage[attribute].value
        except:
            self.DicomInfo[attribute] = ''

    def LabelData(self):
        """Creates a string with information in both dictionaries and returns the string
        """
        MainData = "Width: {}\n\
Height: {}\n\
Size in bits: {}\n\
Color: {}\n\
bit Depth: {}\n".format(self.Info['width'],
        self.Info['height'],
        self.Info['size'],
        self.Info['color'],
        self.Info['depth'])

        if self.DicomImage:
            DicomData = "Patient Name: {}\n\
Patient Age: {}\n\
Modality: {}\n\
Body Part Examined: {}".format(self.DicomInfo['PatientName'],
            self.DicomInfo['PatientAge'],
            self.DicomInfo['Modality'],
            self.DicomInfo['BodyPartExamined'])
            MainData = MainData +DicomData

        return MainData

    def ShowArray(self, Array, color= None, width=None, height=None, VMin = None, VMax = None):
        """Creates a Qpixmap from an array

        Args:
            Array (ndarray): array of pixels
            color (str): Color Template
        """
        self.ImageDisplayer.axes.clear()
        self.ImageDisplayer.axes.imshow(Array, cmap=color, vmin = VMin, vmax = VMax)
        if width != None and height!= None:
            if self.height()==height and self.width()==width:
                self.setFixedWidth(width+1)
                self.setFixedHeight(height+1)
            else:
                self.setFixedWidth(width)
                self.setFixedHeight(height)
        else:
            if self.height()==height and self.width()==width:
                self.setFixedWidth(self.Info['width']+1)
                self.setFixedHeight(self.Info['height']+1)
            else:
                self.setFixedWidth(self.Info['width'])
                self.setFixedHeight(self.Info['height'])
        self.update()

    def PltHistogram(self, keys, values):
        self.ImageDisplayer.axes.clear()
        self.ImageDisplayer.axes.bar(keys, values)
        if self.height()==720:
            self.setFixedHeight(721)
        else:
            self.setFixedHeight(720)
        self.ImageDisplayer.axes.axis('on')


    def DisplayError(self, title, Message):
        """Creates a messsage box when and error happens

        Args:
            title (str): title of the error message
            Message (str): information about the error to be displayed
        """
        self.MessageBox.setWindowTitle(title)
        self.MessageBox.setText(Message)
        self.MessageBox.exec()

    @jit(forceobj=True)
    def ToGrayScale(self, array):
        if len(array.shape)!=3:
            return array
        
        rows, columns, _ = array.shape
        NewArray = np.ndarray((rows, columns))
        pixelValue = 0
        array = array/255
        for i in range(rows):
            for j in range(columns):
                pixelValue = 0.2126*array[i][j][0]+0.7152*array[i][j][1]+0.0722*array[i][j][2]
                NewArray[i][j] = round((pixelValue/3)*255)

        return NewArray

