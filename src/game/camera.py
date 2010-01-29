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


from pandac.PandaModules import (
    Vec3, OdeRayGeom, OdeSphereGeom, OdeCappedCylinderGeom)

from core import task
from base.util import bound
from ent.observer import SpatialEntityListener
from ent.entity import SpatialEntity, Entity

from level import level_physics_category

import math
import weakref

class EntityFollowerBase (SpatialEntityListener, Entity):
    
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
    speed        = 0.01
    ent_position = Vec3 (0, 0, 0)
    ent_angle    = 0
    offset       = Vec3 (0, 0, 10)
    contact_dist = 5
    contact_off  = Vec3 (0, 0, -5)
    control_angle = False

    _spin_task   = None
    
    def loop_angle (self, *a, **k):
        if self._spin_task:
            self._spin_task.kill ()

        self._spin_task = self.entities.tasks.add (
            task.linear (self.set_angle, self.angle, self.angle + 2. * math.pi,
                         loop = True, *a, **k))

    def restore_angle (self, *a, **k):
        if self._spin_task:
            self._spin_task.kill ()
        self._spin_task = self.entities.tasks.add (
            task.sinusoid (self.set_angle, self.angle, 0.))
    
    def set_angle (self, val):
        self.angle = val

    def set_hangle (self, val):
        self.hangle = val
    
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
        if self.control_angle:
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
        direction = Vec3 (math.sin (angle), math.cos (angle),
                          - math.sin  (self.hangle))
        position  = self.ent_position + self.offset
        distance = self.distance
        camera_pos = position + direction * (- distance)

        physics = self.entities.physics

        ray = OdeRayGeom (self.distance)
        ray.set (position + self.contact_off, - direction)
        ray.setCollideBits (level_physics_category)
        ray.setCategoryBits (0)
        result = physics.collide_world (ray)
        
        if result and result.getNumContacts () > 0:
            contact  = result.getContactGeom (0)
            new_distance = max (
                0, (position - contact.getPos ()).length () -
                self.contact_dist)
            if new_distance < distance:
                camera_pos = position + direction * (- new_distance)

        # sphere = OdeSphereGeom (self.contact_dist)
        # sphere.setPosition (camera_pos)
        # sphere.setCategoryBits (0)
        # sphere.setCollideBits (level_physics_category)
        # result = physics.collide_world (sphere)

        # if result:
        #     # cyl = OdeCappedCylinderGeom (self.contact_dist, self.distance)
        #     # cyl.setHpr ()
        #     # Find where to replace the camera
        #     ray = OdeRayGeom (self.distance)
        #     ray.set (camera_pos, direction)
        #     ray.setCollideBits (level_physics_category) # hackish
        #     ray.setCategoryBits (0)
        #     result = physics.collide_world (ray)
        #     print "CABRON!"
        #     if result and result.getNumContacts () > 0:
        #         contact  = result.getContactGeom (0)
        #         new_distance = max (
        #             0, (position - contact.getPos ()).length () -
        #             self.contact_dist)
        #         if new_distance < distance:
        #             camera_pos = position + direction * (- new_distance) #+ \
        #                          #self.contact_off

            
        self.camera.setPos (camera_pos)
        self.camera.lookAt (*position)


class SlowEntityFollower (EntityFollowerBase):

    distance = 50
    height   = 50
    offset   = Vec3 (0, 0, 20)
    
    def handle_connect (self, entity):
        super (SlowEntityFollower, self).handle_connect (entity)

        if isinstance (entity, SpatialEntity):
            targetpos = entity.position
            targethpr = entity.hpr
            
            angle = (- targethpr.getX () / 180. + 1) * math.pi
            
            direction = Vec3 (math.sin (angle), math.cos (angle), 0)
            position  = targetpos + Vec3 (0, 0, self.height)
            
            self.camera.setPos (position + direction * (- self.distance))
            self.camera.lookAt (*targetpos)
    
    def on_entity_set_position (self, ent, pos):        
        camvec = ent.position + Vec3 (0, 0, self.height) - self.camera.getPos()
        camdist = camvec.length ()
        camvec.normalize ()

        maxdist = 200.0
        mindist = 50
        if (camdist > maxdist):
            self.camera.setPos (self.camera.getPos() +
                                camvec * (camdist - maxdist))
            camdist = maxdist
        if (camdist < mindist):
            self.camera.setPos (self.camera.getPos() -
                                camvec * (mindist - camdist))
            camdist = mindist

        self.camera.lookAt (* (pos + self.offset))
        

