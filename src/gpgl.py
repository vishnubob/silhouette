import math

class GPGL_Command(object):
    Name = "__GPGL_Command__"
    Command = ''

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def encode(self, msg=''):
        return "%s%s\x03" % (self.Command, msg)

    def decode(self, msg):
        pass

class Point(object):
    def __init__(self, *args, **kw):
        try: self.x = args[0]
        except: self.x = kw.get('x', 0)
        try: self.y = args[1]
        except: self.y = kw.get('y', 0)

    def __eq__(self, other):
        if other == None:
            return False
        other = Point(*list(other))
        return (self.x == other.x) and (self.y == other.y)
    def __sub__(self, other):
        other = Point(*list(other))
        return Point(self.x - other.x, self.y - other.y)
    def __add__(self, other):
        other = Point(*list(other))
        return Point(self.x + other.x, self.y + other.y)

    def __getitem__(self, idx):
        if idx == 0: return self.x
        if idx == 1: return self.y
        raise IndexError
    
    def __setitem__(self, idx, val):
        if idx == 0: self.x = val
        if idx == 1: self.y = val
        else: raise IndexError

    def __iter__(self):
        return iter([self.x, self.y])
    
    def __str__(self):
        return "%s,%s" % (self.x, self.y)

class Points(list):
    def __init__(self, *args, **kw):
        for arg in args:
            self.append(Point(*arg))

class Move(GPGL_Command):
    Command = 'M'
    
    def __init__(self, *args, **kw):
        self.position = Point(*args, **kw)
        super(Move, self).__init__(*args, **kw)

    def encode(self, msg=''):
        msg = "%s,%s" % (self.position.x, self.position.y)
        return super(Move, self).encode(msg)

class RelativeMove(Move):
    Command = 'O'

class Draw(GPGL_Command):
    Command = 'D'
    
    def __init__(self, *args, **kw):
        self.points = Points(*args, **kw)
        super(Draw, self).__init__(*args, **kw)
    
    def encode(self, msg=''):
        msg = [str(pt) for pt in self.points]
        msg = str.join(',', msg)
        return super(Draw, self).encode(msg)

class RelativeDraw(Draw):
    Command = 'E'

class Home(GPGL_Command):
    Command = 'H'

class Speed(GPGL_Command):
    Command = '!'

    def __init__(self, *args, **kw):
        self.speed = 1
        if args:
            self.speed = args[0]
        super(Speed, self).__init__(*args, **kw)

    def encode(self, msg=''):
        msg = str(self.speed)
        return super(Speed, self).encode(msg)

    def get_speed(self):
        return self._speed
    def set_speed(self, speed):
        self._speed = min(10, max(1, speed))
    speed = property(get_speed, set_speed)

class Media(GPGL_Command):
    Command = 'FW'

    def __init__(self, *args, **kw):
        try: self.media = args[0]
        except: self.media = kw.get('media', 300)
        super(Media, self).__init__(*args, **kw)

    def encode(self, msg=''):
        msg = str(self.media)
        return super(Media, self).encode(self.media)
    
    def set_media(self, val):
        self._media = min(300, max(100, val))
    def get_media(self):
        return self._media
    media = property(get_media, set_media)

class Pressure(GPGL_Command):
    Command = 'FX'

    def __init__(self, *args, **kw):
        try: self.pressure = args[0]
        except: self.pressure = kw.get('pressure', 0)
        super(Pressure, self).__init__(*args, **kw)

    def encode(self, msg=''):
        msg = str(self.pressure)
        return super(Pressure, self).encode(msg)

class Circle(GPGL_Command):
    Command = 'W'

    def __init__(self, *args, **kw):
        self.center = Point(*kw.get("center", (0, 0)))
        self.radius = kw.get("radius", 1)
        self.move = kw.get("move", False)
        super(Circle, self).__init__(*args, **kw)

    def three_points(self):
        pts = []
        pts.extend([self.center.x, self.center.y - self.radius])
        pts.extend([self.center.x, self.center.y + self.radius])
        pts.extend([self.center.x + self.radius, self.center.y])
        return pts
        
    def encode(self, msg=''):
        points = self.three_points()
        msg = [str(x) for x in points]
        msg = str.join(',', msg)
        msg =  super(Circle, self).encode(msg)
        if self.move:
            move = Move(self.center.x + self.radius, self.center.y)
            msg = move.encode() + msg
        return msg

