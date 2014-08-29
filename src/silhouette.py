import time
import usb.core
import usb.util
from warnings import warn
import gpgl

class SilhouetteException(Exception):
    pass

class Silhouette(object):
    def __init__(self, **kw):
        self.vendor_id = kw.get('vendor_id', 0x0b4d)
        self.product_id = kw.get('product_id', None)
        self.pos = (0, 0)
        self._pressure = gpgl.Pressure()
        self._speed = gpgl.Speed()
        self._position = None

    def usbscan(self):
        args = {"find_all": True, "idVendor": self.vendor_id}
        if self.product_id:
            args["idProduct"] = self.product_id
        devs = usb.core.find(**args)
        devs = list(devs)
        if not devs:
            msg = "Can not find any devices with vendor_id == %s" % self.vendor_id
            raise SilhouetteException, msg
        if len(devs) > 1:
            msg = "There are multiple devices that match vendor_id == %s, using the first one in the list." % self.vendor_id
            warn(msg)
        return devs[0]

    def connect(self):
        self.dev = self.usbscan()
        self.dev.reset()

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.dev.set_configuration()

        # get an endpoint instance
        cfg = self.dev.get_active_configuration()

        intf = cfg[(0,0)]

        self.ep_out = usb.util.find_descriptor(intf,
            custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        assert self.ep_out is not None

        self.ep_in = usb.util.find_descriptor(intf,
            custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        assert self.ep_in is not None

        self.ep_intr_in = usb.util.find_descriptor(intf, 
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN and usb.util.endpoint_type(e.bEndpointAddress) == usb.util.ENDPOINT_TYPE_INTR)
        assert self.ep_intr_in is not None
        self.init()

    def move(self, pos, rel=True):
        pos = gpgl.Point(*list(pos))
        if self._position == pos:
            return
        if rel:
            rel_pos = pos - self._position
            move = gpgl.RelativeMove(*rel_pos)
        else:
            move = gpgl.Move(*pos)
        self.send(move)
        self._position = gpgl.Point(*pos)

    def get_position(self):
        return self._position
    def set_position(self, pos):
        if self._position == None:
            self.move(pos, rel=False)
        else:
            self.move(pos)
    position = property(get_position, set_position)

    def draw(self, points):
        cmd = gpgl.Draw(*points)
        self.send(cmd)
        self._position = cmd.points[-1]

    def init(self):
        self.write("\x1b\x04")

    def set_speed(self, speed):
        self._speed.speed = speed
        self.send(self._speed)
    def get_speed(self):
        return self._speed.speed
    speed = property(get_speed, set_speed)

    def set_pressure(self, pressure):
        self._pressure = gpgl.Pressure(pressure)
        self.send(self._pressure)
    def get_pressure(self):
        return self._pressure.pressure
    pressure = property(get_pressure, set_pressure)

    def home(self):
        self.send(gpgl.Home())

    @property
    def status(self):
        self.write("\x1b\x05")
        resp = self.read(1000)
        resp = list(resp)
        return resp
    
    @property
    def idle(self):
        return self.status == [48, 3]

    @property
    def version(self):
        self.write("FG")
        resp = self.read(1000)
        resp = str.join('', map(chr, resp))
        return resp
    
    def wait(self):
        while not self.idle:
            time.sleep(.1)

    def read(self, length=1):
        return self.ep_in.read(length)

    def write(self, msg):
        reslen = self.ep_out.write(msg)
        assert reslen == len(msg)

    def send(self, *commands, **kw):
        block = kw.get('block', True)
        for cmd in commands:
            self.write(cmd.encode())
            if block: 
                self.wait()
