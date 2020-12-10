from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QPushButton, QLCDNumber, QVBoxLayout
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from my_lib.Image_analysis_gui import *
import sys
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import cv2 as cv
from my_lib.HoughCircle import *
from ImageAnalysisTools import *
from matplotlib import pyplot as plt


class ImageShow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(ImageShow, self).__init__(parent)
        self.setupUi(self)

        self.img = cv.imread(r'F:\PythonProject\dPCR_Gui\image\FAM_density_mid.tif', 2)

        self.img = self.img.T
        self.imgCopy = self.img.copy()
        self.blurImg = None
        self.contrastImg = None
        self.rectificationImg = None

        self.thresholdImg = None

        self.ContrastImgBtn.clicked.connect(lambda: self.imgItem.setImage(self.contrastImg))
        self.BluredImgBtn.clicked.connect(lambda: self.imgItem.setImage(self.blurImg))

        pg.setConfigOptions(antialias=True)
        self.showImgWindow = pg.GraphicsLayoutWidget()
        self.ShowImgLayout.addWidget(self.showImgWindow)

        self.ROIWindow = pg.GraphicsLayoutWidget()
        self.ROILayout.addWidget(self.ROIWindow)

        self.histWindow = pg.GraphicsLayoutWidget()
        self.HistImgLayout.addWidget(self.histWindow)

        self.imgPlot = self.showImgWindow.addPlot(title="")
        self.ROIPlot = self.ROIWindow.addPlot(title="")
        self.histPlot = self.histWindow.addPlot(title="")

        self.imgItem = pg.ImageItem()
        # self.ROIItem = pg.PlotItem()

        self.imgPlot.addItem(self.imgItem)
        # self.histPlot.addItem(self.pltItem)
        # self.ROIPlot.addItem(self.ROIItem)

        self.imgItem.setImage(self.img)
        self.currentImg = self.img

        self.roi = pg.LineSegmentROI(positions=[[10, 64], [120, 64]])
        self.imgPlot.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update)
        self.update()
        self.showHist()

        self.returnOrignalImgBtn.clicked.connect(self.returnOrignalImg)

    def update(self):
        d2 = self.roi.getArrayRegion(self.currentImg, self.imgItem)
        self.ROIPlot.clear()
        self.ROIPlot.plot(d2, pen=(255, 0, 0), name="Red curve")

    def showHist(self):
        self.histPlot.clear()
        y, x = np.histogram(self.currentImg.ravel(), 256, [0, 256])
        self.histPlot.plot(x, y, stepMode=True, fillLevel=0, fillOutline=True, brush=(0, 0, 255, 150))

    def returnOrignalImg(self):
        self.imgCopy = self.img.copy()
        self.currentImg = self.img
        self.imgItem.setImage(self.imgCopy)


class LinearImageEnhance(ImageShow):
    def __init__(self, parent=None):
        super(LinearImageEnhance, self).__init__(parent)

        self.LinearAlphaEdit.setText('0.1')
        self.LinearAlphaVlidator = QDoubleValidator()
        self.LinearAlphaVlidator.setRange(0, 2)
        self.LinearAlphaVlidator.setNotation(QDoubleValidator.StandardNotation)
        self.LinearAlphaVlidator.setDecimals(1)

        self.LinearBetaEdit.setText('1')
        self.LinearBetaVlidator = QIntValidator()
        self.LinearBetaVlidator.setRange(0, 200)

        self.LinearAlphaEdit.setValidator(self.LinearAlphaVlidator)
        self.LinearBetaEdit.setValidator(self.LinearBetaVlidator)

    def linearChange(self):
        alpha = float(self.LinearAlphaEdit.text())
        beta = float(self.LinearBetaEdit.text())
        print(alpha, beta)
        self.contrastImg = cv.convertScaleAbs(self.imgCopy, alpha=alpha, beta=beta)
        self.imgItem.setImage(self.contrastImg)


class NormalizeImageEnhance(ImageShow):
    def __init__(self, parent=None):
        super(NormalizeImageEnhance, self).__init__(parent)

        self.NormAlphaEdit.setText('300')
        self.NormBetaEdit.setText('1')

    def normalizeChange(self):
        alpha = float(self.NormAlphaEdit.text())
        beta = float(self.NormBetaEdit.text())

        self.contrastImg = cv.normalize(self.imgCopy, dst=None, alpha=alpha, beta=beta, norm_type=cv.NORM_MINMAX)


