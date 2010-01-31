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

from base.signal import signal

from ent.entity import Entity
from ent.observer import ObservableSpatialEntity
from ent.panda import DelegateActorEntity, ActorEntity
from ent.physical import (DelegateStandingPhysicalEntity, OnFloorEntity,
                          StandingPhysicalEntity, DelegateOnFloorEntity)
from pandac.PandaModules import Vec3

from phys import geom
from phys import mass

from kill import KillableEntity
from weapon import WeaponOwner, DelegateWeaponOwner


class BoyBase (Entity):

    boy_model = 'char/boy-anims.egg'
    boy_anims = { 'run'  : 'char/boy-run.egg',
                  'walk' : 'char/boy-walk.egg',
                  'idle' : 'char/boy-idle.egg',
                  'feed' : 'char/boy-feed.egg',
                  'hit'  : 'char/boy-hit.egg' }

    on_boy_noise = signal ()

    def emit_noise (self, rad):
        self.on_boy_noise (self, rad)
    
    def __init__ (self, model = boy_model, anims = boy_anims, *a, **k):
        super (BoyBase, self).__init__ (
            geometry = geom.capsule (1.0, 7.0),
            mass     = mass.capsule (2, 3, 1.0, 7.0),
            model    = model,
            anims    = anims,
            *a, **k)
        self.model_position = Vec3 (.0, .0, -4.0)
        self.model_scale = Vec3 (.1, .1, .1)
        self.enable_collision ()


class Boy (BoyBase,
           ObservableSpatialEntity,
           ActorEntity,
           StandingPhysicalEntity,
           OnFloorEntity,
           KillableEntity,
           WeaponOwner):
    pass


class DelegateBoy (
    BoyBase,
    DelegateActorEntity,
    DelegateStandingPhysicalEntity,
    DelegateOnFloorEntity,
    DelegateWeaponOwner):
    """
    TODO: Add missing delegates. Btw, read TODO note in entity.py before ;)
    """

    @property
    def on_boy_noise (self):
        return self.delegate.on_boy_noise

    def emit_noise (self, rad):
        self.delegate.emit_noise (rad)
