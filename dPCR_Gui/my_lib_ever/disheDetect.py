import sys
import math
from PyQt5.QtWidgets import QWidget, QApplication
import pyqtgraph as pg
from ImageAnalysisTools import *
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from tensorflow import keras
from keras_preprocessing import image

new_model = keras.models.load_model(r'.\my_lib_ever\dish_detect.h5')

def cv_show(name, img):
    cv.namedWindow(name, cv.WINDOW_NORMAL)  # 设置为WINDOW_NORMAL可以任意缩放
    cv.imshow(name, img)
    cv.waitKey(0)
    cv.destroyAllWindows()

class circleDetect:
    def __init__(self):
        pass


    def detect(self, img):

        rectify_tools = RectificationTools()
        rectImg = rectify_tools.imageRectification(img)
        rectImg = cv.medianBlur(rectImg, 3)
        clahe = cv.createCLAHE(clipLimit=60, tileGridSize=(35, 35))
        self.clahe_img = clahe.apply(rectImg)
        self.contrastImg = cv.convertScaleAbs(rectImg, alpha=6, beta=10)
        self.color_image = cv.cvtColor(self.contrastImg, cv.COLOR_BAYER_GR2BGR)
        circles = self.dishesLocal()
        self.predict(circles)



    def dishesLocal(self):
        '''
        对图片中的培养皿进行定位，返回所有定位的圆
        :return:
        '''
        y_sum_gray = np.sum(self.clahe_img, axis=1) #将图片横向累加
        y_sum_gray = y_sum_gray / np.max(y_sum_gray) #归一化
        y_set = self.findMaximumValue(y_sum_gray, 10, mode='y') #寻找极大值点
        self.circles = []
        for y in y_set:
            block = self.clahe_img[y - 8:y + 8, :]
            x_sum_gray = np.sum(block, axis=0)
            x_sum_gray = x_sum_gray / np.max(x_sum_gray)
            x_set = self.findMaximumValue(x_sum_gray, 15)
            for x in x_set:
                self.circles.append((x, y))

        return self.circles

    def predict(self, circles):
        self.bad_dishes = 0
        self.bright_dishes = 0
        self.dark_dishes = 0

        circleNum = len(circles)
        circles_array = np.zeros((circleNum, 64, 64))
        pos = dict()
        invalid_index = 0
        k = 0
        for circle in circles:
            x = circle[0]
            y = circle[1]
            img, ret = self.getImage(x, y, self.clahe_img)
            if ret == 0:
                invalid_index += 1
                continue
            circles_array[k] = img
            pos[k] = (x, y)
            k += 1

        valid_circles = circles_array[:-invalid_index].reshape((-1, 64, 64, 1))
        predictions = new_model.predict(valid_circles)

        for index, result in enumerate(predictions):
            x = pos[index][0]
            y = pos[index][1]
            r = 8
            if result < 0.5:
                cv.circle(self.color_image, (x, y), r, (255, 0, 0), 1)
                self.bad_dishes += 1
            if result > 0.5:
                img, ret = self.getImage(x, y, self.contrastImg)
                gray_level = np.mean(img)
                if gray_level > 140:
                    cv.circle(self.color_image, (x, y), r, (255, 255, 0), 2)
                    self.bright_dishes += 1
                else:
                    cv.circle(self.color_image, (x, y), r, (0, 255, 0), 1)
                    self.dark_dishes += 1

    def circleLocationGraph(self):
        color_image = cv.cvtColor(self.contrastImg, cv.COLOR_BAYER_GR2BGR)

        for circle in self.circles:
            x, y = circle
            r = 8
            cv.circle(color_image, (x, y), r, (0, 255, 255), 2)

        return color_image

    def findMaximumValue(self, data, interval, mode='x'):
        """
        用于求一组数的极大值点：若该点的前3三个点为正，后3个点为负，并且与上个点之间间距大于一定的间隔被判定为极大值点
        如若是x方向寻找峰值，则还会考虑两极大值点不能超过多少间隔

        :param data: 一维数组
        :param interval: 两极大值最小间距
        :param mode: mode 分 'x' 和'y'两种, 'x'模式除了考虑x之间峰值点的最小间距也会考虑x之间峰值点的最大间距，
        当x之间间距过大时，会在两峰值之间插入一个中间值
        :return: 极大值列表
        """

        maxValue = [] #用于存放极大值的列表
        diff = np.diff(data) #对数值求导
        index = 1
        Num = len(diff)
        while index < Num - 1:
            front_diff = np.array(diff[index - 3:index - 1])
            behind_diff = np.array(diff[index + 1:index + 3])
            if np.size(front_diff[front_diff < 0]) == 0 and np.size(behind_diff[behind_diff > 0]) == 0:
                if not maxValue:
                    maxValue.append(index)

                if mode == 'x':
                    if index - maxValue[-1] > 30:
                        maxValue.append(int(index - (index - maxValue[-1]) / 2))

                if index - maxValue[-1] > interval:
                    maxValue.append(index)

            index += 1
        return maxValue

    def getImage(self, x, y, img):
        """
        根据圆心坐标截取图片

        :param x: 圆心x坐标
        :param y: 圆心y坐标
        :param img: 被截取的图片
        :return: 圆图
        """
        r = 8
        img_r = np.array(img[y - r:y + r, x - r:x + r])
        if img_r.shape != (2 * r, 2 * r):
            return img_r, 0
        else:
            img_r = cv.resize(img_r, (64, 64))
            return img_r, 1


if __name__ == '__main__':
    img = cv.imread(r'F:\PythonProject\dPCR_Gui\image\FAM_density_high.tif', 2)
    cd = circleDetect()
    color_image, bad_dishes, bright_dishes, dark_dishes = cd.detect(img)
    print('bad_dishes:',bad_dishes,
          'bright_dishes:',bright_dishes,'dark_dishes:',dark_dishes)
    cv_show('color_image',color_image)
