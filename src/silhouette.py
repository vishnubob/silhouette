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
        self._media = gpgl.Media()
        self._offset = gpgl.Offset()
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

    def set_offset(self, offset):
        self._offset.offset = offset
        self.send(self._offset)
    def get_offset(self):
        return self._offset.offset
    offset = property(get_offset, set_offset)

    def set_speed(self, speed):
        self._speed.speed = speed
        self.send(self._speed)
    def get_speed(self):
        return self._speed.speed
    speed = property(get_speed, set_speed)

    def set_media(self, media):
        self._media.media = media
        self.send(self._media)
    def get_media(self):
        return self._media.media
    media = property(get_media, set_media)


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
        reslen = self.ep_out.write("\x1b\x05")
        resp = self.read(2)
        resp = list(resp)
        if len(resp) != 2:
            raise ValueError, "Bad response to status request"
        (status_byte, magic_byte) = resp
        if magic_byte != 0x3:
            raise ValueError, "Status magic byte does not equal 0x03 (0x%02x)" % resp[-1]
        if status_byte == 0x30:
            return "ready"
        if status_byte == 0x31:
            return "moving"
        if status_byte == 0x32:
            return "unloaded"
        return "unknown"
    
    @property
    def ready(self):
        return self.status == "ready"

    @property
    def moving(self):
        return self.status == "moving"

    @property
    def unloaded(self):
        return self.status == "unloaded"

    @property
    def version(self):
        self.write("FG")
        resp = self.read(1000)
        resp = str.join('', map(chr, resp))
        return resp
    
    def wait(self):
        while not self.ready:
            time.sleep(.1)

    def read(self, length=1):
        info = self.ep_in.read(length)
        return info

    def write(self, msg):
        bufsize = self.ep_out.wMaxPacketSize
        idx = 0
        #print str.join(' ', ["%s (0x%02x)" % (x, ord(x)) for x in msg])
        while idx < len(msg):
            submsg = msg[idx:idx + bufsize]
            reslen = self.ep_out.write(submsg)
            #print "[%s:%s] %s" % (idx, idx + bufsize, len(msg))
            assert reslen == len(submsg), "%s != %s" % (reslen, len(submsg))
            idx += bufsize
            if idx < len(msg):
                self.wait()

    def send(self, *commands, **kw):
        block = kw.get('block', True)
        for cmd in commands:
            self.write(cmd.encode())
            if block: 
                self.wait()
