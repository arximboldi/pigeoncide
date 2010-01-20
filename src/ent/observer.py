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

from base.observer import make_observer
from entity import SpatialEntity


SpatialEntitySubject, SpatialEntityListener = make_observer (
    [ 'on_entity_set_position',
      'on_entity_set_hpr',
      'on_entity_set_scale' ],
    'Entity', __name__)


class ObservableSpatialEntity (SpatialEntity, SpatialEntitySubject):

    def set_position (self, pos):
        super (ObservableSpatialEntity, self).set_position (pos)
        self.on_entity_set_position (self, pos)

    def set_hpr (self, hpr):
        super (ObservableSpatialEntity, self).set_hpr (hpr)
        self.on_entity_set_hpr (self, hpr)

    def set_scale (self, scale):
        super (ObservableSpatialEntity, self).set_scale (scale)
        self.on_entity_set_scale (self, hpr)