class GammaImageEnhance(ImageShow):
    def __init__(self, parent=None):
        super(GammaImageEnhance, self).__init__(parent)

        self.gammaEdit.setText('0.5')

        self.gammaVlidator = QDoubleValidator()
        self.gammaVlidator.setRange(0, 1)
        self.gammaVlidator.setNotation(QDoubleValidator.StandardNotation)
        self.gammaVlidator.setDecimals(1)
        self.gammaEdit.setValidator(self.gammaVlidator)

    def GammaChange(self):
        gamma = float(self.gammaEdit.text())
        img_norm = self.imgCopy / 255.0  # 注意255.0得采用浮点数
        img_gamma = np.power(img_norm, gamma) * 255.0
        self.contrastImg = img_gamma.astype(np.uint8)


class ClaheImageEnhance(ImageShow):
    def __init__(self, parent=None):
        super(ClaheImageEnhance, self).__init__(parent)

        self.clipLimitEdit.setText('40')
        self.tileGridSizeEdit.setText('8')

        self.clipLimitVlidator = QIntValidator()
        self.clipLimitEdit.setValidator(self.clipLimitVlidator)
        self.tileGridSizeEdit.setValidator(self.clipLimitVlidator)

    def claheChange(self):
        clipLimit = int(self.clipLimitEdit.text())
        tileGridSize = int(self.tileGridSizeEdit.text())
        tileGridSize = (tileGridSize, tileGridSize)

        clahe = cv.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
        self.contrastImg = clahe.apply(self.imgCopy)


class Contrast(LinearImageEnhance, NormalizeImageEnhance, GammaImageEnhance, ClaheImageEnhance):
    def __init__(self, parent=None):
        super(Contrast, self).__init__(parent)

        self.EnhanceBtn.clicked.connect(self.executeEnhance)

    def executeEnhance(self):
        if self.LinearEnhanceRadio.isChecked():
            self.linearChange()

        if self.NormEhhanceRadio.isChecked():
            self.normalizeChange()

        if self.GammaRadio.isChecked():
            self.GammaChange()

        if self.equalizeHistRadio.isChecked():
            self.contrastImg = cv.equalizeHist(self.imgCopy)

        if self.CLAHERadio.isChecked():
            self.claheChange()

        self.currentImg = self.contrastImg
        self.imgItem.setImage(self.contrastImg)
        self.showHist()

        if self.isSaveContrastImgCheck.isChecked():
            self.imgCopy = self.contrastImg


class Blur(ImageShow):
    def __init__(self, parent=None):
        super(Blur, self).__init__(parent)
        self.blurBtn.clicked.connect(self.executeBlur)

    def executeBlur(self):

        if self.kernalEdit.text() == '':
            return
        kernalNum = int(self.kernalEdit.text())

        if self.GaussBlurRadio.isChecked():
            kernal = (kernalNum, kernalNum)
            self.blurImg = cv.GaussianBlur(self.imgCopy, kernal, 0)

        if self.medianBlurRadio.isChecked():
            kernal = kernalNum
            self.blurImg = cv.medianBlur(self.imgCopy, kernal)

        if self.averageBlurRadio.isChecked():
            kernal = (kernalNum, kernalNum)
            self.blurImg = cv.blur(self.imgCopy, kernal)

        if self.isSaveBlurImgCheck.isChecked():
            self.imgCopy = self.blurImg

        self.imgItem.setImage(self.blurImg)
        self.currentImg = self.blurImg
        self.showHist()


class Rectification(ImageShow, RectificationTools):
    def __init__(self, parent=None):
        super(Rectification, self).__init__(parent)

        self.RectificationBtn.clicked.connect(self.ExecuteRectify)

    def ExecuteRectify(self):
        image = self.imgCopy.copy()
        self.rectificationImg = self.imageRectification(image)
        self.imgItem.setImage(self.rectificationImg)
        self.currentImg = self.rectificationImg
        self.showHist()
        if self.isSaveRectifyImgCheck.isChecked():
            self.imgCopy = self.rectificationImg


class Threshold(ImageShow):
    def __init__(self, parent=None):
        super(Threshold, self).__init__(parent)
        self.ExecuteThresBtn.clicked.connect(self.executeThreshold)

    def executeThreshold(self):
        img = self.imgCopy
        if self.BlockSizeEdit.text() == '':
            block_size = 3
        else:
            block_size = int(self.BlockSizeEdit.text())
        print(self.ThresholdRadio.isChecked())
        if self.ThresholdRadio.isChecked():
            threshholdVal = self.ThresholdValudEdit.text()
            if threshholdVal == '':
                threshholdVal = 125
            else:
                threshholdVal = int(threshholdVal)
            ret3, self.thresholdImg = cv.threshold(img, threshholdVal, 255, cv.THRESH_BINARY)

        if self.GaussThresholdRadio.isChecked():
            self.thresholdImg = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                                     cv.THRESH_BINARY, block_size, 2)

        if self.MeanThresholdRadio.isChecked():
            self.thresholdImg = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, \
                                                     cv.THRESH_BINARY, block_size, 2)

        if self.OTSUThresholdRadio.isChecked():
            ret3, self.thresholdImg = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

        if self.isSaveThresImgCheck.isChecked():
            self.imgCopy = self.thresholdImg

        self.imgItem.setImage(self.thresholdImg)
        self.currentImg = self.thresholdImg
        self.showHist()


