import usb.core
import usb.util

class Silhouette(object):
    def connect(self):
        # find our device
        self.dev = usb.core.find(idVendor=0x0b4d, idProduct=0x1123)

        # was it found?
        if self.dev is None:
            raise ValueError('Device not found')

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
        assert ep_intr_in is not None

    def read(self, length=1):
        return self.ep_in.read(1)

    def write(self, msg):
        self.ep_out.write(msg)

    def send(self, commands):
        commands = [cmd.encode() for cmd in commands]
        commands = str.join('', commands)
        self.write(commands)


