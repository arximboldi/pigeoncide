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

import unittest
from base.observer import *


_Subject, _Listener = \
    make_observer (['on_test'], '_', __name__)

class AListener (_Listener):

    def __init__ (self):
        super (AListener, self).__init__ ()
        self.message = None
        
    def on_test (self):
        self.message = "test"

class TestObserver (unittest.TestCase):
        
    def test_emit (self):
        
        sub = _Subject ()
        lis = AListener ()
        
        sub.connect (lis)
        self.assertEquals (sub.count, 1)
        
        sub.on_test ()
        self.assertEquals (lis.message, "test")

