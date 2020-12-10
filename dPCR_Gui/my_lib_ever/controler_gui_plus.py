from extended_file.pyzmc import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from my_lib.controler_gui import *
import numpy as np

class ControllerWidget(QWidget, ZMCWrapper, Ui_Form):

    def __init__(self, parent=None):
        super(ControllerWidget, self).__init__(parent)
        self.setupUi(self)
        self.init()
        self.chipPosInit()


    def chipPosInit(self):
        x_range = 3
        y_range = 4
        x_length = 100
        y_length = 90

        number = 1
        self.chip = dict()
        for y in np.linspace(0, y_length, y_range):
            for x in np.linspace(0, x_length, x_range):
                self.chip[number] = (x,y)
                number += 1

        self.Chip1Btn.clicked.connect(lambda :self.MoveToChip(self.chip[1]))
        self.Chip2Btn.clicked.connect(lambda: self.MoveToChip(self.chip[2]))
        self.Chip3Btn.clicked.connect(lambda: self.MoveToChip(self.chip[3]))
        self.Chip4Btn.clicked.connect(lambda: self.MoveToChip(self.chip[4]))
        self.Chip5Btn.clicked.connect(lambda: self.MoveToChip(self.chip[5]))
        self.Chip6Btn.clicked.connect(lambda: self.MoveToChip(self.chip[6]))
        self.Chip7Btn.clicked.connect(lambda: self.MoveToChip(self.chip[7]))
        self.Chip8Btn.clicked.connect(lambda: self.MoveToChip(self.chip[8]))
        self.Chip9Btn.clicked.connect(lambda: self.MoveToChip(self.chip[9]))
        self.Chip10Btn.clicked.connect(lambda: self.MoveToChip(self.chip[10]))
        self.Chip11Btn.clicked.connect(lambda: self.MoveToChip(self.chip[11]))
        self.Chip12Btn.clicked.connect(lambda: self.MoveToChip(self.chip[12]))




    def init(self):
        self.connect("192.168.0.11")
        self.set_units(50)  # 1um
        self.set_dpos(0)
        self.move_dis = 0

        self.XYSpeedSlider.setMaximum(50)
        self.ZSpeedSlider.setMaximum(2)
        self.XYSpeedSlider.setMinimum(10)
        self.ZSpeedSlider.setMinimum(1)
        self.XYSpeedSlider.setTickInterval(2)
        self.ZSpeedSlider.setTickInterval(1)
        self.XYSpeedSlider.setSingleStep(1)
        self.ZSpeedSlider.setSingleStep(1)

        self.XYSpeedLabel.setText('1mm/s')
        self.ZSpeedLabel.setText('1m/s')
        self.XYSpeedSlider.valueChanged.connect(lambda val: self.XYSpeedLabel.setText(str(round(val / 10, 2)) + 'mm/s'))
        self.ZSpeedSlider.valueChanged.connect(lambda val: self.ZSpeedLabel.setText(str(round(val, 2)) + 'um/s'))

        self.zPositiveBtn.pressed.connect(
            lambda: self.Motivate(axis='Z', speed=self.ZSpeedSlider.value(), direction=1))
        self.zNegativeBtn.pressed.connect(
            lambda: self.Motivate(axis='Z', speed=self.ZSpeedSlider.value(), direction=-1))

        self.zPositiveBtn.released.connect(lambda: self.cancel_move(3))
        self.zNegativeBtn.released.connect(lambda: self.cancel_move(3))

        self.yPositiveBtn.pressed.connect(
            lambda: self.Motivate(axis='Y', speed=self.XYSpeedSlider.value(), direction=1))
        self.yNegativeBtn.pressed.connect(
            lambda: self.Motivate(axis='Y', speed=self.XYSpeedSlider.value(), direction=-1))

        self.yPositiveBtn.released.connect(lambda: self.cancel_move(3))
        self.yNegativeBtn.released.connect(lambda: self.cancel_move(3))

        self.xPositiveBtn.pressed.connect(
            lambda: self.Motivate(axis='X', speed=self.XYSpeedSlider.value(), direction=-1))
        self.xNegativeBtn.pressed.connect(
            lambda: self.Motivate(axis='X', speed=self.XYSpeedSlider.value(), direction=1))

        self.xPositiveBtn.released.connect(lambda: self.cancel_move(3))
        self.xNegativeBtn.released.connect(lambda: self.cancel_move(3))

        self.ZeroOutBtn.clicked.connect(lambda :self.Run('ZeroOut.bas'))

    def Motivate(self, axis, speed, direction):
        if axis == 'X':
            self.base(0)
            self.set_units(100)  # 一个units = 100um

            self.set_speed(speed)
            self.set_accel(50)
            self.set_decel(50)

        if axis == 'Y':
            self.base(1)
            self.set_units(100)  # 一个units = 100um

            self.set_speed(speed)
            self.set_accel(50)
            self.set_decel(50)
            print('Y移动被调用')
        if axis == 'Z':
            self.base(2)
            self.set_units(500)  # 500脉冲0.5mm
            speed = speed *2
            self.set_speed(speed)
            self.set_accel(8)
            self.set_decel(8)

        if direction == 1:
            self.table_move(500)

        if direction == -1:
            self.table_move(-500)

    def MoveToChip(self,coord):
        x,y = coord
        self.SetUserVar('xcoord',x)
        self.SetUserVar('ycoord',y)
        self.Run('MoveToChip.bas')


if __name__ == '__main__':
    import sys

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = ControllerWidget()
    myWin.show()
    sys.exit(app.exec_())
