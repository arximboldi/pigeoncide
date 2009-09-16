#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pidgeoncide.
#
#  Pidgeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pidgeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest
from core.signal import *

class TestSignalSlot (unittest.TestCase):

    class Counter:
        def __init__ (self, val = 0):
            self.val = val
        def increase (self):
            self.val += 1
            return self.val
        def decrease (self):
            self.val -= 1
            return self.val

    def test_00 (self):
        sig = Signal ()
        cnt = TestSignalSlot.Counter ()

        slt_a = sig.connect (cnt.increase)
        sig += cnt.decrease
        self.assertEquals (sig.slots (), 2)

        sig.notify ()
        self.assertEquals (cnt.val, 0)
        self.assertEquals (sig.fold (lambda x, y: x+y), 1)
        self.assertEquals (sig.fold (lambda x, y: x+y, 1), 2)

        sig.disconnect_func (cnt.decrease)
        self.assertEquals (sig.slots (), 1)
        
        sig.notify ()
        self.assertEquals (cnt.val, 1)

        sig.disconnect (slt_a)
        self.assertEquals (sig.slots (), 0)

    def test_01 (self):
        sig_a = Signal ()
        sig_b = Signal ()
        cnt = TestSignalSlot.Counter ()
        slt = CleverSlot (cnt.increase)
        
        sig_a += slt
        sig_a += slt
        sig_b += slt
        self.assertEquals (slt.signals (), 2)

        sig_a ()
        self.assertEquals (cnt.val, 1)
        sig_b ()
        self.assertEquals (cnt.val, 2)

        slt.disconnect_all ()
        self.assertEquals (slt.signals (), 0)
        self.assertEquals (sig_a.slots (), 0)
        self.assertEquals (sig_b.slots (), 0)

