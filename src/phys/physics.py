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

class Physics (Task):

    time_step = .1 / 120.

    def __init__ (self, *a, **k):
        super (Physics, self).__init__ (*a, **k)

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
            .00001,       # soft_cfm ...
            .01,          # 
            .01)          # dampening

        #self._world.setContactMaxCorrectingVel (1.0)
        self._world.setAutoDisableFlag (1)
        
        self._space = OdeHashSpace ()
        self._space.setAutoCollideWorld (self._world)
        
        self._group = OdeJointGroup ()
        self._space.setAutoCollideJointGroup (self._group)
    
        self._time_acc = 0

    def set_gravity (self, gravity):
        self._world.setGravity (gravity)

    def get_gravity (self,):
        return self._world.getGravity ()
        
    @property
    def world (self):
        return self._world

    @property
    def space (self):
        return self._space
    
    def update (self, timer):
        self._space.autoCollide ()
        self._world.step (timer.delta)
        self._group.empty ()

    gravity = property (get_gravity, set_gravity) 
