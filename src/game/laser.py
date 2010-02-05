#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pigeoncide.
#
#  Pigeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pigeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from base.util import printfn, near0
from core.util import normalize

from ent.task import TaskEntity
from ent.physical import StaticPhysicalEntity
from ent.panda import PandaEntity, ModelEntity
from ent.entity import Entity

from functools import partial
from operator import lt
from core import task
from phys import geom

import weakref

from pandac.PandaModules import *

class Group (Entity):

    field_dist = 100
    field_dist_sq = field_dist * field_dist
    
    def __init__ (self, *a, **k):
        super (Group, self).__init__ (*a, **k)
        self.parts  = []
        self.sticks = []
        
    def add_stick (self, stick):
        best = self.best_stick (stick.position)
        if best:
            self.parts.append (
                Field (fst      = stick,
                       snd      = best,
                       entities = self.entities))
        self.sticks.append (stick)

    def best_stick (self, pos):
        bestdist = self.field_dist_sq
        best = None

        for curr in self.sticks:
            dist = (pos - curr.position).lengthSquared ()
            if dist < bestdist:
                bestdist = dist
                best = curr
        return best


class Field (PandaEntity, StaticPhysicalEntity):
    
    def __init__ (self, fst = None, snd = None, *a, **k):

        model = make_laser_model (fst, snd, 50)
        super (Field, self).__init__ (
            geometry = geom.node (model),
            *a, **k)
        
        model.reparentTo (self.node)
        self.position = fst.position - Vec3 (0, 0, 6)
        self.physical_position = Vec3 (0, 0, -15)

        model.setScale (near0, near0, near0)
        fst.init_task ().add_next (
            task.fade (lambda x: model.setScale (
                Vec3 (x, x, 1.))))
        
        self.enable_collision ()

        sound = self.load_sound ('snd/electrocute-long.wav')
        sound.setLoop (True)
        sound.play ()
        sound.setVolume (0.1)

        
class Stick (ModelEntity, StaticPhysicalEntity):

    MODEL = 'obj/stick.egg'
    HL_MODEL = 'obj/stick-hl.egg'

    _is_highlight = False
    
    def __init__ (self, *a, **k):
        super (Stick, self).__init__ (
            model = self.MODEL,
            geometry = geom.box (5, 5, 50),
            *a, **k)

        self.model_position = Vec3 (0, 0, -5)
        self.model.setTwoSided (True) # HACK

        self.hl_model = loader.loadModel (self.HL_MODEL)
        self.hl_model.setScale (1.3, 1.3, 1)
        
        self.scale = Vec3 (near0, near0, near0)
        tsk = task.sinusoid (lambda x: self.set_scale (Vec3 (x, x, x)), 0., 1.3)
        
        self.entities.tasks.add (tsk)
        self.init_task = weakref.ref (tsk)

    def highlight (self):
        if not self._is_highlight:
            self.hl_model.reparentTo (self.model)
            self._is_highlight = True
            
    def unhighlight (self):
        if self._is_highlight:
            self.hl_model.detachNode ()
            self._is_highlight = False


def make_laser_model (fst, snd, height):
    # Panda3d sucks when it comes to procedural model generation
    
    format   = GeomVertexFormat.getV3n3cpt2 ()
    vdata    = GeomVertexData ('square', format, Geom.UHDynamic)
    vertex   = GeomVertexWriter (vdata, 'vertex')
    normal   = GeomVertexWriter (vdata, 'normal')
    color    = GeomVertexWriter (vdata, 'color')
    texcoord = GeomVertexWriter (vdata, 'texcoord')
    
    v0 = Vec3 (0, 0, 0)
    v1 = snd.position - fst.position
    v2 = v1 + Vec3 (0, 0, height)
    v3 = v0 + Vec3 (0, 0, height)
    
    vertex.addData3f (v0)
    vertex.addData3f (v1)
    vertex.addData3f (v2)
    vertex.addData3f (v3)
    vertex.addData3f (v3)
    vertex.addData3f (v2)
    vertex.addData3f (v1)
    vertex.addData3f (v0)
    
    n = normalize ((v0 - v1).cross (v1 - v2))
    for x in xrange (4):
        normal.addData3f (n)
    n = -n
    for x in xrange (4):
        normal.addData3f (n)
        
    c = Vec4 (1., 0., 0., .5)
    for x in xrange (8):
        color.addData4f (c)
    
    texcoord.addData2f (1, 0)
    texcoord.addData2f (0, 0)
    texcoord.addData2f (0, 1)
    texcoord.addData2f (1, 1)
    texcoord.addData2f (1, 1)
    texcoord.addData2f (0, 1)
    texcoord.addData2f (0, 0)
    texcoord.addData2f (1, 0)
    
    tri1 = GeomTriangles (Geom.UHDynamic)
    tri2 = GeomTriangles (Geom.UHDynamic)
    tri3 = GeomTriangles (Geom.UHDynamic)
    tri4 = GeomTriangles (Geom.UHDynamic)
    
    tri1.addVertex (0)
    tri1.addVertex (1)
    tri1.addVertex (3)
    tri2.addConsecutiveVertices (1, 3)
    tri3.addVertex (4+0)
    tri3.addVertex (4+1)
    tri3.addVertex (4+3)
    tri4.addConsecutiveVertices (4+1, 3)
    
    tri1.closePrimitive ()
    tri2.closePrimitive ()
    tri3.closePrimitive ()
    tri4.closePrimitive ()
    
    square = Geom (vdata)
    square.addPrimitive (tri1)
    square.addPrimitive (tri2)
    square.addPrimitive (tri3)
    square.addPrimitive (tri4)
    
    node = GeomNode ('laser')
    node.addGeom (square)
    
    laser = NodePath (node)
    laser.setTwoSided (False)
    laser.setPos (0, 0, -13)
    
    tex = loader.loadTexture ('obj/laser.png')
    ts = TextureStage ('ts')
    laser.setTexture (ts, tex)
    laser.setTransparency (TransparencyAttrib.MDual) 
    
    # tex = loader.loadTexture ('./data/tex/laser2-glow.png')
    # ts = TextureStage ('ts')
    # ts.setMode (TextureStage.MGlow)
    # laser.setTexture (ts, tex)

    return laser
