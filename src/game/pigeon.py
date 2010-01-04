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

from ent.observer import ObservableEntity
from ent.panda import ModelEntity
from flock import Boid

from pandac.PandaModules import Vec3

import phys.geom as geom
import phys.mass as mass

class Pigeon (Boid, ModelEntity, ObservableEntity):

    MODEL = '../data/mesh/pigeon-old.x'
    #ANIMS = { 'run'  : '../data/mesh/ralph-run.egg.pz',
    #          'walk' : '../data/mesh/ralph-walk.egg.pz' }
    ANIMS = {}
    
    def __init__ (self,
                  model = MODEL,
                  *a, **k):
        super (Pigeon, self).__init__ (
            geometry = geom.sphere (2),
            mass     = mass.sphere (1, 2),
            model    = model,
            anims    = self.ANIMS,
            *a, **k)

        self.model_position = Vec3 (0, 0, -2)
        self.model_scale = Vec3 (0.05, 0.05, 0.05)
        self.model_hpr = Vec3 (180, 0, 0)
