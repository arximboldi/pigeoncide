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
from core.task import *

class TestTask (unittest.TestCase):

    class Counter (Task):
        def __init__ (self):
            super (TestTask.Counter, self).__init__ ()
            self._count = 0
        def do_update (self, x):
            self._count += x

    def test_states (self):
        t = Task ()
        self.assertEqual (t.state, Task.RUNNING)
        t.pause ()
        self.assertEqual (t.state, Task.PAUSED)
        t.resume ()
        self.assertEqual (t.state, Task.RUNNING)
        t.kill ()
        self.assertEqual (t.state, Task.KILLED)
        t.pause ()
        self.assertEqual (t.state, Task.KILLED)
        t.restart ()
        self.assertEqual (t.state, Task.RUNNING)

    def test_next (self):
        class DummyParent:
            def __init__ (self):
                self._tasks = []
                
            def add (self, t):
                self._tasks.append (t)

        t = Task ()
        p = DummyParent ()
        t._set_parent (p)
        self.assertEqual (t.parent, p)
        
        l = [Task (), Task (), Task ()]
        for n in l:
            t.add_next (n)

        t.kill ()
        t.update (None)
        self.assertEqual (p._tasks, l)

    def test_update (self):

        c = TestTask.Counter ()
        c.update (1)
        self.assertEqual (c._count, 1)
        c.update (2)
        self.assertEqual (c._count, 3)
        c.pause ()
        c.update (1)
        self.assertEqual (c._count, 3)
    
    def test_func (self):
        t = FuncTask (func = lambda: None)
        self.assertEqual (t.state, Task.RUNNING)

        t.update (None)
        self.assertEqual (t.state, Task.KILLED)

        t.func = lambda: Task.PAUSED
        t.restart ()
        t.update (None)
        self.assertEqual (t.state, Task.PAUSED)

    def test_group_update (self):

        g = TaskGroup ()
        t1 = TestTask.Counter ()
        t2 = TestTask.Counter ()

        g.add (t1)
        self.assertEqual (g.count, 1)
        g.update (1)
        self.assertEqual (t1._count, 1)
        
        g.add (t2)
        self.assertEqual (g.count, 2)
        g.update (2)
        self.assertEqual (t1._count, 3)
        self.assertEqual (t2._count, 2)

        t1.kill ()
        t2.kill ()
        g.update (0)
        self.assertEqual (g.count, 0)

    def test_group_find (self):

        t1 = Task ()
        t2 = lambda: Task.RUNNING
        g = TaskGroup (t1, t2)
        self.assertEqual (g.count, 2)
        self.assertTrue (isinstance (g.find (t2), FuncTask))

        g.remove (g.find (t2))
        self.assertEqual (g.count, 1)
        self.assertRaises (TaskError, g.add, "not-task-nor-callable")
    
        
        
