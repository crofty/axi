from __future__ import division

from math import sin, cos, radians

from .paths import simplify_paths, sort_paths, join_paths

try:
    import cairo
except ImportError:
    cairo = None

class Drawing(object):
    def __init__(self, paths=None):
        self.paths = paths or []
        self._bounds = None

    @property
    def bounds(self):
        if not self._bounds:
            points = [(x, y) for path in self.paths for x, y in path]
            if points:
                x1 = min(x for x, y in points)
                x2 = max(x for x, y in points)
                y1 = min(y for x, y in points)
                y2 = max(y for x, y in points)
            else:
                x1 = x2 = y1 = y2 = 0
            self._bounds = (x1, y1, x2, y2)
        return self._bounds

    @property
    def width(self):
        x1, y1, x2, y2 = self.bounds
        return x2 - x1

    @property
    def height(self):
        x1, y1, x2, y2 = self.bounds
        return y2 - y1

    def simplify_paths(self, tolerance):
        return Drawing(simplify_paths(self.paths, tolerance))

    def sort_paths(self, reversable=True):
        return Drawing(sort_paths(self.paths, reversable))

    def join_paths(self, tolerance):
        return Drawing(join_paths(self.paths, tolerance))

    # def remove_duplicates(self):
    #     return Drawing(util.remove_duplicates(self.paths))

    def transform(self, func):
        return Drawing([[func(x, y) for x, y in path] for path in self.paths])

    def translate(self, dx, dy):
        def func(x, y):
            return (x + dx, y + dy)
        return self.transform(func)

    def scale(self, sx, sy):
        def func(x, y):
            return (x * sx, y * sy)
        return self.transform(func)

    def rotate(self, angle):
        c = cos(radians(angle))
        s = sin(radians(angle))
        def func(x, y):
            return (x * c - y * s, y * c + x * s)
        return self.transform(func)

    def move(self, x, y, ax, ay):
        x1, y1, x2, y2 = self.bounds
        dx = x1 + (x2 - x1) * ax - x
        dy = y1 + (y2 - y1) * ay - y
        return self.translate(-dx, -dy)

    def origin(self):
        return self.move(0, 0, 0, 0)

    def center(self, width, height):
        return self.move(width / 2, height / 2, 0.5, 0.5)

    def rotate_to_fit(self, width, height, step=5):
        for angle in range(0, 180, step):
            drawing = self.rotate(angle)
            if drawing.width <= width and drawing.height <= height:
                return drawing.center(width, height)
        return None

    def scale_to_fit(self, width, height, padding=0):
        width -= padding * 2
        height -= padding * 2
        scale = min(width / self.width, height / self.height)
        return self.scale(scale, scale).center(width, height)

    def rotate_and_scale_to_fit(self, width, height, padding=0, step=5):
        drawings = []
        width -= padding * 2
        height -= padding * 2
        for angle in range(0, 180, step):
            drawing = self.rotate(angle)
            scale = min(width / drawing.width, height / drawing.height)
            drawings.append((scale, drawing))
        scale, drawing = max(drawings)
        return drawing.scale(scale, scale).center(width, height)

    def remove_paths_outside(self, width, height):
        paths = []
        for path in self.paths:
            ok = True
            for x, y in path:
                if x < 0 or y < 0 or x > width or y > height:
                    ok = False
                    break
            if ok:
                paths.append(path)
        return Drawing(paths)

    def render(self, scale=96, margin=30, line_width=0.5/25.4):
        if cairo is None:
            raise Exception('Drawing.render() requires cairo')
        # x1, y1, x2, y2 = self.bounds
        x1, y1, x2, y2 = (0, 0, 11, 8.5)
        w = x2 - x1
        h = y2 - y1
        width = int(scale * w + margin * 2)
        height = int(scale * h + margin * 2)
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        dc = cairo.Context(surface)
        dc.set_line_cap(cairo.LINE_CAP_ROUND)
        dc.set_line_join(cairo.LINE_JOIN_ROUND)
        dc.translate(margin, margin)
        dc.scale(scale, scale)
        dc.translate(-x1, -y1)
        dc.set_source_rgb(1, 1, 1)
        dc.paint()
        dc.set_source_rgb(0.5, 0.5, 0.5)
        dc.set_line_width(1 / scale)
        dc.rectangle(x1, y1, w, h)
        dc.stroke()
        dc.set_source_rgb(0, 0, 0)
        dc.set_line_width(line_width)
        for path in self.paths:
            dc.move_to(*path[0])
            for x, y in path:
                dc.line_to(x, y)
        dc.stroke()
        return surface