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

from entity import EntityManager, Entity, DelegateEntity
from pandac.PandaModules import *
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from direct.showbase.Audio3DManager import Audio3DManager

class PandaEntityManager (EntityManager):

    def __init__ (self, render = None, audio3d = None, *a, **k):
        super (PandaEntityManager, self).__init__ (*a, **k)
        if render:
            self.render = render
        else:
            self.render = base.render
        if audio3d:
            self.audio3d = audio3d
        else:
            self.audio3d = Audio3DManager (base.sfxManagerList [0], camera)
            self.audio3d.setListenerVelocityAuto ()


class PandaEntity (Entity):

    def __init__ (self,
                  entities  = None,
                  node_name = 'entity',
                  *a, **k):
        super (PandaEntity, self).__init__ (
            entities = entities,
            *a, **k)
        
        self._node = NodePath (PandaNode (node_name))
        self._node.reparentTo (render)
        self._panda_sounds = []
        
    @property
    def node (self):
        return self._node
        
    def set_position (self, pos):
        super (PandaEntity, self).set_position (pos)
        self._node.setPos (pos)
        
    def set_hpr (self, hpr):
        super (PandaEntity, self).set_hpr (hpr)
        self._node.setHpr (hpr)
                
    def set_scale (self, scale):
        super (PandaEntity, self).set_scale (scale)
        self._node.setScale (scale)

    def dispose (self):
        audio3d = self.entities.audio3d
        map (audio3d.detachSound, self._panda_sounds)
        self._node.removeNode ()
        super (PandaEntity, self).dispose ()
        
    def load_sound (self, name):
        audio3d = self.entities.audio3d
        snd = audio3d.loadSfx (name)
        audio3d.attachSoundToObject (snd, self._node)
        audio3d.setSoundVelocityAuto (snd)
        self._panda_sounds.append (snd) 
        return snd


class DelegatePandaEntity (DelegateEntity):

    @property
    def node (self):
        return self.delegate.node


class ModelEntityBase (PandaEntity):

    @property
    def model (self):
        return self._model
    
    def set_model_position (self, pos):
        self._model.setPos (pos)

    def get_model_position (self):
        return self._model.getPos ()
        
    def set_model_hpr (self, hpr):
        self._model.setHpr (hpr)

    def get_model_hpr (self):
        return self._model.getHpr ()
        
    def set_model_scale (self, scale):
        self._model.setScale (scale)

    def get_model_scale (self):
        return self._model.getScale ()

    model_position = property (get_model_position, set_model_position)
    model_hpr      = property (get_model_hpr,      set_model_hpr)
    model_scale    = property (get_model_scale,    set_model_scale)


class ModelEntity (ModelEntityBase):

    def __init__ (self,
                  model = None,
                  *a, **k):
        super (ModelEntity, self).__init__ (*a, **k)

        self._model = loader.loadModel (model)
        self._model.reparentTo (self._node)


class ActorEntity (ModelEntityBase):

    def __init__ (self,
                  model = None,
                  anims = {},
                  *a, **k):
        super (ActorEntity, self).__init__ (*a, **k)

        self._model = Actor (loader.loadModel (model), anims)
        self._model.loadAnims (anims)
        self._model.reparentTo (self._node)


class DelegateModelEntity (DelegatePandaEntity):

    @property
    def model (self):
        return self.delegate.model
    
    def set_model_position (self, pos):
        self.delegate.set_model_position (pos)

    def get_model_position (self):
        return self.delegate.get_model_position ()
        
    def set_model_hpr (self, hpr):
        self.delegate.set_model_hpr (hpr)

    def get_model_hpr (self):
        return self.delegate.get_model_hpr ()
        
    def set_model_scale (self, scale):
        self.delegate.set_model_scale (scale)

    def get_model_scale (self):
        return self.delegate.get_model_scale ()

    model_position = property (get_model_position, set_model_position)
    model_hpr      = property (get_model_hpr,      set_model_hpr)
    model_scale    = property (get_model_scale,    set_model_scale)
