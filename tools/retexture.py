#!/usr/bin/env python3
"""Gives every polygon of an egg model texture coordinates by box
projection, so the texture has the same scale everywhere: each polygon is
mapped through the axis plane its face normal points to most, one texture
tile per TILE world units. Vertices shared by polygons that need different
coordinates are split.

The level was mapped this way, at 100 world units per tile:
    nix develop -c python3 tools/retexture.py data/lvl/world.egg data/lvl/world.egg 100

Usage: retexture.py IN.egg OUT.egg TILE"""
import sys
from panda3d.egg import EggData, EggPolygon, EggGroupNode, EggVertex
from panda3d.core import Filename, Vec3, LTexCoordd, CS_yup_left

src, dst, tile = sys.argv[1], sys.argv[2], float(sys.argv[3])
egg = EggData(); egg.read(Filename.fromOsSpecific(src))
assert egg.getCoordinateSystem() == CS_yup_left, egg.getCoordinateSystem()
UP = 1   # Y is up in this file

polys = []
def walk(node):
    for child in node.getChildren():
        if isinstance(child, EggPolygon): polys.append(child)
        elif isinstance(child, EggGroupNode): walk(child)
walk(egg)

def face_normal(ps):
    # Newell's method: robust for the model's large, concave polygons.
    n = Vec3(0, 0, 0)
    for i, a in enumerate(ps):
        b = ps[(i + 1) % len(ps)]
        n += Vec3((a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1]))
    return n

def project(p, axis):
    # The two other axes, ordered so that on walls v runs up.
    u, v = {0: (2, 1), 1: (0, 2), 2: (0, 1)}[axis]
    return LTexCoordd(p[u] / tile, p[v] / tile)

assigned = {}   # vertex -> the coordinates this pass gave it
split = 0
for poly in polys:
    verts = [poly.getVertex(i) for i in range(poly.getNumVertices())]
    n = face_normal([v.getPos3() for v in verts])
    axis = max(range(3), key=lambda k: abs(n[k]))
    for i, v in enumerate(verts):
        uv = project(v.getPos3(), axis)
        if v not in assigned:
            v.setUv(uv); assigned[v] = uv
        elif not assigned[v].almostEqual(uv):
            copy = EggVertex(v); copy.setUv(uv)
            copy = v.getPool().createUniqueVertex(copy)
            assigned[copy] = uv
            poly.setVertex(i, copy); split += 1
print(f'{len(polys)} polygons, {split} vertex references split')
egg.writeEgg(Filename.fromOsSpecific(dst))
