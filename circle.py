import argparse
import sys
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

def run_pattern(args, center=None, home=True):
    if center:
        args[2]["center_x"] = center[0]
        args[2]["center_y"] = center[1]
    w = Worker()
    w.iter_cut(*args)
    if home:
        w.cutter.home()

def run_mode(mode, center=None):
    if mode == "membrane":
        run_pattern(membrane_args, center)
    elif mode == "vseal":
        run_pattern(valve_seal_inner_args, center, home=False)
        run_pattern(valve_seal_outer_args, center)

def cli():
    Defaults = {
        'radius': 0,
        'repeat': 2,
        'center_x': 0,
        'center_y': 0,
        'min_pressure': 1,
        'max_pressure': 10,
        'steps': 100,
    }

    parser = argparse.ArgumentParser(description='Cut/draw circles')
    parser.add_argument('-r', '--radius', type=str, help='Radius of circle')
    parser.add_argument('-R', '--repeat', type=int, help='How many times to repeat the cut')
    parser.add_argument('-p', '--min-pressure', type=int, help='Min pressure')
    parser.add_argument('-P', '--max-pressure', type=int, help='Max pressure')
    parser.add_argument('-x', '--center-x', type=str, help='X center of circle')
    parser.add_argument('-y', '--center-y', type=str, help='Y center of circle')
    parser.add_argument('-s', '--steps', type=int, help='Number of points in circle')
    parser.add_argument('-m', '--mode', type=str, help='Number of points in circle')
    parser.set_defaults(**Defaults)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = cli()
    if args.mode:
        run_mode(args.mode, (args.center_x, args.center_y))
    else:
        ckw = {
            "steps": args.steps, 
            "radius": args.radius,
            "center_x": args.center_x,
            "center_y": args.center_y,
        }
        args = (args.min_pressure, args.max_pressure, ckw, args.repeat)
        run_pattern(args)

