import numpy as np
import cv2 as cv


class RectificationTools:
    def four_point_transform(self, image, pts):
        # 获取输入坐标点
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # 计算输入的w和h值
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # 变换后对应坐标位置
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # 计算变换矩阵
        M = cv.getPerspectiveTransform(rect, dst)
        warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))

        # 返回变换后结果
        return warped

    def order_points(self, pts):
        # 一共4个坐标点
        rect = np.zeros((4, 2), dtype="float32")

        # 按顺序找到对应坐标0123分别是 左上，右上，右下，左下
        # 计算左上，右下
        s = pts.sum(axis=1)
        min_pos = np.argmin(s)
        max_pos = np.argmax(s)
        rect[0] = pts[min_pos]
        rect[2] = pts[max_pos]
        pts = np.delete(pts, [min_pos, max_pos], axis=0)
        # 计算右上和左下
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def imageRectification(self, image):
        img = cv.medianBlur(image, 5)

        clahe = cv.createCLAHE(clipLimit=40, tileGridSize=(35, 35))
        dst = clahe.apply(img)

        kernel = cv.getStructuringElement(cv.MORPH_RECT, (13, 13))  # 膨胀
        dige_dilate = cv.dilate(dst, kernel, iterations=2)
        dige_erode = cv.erode(dige_dilate, kernel, iterations=2)
        thresh = cv.threshold(dige_erode, 0, 255,  # 阈值
                              cv.THRESH_BINARY | cv.THRESH_OTSU)[1]

        contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)  # 寻找轮廓

        cnt = sorted(contours, key=cv.contourArea, reverse=True)[0]
        rect = cv.minAreaRect(cnt)
        box = cv.boxPoints(rect)
        box = np.int0(box)

        self.rectificationImg = self.four_point_transform(img, box)

        return self.rectificationImg


def HoughCircleDetect(detect_image, draw_image):
    circles = cv.HoughCircles(detect_image, cv.HOUGH_GRADIENT, 1, 9, param1=40, param2=15
                              , minRadius=3, maxRadius=11)

    circles = np.uint16(np.around(circles))[0]  # 把circles包含的圆心和半径的值变成整数

    cimage = draw_image.copy()
    cimage = cv.cvtColor(cimage, cv.COLOR_BAYER_GR2BGR)

    for index, i in enumerate(circles):
        x = int(i[0])
        y = int(i[1])
        r = int(i[2])

        cv.circle(cimage, (x, y), r, (0, 255, 0), 2)

    return cimage, circles
