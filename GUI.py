from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont, QIcon
import numpy as np
import os
from ImageDisplayer import ImageDisplay
from Task1 import Task1
from Task2 import Task2

NO_OF_TASKS = 2
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
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.main_widget = QtWidgets.QWidget(self)
        self.layout_main = QtWidgets.QGridLayout(self.main_widget)
        self.layout_main.setContentsMargins(0,0,0,0)
        self.layout_Task = QtWidgets.QGridLayout()
        self.layout_Task.setContentsMargins(0,0,0,0)
        self.TaskWindowCC = QtWidgets.QWidget()
        self.TaskWindowCC.setStyleSheet("""
        background-color:#1e1e1e;
        """)
        self.TaskWindowCC.setLayout(self.layout_Task)

        self.layout_sidebar = QtWidgets.QVBoxLayout()
        self.layout_sidebar.setContentsMargins(0,10,0,0)
        self.sidebar_container = QtWidgets.QWidget()
        self.sidebar_container.setLayout(self.layout_sidebar)
        self.sidebar_container.setStyleSheet("background-color:#333333;")
        self.sidebar_container.setFixedWidth(55)
        self.layout_side_component = QtWidgets.QVBoxLayout()

        self.layout_main.addWidget(self.sidebar_container, 0, 0)
        self.layout_main.addLayout(self.layout_side_component, 0, 1)
        self.layout_main.addWidget(self.TaskWindowCC, 0, 2)
        
        self.layout_main.setColumnStretch(2,10)

        #Creating sidebar icons
        self.sidebar_task = QtWidgets.QPushButton()
        self.sidebar_task.setIcon(QIcon('Sidebar_Icons/tasks.png'))
        self.sidebar_task.clicked.connect(lambda: self.OpenTaskBar())
        self.sidebar_task.setStyleSheet(" QPushButton { border: none; }")
        self.sidebar_task.setCheckable(True)
        self.layout_sidebar.addWidget(self.sidebar_task)

        #Resizing the icons in the sidebar using  
        ButtonHeight = 40
        self.IconRatio = self.sidebar_task.iconSize().height()/self.sidebar_task.iconSize().width() 
        self.sidebar_task.setFixedHeight(ButtonHeight)
        self.sidebar_task.setIconSize(QtCore.QSize(ButtonHeight/self.IconRatio, ButtonHeight))
        self.sidebar_task.setFixedWidth(50)
        self.sidebar_task.setChecked(True)

        self.InitialLabel()
        self.ConstructSideComponents()
        self.current_task_opened = 0

        self.layout_sidebar.addStretch(1)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.resize(1080,720)

    def OpenTaskBar(self):
        """Handels the deletion and creation of the buttons that selects the task
        when the user clckes on the task menu in the SideBar
        """
        if self.sidebar_task.isChecked():
            self.ConstructSideComponents()
        else:
            self.DestructSideComponents()
        
    def ConstructSideComponents(self):
        """Creates the items inside the task menu
        """
        self.SideComponentCC =QtWidgets.QWidget() 
        self.layout_side_component = QtWidgets.QVBoxLayout()
        self.SideComponentCC.setStyleSheet("background-color:#252526;")
        self.SideComponentCC.setFixedWidth(220)
        self.SideComponentCC.setLayout(self.layout_side_component)
        self.layout_main.addWidget(self.SideComponentCC, 0, 1)
        self.TasksButtonsMapper = QtCore.QSignalMapper()
        self.SideComponentButtons =[]
        for Task in range(NO_OF_TASKS):
            
            self.SideComponentButtons.append(QtWidgets.QPushButton('Task {}'.format(Task+1)))
            self.SideComponentButtons[Task].clicked.connect(self.TasksButtonsMapper.map)
            self.SideComponentButtons[Task].setStyleSheet(PUSH_BUTTON_STYLE)
            self.TasksButtonsMapper.setMapping(self.SideComponentButtons[Task], Task)
            self.layout_side_component.addWidget(self.SideComponentButtons[Task])
        self.layout_side_component.addStretch()
        self.TasksButtonsMapper.mapped.connect(self.SelectTask)
        self.layout_main.setSpacing(0)

    def DestructSideComponents(self):
        """Deletes the items inside the task menu
        """
        for button in self.SideComponentButtons:
            self.layout_side_component.removeWidget(button)
            button.deleteLater()
        self.SideComponentCC.deleteLater()
        #self.layout_main.removeItem(self.layout_side_component)
        self.layout_side_component = None

    def SelectTask(self, index):
        """checks if the task selected is already opened or not. if not,
        the function will delete the opened task and created the newly selected task

        Args:
            index (int): the index of the clicked task button 
        """
        if (index+1)==self.current_task_opened:
            return

        self.current_task_opened = index+1

        self.layout_Task.removeWidget(self.OpenedTask)
        if self.OpenedTask == self.InitialLabel:
            self.InitialLabel.deleteLater()
        else:
            self.OpenedTask.DeleteWidget()

        if index == 0:
            self.OpenedTask = Task1()
            self.layout_Task.addWidget(self.OpenedTask)
        elif index==1:
            self.OpenedTask = Task2()
            self.layout_Task.addWidget(self.OpenedTask)
            
    
    def InitialLabel(self):
        """Creates the initial label that say "Please Select A Task" when no task is selected
        """
        self.InitialLabel = QtWidgets.QLabel('Please Select A Task')
        self.InitialLabel.setStyleSheet(TEXT_COLOR)
        self.InitialLabel.setFont(QFont('impact', 30))
        self.InitialLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.OpenedTask = self.InitialLabel
        self.layout_Task.addWidget(self.OpenedTask) 