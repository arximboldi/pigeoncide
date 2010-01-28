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

from pandac.PandaModules import TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from ent.panda import Panda2dEntity
from ent.task import TaskEntity

class UiEntity (Panda2dEntity):

    panda_ui_cls = None

    def __init__ (self, entities = None, *a, **k):
        super (UiEntity, self).__init__ (entities = entities)
        self._ui    = self.panda_ui_cls (parent = self.node, *a, **k)
        self._alpha = 0.0

    def get_alpha (self):
        return self._alpha
    
    def set_alpha (self, val):
        self._alpha = val
        self._ui.setAlphaScale (val)
        
    def fade_in (self, *a, **k):
        return self.entities.tasks.add (
            task.linear (self.set_alpha, self._alpha, 1.0,
                         init = True, *a, **k))

    def fade_out (self, *a, **k):
        return self.entities.tasks.add (
            task.linear (self.set_alpha, self._alpha, 0.0,
                         init = True, *a, **k))

    alpha = property (get_alpha, set_alpha)


class ImageEntity (UiEntity):
    panda_ui_cls = OnscreenImage

    def __init__ (self, *a, **k):
        super (ImageEntity, self).__init__ (*a, **k)
        self._ui.setTransparency (TransparencyAttrib.MAlpha)


class TextEntity (UiEntity):

    panda_ui_cls = OnscreenText
    
    def __init__ (self, font = None, *a, **k):
        if font:
            if isinstance (font, str):
                font = loader.loadFont (font)
            k ['font'] = font
            
        super (TextEntity, self).__init__ (*a, **k)
    
        
    def set_text (self, text):
        self._ui.setText (text)

    def get_text (self):
        self._ui.getText ()

    text = property (get_text, set_text)
    
