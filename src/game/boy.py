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

from ent.observer import ObservableSpatialEntity
from ent.panda import ActorEntity
from ent.physical import StandingPhysicalEntity
from pandac.PandaModules import Vec3

from phys import geom
from phys import mass

from kill import KillableEntity

class Boy (ObservableSpatialEntity,
           ActorEntity,
           StandingPhysicalEntity,
           KillableEntity):

    MODEL = 'mesh/boy.egg'
    ANIMS = { 'run'  : 'mesh/boy-run.egg',
              'walk' : 'mesh/boy-walk.egg',
              'idle' : 'mesh/boy-idle.egg',
              'feed' : 'mesh/boy-feed.egg',
              'hit'  : 'mesh/boy-feed.egg' }
        
    def __init__ (self, model = MODEL, *a, **k):
        super (Boy, self).__init__ (geometry = geom.capsule (1.0, 7.0),
                                    mass     = mass.capsule (2, 3, 1.0, 7.0),
                                    model    = model,
                                    anims    = self.ANIMS,
                                    *a, **k)

        self.model_position = Vec3 (.0, .0, -4.0)
        self.model_scale = Vec3 (.1, .1, .1)
        self.enable_collision ()
        
        hand_joint = self.model.exposeJoint (
            None, 'modelRoot', 'Bip01_R_Finger0')
        weapon = loader.loadModel ('mesh/baseball_bat.x')
        weapon.reparentTo (hand_joint)
        weapon.setScale (100., 100., 100.)
        weapon.setHpr (120, 0, 0)
