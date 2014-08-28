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

