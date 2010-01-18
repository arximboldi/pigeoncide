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
from ent.observer import EntityListener
import math
import weakref

class EntityFollowerBase (EntityListener):
    
    def __init__ (self, camera = None, *a, **k):
        super (EntityFollowerBase, self).__init__ (*a, **k)
        self.camera = camera


class FastEntityFollower (EntityFollowerBase):

    angle        = 0.
    hangle       = math.pi / 12
    distance     = 50.
    min_distance = 10.
    max_distance = 1000.
    delta_dist   = 5
    speed        = 2.
    ent_position = Vec3 (0, 0, 0)
    ent_angle    = 0
    
    def on_zoom_in (self):
        self.distance += self.delta_dist
        if self.distance > self.max_distance:
            self.distance = self.max_distance
        self.update_camera ()
        
    def on_zoom_out (self):
        self.distance -= self.delta_dist
        if self.distance < self.min_distance:
            self.distance = self.min_distance
        self.update_camera ()
        
    def on_angle_change (self, (px, py)):
        self.angle  += px * self.speed
        self.hangle += py * self.speed
        self.update_camera ()

    def on_entity_set_hpr (self, ent, (h, p, r)):
        self.ent_angle = (- h / 180. + 1) * math.pi
    
    def on_entity_set_position (self, ent, pos):
        self.ent_position = ent.position
        self.update_camera ()
            
    def update_camera (self):
        angle = self.ent_angle + self.angle
        direction = Vec3 (math.sin (angle),
                          math.cos (angle),
                          - math.sin  (self.hangle))
        position  = Vec3 (self.ent_position)

        self.camera.setPos (position + direction * (- self.distance))
        self.camera.lookAt (*position)


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
        

