import cv2 as cv


class Camera:
    device_manager = gx.DeviceManager()

    def __init__(self, UI):
        self.pics = []  # 用于存储获取的图片
        self.parentUI = UI



        self.isOpen = False
        self.camera_mode = 'live'  # 设置为录像模式

        """Camera Init"""

        self.MonitorCamera()  # 监视相机是否被打开
        self.thread_get_image.end_snap.connect(self.parentUI.DetectionFinished)

    def CaptureStream(self):
        """
        获取数据流
        :return:
        """
        self.cam = self.device_manager.open_device_by_index(1)
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        # set exposure
        self.cam.ExposureTime.set(6000)

        # set gain
        self.cam.Gain.set(0)

        self.stream = self.cam.data_stream[0]
        # self.stream.set_acquisition_buffer_number(50)
        # start data acquisition
        self.cam.stream_on()
        self.isOpen = True

    def TriggerLineOn(self):
        """
        打开外触发
        :return:
        """

        self.cam.TriggerMode.set(gx.GxSwitchEntry.ON)  # 打开相机触发功能
        self.cam.TriggerSource.set(gx.GxTriggerSourceEntry.LINE0)  # 选用线触发，触发线位line0

    def TriggerLineOff(self):
        '''
        关闭外触发
        :return:
        '''
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)  # 关闭相机外触发

    def MonitorCamera(self):
        """用于检测相机是否被展现"""
        dev_num, dev_info_list = self.device_manager.update_device_list()
        if dev_num == 0:
            self.parentUI.CameraView.setText('未找到相机')  # 如果未连接相机 则显示未找到

        else:
            self.parentUI.StatusCam.setText('已连接')
            self.CameraInit()  # 展示相机

    def CameraInit(self):
        self.CaptureStream()  # 如果没打开过，获取相机 打开视频流
        self.timer_live.start(10)
        self.timer_live.timeout.connect(self.ImageSnaping)

    def ImageSnaping(self):
        raw_image = self.stream.get_image(timeout=10)
        if raw_image is not None:
            image = raw_image.get_numpy_array()
            show = cv2.resize(image, (1300, 980))  # 把读到的帧的大小重新设置为 640x480
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                     QtGui.QImage.Format_Grayscale8)  # 把读取到的视频数据变成QImage形式
            self.parentUI.CameraView.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
            return image
        else:
            return None


    def DetectionProcessing(self, file, detect_time=None, snap_num=None, detect_mode=None):
        print('DetectionProcessing被调用了')
        self.TriggerLineOn()
        self.timer_live.stop()  # 相机 Live 停止
        self.camera_mode = 'snap'  # 调整相机模式为拍摄
        self.parentUI.cont.Run(file)  # 运行controler里的测试文件
        self.thread_get_image.detect_time = detect_time  # 设置检测所用时间
        self.thread_get_image.snap_num = snap_num
        self.thread_get_image.detect_mode = detect_mode
        self.stream.flush_queue()  # 清空buffer
        self.thread_get_image.start()  # 开始获取图片