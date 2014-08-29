import math
from silhouette import *

class Worker(object):
    def __init__(self):
        self.cutter = Silhouette()
        self.cutter.connect()
        self.cutter.home
        self.cutter.speed = 1
        self.cutter.home()

    def cut_circle(self, **kw):
        points = circle(**kw)
        points = list(points)
        self.cutter.position = points[0]
        self.cutter.draw(points)

    def iter_cut(self, minp, maxp, ckw, reps=1):
        for pressure in range(minp, maxp + 1):
            for rep in range(reps):
                print "rep:", rep + 1, "pressure:", pressure
                self.cutter.pressure = pressure
                self.cut_circle(**ckw)

membrane_circle = {
    "steps": 500, 
    "radius": "19mm", 
}
membrane_args = (1, 10, membrane_circle, 2)

valve_seal_inner = {
    "steps": 500, 
    "radius": "8mm", 
}
valve_seal_inner_args = (1, 10, valve_seal_inner, 2)

valve_seal_outer = {
    "steps": 500, 
    "radius": "10mm", 
}
valve_seal_outer_args = (1, 10, valve_seal_outer, 2)

def run_pattern(args, center, home=True):
    args[2]["center_x"] = center[0]
    args[2]["center_y"] = center[1]
    w = Worker()
    w.iter_cut(*args)
    if home:
        w.cutter.home()

def run_mode(mode, center):
    if mode == "membrane":
        run_pattern(membrane_args, center)
    elif mode == "vseal":
        run_pattern(valve_seal_inner_args, center, home=False)
        run_pattern(valve_seal_outer_args, center)

center = ("5in", "2.5in")
run_mode("vseal", center)


def membrane():
    run_patter(membrane_args)
