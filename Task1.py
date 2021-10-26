from PyQt5.QtWidgets import QGridLayout, QSpacerItem, QWidget
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtCore
from ImageDisplayer import ImageDisplay
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
        self.layout_browse = QtWidgets.QHBoxLayout()
        self.browse_label = QtWidgets.QLabel()
        self.browse_label = QtWidgets.QLabel("Open: ")
        self.browse_label.setFont(QFont('impact', 15))
        self.browse_label.setStyleSheet(TEXT_COLOR)

        self.browse_text = QtWidgets.QLineEdit()
        self.browse_text.setStyleSheet(TEXT_COLOR)
        self.browse_button = QtWidgets.QPushButton('Browse')
        self.browse_button.setStyleSheet(PUSH_BUTTON_STYLE)

        self.browse_button.clicked.connect(lambda: self.BrowseClicked())
        self.image= ImageDisplay()

        self.details_label = QtWidgets.QLabel()
        self.details_label.setFont(QFont('default', 13))
        self.details_label.setAlignment(QtCore.Qt.AlignTop)
        self.details_label.setContentsMargins(15,15,15,15)
        self.details_label.setStyleSheet(TEXT_COLOR)
        self.layout_browse.addWidget(self.browse_label)
        self.layout_browse.addWidget(self.browse_text)
        self.layout_browse.addWidget(self.browse_button)
        self.layout_image.addWidget(self.image,0,0)
        self.layout_image.addLayout(self.layout_browse,1,0)
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

        self.MessageBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Error", "Error")

    def BrowseClicked(self):
        """saves the image from path and creates the image info string
        """
        Imagepath = self.open_dialog_box()
        
        if not Imagepath: 
            return
        self.browse_text.insert(Imagepath[0])
        try:
            if Imagepath[1] == '.dcm':
                    self.image.SetDicom(Imagepath[0])
            else:
                self.image.SetPath(Imagepath[0])
            self.details_label.setText(self.image.LabelData())
        except:
            self.DisplayError("Corrupted File", "This file is corrupted")
    
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
            self.DisplayError('file type error', 'please select a JPEG or BMP or DICOM')
            return self.open_dialog_box()
            

    def DisplayError(self, title, Message):
        """Creates a messsage box when and error happens

        Args:
            title (str): title of the error message
            Message (str): information about the error to be displayed
        """
        self.MessageBox.setWindowTitle(title)
        self.MessageBox.setText(Message)
        self.MessageBox.exec()

    def DeleteWidget(self):
        """Destructs the widget
        """
        self.details_label.deleteLater()
        self.browse_button.deleteLater()
        self.browse_text.deleteLater()
        self.layout_browse.deleteLater()
        self.layout_image.deleteLater()
        self.deleteLater()