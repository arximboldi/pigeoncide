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

from pandac.PandaModules import Vec3
from base.util import bound
from observer import EntityListener
import math


class EntityFollowerBase (EntityListener):
    
    def __init__ (self, camera = None, *a, **k):
        super (EntityFollowerBase, self).__init__ (*a, **k)
        self.camera = camera
        

class FastEntityFollower (EntityFollowerBase):

    hangle   = math.pi / 12
    distance = 40
    
    def on_entity_set_position (self, ent, pos):
        angle = ent.angle
        direction = Vec3 (math.sin (angle),
                          math.cos (angle),
                          - math.sin  (self.hangle))
        position  = Vec3 (* ent.position)

        self.camera.setPos (position + direction * (- self.distance))


class SlowEntityFollower (EntityFollowerBase):
    
    def on_entity_set_position (self, ent, pos):        
        camvec = ent.position - self.camera.getPos()
        camvec.setZ (0)
        camdist = camvec.length ()
        camvec.normalize ()

        maxdist = 100.0
        mindist = 5.0
        if (camdist > maxdist):
            self.camera.setPos (self.camera.getPos() +
                                camvec * (camdist - maxdist))
            camdist = maxdist
        if (camdist < mindist):
            self.camera.setPos (self.camera.getPos() -
                                camvec * (mindist - camdist))
            camdist = mindist

        self.camera.lookAt (*pos)
        

