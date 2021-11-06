from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from Helpers import BrowseWidget
from ImageDisplayerMatplot import ImageDisplay
import os

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

class Task1(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.layout_main = QGridLayout()
        self.layout_main.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout_main)

        self.layout_image = QtWidgets.QGridLayout()
        self.layout_image.setContentsMargins(15,15,15,15)
        self.Browse = BrowseWidget()
        self.Browse.browse_button.clicked.connect(lambda: self.BrowseClicked())
        
        self.image= ImageDisplay()
        self.ScrollArea = QtWidgets.QScrollArea()
        self.ScrollArea.setWidget(self.image)

        self.details_label = QtWidgets.QLabel()
        self.details_label.setFont(QFont('default', 13))
        self.details_label.setAlignment(QtCore.Qt.AlignTop)
        self.details_label.setContentsMargins(15,15,15,15)
        self.details_label.setStyleSheet(TEXT_COLOR)

        self.layout_image.addWidget(self.ScrollArea,0,0)
        self.layout_image.addWidget(self.Browse,1,0)
        self.layout_main.addLayout(self.layout_image,0,0)
        
        Separator = QtWidgets.QFrame()
        Separator.setFrameShape(QtWidgets.QFrame.VLine)
        Separator.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
        Separator.setStyleSheet("color: #383838;")
        Separator.setLineWidth(1)
        self.layout_main.addWidget(Separator,0,1)
        self.layout_main.addWidget(self.details_label,0,2)
        self.layout_main.setColumnStretch(0,4)
        self.layout_main.setColumnStretch(2,1)

    def BrowseClicked(self):
        """saves the image from path and creates the image info string
        """
        Imagepath = self.open_dialog_box()
        
        if not Imagepath: 
            return
        self.Browse.browse_text.insert(Imagepath[0])

        try:
            if Imagepath[1] == '.dcm':
                    self.image.SetDicom(Imagepath[0])
            else:
                self.image.SetPath(Imagepath[0])
            self.details_label.setText(self.image.LabelData())
        except:
            self.image.DisplayError("Corrupted File", "This file is corrupted")
    
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
        FileTypes = ['.bmp', '.jpeg', '.dcm', '.jpg']
        if Imagepath[1].lower() in FileTypes:
            return [filename[0], Imagepath[1].lower()]
        else:
            self.image.DisplayError('file type error', 'please select a JPEG or BMP or DICOM')
            return self.open_dialog_box()

    def DeleteWidget(self):
        """Destructs the widget
        """
        self.details_label.deleteLater()
        self.Browse.deleteLater()
        self.layout_image.deleteLater()
        self.deleteLater()