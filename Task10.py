from PyQt5 import QtWidgets
from matplotlib import interactive
from numpy.core.fromnumeric import amax, amin
from ImageDisplayerMatplot import ImageDisplay
from Helpers import BrowseWidget
from matplotlib.widgets import RectangleSelector
from matplotlib import cm
import numpy as np
import os
import matplotlib.pyplot as plt

class Task10(QtWidgets.QWidget):
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

        self.layout_main.addWidget(self.BrowseWidget,0,0)
        self.layout_main.addWidget(self.ImageScrollArea,1,0)

    def line_select_callback(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata 
        x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
        if abs(x1-x2)<25 or abs(y1-y2)<25:
            self.Image.DisplayError('size error', 'selected area can not have a lemgth or width less than 25')
        # selected_area = self.variance[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
        # selected_area, row_count, col_count = self.to_odd_image(selected_area)

        # kernel = np.full((25, 25), 1/(25**2))
        # rows, columns = selected_area.shape
        # row_pad = (rows-25)//2
        # column_pad = (columns-25)//2
        # kernel = np.pad(kernel, [(row_pad, row_pad), (column_pad, column_pad)], 'constant')
        
        # image_fourier = np.fft.fft2(selected_area)
        # image_fourier2 = np.fft.fft2(selected_area**2)
        # kernel_fourier = np.fft.fft2(kernel)
        # avg_X = np.fft.ifft2(kernel_fourier*image_fourier)
        # avg_X2 = np.fft.ifft2(kernel_fourier*image_fourier2)
        
        # variance = avg_X2-avg_X**2
        # variance = np.abs(variance)
        # norm = plt.Normalize(amin(variance), amax(variance))
        # variance = cm.jet(norm(variance))
        # variance = variance[:,:,:3]
        array_variance = self.PixelsArray.copy()
        array_variance = np.stack((array_variance,)*3, axis=-1)
        array_variance = self.NormalizeData(array_variance)
        
        # array_variance[min(y1, y2):max(y1, y2)+col_count, min(x1, x2):max(x1, x2)+row_count] = self.variance[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
        array_variance[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)] = self.variance[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
        self.Image.ImageDisplayer.axes.imshow(array_variance)
    
    def NormalizeData(self, data):
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    def to_odd_image(self, image):
        print(image.shape)
        rows, columns = image.shape
        row_count = 0
        column_count=0
        if rows%2==0:
            image = np.vstack((image, np.tile(image[[-1], :], 1)))
            row_count+=1
        if columns%2==0:
            image = np.hstack((image, np.tile(image[:, [-1]], 1)))
            column_count+=1
        return image, row_count, column_count

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
        self.PixelsArray, _, _ = self.to_odd_image(self.PixelsArray)
        Rows, Columns = self.PixelsArray.shape
        self.Image.ShowArray(self.PixelsArray, width = Columns, height=Rows)
        self.rs = RectangleSelector(self.Image.ImageDisplayer.axes, self.line_select_callback,
        drawtype = 'box', useblit=False, button=[1], minspanx=5, minspany=5, spancoords='pixels', interactive=False)
        self.calc_variance(self.PixelsArray)
    
    def calc_variance(self, image):
        kernel = np.full((25, 25), 1/(25**2))
        rows, columns = image.shape
        row_pad = (rows-25)//2
        column_pad = (columns-25)//2
        kernel = np.pad(kernel, [(row_pad, row_pad), (column_pad, column_pad)], 'constant')
        
        image_fourier = np.fft.fft2(image)
        image_fourier2 = np.fft.fft2(image**2)
        kernel_fourier = np.fft.fft2(kernel)
        avg_X = np.fft.ifft2(kernel_fourier*image_fourier)
        avg_X = np.fft.ifftshift(avg_X)
        avg_X2 = np.fft.ifft2(kernel_fourier*image_fourier2)
        avg_X2 = np.fft.ifftshift(avg_X2)
        self.variance = avg_X2-avg_X**2
        self.variance = np.abs(self.variance)
        norm = plt.Normalize(amin(self.variance), amax(self.variance))
        self.variance = cm.jet(norm(self.variance))
        self.variance = self.variance[:,:,:3]

    def DeleteWidget(self):
        """Deletes the widget and it's components
        """
        self.Image.deleteLater()
        self.ImageScrollArea.deleteLater()
        self.BrowseWidget.deleteLater()
        self.layout_main.deleteLater()