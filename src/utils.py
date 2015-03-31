import math
import re

# units
from pint import UnitRegistry
units = UnitRegistry()

# my guess as to why 508 is the magic number is the motor steps and the belt TPI
# i am guessing the belt is 2.54 TPI, and the motor can provide 200 steps
# 2.54 * 200 = 508
units.define('steps = inch / 508.0 = step')

# For SVG files, Silhouette Studio defines one inch as 72 points
units.define('dpi = inch / 72.0')

def steps(val):
    val = unit(val, unit=None)
    return int(val.to("steps").magnitude)

## units

DEFAULT_UNIT = "mm"

def unit(val, **kw):
    _unit = kw.get("unit", DEFAULT_UNIT)
    if _unit != None:
        _unit = units.parse_expression(_unit)
    if type(val) != units.Quantity:
        if type(val) in (int, float):
            assert _unit, "value %r of type '%r' requires a unit definition" % (val, type(val))
            val = val * _unit
        elif type(val) in (str, unicode):
            val = units.parse_expression(val)
        else:
            raise TypeError, "I don't know how to convert type '%s' to a unit" % str(type(val))
    assert type(val) == units.Quantity, "%r != %r" % (type(val), units.Quantity)
    if _unit:
        val = val.to(_unit)
    return val

def inch2mm(inches):
    inches = unit(inches, unit="inch")
    return inches.to(units.mm).magnitude

def mm2inch(mm):
    mm = unit(mm, unit="mm")
    return mm.to(units.inch).magnitude

def circle(**kw):
    assert "radius" in kw, "Need radius keyword argument"
    defs = {"steps": 20, "center_x": "0in", "center_y": "0in", "phase": 0}
    _kw = defs.copy()
    _kw.update(kw)
    _steps = int(_kw["steps"])
    radius = unit(_kw["radius"])
    center_x = unit(_kw["center_x"])
    center_y = unit(_kw["center_y"])
    phase = float(_kw["phase"])
    #
    if steps < 2:
        raise ValueError, "3 or more steps are required"
    radstep = (2 * math.pi) / float(_steps - 1)
    for rad in range(int(_steps)):
        x = math.cos(rad * radstep + phase) * radius + center_x
        y = math.sin(rad * radstep + phase) * radius + center_y
        yield (steps(x), steps(y))
