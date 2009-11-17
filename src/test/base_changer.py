#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente
#
#  This program is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest

from util import *
from base.changer import Changer

class TestChanger (unittest.TestCase):

    def test_member (self):
        class Mock (object):
            changer = Changer (mock_raiser, 0)

        a = Mock ()
        self.assertEquals (a.changer, 0)

        def setter (x, val):
            x.changer = val
            
        self.assertRaises (MockError, setter, a, 1)
        self.assertEquals (a.changer, 1)

        b = Mock ()
        self.assertRaises (MockError, setter, b, 2)
        self.assertEquals (a.changer, 1)
        
