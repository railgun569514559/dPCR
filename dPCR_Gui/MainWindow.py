import sys
# from Equipment import *
from PyQt5.QtGui import QPixmap, QImage
# from ObjectDetection import *
from my_lib.dPCR_gui import *
from my_lib_ever.controler_gui_plus import *
from my_lib_ever.Image_analysis_gui_plus import ImageAnalysisWidget
from my_lib_ever.Result_gui_plus import *
import time
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QApplication, QLabel, QWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
from my_lib_ever.disheDetect import circleDetect
import cv2 as cv
import qdarkstyle


class detectThread(QThread):
    detectFinish = pyqtSignal()

    def __init__(self, cd):
        super().__init__()
        self.cd = cd

    def run(self):
        img = cv.imread(r'F:\PythonProject\dPCR_Gui\image\FAM_density_mid.tif', 2)
        start = time.time()
        self.cd.detect(img)
        end = time.time()
        print('time:', end - start)
        self.detectFinish.emit()


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.controller_gui = ControllerWidget()
        self.ImageAnalysis_gui = ImageAnalysisWidget()
        self.ControllerLayout.addWidget(self.controller_gui)
        self.ImgAnalysisLayout.addWidget(self.ImageAnalysis_gui)

        self.result_gui = ResultGui()
        self.resultLayout.addWidget(self.result_gui)

        self.initUI()

    def initUI(self):
        self.cd = circleDetect()
        self.detectThread = detectThread(self.cd)
        self.detectCurrentBtn.clicked.connect(self.detectThread.start)
        self.detectThread.detectFinish.connect(self.detectFinish)

    def detectFinish(self):
        self.result_gui.setResult([self.cd.color_image,self.cd.bright_dishes,self.cd.dark_dishes,self.cd.bad_dishes])



if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    a.show()
    sys.exit(app.exec_())
