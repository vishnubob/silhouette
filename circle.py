import math
from silhouette import *

def circle_func(steps=10, radius=1, center_x=0, center_y=0):
    if steps < 2:
        raise ValueError, "3 or more steps are required"
    radstep = (2 * math.pi) / float(steps - 1)
    for rad in range(int(steps)):
        x = math.cos(rad * radstep) * radius + center_x
        y = math.sin(rad * radstep) * radius + center_y
        yield (x, y)

def circle(**kw):
    defs = {"steps": 10, "radius": "1in", "center_x": "2in", "center_y": "2in"}
    _kw = defs.copy()
    _kw.update({key: parse_unit(val) for (key, val) in kw.items()})
    pts = list(circle_func(**_kw))
    return Draw(*pts)

cutter = Silhouette()
cutter.connect()
cutter.home
cutter.speed = 1
cutter.home()
for x in range(10):
    print x
    cutter.pressure = x
    cmd = circle(steps=10 * x + 20, radius="5mm", center_y="%fmm" % (15 * x + 20), center_x="170mm")
    cutter.position = cmd.points[0]
    cutter.send(cmd)
cutter.home()
