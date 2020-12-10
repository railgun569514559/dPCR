import sys
# from Equipment import *
from PyQt5.QtGui import QPixmap, QImage
# from ObjectDetection import *
from my_lib.dPCR_gui import *
from my_lib_ever.controler_gui_plus import *
from my_lib_ever.Image_analysis_gui_plus import ImageAnalysisWidget
import time
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QApplication, QLabel, QWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import cv2
import qdarkstyle

def cv_show(name, img):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # 设置为WINDOW_NORMAL可以任意缩放
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

class MainWindow(Ui_MainWindow,QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.controller_gui = ControllerWidget()
        self.ImageAnalysis_gui = ImageAnalysisWidget()
        self.ControllerLayout.addWidget(self.controller_gui)
        self.ImgAnalysisLayout.addWidget(self.ImageAnalysis_gui)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    a.show()
    sys.exit(app.exec_())
