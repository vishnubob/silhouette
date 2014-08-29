import math
import re

def inch(val):
    return int(val * 508)

def mm(val):
    return inch(val * 0.0393701)

def parse_unit(val):
    inch_re = re.compile("([\d\.]+)in(ch)?", re.IGNORECASE)
    mm_re = re.compile("([\d\.]+)m(m)?", re.IGNORECASE)
    val = str(val)
    inch_m = inch_re.match(val)
    mm_m = mm_re.match(val)
    if inch_m:
        val = float(inch_m.group(1))
        return inch(val)
    if mm_m:
        val = float(mm_m.group(1))
        return mm(val)
    return float(val)

def circle(**kw):
    defs = {"steps": 10, "radius": "1in", "center_x": "2in", "center_y": "2in"}
    _kw = defs.copy()
    _kw.update({key: parse_unit(val) for (key, val) in kw.items()})
    steps = _kw["steps"]
    radius = _kw["radius"]
    center_x = _kw["center_x"]
    center_y = _kw["center_y"]
    #
    if steps < 2:
        raise ValueError, "3 or more steps are required"
    radstep = (2 * math.pi) / float(steps - 1)
    for rad in range(int(steps)):
        x = math.cos(rad * radstep) * radius + center_x
        y = math.sin(rad * radstep) * radius + center_y
        yield (x, y)
