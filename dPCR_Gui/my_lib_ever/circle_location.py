import sys
import math
from PyQt5.QtWidgets import QWidget, QApplication
import pyqtgraph as pg
from ImageAnalysisTools import *
from my_lib.HoughCircle import HoughUI
from sklearn.linear_model import LinearRegression

from tensorflow import keras
from keras_preprocessing import image

#
new_model = keras.models.load_model(r'F:\PythonProject\dPCR_Gui\good_bad_dishes.h5')


def cv_show(name, img):
    cv.namedWindow(name, cv.WINDOW_NORMAL)  # 设置为WINDOW_NORMAL可以任意缩放
    cv.imshow(name, img)
    cv.waitKey(0)
    cv.destroyAllWindows()


def widget_show(img):
    if len(img.shape) == 2:
        img = img.T
    if len(img.shape) == 3:
        img = np.transpose(img, axes=[1, 0, 2])
    app = QApplication(sys.argv)

    cv_show = HoughCircleWidget(img)
    cv_show.show()
    sys.exit(app.exec_())


class HoughCircleWidget(QWidget, HoughUI):
    def __init__(self, image, parent=None):
        super(HoughCircleWidget, self).__init__(parent)
        self.setupUi(self)
        self.img = image
        self.newWindowUI()

    def newWindowUI(self):
        self.resize(500, 700)
        self.move(200, 200)
        self.showImgWindow = pg.GraphicsLayoutWidget()
        self.gridLayout.addWidget(self.showImgWindow)
        self.imgItem = pg.ImageItem()
        self.imgPlot = self.showImgWindow.addPlot(title="")

        self.imgPlot.addItem(self.imgItem)
        self.imgItem.setImage(self.img)


class Block:
    def __init__(self):
        self.circles = []  # Block 所有圆坐标
        self.y = []  # Block 圆所有y坐标
        self.average = None  # Block 圆y坐标均值
        self.upperCircle = []  # 存放位于Block 上部的圆坐标
        self.downerCircle = []  # 存放位于Block 下部的圆坐标
        self.upperCircleY_average = None  # Block 上部的圆y坐标均值
        self.downerCircleY_average = None  # Block 下部的圆y坐标均值

    def addCircle(self, circle):
        self.circles.append(circle)
        self.y.append(circle[1])
        self.average = np.mean(self.y)

    def binary_classification(self):
        """
        将圆进行上下两层的分类
        :return:
        """
        for circle in self.circles:
            if circle[1] < self.average:
                self.upperCircle.append(circle)

            else:
                self.downerCircle.append(circle)

        self.upperCircleY_average = np.mean([i[1] for i in self.upperCircle])
        self.downerCircleY_average = np.mean([i[1] for i in self.downerCircle])

        return self.upperCircle, self.downerCircle


class Blocks:
    def __init__(self, blocks, ystart, ymax):
        self.upperCircles = []
        self.downerCircles = []
        self.average = []
        self.diff = None
        self.std = None
        self.averageUpperY = []
        self.averageDownerY = []

        self.global_upperY = []
        self.global_dowerY = []

        self.blocks = blocks
        self.y_start = ystart
        self.y_max = ymax
        self.blockPrecessing()
        self.CalculateStd()
        self.upperY = self.fitY(mode='upper')
        self.downerY = self.fitY(mode='downer')
        self.blockY = self.fitY(mode='block')

    def blockPrecessing(self):
        self.blocks = sorted(self.blocks, key=lambda x: x.average)  # 排序
        del self.blocks[0]  # 删除最靠近边缘的两个Block
        del self.blocks[-1]

        for block in self.blocks:
            upperCircle, downerCircle = block.binary_classification()  # 返回各个Block里的上层圆与下层圆
            self.upperCircles.extend(upperCircle)
            self.downerCircles.extend(downerCircle)

    def CalculateStd(self):
        for block in self.blocks:
            self.average.append(block.average)
            self.averageUpperY.append(block.upperCircleY_average)
            self.averageDownerY.append(block.downerCircleY_average)

        self.diff = np.diff(self.average)
        self.std = np.std(self.diff)

    def fitY(self, mode='upper'):
        data = []
        if mode == 'upper':
            data = self.averageUpperY
        if mode == 'downer':
            data = self.averageDownerY

        if mode == 'block':
            data = self.average

        lc = LinearRegression()
        x = np.arange(len(data)).reshape(-1, 1)
        y = np.array(data).astype(np.int) + self.y_start
        reg = lc.fit(x, y)
        x_predict = np.arange(-20, 50).reshape(-1, 1)
        y_predict = reg.predict(x_predict)
        global_y = [int(i) for i in y_predict if 0 < i < 2400]
        return global_y


