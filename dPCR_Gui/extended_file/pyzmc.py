import platform
import ctypes
import time

systype = platform.system()
if systype == 'Windows':
    if platform.architecture()[0] == '64bit':
        zmcdll = ctypes.WinDLL('..\extended_file\zmotion.dll')
        zauxdll = ctypes.WinDLL('..\extended_file\zauxdll.dll')
        print('Windows x64')
    else:
        zmcdll = ctypes.WinDLL('./zmotion32.dll')
        print('Windows x86')
elif systype == 'Darwin':
    zmcdll = ctypes.CDLL('./zmotion.dylib')
    print("macOS")
elif systype == 'Linux':
    zmcdll = ctypes.CDLL('./zmotion.so')
    print("Linux")
else:
    print("OS Not Supported!!")


class ZMCWrapper:
    current_axis = 0
    current_speed = 0
    current_move_distance = 0
    current_unit = 0

    def __init__(self):
        self.handle = ctypes.c_void_p()
        self.sys_ip = ""
        self.sys_info = ""
        self.is_connected = False

    def DownZar(self, file):
        # file = '.\\ZDevelop.zar'
        cmd2 = ctypes.c_char_p(bytes(file, 'utf-8'))
        zmcdll.ZMC_DownZar(self.handle, cmd2)

    def Zmc_Execute(self, string):
        cmdbuffer = (ctypes.c_char * 2048)()
        cmd2 = ctypes.c_char_p(bytes(string, 'utf-8'))
        zmcdll.ZMC_Execute(self.handle, cmd2, 10, cmdbuffer, 2048)

    def Zmc_DriectCommand(self, string):
        cmdbuffer = (ctypes.c_char * 2048)()
        cmd2 = ctypes.c_char_p(bytes(string, 'utf-8'))
        zmcdll.ZMC_DirectCommand(self.handle, cmd2, cmdbuffer, 2048)

    def search(self, console=[]):
        iplist = ctypes.create_string_buffer(b'', 1024)  # create_string_buffer创建的是一个 ANSI 标准的 C类型字符串
        zmcdll.ZMC_SearchEth(ctypes.byref(iplist), 1024, 200)
        s = iplist.value.decode()
        str_iplist = s.split()
        num = len(str_iplist)
        print(num, "Controller(s) Found:")
        print(*str_iplist, sep='\n')
        console.append("Searching...")
        console.append(str(num) + " Controller(s) Found:")
        return str_iplist, num

    def connect(self, ip, console=[]):
        if self.handle.value is not None:
            self.disconnect()
        ip_bytes = ip.encode('utf-8')
        p_ip = ctypes.c_char_p(ip_bytes)
        print("Connecting to", ip, "...")

        ret = zmcdll.ZMC_OpenEth(p_ip, ctypes.pointer(self.handle))
        print(ret)
        msg = "Connected"
        if ret == 0:
            print("Connected")
            msg = ip + " Connected"
            self.sys_info = self.read_info()
            self.sys_ip = ip
            self.is_connected = True
        else:
            # print("Error", ret)
            msg = "Connection Failed, Error " + str(ret)
            self.is_connected = False
        console.append(msg)
        console.append(self.sys_info)
        return ret

    def disconnect(self):
        ret = zmcdll.ZMC_Close(self.handle)
        self.is_connected = False
        return ret

    def read_info(self):
        cname = ctypes.create_string_buffer(b'', 32)
        fVersion = ctypes.c_float()
        date = ctypes.c_uint32()
        zmcdll.ZMC_GetSoftVersion(self.handle, ctypes.byref(fVersion), ctypes.byref(cname), ctypes.byref(date))
        # print("%.2f" % fVersion.value, cname.value, date.value)
        info = cname.value.decode() + " Version:" + str("%.2f" % fVersion.value) + " Date:" + str(date.value)
        # print(info)
        return info

    # 读取多个轴的mpos
    def get_ax_pos(self, ax_num):
        # ZMC_Modbus_Get4x(handle, 11000, imaxaxises*2, (uint16 *)pValueList);
        ax_pos = (ctypes.c_float * ax_num)()
        zmcdll.ZMC_Modbus_Get4x(self.handle, 11000, ax_num * 2, ctypes.byref(ax_pos))
        return ax_pos

    def set_4x_pos(self, addr, anum):
        # ZMC_Modbus_Get4x(handle, 11000, imaxaxises*2, (uint16 *)pValueList);
        sx_pos = (ctypes.c_ushort * anum)()
        sx_pos[0] = 300
        sx_pos[1] = 400
        sx_pos[2] = 500
        sx_pos[3] = 600

        result = zmcdll.ZMC_Modbus_Set4x(self.handle, addr, anum, ctypes.byref(sx_pos))
        print(*sx_pos)
        return sx_pos

    def get_4x_pos(self, addr, anum):
        gx_pos = (ctypes.c_ushort * anum)()
        result = zmcdll.ZMC_Modbus_Get4x(self.handle, addr, anum, ctypes.byref(gx_pos))
        print(result)
        return gx_pos

    def get_dpos(self, iaxis):
        cmdbuffer = (ctypes.c_char * 2048)()
        str(cmdbuffer, encoding='utf-8')
        str1 = "?DPOS"
        cmd = ctypes.c_char_p(bytes(str1, 'utf-8'))

        zmcdll.ZMC_DirectCommand(self.handle, cmd, cmdbuffer, 2048)

        a = list(cmdbuffer)

        b = b''.join(a)
        # print(b)
        c = b.decode().strip(b'\x00'.decode())
        return c

        # str(*cmdbuffer, encoding='utf-8')
        # bytes.decode(*cmdbuffer)
        # print(*cmdbuffer)

        # print(list[1])

    # it=re.finditer(r"\d+",str1)
    # for match in it:
    # print(match.group())

    # 移动轴
    def move(self, distance):
        str1 = "MOVE(%d)" % distance
        self.Zmc_DriectCommand(str1)

    # 获取某轴速度
    def get_mspeed(self, iaxis):
        cmdbuffer = (ctypes.c_char * 2048)()
        str(cmdbuffer, encoding='utf-8')
        str1 = "?speed(%d)" % iaxis
        cmd = ctypes.c_char_p(bytes(str1, 'utf-8'))

        zmcdll.ZMC_DirectCommand(self.handle, cmd, cmdbuffer, 2048)

        a = list(cmdbuffer)

        b = b''.join(a)
        # print(b)
        c = b.decode().strip(b'\x00'.decode())
        return c

    def set_creep(self, creep):
        str1 = 'CREEP = %d' % creep
        self.Zmc_DriectCommand(str1)

    # 选轴
    def base(self, iaxis):
        str1 = "BASE(%d)" % iaxis
        self.Zmc_DriectCommand(str1)
        self.current_axis = iaxis

    # 设定加速度
    def set_accel(self, accel):
        str1 = "ACCEL = %d" % accel
        self.current_speed = accel
        self.Zmc_DriectCommand(str1)
        print('set_speed 被调用')

    # 设定减速度
    def set_decel(self, decel):
        str1 = "DECEL = %d" % decel
        self.current_speed = decel
        self.Zmc_DriectCommand(str1)
        print('set_speed 被调用')

    # 设定速度
    def set_speed(self, speed):
        str1 = "SPEED = %d" % speed
        self.current_speed = speed
        self.Zmc_DriectCommand(str1)
        print('set_speed 被调用')
    # 设定脉冲大小（单位mm）
    def set_units(self, units):
        str1 = "units = %d" % units
        self.Zmc_DriectCommand(str1)
        self.current_unit = units

    def set_dpos(self, dpos):

        str1 = "DPOS = %d" % dpos
        self.Zmc_DriectCommand(str1)

    # 取消当前运动
    def cancel_move(self, order):
        str1 = "CANCEL(%d)" % order
        self.Zmc_DriectCommand(str1)

    def op(self, ionum1, status):
        str1 = "OP(%d,%d)" % (ionum1, status)
        self.Zmc_DriectCommand(str1)

    def atype(self, type):
        str1 = "ATYPE = %d" % type
        self.Zmc_DriectCommand(str1)

    def SetUserVar(self, var, value):
        value = ctypes.c_float(value)
        var = ctypes.c_char_p(bytes(var, 'utf-8'))
        zauxdll.ZAux_Direct_SetUserVar(self.handle, var, value)

    def Run(self, file):
        str1 = 'Run"%s",1' % file
        self.Zmc_Execute(str1)

    def Vmove(self,direction):
        str1 = "VMOVE(%d)" % direction
        self.Zmc_DriectCommand(str1)


