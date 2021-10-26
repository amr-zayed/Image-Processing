from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QRect
import numpy as np
import pydicom as dicom
from os import stat
from PIL.Image import fromarray, open
# from DicomToPIL import get_PIL_image, show_PIL

class ImageDisplay(QLabel):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.ImageDisplayer = QPixmap()
        self.setPixmap(self.ImageDisplayer)
        self.path = ''
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

    def SetPath(self, path):
        """Sets the path of the image and generates the information and puts it in a dictionary called Info

        Args:
            path (str): File Path
        """
        self.DicomImage = None
        self.path = path
        data = open(self.path)
        mode_to_depth = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}
        self.ImageDisplayer = QPixmap(self.path)
        self.Info['width'] = self.ImageDisplayer.width()
        self.Info['height'] = self.ImageDisplayer.height()
        self.Info['size'] = stat(self.path).st_size
        self.Info['depth'] = mode_to_depth[data.mode]
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
        # show_PIL(self.DicomImage)
        # pil_image = get_PIL_image(self.DicomImage)
        self.CheckDicomData('PatientName')
        self.CheckDicomData('PatientAge')
        self.CheckDicomData('Modality')
        self.CheckDicomData('BodyPartExamined')

        PixelArray = self.DicomImage.pixel_array

        image = fromarray(PixelArray.astype(np.int8), 'P')
        image = ImageQt(image)
        self.ImageDisplayer = QPixmap.fromImage(image)
        self.Info['width'] = self.ImageDisplayer.width()
        self.Info['height'] = self.ImageDisplayer.height()
        self.Info['size'] = stat(self.path).st_size
        self.Info['color'] = 'grayscale'
        self.Info['depth'] = 8
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

    def ArrayToQpixmap(self, Array, mode):
        """Creates a Qpixmap from an array

        Args:
            Array (ndarray): array of pixels
            mode (str): image mode: RGB, L, P, 1, etc...
        """
        image = fromarray(Array).convert(mode)
        image.save('C:/Users/hp/Desktop/Image Processing/Image Viewer/Image Viewer/Sidebar_Icons/imagePIL.jpg')
        image = ImageQt(image)
        image = QPixmap('C:/Users/hp/Desktop/Image Processing/Image Viewer/Image Viewer/Sidebar_Icons/imagePIL.jpg')
        self.ImageDisplayer = image
        self.update()

    def paintEvent(self, event):
        if not self.ImageDisplayer.isNull():
            height = 0
            width = 0
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            canvas_width = event.rect().width()
            canvas_height = event.rect().height()
            image_width = self.ImageDisplayer.width()
            image_height = self.ImageDisplayer.height()
            Scaled_width = (canvas_height*image_width)/image_height
            Scaled_height = (canvas_width*image_height)/image_width

            new_width = 0
            new_height = 0

            if Scaled_width < canvas_width:
                new_height = canvas_height
                new_width = Scaled_width
            else:
                new_height = Scaled_height
                new_width = canvas_width
            
            HeightShift = (event.rect().height()/2) - (new_height/2)
            widthtShift = (event.rect().width()/2) - (new_width/2)
            painter.drawPixmap(QRect(widthtShift, HeightShift,new_width, new_height), self.ImageDisplayer)
    
    