class Strip:
    def __init__(self):
        self.circles = []
        self.x = []
        self.average = None

    def addCircle(self, circle):
        x = circle[0]
        self.circles.append(circle)
        self.x.append(x)
        self.average = np.mean(self.x)


class Strips:
    def __init__(self, strips, xstart, xmax):
        self.strips = strips  # list
        self.diff = None
        self.std = None
        self.average = []  # strip的average 为圆的x坐标
        self.x_start = xstart
        self.x_max = xmax
        self.stripPrecessing()
        self.CalculateStd()
        self.fitX()

    def stripPrecessing(self):
        self.strips = sorted(self.strips, key=lambda x: x.average)  # 排序
        del self.strips[0]  # 删除最靠近边缘的两个Block
        del self.strips[-1]

    def CalculateStd(self):
        for strip in self.strips:
            self.average.append(strip.average)
        self.diff = np.diff(self.average)
        self.std = np.std(self.diff)

    def fitX(self):
        lc = LinearRegression()
        x = np.arange(len(self.average)).reshape(-1, 1)
        y = np.array(self.average) + self.x_start
        reg = lc.fit(x, y)
        x_predict = np.arange(-400, 400).reshape(-1, 1)
        y_predict = reg.predict(x_predict)
        self.global_x = [int(i) for i in y_predict if 0 < i < self.x_max]
        # self.distortionCorrection()

    def distortionCorrection(self):
        CorrectionX = []

        median = 0.5 * self.x_max
        dist_max = self.x_max - median

        compensateValuelist = []

        for x in self.global_x:
            vector = x - median
            a = 2.5 * ((abs(vector)) / dist_max) - 1
            compensateValue = math.floor(np.exp(a))
            compensateValuelist.append((vector, compensateValue))
            if vector >= 0:
                CorrectionX.append(x + compensateValue)
            else:
                CorrectionX.append(x - compensateValue)

        self.global_x = CorrectionX


