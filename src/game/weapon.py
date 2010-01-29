#
#  Copyright (C) 2010 Juan Pedro Bolivar Puente, Alberto Villegas Erce
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

from ent.physical import StaticPhysicalEntity, DynamicPhysicalEntity
from ent.panda import RelativeModelEntity, ModelEntity
from base.signal import weak_slot

class OwnedWeaponEntity (
    StaticPhysicalEntity,
    RelativeModelEntity):
    pass

class FreeWeaponEntity (
    DynamicPhysicalEntity,
    ModelEntity):
    pass

class WeaponEntity (Entity):

    _owner    = None
    
    def __init__ (self, geom = None, hit_geom = None, *a, **k):
        super (WeaponEntity, self).__init__ (*a, **k)
        self._geom     = geom
        self._hit_geom = hit_geom

    @weak_slot
    def on_hit (self, ev, a, b):
        pass

    def enable_hitting (self):
        if self._owner:
            self.on_collide += self.on_hit

    def disable_hitting (self):
        if self._owner:
            self.on_collide -= self.on_hit

    def set_owner (self, owner):
        self._owner = owner
    
    def get_owner (self):
        return self._owner

    owner = property (get_owner, set_owner)

class BaseballBat (WeaponEntityBase):
    pass
