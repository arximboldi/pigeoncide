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
from ent.model import ModelEntity
from ent.physical import DynamicPhysicalEntity

import phys.geom as geom

class Boy (ObservableEntity,
           ModelEntity,
           DynamicPhysicalEntity):

    MODEL = '../data/mesh/ralph.egg.pz'
    
    def __init__ (self, model = MODEL, *a, **k):
        super (Boy, self).__init__ (geometry = geom.capsule (1.0, 7.0),
                                    model    = model,
                                    *a, **k)
        self.offset_position = (.0, .0, 3.5)
        
