
from PyQt5.QtWidgets import QApplication, QMainWindow,QWidget
from  my_lib.controler_gui import *


class ControllerWidget(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super(ControllerWidget, self).__init__(parent)
        self.setupUi(self)
        self.init()

    def init(self):
        self.XYSpeedSlider.setMaximum(500)
        self.ZSpeedSlider.setMaximum(100)
        self.XYSpeedSlider.setMinimum(50)
        self.ZSpeedSlider.setMinimum(10)
        self.XYSpeedSlider.setTickInterval(50)
        self.ZSpeedSlider.setTickInterval(10)
        self.XYSpeedSlider.setSingleStep(50)
        self.ZSpeedSlider.setSingleStep(10)

        self.XYSpeedLabel.setText('1um/s')
        self.ZSpeedLabel.setText('10um/s')
        self.XYSpeedSlider.valueChanged.connect(lambda val: self.XYSpeedLabel.setText(str(round(val / 50, 2)) + 'um/s'))
        self.ZSpeedSlider.valueChanged.connect(lambda val: self.ZSpeedLabel.setText(str(round(val, 2)) + 'um/s'))

        self.zPositiveBtn.pressed.connect(
            lambda: self.cont.Motivate(axis='Z', speed=self.ZSpeedSlider.value()/10, direction=1))
        self.zNegativeBtn.pressed.connect(
            lambda: self.cont.Motivate(axis='Z', speed=self.ZSpeedSlider.value()/10, direction=-1))

        self.zPositiveBtn.released.connect(lambda: self.cont.cancel_move(3))
        self.zNegativeBtn.released.connect(lambda: self.cont.cancel_move(3))

        self.yPositiveBtn.pressed.connect(
            lambda: self.cont.Motivate(axis='Y', speed=self.XYSpeedSlider.value(), direction=-1))
        self.yNegativeBtn.pressed.connect(
            lambda: self.cont.Motivate(axis='Y', speed=self.XYSpeedSlider.value(), direction=1))

        self.yPositiveBtn.released.connect(lambda: self.cont.cancel_move(3))
        self.yNegativeBtn.released.connect(lambda: self.cont.cancel_move(3))

        self.xPositiveBtn.pressed.connect(
            lambda: self.cont.Motivate(axis='X', speed=self.XYSpeedSlider.value(), direction=1))
        self.xNegativeBtn.pressed.connect(
            lambda: self.cont.Motivate(axis='X', speed=self.XYSpeedSlider.value(), direction=-1))

        self.xPositiveBtn.released.connect(lambda: self.cont.cancel_move(3))
        self.xNegativeBtn.released.connect(lambda: self.cont.cancel_move(3))




if __name__ == '__main__':
    import sys
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = ControllerWidget()
    myWin.show()
    sys.exit(app.exec_())
