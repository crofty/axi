from __future__ import division

from shapely import geometry

import axi
import layers
import parser
import projections
import sys
import util

CARY = 35.787196, -78.783337
BUDAPEST = 47.498206, 19.052509

LAT, LNG = BUDAPEST

ROTATION_DEGREES = 0
MAP_WIDTH_KM = 4
PAGE_WIDTH_IN = 12
PAGE_HEIGHT_IN = 8.5
ASPECT_RATIO = PAGE_WIDTH_IN / PAGE_HEIGHT_IN

def crop_geom(g, w, h):
    result = util.centered_crop(g, w, h)
    if result.is_empty:
        return None
    result.tags = g.tags
    return result

def main():
    args = sys.argv[1:]
    filename = args[0]
    proj = projections.LambertAzimuthalEqualArea(LNG, LAT, ROTATION_DEGREES)
    geoms = parser.parse(filename, transform=proj.project)
    print len(geoms)
    w = MAP_WIDTH_KM
    h = w / ASPECT_RATIO
    geoms = filter(None, [crop_geom(g, w * 1.1, h * 1.1) for g in geoms])
    # g = geometry.collection.GeometryCollection(geoms)
    g = geometry.collection.GeometryCollection([
        layers.roads(geoms),
        # layers.railroads(geoms),
        # layers.buildings(geoms),
        # layers.water(geoms),
    ])
    g = util.paths_to_shapely(util.shapely_to_paths(g))
    g = util.centered_crop(g, w, h)
    paths = util.shapely_to_paths(g)
    # paths = []
    # x, y = proj.project(HOME[1], HOME[0])
    # paths.append(util.star(x, y, 8 / 1000))
    # paths.append(util.star(x, y, 6 / 1000))
    # paths.append(util.star(x, y, 4 / 1000))
    # paths.append(util.star(x, y, 2 / 1000))
    # paths.append(util.centered_rectangle(w, h))
    d = axi.Drawing(paths)
    d = d.translate(w / 2, h / 2)
    d = d.scale(PAGE_WIDTH_IN / w)
    # d = d.sort_paths().join_paths(0.002).simplify_paths(0.002)
    im = d.render(line_width=0.25/25.4)
    im.write_to_png('out.png')
    # raw_input('Press ENTER to continue!')
    # axi.draw(d)

if __name__ == '__main__':
    main()