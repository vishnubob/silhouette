import usb.core
import usb.util
from warnings import warn

class SilhouetteException(Exception):
    pass

class Silhouette(object):
    def __init__(self, **kw):
        self.vendor_id = kw.get('vendor_id', 0x0b4d)
        self.product_id = kw.get('product_id', None)

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

    def read(self, length=1):
        return self.ep_in.read(1)

    def write(self, msg):
        self.ep_out.write(msg)

    def send(self, commands):
        commands = [cmd.encode() for cmd in commands]
        commands = str.join('', commands)
        self.write(commands)
