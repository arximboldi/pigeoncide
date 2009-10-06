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
from core.event import *

class TestEventManager (unittest.TestCase):

    def test_adddel (self):
        e = EventManager ()
        x = "test1"
        y = "test2"
        e.add_forwarder (x)
        self.assertEqual (e.forwarder_count, 1)
        e.add_forwarder (y)
        self.assertEqual (e.forwarder_count, 2)
        e.del_forwarder (x)
        self.assertEqual (e.forwarder_count, 1)
        e.del_forwarder (y)
        self.assertEqual (e.forwarder_count, 0)
        self.assertRaises (ValueError, e.del_forwarder, x)

    def test_forward_and_quiet (self):
        class DummyForwarder (object):
            def __init__ (self):
                self.last = ''
            def notify (self, name, *a, **k):
                self.last = name

        fw = DummyForwarder ()
        mgr = EventManager ()
        mgr.add_forwarder (fw)
        
        a = mgr.event ('a').notify ()
        self.assertEqual (fw.last, 'a')
        
        b = mgr.notify ('b')
        self.assertEqual (fw.last, 'b')

        mgr.quiet = True
        mgr.notify ('a')
        self.assertEqual (fw.last, 'b')

    def test_notify_and_quiet (self):
        l = []
        def accum (x):
            l.append (x)

        mgr = EventManager ()
        mgr.event ('ac').connect (accum)

        mgr.notify ('ac', 1)
        self.assertEqual (l, [1])

        mgr.event ('ac') (2)
        self.assertEqual (l, [1, 2])

        mgr.quiet = True

        mgr.notify ('ac', 3)
        self.assertEqual (l, [1, 2])

        mgr.event ('ac') (3)
        self.assertEqual (l, [1, 2, 3])
        
        
