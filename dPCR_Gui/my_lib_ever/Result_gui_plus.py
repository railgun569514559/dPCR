import sys
import pyqtgraph as pg
from my_lib.Result_gui import *
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QListWidgetItem
import numpy as np


class ResultGui(QWidget, Ui_Form):
    picNum = 0

    def __init__(self, parent=None):
        super(ResultGui, self).__init__(parent)
        self.setupUi(self)

        pg.setConfigOptions(antialias=True, imageAxisOrder='row-major')
        self.showResultImgWindow = pg.GraphicsLayoutWidget()
        self.resultImgShowLayout.addWidget(self.showResultImgWindow)

        self.imgPlot = self.showResultImgWindow.addPlot(title="")
        self.imgItem = pg.ImageItem()
        self.imgPlot.addItem(self.imgItem)
        self.testBtn.clicked.connect(self.setResult)
        self.imgListWidget.itemClicked.connect(self.selectPic)
        self.itemInfo = dict()

    def setResult(self, info):
        pic = 'pic{}'.format(self.picNum)
        a = QListWidgetItem()
        self.imgListWidget.addItem(pic)
        self.itemInfo[pic] = info
        self.picNum += 1

    def selectPic(self, item):
        img, brightNum, darkNum, badNum = self.itemInfo[item.text()]
        self.imgItem.setImage(img)
        self.birghtDishesLCD.display(brightNum)
        self.darkDishesLCD.display(darkNum)
        self.badDishesLCD.display(badNum)
        brightProportion = (brightNum / (darkNum + brightNum)) * 100
        self.brightProporLabel.setText(str(brightProportion) + '%')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = ResultGui()
    myWin.show()
    sys.exit(app.exec_())
