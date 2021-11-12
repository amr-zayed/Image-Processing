from PyQt5 import QtCore, QtWidgets
from ImageDisplayerMatplot import ImageDisplay
from Helpers import BrowseWidget
import os
import numpy as np
class Task4(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout_main)

        self.BrowseWidget = BrowseWidget()
        self.BrowseWidget.browse_button.clicked.connect(lambda: self.BrowseClicked())

        self.Image = ImageDisplay()
        self.ImageScrollArea = QtWidgets.QScrollArea()
        self.ImageScrollArea.setWidget(self.Image)

        self.ImageEqualized = ImageDisplay()
        self.EqualizedScrollArea = QtWidgets.QScrollArea()
        self.EqualizedScrollArea.setWidget(self.ImageEqualized)

        self.HistogramImage = ImageDisplay()
        self.HistogramEqualized = ImageDisplay()

        self.ScrollWidget = QtWidgets.QWidget()
        self.ScrollArea = QtWidgets.QScrollArea()
        self.ScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ScrollArea.setWidgetResizable(True)

        self.layout_scroll = QtWidgets.QGridLayout()
        self.layout_scroll.addWidget(self.BrowseWidget, 0, 0, 1, 2)
        self.layout_scroll.addWidget(self.ImageScrollArea, 1, 0)
        self.layout_scroll.addWidget(self.HistogramImage, 1, 1)
        self.layout_scroll.addWidget(self.EqualizedScrollArea, 2, 0)
        self.layout_scroll.addWidget(self.HistogramEqualized, 2, 1)
        self.layout_scroll.setRowStretch(0,0)
        self.layout_scroll.setColumnStretch(0,1)
        self.layout_scroll.setColumnStretch(1,1)

        self.ScrollWidget.setLayout(self.layout_scroll)
        self.ScrollWidget.setFixedHeight(1720)
        
        self.ScrollArea.setWidget(self.ScrollWidget)
        self.layout_main.addWidget(self.ScrollArea)        

        self.PixelsArray = []
        self.Path = ''
        self.HistogramData = {}
        for i in range(256):
            self.HistogramData[i]=[0]

    def BrowseClicked(self):
        """saves the image from path and creates the image info string
        """
        Imagepath = self.open_dialog_box()
        
        if not Imagepath: 
            return
        self.BrowseWidget.browse_text.insert(Imagepath[0])
        self.Path=Imagepath[0]

        try:
            if Imagepath[1] == '.dcm':
                    self.Image.SetDicom(Imagepath[0])
            else:
                self.Image.SetPath(Imagepath[0])
        except:
            self.Image.DisplayError("Corrupted File", "This file is corrupted")

        self.PixelsArray = self.Image.ToGrayScale(self.Image.PixelArray)
        Rows, Columns = self.PixelsArray.shape
        self.Image.ShowArray(np.uint8(self.PixelsArray), 'gray', Columns, Rows, 0, 255)
        self.HistogramData = self.CalculateHistogram(self.PixelsArray)
        self.PlotHistogram(self.HistogramData, False)
        EqualizedArray = self.HistoEqualization()
        EqualizedData = self.CalculateHistogram(EqualizedArray)
        self.PlotHistogram(EqualizedData, True)


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
        FileTypes = ['.bmp', '.jpeg', '.dcm', '.jpg', '.tif']
        if Imagepath[1].lower() in FileTypes:
            return [filename[0], Imagepath[1].lower()]
        else:
            self.Image.DisplayError('file type error', 'please select a JPEG or BMP or DICOM')
            return self.open_dialog_box()

    def CalculateHistogram(self, array):
        Rows, Columns = array.shape
        Data = {}
        for i in range(256):
            Data[i]=[0]
        for i in range(Rows):
            for j in range(Columns):
                Data[array[i][j]][0] += 1
        return Data

    def PlotHistogram(self, histo, IsEqualized):
        Intensities = list(histo.keys())
        Values = list(zip(*list(histo.values())))[0]
        if IsEqualized:
            self.HistogramEqualized.PltHistogram(Intensities, Values)
        else: 
            self.HistogramImage.PltHistogram(Intensities, Values)

    def HistoEqualization(self):
        Rows, Columns = self.PixelsArray.shape
        PixelsCount = Rows*Columns
        pdf = 0
        for i in range(256):
            n = self.HistogramData[i][0]
            pdf = n/PixelsCount
            if i==0:
                self.HistogramData[i].append(pdf)
            else:
                self.HistogramData[i].append(self.HistogramData[i-1][1]+pdf)
            self.HistogramData[i].append(round(self.HistogramData[i][1]*255))
        NewArray = np.ndarray((Rows, Columns))
        for i in range(Rows):
            for j in range(Columns):
                NewArray[i][j] = self.HistogramData[self.PixelsArray[i][j]][2]
        self.ImageEqualized.ShowArray(np.uint8(NewArray), 'gray', Columns, Rows, 0, 255)
        return NewArray
        
            
    def DeleteWidget(self):
        """Destructs the widget
        """
        self.Image.deleteLater()
        self.ImageEqualized.deleteLater()
        self.BrowseWidget.deleteLater()
        self.layout_main.deleteLater()
