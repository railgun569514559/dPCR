from extended_file.pyzmc import *


class Controller(ZMCWrapper):
    def __init__(self):
        super().__init__()

        self.connect("192.168.0.11")
        self.set_units(50)  # 1um
        self.set_dpos(0)
        self.move_dis = 0


    def Motivate(self, mode: str = None):

        if mode == 'positive':
            self.move(0.1*self.move_dis)

        if mode == 'negative':
            self.move(-0.1*self.move_dis)


    def ChangeSpeed(self, speed: int):
        self.set_speed(speed)
        self.move_dis = speed
