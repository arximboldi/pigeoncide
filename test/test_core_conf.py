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
from core.conf import *

class TestConfBackend:

    class MockBackend:
        def __init__ (self):
            self.called = None
        def _do_load (self, overwrite):
            self.called = "_do_load"
        def _do_save (self):
            self.called = "_do_save"
        def _handle_conf_new_child (self):
            self.called = "_handle_conf_new_child"
        def _handle_conf_del_child (self):
            self.called = "_handle_conf_del_child"

    def test_called (self):
        c = ConfNode ()
        c.backend = TestConfBackend.MockBackend ()

        c.load ()
        self.assertEqual (c.backend.called, "_do_load")
        c.save ()
        self.assertEqual (c.backend.called, "_do_load")
        c.get_child ("x")
        self.assertEqual (c.backend.called, "_handle_cond_new_child")
        c.remove ("x")
        self.assertEqual (c.backend.called, "_handle_conf_del_child")
        c.val = 1
        self.assertEqual (c.backend.called, "_handle_conf_change")
        c.nudge ()
        self.assertEqual (c.backend.called, "_handle_conf_nudge")

    def test_set_backend (self):
        c = ConfNode ()
        c.get_child ("a")
        c.backend = TestConfBackend.MockBanckend ()
        c.get_child ("b")

        self.assertTrue (isinstance (c.backend,
                                     TestConfBackend.MockBanckend))
        self.assertTrue (isinstance (c.get_child ("a").backend,
                                      TestConfBackend.MockBanckend))
        self.assertTrue (isinstance (c.get_child ("b").backend,
                                      TestConfBackend.MockBanckend))
        self.assertRaises (ConfError,
                           c.get_child ("a").set_backend, ConfBackend ())
        
    def test_global_conf (self):
        cfg = GlobalConf ()

        self.asserTrue (isinstance (cfg.get_path ("h.o.l.a"), ConfNode))
        self.asserTrue (not isinstance (cfg.get_path ("h.o.l.a"), GlobalConf))
