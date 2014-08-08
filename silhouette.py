import usb.core
import usb.util
import sys
import re
import time

def transform_data(data):
    data = data.split(' ')
    res = []
    for datum in data:
        if datum[0] == '(' and datum[-1] == ')':
            datum = datum[1:-1]
            res.append(eval(datum))
    return res

# find our device
dev = usb.core.find(idVendor=0x0b4d, idProduct=0x1123)

# was it found?
if dev is None:
    raise ValueError('Device not found')

dev.reset()
#print dev.get_active_configuration()

# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()

intf = cfg[(0,0)]

ep_out = usb.util.find_descriptor(
    intf,
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

assert ep_out is not None

ep_in = usb.util.find_descriptor(
    intf,
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)

assert ep_in is not None

ep_intr_in = usb.util.find_descriptor(intf, 
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN and usb.util.endpoint_type(e.bEndpointAddress) == usb.util.ENDPOINT_TYPE_INTR)

assert ep_intr_in is not None

def run_script(fn):
    f = open(fn)
    state = None
    for (line_num, line) in enumerate(f):
        line = line.strip()
        line = line.split(',')
        pid = line[1]
        if pid.startswith("DATA"):
            data = line[5]
            data = transform_data(data)
            if state == "out":
                if data != [27, 5]:
                    ep_out.write(data)
                    print "sent", data, sum(data)
                    skip_read = False
                else:
                    skip_read = True
            elif state == "in":
                if skip_read:
                    continue
                for x in range(10):
                    try:
                        res = ep_in.read(20)
                    except:
                        print "TO"
                        time.sleep(.1)
                    if list(res) != data and data[-1] != 3:
                        print "got", res, line_num
                        print "-> expected", data
                    break
        elif pid == "OUT":
            state = "out"
        elif pid == "IN":
            state = "in"
        elif pid == "SETUP":
            state = "setup"
        elif pid == "NAK":
            state = "nak"
        elif pid == "ACK":
            state = "ack"
        elif pid == "SOF":
            state = "sof"
        else:
            state = None
        prevline = line

fn = sys.argv[1]
run_script(fn)