class circleLocation(RectificationTools):
    def __init__(self):
        super(circleLocation, self).__init__()
        self.img = cv.imread(r'F:\PythonProject\dPCR_Gui\image\FAM_density_mid.tif', 2)

    def run(self):

        self.rectImg = self.imageRectification(self.img)

        clahe = cv.createCLAHE(clipLimit=40, tileGridSize=(35, 35))
        self.dst = clahe.apply(self.rectImg)

        self.contrastImg = cv.convertScaleAbs(self.rectImg, alpha=5, beta=10)

        self.x_max = self.rectImg.shape[1]
        self.y_max = self.rectImg.shape[0]

        x_start = 500
        y_start = 400
        centre_part = self.dst[y_start:2000, x_start:3000]
        centre_part_gauss = cv.GaussianBlur(centre_part, (5, 5), 0)
        houghImg, circles = HoughCircleDetect(centre_part_gauss, centre_part_gauss)
        ##########根据所检测的圆进行Block分类############
        blocks = self.Classify(circles=circles, obj=Block, thresValue=25, criterion='y')
        self.Blocks = Blocks(blocks, ystart=y_start, ymax=self.y_max)
        ###############################################

        strips = self.Classify(circles=self.Blocks.upperCircles, obj=Strip, thresValue=10, criterion='x')
        self.upperStrips = Strips(strips, xstart=x_start, xmax=self.x_max)

        strips = self.Classify(circles=self.Blocks.downerCircles, obj=Strip, thresValue=13, criterion='x')
        self.downerStrips = Strips(strips, xstart=x_start, xmax=self.x_max)

        self.upperY = self.Blocks.upperY
        self.downerY = self.Blocks.downerY
        self.blockY = self.Blocks.blockY

        self.upperX = self.upperStrips.global_x
        self.downerX = self.downerStrips.global_x

        # for y_coord in self.blockY:
        #     up = y_coord - 25
        #     if up < 0:
        #         up = 0
        #     img = self.contrastImg[up:y_coord + 25, :]
        #     cv.imwrite(r'F:\PythonProject\dPCR_Gui\blockImg\img{}.jpg'.format(y_coord),img)

        # for y_coord in self.upperY:
        #     img = self.contrastImg[y_coord - 10:y_coord + 10, :]
        #     kernel = cv.getStructuringElement(cv.MORPH_RECT,(5,5))
        #     tophat = cv.morphologyEx(img, cv.MORPH_TOPHAT, kernel)
        #
        #     widget_show(tophat)

        cimg = self.distortionCorrection()

        #

    def Classify(self, circles, obj, thresValue, criterion='x'):
        Group = []
        flag = 0

        for circle in circles:
            value = 0
            if criterion == 'x':
                value = circle[0]
            if criterion == 'y':
                value = circle[1]

            if not Group:  # 组堆里无成员，添加一个成员进入
                member = obj()
                member.addCircle(circle)
                Group.append(member)
                continue

            for member in Group:
                dist = np.abs(member.average - value)  # 计算当前圆的y坐标值与
                if dist < thresValue:
                    member.addCircle(circle)
                    flag = 1
                    break

            if flag == 1:
                flag = 0
                continue

            member = obj()
            member.addCircle(circle)
            Group.append(member)

        return Group

    def distortionCorrection(self):

        self.cimage = self.rectImg.copy()
        self.cimage = cv.convertScaleAbs(self.cimage, alpha=4, beta=10)
        self.jietu = cv.convertScaleAbs(self.rectImg, alpha=5, beta=10)
        self.dst = cv.GaussianBlur(self.dst, (5, 5), 0)

        # self.dst = cv.cvtColor(self.cimage, cv.COLOR_BAYER_GR2BGR)
        self.cimage = cv.cvtColor(self.dst, cv.COLOR_BAYER_GR2BGR)
        # cv_show('cimage', self.cimage)

        x_proportion = 0.65
        y_proportion = 0.3

        self.x_median = x_proportion * self.x_max
        self.y_median = y_proportion * self.y_max

        if self.x_median > self.x_max / 2:
            dist_max_x = self.x_median
        else:
            dist_max_x = self.x_max - self.x_median

        if self.y_median > self.y_max / 2:
            dist_max_y = self.y_median
        else:
            dist_max_y = self.y_max - self.y_median

        self.dist_max = np.sqrt((dist_max_x) ** 2 + (dist_max_y) ** 2)
        circles_nums = len(self.upperX) * len(self.upperY) + len(self.downerX) * len(self.downerY)
        circles_array = np.zeros((circles_nums, 28, 28, 1))
        circles_position = dict()
        self.circleOrder = 0
        invalid_circle = 0
        for x_upper in self.upperX:
            for y_upper in self.upperY:
                x, y = self.calcNewXY(x_upper, y_upper)
                img = self.saveImg(x, y)
                # if 300 < x < self.x_max - 180 and 180 < y < self.y_max - 180:
                #     invalid_circle += 1
                #     continue

                if img is None:
                    invalid_circle+=1
                    continue
                # if y < 115 or y > 2210:
                #     cv.imwrite(r'F:\sample\bad\circle({},{}).jpg'.format(x, y), img)
                # if 700<x<2300 and 300<y<1700:
                #     cv.imwrite(r'F:\sample\good\circle({},{}).jpg'.format(x, y), img)

                circles_array[self.circleOrder] = img
                circles_position[self.circleOrder] = (x, y)
                self.circleOrder += 1

        for x_downer in self.downerX:
            for y_downer in self.downerY:
                x, y = self.calcNewXY(x_downer, y_downer)
                img = self.saveImg(x, y)
                # if 180 < x < self.x_max-180 and 180< y < self.y_max - 180:
                #     invalid_circle += 1
                #     continue

                if img is None:
                    invalid_circle += 1
                    continue
                # if y <115 or y > 2210:
                #     cv.imwrite(r'F:\sample\bad\circle({},{}).jpg'.format(x,y),img)
                # if 700 < x < 2300 and 300 < y < 1700:
                #     cv.imwrite(r'F:\sample\good\circle({},{}).jpg'.format(x, y), img)

                circles_array[self.circleOrder] = img
                circles_position[self.circleOrder] = (x, y)
                self.circleOrder += 1
        circles_array = circles_array[:-invalid_circle]
        predictions = new_model.predict(circles_array)

        for index, prediction in enumerate(predictions):
            if prediction < 0.5:
                x = circles_position[index][0]
                y = circles_position[index][1]
                r = 7
                cv.circle(self.cimage, (x, y), r, (0, 255, 0), 2)
            if index % 100 == 0:
                print(index / len(predictions))

        cv.circle(self.cimage, (int(self.x_median), int(self.y_median)), 9, (255, 0, 0), 2)
        cv_show('cimage', self.cimage)
        return self.cimage

    def saveImg(self, x, y):
        radius = 9
        up = y - radius
        down = y + radius
        left = x - radius
        right = x + radius
        if up >= self.y_max:
            return None
        if up < 0:
            up = 1
        if down >= self.y_max:
            down = self.y_max
        if left < 0:
            left = 0
        if right >= self.x_max:
            right = self.x_max

        # if self.circleOrder %200 ==0:

        # temp = self.cimage.copy()
        # img = self.cimage[up:down, left:right]
        # cv.circle(temp, (x, y), 9, (255, 0, 0), 2)
        # cv.namedWindow('dingwei', cv.WINDOW_NORMAL)  # 设置为WINDOW_NORMAL可以任意缩放
        # cv.imshow('dingwei', temp)
        # cv_show('img',img)

        img = cv.resize(self.dst[up:down, left:right], (28, 28)).reshape((28, 28, 1))

        # print(img.shape,up,down)
        #
        return img
        # if y < 100 or y>self.y_max-100:
        #     cv.imwrite(r'F:\sample\bad\circle{}.jpg'.format(self.circleOrder), img)
        #
        # if 400<x<self.x_max-400 and 400<y<self.y_max-400:
        #     cv.imwrite(r'F:\sample\good\circle{}.jpg'.format(self.circleOrder), img)

        # gamma = 0.2
        # img_norm = img / 255.0  # 注意255.0得采用浮点数
        # img_gamma = np.power(img_norm, gamma) * 255.0
        # img= img_gamma.astype(np.uint8)

        # img = cv.equalizeHist(img)

        # if x < self.x_max/2 and y <self.y_max/2:
        #     cv.imwrite(r'F:\sample\leftup\circle{}.jpg'.format(self.circleOrder), img)
        # if x < self.x_max/2 and y >self.y_max/2:
        #     cv.imwrite(r'F:\sample\leftdown\circle{}.jpg'.format(self.circleOrder), img)
        # if x > self.x_max/2 and y <self.y_max/2:
        #     cv.imwrite(r'F:\sample\rightup\circle{}.jpg'.format(self.circleOrder), img)
        # if x > self.x_max/2 and y >self.y_max/2:
        #     cv.imwrite(r'F:\sample\rightdown\circle{}.jpg'.format(self.circleOrder), img)
        #

    def calcNewXY(self, x1, y1):
        compensateValuelist = []
        x_vector = x1 - self.x_median
        y_vector = y1 - self.y_median

        vector = np.sqrt((x_vector) ** 2 + (y_vector) ** 2)

        sinTheta = abs(y_vector) / vector
        cosTheta = abs(x_vector) / vector

        a = 2.7 * (vector / self.dist_max) - 1
        c = 2 * np.exp(a)
        compensateValue = c
        # if 0<a < 1:
        #     cv.circle(self.cimage, (x1, y1), 3, (255, 255, 0), 2)
        # if 1 < a < 2:
        #     cv.circle(self.cimage, (x1, y1), 3, (255, 0, 0), 2)
        # #
        # if a <0:
        #     cv.circle(self.cimage, (x1, y1), 3, (255, 0, 255), 2)
        compensateValuelist.append((vector, compensateValue))
        x_compValue = math.floor(compensateValue * cosTheta)
        y_compValue = math.floor(compensateValue * sinTheta)
        if x_vector >= 0:
            x = x1 + x_compValue

        else:
            x = x1 - x_compValue

        if y_vector >= 0:

            y = y1 + y_compValue
        else:
            y = y1 - y_compValue
            pass

        return x, y


if __name__ == '__main__':
    cL = circleLocation()
    cL.run()
