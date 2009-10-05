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
from core.state import *

class DummyStateBase (State):

    def __init__ (self, mgr):
        State.__init__ (self, mgr)
        self.st = "init"

    def setup (self):
        self.st = "setup"

    def sink (self):
        self.st = "sink"

    def unsink (self):
        self.st = "unsink"

    def release (self):
        self.st = "release"

class DummyStateOne (DummyStateBase):
    pass

class DummyStateTwo (DummyStateBase):
    pass

class TestState (unittest.TestCase):

    def setUp (self):
        self.mgr = StateManager ()
        self.mgr.add ('one', DummyStateOne)
        self.mgr.add ('two', DummyStateTwo)
    
    def test_errors (self):
        self.assertEqual (self.mgr.current, None)
        self.mgr.leave_state ()
        self.assertRaises (StateError, self.mgr.update, 0)
        self.mgr.start ('one')
        self.assertRaises (StateError, self.mgr.start, 'one')
        
    # TODO

