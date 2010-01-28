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

"""
TODO: Move this and hud.py to the ent module?
"""

from core import task

from direct.gui.OnscreenText import OnscreenText
from ent.panda import Panda2dEntity
from ent.task import TaskEntity

class TextEntity (Panda2dEntity):

    def __init__ (self, entities = None, font = None, *a, **k):
        super (TextEntity, self).__init__ (entities = entities)
        
        if isinstance (font, str):
            font = loader.loadFont (font)
        
        self.text = OnscreenText (
            font         = font,
            fg           = k.pop ('fg',           (1, 1, 1, 1)),
            bg           = k.get ('bg',           (0, 0, 0, .5)),
            shadow       = k.pop ('shadow',       (.5, 0, 0, 1)),
            shadowOffset = k.pop ('shadowOffset', (.08, .08)),
            frame        = k.pop ('frame',        k.pop ('bg', (0, 0, 0, .5))),
            wordwrap     = k.pop ('wordwrap',     30),
            parent       = self.node,
            *a, **k)
        self._alpha = 0.0

    def _set_alpha (self, val):
        self._alpha = val
        self.text.setAlphaScale (val)
        
    def fade_in (self, *a, **k):
        return self.entities.tasks.add (
            task.linear (self._set_alpha, self._alpha, 1.0,
                         init = True, *a, **k))

    def fade_out (self, *a, **k):
        return self.entities.tasks.add (
            task.linear (self._set_alpha, self._alpha, 0.0,
                         init = True, *a, **k))
