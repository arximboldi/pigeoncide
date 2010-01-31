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

from core import task
from ent.panda import Panda2dEntity

from pandac.PandaModules import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText

class Hud (Panda2dEntity):

    hud_position  = Vec3 (-0.88, 0, 1) 
    hide_position = Vec3 (-.6, 0, 0)
    show_position = Vec3 (0, 0, 0)
    
    def __init__ (self, *a, **k):
        super (Hud, self).__init__ (*a, **k)

        self.font = loader.loadFont ('font/three-hours.ttf')
        if self.font.getPixelsPerUnit () < 100:
            self.font.setPageSize (512, 512)
            self.font.setPixelsPerUnit (120)
        
        self._next_position = Vec3 (0, 0, -.12)
        self.position = self.hud_position
        self._counter_nodes = []
        
    def dec_counter (self, attr, dec = -1):
        try:
            val = getattr (self, 'num_' + attr)
        except AttributeError:
            val = 0
        self.set_counter (attr, val + dec)

    def set_counter (self, attr, val):
        txt = getattr (self, 'txt_' + attr)
        txt.setText (str (val))
        setattr (self, 'num_' + attr, val)
    
    def add_counter (self, attr, pic):
        root = NodePath (PandaNode ('new-root'))
        root.reparentTo (self.node)
        
        img = OnscreenImage (
            image  = pic,
            pos    = self._next_position,
            parent = root,
            scale  = 0.1)
        img.setTransparency (TransparencyAttrib.MAlpha)
        setattr (self, 'img_' + attr, img)

        txt_pos = self._next_position + Vec3 (.12, 0, -.05)
        txt = OnscreenText (
            text      = '0',
            shadow    = (1, 1, 1, 1),
            font      = self.font,
            mayChange = True,
            pos       = (txt_pos.getX (), txt_pos.getZ ()),
            scale     = .16,
            align     = TextNode.ALeft,
            parent    = root)
        setattr (self, 'txt_' + attr, txt)

        self._next_position += Vec3 (0, 0, -.22)
        self._counter_nodes.append (root)

    def hide (self):
        for n in self._counter_nodes:
            n.setPos (self.hide_position)
                
    def show (self):
        for n in self._counter_nodes:
            n.setPos (self.show_position)

    def soft_show (self):
        return self._soft_move (self.show_position)

    def soft_hide (self):
        return self._soft_move (self.hide_position)
        
    def _soft_move (self, dst):
        next_time = 0
        group = task.parallel ()
        for n in self._counter_nodes:
            group.add (task.sequence (
                task.wait (next_time),
                task.linear (n.setPos, n.getPos (), dst, init = True)))
            next_time += .5
        return self.entities.tasks.add (group)

    
