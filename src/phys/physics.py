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

    def __init__ (self, *a, **k):
        super (Physics, self).__init__ (*a, **k)

        self._world = OdeWorld ()
        self._world.setGravity (0, 0, -9.81)
        self._world.initSurfaceTable (1)
        self._world.setSurfaceEntry (
            0,
            0,
            1.0,          # u
            .35,          # elasticity
            .01,          # minimum threshold for physical movement
            .01,          #
            .00000001,    # softening
            .01,          #
            .01)          # dampening
        
        self._space = OdeHashSpace ()
        self._space.setAutoCollideWorld (self._world)
        
        self._group = OdeJointGroup ()
        self._space.setAutoCollideJointGroup (self._group)
    

    @property
    def world (self):
        return self._world

    @property
    def space (self):
        return self._space
    
    def update (self, timer):
        self._space.autoCollide ()
        self._world.quickStep (timer.delta)