if __name__ == '__main__':
    zmc = ZMCWrapper()

    # iplist,num = zmc.search()

    zmc.connect("192.168.0.11")  # ip连接
    # ret = zmc.disconnect()
    # if ret == 0:
    #     print('disconnect')
    # zmc.read_info()
    # pos = zmc.get_ax_pos(2)
    # print("Axis 0 MPOS:", pos[0])
    # print("Axis 1 MPOS:", pos[1])
    #
    # pos1 = zmc.set_4x_pos(0, 5)
    # # zmc.move(0,500,100)
    # zmc.base(3)
    # zmc.set_units(100)
    # zmc.set_speed(200)
    # zmc.move(-500)

    # zmc.set_accel(10000)
    # zmc.set_decel(1000)
    # for i in range(10):
    #     zmc.move(-100)
    #     time.sleep(0.1)
    # pos2 = zmc.get_4x_pos(200, 1)
    # print(pos2[0])
    # #
    # # zmc.vmove(0,1)

    # number = zmc.get_dpos(1)
    # print(number)

    # speed = zmc.get_mspeed(0)
    # print(speed)

    # # zmc.SetUserVar('backdist', 125)
    # # zmc.SetUserVar('range', 250)
    # # zmc.SetUserVar('astep', 1)
    zmc.Run('ZeroOut.bas')
