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
from phys import geom

level_physics_category = 0x0002

class Level (StaticPhysicalEntity, ModelEntity):

    def __init__ (self, model = 'mesh/cloud.x', *a, **k):
        super (Level, self).__init__ (model = model,
                                      geometry = geom.mesh (model),
                                      category = level_physics_category,
                                      *a, **k)
        self.model.setTexture (loader.loadTexture ('data/sky/south-epo.png'))
