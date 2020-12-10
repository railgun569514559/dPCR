# version:1.0.1808.9101
import gxipy as gx
from PIL import Image
import cv2


def cv_show(name, img):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # 设置为WINDOW_NORMAL可以任意缩放
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def acq_color(device, num):
    """
           :brief      acquisition function of color device
           :param      device:     device object[Device]
           :param      num:        number of acquisition images[int]
    """
    for i in range(num):
        # send software trigger command
        device.TriggerSoftware.send_command()

        # get raw image
        raw_image = device.data_stream[0].get_image()
        if raw_image is None:
            print("Getting image failed.")
            continue

        # get RGB image from raw image
        rgb_image = raw_image.convert("RGB")
        if rgb_image is None:
            continue

        # create numpy array with data from raw image
        numpy_image = rgb_image.get_numpy_array()
        if numpy_image is None:
            continue

        # show acquired image
        img = Image.fromarray(numpy_image, 'RGB')
        img.show()

        # print height, width, and frame ID of the acquisition image
        print("Frame ID: %d   Height: %d   Width: %d"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))


def acq_mono(device, num):
    """
           :brief      acquisition function of mono device
           :param      device:     device object[Device]
           :param      num:        number of acquisition images[int]
    """
    for i in range(num):
        # send software trigger command
        device.TriggerSoftware.send_command()

        # get raw image
        raw_image = device.data_stream[0].get_image()
        if raw_image is None:
            print("Getting image failed.")
            continue

        # create numpy array with data from raw image
        numpy_image = raw_image.get_numpy_array()
        if numpy_image is None:
            continue

        # show acquired image
        cv_show('picture',numpy_image)

        # print height, width, and frame ID of the acquisition image
        print("Frame ID: %d   Height: %d   Width: %d"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))


def main():
    # print the demo information
    print("")
    print("-------------------------------------------------------------")
    print("Sample to show how to acquire mono or color image continuously according to camera type "
          "and show acquired image.")
    print("-------------------------------------------------------------")
    print("")
    print("Initializing......")
    print("")

    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num is 0:
        print("Number of enumerated devices is 0")
        return

    # open the first device
    cam = device_manager.open_device_by_index(1)

    # set exposure
    cam.ExposureTime.set(10000)

    # set gain
    cam.Gain.set(10.0)

    # send software trigger command
    cam.TriggerMode.set(gx.GxSwitchEntry.ON)
    cam.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)

    # start data acquisition
    cam.stream_on()

    # camera is color
    if cam.PixelColorFilter.is_implemented() is True:
        acq_color(cam, 1)
    # camera is mono
    else:
        acq_mono(cam, 1)

    # stop acquisition
    cam.stream_off()

    # close device
    cam.close_device()


if __name__ == "__main__":
    main()
