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

from base.util import printfn
from ent.physical import PhysicalEntityBase
from ent.panda import ModelEntityBase
from laser import Field
from core import task

from pandac.PandaModules import *
from direct.particles.ParticleEffect import ParticleEffect


class KillableEntity (ModelEntityBase, PhysicalEntityBase):
    """
    Incomplete mixin, must be combined with some form of physical
    entity and panda model entity.
    """
    
    def __init__ (self, *a, **k):
        super (KillableEntity, self).__init__ (*a, **k)

        self.enable_collision ()
        self.on_collide += self.on_kill_collision

        self._smoke_particles = self.load_particles ('data/part/smoke.ptf')
        self._fire_particles  = self.load_particles ('data/part/fireish.ptf')
        
        self.dead = False

    def on_kill_collision (self, ev, me, other):
        if not self.dead and isinstance (other, Field):
            pos = ev.getContactPoint (0)
            
            self._model.detachNode ()
            
            node = self.entities.render
            self._smoke_particles.start (node)
            self._smoke_particles.setPos (pos + Vec3 (0, 0, 2))
            self._fire_particles.start (node)
            self._fire_particles.setPos (pos)
            
            self.entities.tasks.add (task.sequence (
                task.wait (1.),
                task.run (self._fire_particles.softStop),
                task.wait (1.),
                task.run (self._smoke_particles.softStop),
                task.wait (2.),
                task.run (self.dispose)))
            
            self.on_die ()
            self.dead = True

            # import game
            # game.DEBUG_INSTANCE.pause ()

    def load_particles (self, name):
        p = ParticleEffect ()
        p.loadConfig (Filename (name))
        p.setLightOff () 
        p.setTransparency (TransparencyAttrib.MAlpha) 
        p.setBin ('fixed', 0) 
        p.setDepthWrite (False)
        p.setShaderOff ()
        return p
    
    def on_die (self):
        pass

    def dispose (self):
        self._smoke_particles.removeNode ()
        self._fire_particles.removeNode ()
        super (KillableEntity, self).dispose ()