class MorphologicalTransformations(ImageShow):
    def __init__(self, parent=None):
        super(MorphologicalTransformations, self).__init__(parent)
        self.BlackHatBtn.clicked.connect(self.blackHat)
        self.TopHatBtn.clicked.connect(self.topHat)
        self.ErosionBtn.clicked.connect(self.erosion)
        self.DilationBtn.clicked.connect(self.dilation)


    def blackHat(self):
        kernel = self.getKernel()
        self.MorphImg = cv.morphologyEx(self.imgCopy, cv.MORPH_BLACKHAT, kernel)
        self.endMorph()

    def topHat(self):
        kernel = self.getKernel()
        self.MorphImg = cv.morphologyEx(self.imgCopy, cv.MORPH_BLACKHAT, kernel)
        self.endMorph()

    def dilation(self):
        kernel = self.getKernel()
        iteration = int(self.MorphInterationEdit.text())
        self.MorphImg = cv.dilate(self.imgCopy, kernel, iterations=iteration)
        self.endMorph()

    def erosion(self):
        kernel = self.getKernel()
        iteration = int(self.MorphInterationEdit.text())
        self.MorphImg = cv.erode(self.imgCopy, kernel, iterations=iteration)
        self.endMorph()

    def endMorph(self):
        if self.isSaveMorphImgCheck.isChecked():
            self.imgCopy = self.MorphImg

        self.imgItem.setImage(self.MorphImg)
        self.currentImg = self.MorphImg
        self.showHist()

    def getKernel(self):
        kernel_size = int(self.MorphKernelSizeEdit.text())
        kernel_size = (kernel_size, kernel_size)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        if self.MorphElliRadio.isChecked():
            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, kernel_size)

        if self.MorphRectRadio.isChecked():
            kernel = cv.getStructuringElement(cv.MORPH_RECT, kernel_size)

        if self.MorphCrossRadio.isChecked():
            kernel = cv.getStructuringElement(cv.MORPH_CROSS, kernel_size)

        return kernel


class ImageAnalysisWidget(Contrast, Blur, Rectification, Threshold,MorphologicalTransformations):

    def __init__(self, parent=None):
        super(ImageAnalysisWidget, self).__init__(parent)

        self.HoughCircleBtn.clicked.connect(self.HoughCircle)
        self.FindRectBtn.clicked.connect(self.FindContour)


    def HoughCircle(self):
        # app = QApplication(sys.argv)
        self.newWindow = HoughCircleWidget(self.currentImg)
        self.newWindow.show()
        # sys.exit(app.exec_())

    def FindContour(self):
        self.newWindow1 = ContourFindWidget(self.currentImg)
        self.newWindow1.show()



class ContourFindWidget(QWidget, HoughUI):
    def __init__(self, image, parent=None):
        super(ContourFindWidget, self).__init__(parent)
        self.setupUi(self)
        self.img = image
        self.newWindowUI()

    def newWindowUI(self):
        self.resize(500, 700)
        self.move(200, 200)
        cimage= cv.cvtColor(self.img, cv.COLOR_GRAY2BGR)
        cnts, hierarchy = cv.findContours(self.img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        print(len(cnts))
        for cnt in cnts:
            x, y, w, h = cv.boundingRect(cnt)
            cv.rectangle(cimage, (x, y), (x + w, y + h), (0, 255, 0), 2)

        self.showImgWindow = pg.GraphicsLayoutWidget()
        self.gridLayout.addWidget(self.showImgWindow)
        self.imgItem = pg.ImageItem()
        self.imgPlot = self.showImgWindow.addPlot(title="")

        self.imgPlot.addItem(self.imgItem)
        self.imgItem.setImage(cimage)


class HoughCircleWidget(QWidget, HoughUI):
    def __init__(self, image, parent=None):
        super(HoughCircleWidget, self).__init__(parent)
        self.setupUi(self)
        self.img = image
        self.newWindowUI()

    def newWindowUI(self):
        self.resize(500, 700)
        self.move(200, 200)
        cimage, _ = HoughCircleDetect(self.img, self.img)

        self.showImgWindow = pg.GraphicsLayoutWidget()
        self.gridLayout.addWidget(self.showImgWindow)
        self.imgItem = pg.ImageItem()
        self.imgPlot = self.showImgWindow.addPlot(title="")

        self.imgPlot.addItem(self.imgItem)
        self.imgItem.setImage(cimage)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = ImageAnalysisWidget()
    myWin.show()
    sys.exit(app.exec_())
