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

from pandac.PandaModules import *
from core.task import Task
from base.util import nop, remove_if

def get_ode_id (ode_object):
    return int (get_ode_id_str (ode_object), 16)

def get_ode_id_str (ode_object):
    return str (ode_object).split (" ") [-1].rstrip (")")

class Physics (Task):

    time_step = .1 / 60.

    def __init__ (self, events = None, *a, **k):
        super (Physics, self).__init__ (*a, **k)

        self._geoms = []

        self._world = OdeWorld ()
        self._world.setGravity (0, 0, -100)
        self._world.initSurfaceTable (1)
        self._world.setSurfaceEntry (
            0,            # pos1
            0,            # pos2
            1.0,          # mu
            .35,          # bounce
            .01,          # bounce_vel (minimum vel for bounce)
            .2,           # soft_erp contact normal softness
            .0000001,     # soft_cfm ...
            .01,          # 
            .01)          # dampening

        self._world.setContactMaxCorrectingVel (100.0)
        self._world.setAutoDisableFlag (False)
        
        self._space = OdeHashSpace ()
        self._space.setAutoCollideWorld (self._world)
        
        self._group = OdeJointGroup ()
        self._space.setAutoCollideJointGroup (self._group)
    
        self._time_acc = 0
        
        if events:
            self._space.setCollisionEvent ('ode-collision')
            events.event ('panda-ode-collision').connect (self.on_collision)
            self._geom_cbs = {}
            
    def on_collision (self, ev):
        geom1 = str (ev.getGeom1 ())
        geom2 = str (ev.getGeom2 ())
        
        cb1, data1 = self._geom_cbs.get (geom1, (nop, None))
        cb2, data2 = self._geom_cbs.get (geom2, (nop, None))

        cb1 (data1, data2)
        cb2 (data2, data1)

    def register_geom_callback (self, geom, cb, data):
        geom_id = 'OdeGeom(id = ' + get_ode_id_str (geom) + ')'
        self._geom_cbs [geom_id] = (cb, data)

    def unregister_geom_callback (self, geom):
        geom_id = 'OdeGeom(id = ' + get_ode_id_str (geom) + ')'
        del self._geom_cbs [geom_id]
    
    def set_gravity (self, gravity):
        self._world.setGravity (gravity)

    def get_gravity (self,):
        return self._world.getGravity ()
        
    @property
    def world (self):
        return self._world

    def register (self, geom):
        self._geoms.append (geom)

    def unregister (self, geom):
        #self._geoms = remove_if (lambda (g, _): g == geom, self._geoms)
        self._geoms.remove (geom)

    def collide_world (self, geom):
        scene = OdeUtil.spaceToGeom (self._space)
        return OdeUtil.collide (self, scene, geom)

    def collide_geoms (self, geom):
        pass
        
    @property
    def space (self):
        return self._space
    
    def update (self, timer):
        self._space.autoCollide ()
        self._world.quickStep (timer.delta)
        self._group.empty ()
        
        # self._time_acc += timer.delta
        # while self._time_acc > 0:
        #      self._space.autoCollide ()
        #      self._world.quickStep (self.time_step)
        #      self._time_acc -= self.time_step
        #      self._group.empty ()
        
    gravity = property (get_gravity, set_gravity) 

