import silhouette
import svgwrite

def translate(vectors, offset):
    ret = []
    for vector in vectors:
        vector = map(sum, zip(vector, offset))
        ret.append(vector)
    return ret

def to_dpi(vector):
    return [val.to("dpi").magnitude for val in vector]

class RegistrationMarks(object):
    Defaults = {
        "top_margin": "12mm",
        "bottom_margin": "12mm",
        "left_margin": "12mm",
        "right_margin": "12mm",
        "width": "8.5inch",
        "height": "11inch",
        "thickness": "1.0mm",
        "length": "20mm",
        "square": "5mm",
    }

    def __init__(self, **kw):
        _kw = self.Defaults.copy()
        _kw.update(kw)
        _kw = {key: silhouette.unit(val) for (key, val) in _kw.items()}
        self.__dict__.update(_kw)

    def cube_mark(self):
        # top left
        insert = (self.top_margin - self.thickness / 2.0, self.right_margin - self.thickness / 2.0)
        insert = to_dpi(insert)
        size = to_dpi((self.square + self.thickness, self.square + self.thickness))
        rect = svgwrite.shapes.Rect(insert=insert, size=size)
        return rect
    
    def top_angle_mark(self):
        length = self.length + self.thickness / 2.0
        width = self.thickness
        points = [
            [0, 0],
            [length, 0],
            [length, length],
            [length - width, length],
            [length - width, width],
            [0, width],
        ]
        origin_x = self.width - self.right_margin - self.length
        origin_y = self.top_margin - width / 2.0
        points = translate(points, (origin_x, origin_y))
        points = map(to_dpi, points)
        polygon = svgwrite.shapes.Polygon(points=points)
        return polygon

    def bottom_angle_mark(self):
        length = self.length + self.thickness / 2.0
        width = self.thickness
        points = [
            [0, 0],
            [width, 0],
            [width, length - width],
            [length, length - width],
            [length, length],
            [0, length],
        ]
        origin_x = self.left_margin - width / 2.0
        origin_y = self.height - self.bottom_margin - self.length
        points = translate(points, (origin_x, origin_y))
        points = map(to_dpi, points)
        polygon = svgwrite.shapes.Polygon(points=points)
        return polygon

    def generate(self, svgfn="registration.svg"):
        svg = svgwrite.Drawing(svgfn)
        svg.add(self.cube_mark())
        svg.add(self.top_angle_mark())
        svg.add(self.bottom_angle_mark())
        svg.save()

marks = RegistrationMarks()
marks.generate()
