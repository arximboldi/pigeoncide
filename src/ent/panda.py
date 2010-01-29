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

from entity import *
from task import TaskEntity

from pandac.PandaModules import *
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from direct.showbase.Audio3DManager import Audio3DManager


class PandaEntityManager (EntityManager):

    _owns_render   = False
    _owns_render2d = False
    _owns_audio3d  = False
    
    def __init__ (self,
                  render   = None,
                  render2d = None,
                  audio3d  = None,
                  *a, **k):
        super (PandaEntityManager, self).__init__ (*a, **k)

        if render:
            self.render = render
        else:
            node = NodePath (PandaNode ('entities'))
            node.reparentTo (base.render)
            self.render = node
            self._owns_render = True

        if render2d:
            self.render = render2d
        else:
            node = NodePath (PandaNode ('entities'))
            node.reparentTo (base.render2d)
            self.render2d = node
            self._owns_render2d = True
        
        if audio3d:
            self.audio3d = audio3d
        else:
            self.audio3d = Audio3DManager (base.sfxManagerList [0], camera)
            self.audio3d.setListenerVelocityAuto ()
            self._owns_audio3d = True
    
    def dispose (self):
        super (PandaEntityManager, self).dispose ()
        
        if self._owns_render:
            self.render.removeNode ()
        if self._owns_render2d:
            self.render2d.removeNode ()


class PandaEntityBase (SpatialEntity):
    """
    TODO: Here 'Base' in the name doesn't have the same meaning as in
    the rest of the entities, where it reflects the common behaviour
    to both Decorator or actual instance versions... Here it is just
    to be able to parametrize wether it is a 2D or 3D entity.
    """
    
    def __init__ (self,
                  entities  = None,
                  node_name = 'entity',
                  *a, **k):
        super (PandaEntityBase, self).__init__ (
            entities = entities,
            *a, **k)
        
        self._node = NodePath (PandaNode (node_name))
        self._node.reparentTo (self.get_parent_node ())
        self._panda_sounds = []
        
    @property
    def node (self):
        return self._node
        
    def dispose (self):
        audio3d = self.entities.audio3d
        map (audio3d.detachSound, self._panda_sounds)
        self._node.removeNode ()
        super (PandaEntityBase, self).dispose ()
        
    def load_sound (self, name):
        audio3d = self.entities.audio3d
        snd = audio3d.loadSfx (name)
        audio3d.attachSoundToObject (snd, self._node)
        audio3d.setSoundVelocityAuto (snd)
        self._panda_sounds.append (snd) 
        return snd


class RelativePandaEntityBase (TaskEntity):

    def __init__ (self, parent_node = None, *a, **k):
        self._parent_node = parent_node
        super (RelativePandaEntityBase, self).__init__ (*a, **k)

    def set_parent_node (self, node):
        self.node.reparentTo (node)
        self._parent_node = node
        
    def get_parent_node (self):
        return self._parent_node

    def get_root_node (self):
        pass

    def do_update (self, timer):
        super (RelativePandaEntityBase, self).do_update (timer)

        old_position = self._node.getPos ()
        old_scale    = self._node.getScale ()
        old_hpr      = self._node.getHpr ()
        
        self.node.wrtReparentTo (self.get_root_node ())
        self.position = self._node.getPos ()
        self.scale    = self._node.getScale ()
        self.hpr      = self._node.getHpr ()

        self._node.reparentTo (self._parent_node)
        self._node.setPos (old_position)
        self._node.setHpr (old_hpr)
        self._node.setScale (old_scale)


class RelativePandaEntity (RelativePandaEntityBase):

    def get_root_node (self):
        return self.entities.render


class RelativePanda2dEntity (RelativePandaEntityBase):

    def get_root_node (self):
        return self.entities.render2d


class NormalPandaEntityBase (PandaEntityBase):

    def set_position (self, pos):
        super (NormalPandaEntityBase, self).set_position (pos)
        if not pos.isNan ():
            self._node.setPos (pos)
        
    def set_hpr (self, hpr):
        super (NormalPandaEntityBase, self).set_hpr (hpr)
        self._node.setHpr (hpr)
                
    def set_scale (self, scale):
        super (NormalPandaEntityBase, self).set_scale (scale)
        self._node.setScale (scale)


class PandaEntity (NormalPandaEntityBase):

    def get_parent_node (self):
        return self.entities.render


class Panda2dEntity (NormalPandaEntityBase):

    def get_parent_node (self):
        return self.entities.render2d


class DelegatePandaEntity (DelegateSpatialEntity):

    @property
    def node (self):
        return self.delegate.node


class ModelEntityBase (PandaEntityBase):
    """
    TODO: Rethink why not to merge this into PandaEntity and solve a
    lot of trouble in the way.
    """
    
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


class ModelEntityImpl (ModelEntityBase):

    def __init__ (self,
                  model = None,
                  *a, **k):
        super (ModelEntityImpl, self).__init__ (*a, **k)

        self._model = loader.loadModel (model)
        self._model.reparentTo (self._node)

class RelativeModelEntity (
    ModelEntityImpl,
    RelativePandaEntity):
    pass

class ModelEntity (
    ModelEntityImpl,
    PandaEntity):
    pass


class ActorEntityImpl (ModelEntityBase):

    def __init__ (self,
                  model = None,
                  anims = {},
                  *a, **k):
        super (ActorEntityImpl, self).__init__ (*a, **k)

        self._model = Actor (loader.loadModel (model), anims)
        self._model.loadAnims (anims)
        self._model.reparentTo (self._node)

class RelativeActorEntity (
    ActorEntityImpl,
    RelativePandaEntity):
    pass

class ActorEntity (
    ActorEntityImpl,
    PandaEntity):
    pass


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


DelegateActorEntity = DelegateModelEntity
