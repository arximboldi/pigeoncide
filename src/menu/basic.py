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

from direct.gui.DirectButton import DirectButton

class BasicMenu (object):

    def __init__ (self, tasks = None, manager = None, *a, **k):
        super (BasicMenu, self).__init__ (*a, **k)
        if tasks:
            self.tasks = tasks
        if manager:
            self.manager = manager

    def do_paint (self):
        pass
        
    def do_connect (self):
        pass
        
    def do_destroy (self):
        pass
        
    def create_button (self, btext, pos = (0, 0)):
        return DirectButton(text = (btext, btext, btext, ""),
            scale = .1,
            #command = setText,
            frameSize = (-2., 2., -1, 1),
            #frameSize = ( 1, 1, 1 ),
            frameColor = (1, 1, 0, 0),
            pos = (pos[0], 0, pos[1]),
            #image = '../data/mesh/playButton.png',
            relief = None
            ) 
             
