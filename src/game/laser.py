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

from ent.physical import StaticPhysicalEntity
from ent.panda import ModelEntity
from ent.entity import Entity

from functools import partial
from operator import lt
from core import task
from phys import geom

from pandac.PandaModules import Vec3

class Group (Entity):

    field_dist = 100
    field_dist_sq = field_dist * field_dist
    
    def __init__ (self, *a, **k):
        super (Group, self).__init__ (*a, **k)
        self.parts  = []
        self.sticks = []
        
    def add_stick (self, stick):
        pos = stick.position
        bestdist = self.field_dist_sq
        best = None
        for curr in self.sticks:
            dist = (pos - curr.position).lengthSquared ()
            if dist < self.field_dist_sq:
                bestdist = dist
                best = curr
        self.sticks.append (stick)
        if best:
            self.parts.append (Field (best,
                                      stick,
                                      entities = self.entities))


class Field (ModelEntity, StaticPhysicalEntity):

    MODEL = '../data/mesh/box.egg.pz'
    
    def __init__ (self, fst = None, snd = None, *a, **k):
        super (Field, self).__init__ (model = self.MODEL,
                                      *a, **k)

        center = (fst.position + snd.position) / 2
        center.setZ (center.getZ () + 10)
        distance = fst.position - snd.position
        self.position = center
        self.scale = Vec3 (10, 10, 10)

class Stick (ModelEntity, StaticPhysicalEntity):

    MODEL = '../data/mesh/stick_arch_sub.x'

    def __init__ (self, *a, **k):
        super (Stick, self).__init__ (
            model = self.MODEL,
            geometry = geom.box (1, 1, 1),
            *a, **k)

        self.model_position = Vec3 (0, 0, -0.18)
        self.entities.tasks.add (
             task.linear (lambda x: self.set_scale (Vec3 (x, x, x)), 0, 30))

