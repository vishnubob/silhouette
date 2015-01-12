import argparse
import sys
import math
import pint
import operator
from silhouette import *

def log(msg):
    ts = time.strftime("%c")
    msg = "%s] %s" % (ts, msg)
    sys.stdout.write(msg)
    sys.stdout.flush()

class Worker(object):
    def __init__(self):
        self._cutter = None

    @property
    def cutter(self):
        if self._cutter == None:
            self._cutter = Silhouette()
            self._cutter.connect()
            self._cutter.speed = 1
            self._cutter.home()
        return self._cutter

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
        total_cycles = ((maxp + 1) - minp) * reps
        phase_step = (2 * math.pi) / total_cycles
        for pressure in range(minp, maxp + 1):
            for rep in range(reps):
                #kw["phase"] = phase_step * cnt
                kw["phase"] = 0
                msg = "Run #%d/%d, repeat #%d/%d, pressure: %d, phase: %0.2f degs\n" % (cnt + 1, total_cycles, rep + 1, reps, pressure, math.degrees(kw["phase"]))
                log(msg)
                self.cutter.pressure = pressure
                self.cut_circle(**kw)
                cnt += 1

class CircleMode(object):
    boiler_plate = {
        "steps": 500, 
        "repeat": 2,
        "min_pressure": 1,
        "max_pressure": 10,
    }
    
    def __init__(self, args):
        self.args = args
        self.worker = Worker()

    def run_circle(self, kw):
        self.worker.iter_cut(**kw)

    def run(self):
        rmap = [(x, unit(y)) for (x, y) in self.radius_map.items()]
        func = operator.itemgetter(1)
        rmap.sort(key=func)
        for (name, radius) in rmap:
            kw = self.boiler_plate.copy()
            kw.update(self.args)
            kw["radius"] = radius
            self.run_circle(kw)
        self.worker.cutter.home()

class Membrane(CircleMode):
    radius_map = {
        "outer": "19mm", 
    }

class MembraneOring(CircleMode):
    radius_map = {
        "outer": "19mm", 
        "inner": "15mm", 
    }

class ValveSeal(CircleMode):
    radius_map = {
        "outer": "10mm",
        "inner": "8mm", 
    }

class InletSeal54(CircleMode):
    radius_map = {
        "outer": "7.5mm",
        "inner": "2.5mm",
    }

class InletSeal72(CircleMode):
    radius_map = {
        "outer": "7.5mm",
        "inner": "3mm",
    }

class OutletSeal72(CircleMode):
    radius_map = {
        "outer": "10mm",
        "inner": "4mm",
    }

class InSealValve(CircleMode):
    radius_map = {
        "outer": "7.75mm",
        "inner": "2mm",
    }

class InnerInSeal(CircleMode):
    radius_map = {
        "outer": "10mm",
        "inner": "4mm",
    }


class StretchMembrane(CircleMode):
    #original_radius = 58
    original_radius = 34
    # first membrane, seems to stretch out still
    stretch = 15
    #stretch = 25
    margin = 20
    hole_radius = original_radius - stretch
    outer_radius = hole_radius + margin
    post_radius = 1.5
    post_count = 16

    radius_map = {
        "outer": str(outer_radius) + "mm",
        "post": str(post_radius) + "mm",
        "wreath": str(hole_radius) + "mm",
    }

    def posts(self):
        astep = math.pi * 2 / self.post_count
        for idx in range(self.post_count):
            x = math.cos(astep * idx) * self.hole_radius
            y = math.sin(astep * idx) * self.hole_radius
            yield (x, y)

    def run(self):
        cx = unit(self.args["center_x"])
        cy = unit(self.args["center_y"])
        kw = self.boiler_plate.copy()
        kw["radius"] = unit(self.radius_map["post"])
        kw.update(self.args)
        #
        for (x, y) in self.posts():
            kw["center_x"] = unit(x, unit="mm") + cx
            kw["center_y"] = unit(y, unit="mm") + cy
            self.run_circle(kw)
        # outer radius
        kw["radius"] = unit(self.radius_map["outer"])
        kw["center_x"] = cx
        kw["center_y"] = cy
        self.run_circle(kw)
        self.worker.cutter.home()


class Gasket(CircleMode):
    radius_map = {
        "outer": "19.5mm",
        "inner": "10.0mm",
        "lughole": "2.0mm",
    }
    spoke_radius = "15.5mm"
    lug_holes = 3

    def run(self):
        cx = unit(self.args["center_x"])
        cy = unit(self.args["center_y"])
        kw = self.boiler_plate.copy()
        kw["radius"] = unit(self.radius_map["lughole"])
        kw.update(self.args)
        # lug holes
        astep = (2.0 * math.pi) / self.lug_holes
        radius = unit(self.spoke_radius)
        for step in range(self.lug_holes):
            x = math.cos(astep * step) * radius + cx
            y = math.sin(astep * step) * radius + cy
            kw["center_x"] = x
            kw["center_y"] = y
            self.run_circle(kw)
        # inner radius
        kw["radius"] = self.radius_map["inner"]
        kw["center_x"] = cx
        kw["center_y"] = cy
        self.run_circle(kw)
        # outer radius
        kw["radius"] = self.radius_map["outer"]
        kw["center_x"] = cx
        kw["center_y"] = cy
        self.run_circle(kw)
        self.worker.cutter.home()

Modes = [mode for mode in globals().values() if (type(mode) == type) and issubclass(mode, CircleMode)]

def run_pattern(args, home=True):
    w = Worker()
    w.iter_cut(**args)
    if home:
        w.cutter.home()

def run_mode(mode, args, center=None):
    mmap = {m.__name__.lower(): m for m in Modes}
    mode = mode.lower()
    _mode = mmap.get(mode, None)
    if not _mode:
        raise KeyError, "Mode must be one of %s, not %s" % (str.join(', ', mmap), mode)
    mode = _mode(args)
    mode.run()

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
