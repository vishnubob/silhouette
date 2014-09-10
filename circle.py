import argparse
import sys
import math
from silhouette import *

def log(msg):
    ts = time.strftime("%c")
    msg = "%s] %s" % (ts, msg)
    sys.stdout.write(msg)
    sys.stdout.flush()

class Worker(object):
    def __init__(self):
        self.cutter = Silhouette()
        self.cutter.connect()
        self.cutter.speed = 1
        self.cutter.home()

    def cut_circle(self, **kw):
        points = circle(**kw)
        points = list(points)
        self.cutter.position = points[0]
        self.cutter.draw(points)

    def iter_cut(self, **kw):
        cnt = 0
        kwstr = 'Cutting circle:\n    radius: %(radius)s, steps: %(steps)s, center: (%(center_x)s, %(center_y)s)' % kw
        msg = "%s\n" % kw
        log(msg)
        reps = kw.get("repeat", 1)
        minp = kw.get("min_pressure", 1)
        maxp = kw.get("max_pressure", 1)
        for pressure in range(minp, maxp + 1):
            for rep in range(reps):
                cnt += 1
                msg = "Run #%d, repeat #%d/%d, pressure: %d\n" % (cnt, rep + 1, reps, pressure)
                log(msg)
                self.cutter.pressure = pressure
                self.cut_circle(**kw)

Modes = {}

membrane = {
    "steps": 500, 
    "radius": "19mm", 
    "repeat": 2,
    "min_pressure": 1,
    "max_pressure": 10,
}
Modes["membrane"] = membrane

valve_seal_inner = {
    "steps": 500, 
    "radius": "8mm", 
    "repeat": 2,
    "min_pressure": 1,
    "max_pressure": 10,
}
Modes["valve_seal_inner"] = valve_seal_inner

valve_seal_outer = {
    "steps": 500, 
    "radius": "10mm", 
    "repeat": 2,
    "min_pressure": 1,
    "max_pressure": 10,
}
Modes["valve_seal_outer"] = valve_seal_outer

def run_pattern(args, home=True):
    w = Worker()
    w.iter_cut(**args)
    if home:
        w.cutter.home()

def run_mode(mode, args, center=None):
    _mode = Modes.get(mode, None)
    if not _mode:
        raise KeyError, "Mode must be one of %s, not %s" % (str.join(', ', Modes), mode)
    _args = _mode.copy()
    _args.update(args)
    run_pattern(_args)

def cli():
    Defaults = {
        "center_x": 0,
        "center_y": 0,
        "steps": 100,
    }
    parser = argparse.ArgumentParser(description='Cut/draw circles')
    parser.add_argument('-r', '--radius', type=str, help='Radius of circle (1.2in, 3mm, etc)')
    parser.add_argument('-x', '--center-x', type=str, help='X center of circle (1.2in, 3mm, etc)')
    parser.add_argument('-y', '--center-y', type=str, help='Y center of circle (1.2in, 3mm, etc)')
    parser.add_argument('-s', '--steps', type=int, help='The number of points used to draw the circle (resolution)')
    parser.add_argument('-p', '--min-pressure', type=int, help='Min pressure of knife (1-33)')
    parser.add_argument('-P', '--max-pressure', type=int, help='Max pressure of knife (1-33)')
    parser.add_argument('-R', '--repeat', type=int, help='How many times to repeat the cut')
    parser.add_argument('-m', '--mode', type=str, help='Use a predefined mode (see this code)')
    parser.set_defaults(**Defaults)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = cli()
    args = args.__dict__.copy()
    # wash args
    goodkeys = ("radius", "steps", "repeat", "min_pressure", "max_pressure", "center_x", "center_y")
    _args = {k: v for (k, v) in args.items() if (k in goodkeys) and (v != None)}
    if args["mode"]:
        run_mode(args["mode"], _args)
    else:
        run_pattern(_args)
